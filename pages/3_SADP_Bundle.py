import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.generators import generate_sadp_bundle_yaml
from utils.examples import EXAMPLE_BUNDLE, show_example

st.set_page_config(page_title="SADP — Bundle", layout="wide")
from utils.ui_utils import load_global_css
load_global_css()

st.markdown("""
<style>
.stButton>button { width: 100%; height: 45px; border-radius: 8px; font-size: 15px; }
</style>
""", unsafe_allow_html=True)

SADP_BUNDLE_KEYS = [
    "sadp_bundle_step", "sadp_bundle_preview_mode",
    "sadp_bundle_tags",
    "sadp_bundle_name", "sadp_generated_bundle", "sadp_bundle_qc_file",
]

for k, v in [
    ("sadp_bundle_preview_mode", False),
    ("sadp_bundle_tags",         ["dataproduct"]),
]:
    if k not in st.session_state:
        st.session_state[k] = v

_origin = st.session_state.get("sadp_origin", "specific")

def _back():
    for k in SADP_BUNDLE_KEYS:
        st.session_state.pop(k, None)
    if _origin == "sadp_full":
        st.switch_page("pages/sadp_flow.py")
    else:
        st.session_state.home_screen = "specific"
        st.switch_page("app.py")

nav_l, _, nav_r = st.columns([1, 4, 1.5])
with nav_l:
    if st.button("← Back"):
        _back()
with nav_r:
    if st.button("✖ Cancel / Start Over"):
        for k in SADP_BUNDLE_KEYS:
            st.session_state.pop(k, None)
        st.rerun()

st.divider()

if not st.session_state.sadp_bundle_preview_mode:

    st.subheader("Bundle")
    show_example(st, "Bundle YAML", EXAMPLE_BUNDLE)
    st.caption(
        "The Bundle groups all resources for your SADP data product. "
        "Quality Checks is the primary active resource. API and policy blocks are commented for future use."
    )

    with st.form("sadp_bundle_form"):

        st.markdown("#### Metadata")
        bm1, bm2 = st.columns(2)
        with bm1:
            b_name = st.text_input(
                "Bundle Name *",
                placeholder="e.g. retail-sales-bundle",
                help="Must be unique in DataOS. Do not use spaces.",
            )
            b_layer = st.text_input("Layer", value="user")
        with bm2:
            b_desc = st.text_area(
                "Description *",
                value=st.session_state.get("sadp_bundle_desc", "Bundle resource for the data product"),
                height=100,
            )

        _bth1, _bth2 = st.columns([5, 1])
        with _bth1: st.markdown("**Tags**")
        with _bth2:
            if st.form_submit_button("➕ Add", key="sadp_add_btag"):
                st.session_state.sadp_bundle_tags.append(""); st.rerun()
        updated_tags = []
        for i, tag in enumerate(st.session_state.sadp_bundle_tags):
            tc1, tc2 = st.columns([5, 1])
            with tc1:
                val = st.text_input(f"Tag {i+1}", value=tag, key=f"sadp_btag_{i}",
                                    placeholder="e.g. dataproduct", label_visibility="collapsed")
                updated_tags.append(val)
            with tc2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("❌", key=f"sadp_rm_btag_{i}"):
                    st.session_state.sadp_bundle_tags.pop(i); st.rerun()

        st.divider()

        st.markdown("#### Quality Checks Resource")
        st.caption("The primary active resource for a SADP bundle. Leave blank to render as a comment.")
        qc1, qc2 = st.columns(2)
        with qc1:
            b_qc_file = st.text_input(
                "Quality Checks File Path",
                value=st.session_state.get("sadp_bundle_qc_file", "build/quality-checks/checks.yml"),
                help="Relative path to the quality checks YAML in your repo.",
            )
        with qc2:
            b_qc_ws = st.text_input("Workspace", value="public")

        st.markdown(" ")
        submit = st.form_submit_button("Preview Bundle YAML →", use_container_width=True)

    st.session_state.sadp_bundle_tags = updated_tags

    if submit:
        if not b_name.strip():
            st.error("Bundle Name is required.")
        elif not b_desc.strip():
            st.error("Description is required.")
        else:
            st.session_state.sadp_bundle_name      = b_name.strip()
            st.session_state.sadp_bundle_qc_file   = b_qc_file.strip()
            st.session_state.sadp_generated_bundle = generate_sadp_bundle_yaml({
                "name":         b_name.strip(),
                "description":  b_desc.strip(),
                "tags":         [t for t in st.session_state.sadp_bundle_tags if t.strip()],
                "layer":        b_layer.strip() or "user",
                "qc_file":      b_qc_file.strip(),
                "qc_workspace": b_qc_ws.strip(),
            })
            st.session_state.sadp_bundle_preview_mode = True
            st.rerun()

else:
    st.subheader("Bundle YAML Preview")
    st.code(st.session_state.sadp_generated_bundle, language="yaml")
    pc1, pc2 = st.columns(2)
    with pc1:
        if st.button("← Edit Bundle"):
            st.session_state.sadp_bundle_preview_mode = False
            st.rerun()
    with pc2:
        if st.button("Continue to Spec →", use_container_width=True, type="primary"):
            st.session_state.sadp_bundle_preview_mode = False
            if _origin == "sadp_full":
                if "sadp_completed_steps" not in st.session_state:
                    st.session_state.sadp_completed_steps = set()
                st.session_state.sadp_completed_steps.add(3)
            st.switch_page("pages/4_SADP_Spec.py")