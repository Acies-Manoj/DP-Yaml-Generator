import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.examples import (
    EXAMPLE_SECRET_R, EXAMPLE_SECRET_RW, EXAMPLE_DEPOT, EXAMPLE_SCANNER,
    show_example,
)
from utils.depot_generators import (
    generate_secret_r_yaml,
    generate_secret_rw_yaml,
    generate_depot_yaml,
    generate_scanner_yaml,
)

st.set_page_config(page_title="Depot Builder", layout="wide")

st.markdown("""
<style>
.stButton>button {
    width: 100%;
    height: 45px;
    border-radius: 8px;
    font-size: 15px;
}
.info-pill {
    display: inline-block;
    background-color: #1f2937;
    color: #9ca3af;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 13px;
    margin: 2px 4px 2px 0;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# BACK NAVIGATION — context-aware (SADP vs CADP)
# ─────────────────────────────────────────────────────────────────────────────
origin = st.session_state.get("depot_origin", "cadp")

# ─────────────────────────────────────────────────────────────────────────────
# STATE INITIALISATION
# ─────────────────────────────────────────────────────────────────────────────
DEPOT_KEYS_TO_CLEAR = [
    "depot_step", "depot_source",
    "depot_base_name", "depot_username", "depot_password",
    "depot_layer_secret", "depot_desc_r", "depot_desc_rw",
    "depot_description", "depot_tags", "depot_warehouse",
    "depot_url", "depot_database", "depot_account",
    "depot_layer_depot", "depot_external",
    "depot_workflow_name", "depot_wf_description", "depot_dag_description",
    "depot_scanner_tags", "depot_schemas",
    "depot_stack", "depot_compute", "depot_run_as_user",
    "depot_include_tables", "depot_include_views",
    "depot_yaml_r", "depot_yaml_rw", "depot_yaml_depot", "depot_yaml_scanner",
]

# Keys to preserve when returning to full DP flow
DEPOT_CRED_KEYS = {"depot_username", "depot_password", "depot_account", "depot_warehouse", "depot_url", "depot_database"}
DEPOT_YAML_KEYS = {"depot_yaml_r", "depot_yaml_rw", "depot_yaml_depot", "depot_yaml_scanner", "depot_base_name"}

def clear_depot_state(keep_creds=False):
    keep = set()
    if keep_creds:
        keep |= DEPOT_CRED_KEYS | DEPOT_YAML_KEYS
    for k in DEPOT_KEYS_TO_CLEAR:
        if k in keep:
            continue
        st.session_state.pop(k, None)

for k, v in [
    ("depot_step",           0),
    ("depot_source",         None),
    ("depot_tags",           ["snowflake depot", "user data"]),
    ("depot_scanner_tags",   ["snowflake-scanner"]),
    ("depot_schemas",        [""]),
]:
    if k not in st.session_state:
        st.session_state[k] = v

step = st.session_state.depot_step
source = st.session_state.get("depot_source")
specific_file = st.session_state.get("depot_specific_file")  # set by specific file picker

STEP_LABELS = [
    "1. Credentials & Naming",
    "2. Depot Configuration",
    "3. Scanner Configuration",
    "4. Review & Download",
]

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
source_label = f" — {source}" if source else ""
st.title(f"Depot Builder{source_label}")

# Progress bar — only show after source is selected
if step > 0:
    label = STEP_LABELS[step - 1] if step <= 4 else "Complete"
    st.progress((step - 1) / 4, text=f"Step {step} of 4 — {label}")

def _back_to_origin():
    keep = origin in ("cadp_full", "sadp_full")
    clear_depot_state(keep_creds=keep)
    if origin == "sadp_full":
        st.switch_page("pages/sadp_flow.py")
    elif origin == "cadp_full":
        st.switch_page("pages/cadp_flow.py")
    elif origin == "sadp":
        st.switch_page("app.py")
    elif origin == "specific":
        st.switch_page("app.py")
    else:
        st.switch_page("pages/1_CADP.py")

# Nav row
nav_l, _, nav_r = st.columns([1, 4, 1.5])
with nav_l:
    if step == 0:
        if st.button("← Back"):
            _back_to_origin()
    elif step == 1:
        if st.button("← Back"):
            st.session_state.depot_step = 0
            st.rerun()
    elif step > 1:
        if st.button("← Back"):
            st.session_state.depot_step -= 1
            st.rerun()
with nav_r:
    if st.button("✖ Cancel / Start Over"):
        _back_to_origin()

st.divider()



# ══════════════════════════════════════════════════════════════════════════════
# INDIVIDUAL MODE — render a single file directly (from specific file picker)
# ══════════════════════════════════════════════════════════════════════════════
if origin == "specific" and specific_file:

    FILE_LABELS = {
        "secret_r":  "Instance Secret (Read)",
        "secret_rw": "Instance Secret (Read-Write)",
        "depot":     "Depot",
        "scanner":   "Depot Scanner",
    }
    st.subheader(FILE_LABELS.get(specific_file, specific_file))

    # ── Individual: Secret R ──────────────────────────────────────────────────
    if specific_file == "secret_r":
        show_example(st, "Instance Secret R", EXAMPLE_SECRET_R)
        with st.form("ind_secret_r_form"):
            st.markdown("#### Naming")
            c1, c2 = st.columns(2)
            with c1:
                base_name = st.text_input("Secret Name *", placeholder="e.g. depot-name-r",
                    help="Convention: {depot-name}-r")
                layer = st.text_input("Layer", value="user")
            with c2:
                desc = st.text_input("Description",
                    placeholder="e.g. read instance-secret for depot snowflake depot")
            st.divider()
            st.markdown("#### Credentials")
            cr1, cr2 = st.columns(2)
            with cr1:
                username = st.text_input("Username *", placeholder="e.g. snowflake_user")
            with cr2:
                password = st.text_input("Password *", type="password")
            st.markdown(" ")
            sub = st.form_submit_button("Generate YAML", use_container_width=True)
        if sub:
            if not base_name.strip():
                st.error("Secret Name is required.")
            elif not username.strip() or not password.strip():
                st.error("Username and Password are required.")
            else:
                yaml_out = generate_secret_r_yaml({
                    "name": base_name.strip(), "layer": layer.strip() or "user",
                    "username": username.strip(), "password": password,
                    "desc_r": desc.strip() or f"read instance-secret for {base_name.strip()} snowflake depot",
                    "desc_rw": "",
                })
                st.code(yaml_out, language="yaml")
                st.download_button("Download YAML", data=yaml_out,
                    file_name=f"{base_name.strip()}.yml", mime="text/yaml",
                    use_container_width=True)

    # ── Individual: Secret RW ─────────────────────────────────────────────────
    elif specific_file == "secret_rw":
        show_example(st, "Instance Secret RW", EXAMPLE_SECRET_RW)
        with st.form("ind_secret_rw_form"):
            st.markdown("#### Naming")
            c1, c2 = st.columns(2)
            with c1:
                base_name = st.text_input("Secret Name *", placeholder="e.g. depot-name-rw",
                    help="Convention: {depot-name}-rw")
                layer = st.text_input("Layer", value="user")
            with c2:
                desc = st.text_input("Description",
                    placeholder="e.g. read-write instance-secret for depot snowflake depot")
            st.divider()
            st.markdown("#### Credentials")
            cr1, cr2 = st.columns(2)
            with cr1:
                username = st.text_input("Username *", placeholder="e.g. snowflake_user")
            with cr2:
                password = st.text_input("Password *", type="password")
            st.markdown(" ")
            sub = st.form_submit_button("Generate YAML", use_container_width=True)
        if sub:
            if not base_name.strip():
                st.error("Secret Name is required.")
            elif not username.strip() or not password.strip():
                st.error("Username and Password are required.")
            else:
                yaml_out = generate_secret_rw_yaml({
                    "name": base_name.strip(), "layer": layer.strip() or "user",
                    "username": username.strip(), "password": password,
                    "desc_r": "", 
                    "desc_rw": desc.strip() or f"read-write instance-secret for {base_name.strip()} snowflake depot",
                })
                st.code(yaml_out, language="yaml")
                st.download_button("Download YAML", data=yaml_out,
                    file_name=f"{base_name.strip()}.yml", mime="text/yaml",
                    use_container_width=True)

    # ── Individual: Depot ─────────────────────────────────────────────────────
    elif specific_file == "depot":
        show_example(st, "Depot YAML", EXAMPLE_DEPOT)

        # tags managed outside form
        if "depot_tags" not in st.session_state:
            st.session_state.depot_tags = ["snowflake depot", "user data"]

        with st.form("ind_depot_form"):
            st.markdown("#### Metadata")
            m1, m2 = st.columns(2)
            with m1:
                dep_name = st.text_input("Depot Name *", placeholder="e.g. sampleobs")
                layer = st.text_input("Layer", value="user")
            with m2:
                description = st.text_input("Description *",
                    value="Depot to fetch data from Snowflake datasource")
                external = st.checkbox("External", value=True)

            st.markdown("#### Tags")
            _th1, _th2 = st.columns([5, 1])
            with _th1: st.markdown("**Tags**")
            with _th2:
                if st.form_submit_button("➕ Add", key="ind_depot_add_tag"):
                    st.session_state.depot_tags.append(""); st.rerun()
            updated_tags = []
            for i, tag in enumerate(st.session_state.depot_tags):
                tc1, tc2 = st.columns([5, 1])
                with tc1:
                    val = st.text_input(f"Tag {i+1}", value=tag, key=f"ind_dtag_{i}",
                        placeholder="e.g. snowflake depot", label_visibility="collapsed")
                    updated_tags.append(val)
                with tc2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("❌", key=f"ind_rm_dtag_{i}"):
                        st.session_state.depot_tags.pop(i); st.rerun()

            st.divider()
            st.markdown("#### Secrets")
            st.caption("The depot references two instance secrets — enter the base name and -r / -rw suffixes are added automatically.")
            secret_base = st.text_input("Secret Base Name *", placeholder="e.g. sampleobs",
                help="Generates references to {name}-r and {name}-rw")

            st.divider()
            st.markdown("#### Snowflake Connection")
            sf1, sf2 = st.columns(2)
            with sf1:
                warehouse = st.text_input("Warehouse *", placeholder="e.g. COMPUTE_WH")
                url = st.text_input("URL *", placeholder="e.g. myorg.snowflakecomputing.com")
            with sf2:
                database = st.text_input("Database *", placeholder="e.g. PROD_DB")
                account = st.text_input("Account *", placeholder="e.g. myorg-myaccount")
            st.markdown(" ")
            sub = st.form_submit_button("Generate YAML", use_container_width=True)

        st.session_state.depot_tags = updated_tags

        if sub:
            errors = []
            if not dep_name.strip(): errors.append("Depot Name is required.")
            if not description.strip(): errors.append("Description is required.")
            if not secret_base.strip(): errors.append("Secret Base Name is required.")
            if not warehouse.strip(): errors.append("Warehouse is required.")
            if not url.strip(): errors.append("URL is required.")
            if not database.strip(): errors.append("Database is required.")
            if not account.strip(): errors.append("Account is required.")
            if errors:
                for e in errors: st.error(e)
            else:
                yaml_out = generate_depot_yaml({
                    "name": dep_name.strip(),
                    "description": description.strip(),
                    "tags": [t for t in updated_tags if t.strip()],
                    "layer": layer.strip() or "user",
                    "external": external,
                    "warehouse": warehouse.strip(),
                    "url": url.strip(),
                    "database": database.strip(),
                    "account": account.strip(),
                    "secret_base": secret_base.strip(),
                })
                st.code(yaml_out, language="yaml")
                st.download_button("Download YAML", data=yaml_out,
                    file_name=f"{dep_name.strip()}-depot.yml", mime="text/yaml",
                    use_container_width=True)

    # ── Individual: Scanner ───────────────────────────────────────────────────
    elif specific_file == "scanner":
        show_example(st, "Scanner YAML", EXAMPLE_SCANNER)

        if "depot_scanner_tags" not in st.session_state:
            st.session_state.depot_scanner_tags = ["snowflake-scanner"]
        if "depot_schemas" not in st.session_state:
            st.session_state.depot_schemas = [""]

        with st.form("ind_scanner_form"):
            st.markdown("#### Workflow Identity")
            w1, w2 = st.columns(2)
            with w1:
                workflow_name = st.text_input("Workflow Name *",
                    placeholder="e.g. scan-sampleobs",
                    help="Convention: scan-{depot-name}")
                depot_ref = st.text_input("Depot Name *",
                    placeholder="e.g. sampleobs",
                    help="The depot this scanner will crawl.")
            with w2:
                wf_desc = st.text_input("Workflow Description",
                    value="Workflow to scan Snowflake database tables and register metadata in Metis.")
                dag_desc = st.text_input("DAG Description",
                    value="Scans schemas from Snowflake database and registers metadata to Metis.")

            st.markdown("#### Scanner Tags")
            _scth1, _scth2 = st.columns([5, 1])
            with _scth1: st.markdown("**Tags**")
            with _scth2:
                if st.form_submit_button("➕ Add", key="ind_add_stag"):
                    st.session_state.depot_scanner_tags.append(""); st.rerun()
            updated_scanner_tags = []
            for i, tag in enumerate(st.session_state.depot_scanner_tags):
                stc1, stc2 = st.columns([5, 1])
                with stc1:
                    val = st.text_input(f"Tag {i+1}", value=tag, key=f"ind_stag_{i}",
                        label_visibility="collapsed")
                    updated_scanner_tags.append(val)
                with stc2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("❌", key=f"ind_rm_stag_{i}"):
                        st.session_state.depot_scanner_tags.pop(i); st.rerun()

            st.divider()
            st.markdown("#### Schema Filter")
            st.caption("Enter schema names to include — `^...$` anchors are added automatically.")
            _sch1, _sch2 = st.columns([5, 1])
            with _sch1: st.markdown("**Schemas**")
            with _sch2:
                if st.form_submit_button("➕ Add", key="ind_add_schema"):
                    st.session_state.depot_schemas.append(""); st.rerun()
            updated_schemas = []
            for i, schema in enumerate(st.session_state.depot_schemas):
                sc1, sc2 = st.columns([5, 1])
                with sc1:
                    val = st.text_input(f"Schema {i+1}", value=schema, key=f"ind_schema_{i}",
                        placeholder="e.g. SAMPLE_MANOJ", label_visibility="collapsed")
                    updated_schemas.append(val)
                with sc2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.form_submit_button("❌", key=f"ind_rm_schema_{i}"):
                        st.session_state.depot_schemas.pop(i); st.rerun()

            filled = [s.strip() for s in updated_schemas if s.strip()]
            if filled:
                st.caption("Will render as: " + "  |  ".join(f"`^{s}$`" for s in filled))

            st.divider()
            st.markdown("#### Runtime Settings")
            rt1, rt2, rt3 = st.columns(3)
            with rt1: stack = st.text_input("Stack", value="scanner:2.0")
            with rt2: compute = st.text_input("Compute", value="runnable-default")
            with rt3: run_as_user = st.text_input("Run As User", value="metis")
            inc1, inc2 = st.columns(2)
            with inc1: include_tables = st.checkbox("Include Tables", value=True)
            with inc2: include_views = st.checkbox("Include Views", value=True)

            st.markdown(" ")
            sub = st.form_submit_button("Generate YAML", use_container_width=True)

        st.session_state.depot_scanner_tags = updated_scanner_tags
        st.session_state.depot_schemas = updated_schemas

        if sub:
            if not workflow_name.strip():
                st.error("Workflow Name is required.")
            elif not depot_ref.strip():
                st.error("Depot Name is required.")
            else:
                yaml_out = generate_scanner_yaml({
                    "workflow_name": workflow_name.strip(),
                    "description": wf_desc.strip(),
                    "dag_description": dag_desc.strip(),
                    "tags": [t for t in updated_scanner_tags if t.strip()],
                    "depot_name": depot_ref.strip(),
                    "schemas": [s for s in updated_schemas if s.strip()],
                    "stack": stack.strip() or "scanner:2.0",
                    "compute": compute.strip() or "runnable-default",
                    "run_as_user": run_as_user.strip() or "metis",
                    "include_tables": include_tables,
                    "include_views": include_views,
                })
                st.code(yaml_out, language="yaml")
                st.download_button("Download YAML", data=yaml_out,
                    file_name=f"{workflow_name.strip()}.yml", mime="text/yaml",
                    use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 0 — SOURCE SELECTION  (multi-step flow)
# ══════════════════════════════════════════════════════════════════════════════
elif step == 0:

    st.subheader("Select a Source System")
    st.caption("Choose the source you want to connect to DataOS. Each source has its own depot template.")
    st.markdown(" ")

    SOURCES = [
        {"key": "Snowflake",   "desc": "Cloud data warehouse by Snowflake Inc.",          "available": True},
        {"key": "PostgreSQL",  "desc": "Open-source relational database.",                "available": False}
    ]

    # 4 cards per row
    for row_start in range(0, len(SOURCES), 4):
        cols = st.columns(4)
        for col, src in zip(cols, SOURCES[row_start:row_start + 4]):
            with col:
                st.markdown(f"""
                    <div style="padding:20px;border-radius:12px;background-color:#111827;
                                color:white;height:140px;margin-bottom:8px;">
                        <h4 style="margin:0 0 6px 0">{src['key']}</h4>
                        <p style="font-size:13px;color:#9ca3af;margin:0">{src['desc']}</p>
                    </div>
                """, unsafe_allow_html=True)
                if src["available"]:
                    if st.button(f"Select {src['key']}", use_container_width=True, key=f"src_{src['key']}"):
                        st.session_state.depot_source = src["key"]
                        st.session_state.depot_step   = 1
                        st.rerun()
                else:
                    st.button("Coming Soon", use_container_width=True,
                              key=f"src_{src['key']}", disabled=True)
        st.markdown(" ")
elif step == 1:
    st.subheader("Step 1 — Credentials & Naming")
    c_ex1, c_ex2 = st.columns([1, 1])
    with c_ex1:
        show_example(st, "Instance Secret R", EXAMPLE_SECRET_R)
    with c_ex2:
        show_example(st, "Instance Secret RW", EXAMPLE_SECRET_RW)
    st.caption(
        "The name you enter will be depot name and instance secret names will be generated with -r & -rw as suffixes"
        "Secrets will be named `{name}-r` and `{name}-rw`."
    )
    st.markdown(" ")


    with st.form("depot_step1_form"):
        st.markdown("#### Secret Names")
        c1, c2 = st.columns(2)
        with c1:
            base_name = st.text_input(
                "Instance Secret Name *",
                value=st.session_state.get("depot_base_name", ""),
                placeholder="e.g. depot-name",
                help="This is the depot name. The names for two secrets will be generated with this name - r & rw.",
            )
        with c2:
            layer = st.text_input(
                "Layer",
                value=st.session_state.get("depot_layer_secret", "user"),
            )

        st.divider()
        st.markdown("#### Snowflake Credentials")
        st.caption("Stored in both instance secrets (R and RW) with the same values.")

        cr1, cr2 = st.columns(2)
        with cr1:
            username = st.text_input(
                "Username *",
                value=st.session_state.get("depot_username", ""),
                placeholder="e.g. snowflake_user",
            )
        with cr2:
            password = st.text_input(
                "Password *",
                value=st.session_state.get("depot_password", ""),
                type="password",
                placeholder="Snowflake password",
            )

        st.divider()
        st.markdown("#### Secret Descriptions")
        st.caption("Auto-generated — edit if needed.")

        auto_r  = f"read instance-secret for {base_name} snowflake depot"
        auto_rw = f"read-write instance-secret for {base_name} snowflake depot"

        desc_r = st.text_input(
            "Instance Secret R description",
            value=st.session_state.get("depot_desc_r", auto_r),
        )
        desc_rw = st.text_input(
            "Instance Secret RW description",
            value=st.session_state.get("depot_desc_rw", auto_rw),
        )

        st.markdown(" ")
        submit1 = st.form_submit_button("Next →", use_container_width=True)

    if submit1:
        if not base_name.strip():
            st.error("Base Name is required.")
        elif not username.strip():
            st.error("Username is required.")
        elif not password.strip():
            st.error("Password is required.")
        else:
            st.session_state.depot_base_name    = base_name.strip()
            st.session_state.depot_layer_secret = layer.strip() or "user"
            st.session_state.depot_username     = username.strip()
            st.session_state.depot_password     = password
            st.session_state.depot_desc_r       = desc_r.strip() or auto_r
            st.session_state.depot_desc_rw      = desc_rw.strip() or auto_rw

            payload = {
                "name":     base_name.strip(),
                "layer":    layer.strip() or "user",
                "username": username.strip(),
                "password": password,
                "desc_r":   desc_r.strip() or auto_r,
                "desc_rw":  desc_rw.strip() or auto_rw,
            }
            st.session_state.depot_yaml_r  = generate_secret_r_yaml(payload)
            st.session_state.depot_yaml_rw = generate_secret_rw_yaml(payload)
            st.session_state.depot_step    = 2
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — DEPOT CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
elif step == 2:
    name = st.session_state.depot_base_name

    st.subheader("Step 2 — Depot Configuration")
    show_example(st, "Depot YAML", EXAMPLE_DEPOT)
    st.caption("Configure the Snowflake connection. Secret references are auto-filled from Step 1.")
    st.markdown(" ")

    # Show locked secret references
    st.markdown("**Secret references (auto-filled from Step 1)**")
    st.markdown(
        f'<span class="info-pill">Secret R → <strong>{name}-r</strong></span>'
        f'<span class="info-pill">Secret RW → <strong>{name}-rw</strong></span>',
        unsafe_allow_html=True,
    )
    st.markdown(" ")

    # Add / remove tags outside form
    tag_col1, tag_col2 = st.columns([6, 1])
    with tag_col1:
        st.markdown("**Tags** — click ➕ to add")
    with tag_col2:
        if st.button("➕ Tag", key="depot_add_tag"):
            st.session_state.depot_tags.append("")
            st.rerun()


    with st.expander("See example output — Depot YAML"):
        st.code("""name: sampleobs
version: v2alpha
type: depot
description: Depot to fetch data from Snowflake datasource
layer: user
depot:
  name: sampleobs
  type: snowflake
  external: true
  secrets:
    - name: sampleobs-r
      allkeys: true
    - name: sampleobs-rw
      allkeys: true
  snowflake:
    warehouse: COMPUTE_WH
    url: myorg.snowflakecomputing.com
    database: PROD_DB
    account: myorg-myaccount""", language="yaml")

    with st.form("depot_step2_form"):
        st.markdown("#### 🏷️ Metadata")
        m1, m2 = st.columns(2)
        with m1:
            description = st.text_input(
                "Description *",
                value=st.session_state.get("depot_description", "Depot to fetch data from Snowflake datasource"),
                placeholder="e.g. Depot to fetch data from Snowflake datasource",
            )
            layer_depot = st.text_input(
                "Layer",
                value=st.session_state.get("depot_layer_depot", "user"),
            )
        with m2:
            external = st.checkbox(
                "External",
                value=st.session_state.get("depot_external", True),
                help="Set to true for external data sources (standard for Snowflake).",
            )

        st.divider()
        st.markdown("**Tags**")
        updated_tags = []
        for i, tag in enumerate(st.session_state.depot_tags):
            tc1, tc2 = st.columns([5, 1])
            with tc1:
                val = st.text_input(
                    f"Tag {i+1}", value=tag, key=f"depot_tag_{i}",
                    placeholder="e.g. snowflake depot", label_visibility="collapsed",
                )
                updated_tags.append(val)
            with tc2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("❌", key=f"depot_rm_tag_{i}"):
                    st.session_state.depot_tags.pop(i)
                    st.rerun()

        st.divider()
        st.markdown("#### ❄️ Snowflake Connection")
        sf1, sf2 = st.columns(2)
        with sf1:
            warehouse = st.text_input(
                "Warehouse *",
                value=st.session_state.get("depot_warehouse", ""),
                placeholder="e.g. COMPUTE_WH",
            )
            url = st.text_input(
                "URL *",
                value=st.session_state.get("depot_url", ""),
                placeholder="e.g. myorg.snowflakecomputing.com",
            )
        with sf2:
            database = st.text_input(
                "Database *",
                value=st.session_state.get("depot_database", ""),
                placeholder="e.g. PROD_DB",
            )
            account = st.text_input(
                "Account *",
                value=st.session_state.get("depot_account", ""),
                placeholder="e.g. myorg-myaccount",
            )

        st.markdown(" ")
        submit2 = st.form_submit_button("Next →", use_container_width=True)

    st.session_state.depot_tags = updated_tags

    if submit2:
        errors = []
        if not description.strip(): errors.append("Description is required.")
        if not warehouse.strip():   errors.append("Warehouse is required.")
        if not url.strip():         errors.append("URL is required.")
        if not database.strip():    errors.append("Database is required.")
        if not account.strip():     errors.append("Account is required.")
        if errors:
            for e in errors: st.error(e)
        else:
            st.session_state.depot_description  = description.strip()
            st.session_state.depot_layer_depot  = layer_depot.strip() or "user"
            st.session_state.depot_external     = external
            st.session_state.depot_warehouse    = warehouse.strip()
            st.session_state.depot_url          = url.strip()
            st.session_state.depot_database     = database.strip()
            st.session_state.depot_account      = account.strip()

            st.session_state.depot_yaml_depot = generate_depot_yaml({
                "name":        name,
                "description": description.strip(),
                "tags":        [t for t in updated_tags if t.strip()],
                "layer":       layer_depot.strip() or "user",
                "external":    external,
                "warehouse":   warehouse.strip(),
                "url":         url.strip(),
                "database":    database.strip(),
                "account":     account.strip(),
            })
            st.session_state.depot_step = 3
            st.rerun()



# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — SCANNER CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
elif step == 3:
    name = st.session_state.depot_base_name

    st.subheader("🔍 Step 3 — Scanner Configuration")
    show_example(st, "Scanner YAML", EXAMPLE_SCANNER)
    st.caption("Configure the metadata scanner workflow for this Snowflake depot.")
    st.markdown(" ")

    # Show locked depot reference
    st.markdown("**Depot reference (auto-filled)**")
    st.markdown(
        f'<span class="info-pill">dataos://<strong>{name}</strong></span>',
        unsafe_allow_html=True,
    )
    st.markdown(" ")

    # Add / remove buttons outside form
    btn1, btn2, btn3 = st.columns(3)
    with btn1:
        if st.button("➕ Scanner Tag", key="depot_add_stag"):
            st.session_state.depot_scanner_tags.append("")
            st.rerun()
    with btn2:
        if st.button("➕ Schema", key="depot_add_schema"):
            st.session_state.depot_schemas.append("")
            st.rerun()


    with st.expander("See example output — Scanner YAML"):
        st.code("""version: v1
name: scan-sampleobs
type: workflow
description: Workflow to scan Snowflake database tables and register metadata in Metis.
workflow:
  dag:
    - name: scan-sampleobs
      description: Scans schemas from Snowflake database and registers metadata to Metis.
      spec:
        stack: scanner:2.0
        tags:
          - scanner
        compute: runnable-default
        runAsUser: metis
        stackSpec:
          depot: dataos://sampleobs
          sourceConfig:
            config:
              includeTables: true
              includeViews: true
              schemaFilterPattern:
                includes:
                  - ^retail$""", language="yaml")

    with st.form("depot_step3_form"):
        st.markdown("#### Workflow Identity")
        w1, w2 = st.columns(2)
        default_wf_name = f"{name}-snowflake-scanner"
        with w1:
            workflow_name = st.text_input(
                "Workflow Name *",
                value=st.session_state.get("depot_workflow_name", default_wf_name),
            )
        with w2:
            wf_description = st.text_input(
                "Workflow Description",
                value=st.session_state.get("depot_wf_description", "Workflow to scan Snowflake database tables and register metadata in Metis."),
                placeholder=f"Workflow to scan Snowflake database tables and register metadata in Metis.",
            )

        dag_description = st.text_input(
            "DAG Step Description",
            value=st.session_state.get("depot_dag_description", "Scans schemas from Snowflake database and registers metadata to Metis."),
            placeholder=f"Scans schemas from Snowflake database and registers metadata to Metis.",
        )

        st.markdown("**Scanner Tags**")
        updated_scanner_tags = []
        for i, tag in enumerate(st.session_state.depot_scanner_tags):
            stc1, stc2 = st.columns([5, 1])
            with stc1:
                val = st.text_input(
                    f"STag {i+1}", value=tag, key=f"depot_stag_{i}",
                    placeholder="e.g. snowflake-scanner", label_visibility="collapsed",
                )
                updated_scanner_tags.append(val)
            with stc2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("❌", key=f"depot_rm_stag_{i}"):
                    st.session_state.depot_scanner_tags.pop(i)
                    st.rerun()

        st.divider()
        st.markdown("#### Schema Filter")
        st.caption("Enter schema names to include — `^...$` anchors are added automatically.")

        updated_schemas = []
        for i, schema in enumerate(st.session_state.depot_schemas):
            sc1, sc2 = st.columns([5, 1])
            with sc1:
                val = st.text_input(
                    f"Schema {i+1}", value=schema, key=f"depot_schema_{i}",
                    placeholder="e.g. SAMPLE_MANOJ", label_visibility="collapsed",
                )
                updated_schemas.append(val)
            with sc2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("❌", key=f"depot_rm_schema_{i}"):
                    st.session_state.depot_schemas.pop(i)
                    st.rerun()

        # Show preview of what the regex will look like
        filled = [s.strip() for s in updated_schemas if s.strip()]
        if filled:
            st.caption("Will render as: " + "  |  ".join(f"`^{s}$`" for s in filled))

        st.divider()
        st.markdown("#### Runtime Settings")
        st.caption("These are standard defaults — edit only if needed.")

        rt1, rt2, rt3 = st.columns(3)
        with rt1:
            stack = st.text_input(
                "Stack",
                value=st.session_state.get("depot_stack", "scanner:2.0"),
            )
        with rt2:
            compute = st.text_input(
                "Compute",
                value=st.session_state.get("depot_compute", "runnable-default"),
            )
        with rt3:
            run_as_user = st.text_input(
                "Run As User",
                value=st.session_state.get("depot_run_as_user", "metis"),
            )

        inc1, inc2 = st.columns(2)
        with inc1:
            include_tables = st.checkbox(
                "Include Tables",
                value=st.session_state.get("depot_include_tables", True),
            )
        with inc2:
            include_views = st.checkbox(
                "Include Views",
                value=st.session_state.get("depot_include_views", True),
            )

        st.markdown(" ")
        submit3 = st.form_submit_button("Next →", use_container_width=True)

    st.session_state.depot_scanner_tags = updated_scanner_tags
    st.session_state.depot_schemas      = updated_schemas

    if submit3:
        if not workflow_name.strip():
            st.error("Workflow Name is required.")
        else:
            st.session_state.depot_workflow_name   = workflow_name.strip()
            st.session_state.depot_wf_description  = wf_description.strip()
            st.session_state.depot_dag_description = dag_description.strip()
            st.session_state.depot_stack           = stack.strip() or "scanner:2.0"
            st.session_state.depot_compute         = compute.strip() or "runnable-default"
            st.session_state.depot_run_as_user     = run_as_user.strip() or "metis"
            st.session_state.depot_include_tables  = include_tables
            st.session_state.depot_include_views   = include_views

            st.session_state.depot_yaml_scanner = generate_scanner_yaml({
                "workflow_name":   workflow_name.strip(),
                "description":     wf_description.strip() or f"Workflow to scan Snowflake database tables and register metadata in Metis.",
                "dag_description": dag_description.strip() or f"Scans schemas from Snowflake database and registers metadata to Metis.",
                "tags":            [t for t in updated_scanner_tags if t.strip()],
                "depot_name":      name,
                "schemas":         [s for s in updated_schemas if s.strip()],
                "stack":           stack.strip() or "scanner:2.0",
                "compute":         compute.strip() or "runnable-default",
                "run_as_user":     run_as_user.strip() or "metis",
                "include_tables":  include_tables,
                "include_views":   include_views,
            })
            st.session_state.depot_step = 4
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — REVIEW & DOWNLOAD ALL
# ══════════════════════════════════════════════════════════════════════════════
elif step == 4:
    name = st.session_state.depot_base_name

    st.subheader("Step 4 — Review All Files & Download")
    st.success(f"All 4 files generated for depot **{name}**. Review and download below.")
    st.markdown(" ")

    yaml_r       = st.session_state.get("depot_yaml_r", "")
    yaml_rw      = st.session_state.get("depot_yaml_rw", "")
    yaml_depot   = st.session_state.get("depot_yaml_depot", "")
    yaml_scanner = st.session_state.get("depot_yaml_scanner", "")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Secret R",
        "Secret RW",
        "Depot",
        "Scanner",
    ])

    with tab1:
        st.markdown(f"**`{name}-r.yml`**")
        st.code(yaml_r, language="yaml")
        st.download_button(
            "⬇ Download Secret R",
            data=yaml_r,
            file_name=f"{name}-r.yml",
            mime="text/yaml",
            use_container_width=True,
        )

    with tab2:
        st.markdown(f"**`{name}-rw.yml`**")
        st.code(yaml_rw, language="yaml")
        st.download_button(
            "⬇ Download Secret RW",
            data=yaml_rw,
            file_name=f"{name}-rw.yml",
            mime="text/yaml",
            use_container_width=True,
        )

    with tab3:
        st.markdown(f"**`{name}-depot.yml`**")
        st.code(yaml_depot, language="yaml")
        st.download_button(
            "⬇ Download Depot",
            data=yaml_depot,
            file_name=f"{name}-depot.yml",
            mime="text/yaml",
            use_container_width=True,
        )

    with tab4:
        st.markdown(f"**`{name}-scanner.yml`**")
        st.code(yaml_scanner, language="yaml")
        st.download_button(
            "⬇ Download Scanner",
            data=yaml_scanner,
            file_name=f"{name}-scanner.yml",
            mime="text/yaml",
            use_container_width=True,
        )

    st.divider()

    # ── ZIP download ──────────────────────────────────────────────────────────
    import zipfile, io
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as zf:
        zf.writestr(f"{name}-depot/{name}-r.yml",       yaml_r)
        zf.writestr(f"{name}-depot/{name}-rw.yml",      yaml_rw)
        zf.writestr(f"{name}-depot/{name}-depot.yml",   yaml_depot)
        zf.writestr(f"{name}-depot/{name}-scanner.yml", yaml_scanner)
    zip_buf.seek(0)

    st.download_button(
        f"Download All as ZIP  ({name}-depot.zip)",
        data=zip_buf,
        file_name=f"{name}-depot.zip",
        mime="application/zip",
        use_container_width=True,
    )

    st.markdown(" ")

    if origin == "cadp_full":
        # Mark depot complete in CADP flow, pass name forward
        st.session_state["cadp_depot_name"] = name
        if "cadp_completed_steps" not in st.session_state:
            st.session_state.cadp_completed_steps = set()
        st.session_state.cadp_completed_steps.add(1)

        st.divider()
        st.success("Depot files ready. Return to the CADP flow to continue.")
        if st.button("Back to CADP Flow →", use_container_width=True, type="primary"):
            clear_depot_state(keep_creds=True)
            st.switch_page("pages/cadp_flow.py")

    elif origin == "sadp_full":
        # Mark depot complete in SADP flow, pass name forward
        st.session_state["sadp_depot_name"] = name
        if "sadp_completed_steps" not in st.session_state:
            st.session_state.sadp_completed_steps = set()
        st.session_state.sadp_completed_steps.add(1)

        st.divider()
        st.success("Depot files ready. Return to the SADP flow to continue.")
        if st.button("Back to SADP Flow →", use_container_width=True, type="primary"):
            clear_depot_state(keep_creds=True)
            st.switch_page("pages/sadp_flow.py")

    elif origin == "specific":
        if st.button("← Back to File List"):
            clear_depot_state()
            st.session_state.home_screen = "specific"
            st.switch_page("app.py")

    else:
        if st.button("← Back to Home"):
            clear_depot_state()
            st.switch_page("app.py")