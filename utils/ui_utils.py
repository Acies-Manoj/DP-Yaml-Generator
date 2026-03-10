"""
ui_utils.py — Shared UI helpers for all pages.
Loads the global CSS design system and provides reusable HTML components.
"""

import os
import streamlit as st


# ── Context detection ──────────────────────────────────────────────────────────

_SECTION_LABELS = {
    "sql":         ("📄 SQL File",          "blue"),
    "table":       ("📐 Table YAML",        "blue"),
    "view":        ("👁️ View YAML",         "blue"),
    "lens":        ("🔭 Lens Deployment",   "blue"),
    "qc":          ("✅ Quality Checks",    "green"),
    "user_groups": ("👥 User Groups",       "blue"),
    "repo_cred":   ("🔐 Repo Credential",  "blue"),
}

_DP_STEP_LABELS = {1: "📦 Bundle", 2: "📋 Spec", 3: "🔍 DP Scanner"}

_CADP_STEP_LABELS = {
    1: "Depot",
    2: "Semantic Model",
    3: "Quality Checks",
    4: "Flare Job",
    5: "DP Deployment",
}

_SADP_STEP_LABELS = {
    1: "Depot",
    2: "Quality Checks",
    3: "Bundle",
    4: "Spec",
    5: "Scanner",
}


def _get_sidebar_context():
    """Return (label_html, accent_class) based on current session state."""
    ss = st.session_state

    # ── CADP full flow pages ───────────────────────────────────────────────
    if (ss.get("sm_origin") == "cadp_full"
            or ss.get("cadp_qc_origin") == "cadp_full"
            or ss.get("depot_origin") == "cadp_full"
            or ss.get("flare_origin") == "cadp_full"):
        completed = len(ss.get("cadp_completed_steps", set()))
        current   = completed + 1
        step_name = _CADP_STEP_LABELS.get(current, "")
        return f"🔵 CADP Full Flow<br><small style='color:#6b7280'>Step {current}/5 — {step_name}</small>", "blue"

    # ── SADP full flow pages ───────────────────────────────────────────────
    if ss.get("sadp_qc_origin") or ss.get("dp_origin") == "sadp_full":
        completed = len(ss.get("sadp_completed_steps", set()))
        current   = completed + 1
        step_name = _SADP_STEP_LABELS.get(current, "")
        return f"🟢 SADP Full Flow<br><small style='color:#6b7280'>Step {current}/5 — {step_name}</small>", "green"

    # ── sadp_flow / cadp_flow hub pages ───────────────────────────────────
    if ss.get("home_screen") == "full_dp":
        return "🚀 Full Data Product", "purple"

    # ── Individual Semantic Model section ─────────────────────────────────
    section = ss.get("semantic_section")
    if ss.get("sm_mode") == "individual" and section:
        lbl, accent = _SECTION_LABELS.get(section, (section, "blue"))
        return f"📁 File Builder<br><small style='color:#6b7280'>{lbl}</small>", accent

    # ── DP Deployment — individual ─────────────────────────────────────────
    if ss.get("dp_origin") == "specific":
        dp_step = ss.get("dp_step", 1)
        lbl     = _DP_STEP_LABELS.get(dp_step, "DP Deployment")
        return f"📁 File Builder<br><small style='color:#6b7280'>{lbl}</small>", "purple"

    # ── CADP full flow — DP Deployment ────────────────────────────────────
    if ss.get("dp_origin") == "cadp_full":
        dp_step = ss.get("dp_step", 1)
        lbl     = _DP_STEP_LABELS.get(dp_step, "DP Deployment")
        return f"🔵 CADP Full Flow<br><small style='color:#6b7280'>Step 5 — {lbl}</small>", "blue"

    # ── Depot / Flare / other specific file pages ─────────────────────────
    if ss.get("depot_origin") == "specific":
        file_map = {
            "secret_r":  "🔐 Secret (Read)",
            "secret_rw": "🔑 Secret (R/W)",
            "depot":     "🏗️ Depot",
            "scanner":   "🔍 Depot Scanner",
        }
        lbl = file_map.get(ss.get("depot_specific_file", ""), "📁 Depot File")
        return f"📁 File Builder<br><small style='color:#6b7280'>{lbl}</small>", "teal"

    if ss.get("flare_origin") == "specific":
        return "📁 File Builder<br><small style='color:#6b7280'>⚡ Flare Job</small>", "orange"

    # ── Generic file builder ───────────────────────────────────────────────
    if ss.get("home_screen") == "specific":
        return "📁 File Builder", "blue"

    return "🏠 Home", "blue"


def render_sidebar():
    """Render the branded sidebar panel. Called automatically by load_global_css()."""
    label_html, accent = _get_sidebar_context()

    with st.sidebar:
        # ── Logo / app name ────────────────────────────────────────────────
        st.markdown(
            '<div class="sb-header">'
            '<div class="sb-logo">DP YAML<br>Generator</div>'
            '<div class="sb-tagline">DataOS · Internal Tool</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # ── Current context ────────────────────────────────────────────────
        st.markdown(
            f'<div class="sb-context">'
            f'<div class="sb-context-label">Current Context</div>'
            f'<div class="sb-context-value {accent}">{label_html}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

        # ── Home button ────────────────────────────────────────────────────
        if st.button("⬅ Back to Home", key="_sb_home", use_container_width=True):
            # Clear flow-specific keys so landing on app.py is clean
            for _k in ["sm_mode", "sm_origin", "semantic_section",
                        "dp_origin", "dp_step", "dp_entry_step",
                        "depot_origin", "depot_specific_file", "flare_origin",
                        "cadp_qc_origin", "sadp_qc_origin"]:
                st.session_state.pop(_k, None)
            st.session_state["home_screen"] = "home"
            st.switch_page("app.py")


def load_global_css():
    """Inject the global CSS design system and render the branded sidebar."""
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    try:
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # Graceful fallback — page still works without global styles

    render_sidebar()



def section_header(icon: str, title: str):
    """Render a styled section header with left accent border."""
    st.markdown(
        f'<div class="section-header"><span>{icon}</span><h4>{title}</h4></div>',
        unsafe_allow_html=True,
    )


def group_label(title: str, dot_class: str = "dot-blue"):
    """Render a category group label with a colored dot."""
    st.markdown(
        f'<div class="group-label"><span class="dot {dot_class}"></span>{title}</div>',
        unsafe_allow_html=True,
    )


def yaml_tab(filename: str):
    """Render a code-editor-style tab bar above a YAML preview block."""
    st.markdown(
        f'<div class="yaml-tab"><span class="yaml-dot"></span>{filename}</div>',
        unsafe_allow_html=True,
    )


def app_footer():
    """Render the app footer."""
    st.markdown(
        '<div class="app-footer">⚙️ &nbsp; Internal Automation Tool — YAML & SQL Generation</div>',
        unsafe_allow_html=True,
    )