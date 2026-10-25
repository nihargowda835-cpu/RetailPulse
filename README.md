# RetailPulse: Big Data Sales Analytics and Demand Forecasting

## Live Dashboard
https://retailpulse-3jx6vyphybtmvbj45vq7ds.streamlit.app

## Project Overview
RetailPulse is a sales analytics dashboard designed to explore retail and warehouse sales, analyze product performance, visualize monthly trends, and demonstrate baseline demand forecasting.

## Technologies Used
- Python
- Pandas
- Plotly
- Streamlit
- PySpark

## Key Features
- Sales performance KPIs
- Monthly sales trend analysis
- Product performance analysis
- Demand forecasting using a moving-average baseline
- Interactive data exploration
- PySpark-based data aggregation

## Project Files
- `app.py` — Streamlit dashboard
- `pyspark_analysis.py` — PySpark data analysis
- `inspect_data.py` — Dataset inspection
- `requirements.txt` — Dashboard dependencies
- `data/` — Retail sales dataset
- `outputs/` — Analysis results

## Run Locally
Install the dependencies and start the dashboard:

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```
