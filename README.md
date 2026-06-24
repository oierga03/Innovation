# ALK R&D Data Platform

A clickable **Streamlit prototype** of a pharmaceutical R&D data-management platform,
built for usability testing. It is a mock-up only — it does **not** use a real database
(all data is fictional and lives in the browser session).

## Features

- **Login with roles** — every user has a role (Researcher, Scientist, Team Lead,
  Regulatory Affairs, Admin).
- **Folder explorer** — structured documents organised in folders
  (ALK Management, ALK R&D → Researchers / Scientists).
- **Role-based access** — restricted folders show "Access denied" with a
  *Request access* flow; managers approve or deny requests (VPN + role-based control).
- **In-explorer search** — flexible search across multiple categories
  (Project, Department, Type, Owner, Date). Restricted files are not shown.
- **Audit trail per file** — version history with who created / edited / reviewed /
  approved each file, and the latest approved version.
- **SOP Guide** — how to upload and name files, with examples.
- **Feedback box** on every page.

## Run locally

```bash
pip install -r requirements.txt
streamlit run alk_rnd_data_platform.py
```

Then open http://localhost:8501

## Test users

| User      | Role               | Can approve requests |
|-----------|--------------------|----------------------|
| Maria S.  | Researcher         | No                   |
| Alex R.   | Scientist          | No                   |
| Sarah L.  | Team Lead          | Yes                  |
| James K.  | Regulatory Affairs | Yes                  |
| Admin     | Admin              | Yes                  |

The password is fictional — any value works.
