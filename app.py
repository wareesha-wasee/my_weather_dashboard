import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Weather Intelligence Dashboard",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp {
    background:
      radial-gradient(circle at 8% 2%, rgba(44, 110, 150, .22), transparent 28%),
      radial-gradient(circle at 92% 10%, rgba(126, 86, 180, .18), transparent 26%),
      linear-gradient(135deg, #080f1d 0%, #101a2d 52%, #111629 100%);
    color: #edf3ff;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101b30 0%, #151b31 100%);
    border-right: 1px solid rgba(151,177,220,.14);
}
[data-testid="stSidebar"] * { color: #e8efff !important; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1500px; }
h1,h2,h3 { font-family: 'Outfit', sans-serif !important; color: #f5f7ff !important; }
.hero {
    padding: 26px 30px; border-radius: 22px; margin-bottom: 22px;
    background: linear-gradient(115deg, rgba(33,72,112,.72), rgba(67,51,105,.65));
    border: 1px solid rgba(166,197,255,.20);
    box-shadow: 0 16px 45px rgba(0,0,0,.20);
}
.hero-kicker { color:#a9c8ee; letter-spacing:2px; font-size:11px; font-weight:800; text-transform:uppercase; }
.hero-title { font-family:'Outfit',sans-serif; font-size:34px; font-weight:800; margin:5px 0 4px; color:#fff; }
.hero-sub { color:#c4d2e8; font-size:14px; }
.metric-card {
    padding: 18px 20px; min-height: 122px; border-radius: 18px;
    background: linear-gradient(145deg, rgba(27,43,68,.95), rgba(23,31,53,.95));
    border: 1px solid rgba(148,177,220,.17);
    box-shadow: 0 10px 28px rgba(0,0,0,.16);
}
.metric-label { color:#9fb3d2; font-size:12px; font-weight:700; letter-spacing:.7px; text-transform:uppercase; }
.metric-value { color:#f7f9ff; font-family:'Outfit',sans-serif; font-size:29px; font-weight:800; margin-top:8px; }
.metric-note { color:#8fa5c7; font-size:11px; margin-top:2px; }
.section-head { margin: 26px 0 12px; font-family:'Outfit',sans-serif; font-size:20px; font-weight:700; color:#f3f6ff; }
.panel {
    background: rgba(21,32,53,.82); border:1px solid rgba(148,177,220,.15);
    border-radius:18px; padding:16px 18px 8px; box-shadow:0 10px 28px rgba(0,0,0,.13);
}
div[data-testid="stDataFrame"] { border:1px solid rgba(148,177,220,.15); border-radius:14px; }
.stCaption, small { color:#9fb3d2 !important; }
button[kind="primary"] { background:linear-gradient(90deg,#4c9bd6,#8b72d6); border:0; }
hr { border-color:rgba(148,177,220,.15); }
</style>
""", unsafe_allow_html=True)

# ---------- Load data ----------
@st.cache_data
def load_data(path):
    data = pd.read_csv(path)
    data["Formatted Date"] = pd.to_datetime(data["Formatted Date"], errors="coerce", utc=True)
    data["Month Name"] = data["Formatted Date"].dt.strftime("%b")
    data["Date"] = data["Formatted Date"].dt.date
    data["Humidity (%)"] = data["Humidity"] * 100
    return data

default_path = Path(__file__).with_name("weather_data.csv")
uploaded = st.sidebar.file_uploader("Upload your weather CSV", type=["csv"])
if uploaded is not None:
    df = load_data(uploaded)
elif default_path.exists():
    df = load_data(default_path)
else:
    st.error("weather_data.csv nahi mili. CSV ko app.py ke same folder mein rakhein ya sidebar se upload karein.")
    st.stop()

# ---------- Sidebar filters ----------
st.sidebar.markdown("## 🌦️ Dashboard Controls")
st.sidebar.caption("Choose filters to explore the weather records.")
years = sorted(df["Year"].dropna().unique().tolist())
selected_years = st.sidebar.multiselect("Year", years, default=years)
months = list(range(1, 13))
selected_months = st.sidebar.multiselect(
    "Month",
    months,
    default=months,
    format_func=lambda x: pd.Timestamp(2000, x, 1).strftime("%B")
)
summaries = sorted(df["Summary"].dropna().unique().tolist())
selected_summaries = st.sidebar.multiselect("Weather condition", summaries, default=summaries)
precips = sorted(df["Precip Type"].dropna().unique().tolist())
selected_precips = st.sidebar.multiselect("Precipitation type", precips, default=precips)

filtered = df[
    df["Year"].isin(selected_years)
    & df["Month"].isin(selected_months)
    & df["Summary"].isin(selected_summaries)
]
if selected_precips:
    filtered = filtered[filtered["Precip Type"].isin(selected_precips) | filtered["Precip Type"].isna()]
else:
    filtered = filtered[filtered["Precip Type"].isna()]

if filtered.empty:
    st.warning("Selected filters ke liye koi record nahi mila. Filters change karein.")
    st.stop()

# ---------- Header ----------
st.markdown("""
<div class="hero">
  <div class="hero-kicker">CLIMATE • DATA • INSIGHTS</div>
  <div class="hero-title">Weather Intelligence</div>
  <div class="hero-sub">Explore temperature, humidity, wind and atmospheric conditions through your dataset.</div>
</div>
""", unsafe_allow_html=True)

# ---------- KPI cards ----------
avg_temp = filtered["Temperature (C)"].mean()
avg_feels = filtered["Apparent Temperature (C)"].mean()
avg_humidity = filtered["Humidity (%)"].mean()
avg_wind = filtered["Wind Speed (km/h)"].mean()
avg_visibility = filtered["Visibility (km)"].mean()
total = len(filtered)

kpis = [
    ("TOTAL RECORDS", f"{total:,}", "Hourly weather observations"),
    ("AVG TEMPERATURE", f"{avg_temp:.1f}°C", "Actual air temperature"),
    ("FEELS LIKE", f"{avg_feels:.1f}°C", "Apparent temperature"),
    ("AVG HUMIDITY", f"{avg_humidity:.0f}%", "Relative humidity"),
    ("WIND SPEED", f"{avg_wind:.1f}", "km/h average"),
]
cols = st.columns(5)
for col, (label, value, note) in zip(cols, kpis):
    with col:
        st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)

# ---------- Charts ----------
st.markdown('<div class="section-head">01 / Temperature & Climate Trends</div>', unsafe_allow_html=True)
monthly = filtered.groupby(["Year", "Month"], as_index=False).agg(
    temperature=("Temperature (C)", "mean"),
    feels_like=("Apparent Temperature (C)", "mean"),
    humidity=("Humidity (%)", "mean")
)
monthly["Period"] = pd.to_datetime(monthly["Year"].astype(str) + "-" + monthly["Month"].astype(str) + "-01")
c1, c2 = st.columns([1.55, 1])
with c1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly["Period"], y=monthly["temperature"], name="Temperature", mode="lines+markers", line=dict(width=3, color="#63c7e8")))
    fig.add_trace(go.Scatter(x=monthly["Period"], y=monthly["feels_like"], name="Feels like", mode="lines", line=dict(width=2, color="#aa8cf2", dash="dot")))
    fig.update_layout(title="Monthly Average Temperature", xaxis_title="", yaxis_title="Temperature (°C)", template="plotly_dark", height=350, margin=dict(l=10,r=10,t=55,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h", y=1.12))
    st.plotly_chart(fig, use_container_width=True)
with c2:
    fig = px.histogram(filtered, x="Temperature (C)", nbins=35, title="Temperature Distribution", color_discrete_sequence=["#8e83e8"])
    fig.update_layout(template="plotly_dark", height=350, margin=dict(l=10,r=10,t=55,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="Temperature (°C)", yaxis_title="Records")
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="section-head">02 / Weather Conditions</div>', unsafe_allow_html=True)
c3, c4 = st.columns([1.1, 1])
with c3:
    summary_counts = filtered["Summary"].value_counts().head(12).reset_index()
    summary_counts.columns = ["Weather Condition", "Records"]
    fig = px.bar(summary_counts.sort_values("Records"), x="Records", y="Weather Condition", orientation="h", title="Most Frequent Weather Conditions", color="Records", color_continuous_scale=["#4b86b8", "#9a83e8"])
    fig.update_layout(template="plotly_dark", height=390, margin=dict(l=10,r=10,t=55,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)
with c4:
    precip_counts = filtered["Precip Type"].fillna("Not recorded").value_counts().reset_index()
    precip_counts.columns = ["Precipitation", "Records"]
    fig = px.pie(precip_counts, names="Precipitation", values="Records", hole=.62, title="Precipitation Type", color_discrete_sequence=["#63c7e8", "#a88af0", "#62748f"])
    fig.update_layout(template="plotly_dark", height=390, margin=dict(l=10,r=10,t=55,b=10), paper_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h", y=-.08))
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="section-head">03 / Humidity, Wind & Visibility</div>', unsafe_allow_html=True)
c5, c6 = st.columns(2)
with c5:
    fig = px.scatter(filtered.sample(min(5000, len(filtered)), random_state=7), x="Humidity (%)", y="Temperature (C)", color="Wind Speed (km/h)", title="Temperature vs Humidity", color_continuous_scale="Tealgrn", opacity=.65, hover_data=["Summary"])
    fig.update_layout(template="plotly_dark", height=360, margin=dict(l=10,r=10,t=55,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis_title="Temperature (°C)")
    st.plotly_chart(fig, use_container_width=True)
with c6:
    fig = px.scatter(filtered.sample(min(5000, len(filtered)), random_state=11), x="Wind Speed (km/h)", y="Visibility (km)", color="Humidity (%)", title="Wind Speed vs Visibility", color_continuous_scale="Purples", opacity=.65)
    fig.update_layout(template="plotly_dark", height=360, margin=dict(l=10,r=10,t=55,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

# ---------- Quick insights ----------
st.markdown('<div class="section-head">04 / Quick Insights</div>', unsafe_allow_html=True)
warmest = filtered.loc[filtered["Temperature (C)"].idxmax()]
coldest = filtered.loc[filtered["Temperature (C)"].idxmin()]
most_common = filtered["Summary"].mode().iloc[0]
i1, i2, i3 = st.columns(3)
for col, heading, value, detail in [
    (i1, "Warmest observation", f'{warmest["Temperature (C)"]:.1f}°C', str(warmest["Formatted Date"])),
    (i2, "Coldest observation", f'{coldest["Temperature (C)"]:.1f}°C', str(coldest["Formatted Date"])),
    (i3, "Most common condition", most_common, f'{(filtered["Summary"] == most_common).mean()*100:.1f}% of selected records'),
]:
    with col:
        st.markdown(f'<div class="metric-card"><div class="metric-label">{heading}</div><div class="metric-value" style="font-size:22px">{value}</div><div class="metric-note">{detail}</div></div>', unsafe_allow_html=True)

# ---------- Data table ----------
st.markdown('<div class="section-head">05 / Explore Raw Data</div>', unsafe_allow_html=True)
st.caption("Filtered records from the original CSV file.")
display_cols = ["Formatted Date", "Summary", "Precip Type", "Temperature (C)", "Apparent Temperature (C)", "Humidity", "Wind Speed (km/h)", "Visibility (km)", "Pressure (millibars)"]
st.dataframe(filtered[display_cols].head(1000), use_container_width=True, hide_index=True)
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("⬇ Download filtered data as CSV", data=csv, file_name="filtered_weather_data.csv", mime="text/csv")

st.markdown("---")
st.caption("Weather Intelligence Dashboard • Built from the provided weather_data.csv • Values are calculated from the selected records.")
