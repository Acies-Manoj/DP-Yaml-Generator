"""
ui_utils.py — Shared UI helpers for all pages.
Loads the global CSS design system and provides reusable HTML components.
"""

import os
import streamlit as st


def _clear_nav_state():
    """Clear all flow-specific session state keys before navigating."""
    for _k in ["sm_mode", "sm_origin", "semantic_section",
                "dp_origin", "dp_step", "dp_entry_step",
                "depot_origin", "depot_specific_file", "flare_origin",
                "cadp_qc_origin", "sadp_qc_origin"]:
        st.session_state.pop(_k, None)


def render_sidebar():
    """Render the branded sidebar — logo, back to home, quick jump links."""
    with st.sidebar:

        # ── Logo / app name ────────────────────────────────────────────────
        st.markdown(
            '<div class="sb-header">'
            '<div class="sb-logo">DP YAML<br>Generator</div>'
            '<div class="sb-tagline">DataOS · Internal Tool</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

        # ── Back to Home ───────────────────────────────────────────────────
        if st.button("⬅ Back to Home", key="_sb_home", use_container_width=True):
            _clear_nav_state()
            st.session_state["home_screen"] = "home"
            st.switch_page("app.py")

        st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

        # ── Quick Jump ─────────────────────────────────────────────────────
        st.markdown(
            '<div class="sb-context-label" style="padding: 0 18px 8px 18px;">QUICK JUMP</div>',
            unsafe_allow_html=True,
        )

        # Each entry: (label, emoji, page, session_state_overrides)
        quick_links = [
            ("SQL File",        "🗄️", "pages/1_CADP.py",                 {"sm_origin": "specific", "sm_mode": "individual", "semantic_section": "sql"}),
            ("Table YAML",      "📄", "pages/1_CADP.py",                 {"sm_origin": "specific", "sm_mode": "individual", "semantic_section": "table"}),
            ("View YAML",       "📄", "pages/1_CADP.py",                 {"sm_origin": "specific", "sm_mode": "individual", "semantic_section": "view"}),
            ("Lens Deployment", "🔭", "pages/1_CADP.py",                 {"sm_origin": "specific", "sm_mode": "individual", "semantic_section": "lens"}),
            ("Flare Job",       "⚡", "pages/8_CADP_Flare.py",           {"flare_origin": "specific"}),
            ("Depot",           "🏗️", "pages/6_Depot.py",               {"depot_origin": "specific", "depot_specific_file": "depot"}),
            ("Bundle",          "📦", "pages/9_CADP_DP_Deployment.py",   {"dp_origin": "specific", "dp_step": 1, "dp_entry_step": 1}),
            ("DP Scanner",      "🔍", "pages/9_CADP_DP_Deployment.py",   {"dp_origin": "specific", "dp_step": 3, "dp_entry_step": 3}),
            ("Quality Checks",  "✅", "pages/1_CADP.py",                 {"sm_origin": "specific", "sm_mode": "individual", "semantic_section": "qc"}),
        ]

        for label, icon, page, state_overrides in quick_links:
            st.markdown(
                f'<div class="sb-quick-item">'
                f'<span class="sb-quick-icon">{icon}</span>'
                f'<span class="sb-quick-label">{label}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button(label, key=f"_sb_qj_{label}", use_container_width=True):
                _clear_nav_state()
                for k, v in state_overrides.items():
                    st.session_state[k] = v
                st.session_state["home_screen"] = "specific"
                st.switch_page(page)

        # ── Footer ─────────────────────────────────────────────────────────
        st.markdown(
            '<div class="sb-footer">⚙️ YAML & SQL Generation</div>',
            unsafe_allow_html=True,
        )


def load_global_css():
    """Inject the global CSS design system and render the branded sidebar."""
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    try:
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

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