"""
Streamlit UI for the Multi-Agent RAG system.
Run with: streamlit run streamlit_app.py
Requires the FastAPI backend running at http://localhost:8000
"""

import streamlit as st
import requests

API_BASE = "http://localhost:8000"

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent RAG",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global font & background ── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* ── Hide Streamlit default header/footer ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Sidebar styling ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29, #302b63, #24243e);
    padding-top: 1rem;
}
[data-testid="stSidebar"] * {
    color: #e8e8f0 !important;
}
[data-testid="stSidebar"] .stRadio label {
    font-size: 1rem;
    padding: 0.4rem 0;
}

/* ── Auth page card ── */
.auth-card {
    background: white;
    border-radius: 16px;
    padding: 2.5rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.10);
    max-width: 440px;
    margin: 3rem auto;
}
.auth-title {
    font-size: 2rem;
    font-weight: 700;
    color: #302b63;
    text-align: center;
    margin-bottom: 0.25rem;
}
.auth-subtitle {
    text-align: center;
    color: #888;
    margin-bottom: 1.5rem;
    font-size: 0.95rem;
}

/* ── Agent badge ── */
.badge-rag {
    display: inline-block;
    background: #e8f4fd;
    color: #1a73e8;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-top: 4px;
}
.badge-tool {
    display: inline-block;
    background: #fef3e8;
    color: #e67e22;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-top: 4px;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #f8f9ff;
    border-radius: 12px;
    padding: 1rem;
    border: 1px solid #e8eaf6;
}

/* ── Todo card ── */
.todo-card {
    background: #fff;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    border: 1px solid #e8eaf6;
    margin-bottom: 0.5rem;
}
.todo-done {
    background: #f7fdf7;
    border: 1px solid #d4edda;
}

/* ── Primary button override ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #302b63, #6c63ff);
    border: none;
    border-radius: 8px;
    color: white;
    font-weight: 600;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #24243e, #5a52e0);
}

/* ── Page title ── */
.page-header {
    font-size: 1.8rem;
    font-weight: 700;
    color: #302b63;
    margin-bottom: 0.25rem;
}
.page-sub {
    color: #888;
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ─────────────────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── API helpers ────────────────────────────────────────────────────────────────

def auth_headers() -> dict:
    return {"Authorization": f"Bearer {st.session_state.token}"}


def api_post(path, json=None, data=None, headers=None, auth=True):
    h = auth_headers() if auth else {}
    if headers:
        h.update(headers)
    try:
        return requests.post(f"{API_BASE}{path}", json=json, data=data, headers=h, timeout=60)
    except requests.exceptions.ConnectionError:
        return None


def api_get(path):
    try:
        return requests.get(f"{API_BASE}{path}", headers=auth_headers(), timeout=30)
    except requests.exceptions.ConnectionError:
        return None


def api_put(path, json=None):
    try:
        return requests.put(f"{API_BASE}{path}", json=json, headers=auth_headers(), timeout=30)
    except requests.exceptions.ConnectionError:
        return None


def api_delete(path):
    try:
        return requests.delete(f"{API_BASE}{path}", headers=auth_headers(), timeout=30)
    except requests.exceptions.ConnectionError:
        return None


def handle_401():
    st.error("Session expired. Please log in again.")
    st.session_state.token = None
    st.rerun()


def connection_error():
    st.error("Cannot reach the backend at **http://localhost:8000**. Make sure FastAPI is running.")


# ── Auth page ──────────────────────────────────────────────────────────────────

def page_auth():
    col_l, col_c, col_r = st.columns([1, 1.4, 1])
    with col_c:
        st.markdown("""
        <div style='text-align:center; margin-top: 2rem; margin-bottom: 1.5rem;'>
            <div style='font-size:3.5rem;'>🤖</div>
            <div style='font-size:1.9rem; font-weight:800; color:#302b63;'>Multi-Agent RAG</div>
            <div style='color:#888; margin-top:0.3rem;'>Powered by GPT-4.1-mini · LangGraph · ChromaDB</div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔑  Sign In", "✨  Create Account"])

        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

            if submitted:
                if not username or not password:
                    st.error("Please fill in both fields.")
                else:
                    with st.spinner("Signing in…"):
                        resp = api_post(
                            "/auth/token",
                            data={"username": username, "password": password},
                            headers={"Content-Type": "application/x-www-form-urlencoded"},
                            auth=False,
                        )
                    if resp is None:
                        connection_error()
                    elif resp.status_code == 200:
                        st.session_state.token = resp.json()["access_token"]
                        st.session_state.username = username
                        st.rerun()
                    elif resp.status_code == 401:
                        st.error("Invalid username or password.")
                    else:
                        st.error(f"Login failed ({resp.status_code}).")

        with tab_register:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("register_form"):
                new_username = st.text_input("Username", placeholder="Choose a username", key="reg_user")
                new_email    = st.text_input("Email", placeholder="your@email.com", key="reg_email")
                new_password = st.text_input("Password", type="password", placeholder="Create a password", key="reg_pass")
                new_password2= st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="reg_pass2")
                submitted_reg = st.form_submit_button("Create Account", use_container_width=True, type="primary")

            if submitted_reg:
                if not all([new_username, new_email, new_password, new_password2]):
                    st.error("Please fill in all fields.")
                elif new_password != new_password2:
                    st.error("Passwords do not match.")
                else:
                    with st.spinner("Creating account…"):
                        resp = api_post(
                            "/auth/register",
                            json={"username": new_username, "email": new_email, "password": new_password},
                            auth=False,
                        )
                    if resp is None:
                        connection_error()
                    elif resp.status_code in (200, 201):
                        st.success("Account created! Switch to Sign In to continue.")
                    elif resp.status_code == 400:
                        st.error("Username or email already taken.")
                    else:
                        st.error(f"Registration failed ({resp.status_code}).")


# ── Chat page ──────────────────────────────────────────────────────────────────

def page_chat():
    st.markdown('<div class="page-header">💬 Chat</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Ask about FAQs — or request weather & todo actions. The system routes automatically.</div>', unsafe_allow_html=True)

    # Chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.write(msg["content"])
                agent = msg.get("agent", "")
                if agent == "rag":
                    st.markdown('<span class="badge-rag">🔍 RAG Agent</span>', unsafe_allow_html=True)
                elif agent == "tool":
                    st.markdown('<span class="badge-tool">🛠️ Tool Agent</span>', unsafe_allow_html=True)

    query = st.chat_input("Ask anything…")
    if query:
        st.session_state.chat_history.append({"role": "user", "content": query, "agent": None})
        with st.chat_message("user"):
            st.write(query)

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                resp = api_post("/chat", json={"query": query})

            if resp is None:
                connection_error()
                st.session_state.chat_history.append({"role": "assistant", "content": "Backend unreachable.", "agent": None})
            elif resp.status_code == 200:
                data = resp.json()
                answer = data["answer"]
                agent_used = data.get("agent_used", "")
                st.write(answer)
                if agent_used == "rag":
                    st.markdown('<span class="badge-rag">🔍 RAG Agent</span>', unsafe_allow_html=True)
                elif agent_used == "tool":
                    st.markdown('<span class="badge-tool">🛠️ Tool Agent</span>', unsafe_allow_html=True)
                st.session_state.chat_history.append({"role": "assistant", "content": answer, "agent": agent_used})
            elif resp.status_code == 401:
                handle_401()
            else:
                err = f"Error {resp.status_code}: {resp.text}"
                st.error(err)
                st.session_state.chat_history.append({"role": "assistant", "content": err, "agent": None})

    if st.session_state.chat_history:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear conversation", use_container_width=False):
            st.session_state.chat_history = []
            st.rerun()


# ── Weather page ───────────────────────────────────────────────────────────────

def page_weather():
    st.markdown('<div class="page-header">🌤️ Weather</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Live weather via wttr.in — no API key required.</div>', unsafe_allow_html=True)

    CITIES = [
        "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
        "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat",
        "Lucknow", "Kochi", "Chandigarh", "Bhopal", "Indore",
        "Nagpur", "Visakhapatnam", "Coimbatore", "Guwahati", "Mysuru",
    ]

    col_select, _ = st.columns([2, 2])
    with col_select:
        city = st.selectbox("Select a city", CITIES, index=0)

    st.markdown(f"<br>", unsafe_allow_html=True)

    if st.button(f"Get Weather for **{city}**", type="primary"):
        with st.spinner(f"Fetching weather for {city}…"):
            resp = api_get(f"/weather?city={city}")

        if resp is None:
            connection_error()
        elif resp.status_code == 200:
            w = resp.json()
            st.markdown(f"### 📍 {w['city']}")
            st.markdown(f"**{w['description']}**")
            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("🌡️ Temperature", f"{w['temperature_c']} °C")
            c2.metric("💧 Humidity", f"{w['humidity']}%")
            c3.metric("💨 Wind Speed", f"{w['wind_kmh']} km/h")
        elif resp.status_code == 401:
            handle_401()
        elif resp.status_code == 502:
            st.error(f"Could not fetch weather for **{city}**. Try a different city name.")
        else:
            st.error(f"Error {resp.status_code}: {resp.text}")


# ── Todos page ─────────────────────────────────────────────────────────────────

def page_todos():
    st.markdown('<div class="page-header">✅ Todo Manager</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Create, complete, and manage your tasks.</div>', unsafe_allow_html=True)

    # Add task form
    with st.expander("➕  Add new task", expanded=False):
        with st.form("add_todo", clear_on_submit=True):
            title       = st.text_input("Task title", placeholder="What needs to be done?")
            description = st.text_area("Description (optional)", height=80, placeholder="Add details…")
            add_btn     = st.form_submit_button("Add Task", use_container_width=True, type="primary")

        if add_btn:
            if not title.strip():
                st.error("Title cannot be empty.")
            else:
                resp = api_post("/todos", json={"title": title.strip(), "description": description.strip()})
                if resp is None:
                    connection_error()
                elif resp.status_code in (200, 201):
                    st.success("Task added!")
                    st.rerun()
                elif resp.status_code == 401:
                    handle_401()
                else:
                    st.error(f"Failed: {resp.text}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Load todos
    resp = api_get("/todos")
    if resp is None:
        connection_error()
        return
    if resp.status_code == 401:
        handle_401()
        return
    if resp.status_code != 200:
        st.error(f"Failed to load tasks: {resp.text}")
        return

    todos   = resp.json()
    pending = [t for t in todos if not t["completed"]]
    done    = [t for t in todos if t["completed"]]

    def render_section(task_list, label, icon):
        if not task_list:
            return
        st.markdown(f"#### {icon} {label} &nbsp; `{len(task_list)}`", unsafe_allow_html=True)
        for todo in task_list:
            card_class = "todo-done" if todo["completed"] else "todo-card"
            with st.container():
                col_chk, col_info, col_actions = st.columns([0.4, 5.5, 2.1])

                with col_chk:
                    new_done = st.checkbox(
                        "done",
                        value=todo["completed"],
                        key=f"chk_{todo['id']}",
                        label_visibility="collapsed",
                    )
                    if new_done != todo["completed"]:
                        r = api_put(f"/todos/{todo['id']}", json={"completed": new_done})
                        if r and r.status_code == 200:
                            st.rerun()

                with col_info:
                    if todo["completed"]:
                        st.markdown(f"~~{todo['title']}~~")
                    else:
                        st.markdown(f"**{todo['title']}**")
                    if todo.get("description"):
                        st.caption(todo["description"])

                with col_actions:
                    btn_edit, btn_del = st.columns(2)
                    if btn_edit.button("✏️", key=f"edit_{todo['id']}", use_container_width=True, help="Edit task"):
                        st.session_state[f"editing_{todo['id']}"] = True
                    if btn_del.button("🗑️", key=f"del_{todo['id']}", use_container_width=True, help="Delete task"):
                        r = api_delete(f"/todos/{todo['id']}")
                        if r and r.status_code in (200, 204):
                            st.rerun()
                        else:
                            st.error("Delete failed.")

                st.markdown("<hr style='margin:4px 0; border-color:#f0f0f0;'>", unsafe_allow_html=True)

            # Inline edit form
            if st.session_state.get(f"editing_{todo['id']}"):
                with st.form(key=f"edit_form_{todo['id']}"):
                    upd_title = st.text_input("Title", value=todo["title"])
                    upd_desc  = st.text_area("Description", value=todo.get("description", ""), height=70)
                    s_col, c_col = st.columns(2)
                    save_btn   = s_col.form_submit_button("Save", use_container_width=True, type="primary")
                    cancel_btn = c_col.form_submit_button("Cancel", use_container_width=True)

                if save_btn:
                    r = api_put(f"/todos/{todo['id']}", json={"title": upd_title, "description": upd_desc})
                    if r and r.status_code == 200:
                        del st.session_state[f"editing_{todo['id']}"]
                        st.rerun()
                    else:
                        st.error("Update failed.")
                if cancel_btn:
                    del st.session_state[f"editing_{todo['id']}"]
                    st.rerun()

    if not todos:
        st.info("No tasks yet. Add your first task above!")
        return

    render_section(pending, "Pending", "🔵")
    if done:
        st.markdown("<br>", unsafe_allow_html=True)
        render_section(done, "Completed", "✅")


# ── Sidebar ────────────────────────────────────────────────────────────────────

def sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding: 1rem 0 0.5rem;'>
            <div style='font-size:2.4rem;'>🤖</div>
            <div style='font-size:1.1rem; font-weight:700; letter-spacing:0.5px;'>Multi-Agent RAG</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        if not st.session_state.token:
            st.markdown("""
            <div style='text-align:center; color:#aaa; font-size:0.85rem; padding: 0.5rem 0;'>
                Sign in to get started
            </div>
            """, unsafe_allow_html=True)
            return None

        # User info
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.08); border-radius:10px;
                    padding:0.7rem 1rem; margin-bottom:1rem;'>
            <div style='font-size:0.75rem; color:#aaa;'>Signed in as</div>
            <div style='font-size:1rem; font-weight:600;'>👤 {st.session_state.username}</div>
        </div>
        """, unsafe_allow_html=True)

        page = st.radio(
            "Navigate",
            ["💬 Chat", "🌤️ Weather", "✅ Todos"],
            label_visibility="collapsed",
        )

        st.divider()

        if st.button("Sign Out", use_container_width=True):
            st.session_state.token = None
            st.session_state.username = None
            st.session_state.chat_history = []
            st.rerun()

        # Subtle system info at bottom
        st.markdown("""
        <div style='position:fixed; bottom:1rem; font-size:0.72rem; color:#666; line-height:1.8;'>
            Model &nbsp;·&nbsp; gpt-4.1-mini<br>
            Embeddings &nbsp;·&nbsp; MiniLM-L6<br>
            Vector DB &nbsp;·&nbsp; ChromaDB
        </div>
        """, unsafe_allow_html=True)

    return page


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    page = sidebar()

    if not st.session_state.token:
        page_auth()
        return

    if page == "💬 Chat":
        page_chat()
    elif page == "🌤️ Weather":
        page_weather()
    elif page == "✅ Todos":
        page_todos()


if __name__ == "__main__":
    main()