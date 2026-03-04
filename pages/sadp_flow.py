import streamlit as st

st.set_page_config(page_title="SADP — Full Data Product", layout="wide")

st.markdown("""
<style>
.stButton>button { width: 100%; height: 42px; border-radius: 8px; font-size: 14px; }
.step-card { padding: 20px; border-radius: 12px; margin-bottom: 4px; }
.step-card.complete { background-color: #064e3b; border: 1px solid #059669; }
.step-card.current  { background-color: #1e3a5f; border: 1px solid #3b82f6; }
.step-card.pending  { background-color: #1f2937; border: 1px solid #374151; }
.step-card.locked   { background-color: #111827; border: 1px solid #1f2937; opacity: 0.5; }
.step-card h4 { margin: 0 0 4px 0; font-size: 15px; color: white; }
.step-card p  { margin: 0; font-size: 13px; color: #9ca3af; }
.step-badge { display: inline-block; font-size: 11px; font-weight: 600;
    padding: 2px 8px; border-radius: 10px; margin-bottom: 8px; }
.b-complete { background: #059669; color: white; }
.b-current  { background: #3b82f6; color: white; }
.b-pending  { background: #4b5563; color: white; }
.b-locked   { background: #374151; color: #9ca3af; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
STEPS = {
    1: {"label": "Depot",           "optional": False},
    2: {"label": "Quality Checks",  "optional": False},
    3: {"label": "Bundle",          "optional": False},
    4: {"label": "Spec",            "optional": False},
    5: {"label": "Scanner",         "optional": False},
}

if "sadp_completed_steps" not in st.session_state:
    st.session_state.sadp_completed_steps = set()

completed = st.session_state.sadp_completed_steps

# ─────────────────────────────────────────────────────────────────────────────
# NAVIGATION HELPER
# ─────────────────────────────────────────────────────────────────────────────
def go_to_step(n):
    if n == 1:
        st.session_state["depot_origin"] = "sadp_full"
        st.switch_page("pages/6_Depot.py")
    elif n == 2:
        st.switch_page("pages/2_SADP_Quality_Checks.py")
    elif n == 3:
        st.session_state["sadp_origin"] = "sadp_full"
        st.switch_page("pages/3_SADP_Bundle.py")
    elif n == 4:
        st.session_state["sadp_origin"] = "sadp_full"
        st.switch_page("pages/4_SADP_Spec.py")
    elif n == 5:
        st.session_state["sadp_origin"] = "sadp_full"
        st.switch_page("pages/5_SADP_Scanner.py")

def is_unlocked(n):
    return True  # All steps always accessible during testing

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.title("SADP — Full Data Product")

nav_l, _, nav_r = st.columns([1, 4, 1.5])
with nav_l:
    if st.button("← Back to Home"):
        st.session_state.home_screen = "full_dp"
        st.switch_page("app.py")
with nav_r:
    if st.button("Start Over"):
        for k in ["sadp_completed_steps", "sadp_depot_name"]:
            st.session_state.pop(k, None)
        st.rerun()

st.divider()

done_count = len(completed)
st.progress(done_count / 5, text=f"{done_count} of 5 steps done")
st.markdown(" ")

# ─────────────────────────────────────────────────────────────────────────────
# STEP CARDS
# ─────────────────────────────────────────────────────────────────────────────
for n, info in STEPS.items():
    is_done  = n in completed
    unlocked = is_unlocked(n)

    if is_done:
        card_cls, badge_cls, badge_txt = "complete", "b-complete", "Complete"
    elif not unlocked:
        card_cls, badge_cls, badge_txt = "locked",   "b-locked",   "Locked"
    elif n == min(s for s in STEPS if s not in completed):
        card_cls, badge_cls, badge_txt = "current",  "b-current",  "Current"
    else:
        card_cls, badge_cls, badge_txt = "pending",  "b-pending",  "Pending"

    info_line = ""
    if n == 1 and st.session_state.get("sadp_depot_name"):
        info_line = f"Depot: {st.session_state.sadp_depot_name}"

    # Only Quality Checks (step 2) is still Coming Soon
    coming_soon = n == 2
    coming_note = " — Coming Soon" if coming_soon else ""

    col_card, col_btn = st.columns([4, 1])
    with col_card:
        st.markdown(f"""
            <div class="step-card {card_cls}">
                <span class="step-badge {badge_cls}">{badge_txt}</span>
                <h4>Step {n} — {info['label']}{coming_note}</h4>
                {"<p>" + info_line + "</p>" if info_line else ""}
            </div>
        """, unsafe_allow_html=True)

    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if is_done:
            if st.button("Edit", key=f"sadp_edit_{n}"):
                go_to_step(n)
        elif unlocked:
            if coming_soon:
                st.button("Coming Soon", key=f"sadp_cs_{n}", disabled=True)
            else:
                if st.button("Start", key=f"sadp_start_{n}", type="primary"):
                    go_to_step(n)
        else:
            st.button("Locked", key=f"sadp_locked_{n}", disabled=True)

    st.markdown(" ")

if len(completed) == 5:
    st.success("All steps complete. Your SADP files are ready.")