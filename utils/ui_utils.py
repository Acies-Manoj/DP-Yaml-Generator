"""
ui_utils.py — Shared UI helpers for all pages.
Loads the global CSS design system and provides reusable HTML components.
"""

import os
from datetime import datetime
import streamlit as st


# ── Download History Tracker ───────────────────────────────────────────────────

def track_download(filename: str, data: str, mime: str = "text/plain"):
    """
    Call this instead of st.download_button wherever files are downloaded.
    Logs the file to session-level download history AND renders the button.
    Returns the download button widget.
    """
    if "download_history" not in st.session_state:
        st.session_state.download_history = []

    # Check if already tracked this session (avoid duplicates on re-render)
    existing = [f["filename"] for f in st.session_state.download_history]
    if filename not in existing:
        st.session_state.download_history.insert(0, {
            "filename": filename,
            "data":     data,
            "mime":     mime,
            "time":     datetime.now().strftime("%H:%M"),
        })
        # Cap history at 10 items
        st.session_state.download_history = st.session_state.download_history[:10]

    return st.download_button(
        label=f"⬇ Download {filename}",
        data=data,
        file_name=filename,
        mime=mime,
        use_container_width=True,
    )


def _file_icon(filename: str) -> str:
    """Return an emoji icon based on file extension."""
    if filename.endswith(".sql"):   return "🗄️"
    if filename.endswith(".yaml") or filename.endswith(".yml"): return "📄"
    if filename.endswith(".zip"):   return "🗜️"
    return "📁"


def render_sidebar():
    """Render the branded sidebar — logo, download history, home button."""
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

        # ── Home button ────────────────────────────────────────────────────
        if st.button("⬅ Back to Home", key="_sb_home", use_container_width=True):
            for _k in ["sm_mode", "sm_origin", "semantic_section",
                        "dp_origin", "dp_step", "dp_entry_step",
                        "depot_origin", "depot_specific_file", "flare_origin",
                        "cadp_qc_origin", "sadp_qc_origin"]:
                st.session_state.pop(_k, None)
            st.session_state["home_screen"] = "home"
            st.switch_page("app.py")

        st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

        # ── Download History ───────────────────────────────────────────────
        history = st.session_state.get("download_history", [])

        st.markdown(
            '<div class="sb-context-label" style="padding: 0 18px; margin-bottom: 8px;">'
            'GENERATED FILES</div>',
            unsafe_allow_html=True,
        )

        if not history:
            st.markdown(
                '<div style="padding: 0 18px;">'
                '<p style="font-size:12px; color:#4b5563; line-height:1.6; margin:0;">'
                'No files generated yet.<br>Files you download will appear here for quick re-access.'
                '</p></div>',
                unsafe_allow_html=True,
            )
        else:
            for item in history:
                icon = _file_icon(item["filename"])
                # Card per file
                st.markdown(
                    f'<div class="sb-file-item">'
                    f'<span class="sb-file-icon">{icon}</span>'
                    f'<div class="sb-file-info">'
                    f'<span class="sb-file-name">{item["filename"]}</span>'
                    f'<span class="sb-file-time">{item["time"]}</span>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                st.download_button(
                    label="Re-download",
                    data=item["data"],
                    file_name=item["filename"],
                    mime=item["mime"],
                    use_container_width=True,
                    key=f"_sb_dl_{item['filename']}_{item['time']}",
                )

            # Clear history button
            st.markdown('<div style="padding: 0 4px; margin-top: 4px;">', unsafe_allow_html=True)
            if st.button("🗑 Clear History", key="_sb_clear_history", use_container_width=True):
                st.session_state.download_history = []
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

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