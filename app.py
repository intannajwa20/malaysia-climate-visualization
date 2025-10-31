import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Malaysia Climate Viz (2000–2021)", layout="wide")
sns.set(style="whitegrid")

st.title("Malaysia Climate Visualization (2000–2021)")
st.caption("Mean Temperature • Rainfall • Relative Humidity")

# -------------------------
# Sidebar: File + Tips
# -------------------------
st.sidebar.header("1) Upload Dataset")
uploaded = st.sidebar.file_uploader(
    "Upload DOSM Excel/CSV (Mean Temperature, Rainfall & Mean Relative Humidity, Malaysia)",
    type=["xlsx","csv"]
)

st.sidebar.markdown("---")
st.sidebar.header("Tips")
st.sidebar.write("• Upload the original Excel or a CSV exported from it.")
st.sidebar.write("• Then choose filters (years, states) to explore.")
st.sidebar.write("• Keep the PDF report ≤ 5 pages and include this app link.")

@st.cache_data
def load_and_clean(file) -> pd.DataFrame:
    # Load
    if file.name.lower().endswith(".xlsx"):
        df = pd.read_excel(file)
    else:
        df = pd.read_csv(file)

    # Standardize column names (edit here if yours differ)
    df.columns = [
        'State',
        'Station',
        'Altitude_m',
        'Year',
        'MinTemp_C',
        'MaxTemp_C',
        'Rainfall_mm',
        'RainDays',
        'Humidity_pct'
    ]

    # Clean text -> numeric
    def to_numeric_series(s):
        return (s.astype(str)
                  .str.replace(",", "", regex=True)
                  .str.replace("-", "", regex=True)
                  .str.strip()
               )

    for col in ['Rainfall_mm','RainDays','Humidity_pct','Altitude_m','MinTemp_C','MaxTemp_C','Year']:
        df[col] = to_numeric_series(df[col])

    # Convert types
    df['Rainfall_mm']   = pd.to_numeric(df['Rainfall_mm'], errors='coerce')
    df['RainDays']      = pd.to_numeric(df['RainDays'], errors='coerce')
    df['Humidity_pct']  = pd.to_numeric(df['Humidity_pct'], errors='coerce')
    df['Altitude_m']    = pd.to_numeric(df['Altitude_m'], errors='coerce')
    df['MinTemp_C']     = pd.to_numeric(df['MinTemp_C'], errors='coerce')
    df['MaxTemp_C']     = pd.to_numeric(df['MaxTemp_C'], errors='coerce')
    df['Year']          = pd.to_numeric(df['Year'], errors='coerce', downcast="integer")

    # Drop essential NaNs
    df = df.dropna(subset=['Year','MinTemp_C','MaxTemp_C','Humidity_pct','Rainfall_mm'])

    # Derived feature
    df['AvgTemp_C'] = (df['MinTemp_C'] + df['MaxTemp_C']) / 2

    # Reasonable bounds (safety)
    df = df[
        (df['Rainfall_mm'] >= 0) &
        (df['Humidity_pct'].between(0,100)) &
        (df['MaxTemp_C'] <= 45) &
        (df['MinTemp_C'] >= 5)
    ]

    # Remove duplicates (same station & year)
    df = df.drop_duplicates(subset=['State','Station','Year'])

    return df

if uploaded is None:
    st.info("Upload your dataset (Excel/CSV) to begin.")
    st.stop()

df = load_and_clean(uploaded)

# -------------------------
# Sidebar: Filters
# -------------------------
years = sorted(df['Year'].dropna().unique())
yr_min, yr_max = int(min(years)), int(max(years))
sel_years = st.sidebar.slider("Year range", min_value=yr_min, max_value=yr_max, value=(yr_min, yr_max), step=1)

states = sorted(df['State'].dropna().unique().tolist())
sel_states = st.sidebar.multiselect("States", options=states, default=states)

mask = (df['Year'].between(sel_years[0], sel_years[1])) & (df['State'].isin(sel_states))
dff = df.loc[mask].copy()

st.sidebar.markdown("---")
st.sidebar.download_button(
    "Download filtered CSV",
    data=dff.to_csv(index=False).encode("utf-8"),
    file_name="malaysia_climate_filtered.csv",
    mime="text/csv"
)

# KPI row
c1,c2,c3,c4 = st.columns(4)
c1.metric("Rows", f"{len(dff):,}")
c2.metric("States", dff['State'].nunique())
c3.metric("Year Range", f"{dff['Year'].min()}–{dff['Year'].max()}")
c4.metric("Stations", dff['Station'].nunique())

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Objective 1: Annual Trends", "Objective 2: Correlation", "Objective 3: Regional", "Report Outline"])

# === Objective 1 ===
with tab1:
    st.subheader("Objective 1: Annual Climate Trend")
    st.caption("Analyze annual trends of average temperature, rainfall and humidity in Malaysia.")

    annual = (dff.groupby('Year')[['AvgTemp_C','Rainfall_mm','Humidity_pct']]
                .mean()
                .reset_index()
             )

    colA, colB = st.columns([3,2])
    with colA:
        st.info(
            "Summary (auto):\n"
            f"- Years shown: {int(annual['Year'].min())}–{int(annual['Year'].max())}\n"
            f"- Mean Temp: {annual['AvgTemp_C'].mean():.2f} °C\n"
            f"- Rainfall: {annual['Rainfall_mm'].mean():.0f} mm\n"
            f"- Humidity: {annual['Humidity_pct'].mean():.1f} %"
        )

    fig, ax = plt.subplots(figsize=(7,4))
    sns.lineplot(data=annual, x='Year', y='AvgTemp_C', marker='o', ax=ax)
    ax.set_title("Annual Average Temperature"); ax.set_xlabel("Year"); ax.set_ylabel("°C")
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(7,4))
    sns.lineplot(data=annual, x='Year', y='Rainfall_mm', marker='o', ax=ax)
    ax.set_title("Annual Average Rainfall"); ax.set_xlabel("Year"); ax.set_ylabel("mm")
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(7,4))
    sns.lineplot(data=annual, x='Year', y='Humidity_pct', marker='o', ax=ax)
    ax.set_title("Annual Average Humidity"); ax.set_xlabel("Year"); ax.set_ylabel("%")
    st.pyplot(fig)

# === Objective 2 ===
with tab2:
    st.subheader("Objective 2: Correlation Between Variables")
    st.caption("Explore relationships between temperature, rainfall and humidity.")

    fig, ax = plt.subplots(figsize=(7,5))
    sns.scatterplot(data=dff, x='AvgTemp_C', y='Rainfall_mm', hue='State', alpha=0.7, ax=ax)
    ax.set_title("Avg Temperature vs Rainfall"); ax.set_xlabel("Avg Temp (°C)"); ax.set_ylabel("Rainfall (mm)")
    ax.legend(loc='best', fontsize=7, ncol=2)
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(7,5))
    sns.scatterplot(data=dff, x='AvgTemp_C', y='Humidity_pct', hue='State', alpha=0.7, ax=ax)
    ax.set_title("Avg Temperature vs Humidity"); ax.set_xlabel("Avg Temp (°C)"); ax.set_ylabel("Humidity (%)")
    ax.legend(loc='best', fontsize=7, ncol=2)
    st.pyplot(fig)

    corr = dff[['AvgTemp_C','Rainfall_mm','Humidity_pct']].corr()
    fig, ax = plt.subplots(figsize=(4.5,3.8))
    sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, fmt=".2f", ax=ax)
    ax.set_title("Correlation Matrix")
    st.pyplot(fig)

# === Objective 3 ===
with tab3:
    st.subheader("Objective 3: Regional Climate Comparison by State")
    st.caption("Compare rainfall, temperature and humidity across states.")

    state_summary = (dff.groupby('State')[['AvgTemp_C','Rainfall_mm','Humidity_pct']]
                       .mean()
                       .reset_index()
                    )

    fig, ax = plt.subplots(figsize=(9,6))
    sns.barplot(data=state_summary.sort_values('Rainfall_mm', ascending=False),
                x='Rainfall_mm', y='State', ax=ax)
    ax.set_title("Average Rainfall by State"); ax.set_xlabel("mm"); ax.set_ylabel("")
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(9,6))
    sns.barplot(data=state_summary.sort_values('AvgTemp_C', ascending=False),
                x='AvgTemp_C', y='State', ax=ax)
    ax.set_title("Average Temperature by State"); ax.set_xlabel("°C"); ax.set_ylabel("")
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(9,6))
    sns.barplot(data=state_summary.sort_values('Humidity_pct', ascending=False),
                x='Humidity_pct', y='State', ax=ax)
    ax.set_title("Average Humidity by State"); ax.set_xlabel("%"); ax.set_ylabel("")
    st.pyplot(fig)

    st.markdown("**State-wise summary heatmap (optional):**")
    fig, ax = plt.subplots(figsize=(8,6))
    sns.heatmap(state_summary.set_index('State'), annot=True, cmap='YlGnBu', fmt=".1f", ax=ax)
    ax.set_title("State-wise Climate Summary")
    st.pyplot(fig)

# === Report outline ===
with tab4:
    st.subheader("Report Outline (paste into your PDF)")
    st.markdown("""
**Dataset Selection & Relevance**  
- Source: DOSM open data (Mean Temperature, Rainfall, Mean Relative Humidity)  
- Scope: Malaysia, 2000–2021; Variables: Min/Max Temp, Rainfall, Humidity, State, Station, Year  
- Relevance: Climate trends, hydrology, flood risk, planning

**Page 1 – Objective 1 (Trends)**  
- 3 line charts + 100–150 words summary

**Page 2 – Objective 2 (Correlation)**  
- 2 scatter plots + correlation heatmap + interpretation

**Page 3 – Objective 3 (Regional)**  
- 3 bar charts by state + optional heatmap + insights

**Submit this Streamlit link** in your PDF (≤ 5 pages).
""")
