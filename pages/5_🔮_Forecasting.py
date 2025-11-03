import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import timedelta

from utils.auth import is_logged_in

if not is_logged_in():
    st.warning("⚠️ Silakan login terlebih dahulu di halaman 🔐 Login.")
    st.stop()


# ================ PAGE CONFIG ================
st.set_page_config(page_title="Forecasting & Best Practice", page_icon="🔮", layout="wide")
st.header("🔮 Forecasting & Best Practice")
#st.caption("File: pages/4_🔮_Forecasting_&_Best_Practice.py")

# ================ DATA SOURCE ================
df = st.session_state.get("uploaded_df", None)
if df is None:
    st.warning("⚠️ Belum ada data di memori. Unggah data di halaman **📘 Data Excel** dahulu.")
    st.stop()

date_col = df.columns[0]
if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
    try:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    except Exception:
        pass

num_cols = df.select_dtypes(include="number").columns.tolist()
if not num_cols:
    st.error("Tidak ada kolom numerik untuk diforecast.")
    st.stop()

# ================ SIDEBAR / FILTER ================
with st.expander("⚙️ Pengaturan Forecast", expanded=True):
    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        target_y = st.selectbox("Target (Y)", num_cols, index=0)

    with c2:
        method = st.selectbox(
            "Metode",
            ["Linear Trend (Sederhana)", "Naive (Last Value)", "Rata-rata (Window)"],
            index=0
        )

    with c3:
        horizon = st.number_input("Horizon (langkah ke depan)", min_value=1, max_value=365, value=12, step=1)

    # Untuk smoothing opsional
    window = st.slider("Window (untuk Rata-rata)", min_value=2, max_value=60, value=7, help="Dipakai jika metode Rata-rata (Window) dipilih.")

# ================ HELPERS ================
def infer_step(dts: pd.Series) -> pd.Timedelta:
    """Ambil step waktu dominan; fallback median diff jika tidak jelas."""
    s = dts.sort_values().dropna().unique()
    if len(s) < 2:
        return pd.Timedelta(days=1)
    diffs = pd.Series(s[1:] - s[:-1])
    # gunakan modus diff jika ada; fallback median
    try:
        step = diffs.mode().iloc[0]
    except Exception:
        step = diffs.median()
    # guard: jika step==0, fallback 1 hari
    if step == pd.Timedelta(0):
        step = pd.Timedelta(days=1)
    return step

def make_future_dates(last_dt: pd.Timestamp, step: pd.Timedelta, n: int) -> pd.DatetimeIndex:
    return pd.date_range(start=last_dt + step, periods=n, freq=step)

def linear_trend_forecast(x_dt: pd.Series, y: pd.Series, n: int):
    """Linear regression sederhana pada indeks waktu (ordinal)."""
    # gunakan index berbasis urutan agar robust
    x_idx = np.arange(len(y))
    # fit y = a*x + b
    a, b = np.polyfit(x_idx, y.values.astype(float), 1)
    x_future = np.arange(len(y), len(y) + n)
    y_future = a * x_future + b
    return y_future

def naive_last_value(y: pd.Series, n: int):
    return np.repeat(y.dropna().iloc[-1], n)

def rolling_mean_forecast(y: pd.Series, n: int, window: int):
    base = y.rolling(window=window, min_periods=1).mean().iloc[-1]
    return np.repeat(float(base), n)

# ================ PREPARE DATA ================
work = df[[date_col, target_y]].dropna().copy()
work = work.sort_values(by=date_col)
if not pd.api.types.is_datetime64_any_dtype(work[date_col]):
    st.error(f"Kolom pertama (**{date_col}**) belum bertipe tanggal yang valid.")
    st.stop()

# pastikan tidak ada duplikat tanggal untuk plotting yang bersih
work = work.drop_duplicates(subset=[date_col])

# infer step & build future dates
step = infer_step(work[date_col])
future_index = make_future_dates(work[date_col].iloc[-1], step, horizon)

# ================ FORECASTING ================
if method == "Linear Trend (Sederhana)":
    y_hat = linear_trend_forecast(work[date_col], work[target_y], horizon)
elif method == "Naive (Last Value)":
    y_hat = naive_last_value(work[target_y], horizon)
else:
    y_hat = rolling_mean_forecast(work[target_y], horizon, window)

fcst_df = pd.DataFrame({date_col: future_index, target_y: y_hat})
fcst_df["Phase"] = "Forecast"
hist_df = work.copy()
hist_df["Phase"] = "History"

plot_df = pd.concat([hist_df, fcst_df], ignore_index=True)

# ================ VISUAL =================
left, right = st.columns([2, 1], gap="small")

with left:
    with st.expander("📈 Forecast Plot", expanded=True):
        fig = px.line(
            plot_df,
            x=date_col,
            y=target_y,
            color="Phase",
            markers=True,
            title=f"Forecast {target_y} – {method} (+{horizon})"
        )
        # gaya forecast: garis putus-putus
        # for i, tr in enumerate(fig.data):
        #     if tr.name == "Forecast":
        #         fig.data[i].line.update(dash="dash")
        # fig.update_layout(
        #     xaxis_title="Tanggal",
        #     yaxis_title=target_y,
        #     hovermode="x unified",
        #     legend_title="Keterangan",
        #     xaxis=dict(tickangle=-30)
        # )
        st.plotly_chart(fig, use_container_width=True)

with right:
    with st.expander("📋 Tabel Forecast", expanded=True):
        st.dataframe(
            fcst_df.rename(columns={date_col: "Tanggal", target_y: "Prediksi"})
        )
        # Download CSV
        csv = fcst_df.rename(columns={date_col: "Tanggal", target_y: "Prediksi"}).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Unduh Forecast (CSV)", data=csv, file_name=f"forecast_{target_y}.csv", mime="text/csv")


st.divider()
