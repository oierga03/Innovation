"""
DataCompas - Streamlit Prototype
============================================

Clickable MOCK-UP for usability testing. It does NOT use a real database:
all data is fictional and lives only in the browser session memory.

How to run:
    pip install streamlit pandas
    streamlit run alk_rnd_data_platform.py
    # if "streamlit" is not recognized:  python -m streamlit run alk_rnd_data_platform.py

GENERAL IDEA:
    - When the app opens you must LOG IN (every user has a role).
    - Then you see a FOLDER EXPLORER:
          ALK Management
          ALK R&D
              - Researchers
              - Scientists
    - Each folder has allowed roles. If your role CANNOT enter, you see
      "Access denied" and a button to REQUEST ACCESS.
    - Managers (Team Lead / Regulatory Affairs / Admin) see the requests
      and can APPROVE or DENY them.
    - Each FILE has its own AUDIT TRAIL (version history) and a STATUS
      (Approved / Draft): it opens from the explorer, there is no separate section.
    - Newly uploaded files start as DRAFT (not approved yet).

HOW TO EDIT (for students):
    - USERS         -> users and their role.
    - TREE          -> folder structure, allowed roles and files.
    - MANAGER_ROLES -> roles allowed to approve requests.
    Each "page" is a function (page_browse, page_requests, page_sop).
    The colour theme is in .streamlit/config.toml and in the CSS block below.

Only Streamlit and pandas are used.
"""

from datetime import date, datetime, timedelta

import streamlit as st
import pandas as pd

# ---------------------------------------------------------------------------
# PAGE CONFIG + STYLES
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="DataCompas",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS for the "pharma / enterprise" blue & white look.
# Base colours are also in .streamlit/config.toml
NAVY = "#0A3D66"        # dark blue for the sidebar
BRAND = "#0B5FA5"       # brand blue

st.markdown(
    f"""
    <style>
        /* ---- Sidebar (corporate dark blue) ---- */
        section[data-testid="stSidebar"] {{
            background-color: {NAVY};
        }}
        section[data-testid="stSidebar"] * {{ color: #FFFFFF !important; }}

        /* Navigation buttons (inactive): translucent, readable */
        section[data-testid="stSidebar"] .stButton button {{
            background-color: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.18);
            text-align: left;
            font-weight: 500;
            transition: background-color 0.15s ease;
        }}
        section[data-testid="stSidebar"] .stButton button:hover {{
            background-color: rgba(255,255,255,0.20);
            border-color: rgba(255,255,255,0.35);
        }}
        /* ACTIVE navigation button (type=primary): white pill with blue text */
        section[data-testid="stSidebar"] .stButton button[kind="primary"],
        section[data-testid="stSidebar"] .stButton button[kind="primary"] * {{
            background-color: #FFFFFF !important;
            color: {BRAND} !important;
            border: none !important;
            font-weight: 700 !important;
        }}

        /* ---- Header ---- */
        .alk-title    {{ color:{BRAND}; font-size:2.2rem; font-weight:700; margin-bottom:0; }}
        .alk-subtitle {{ color:#5A6B7B; font-size:1.05rem; margin-top:0; margin-bottom:0.4rem; }}

        /* ---- Cards and notices ---- */
        .alk-restricted {{ background:#FCE8E6; border-left:6px solid #C5221F; padding:1rem; border-radius:8px; }}
        .alk-user       {{ background:rgba(255,255,255,0.10); border-radius:8px; padding:0.7rem 0.9rem; margin-bottom:0.4rem; }}

        /* Metadata label/value */
        .alk-label {{ color:#5A6B7B; font-size:0.78rem; text-transform:uppercase; letter-spacing:0.03em; }}
        .alk-value {{ color:#1F2A37; font-size:0.98rem; font-weight:600; }}

        /* Status badge */
        .alk-badge        {{ display:inline-block; padding:2px 12px; border-radius:12px;
                             font-size:0.78rem; font-weight:700; color:#FFFFFF; }}
        .alk-badge-appr   {{ background:#1E8E3E; }}
        .alk-badge-draft  {{ background:#B26A00; }}

        /* Audit trail event: timeline with side border */
        .alk-event {{ background:#F4F8FC; border-left:4px solid {BRAND}; padding:0.6rem 0.9rem;
                      border-radius:6px; margin-bottom:0.5rem; }}
        .alk-event-approved {{ border-left-color:#1E8E3E; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# FICTIONAL DATA: USERS, ROLES AND FOLDERS
# ---------------------------------------------------------------------------
# Mock-up users. The password is fictional (any value works).
USERS = {
    "maria.s": {"name": "Maria S.", "role": "Researcher"},
    "alex.r":  {"name": "Alex R.",  "role": "Scientist"},
    "sarah.l": {"name": "Sarah L.", "role": "Team Lead"},
    "james.k": {"name": "James K.", "role": "Regulatory Affairs"},
    "admin":   {"name": "Admin",    "role": "Admin"},
}

# Roles allowed to APPROVE / DENY access requests.
MANAGER_ROLES = {"Team Lead", "Regulatory Affairs", "Admin"}

# Folder structure (tree).
#   - "_roles"   = roles allowed to ENTER this folder.
#   - "_files"   = files inside the folder. Each file may have its own
#                  "history"; if not, a believable one is generated.
#   - any other key = subfolder.
TREE = {
    "ALK Management": {
        "_roles": ["Team Lead", "Regulatory Affairs", "Admin"],
        "_files": [
            {"File Name": "Budget_2024.xlsx",     "Type": "XLSX", "Project": "Operations", "Department": "Management", "Owner": "Sarah L.", "Date": "2024-02-10", "Version": "v2"},
            {"File Name": "Strategy_Roadmap.pdf",  "Type": "PDF",  "Project": "Operations", "Department": "Management", "Owner": "James K.", "Date": "2024-04-01", "Version": "v1"},
        ],
    },
    "ALK R&D": {
        "_roles": ["Researcher", "Scientist", "Team Lead", "Regulatory Affairs", "Admin"],
        "_files": [
            {"File Name": "RnD_Overview_2024.pdf", "Type": "PDF", "Project": "Aurora", "Department": "R&D", "Owner": "Sarah L.", "Date": "2024-01-15", "Version": "v1"},
        ],
        "Researchers": {
            "_roles": ["Researcher", "Team Lead", "Admin"],
            "_files": [
                {
                    "File Name": "Experiment_15_Result.xlsx", "Type": "XLSX",
                    "Project": "Aurora", "Department": "Immunology",
                    "Owner": "Maria S.", "Date": "2024-03-12", "Version": "v3",
                    # Detailed example history for this file. Roles match the USERS table.
                    "history": [
                        {"Action": "Created",  "By": "Maria S.", "Role": "Researcher",         "Version": "v1", "Timestamp": "2024-03-01 09:14"},
                        {"Action": "Edited",   "By": "Maria S.", "Role": "Researcher",         "Version": "v2", "Timestamp": "2024-03-05 14:32"},
                        {"Action": "Reviewed", "By": "Sarah L.", "Role": "Team Lead",          "Version": "v3", "Timestamp": "2024-03-09 11:05"},
                        {"Action": "Approved", "By": "James K.", "Role": "Regulatory Affairs", "Version": "v3", "Timestamp": "2024-03-12 16:47"},
                    ],
                },
                {"File Name": "Protocol_Cell_Culture.docx", "Type": "DOCX", "Project": "Aurora", "Department": "Cell Biology", "Owner": "Maria S.", "Date": "2023-11-20", "Version": "v2"},
            ],
        },
        "Scientists": {
            "_roles": ["Scientist", "Team Lead", "Admin"],
            "_files": [
                {"File Name": "Immunology_Data.csv", "Type": "CSV",  "Project": "Cygnus",   "Department": "Immunology", "Owner": "Alex R.", "Date": "2024-01-08", "Version": "v5"},
                {"File Name": "Assay_Analysis.xlsx", "Type": "XLSX", "Project": "Borealis", "Department": "Clinical",   "Owner": "Alex R.", "Date": "2024-05-22", "Version": "v1"},
            ],
        },
    },
}


# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------
def init_state():
    st.session_state.setdefault("user", None)      # key of the logged-in user
    st.session_state.setdefault("page", "browse")   # current page
    st.session_state.setdefault("path", [])          # current folder
    st.session_state.setdefault("requests", [])      # access requests
    st.session_state.setdefault("granted", set())    # granted access: "user||path"
    st.session_state.setdefault("uploads", {})        # files uploaded this session: "path" -> [files]
    st.session_state.setdefault("approvals", {})      # approvals this session: file uid -> approval event


def current_role():
    return USERS[st.session_state.user]["role"]


def current_name():
    return USERS[st.session_state.user]["name"]


# ---------------------------------------------------------------------------
# FOLDER TREE HELPERS
# ---------------------------------------------------------------------------
def get_node(path):
    node = TREE
    for part in path:
        node = node[part]
    return node


def can_access_path(path_list):
    """True if the current user can access the folder at `path_list` (by role or granted)."""
    node = get_node(path_list)
    if "_roles" not in node:        # the root only requires being logged in
        return True
    if current_role() in node["_roles"]:
        return True
    key = f"{st.session_state.user}||{'/'.join(path_list)}"
    return key in st.session_state.granted


def folder_files(node, path):
    """Files of a folder = tree files + files uploaded this session.
    Each is returned as a copy tagged with its folder path ("_path")."""
    base = node.get("_files", [])
    uploaded = st.session_state.uploads.get("/".join(path), [])
    return [{**f, "_path": path} for f in base + uploaded]


def file_uid(f):
    """Unique id for a file = folder path + name (used for approvals and widget keys)."""
    return "/".join(f.get("_path", [])) + "||" + f["File Name"]


def subfolders_of(node):
    """Names of the subfolders inside a node (keys that are not metadata)."""
    return [k for k in node.keys() if not k.startswith("_")]


def count_items(node, path):
    """How many items (subfolders + files) a folder contains, for the counter badge."""
    return len(subfolders_of(node)) + len(folder_files(node, path))


def all_files(node=None, path=None):
    """Flatten the whole tree into a list of files, each tagged with its folder path ("_path")."""
    if node is None:
        node, path = TREE, []
    results = list(folder_files(node, path))  # already tagged with "_path"
    for name in subfolders_of(node):
        results.extend(all_files(node[name], path + [name]))  # recurse into subfolders
    return results


def get_history(f):
    """Return a file's audit trail.

    If the file has an explicit "history" we use it. Otherwise we build a
    believable one spread over several days: Created (v1) -> [Edited] ->
    Reviewed -> Approved on the file's date.
    Uploaded files carry their own short history, so they stay as DRAFT
    until a manager approves them (that approval is stored in session state).
    """
    if "history" in f:
        history = list(f["history"])
    else:
        owner, version = f["Owner"], f["Version"]
        try:
            approved_day = datetime.strptime(f["Date"], "%Y-%m-%d")
        except ValueError:
            approved_day = datetime.now()
        # Version number, e.g. "v3" -> 3.
        n = int(version[1:]) if version.startswith("v") and version[1:].isdigit() else 1

        history = [{"Action": "Created", "By": owner, "Role": "Researcher", "Version": "v1",
                    "Timestamp": (approved_day - timedelta(days=11)).strftime("%Y-%m-%d 09:14")}]
        if n > 1:  # there were edits between v1 and the current version
            history.append({"Action": "Edited", "By": owner, "Role": "Researcher", "Version": version,
                            "Timestamp": (approved_day - timedelta(days=7)).strftime("%Y-%m-%d 14:05")})
        history.append({"Action": "Reviewed", "By": "Sarah L.", "Role": "Team Lead", "Version": version,
                        "Timestamp": (approved_day - timedelta(days=3)).strftime("%Y-%m-%d 11:30")})
        history.append({"Action": "Approved", "By": "James K.", "Role": "Regulatory Affairs", "Version": version,
                        "Timestamp": approved_day.strftime("%Y-%m-%d 16:20")})

    # Append a manager approval made during this session (e.g. for an upload).
    approval = st.session_state.approvals.get(file_uid(f))
    if approval and not any(e["Action"] == "Approved" for e in history):
        history = history + [approval]
    return history


def file_status(f):
    """A file is Approved if its audit trail contains an Approved event, else Draft."""
    return "Approved" if any(e["Action"] == "Approved" for e in get_history(f)) else "Draft"


# ---------------------------------------------------------------------------
# FEEDBACK BOX (at the bottom of every page)
# ---------------------------------------------------------------------------
def feedback_box(page_name: str):
    st.markdown("---")
    with st.expander("Quick feedback (help us improve this prototype)"):
        st.text_area("What was easy to understand?", key=f"easy_{page_name}")
        st.text_area("What was confusing?", key=f"conf_{page_name}")
        st.radio("Would you use this in your daily work?", ["Yes", "Maybe", "No"],
                 horizontal=True, key=f"use_{page_name}")
        if st.button("Submit feedback", key=f"sub_{page_name}"):
            st.success("Thank you! Your feedback has been recorded (mock-up).")


# ---------------------------------------------------------------------------
# LOGIN SCREEN
# ---------------------------------------------------------------------------
def render_login():
    st.markdown("---")
    col = st.columns([1, 2, 1])[1]
    with col:
        with st.container(border=True):
            st.subheader("Sign in")
            st.caption("Select a test user. The password is fictional.")
            options = {f"{u['name']}  ·  {u['role']}": key for key, u in USERS.items()}
            choice = st.selectbox("User", list(options.keys()))
            st.text_input("Password", type="password", placeholder="(any value)")
            if st.button("Log in", type="primary", use_container_width=True):
                st.session_state.user = options[choice]
                st.session_state.path = []
                st.session_state.page = "browse"
                st.rerun()

        st.info(
            "**Tester hint:** log in as *Maria S. (Researcher)* and try to open "
            "**ALK Management** or **Scientists** — you will see 'Access denied' and "
            "you can request access. Then log in as *Sarah L. (Team Lead)* to approve it."
        )


# ---------------------------------------------------------------------------
# PAGE: FOLDER EXPLORER (with built-in search)
# ---------------------------------------------------------------------------
def page_browse():
    st.subheader("File explorer")

    # ---- Search bar (lives inside the explorer) ----
    query = st.text_input("Search", placeholder="Search by name, owner, project or department…",
                          label_visibility="collapsed")

    # Only files in folders the current user can access. Restricted files are
    # never included in the search (they don't even show up as locked).
    accessible = [f for f in all_files() if can_access_path(f["_path"])]

    # Optional filters across multiple categories.
    with st.expander("Filters"):
        def opts(field):
            return ["All"] + sorted({f.get(field, "—") for f in accessible})
        c1, c2, c3 = st.columns(3)
        project = c1.selectbox("Project", opts("Project"))
        department = c2.selectbox("Department", opts("Department"))
        ftype = c3.selectbox("Type", opts("Type"))
        c4, c5 = st.columns(2)
        owner = c4.selectbox("Owner", opts("Owner"))
        status = c5.selectbox("Status", ["All", "Approved", "Draft"])
        # Date range filter (from / to).
        use_date = st.checkbox("Filter by date range")
        d1, d2 = st.columns(2)
        date_from = d1.date_input("From", value=date(2023, 1, 1), disabled=not use_date)
        date_to = d2.date_input("To", value=date.today(), disabled=not use_date)

    # The search view activates when there is a query or any active filter.
    filters_on = any(v != "All" for v in (project, department, ftype, owner, status))
    search_active = bool(query) or filters_on or use_date

    if search_active:
        res = accessible
        if query:
            q = query.lower()
            # Flexible search: name, owner, project and department.
            res = [f for f in res if q in f["File Name"].lower()
                   or q in str(f.get("Owner", "")).lower()
                   or q in str(f.get("Project", "")).lower()
                   or q in str(f.get("Department", "")).lower()]
        if project != "All":
            res = [f for f in res if f.get("Project") == project]
        if department != "All":
            res = [f for f in res if f.get("Department") == department]
        if ftype != "All":
            res = [f for f in res if f["Type"] == ftype]
        if owner != "All":
            res = [f for f in res if f["Owner"] == owner]
        if status != "All":
            res = [f for f in res if file_status(f) == status]
        if use_date:
            lo, hi = date_from.strftime("%Y-%m-%d"), date_to.strftime("%Y-%m-%d")
            res = [f for f in res if lo <= f["Date"] <= hi]

        st.markdown("---")
        st.markdown(f"**Search results ({len(res)})**")
        if not res:
            st.info("No accessible files match your search. Try clearing some filters.")
        else:
            for f in res:
                render_file_card(f, location="/".join(f["_path"]) or "/")
        feedback_box("browse")
        return  # in search mode we don't show the folder navigation

    st.markdown("---")

    # ---- Breadcrumb (path with buttons to go back) ----
    crumb_cols = st.columns(len(st.session_state.path) + 1)
    if crumb_cols[0].button("Home"):
        st.session_state.path = []
        st.rerun()
    for i, part in enumerate(st.session_state.path):
        if crumb_cols[i + 1].button(part):
            st.session_state.path = st.session_state.path[: i + 1]
            st.rerun()

    st.markdown("---")
    node = get_node(st.session_state.path)

    # ---- Access control ----
    if not can_access_path(st.session_state.path):
        render_access_denied()
        feedback_box("browse")
        return

    # ---- Subfolders (with a counter of items inside) ----
    subfolders = subfolders_of(node)
    if subfolders:
        st.markdown("**Folders**")
        cols = st.columns(3)
        for i, folder in enumerate(subfolders):
            child = node[folder]
            child_path = st.session_state.path + [folder]
            locked = "" if can_access_path(child_path) else "🔒 "
            count = count_items(child, child_path)
            if cols[i % 3].button(f"{locked}{folder}  ·  {count} items",
                                  key=f"folder_{folder}", use_container_width=True):
                st.session_state.path = child_path
                st.rerun()
        st.write("")

    # ---- Files (each one opens to show its audit trail) ----
    files = folder_files(node, st.session_state.path)
    if files:
        st.markdown("**Files**")
        st.caption("Open a file to see its audit trail.")
        for f in files:
            render_file_card(f)

    # ---- Upload (only inside a real folder, not at the root) ----
    if st.session_state.path:
        render_upload()

    if not subfolders and not files:
        st.info("This folder is empty.")

    feedback_box("browse")


def render_file_card(f, location=None):
    """Show a file as an expander with its status, metadata and audit trail.

    `location` (optional) shows the folder path of the file; used by the
    in-explorer search so results from other folders are easy to place.
    """
    status = file_status(f)
    # A unique id per file = folder path + file name (avoids widget key clashes
    # when two files share the same name in different folders).
    uid = file_uid(f)

    with st.expander(f"{f['File Name']}   ·   {f['Version']}   ·   {status}"):
        # Status badge.
        badge_class = "alk-badge-appr" if status == "Approved" else "alk-badge-draft"
        st.markdown(f'<span class="alk-badge {badge_class}">{status}</span>',
                    unsafe_allow_html=True)
        if location:
            st.caption(f"Location: {location}")

        # Metadata as a clean label/value grid (no oversized metrics).
        cols = st.columns(4)
        for col, label, value in zip(
            cols,
            ["Type", "Owner", "Date", "Version"],
            [f["Type"], f["Owner"], f["Date"], f["Version"]],
        ):
            col.markdown(f'<div class="alk-label">{label}</div>'
                         f'<div class="alk-value">{value}</div>', unsafe_allow_html=True)
        st.caption(f"Project: {f.get('Project', '—')}  ·  Department: {f.get('Department', '—')}")

        st.markdown("##### Audit trail")
        # View selector (full / approvals only), one key per file.
        view = st.radio("View", ["Full history", "Approvals only"],
                        horizontal=True, key=f"view_{uid}", label_visibility="collapsed")
        history = get_history(f)
        events = [e for e in history if e["Action"] == "Approved"] \
            if view == "Approvals only" else history

        if not events:
            st.caption("No approval events yet.")
        for e in events:
            extra = " alk-event-approved" if e["Action"] == "Approved" else ""
            st.markdown(
                f'<div class="alk-event{extra}"><b>{e["Action"]}</b> by '
                f'<b>{e["By"]}</b> ({e["Role"]}) · version <b>{e["Version"]}</b><br>'
                f'<span style="color:#5A6B7B;">{e["Timestamp"]}</span></div>',
                unsafe_allow_html=True,
            )

        # Summary: latest approved version, or a draft notice + approval action.
        approved = [e for e in history if e["Action"] == "Approved"]
        if approved:
            last = approved[-1]
            st.success(f"Latest approved version: {last['Version']} "
                       f"(by {last['By']}, {last['Timestamp']})")
        else:
            st.warning("Draft — this file has not been approved yet.")
            # Managers can approve the draft here; it then becomes Approved
            # and the approval is recorded in the audit trail above.
            if current_role() in MANAGER_ROLES:
                if st.button("Approve this version", key=f"approve_{uid}", type="primary"):
                    st.session_state.approvals[uid] = {
                        "Action": "Approved", "By": current_name(),
                        "Role": current_role(), "Version": f["Version"],
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                    st.rerun()
            else:
                st.caption("Only a manager (Team Lead, Regulatory Affairs or Admin) "
                           "can approve this file.")


def render_upload():
    """Upload form for the current folder. The saved file really appears in the list
    (stored in the session, visible until the page is refreshed) and starts as DRAFT."""
    key = "/".join(st.session_state.path)
    node = get_node(st.session_state.path)
    existing_names = {x["File Name"] for x in folder_files(node, st.session_state.path)}

    with st.expander("Upload a file to this folder"):
        up = st.file_uploader("Choose a file", type=["csv", "xlsx", "pdf", "docx", "png"],
                              key=f"up_{key}")
        c1, c2 = st.columns(2)
        owner = c1.text_input("Owner", value=current_name(), key=f"own_{key}")
        version = c2.text_input("Version", value="v1", key=f"ver_{key}")
        project = c1.text_input("Project", key=f"proj_{key}")
        department = c2.text_input("Department", key=f"dept_{key}")

        if st.button("Save file", key=f"save_{key}", type="primary"):
            if up is None:
                st.warning("Please choose a file first.")
            elif up.name in existing_names:
                # Duplicate warning: a file with this name already exists here.
                st.error(f"A file named '{up.name}' already exists in this folder. "
                         "Rename it or upload it as a new version.")
            else:
                ext = up.name.rsplit(".", 1)[-1].upper() if "." in up.name else "FILE"
                now = datetime.now()
                new_file = {
                    "File Name": up.name,
                    "Type": ext,
                    "Project": project or "—",
                    "Department": department or "—",
                    "Owner": owner or current_name(),
                    "Date": now.strftime("%Y-%m-%d"),
                    "Version": version or "v1",
                    # New uploads are DRAFT: only an "Uploaded" event, no approval yet.
                    "history": [{
                        "Action": "Uploaded", "By": owner or current_name(),
                        "Role": current_role(), "Version": version or "v1",
                        "Timestamp": now.strftime("%Y-%m-%d %H:%M"),
                    }],
                }
                st.session_state.uploads.setdefault(key, []).append(new_file)
                st.success(f"'{up.name}' saved as DRAFT — it now appears in the list above.")
                st.rerun()


def render_access_denied():
    """Access-denied screen + request access button."""
    folder = st.session_state.path[-1]
    path = "/".join(st.session_state.path)

    st.markdown(
        f'<div class="alk-restricted"><b>Access denied</b><br>'
        f"Your role (<b>{current_role()}</b>) does not have permission to enter "
        f"<b>{folder}</b>.</div>",
        unsafe_allow_html=True,
    )
    st.write("")

    pending = [r for r in st.session_state.requests
               if r["user"] == st.session_state.user and r["folder"] == path
               and r["status"] == "Pending"]
    denied = [r for r in st.session_state.requests
              if r["user"] == st.session_state.user and r["folder"] == path
              and r["status"] == "Denied"]

    if pending:
        st.info("You have already requested access. Waiting for a manager's approval.")
    else:
        if denied:
            st.warning("Your previous request was denied. You can request it again.")
        if st.button("Request access", type="primary"):
            st.session_state.requests.append({
                "user": st.session_state.user, "user_name": current_name(),
                "role": current_role(), "folder": path, "status": "Pending",
            })
            st.rerun()

    st.info(
        "Access is controlled by **role-based permissions** and **VPN** authentication. "
        "A manager must approve the requests."
    )


# ---------------------------------------------------------------------------
# PAGE: ACCESS REQUESTS
# ---------------------------------------------------------------------------
def page_requests():
    st.subheader("Approvals")
    is_manager = current_role() in MANAGER_ROLES

    if is_manager:
        # ---- Pending file approvals (every Draft file the manager can access) ----
        st.markdown("##### Pending file approvals")
        drafts = [f for f in all_files()
                  if can_access_path(f["_path"]) and file_status(f) == "Draft"]
        if not drafts:
            st.success("No files awaiting approval.")
        for f in drafts:
            with st.container(border=True):
                location = "/".join(f["_path"]) or "/"
                st.markdown(f'**{f["File Name"]}**  ·  {f["Version"]}  —  _{location}_')
                st.caption(f"Owner: {f['Owner']}  ·  Project: {f.get('Project', '—')}  ·  "
                           f"Department: {f.get('Department', '—')}")
                if st.button("Approve", key=f"apprfile_{file_uid(f)}", type="primary"):
                    st.session_state.approvals[file_uid(f)] = {
                        "Action": "Approved", "By": current_name(),
                        "Role": current_role(), "Version": f["Version"],
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                    st.rerun()
        st.markdown("---")

        # ---- Folder access requests ----
        st.markdown("##### Access requests")
        pending = [r for r in st.session_state.requests if r["status"] == "Pending"]
        if not pending:
            st.success("No pending access requests.")
        for idx, req in enumerate(st.session_state.requests):
            if req["status"] != "Pending":
                continue
            with st.container(border=True):
                st.markdown(f'**{req["user_name"]}** ({req["role"]}) requests access to '
                            f'**{req["folder"]}**')
                c1, c2, _ = st.columns([1, 1, 4])
                if c1.button("Approve", key=f"appr_{idx}", type="primary"):
                    req["status"] = "Approved"
                    st.session_state.granted.add(f'{req["user"]}||{req["folder"]}')
                    st.rerun()
                if c2.button("Deny", key=f"deny_{idx}"):
                    req["status"] = "Denied"
                    st.rerun()
        st.markdown("---")

    st.markdown("##### My access requests")
    mine = [r for r in st.session_state.requests if r["user"] == st.session_state.user]
    if mine:
        st.dataframe(
            pd.DataFrame([{"Folder": r["folder"], "Status": r["status"]} for r in mine]),
            use_container_width=True, hide_index=True,
        )
    else:
        st.caption("You have not requested access to any folder yet.")

    feedback_box("requests")


# ---------------------------------------------------------------------------
# PAGE: SOP GUIDE
# ---------------------------------------------------------------------------
def page_sop():
    st.subheader("SOP Guide")
    st.write("Standard Operating Procedure for uploading and naming files.")

    st.markdown("##### How to upload a file")
    st.markdown(
        """
        1. Go to the correct folder in the **Explorer**.
        2. Use **Upload a file** (CSV, XLSX, PDF, DOCX or PNG).
        3. Make sure there is no unclassified sensitive data.
        4. Always add the version. New files start as **Draft** until approved.
        """
    )

    st.markdown("##### How to name a file")
    st.markdown(
        """
        Recommended pattern: `Project_Topic_Description_Version`
        - Use underscores `_` instead of spaces.
        - Always add a version (`v1`, `v2`...).
        - Use dates as `YYYY-MM-DD`.
        """
    )

    st.markdown("##### Examples of correct file names")
    st.code(
        "Experiment_15_Result_v3.xlsx\n"
        "Aurora_StudyReport_2024-06-01_v1.pdf\n"
        "CellCulture_Protocol_v2.docx\n"
        "Immunology_AssayData_v5.csv",
        language="text",
    )

    st.markdown("---")
    rating = st.slider("How useful was this guidance? (1 = not useful, 5 = very useful)", 1, 5, 3)
    if st.button("Submit rating", type="primary"):
        st.success(f"Thanks! You rated the guidance {rating}/5.")

    feedback_box("sop")


# ---------------------------------------------------------------------------
# SIDEBAR + MAIN ROUTING
# ---------------------------------------------------------------------------
def nav_button(label, page_key):
    """Sidebar navigation button. The active one is highlighted (type=primary)."""
    is_active = st.session_state.page == page_key
    if st.sidebar.button(label, key=f"nav_{page_key}", use_container_width=True,
                         type="primary" if is_active else "secondary"):
        st.session_state.page = page_key
        st.rerun()


def main():
    init_state()

    # Header (always visible).
    st.markdown('<p class="alk-title">DataCompas</p>', unsafe_allow_html=True)
    st.markdown('<p class="alk-subtitle">Find, organise and trust R&D data</p>',
                unsafe_allow_html=True)
    st.markdown("---")

    # No session -> login only.
    if not st.session_state.user:
        render_login()
        return

    # ---- Sidebar ----
    st.sidebar.title("🧭 DataCompas")
    st.sidebar.markdown(
        f'<div class="alk-user"><b>{current_name()}</b><br>'
        f'<span style="opacity:0.85;">{current_role()}</span></div>',
        unsafe_allow_html=True,
    )

    # Approvals label with a counter for managers (draft files + access requests).
    req_label = "Approvals"
    if current_role() in MANAGER_ROLES:
        pending_reqs = len([r for r in st.session_state.requests if r["status"] == "Pending"])
        pending_files = len([f for f in all_files()
                             if can_access_path(f["_path"]) and file_status(f) == "Draft"])
        total = pending_reqs + pending_files
        if total:
            req_label += f"  ({total})"

    st.sidebar.markdown("###### Navigation")
    nav_button("Explorer", "browse")
    nav_button(req_label, "requests")
    nav_button("SOP Guide", "sop")

    st.sidebar.markdown("---")
    if st.sidebar.button("Log out", use_container_width=True):
        st.session_state.user = None
        st.session_state.path = []
        st.rerun()

    # Prototype signature (footer).
    st.sidebar.markdown("---")
    st.sidebar.caption("DataCompas · Prototype v1.0\nUsability mock-up — not a real database")

    # ---- Routing ----
    if st.session_state.page == "browse":
        page_browse()
    elif st.session_state.page == "requests":
        page_requests()
    elif st.session_state.page == "sop":
        page_sop()


if __name__ == "__main__":
    main()
