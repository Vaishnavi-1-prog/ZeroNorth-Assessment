import streamlit as st
from datetime import date, datetime
import database as db
import ai_helper

st.set_page_config(page_title="Smart Task Manager", layout="wide")
db.init_db()

st.title("🗂️ Smart Task Manager")

# ---------- Sidebar: Add Task ----------
st.sidebar.header("➕ Add a New Task")

with st.sidebar.form("add_task_form"):
    title = st.text_input("Title")
    description = st.text_area("Description", height=80)
    due_date = st.date_input("Due date", value=date.today())

    # Bonus: let user get an AI priority suggestion before picking one
    suggested = ai_helper.suggest_priority(title, str(due_date), description) if title else "Medium"
    priority = st.selectbox("Priority", ["Low", "Medium", "High"],
                             index=["Low", "Medium", "High"].index(suggested))
    st.caption(f"💡 Suggested priority: **{suggested}**")

    submitted = st.form_submit_button("Add Task")
    if submitted:
        if title.strip():
            db.add_task(title, description, priority, str(due_date))
            st.sidebar.success("Task added!")
            st.rerun()
        else:
            st.sidebar.error("Title is required.")

# ---------- Notifications ----------
tasks = db.get_all_tasks()
today = date.today()

overdue, due_today = [], []
for t in tasks:
    if t["status"] != "Done" and t["due_date"]:
        d = datetime.strptime(t["due_date"], "%Y-%m-%d").date()
        if d < today:
            overdue.append(t)
        elif d == today:
            due_today.append(t)

if overdue:
    st.error(f"⏰ {len(overdue)} task(s) overdue: " + ", ".join(t["title"] for t in overdue))
if due_today:
    st.warning(f"📌 {len(due_today)} task(s) due today: " + ", ".join(t["title"] for t in due_today))

st.divider()

# ---------- Kanban Board ----------
st.subheader("📋 Kanban Board")

col1, col2, col3 = st.columns(3)
status_columns = {"To Do": col1, "In Progress": col2, "Done": col3}

priority_color = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}

for status, col in status_columns.items():
    with col:
        st.markdown(f"### {status}")
        status_tasks = [t for t in tasks if t["status"] == status]
        for t in status_tasks:
            with st.container(border=True):
                st.markdown(f"**{priority_color.get(t['priority'], '')} {t['title']}**")
                if t["description"]:
                    st.caption(t["description"])
                st.caption(f"Due: {t['due_date'] or '—'}")

                # Move between columns
                move_options = [s for s in ["To Do", "In Progress", "Done"] if s != status]
                new_status = st.selectbox(
                    "Move to", move_options, key=f"move_{t['id']}", label_visibility="collapsed"
                )
                c1, c2, c3 = st.columns(3)
                if c1.button("Move", key=f"btn_move_{t['id']}"):
                    db.update_status(t["id"], new_status)
                    st.rerun()
                if c2.button("Breakdown", key=f"btn_ai_{t['id']}"):
                    st.session_state[f"breakdown_{t['id']}"] = ai_helper.suggest_breakdown(
                        t["title"], t["description"] or ""
                    )
                if c3.button("Delete", key=f"btn_del_{t['id']}"):
                    db.delete_task(t["id"])
                    st.rerun()

                # Bonus: show AI-generated breakdown if requested
                if f"breakdown_{t['id']}" in st.session_state:
                    st.markdown("**AI Suggested Steps:**")
                    for step in st.session_state[f"breakdown_{t['id']}"]:
                        st.checkbox(step, key=f"{t['id']}_{step}")
