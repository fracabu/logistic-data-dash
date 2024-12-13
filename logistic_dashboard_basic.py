
import streamlit as st
import pandas as pd
import os
import plotly.express as px

# Configurazione della pagina
st.set_page_config(page_title="Logistics Dashboard", layout="wide")

# Titolo principale
st.title("🚚 Logistics Tracking Dashboard")

# Percorso del file predefinito
default_file_path = os.path.join("sample_data", "Primary_data.csv")

# Funzione per caricare i dati
def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        st.error(f"Errore nel caricamento del file: {e}")
        return None

# Upload del file
uploaded_file = st.file_uploader("Carica il file CSV dei dati logistici", type=['csv'])

if uploaded_file is not None:
    primary_data = pd.read_csv(uploaded_file)
    st.success("✅ File caricato correttamente!")
elif os.path.exists(default_file_path):
    st.info("ℹ️ Nessun file caricato. Utilizzando il file predefinito.")
    primary_data = load_data(default_file_path)
else:
    st.error("⚠️ Nessun file caricato e il file predefinito non è disponibile.")
    st.stop()

# Convertire le colonne di data in formato datetime
# Versione alternativa con gestione più dettagliata
primary_data['BookingID_Date'] = pd.to_datetime(primary_data['BookingID_Date'], 
                                               format='%Y-%m-%d %H:%M:%S', 
                                               errors='coerce')

# Sidebar per i filtri base
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

# Applicazione dei filtri
filtered_data = primary_data[
    (primary_data['BookingID_Date'].dt.date >= date_range[0]) &
    (primary_data['BookingID_Date'].dt.date <= date_range[1]) &
    (primary_data['vehicleType'].isin(selected_vehicle_types))
]

# KPI principali
st.header("📊 KPI Principali")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Totale Prenotazioni", len(filtered_data))
with col2:
    st.metric("Distanza Totale (km)", f"{filtered_data['TRANSPORTATION_DISTANCE_IN_KM'].sum():,.0f} km")
with col3:
    st.metric("Distanza Media (km)", f"{filtered_data['TRANSPORTATION_DISTANCE_IN_KM'].mean():.2f} km")

# Statistiche sui materiali
st.header("📦 Statistiche Materiali")
material_stats = filtered_data.groupby('Material Shipped')['TRANSPORTATION_DISTANCE_IN_KM'].sum().sort_values(ascending=False)

fig_materials = px.bar(
    x=material_stats.index[:10],  # Solo i top 10 materiali
    y=material_stats.values[:10],
    title="Top 10 Materiali per Distanza",
    labels={'x': 'Materiale', 'y': 'Distanza Totale (KM)'}
)
st.plotly_chart(fig_materials, use_container_width=True)

# Statistiche per veicoli
st.header("🚛 Statistiche per Veicoli")
vehicle_stats = filtered_data.groupby('vehicleType')['TRANSPORTATION_DISTANCE_IN_KM'].agg(['sum', 'mean', 'count']).round(2)
vehicle_stats.columns = ['Distanza Totale', 'Distanza Media', 'Numero Spedizioni']
st.dataframe(vehicle_stats)

# Trend temporale semplice
st.header("📈 Trend Temporale")
daily_data = filtered_data.groupby(filtered_data['BookingID_Date'].dt.date)['TRANSPORTATION_DISTANCE_IN_KM'].sum().reset_index()
fig_trend = px.line(
    daily_data,
    x='BookingID_Date',
    y='TRANSPORTATION_DISTANCE_IN_KM',
    title="Andamento Distanze nel Tempo"
)
st.plotly_chart(fig_trend, use_container_width=True)

# Tabella dettagliata
st.header("📋 Dettaglio Spedizioni")
st.dataframe(
    filtered_data[['BookingID', 'BookingID_Date', 'Origin_Location', 'Destination_Location', 
                  'vehicleType', 'Material Shipped', 'TRANSPORTATION_DISTANCE_IN_KM']]
    .sort_values(by='BookingID_Date', ascending=False)
    .head(100)  # Mostra solo le prime 100 righe
)
