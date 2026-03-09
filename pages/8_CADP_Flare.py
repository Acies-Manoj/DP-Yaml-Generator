import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.examples import EXAMPLE_FLARE, show_example
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.generators import generate_flare_yaml

st.set_page_config(page_title="CADP — Flare Jobs", layout="wide")
from utils.ui_utils import load_global_css
load_global_css()

st.markdown("""
<style>
.stButton>button { width: 100%; height: 45px; border-radius: 8px; font-size: 15px; }
.section-label {
    font-size: 12px;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
FLARE_KEYS_TO_CLEAR = [
    "flare_tags", "flare_dag_tags",
    "flare_inputs", "flare_steps", "flare_outputs",
    "flare_generated_yaml", "flare_job_name_for_file",
]

for k, v in [
    ("flare_tags",     [""]),
    ("flare_dag_tags", [""]),
    ("flare_inputs",   [{"name": "", "dataset": "", "format": "csv", "infer_schema": True}]),
    ("flare_steps",    [{"name": "final", "sql": ""}]),
    ("flare_outputs",  [{
        "name": "final", "dataset": "", "format": "Iceberg",
        "save_mode": "overwrite", "write_format": "parquet", "compression": "gzip",
    }]),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
# NAV
# ─────────────────────────────────────────────────────────────────────────────
_flare_origin = st.session_state.get("flare_origin", "specific")

def _flare_back():
    if _flare_origin == "cadp_full":
        st.switch_page("pages/cadp_flow.py")
    else:
        st.session_state.home_screen = "specific"
        st.switch_page("app.py")

nav_l, _, nav_r = st.columns([1, 4, 1.5])
with nav_l:
    if st.button("← Back"):
        _flare_back()
with nav_r:
    if st.button("✖ Clear / Start Over"):
        for k in FLARE_KEYS_TO_CLEAR:
            st.session_state.pop(k, None)
        st.rerun()

st.title("CADP — Flare Jobs")
st.caption("Generate a Flare Workflow YAML for ingesting and transforming data into the DataOS lakehouse.")
st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# ADD / REMOVE BUTTONS  (must be outside the form so they trigger reruns)
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
INPUT_FORMATS  = ["csv", "json", "parquet", "orc", "avro", "delta", "iceberg", "text"]
OUTPUT_FORMATS = ["Iceberg", "parquet", "delta", "csv", "json", "orc"]
SAVE_MODES     = ["overwrite", "append", "ignore", "errorIfExists"]
WRITE_FORMATS  = ["parquet", "orc", "avro"]
COMPRESSIONS   = ["gzip", "snappy", "zstd", "none"]
LOG_LEVELS     = ["INFO", "DEBUG", "WARN", "ERROR"]

# ─────────────────────────────────────────────────────────────────────────────
# FORM
# ─────────────────────────────────────────────────────────────────────────────
with st.form("flare_form"):

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 1 — Workflow Metadata
    # ══════════════════════════════════════════════════════════════════════════
    st.subheader("Workflow Metadata")
    st.caption("Required — unique to each job.")

    wm1, wm2 = st.columns(2)
    with wm1:
        wf_name = st.text_input(
            "Workflow Name *",
            placeholder="e.g. wf-product-data",
            help="DAG name is auto-derived: wf-product-data → dg-product-data",
        )
    with wm2:
        wf_desc = st.text_input(
            "Description *",
            value=st.session_state.get("flare_wf_desc", "Ingesting data into the lakehouse"),
        )

    _th1, _th2 = st.columns([5, 1])
    with _th1: st.markdown("**Tags**")
    with _th2:
        if st.form_submit_button("➕ Add", key="flare_add_tag"):
            st.session_state.flare_tags.append(""); st.rerun()
    updated_tags = []
    for i, tag in enumerate(st.session_state.flare_tags):
        tc1, tc2 = st.columns([5, 1])
        with tc1:
            val = st.text_input(f"Tag {i+1}", value=tag, key=f"ftag_{i}",
                                placeholder="e.g. crm", label_visibility="collapsed")
            updated_tags.append(val)
        with tc2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("❌", key=f"rm_ftag_{i}"):
                st.session_state.flare_tags.pop(i); st.rerun()

    st.markdown("**Schedule** — rendered as comments in output (optional)")
    cron_val = st.text_input(
        "Cron Expression",
        placeholder="e.g. 00 20 * * *",
        help="Leave blank to keep the schedule block fully commented out.",
    )

    st.divider()

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 2 — Compute & Stack
    # ══════════════════════════════════════════════════════════════════════════
    st.subheader("Compute & Stack")
    st.caption("Pre-filled with standard defaults — edit only if needed.")

    cs1, cs2, cs3, cs4 = st.columns(4)
    with cs1: stack     = st.text_input("Stack",     value="flare:6.0")
    with cs2: compute   = st.text_input("Compute",   value="runnable-default")
    with cs3: log_level = st.selectbox("Log Level",  LOG_LEVELS, index=0)
    with cs4: explain   = st.checkbox("explain: true", value=True)

    _dth1, _dth2 = st.columns([5, 1])
    with _dth1: st.markdown("**DAG Tags**")
    with _dth2:
        if st.form_submit_button("➕ Add", key="flare_add_dag_tag"):
            st.session_state.flare_dag_tags.append(""); st.rerun()
    updated_dag_tags = []
    for i, tag in enumerate(st.session_state.flare_dag_tags):
        dtc1, dtc2 = st.columns([5, 1])
        with dtc1:
            val = st.text_input(f"DAG Tag {i+1}", value=tag, key=f"fdtag_{i}",
                                placeholder="e.g. crm", label_visibility="collapsed")
            updated_dag_tags.append(val)
        with dtc2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("❌", key=f"rm_fdtag_{i}"):
                st.session_state.flare_dag_tags.pop(i); st.rerun()

    st.divider()

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 3 — Driver & Executor
    # ══════════════════════════════════════════════════════════════════════════
    st.subheader("Driver & Executor Resources")
    st.caption("Pre-filled with standard defaults — edit only if needed.")

    st.markdown("**Driver**")
    dr1, dr2, dr3 = st.columns(3)
    with dr1: drv_core_limit = st.text_input("Core Limit", value="2000m",  key="drv_cl")
    with dr2: drv_cores      = st.number_input("Cores",    value=1, min_value=1, key="drv_c")
    with dr3: drv_memory     = st.text_input("Memory",    value="2000m",  key="drv_m")

    st.markdown("**Executor**")
    ex1, ex2, ex3, ex4 = st.columns(4)
    with ex1: exc_core_limit = st.text_input("Core Limit", value="2000m",  key="exc_cl")
    with ex2: exc_cores      = st.number_input("Cores",    value=1, min_value=1, key="exc_c")
    with ex3: exc_instances  = st.number_input("Instances", value=1, min_value=1, key="exc_i")
    with ex4: exc_memory     = st.text_input("Memory",    value="2000m",  key="exc_m")

    st.divider()

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 4 — Inputs
    # ══════════════════════════════════════════════════════════════════════════
    _inh1, _inh2 = st.columns([5, 1])
    with _inh1: st.subheader("Inputs")
    with _inh2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("➕ Add Input", key="flare_add_inp"):
            st.session_state.flare_inputs.append(
                {"name": "", "dataset": "", "format": "csv", "infer_schema": True}
            ); st.rerun()
    st.caption("Define each input dataset. Dataset path format: `dataos://<depot>:<collection>/<file>?acl=rw`")

    for i, inp in enumerate(st.session_state.flare_inputs):
        st.markdown(f"**Input {i + 1}**")
        ic1, ic2, ic3, ic4 = st.columns([2.5, 3.5, 1.5, 1])
        with ic1:
            st.session_state.flare_inputs[i]["name"] = st.text_input(
                "Input Name *", value=inp["name"], key=f"inp_name_{i}",
                placeholder="e.g. product_data",
            )
        with ic2:
            st.session_state.flare_inputs[i]["dataset"] = st.text_input(
                "Dataset Path *", value=inp["dataset"], key=f"inp_ds_{i}",
                placeholder="e.g. dataos://thirdparty01:onboarding/product.csv?acl=rw",
            )
        with ic3:
            st.session_state.flare_inputs[i]["format"] = st.selectbox(
                "Format",
                INPUT_FORMATS,
                index=INPUT_FORMATS.index(inp["format"]) if inp["format"] in INPUT_FORMATS else 0,
                key=f"inp_fmt_{i}",
            )
        with ic4:
            st.markdown("<br>", unsafe_allow_html=True)
            st.session_state.flare_inputs[i]["infer_schema"] = st.checkbox(
                "inferSchema", value=inp.get("infer_schema", True), key=f"inp_is_{i}",
                help="Adds options.inferSchema: true — recommended for CSV.",
            )
        if i > 0:
            if st.form_submit_button("❌ Remove Input", key=f"rm_inp_{i}"):
                st.session_state.flare_inputs.pop(i); st.rerun()
        if i < len(st.session_state.flare_inputs) - 1:
            st.markdown("---")

    st.divider()

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 5 — Steps (SQL transformations)
    # ══════════════════════════════════════════════════════════════════════════
    _sth1, _sth2 = st.columns([5, 1])
    with _sth1: st.subheader("Steps")
    with _sth2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("➕ Add Step", key="flare_add_step"):
            st.session_state.flare_steps.append({"name": "", "sql": ""}); st.rerun()
    st.caption("Each step is a named SQL transformation. The step name must match the corresponding output name below.")

    for i, step in enumerate(st.session_state.flare_steps):
        st.markdown(f"**Step {i + 1}**")
        sc1, sc2 = st.columns([1, 4])
        with sc1:
            st.session_state.flare_steps[i]["name"] = st.text_input(
                "Step Name *", value=step["name"], key=f"step_name_{i}",
                placeholder="e.g. final",
                help="Use 'final' for the last step — this name links to the output.",
            )
        with sc2:
            st.session_state.flare_steps[i]["sql"] = st.text_area(
                "SQL *", value=step["sql"], key=f"step_sql_{i}", height=160,
                placeholder=(
                    "SELECT\n"
                    "  CAST(customer_id AS DOUBLE) as customer_id,\n"
                    "  product_id,\n"
                    "  product_name\n"
                    "FROM product_data"
                ),
            )
        if i > 0:
            if st.form_submit_button("❌ Remove Step", key=f"rm_step_{i}"):
                st.session_state.flare_steps.pop(i); st.rerun()
        if i < len(st.session_state.flare_steps) - 1:
            st.markdown("---")

    st.divider()

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 6 — Outputs
    # ══════════════════════════════════════════════════════════════════════════
    _oth1, _oth2 = st.columns([5, 1])
    with _oth1: st.subheader("Outputs")
    with _oth2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("➕ Add Output", key="flare_add_out"):
            st.session_state.flare_outputs.append({
                "name": "final", "dataset": "", "format": "Iceberg",
                "save_mode": "overwrite", "write_format": "parquet", "compression": "gzip",
            }); st.rerun()
    st.caption("Each output writes a step result to a DataOS dataset. Output name must match the step name above. Dataset path format: `dataos://<depot>:<collection>/<table>?acl=rw`")

    for i, out in enumerate(st.session_state.flare_outputs):
        st.markdown(f"**Output {i + 1}**")
        oc1, oc2 = st.columns(2)
        with oc1:
            st.session_state.flare_outputs[i]["name"] = st.text_input(
                "Output Name *", value=out["name"], key=f"out_name_{i}",
                placeholder="e.g. final",
                help="Must match the step name whose result you want to write.",
            )
            st.session_state.flare_outputs[i]["dataset"] = st.text_input(
                "Dataset Path *", value=out["dataset"], key=f"out_ds_{i}",
                placeholder="e.g. dataos://icebase:crm/product_data?acl=rw",
            )
        with oc2:
            oa1, oa2 = st.columns(2)
            with oa1:
                st.session_state.flare_outputs[i]["format"] = st.selectbox(
                    "Format", OUTPUT_FORMATS,
                    index=OUTPUT_FORMATS.index(out["format"]) if out["format"] in OUTPUT_FORMATS else 0,
                    key=f"out_fmt_{i}",
                )
                st.session_state.flare_outputs[i]["save_mode"] = st.selectbox(
                    "Save Mode", SAVE_MODES,
                    index=SAVE_MODES.index(out["save_mode"]) if out["save_mode"] in SAVE_MODES else 0,
                    key=f"out_sm_{i}",
                )
            with oa2:
                st.session_state.flare_outputs[i]["write_format"] = st.selectbox(
                    "write.format.default", WRITE_FORMATS,
                    index=WRITE_FORMATS.index(out["write_format"]) if out["write_format"] in WRITE_FORMATS else 0,
                    key=f"out_wf_{i}",
                )
                st.session_state.flare_outputs[i]["compression"] = st.selectbox(
                    "compression-codec", COMPRESSIONS,
                    index=COMPRESSIONS.index(out["compression"]) if out["compression"] in COMPRESSIONS else 0,
                    key=f"out_comp_{i}",
                )
        if i > 0:
            if st.form_submit_button("❌ Remove Output", key=f"rm_out_{i}"):
                st.session_state.flare_outputs.pop(i); st.rerun()
        if i < len(st.session_state.flare_outputs) - 1:
            st.markdown("---")

    st.markdown(" ")
    generate_btn = st.form_submit_button("Generate Flare YAML", use_container_width=True)

# Persist tag lists (must happen after form closes)
st.session_state.flare_tags     = updated_tags
st.session_state.flare_dag_tags = updated_dag_tags

# ─────────────────────────────────────────────────────────────────────────────
# VALIDATE + GENERATE
# ─────────────────────────────────────────────────────────────────────────────
if generate_btn:
    errors = []
    if not wf_name.strip():
        errors.append("Workflow Name is required.")
    if not wf_desc.strip():
        errors.append("Description is required.")
    for i, inp in enumerate(st.session_state.flare_inputs):
        if not inp.get("name", "").strip():
            errors.append(f"Input {i + 1}: Name is required.")
        if not inp.get("dataset", "").strip():
            errors.append(f"Input {i + 1}: Dataset Path is required.")
    for i, step in enumerate(st.session_state.flare_steps):
        if not step.get("name", "").strip():
            errors.append(f"Step {i + 1}: Step Name is required.")
        if not step.get("sql", "").strip():
            errors.append(f"Step {i + 1}: SQL is required.")
    for i, out in enumerate(st.session_state.flare_outputs):
        if not out.get("name", "").strip():
            errors.append(f"Output {i + 1}: Output Name is required.")
        if not out.get("dataset", "").strip():
            errors.append(f"Output {i + 1}: Dataset Path is required.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        flare_data = {
            "name":        wf_name.strip(),
            "description": wf_desc.strip(),
            "tags":        [t for t in st.session_state.flare_tags     if t.strip()],
            "dag_tags":    [t for t in st.session_state.flare_dag_tags if t.strip()],
            "cron":        cron_val.strip(),
            "stack":       stack.strip(),
            "compute":     compute.strip(),
            "log_level":   log_level,
            "explain":     explain,
            "driver": {
                "core_limit": drv_core_limit.strip(),
                "cores":      int(drv_cores),
                "memory":     drv_memory.strip(),
            },
            "executor": {
                "core_limit": exc_core_limit.strip(),
                "cores":      int(exc_cores),
                "instances":  int(exc_instances),
                "memory":     exc_memory.strip(),
            },
            "inputs":  st.session_state.flare_inputs,
            "steps":   st.session_state.flare_steps,
            "outputs": st.session_state.flare_outputs,
        }
        st.session_state.flare_generated_yaml    = generate_flare_yaml(flare_data)
        st.session_state.flare_job_name_for_file = wf_name.strip()

# ─────────────────────────────────────────────────────────────────────────────
# PREVIEW + DOWNLOAD
# ─────────────────────────────────────────────────────────────────────────────
if "flare_generated_yaml" in st.session_state:
    st.divider()
    st.subheader("Flare Workflow YAML Preview")
    show_example(st, "Flare Job YAML", EXAMPLE_FLARE)
    st.code(st.session_state.flare_generated_yaml, language="yaml")
    st.download_button(
        label="⬇ Download Flare YAML",
        data=st.session_state.flare_generated_yaml,
        file_name=f"{st.session_state.get('flare_job_name_for_file', 'flare-job')}.yml",
        mime="text/yaml",
        use_container_width=True,
    )

    if _flare_origin == "cadp_full":
        st.divider()
        st.success("Flare Job complete. Return to the CADP flow to continue.")
        if st.button("Back to CADP Flow", use_container_width=True, type="primary"):
            if "cadp_completed_steps" not in st.session_state:
                st.session_state.cadp_completed_steps = set()
            st.session_state.cadp_completed_steps.add(4)
            st.switch_page("pages/cadp_flow.py")