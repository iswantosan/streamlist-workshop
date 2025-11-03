import streamlit as st
import pandas as pd
from utils.auth import login, is_logged_in, logout


if is_logged_in():
    st.set_page_config(page_title="Dashboard", page_icon="🔐", layout="centered")
    st.header("🏠 Dashboard")

    
    # Contoh DataFrame berisi koordinat
    # data = pd.DataFrame({
    #     "latitude": [-6.200000, -7.250445, -8.409518],
    #     "longitude": [106.816666, 112.768845, 115.188919],
    #     "kota": ["Jakarta", "Surabaya", "Denpasar"]
    # })

    # #st.dataframe(data)

    # st.subheader("🌍 Visualisasi Peta")
    # st.map(data, latitude="latitude", longitude="longitude", zoom=4)

    st.success(f"Anda sudah login sebagai **{st.session_state['username']}**.")
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.success("Berhasil logout.")
        st.rerun()
    st.stop()

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")
st.header("🔐 Login")

with st.form("login_form", clear_on_submit=False):
    u = st.text_input("Username", placeholder="username")
    p = st.text_input("Password", type="password", placeholder="••••••")
    col1, col2 = st.columns([1,1])
    with col1:
        submit = st.form_submit_button("Masuk")
    with col2:
        st.caption("Gunakan: admin/admin123")

if submit:
    if login(u, p):
        st.success("Login berhasil.")
        st.rerun()
    else:
        st.error("Username atau password salah.")
