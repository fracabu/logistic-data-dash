<h1 align="center">Logistics Tracking Dashboard</h1>
<h3 align="center">Multi-tier Analytics for Logistics Data</h3>

<p align="center">
  <em>Interactive dashboard for monitoring and analyzing logistics data with three versions</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white" alt="Plotly" />
  <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white" alt="scikit-learn" />
</p>

<p align="center">
  :gb: <a href="#english">English</a> | :it: <a href="#italiano">Italiano</a>
</p>

---

<a name="english"></a>
## :gb: English

### Overview

An interactive dashboard for monitoring and analyzing logistics data, available in three versions with increasing functionality to adapt to different analysis needs.

### Features

| Version | Features |
|---------|----------|
| **Basic** | CSV loading, date/vehicle filters, core KPIs, top 10 materials, basic trend |
| **Standard** | + Material filters, logistics map, extended KPIs, detailed statistics |
| **Premium** | + ML predictions, advanced route maps, performance analysis, feature importance |

### Quick Start

```bash
git clone https://github.com/fracabu/logistic-data-dash.git
cd logistic-data-dash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
streamlit run logistic_dashboard_premium.py
```

### Data Format

Required CSV columns:
- `BookingID`, `BookingID_Date` - Booking identification
- `Origin_Location`, `Destination_Location` - Locations
- `vehicleType`, `Material Shipped` - Transport details
- `TRANSPORTATION_DISTANCE_IN_KM` - Distance
- `Org_lat_lon`, `Des_lat_lon` - Coordinates (Standard/Premium)

---

<a name="italiano"></a>
## :it: Italiano

### Panoramica

Dashboard interattiva per il monitoraggio e l'analisi dei dati logistici, disponibile in tre versioni con funzionalita crescenti per diverse esigenze di analisi.

### Funzionalita

| Versione | Funzionalita |
|----------|--------------|
| **Basic** | Caricamento CSV, filtri data/veicolo, KPI base, top 10 materiali, trend base |
| **Standard** | + Filtri materiali, mappa logistica, KPI estesi, statistiche dettagliate |
| **Premium** | + Previsioni ML, mappe rotte avanzate, analisi performance, feature importance |

### Avvio Rapido

```bash
git clone https://github.com/fracabu/logistic-data-dash.git
cd logistic-data-dash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
streamlit run logistic_dashboard_premium.py
```

### Formato Dati

Colonne CSV richieste:
- `BookingID`, `BookingID_Date` - Identificazione prenotazione
- `Origin_Location`, `Destination_Location` - Localita
- `vehicleType`, `Material Shipped` - Dettagli trasporto
- `TRANSPORTATION_DISTANCE_IN_KM` - Distanza
- `Org_lat_lon`, `Des_lat_lon` - Coordinate (Standard/Premium)

---

## Tech Stack

- **Framework**: Streamlit
- **Visualization**: Plotly
- **ML**: scikit-learn, statsmodels
- **Data**: Pandas, NumPy

## License

MIT

---

<p align="center">
  <a href="https://github.com/fracabu">
    <img src="https://img.shields.io/badge/Made_by-fracabu-8B5CF6?style=flat-square" alt="Made by fracabu" />
  </a>
</p>
