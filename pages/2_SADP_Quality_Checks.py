import streamlit as st

st.set_page_config(page_title="SADP — Quality Checks", page_icon="✅", layout="wide")

st.markdown("""
<style>
.stButton>button { width: 100%; height: 45px; border-radius: 8px; font-size: 15px; }
</style>
""", unsafe_allow_html=True)

if st.button("← Back to Home"):
    st.switch_page("app.py")

st.title("✅ SADP — Quality Checks")
st.markdown("---")

st.info("""
**Coming Soon**

Define data quality rules and validation checks for your **source-aligned** data product.

Planned features:
- Rule builder (not-null, uniqueness, range checks, regex patterns)
- YAML output compatible with the DataOS Quality Check spec
- Upload existing check definitions to edit
""")

st.caption("Planned for a future release.")
