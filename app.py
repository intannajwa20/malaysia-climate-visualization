# app.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Malaysia Climate Visualization", layout="wide")
sns.set(style="whitegrid")

st.title("Malaysia Climate Visualization (Clean Data)")
st.caption("Upload your already-cleaned CSV from Colab and explore 3 visualization objectives.")

# -------------------------
# Upload cleaned CSV
# -------------------------
uploaded = st.sidebar.file_uploader("Upload cleaned CSV (from Colab)", type=["csv"])
if not uploaded:
    st.info("Please upload your **cleaned CSV** (e.g., `malaysia_climate_clean.csv`).")
    st.stop()

# Load (no cleaning here; we trust your CSV)
df = pd.read_csv(uploaded)

# Optional: re-compute AvgTemp_C if missing
if 'AvgTemp_C' not in df.columns and {'MinTemp_C','MaxTemp_C'}.issubset(df.columns):
    df['AvgTemp_C'] = (df['MinTemp_C'] + df['MaxTemp_C']) / 2

# -------------------------
# Filters (years & states)
# -------------------------
years = sorted(df['Year'].dropna().unique())
yr_min, yr_max = int(min(years)), int(max(years))
sel_years = st.sidebar.slider("Year range", min_value=yr_min, max_value=yr_max, value=(yr_min, yr_max), step=1)

states = sorted(df['State'].dropna().unique().tolist())
sel_states = st.sidebar.multiselect("States", options=states, default=states)

mask = (df['Year'].between(sel_years[0], sel_years[1])) & (df['State'].isin(sel_states))
dff = df.loc[mask].copy()

# Quick KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows", f"{len(dff):,}")
c2.metric("States", dff['State'].nunique())
c3.metric("Years", f"{int(dff['Year'].min())}–{int(dff['Year'].max())}")
c4.metric("Stations", dff['Station'].nunique() if 'Station' in dff.columns else "-")

# Tabs for the 3 objectives
tab1, tab2, tab3 = st.tabs(["Objective 1: Annual Trends", "Objective 2: Correlation", "Objective 3: Regional"])

# ======================================
# Objective 1 — Annual Trends
# ======================================
with tab1:
    st.subheader("Objective 1: Annual Climate Trend")

    annual = (dff.groupby('Year')[['AvgTemp_C','Rainfall_mm','Humidity_pct']]
                .mean()
                .reset_index())

    # Temperature
    fig, ax = plt.subplots(figsize=(8,4))
    sns.lineplot(data=annual, x='Year', y='AvgTemp_C', marker='o', ax=ax)
    ax.set_title("Annual Average Temperature"); ax.set_xlabel("Year"); ax.set_ylabel("°C")
    st.pyplot(fig)

    # Rainfall
    fig, ax = plt.subplots(figsize=(8,4))
    sns.lineplot(data=annual, x='Year', y='Rainfall_mm', marker='o', ax=ax)
    ax.set_title("Annual Average Rainfall"); ax.set_xlabel("Year"); ax.set_ylabel("mm")
    st.pyplot(fig)

    # Humidity
    fig, ax = plt.subplots(figsize=(8,4))
    sns.lineplot(data=annual, x='Year', y='Humidity_pct', marker='o', ax=ax)
    ax.set_title("Annual Average Humidity"); ax.set_xlabel("Year"); ax.set_ylabel("%")
    st.pyplot(fig)

# ======================================
# Objective 2 — Correlation
# ======================================
with tab2:
    st.subheader("Objective 2: Correlation Between Variables")

    # Temp vs Rainfall
    fig, ax = plt.subplots(figsize=(7,5))
    sns.scatterplot(data=dff, x='AvgTemp_C', y='Rainfall_mm', hue='State', alpha=0.7, ax=ax)
    ax.set_title("Avg Temperature vs Rainfall"); ax.set_xlabel("Avg Temp (°C)"); ax.set_ylabel("Rainfall (mm)")
    ax.legend(loc='best', fontsize=7, ncol=2)
    st.pyplot(fig)

    # Temp vs Humidity
    fig, ax = plt.subplots(figsize=(7,5))
    sns.scatterplot(data=dff, x='AvgTemp_C', y='Humidity_pct', hue='State', alpha=0.7, ax=ax)
    ax.set_title("Avg Temperature vs Humidity"); ax.set_xlabel("Avg Temp (°C)"); ax.set_ylabel("Humidity (%)")
    ax.legend(loc='best', fontsize=7, ncol=2)
    st.pyplot(fig)

    # Correlation heatmap
    corr = dff[['AvgTemp_C','Rainfall_mm','Humidity_pct']].corr()
    fig, ax = plt.subplots(figsize=(4.8,4))
    sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, fmt=".2f", ax=ax)
    ax.set_title("Correlation Matrix")
    st.pyplot(fig)

# ======================================
# Objective 3 — Regional Comparison
# ======================================
with tab3:
    st.subheader("Objective 3: Regional Climate Comparison by State")

    state_summary = (dff.groupby('State')[['AvgTemp_C','Rainfall_mm','Humidity_pct']]
                       .mean()
                       .reset_index())

    # Rainfall by state
    fig, ax = plt.subplots(figsize=(9,6))
    sns.barplot(data=state_summary.sort_values('Rainfall_mm', ascending=False),
                x='Rainfall_mm', y='State', ax=ax)
    ax.set_title("Average Rainfall by State"); ax.set_xlabel("mm"); ax.set_ylabel("")
    st.pyplot(fig)

    # Temperature by state
    fig, ax = plt.subplots(figsize=(9,6))
    sns.barplot(data=state_summary.sort_values('AvgTemp_C', ascending=False),
                x='AvgTemp_C', y='State', ax=ax)
    ax.set_title("Average Temperature by State"); ax.set_xlabel("°C"); ax.set_ylabel("")
    st.pyplot(fig)

    # Humidity by state
    fig, ax = plt.subplots(figsize=(9,6))
    sns.barplot(data=state_summary.sort_values('Humidity_pct', ascending=False),
                x='Humidity_pct', y='State', ax=ax)
    ax.set_title("Average Humidity by State"); ax.set_xlabel("%"); ax.set_ylabel("")
    st.pyplot(fig)
