import streamlit as st
import pandas as pd
import random
import json
import datetime
from io import BytesIO
from pathlib import Path
import importlib.util
import streamlit.components.v1 as components
import os
# Config & data paths
st.set_page_config(page_title="TimelyFlow – Smart Timetable Generator", page_icon="📅", layout="wide")
BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
FACULTIES_FILE = DATA_DIR / "faculties.json"
ROOMS_FILE = DATA_DIR / "rooms.json"
GENERATED_FILE = DATA_DIR / "generated_timetable.json"
MANUAL_FILE = DATA_DIR / "manual_entries.json"
UPLOADED_FILE = DATA_DIR / "uploaded_timetable.json"
DATASET_FILE = DATA_DIR / "dataset.json"
GENERATED_XLSX = DATA_DIR / "generated_timetable.xlsx"
MANUAL_XLSX = DATA_DIR / "manual_timetable.xlsx"
# Decorative image path (user-uploaded image from conversation history)
DECOR_IMAGE = "/mnt/data/d88687cf-9ac1-4b25-8934-c31b49840690.png"
# Constants
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
SLOTS = ["9:30-10:30", "10:30-11:30", "11:30-12:30", "12:30-1:30", "1:30-2:30", "2:30-3:30", "3:30-4:30"]
LUNCH_CHOICES = ["12:30-1:30", "1:30-2:30"]
# Helpers
def has_openpyxl():
    return importlib.util.find_spec("openpyxl") is not None
def load_json(path: Path):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []
def save_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
def df_to_excel_bytes(df: pd.DataFrame) -> BytesIO:
    buf = BytesIO()
    if not has_openpyxl():
        raise RuntimeError("openpyxl is required for Excel export.")
    df.to_excel(buf, index=False, engine="openpyxl")
    buf.seek(0)
    return buf
def save_df_excel_to_path(df: pd.DataFrame, path: Path):
    buf = df_to_excel_bytes(df)
    with open(path, "wb") as f:
        f.write(buf.getbuffer())
def safe_unlink(path: Path):
    try:
        if path.exists():
            path.unlink()
            return True
    except Exception:
        return False
    return False
# -----------------------
# Confirmation Dialog 
# -----------------------
# We'll use a single dialog function that reads a message & key from session_state.
# To call a confirmation: set two session_state keys and call confirm_action().
# After the dialog closes the code checks st.session_state[f"confirm_{key}"] for True/False.
if "_confirm_active" not in st.session_state:
    st.session_state["_confirm_active"] = False
@st.dialog("Confirm Action")
def confirm_action():
    msg = st.session_state.get("_confirm_message", "Are you sure?")
    key = st.session_state.get("_confirm_key", "default")

    # Premium layout: warning icon, title, description
    st.markdown("<div style='display:flex;align-items:center; gap:10px'>"
                "<div style='font-size:28px;color:#ff6b6b;'>⚠️</div>"
                "<div style='font-weight:700;font-size:18px;'>Confirm Action</div>"
                "</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='margin-top:8px;font-size:14px;color:#e6e6e6'>{msg}</div>", unsafe_allow_html=True)
    st.write("")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Cancel", key=f"cancel_{key}"):
            st.session_state[f"confirm_{key}"] = False
            st.session_state["_confirm_active"] = False
            st.rerun()
    with c2:
        if st.button("Delete", key=f"delete_{key}"):
            st.session_state[f"confirm_{key}"] = True
            st.session_state["_confirm_active"] = False
            st.rerun()
def ask_confirm(message: str, key: str):
    """Set up a confirmation and open the dialog.
    After calling this function, check st.session_state.get(f"confirm_{key}") is True
    to perform the action.
    """
    # initialize state for this key
    st.session_state[f"confirm_{key}"] = None
    st.session_state["_confirm_message"] = message
    st.session_state["_confirm_key"] = key
    st.session_state["_confirm_active"] = True
    confirm_action()
# Session state init
if "faculties" not in st.session_state:
    st.session_state["faculties"] = load_json(FACULTIES_FILE)
if "rooms" not in st.session_state:
    st.session_state["rooms"] = load_json(ROOMS_FILE)
if "generated_timetable" not in st.session_state:
    gen_data = load_json(GENERATED_FILE)
    st.session_state["generated_timetable"] = pd.DataFrame(gen_data) if gen_data else pd.DataFrame()
if "manual_entries" not in st.session_state:
    man_data = load_json(MANUAL_FILE)
    st.session_state["manual_entries"] = pd.DataFrame(man_data) if man_data else pd.DataFrame()
if "uploaded_preview" not in st.session_state:
    up_data = load_json(UPLOADED_FILE)
    st.session_state["uploaded_preview"] = up_data if up_data else []
# Styling
st.markdown("""
<style>
body {background: linear-gradient(-45deg,#0f2027,#203a43,#2c5364,#1f4037); background-size:400% 400%; animation:gradientBG 15s ease infinite; color:#fff;}
@keyframes gradientBG {0%{background-position:0% 50%;}50%{background-position:100% 50%;}100%{background-position:0% 50%;}}
.main-title {font-size:2.2rem; text-align:center; color:#fff; text-shadow:0 0 10px #00f5ff; margin-bottom:0.2rem;}
.card {background: rgba(255,255,255,0.03); padding: 12px; border-radius:10px; margin-bottom:10px; border: 1px solid rgba(255,255,255,0.04);}
.small-muted {font-size:0.9rem; color: #cbd5e1;}
.big-btn {padding:8px 12px; background:#00f5ff; color:#000; font-weight:700; border-radius:6px; text-decoration:none;}
.delete-confirm {color:#ffb3b3;}
.row-key {font-weight:600;}
</style>
""", unsafe_allow_html=True)
# Header with decorative image (if available)
header_cols = st.columns([1, 5, 1])
with header_cols[0]:
    if Path(DECOR_IMAGE).exists():
        st.image(DECOR_IMAGE, width=80)
with header_cols[1]:
    st.markdown('<div class="main-title">📅 TimelyFlow – Smart Timetable Generator</div>', unsafe_allow_html=True)
with header_cols[2]:
    st.write("")  # reserved
st.markdown("---")
# Router using st.query_params
query = st.query_params
if "view" in query:
    view = query.get("view", "home")
else:
    view = st.sidebar.selectbox("Navigation", ["home", "generated", "manual", "dataset"], index=0)
# HOME VIEW
if view == "home":
    st.header("Home")
    c1, c2, c3 = st.columns(3)
    # -------- QUICK LINKS --------
    with c1:
        st.markdown("<h4>Auto Generated</h4>", unsafe_allow_html=True)
        st.markdown('<a href="?view=generated" target="_blank" class="big-btn">Open Generated →</a>', unsafe_allow_html=True)
    with c2:
        st.markdown("<h4>Manual Timetable</h4>", unsafe_allow_html=True)
        st.markdown('<a href="?view=manual" target="_blank" class="big-btn">Open Manual →</a>', unsafe_allow_html=True)
    with c3:
        st.markdown("<h4>Quick Add Resources</h4>", unsafe_allow_html=True)
        with st.form("add_faculty", clear_on_submit=True):
            fn = st.text_input("Faculty name")
            fs = st.text_input("Subject")
            if st.form_submit_button("Add Faculty"):
                if fn.strip() and fs.strip():
                    st.session_state["faculties"].append({"Faculty": fn.strip(), "Subject": fs.strip()})
                    save_json(FACULTIES_FILE, st.session_state["faculties"])
                    st.success("Faculty added.")
        with st.form("add_room", clear_on_submit=True):
            rn = st.text_input("Room no")
            rc = st.number_input("Capacity", 10, 500, 50)
            if st.form_submit_button("Add Room"):
                if rn.strip():
                    st.session_state["rooms"].append({"Room": rn.strip(), "Capacity": int(rc)})
                    save_json(ROOMS_FILE, st.session_state["rooms"])
                    st.success("Room added.")
    st.markdown("---")
    # -------- CURRENT RESOURCES (UPDATED WITH DELETE) --------
    st.write("### Current Resources")
    col_a, col_b = st.columns(2)
    # FACULTY + SUBJECT TABLE
    with col_a:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Faculties")
        df_fac = pd.DataFrame(st.session_state["faculties"])
        if not df_fac.empty:
            # header row
            h1, h2, h3 = st.columns([3, 3, 1])
            h1.markdown("**Faculty**")
            h2.markdown("**Subject**")
            h3.markdown("**Action**")
            for i, row in df_fac.iterrows():
                c1, c2, c3 = st.columns([3, 3, 1])
                c1.write(row.get("Faculty", ""))
                c2.write(row.get("Subject", ""))
                # delete button per row
                if c3.button("❌", key=f"delete_fac_{i}"):
                    ask_confirm(f"Delete faculty '{row.get('Faculty','')}'?", f"del_fac_{i}")
                # if confirmed, delete and persist
                if st.session_state.get(f"confirm_del_fac_{i}") is True:
                    try:
                        st.session_state["faculties"].pop(i)
                    except Exception:
                        st.session_state["faculties"] = [f for j, f in enumerate(st.session_state["faculties"]) if j != i]
                    save_json(FACULTIES_FILE, st.session_state["faculties"])
                    st.success("Faculty deleted.")
                    # reset confirmation for this key
                    st.session_state[f"confirm_del_fac_{i}"] = None
                    st.experimental_rerun()
            st.markdown("---")
            # delete all with confirmation
            if st.button("🗑 Delete All Faculties"):
                ask_confirm("Delete ALL faculties? This cannot be undone.", "del_all_fac")
            if st.session_state.get("confirm_del_all_fac") is True:
                st.session_state["faculties"] = []
                save_json(FACULTIES_FILE, [])
                st.success("All faculties deleted.")
                st.session_state["confirm_del_all_fac"] = None
                st.experimental_rerun()
        else:
            st.info("No faculty added yet.")
        st.markdown('</div>', unsafe_allow_html=True)
    # ROOMS TABLE
    with col_b:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Rooms")
        df_rooms = pd.DataFrame(st.session_state["rooms"])
        if not df_rooms.empty:
            # header row
            r1, r2, r3 = st.columns([3, 2, 1])
            r1.markdown("**Room**")
            r2.markdown("**Capacity**")
            r3.markdown("**Action**")
            for i, row in df_rooms.iterrows():
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.write(row.get("Room", ""))
                c2.write(row.get("Capacity", ""))
                if c3.button("❌", key=f"delete_room_{i}"):
                    ask_confirm(f"Delete room '{row.get('Room','')}'?", f"del_room_{i}")
                if st.session_state.get(f"confirm_del_room_{i}") is True:
                    try:
                        st.session_state["rooms"].pop(i)
                    except Exception:
                        st.session_state["rooms"] = [r for j, r in enumerate(st.session_state["rooms"]) if j != i]
                    save_json(ROOMS_FILE, st.session_state["rooms"])
                    st.success("Room deleted.")
                    st.session_state[f"confirm_del_room_{i}"] = None
                    st.experimental_rerun()
            st.markdown("---")
            if st.button("🗑 Delete All Rooms"):
                ask_confirm("Delete ALL rooms? This cannot be undone.", "del_all_rooms")
            if st.session_state.get("confirm_del_all_rooms") is True:
                st.session_state["rooms"] = []
                save_json(ROOMS_FILE, [])
                st.success("All rooms deleted.")
                st.session_state["confirm_del_all_rooms"] = None
                st.experimental_rerun()
        else:
            st.info("No rooms added yet.")
        st.markdown('</div>', unsafe_allow_html=True)
    # -------- UPLOAD TIMETABLE --------
    st.markdown("---")
    st.subheader("Upload Timetable (CSV/Excel)")
    uploaded = st.file_uploader("Upload", type=["xlsx", "csv"])
    auto_delete = st.checkbox("Auto-delete after save?", value=False)
    if uploaded:
        try:
            df_up = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded, engine="openpyxl")
            st.success("File loaded")
            st.dataframe(df_up)
            save_json(UPLOADED_FILE, df_up.to_dict(orient="records"))
            save_name = f"uploaded_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded.name}"
            save_path = DATA_DIR / save_name
            with open(save_path, "wb") as f:
                f.write(uploaded.getbuffer())
        except Exception as e:
            st.error(f"Error: {e}")
        if auto_delete:
            safe_unlink(UPLOADED_FILE)
            try:
                safe_unlink(save_path)
            except Exception:
                pass
            st.session_state["uploaded_preview"] = []
            st.experimental_rerun()
# GENERATED VIEW
elif view == "generated":
    st.title("Generated Timetable")
    st.markdown('<a href="?view=home" target="_blank" class="big-btn">Open Home →</a>', unsafe_allow_html=True)
    st.markdown("---")
    with st.form("gen_form"):
        days_sel = st.multiselect("Days", DAYS, default=DAYS[:5])
        slots_sel = st.multiselect("Slots", SLOTS, default=SLOTS)
        lunch_mode = st.selectbox("Lunch", ["Fixed: 12:30-1:30", "Fixed: 1:30-2:30", "Random", "None"])
        gen = st.form_submit_button("Generate")
        if gen:
            if not st.session_state["faculties"] or not st.session_state["rooms"]:
                st.warning("Add faculty/room first.")
            else:
                rows = []
                for d in days_sel:
                    lunch = None
                    if lunch_mode == "Random":
                        lunch = random.choice(LUNCH_CHOICES)
                    elif lunch_mode.startswith("Fixed"):
                        lunch = lunch_mode.split(": ")[1]
                    for s in slots_sel:
                        if lunch and s == lunch:
                            rows.append({"Day": d, "Slot": s, "Subject": "LUNCH", "Faculty": "-", "Room": "-"})
                        else:
                            f = random.choice(st.session_state["faculties"])
                            r = random.choice(st.session_state["rooms"])
                            rows.append({
                                "Day": d,
                                "Slot": s,
                                "Subject": f["Subject"],
                                "Faculty": f["Faculty"],
                                "Room": r["Room"],
                            })
                st.session_state["generated_timetable"] = pd.DataFrame(rows)
                save_json(GENERATED_FILE, rows)
                if has_openpyxl():
                    save_df_excel_to_path(st.session_state["generated_timetable"], GENERATED_XLSX)
    # SHOW TABLE
    if not st.session_state["generated_timetable"].empty:
        st.dataframe(st.session_state["generated_timetable"])
        # DELETE OPTION
        if st.button("🗑 Delete Generated Timetable"):
            ask_confirm("Delete generated timetable?", "del_generated")
        if st.session_state.get("confirm_del_generated") is True:
            st.session_state["generated_timetable"] = pd.DataFrame()
            safe_unlink(GENERATED_FILE)
            safe_unlink(GENERATED_XLSX)
            st.success("Generated timetable deleted.")
            st.session_state["confirm_del_generated"] = None
            st.experimental_rerun()
# MANUAL VIEW
elif view == "manual":
    st.title("Manual Timetable Entry")
    st.markdown('<a href="?view=home" target="_blank" class="big-btn">Open Home →</a>', unsafe_allow_html=True)
    st.markdown("---")
    with st.form("manual_form"):
        mday = st.selectbox("Day", DAYS)
        mslot = st.selectbox("Slot", SLOTS)
        msubject = st.text_input("Subject")
        mfaculty = st.text_input("Faculty")
        mroom = st.text_input("Room")
        if st.form_submit_button("Add"):
            new = {"Day": mday, "Slot": mslot, "Subject": msubject, "Faculty": mfaculty, "Room": mroom}
            if st.session_state["manual_entries"].empty:
                st.session_state["manual_entries"] = pd.DataFrame([new])
            else:
                st.session_state["manual_entries"] = pd.concat(
                    [st.session_state["manual_entries"], pd.DataFrame([new])],
                    ignore_index=True
                )
            save_json(MANUAL_FILE, st.session_state["manual_entries"].to_dict(orient="records"))
            if has_openpyxl():
                save_df_excel_to_path(st.session_state["manual_entries"], MANUAL_XLSX)
    # SHOW TABLE
    if not st.session_state["manual_entries"].empty:
        st.dataframe(st.session_state["manual_entries"])
        # DELETE OPTION
        if st.button("🗑 Delete Manual Entries"):
            ask_confirm("Delete all manual entries?", "del_manual")
        if st.session_state.get("confirm_del_manual") is True:
            st.session_state["manual_entries"] = pd.DataFrame()
            safe_unlink(MANUAL_FILE)
            safe_unlink(MANUAL_XLSX)
            st.success("Manual timetable deleted.")
            st.session_state["confirm_del_manual"] = None
            st.experimental_rerun()
# DATASET VIEW
elif view == "dataset":
    st.title("Dataset Upload / Preview")
    st.markdown('<a href="?view=home" target="_blank" class="big-btn">Open Home →</a>', unsafe_allow_html=True)
    st.markdown("---")

    data = st.session_state.get("uploaded_preview", [])
    if data:
        st.write("### Uploaded Preview")
        st.dataframe(pd.DataFrame(data))

        # DELETE UPLOADED PREVIEW
        if st.button("🗑 Delete Uploaded Preview"):
            ask_confirm("Delete the uploaded preview?", "del_preview")

        if st.session_state.get("confirm_del_preview") is True:
            st.session_state["uploaded_preview"] = []
            safe_unlink(UPLOADED_FILE)
            st.success("Uploaded preview deleted.")
            st.session_state["confirm_del_preview"] = None
            st.experimental_rerun()
    st.subheader("Upload Dataset")
    dataset_file = st.file_uploader("Dataset", type=["csv", "xlsx"])
    if dataset_file:
        try:
            df_dataset = pd.read_csv(dataset_file) if dataset_file.name.endswith(".csv") else pd.read_excel(dataset_file, engine="openpyxl")
            st.dataframe(df_dataset)
            save_json(DATASET_FILE, df_dataset.to_dict(orient="records"))
            st.success("Dataset saved.")
        except Exception as e:
            st.error(str(e))
    # DELETE DATASET
    if DATASET_FILE.exists():
        if st.button("🗑 Delete Dataset"):
            ask_confirm("Delete dataset file?", "del_dataset")

        if st.session_state.get("confirm_del_dataset") is True:
            safe_unlink(DATASET_FILE)
            st.success("Dataset deleted.")
            st.session_state["confirm_del_dataset"] = None
            st.experimental_rerun()
else:
    st.error("Unknown view.")
