
import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configurazione della pagina
st.set_page_config(page_title="Logistics Dashboard", layout="wide")

# Titolo principale
st.title("🚚 Logistics Tracking Dashboard")

# Tabs per la navigazione
tab1, tab2, tab3 = st.tabs(["Dashboard", "Performance Analysis", "Predictions"])

# Percorso del file predefinito
default_file_path = os.path.join("sample_data", "Primary_data.csv")

# Funzione per caricare i dati
@st.cache_data
def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        # Aggiungiamo le colonne simulate solo se non esistono già
        if 'On_Time' not in data.columns:
            data['On_Time'] = np.random.uniform(0.8, 1.0, len(data))
            data['Load_Factor'] = np.random.uniform(0.5, 1.0, len(data))
            data['Cost_per_KM'] = np.random.uniform(1.0, 2.0, len(data))
            data['Fuel_Efficiency'] = np.random.uniform(25, 35, len(data))
            data['Delivery_Status'] = np.random.choice(
                ['On Time', 'Delayed', 'Early'], 
                len(data), 
                p=[0.7, 0.2, 0.1]
            )
        return data
    except Exception as e:
        st.error(f"Errore nel caricamento del file: {e}")
        return None

# Upload del file
uploaded_file = st.file_uploader("Carica il file CSV dei dati logistici", type=['csv'])

if uploaded_file is not None:
    primary_data = load_data(uploaded_file)
    st.success("✅ File caricato correttamente!")
elif os.path.exists(default_file_path):
    st.info("ℹ️ Utilizzo del file predefinito")
    primary_data = load_data(default_file_path)
else:
    st.error("⚠️ Nessun file caricato e il file predefinito non è disponibile.")
    st.stop()

if primary_data is None:
    st.error("⚠️ Errore nel caricamento dei dati")
    st.stop()

# Convertire le colonne di data in formato datetime
primary_data['BookingID_Date'] = pd.to_datetime(primary_data['BookingID_Date'], errors='coerce')
primary_data['Data_Ping_time'] = pd.to_datetime(primary_data['Data_Ping_time'], errors='coerce')

# Tab 1: Dashboard principale
with tab1:
    # Sidebar per i filtri
    st.sidebar.header("📁 Filtri")

    # Filtro per data
    min_date = primary_data['BookingID_Date'].min()
    max_date = primary_data['BookingID_Date'].max()
    date_range = st.sidebar.date_input(
        "Seleziona intervallo date",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Filtro per tipo di veicolo
    vehicle_types = primary_data['vehicleType'].unique()
    selected_vehicle_types = st.sidebar.multiselect(
        "Tipo di veicolo",
        options=vehicle_types,
        default=vehicle_types
    )

    # Filtro per materiale
    materials = primary_data['Material Shipped'].unique()
    selected_materials = st.sidebar.multiselect(
        "Materiale trasportato",
        options=materials,
        default=materials
    )

    # Applicazione dei filtri
    filtered_data = primary_data[
        (primary_data['BookingID_Date'].dt.date >= date_range[0]) &
        (primary_data['BookingID_Date'].dt.date <= date_range[1]) &
        (primary_data['vehicleType'].isin(selected_vehicle_types)) &
        (primary_data['Material Shipped'].isin(selected_materials))
    ].copy()  # Aggiungiamo .copy() per evitare SettingWithCopyWarning

    # KPI principali
    st.header("📊 KPI Principali")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "On-Time Delivery Rate",
            f"{(filtered_data['On_Time'].mean()*100):.1f}%",
            f"{((filtered_data['On_Time'].mean() - 0.9)*100):.1f}%"
        )
    with col2:
        st.metric(
            "Vehicle Utilization",
            f"{(filtered_data['Load_Factor'].mean()*100):.1f}%",
            f"{((filtered_data['Load_Factor'].mean() - 0.75)*100):.1f}%"
        )
    with col3:
        st.metric(
            "Total Distance",
            f"{filtered_data['TRANSPORTATION_DISTANCE_IN_KM'].sum():,.0f} km"
        )
    with col4:
        st.metric(
            "Fuel Efficiency",
            f"{filtered_data['Fuel_Efficiency'].mean():.1f} L/100km"
        )
# Visualizzazione delle rotte su mappa
st.header("🌎 Network Logistico")

# Utilizziamo il caching per le trasformazioni dei dati
@st.cache_data
def prepare_map_data(data):
    data = data.copy()
    data['Origin_Coordinates'] = data['Org_lat_lon'].str.split(',').apply(lambda x: list(map(float, x)) if x is not None else [0, 0])
    data['Destination_Coordinates'] = data['Des_lat_lon'].str.split(',').apply(lambda x: list(map(float, x)) if x is not None else [0, 0])
    return data

# Prepariamo i dati
map_data = prepare_map_data(filtered_data)

# Creiamo la mappa
fig_map = go.Figure()

# Aggiungiamo solo un campione rappresentativo di linee (es. 100 linee)
sample_size = min(100, len(map_data))
sampled_data = map_data.sample(n=sample_size, random_state=42) if len(map_data) > sample_size else map_data

# Linee di connessione (ridotte)
for idx, row in sampled_data.iterrows():
    fig_map.add_trace(go.Scattermapbox(
        lat=[row['Origin_Coordinates'][0], row['Destination_Coordinates'][0]],
        lon=[row['Origin_Coordinates'][1], row['Destination_Coordinates'][1]],
        mode='lines',
        line=dict(width=1, color='rgba(0,0,0,0.1)'),
        showlegend=False
    ))

# Punti di origine (unici)
unique_origins = map_data.drop_duplicates(subset=['Origin_Location'])
fig_map.add_trace(go.Scattermapbox(
    lat=unique_origins['Origin_Coordinates'].apply(lambda x: x[0]),
    lon=unique_origins['Origin_Coordinates'].apply(lambda x: x[1]),
    mode='markers',
    marker=dict(size=8, color='blue'),
    name='Origine',
    text=unique_origins['Origin_Location'],
    hoverinfo='text'
))

# Punti di destinazione (unici)
unique_destinations = map_data.drop_duplicates(subset=['Destination_Location'])
fig_map.add_trace(go.Scattermapbox(
    lat=unique_destinations['Destination_Coordinates'].apply(lambda x: x[0]),
    lon=unique_destinations['Destination_Coordinates'].apply(lambda x: x[1]),
    mode='markers',
    marker=dict(size=8, color='red'),
    name='Destinazione',
    text=unique_destinations['Destination_Location'],
    hoverinfo='text'
))

# Statistiche
num_origins = len(unique_origins)
num_destinations = len(unique_destinations)
total_distance = map_data['TRANSPORTATION_DISTANCE_IN_KM'].sum()

# Layout
fig_map.update_layout(
    mapbox=dict(
        style="carto-positron",
        zoom=4,
        center=dict(
            lat=20.5937,
            lon=78.9629
        )
    ),
    margin=dict(l=0, r=0, t=0, b=0),
    height=500,
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(255, 255, 255, 0.8)"
    )
)

st.plotly_chart(fig_map, use_container_width=True)

# Metriche in colonne
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Punti di Origine", num_origins)
with col2:
    st.metric("Punti di Destinazione", num_destinations)
with col3:
    st.metric("Distanza Totale", f"{total_distance:,.0f} km")
    
   # Statistiche sui materiali
st.header("📦 Analisi Materiali")
col1, col2 = st.columns(2)

with col1:
    # Statistiche dettagliate per materiale
    material_stats = filtered_data.groupby('Material Shipped').agg({
        'TRANSPORTATION_DISTANCE_IN_KM': ['sum', 'mean', 'min', 'max'],
        'BookingID': 'count'
    }).round(2)
    
    # Rinominiamo le colonne
    material_stats.columns = [
        'Distanza Totale (KM)', 
        'Distanza Media (KM)',
        'Distanza Min (KM)',
        'Distanza Max (KM)',
        'Num. Spedizioni'
    ]
    
    # Ordiniamo per distanza totale
    material_stats = material_stats.sort_values('Distanza Totale (KM)', ascending=False)
    st.dataframe(material_stats, height=400)

with col2:
    # Prendiamo i top 15 materiali
    material_dist = (filtered_data.groupby('Material Shipped')['TRANSPORTATION_DISTANCE_IN_KM']
                    .sum()
                    .sort_values(ascending=True)
                    .tail(15))
    
    # Creiamo il grafico a barre orizzontali
    fig_materials = px.bar(
        y=material_dist.index,
        x=material_dist.values,
        orientation='h',
        title="Top 15 Materiali per Distanza Totale",
        labels={
            'x': 'Distanza Totale (KM)',
            'y': 'Materiale'
        },
        color=material_dist.values,
        color_continuous_scale='Viridis'
    )
    
    # Miglioriamo il layout
    fig_materials.update_layout(
        showlegend=False,
        height=600,
        yaxis={'categoryorder': 'total ascending'},
        font=dict(size=12),
        margin=dict(l=200),
        coloraxis_showscale=False
    )
    
    # Aggiorniamo il font delle etichette
    fig_materials.update_yaxes(tickfont=dict(size=12))
    
    st.plotly_chart(fig_materials, use_container_width=True)

# Tab 2: Performance Analysis
with tab2:
    st.header("🎯 Analisi Performance")

    # Metriche temporali
    st.subheader("Trend Temporali")
    metric_choice = st.selectbox(
        "Seleziona Metrica",
        ['Load_Factor', 'On_Time', 'Fuel_Efficiency', 'Cost_per_KM']
    )

    daily_metrics = filtered_data.groupby(
        filtered_data['BookingID_Date'].dt.date
    )[metric_choice].mean().reset_index()

    fig_trend = px.line(
        daily_metrics,
        x='BookingID_Date',
        y=metric_choice,
        title=f"Trend {metric_choice}"
    )
    st.plotly_chart(fig_trend)

    # Analisi veicoli
    st.subheader("Performance Veicoli")
    vehicle_metrics = filtered_data.groupby('vehicleType').agg({
        'Load_Factor': 'mean',
        'On_Time': 'mean',
        'Fuel_Efficiency': 'mean',
        'TRANSPORTATION_DISTANCE_IN_KM': 'sum'
    }).round(3)

    st.dataframe(vehicle_metrics)

# Tab 3: Predictions
with tab3:
    st.header("🔮 Previsioni")

    if len(filtered_data) > 0:
        # Feature Engineering
        def prepare_features(data):
            features = pd.DataFrame()
            
            # Features temporali
            features['month'] = data['BookingID_Date'].dt.month
            features['day_of_week'] = data['BookingID_Date'].dt.dayofweek
            
            # One-hot encoding
            vehicle_dummies = pd.get_dummies(data['vehicleType'], prefix='vehicle')
            material_dummies = pd.get_dummies(data['Material Shipped'], prefix='material')
            
            return pd.concat([features, vehicle_dummies, material_dummies], axis=1)

        # Training del modello
        target_col = st.selectbox(
            "Seleziona variabile target",
            ['TRANSPORTATION_DISTANCE_IN_KM', 'Cost_per_KM', 'Fuel_Efficiency']
        )

        if st.button("Addestra Modello"):
            try:
                X = prepare_features(filtered_data)
                y = filtered_data[target_col]

                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )

                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X_train, y_train)

                train_score = model.score(X_train, y_train)
                test_score = model.score(X_test, y_test)

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("R² Training", f"{train_score:.3f}")
                with col2:
                    st.metric("R² Test", f"{test_score:.3f}")

                # Feature Importance
                feature_importance = pd.DataFrame({
                    'feature': X.columns,
                    'importance': model.feature_importances_
                }).sort_values('importance', ascending=False)

                st.plotly_chart(px.bar(
                    feature_importance.head(10),
                    x='importance',
                    y='feature',
                    title="Feature Importance"
                ))

                st.session_state['model'] = model
                st.session_state['feature_columns'] = X.columns

            except Exception as e:
                st.error(f"Errore nel training: {str(e)}")

        # Previsioni
        if 'model' in st.session_state:
            st.subheader("Fai una Previsione")
            col1, col2 = st.columns(2)

            with col1:
                pred_vehicle = st.selectbox("Tipo di Veicolo", vehicle_types)
                pred_material = st.selectbox("Materiale", materials)

            with col2:
                pred_month = st.slider("Mese", 1, 12, datetime.now().month)
                pred_day = st.slider("Giorno della Settimana", 0, 6, datetime.now().weekday())

            if st.button("Calcola Previsione"):
                try:
                    pred_data = pd.DataFrame({
                        'BookingID_Date': [pd.Timestamp(2024, pred_month, 1)],
                        'vehicleType': [pred_vehicle],
                        'Material Shipped': [pred_material]
                    })

                    X_pred = prepare_features(pred_data)
                    
                    # Aggiungi colonne mancanti
                    for col in st.session_state['feature_columns']:
                        if col not in X_pred.columns:
                            X_pred[col] = 0
                    
                    # Riordina le colonne
                    X_pred = X_pred[st.session_state['feature_columns']]
                    
                    prediction = st.session_state['model'].predict(X_pred)
                    
                    st.metric(
                        f"Previsione {target_col}",
                        f"{prediction[0]:.2f}"
                    )

                except Exception as e:
                    st.error(f"Errore nella previsione: {str(e)}")

# Footer
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)
with footer_col1:
    st.info(f"Totale record: {len(filtered_data):,}")
with footer_col2:
    st.info(f"Periodo: {date_range[0]} - {date_range[1]}")
with footer_col3:
    st.info(f"Tipi di veicolo: {len(selected_vehicle_types)}")
