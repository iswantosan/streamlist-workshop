import streamlit as st

# ====== Konfigurasi user hardcode ======
USERNAME = "admin"
PASSWORD = "123"

def login(username, password):
    """Login sederhana"""
    if username == USERNAME and password == PASSWORD:
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        return True
    return False

def logout():
    """Hapus session login"""
    st.session_state["logged_in"] = False
    st.session_state.pop("username", None)

def is_logged_in():
    """Cek status login"""
    return st.session_state.get("logged_in", False)
