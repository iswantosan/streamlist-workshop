import streamlit as st
import os

def load_css(filename: str):
    # Path absolut ke folder assets
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", filename)
    try:
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"File CSS '{filename}' tidak ditemukan di folder assets.")
