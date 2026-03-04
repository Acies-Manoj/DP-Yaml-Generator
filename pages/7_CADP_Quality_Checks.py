import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.qc_utils import (
    build_default_checks,
    generate_qc_excel,
    parse_qc_excel,
    generate_qc_yaml,
)

st.set_page_config(page_title="CADP — Quality Checks", page_icon="✅", layout="wide")

st.markdown("""
<style>
.stButton>button { width: 100%; height: 45px; border-radius: 8px; font-size: 15px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
QC_KEYS = [
    "qc_step", "qc_default_rows", "qc_custom_checks",
    "qc_generated_yaml", "qc_dataset_ref", "qc_name",
    "qc_uploaded_rows",
]

for k, v in [
    ("qc_step", 1),
]:
    if k not in st.session_state:
        st.session_state[k] = v

_origin = st.session_state.get("cadp_qc_origin", "specific")

# ─────────────────────────────────────────────────────────────────────────────
# Pull ALL tables from bundle_tables — let user pick which one to work on
# ─────────────────────────────────────────────────────────────────────────────
_bundle_tables = st.session_state.get("bundle_tables", [])
_valid_tables  = [t for t in _bundle_tables if t.get("name") and t.get("dims")]

# Fallback: individual / old-style session keys
_fallback_dims  = st.session_state.get("bundle_tbl_dims") or st.session_state.get("tbl_dimensions") or []
_fallback_name  = (st.session_state.get("bundle_tbl_name", "") or st.session_state.get("tbl_name_for_file", "") or st.session_state.get("ind_sf_last_table", "")).strip()
_fallback_db    = (st.session_state.get("bundle_db", "") or st.session_state.get("ind_sf_last_db", "")).strip()
_fallback_schema= (st.session_state.get("bundle_schema", "") or st.session_state.get("ind_sf_last_schema", "")).strip()

if _valid_tables:
    # ── Table selector ────────────────────────────────────────────────────────
    _completed = st.session_state.get("qc_completed_tables", set())   # set of table names already done
    _labels = [
        ("✅ " if t["name"] in _completed else "") + f"{t.get('schema','')}.{t['name']}  ({len(t['dims'])} cols)"
        for t in _valid_tables
    ]
    # Default selection: first table not yet completed, or first table
    _default_idx = next(
        (i for i, t in enumerate(_valid_tables) if t["name"] not in _completed), 0
    )
    _prev_idx = st.session_state.get("qc_selected_table_idx", _default_idx)

    _sel_label = st.selectbox(
        "Select table to generate Quality Checks for:",
        _labels,
        index=_prev_idx,
        key="qc_table_selector",
    )
    _sel_idx = _labels.index(_sel_label)

    # If user switched to a different table — clear step state so they start fresh
    if _sel_idx != st.session_state.get("qc_selected_table_idx", _sel_idx):
        for k in ["qc_step","qc_default_rows","qc_custom_checks","qc_generated_yaml",
                  "qc_dataset_ref","qc_name","qc_uploaded_rows","qc_table_name",
                  "qc_workspace","qc_engine","qc_cluster_name"]:
            st.session_state.pop(k, None)
        st.session_state.qc_step = 1

    st.session_state.qc_selected_table_idx = _sel_idx
    _sel_table  = _valid_tables[_sel_idx]
    _dims       = _sel_table["dims"]
    _table_name = _sel_table["name"].strip()
    _db         = _sel_table.get("db", "").strip()
    _schema     = _sel_table.get("schema", "").strip()

    # Progress badge
    if _completed:
        st.caption(f"✅ Done: {', '.join(f'`{n}`' for n in _completed)}  |  "
                   f"⏳ Remaining: {len(_valid_tables) - len(_completed)} of {len(_valid_tables)}")
    st.markdown(" ")

else:
    # Individual / fallback mode — no table selector needed
    _dims, _table_name, _db, _schema = _fallback_dims, _fallback_name, _fallback_db, _fallback_schema

# Auto-build dataset ref
_auto_dataset_ref = f"dataos://icebase:{_schema}/{_table_name}" if _schema and _table_name else ""


# ─────────────────────────────────────────────────────────────────────────────
# NAV
# ─────────────────────────────────────────────────────────────────────────────
def _back():
    for k in QC_KEYS:
        st.session_state.pop(k, None)
    if _origin == "cadp_full":
        st.switch_page("pages/cadp_flow.py")
    else:
        st.switch_page("pages/1_CADP.py")

nav_l, _, nav_r = st.columns([1, 4, 1.5])
with nav_l:
    if st.button("← Back"):
        _back()
with nav_r:
    if st.button("✖ Cancel / Start Over"):
        for k in QC_KEYS:
            st.session_state.pop(k, None)
        st.rerun()

st.divider()

step = st.session_state.qc_step
STEP_LABELS = ["1. Configure & Download", "2. Upload & Preview", "3. Review & Download YAML"]
st.progress((step - 1) / 3, text=f"Step {step} of 3 — {STEP_LABELS[step - 1]}")
st.markdown(" ")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Configure & Download Excel
# ══════════════════════════════════════════════════════════════════════════════
if step == 1:
    st.subheader("Step 1 — Configure & Download Quality Checks Sheet")

    # ── Context info ──────────────────────────────────────────────────────────
    if _table_name and _dims:
        st.success(
            f"✅ **{len(_dims)} dimensions** loaded from Semantic Model "
            f"(table: `{_table_name}`). Pre-filled into the sheet automatically."
        )
    elif _table_name and not _dims:
        st.warning(
            "Table name found but no dimensions — complete the Semantic Model "
            "Table YAML step first to pre-fill columns."
        )
    else:
        st.info(
            "No Semantic Model context found. You can still enter table details "
            "manually below and download a blank sheet."
        )

    st.markdown(" ")

    with st.form("qc_config_form"):
        st.markdown("#### Quality Check Configuration")
        cf1, cf2 = st.columns(2)
        with cf1:
            qc_name = st.text_input(
                "Quality Check Name *",
                value=f"soda-{_table_name.lower()}-quality" if _table_name else "",
                placeholder="e.g. soda-customer-quality",
                help="Used as the workflow name in the generated YAML.",
            )
            table_name_input = st.text_input(
                "Table Name *",
                value=_table_name,
                placeholder="e.g. CUSTOMER",
                help="The table these checks apply to.",
                disabled=bool(_table_name),
            )
        with cf2:
            dataset_ref = st.text_input(
                "Dataset Reference *",
                value=_auto_dataset_ref,
                placeholder="e.g. dataos://icebase:retail/customer",
                help="Format: dataos://<depot>:<collection>/<table>",
            )
            workspace = st.text_input(
                "Workspace",
                value="public",
                placeholder="e.g. public",
                help="DataOS workspace to deploy the workflow in.",
            )

        st.markdown("#### Compute Options")
        co1, co2 = st.columns(2)
        with co1:
            engine = st.text_input(
                "Engine",
                value="minerva",
                placeholder="e.g. minerva",
                help="Query engine to use (minerva, themis, etc.)",
            )
        with co2:
            cluster_name = st.text_input(
                "Cluster Name",
                value="",
                placeholder="e.g. snowflakeclustertest02",
                help="Optional. The specific cluster to run queries on.",
            )

        st.markdown(" ")
        submit = st.form_submit_button("⬇ Generate & Download Excel Sheet", use_container_width=True)

    if submit:
        tbl = (table_name_input or _table_name).strip()
        if not tbl:
            st.error("Table Name is required.")
        elif not qc_name.strip():
            st.error("Quality Check Name is required.")
        elif not dataset_ref.strip():
            st.error("Dataset Reference is required.")
        else:
            # Use dims from session state, or empty if none
            dims_to_use = _dims if _dims else []
            default_rows = build_default_checks(dims_to_use, tbl)

            # Store for later steps
            st.session_state.qc_default_rows = default_rows
            st.session_state.qc_dataset_ref  = dataset_ref.strip()
            st.session_state.qc_name         = qc_name.strip()
            st.session_state.qc_table_name   = tbl
            st.session_state.qc_workspace    = workspace.strip() or "public"
            st.session_state.qc_engine       = engine.strip() or "minerva"
            st.session_state.qc_cluster_name = cluster_name.strip()

            xls_bytes = generate_qc_excel(dims_to_use, tbl)

            st.success("✅ Sheet generated! Download it, fill in the `custom_checks` column, then come back to upload.")
            st.markdown(" ")
            st.download_button(
                label="⬇ Download Quality Checks Sheet (.xlsx)",
                data=xls_bytes,
                file_name=f"{tbl}_quality_checks.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

            # Show preview of what's pre-filled
            st.markdown(" ")
            st.markdown("**Pre-filled default checks:**")
            import pandas as pd
            preview_df = pd.DataFrame(default_rows)[["column_name", "dataos_type", "default_checks"]]
            st.dataframe(preview_df, use_container_width=True, hide_index=True)

            st.markdown(" ")
            col1, _ = st.columns([1, 2])
            with col1:
                if st.button("Next: Upload Filled Sheet →", type="primary", use_container_width=True):
                    st.session_state.qc_step = 2
                    st.rerun()

    # Quick nav if already configured
    elif st.session_state.get("qc_default_rows"):
        st.markdown(" ")
        if st.button("Next: Upload Filled Sheet →", type="primary"):
            st.session_state.qc_step = 2
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Upload & Preview
# ══════════════════════════════════════════════════════════════════════════════
elif step == 2:
    st.subheader("Step 2 — Upload Filled Sheet & Preview Checks")

    st.info(
        "Upload the Excel sheet you downloaded and filled in. "
        "The app will read your `custom_checks` column and combine them with the defaults."
    )

    # ── Syntax reminder ───────────────────────────────────────────────────────
    with st.expander("📖 Custom checks syntax reminder"):
        st.markdown("""
Use the **`custom_checks`** column (yellow) on each column's row. Separate multiple checks with ` | `.

| Keyword | Example | What it does |
|---|---|---|
| `missing_count=N` | `missing_count=0` | Nulls must be ≤ N |
| `missing_percent=N` | `missing_percent=5` | Null % must be ≤ N |
| `duplicate_count=N` | `duplicate_count=0` | Duplicates must be ≤ N |
| `freshness=Nd` | `freshness=1d` | Data not older than N days |
| `valid_values=A,B,C` | `valid_values=CASH,CARD,UPI` | Allowed values (comma-separated) |
| `min=N` | `min=0` | Minimum numeric value |
| `max=N` | `max=999999` | Maximum numeric value |
| `regex=PATTERN` | `regex=^[A-Z]{3}$` | Column must match regex |
| `failed_rows=SQL` | `failed_rows=amount != price * qty` | Custom SQL condition |

**Multiple checks:** `missing_count=0 | valid_values=CASH,CARD,UPI | min=0`
        """)

    st.markdown(" ")
    uploaded = st.file_uploader(
        "Upload your filled Quality Checks sheet",
        type=["xlsx"],
        key="qc_upload",
    )

    if uploaded:
        try:
            result = parse_qc_excel(uploaded.read())
            st.session_state.qc_uploaded_rows  = result["default_rows"]
            st.session_state.qc_custom_checks  = result["custom_checks"]

            default_rows  = result["default_rows"]
            custom_checks = result["custom_checks"]

            st.success(f"✅ Sheet parsed — {len(custom_checks)} custom check(s) found.")
            st.markdown(" ")

            # ── Show all checks preview ───────────────────────────────────────
            st.markdown("#### All Checks Preview")

            tab_default, tab_custom, tab_combined = st.tabs(
                ["Default Checks", "Your Custom Checks", "Combined (all)"]
            )

            import pandas as pd

            with tab_default:
                st.caption("These are auto-generated from your semantic model dimensions.")
                df_def = pd.DataFrame(default_rows)[["column_name", "dataos_type", "default_checks"]]
                st.dataframe(df_def, use_container_width=True, hide_index=True)

            with tab_custom:
                if custom_checks:
                    st.caption("Custom checks parsed from your `custom_checks` column.")
                    df_cust = pd.DataFrame(custom_checks)
                    st.dataframe(df_cust, use_container_width=True, hide_index=True)
                else:
                    st.info("No custom checks found. Add entries in the `custom_checks` column and re-upload.")

            with tab_combined:
                st.caption("This is what will be written to the YAML.")
                combined_rows = []
                for row in default_rows:
                    col = row["column_name"]
                    def_chks = row["default_checks"]
                    cust_chks = row["custom_checks"]
                    combined_rows.append({
                        "column":         col,
                        "type":           row["dataos_type"],
                        "default_checks": def_chks,
                        "custom_checks":  cust_chks if cust_chks else "—",
                    })
                st.dataframe(pd.DataFrame(combined_rows), use_container_width=True, hide_index=True)

            st.markdown(" ")
            if st.button("Next: Generate YAML →", type="primary", use_container_width=True):
                # Generate YAML using stored default rows + parsed custom checks
                table_name = st.session_state.get("qc_table_name", _table_name)
                yaml_out = generate_qc_yaml(
                    default_rows=result["default_rows"],
                    custom_checks=result["custom_checks"],
                    table_name=table_name,
                    dataset_ref=st.session_state.get("qc_dataset_ref", ""),
                    qc_name=st.session_state.get("qc_name", f"{table_name}-qc"),
                    workspace=st.session_state.get("qc_workspace", "public"),
                    engine=st.session_state.get("qc_engine", "minerva"),
                    cluster_name=st.session_state.get("qc_cluster_name", ""),
                )
                st.session_state.qc_generated_yaml = yaml_out
                st.session_state.qc_step = 3
                st.rerun()

        except Exception as e:
            st.error(f"Failed to parse the uploaded file: {e}")

    # Option to skip custom checks and proceed with defaults only
    st.markdown("---")
    st.caption("Don't have custom checks to add? You can proceed with default checks only.")
    if st.button("Skip — use default checks only →"):
        default_rows = st.session_state.get("qc_default_rows", [])
        table_name   = st.session_state.get("qc_table_name", _table_name)
        yaml_out = generate_qc_yaml(
            default_rows=default_rows,
            custom_checks=[],
            table_name=table_name,
            dataset_ref=st.session_state.get("qc_dataset_ref", ""),
            qc_name=st.session_state.get("qc_name", f"{table_name}-qc"),
            workspace=st.session_state.get("qc_workspace", "public"),
            engine=st.session_state.get("qc_engine", "minerva"),
            cluster_name=st.session_state.get("qc_cluster_name", ""),
        )
        st.session_state.qc_generated_yaml = yaml_out
        st.session_state.qc_step = 3
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Review & Download YAML
# ══════════════════════════════════════════════════════════════════════════════
elif step == 3:
    st.subheader("Step 3 — Review & Download Quality Checks YAML")

    yaml_out   = st.session_state.get("qc_generated_yaml", "")
    qc_name    = st.session_state.get("qc_name", "quality-checks")
    table_name = st.session_state.get("qc_table_name", _table_name)

    custom_count  = len(st.session_state.get("qc_custom_checks", []))
    uploaded_rows = st.session_state.get("qc_uploaded_rows", st.session_state.get("qc_default_rows", []))
    default_count = sum(
        1 for row in uploaded_rows
        for token in row.get("default_checks", "").split("|") if token.strip()
    )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Default Checks", default_count)
    with col_b:
        st.metric("Custom Checks", custom_count)
    with col_c:
        st.metric("Total Assertions", default_count + custom_count)

    st.markdown(" ")
    st.code(yaml_out, language="yaml")
    st.markdown(" ")

    dl1, dl2 = st.columns(2)
    with dl1:
        st.download_button(
            label="⬇ Download Quality Checks YAML",
            data=yaml_out,
            file_name=f"{qc_name}.yml",
            mime="text/yaml",
            use_container_width=True,
            type="primary",
        )
    with dl2:
        if st.button("← Edit / Re-upload Sheet", use_container_width=True):
            st.session_state.qc_step = 2
            st.rerun()

    # ── Multi-table tracking + navigation ─────────────────────────────────────
    # Mark current table as done
    if "qc_completed_tables" not in st.session_state:
        st.session_state.qc_completed_tables = set()
    st.session_state.qc_completed_tables.add(table_name)

    _completed = st.session_state.qc_completed_tables
    _pending   = [t for t in _valid_tables if t["name"] not in _completed] if _valid_tables else []

    st.divider()

    if _pending:
        _next = _pending[0]
        _next_idx = _valid_tables.index(_next)
        st.info(
            f"**{len(_pending)} table(s) still need Quality Checks.** "
            f"Next up: `{_next.get('schema','')}.{_next['name']}` ({len(_next['dims'])} cols)"
        )
        nc1, nc2 = st.columns(2)
        with nc1:
            if st.button(f"→ Generate QC for: {_next['name']}", use_container_width=True, type="primary"):
                for k in ["qc_step","qc_default_rows","qc_custom_checks","qc_generated_yaml",
                          "qc_dataset_ref","qc_name","qc_uploaded_rows","qc_table_name",
                          "qc_workspace","qc_engine","qc_cluster_name"]:
                    st.session_state.pop(k, None)
                st.session_state.qc_step = 1
                st.session_state.qc_selected_table_idx = _next_idx
                st.rerun()
        with nc2:
            if _origin == "cadp_full" and st.button("Back to CADP Flow →", use_container_width=True):
                if "cadp_completed_steps" not in st.session_state:
                    st.session_state.cadp_completed_steps = set()
                st.session_state.cadp_completed_steps.add(2)
                st.switch_page("pages/cadp_flow.py")
    else:
        total = len(_valid_tables) if _valid_tables else 1
        st.success(f"🎉 Quality Checks generated for all {total} table(s)!")
        if _origin == "cadp_full":
            if st.button("Back to CADP Flow →", use_container_width=True, type="primary"):
                if "cadp_completed_steps" not in st.session_state:
                    st.session_state.cadp_completed_steps = set()
                st.session_state.cadp_completed_steps.add(2)
                st.switch_page("pages/cadp_flow.py")