
import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configurazione della pagina
st.set_page_config(page_title="Logistics Dashboard", layout="wide")

# Titolo principale
st.title("🚚 Logistics Tracking Dashboard")

# Percorso del file predefinito
default_file_path = os.path.join("sample_data", "Primary_data.csv")

# Funzione per caricare i dati
@st.cache_data
def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        st.error(f"Errore nel caricamento del file: {e}")
        return None

# Upload del file
uploaded_file = st.file_uploader("Carica il file CSV dei dati logistici", type=['csv'])

if uploaded_file is not None:
    primary_data = pd.read_csv(uploaded_file)
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
].copy()

# KPI principali
st.header("📊 KPI Principali")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Totale Spedizioni",
        f"{len(filtered_data):,}"
    )

with col2:
    st.metric(
        "Distanza Totale",
        f"{filtered_data['TRANSPORTATION_DISTANCE_IN_KM'].sum():,.0f} km"
    )

with col3:
    st.metric(
        "Distanza Media",
        f"{filtered_data['TRANSPORTATION_DISTANCE_IN_KM'].mean():.2f} km"
    )

with col4:
    st.metric(
        "Tipi di Veicoli",
        len(selected_vehicle_types)
    )

# Mappa delle rotte
st.header("🌎 Network Logistico")
filtered_data['Origin_Coordinates'] = filtered_data['Org_lat_lon'].str.split(',').apply(lambda x: list(map(float, x)) if x is not None else [0, 0])
filtered_data['Destination_Coordinates'] = filtered_data['Des_lat_lon'].str.split(',').apply(lambda x: list(map(float, x)) if x is not None else [0, 0])

# Ottimizziamo il campione per la mappa
sample_size = min(100, len(filtered_data))
sampled_data = filtered_data.sample(n=sample_size, random_state=42) if len(filtered_data) > sample_size else filtered_data

fig_map = go.Figure()

# Punti di origine
fig_map.add_trace(go.Scattermapbox(
    lat=sampled_data['Origin_Coordinates'].apply(lambda x: x[0]),
    lon=sampled_data['Origin_Coordinates'].apply(lambda x: x[1]),
    mode='markers',
    marker=dict(size=8, color='blue'),
    name='Origine',
    text=sampled_data['Origin_Location']
))

# Punti di destinazione
fig_map.add_trace(go.Scattermapbox(
    lat=sampled_data['Destination_Coordinates'].apply(lambda x: x[0]),
    lon=sampled_data['Destination_Coordinates'].apply(lambda x: x[1]),
    mode='markers',
    marker=dict(size=8, color='red'),
    name='Destinazione',
    text=sampled_data['Destination_Location']
))

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
    height=400,
    showlegend=True
)

st.plotly_chart(fig_map, use_container_width=True)

# Analisi dei materiali
st.header("📦 Analisi Materiali")
col1, col2 = st.columns(2)

with col1:
    # Statistiche per materiale
    material_stats = filtered_data.groupby('Material Shipped').agg({
        'TRANSPORTATION_DISTANCE_IN_KM': ['sum', 'mean', 'count']
    }).round(2)
    material_stats.columns = ['Distanza Totale', 'Distanza Media', 'Numero Spedizioni']
    st.dataframe(material_stats.sort_values('Distanza Totale', ascending=False))

with col2:
    # Top 10 materiali
    top_materials = filtered_data.groupby('Material Shipped')['TRANSPORTATION_DISTANCE_IN_KM'].sum().sort_values(ascending=True).tail(10)
    
    fig_materials = px.bar(
        y=top_materials.index,
        x=top_materials.values,
        orientation='h',
        title="Top 10 Materiali per Distanza",
        labels={'y': 'Materiale', 'x': 'Distanza Totale (KM)'}
    )
    fig_materials.update_layout(showlegend=False)
    st.plotly_chart(fig_materials, use_container_width=True)

# Analisi temporale
st.header("📈 Trend Temporale")
daily_stats = filtered_data.groupby(filtered_data['BookingID_Date'].dt.date).agg({
    'BookingID': 'count',
    'TRANSPORTATION_DISTANCE_IN_KM': 'sum'
}).reset_index()

fig_trend = px.line(
    daily_stats,
    x='BookingID_Date',
    y=['BookingID', 'TRANSPORTATION_DISTANCE_IN_KM'],
    title="Trend Giornaliero",
    labels={
        'BookingID': 'Numero Spedizioni',
        'TRANSPORTATION_DISTANCE_IN_KM': 'Distanza Totale (KM)'
    }
)
st.plotly_chart(fig_trend, use_container_width=True)

# Footer con statistiche
st.markdown("---")
st.markdown("### 📊 Riepilogo")
col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"Totale record: {len(filtered_data):,}")

with col2:
    st.info(f"Periodo: {date_range[0]} - {date_range[1]}")

with col3:
    st.info(f"Veicoli utilizzati: {len(selected_vehicle_types)}")
