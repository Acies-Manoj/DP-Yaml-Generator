import streamlit as st

st.set_page_config(page_title="Data Product File Generator", layout="wide")

st.markdown("""
<style>
.choice-card {
    padding: 30px;
    border-radius: 12px;
    background-color: #1f2937;
    color: white;
    text-align: center;
    height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.choice-card h3 { margin-bottom: 10px; font-size: 20px; }
.choice-card p  { font-size: 13px; color: #9ca3af; }

.flow-card {
    padding: 20px;
    border-radius: 12px;
    background-color: #111827;
    color: white;
    min-height: 120px;
}
.flow-card h4 { margin-bottom: 6px; font-size: 15px; }
.flow-card p  { font-size: 13px; color: #9ca3af; margin: 0; }

.group-label {
    font-size: 12px;
    font-weight: 700;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 20px 0 8px 0;
}

.stButton>button {
    width: 100%;
    height: 42px;
    border-radius: 8px;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

if "home_screen" not in st.session_state:
    st.session_state.home_screen = "home"

# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 0 — Home
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.home_screen == "home":
    st.title("Data Product File Generator")
    st.markdown("### What would you like to do?")
    st.markdown(" ")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
            <div class="choice-card">
                <h3>Generate a Specific File</h3>
                <p>Pick any single file — Depot, Flare, Semantic Model files,
                DP Deployment files — fill in the details and download it.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Generate a Specific File", use_container_width=True):
            st.session_state.home_screen = "specific"
            st.rerun()

    with col_b:
        st.markdown("""
            <div class="choice-card">
                <h3>Generate a Full Data Product</h3>
                <p>Walk through the complete step-by-step flow for a
                Source-Aligned (SADP) or Consumer-Aligned (CADP) data product.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Generate a Full Data Product", use_container_width=True):
            st.session_state.home_screen = "full_dp"
            st.rerun()

    st.divider()
    st.caption("Internal Automation Tool for YAML & SQL Generation")


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 1 — Specific File (grouped cards)
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.home_screen == "specific":
    st.title("Data Product File Generator")

    if st.button("← Back", key="spec_back"):
        st.session_state.home_screen = "home"
        st.rerun()

    st.markdown("### Generate a Specific File")
    st.caption("Select any file. Each builder is standalone — no dependencies required.")
    st.markdown(" ")

    # Group: Connection
    st.markdown('<div class="group-label">Connection</div>', unsafe_allow_html=True)
    g1c1, g1c2, g1c3, g1c4 = st.columns(4)
    with g1c1:
        st.markdown("""<div class="flow-card"><h4>Instance Secret (Read)</h4>
            <p>Read-only credentials for a depot connection.</p></div>""", unsafe_allow_html=True)
        if st.button("Open", key="spec_secret_r"):
            st.session_state["depot_origin"] = "specific"
            st.session_state["depot_specific_file"] = "secret_r"
            st.switch_page("pages/6_Depot.py")
    with g1c2:
        st.markdown("""<div class="flow-card"><h4>Instance Secret (Read-Write)</h4>
            <p>Read-write credentials for a depot connection.</p></div>""", unsafe_allow_html=True)
        if st.button("Open", key="spec_secret_rw"):
            st.session_state["depot_origin"] = "specific"
            st.session_state["depot_specific_file"] = "secret_rw"
            st.switch_page("pages/6_Depot.py")
    with g1c3:
        st.markdown("""<div class="flow-card"><h4>Depot</h4>
            <p>Depot connection configuration for a data source.</p></div>""", unsafe_allow_html=True)
        if st.button("Open", key="spec_depot"):
            st.session_state["depot_origin"] = "specific"
            st.session_state["depot_specific_file"] = "depot"
            st.switch_page("pages/6_Depot.py")
    with g1c4:
        st.markdown("""<div class="flow-card"><h4>Depot Scanner</h4>
            <p>Scanner workflow to catalog a depot in Metis.</p></div>""", unsafe_allow_html=True)
        if st.button("Open", key="spec_depot_scanner"):
            st.session_state["depot_origin"] = "specific"
            st.session_state["depot_specific_file"] = "scanner"
            st.switch_page("pages/6_Depot.py")

    # Group: Transformation
    st.markdown('<div class="group-label">Transformation</div>', unsafe_allow_html=True)
    g2c1, g2c2, g2c3, g2c4 = st.columns(4)
    with g2c1:
        st.markdown("""<div class="flow-card"><h4>Flare Job</h4>
            <p>Flare workflow for data ingestion and transformation.</p></div>""", unsafe_allow_html=True)
        if st.button("Open", key="spec_flare"):
            st.session_state["flare_origin"] = "specific"
            st.switch_page("pages/8_CADP_Flare.py")

    # Group: Semantic Model
    st.markdown('<div class="group-label">Semantic Model</div>', unsafe_allow_html=True)
    g3c1, g3c2, g3c3, g3c4 = st.columns(4)
    with g3c1:
        st.markdown("""<div class="flow-card"><h4>SQL File</h4>
            <p>SELECT query for a semantic model table.</p></div>""", unsafe_allow_html=True)
        if st.button("Open", key="spec_sql"):
            st.session_state["sm_origin"] = "specific"
            st.session_state["sm_mode"] = "individual"
            st.session_state["semantic_section"] = "sql"
            st.switch_page("pages/1_CADP.py")
    with g3c2:
        st.markdown("""<div class="flow-card"><h4>Table YAML</h4>
            <p>Dimensions, measures, joins and segments.</p></div>""", unsafe_allow_html=True)
        if st.button("Open", key="spec_table"):
            st.session_state["sm_origin"] = "specific"
            st.session_state["sm_mode"] = "individual"
            st.session_state["semantic_section"] = "table"
            st.switch_page("pages/1_CADP.py")
    with g3c3:
        st.markdown("""<div class="flow-card"><h4>View YAML</h4>
            <p>Views referencing semantic model tables.</p></div>""", unsafe_allow_html=True)
        if st.button("Open", key="spec_view"):
            st.session_state["sm_origin"] = "specific"
            st.session_state["sm_mode"] = "individual"
            st.session_state["semantic_section"] = "view"
            st.switch_page("pages/1_CADP.py")
    with g3c4:
        st.markdown("""<div class="flow-card"><h4>Lens Deployment</h4>
            <p>Deployment configuration for Lens.</p></div>""", unsafe_allow_html=True)
        if st.button("Open", key="spec_lens"):
            st.session_state["sm_origin"] = "specific"
            st.session_state["sm_mode"] = "individual"
            st.session_state["semantic_section"] = "lens"
            st.switch_page("pages/1_CADP.py")

    # Group: DP Deployment
    st.markdown('<div class="group-label">DP Deployment</div>', unsafe_allow_html=True)
    g4c1, g4c2, g4c3, g4c4 = st.columns(4)
    with g4c1:
        st.markdown("""<div class="flow-card"><h4>Bundle</h4>
            <p>Bundle configuration for a data product.</p></div>""", unsafe_allow_html=True)
        if st.button("Open", key="spec_bundle"):
            st.session_state["dp_origin"] = "specific"
            st.session_state["dp_step"] = 1
            st.switch_page("pages/9_CADP_DP_Deployment.py")
    with g4c2:
        st.markdown("""<div class="flow-card"><h4>Spec</h4>
            <p>Specification file for a data product.</p></div>""", unsafe_allow_html=True)
        if st.button("Open", key="spec_spec"):
            st.session_state["dp_origin"] = "specific"
            st.session_state["dp_step"] = 2
            st.switch_page("pages/9_CADP_DP_Deployment.py")
    with g4c3:
        st.markdown("""<div class="flow-card"><h4>DP Scanner</h4>
            <p>Scanner workflow to catalog a data product.</p></div>""", unsafe_allow_html=True)
        if st.button("Open", key="spec_dp_scanner"):
            st.session_state["dp_origin"] = "specific"
            st.session_state["dp_step"] = 3
            st.switch_page("pages/9_CADP_DP_Deployment.py")

    # Group: Quality Checks
    st.markdown('<div class="group-label">Quality Checks</div>', unsafe_allow_html=True)
    g5c1, g5c2, g5c3, g5c4 = st.columns(4)
    with g5c1:
        st.markdown("""<div class="flow-card"><h4>Quality Checks</h4>
            <p>Data quality rules and validation checks.</p></div>""", unsafe_allow_html=True)
        st.button("Coming Soon", key="spec_qc", disabled=True)

    st.divider()
    st.caption("Internal Automation Tool for YAML & SQL Generation")


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 2 — Full Data Product: SADP or CADP
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.home_screen == "full_dp":
    st.title("Data Product File Generator")

    if st.button("← Back", key="full_dp_back"):
        st.session_state.home_screen = "home"
        st.rerun()

    st.markdown("### Full Data Product — Select type")
    st.markdown(" ")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
            <div class="choice-card">
                <h3>SADP</h3>
                <p><strong>Source-Aligned Data Product</strong><br><br>
                Step-by-step: Depot, Quality Checks, Bundle, Spec, Scanner.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Create SADP", use_container_width=True):
            st.switch_page("pages/sadp_flow.py")

    with col_b:
        st.markdown("""
            <div class="choice-card">
                <h3>CADP</h3>
                <p><strong>Consumer-Aligned Data Product</strong><br><br>
                Step-by-step: Depot, Semantic Model, Quality Checks (optional),
                Flare Job (optional), DP Deployment.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Create CADP", use_container_width=True):
            st.switch_page("pages/cadp_flow.py")

    st.divider()
    st.caption("Internal Automation Tool for YAML & SQL Generation")