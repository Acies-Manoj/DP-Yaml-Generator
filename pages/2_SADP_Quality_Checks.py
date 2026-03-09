import streamlit as st

st.set_page_config(page_title="SADP — Quality Checks", page_icon="✅", layout="wide")

# Set origin so the shared QC page knows to route back to SADP flow
st.session_state["sadp_qc_origin"] = "sadp_full"
st.switch_page("pages/7_CADP_Quality_Checks.py")