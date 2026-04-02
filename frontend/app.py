from datetime import date
import io
import os

import pandas as pd
import requests
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError
from dotenv import load_dotenv

load_dotenv()


def resolve_api_url() -> str:
    env_api_url = os.getenv("API_URL")
    if env_api_url:
        return env_api_url.rstrip("/")

    try:
        return str(st.secrets["API_URL"]).rstrip("/")
    except (KeyError, StreamlitSecretNotFoundError):
        return "http://localhost:8000"


API_URL = resolve_api_url()
TIMEOUT_SECONDS = 15

st.set_page_config(page_title="Finance Dashboard Demo",
                   page_icon="\U0001f4bc", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Manrope:wght@600;700;800&display=swap');
    :root {
        --ink: #0f172a;
        --muted: #334155;
        --bg-a: #f8fafc;
        --bg-b: #e0f2fe;
        --card: #ffffff;
        --border: #cbd5e1;
        --brand-a: #0b3b7a;
        --brand-b: #0ea5a8;
        --accent: #fb923c;
    }
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        color: var(--ink);
    }
    .stApp {
        background:
          radial-gradient(circle at 10% 0%, rgba(14, 165, 168, 0.20), transparent 32%),
          radial-gradient(circle at 92% 6%, rgba(251, 146, 60, 0.18), transparent 30%),
          linear-gradient(180deg, var(--bg-a) 0%, var(--bg-b) 100%);
        color: var(--ink);
    }
    .stApp, .main, section[data-testid="stMain"], section[data-testid="stSidebar"] {
        color: var(--ink);
    }
    .block-container {
        max-width: 1180px;
        padding-top: 1.2rem;
    }
    .hero {
        border-radius: 22px;
        padding: 1.3rem 1.4rem;
        background: linear-gradient(130deg, var(--brand-a), var(--brand-b));
        color: #fff;
        box-shadow: 0 16px 32px rgba(15, 23, 42, 0.22);
        margin-bottom: 1rem;
    }
    .hero h1 {
        margin: 0;
        font-family: 'Manrope', sans-serif;
        font-size: clamp(1.4rem, 2.4vw, 2rem);
    }
    .hero p {
        margin: 0.45rem 0 0;
        color: rgba(255, 255, 255, 0.92);
    }
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.7rem;
        margin-bottom: 0.9rem;
    }
    .kpi {
        background: rgba(255,255,255,0.96);
        border: 1px solid rgba(15,23,42,0.08);
        border-radius: 14px;
        padding: 0.82rem 0.9rem;
        box-shadow: 0 8px 20px rgba(15,23,42,0.08);
    }
    .kpi .label {
        color: var(--muted);
        font-size: 0.82rem;
        margin-bottom: 0.12rem;
    }
    .kpi .value {
        color: var(--ink);
        font-family: 'Manrope', sans-serif;
        font-size: 1.25rem;
        font-weight: 800;
    }
    .panel {
        background: rgba(255,255,255,0.95);
        border: 1px solid rgba(15,23,42,0.08);
        border-radius: 16px;
        padding: 0.55rem 0.9rem 0.8rem;
        box-shadow: 0 10px 22px rgba(15,23,42,0.08);
        margin-bottom: 0.85rem;
    }
    .auth-note {
        background: linear-gradient(120deg, rgba(11,59,122,0.10), rgba(251,146,60,0.16));
        border: 1px solid rgba(15,23,42,0.12);
        border-radius: 12px;
        padding: 0.72rem 0.82rem;
        color: var(--ink);
        margin-top: 0.45rem;
    }
    .auth-note code {
        background: rgba(255,255,255,0.86);
        border-radius: 6px;
        padding: 0.08rem 0.34rem;
        color: #0c4a6e;
        font-size: 0.84rem;
    }
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span,
    .stText, .stCaption, .stInfo, .stSuccess, .stWarning, .stError {
        color: var(--ink) !important;
    }
    section.main [data-testid="stWidgetLabel"] p,
    section.main label {
        color: var(--ink) !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    section.main h1,
    section.main h2,
    section.main h3,
    section.main h4,
    section.main h5,
    section.main h6,
    section.main p,
    section.main li,
    section.main span,
    section.main [data-testid="stMarkdownContainer"] p,
    section.main [data-testid="stMarkdownContainer"] li,
    section.main [data-testid="stHeadingWithActionElements"],
    section.main [data-testid="stAlertContainer"] *,
    section.main [data-testid="stMetricValue"],
    section.main [data-testid="stMetricLabel"] {
        color: var(--ink) !important;
        opacity: 1 !important;
    }
    section.main [data-testid="stCaptionContainer"] p {
        color: var(--muted) !important;
        opacity: 1 !important;
    }
    section.main [data-baseweb="input"] input,
    section.main [data-baseweb="select"] > div,
    section.main textarea,
    section.main input[type="number"],
    section.main input[type="date"] {
        color: var(--ink) !important;
        background: #ffffff !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    section.main [data-baseweb="input"] input::placeholder,
    section.main textarea::placeholder {
        color: #64748b !important;
    }
    section.main [data-baseweb="select"] span,
    section.main [data-baseweb="select"] input {
        color: var(--ink) !important;
    }
    section.main button[kind="primary"] {
        border-radius: 10px !important;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b1f40 0%, #132a52 100%);
        border-right: 1px solid rgba(255,255,255,0.18);
    }
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {
        color: #f1f5f9 !important;
        opacity: 1 !important;
    }
    section[data-testid="stSidebar"] [data-baseweb="input"] input,
    section[data-testid="stSidebar"] [data-baseweb="select"] > div {
        color: #f8fafc !important;
        background: rgba(15,23,42,0.75) !important;
        border: 1px solid rgba(148,163,184,0.45) !important;
    }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
    section[data-testid="stSidebar"] [data-testid="stHeadingWithActionElements"] {
        color: #f1f5f9 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stAlertContainer"] *,
    section[data-testid="stSidebar"] [data-testid="stMetricValue"],
    section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: #f1f5f9 !important;
    }
    @media (max-width: 980px) {
        .kpi-grid {
            grid-template-columns: 1fr 1fr;
        }
    }
    @media (max-width: 640px) {
        .kpi-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "email" not in st.session_state:
    st.session_state.email = None
if "monthly_budget" not in st.session_state:
    st.session_state.monthly_budget = 3000.0


def auth_headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def api_request(method: str, path: str, **kwargs):
    try:
        response = requests.request(
            method,
            f"{API_URL}{path}",
            timeout=TIMEOUT_SECONDS,
            **kwargs,
        )
        if response.status_code >= 400:
            detail = response.text
            try:
                detail = response.json().get("detail", detail)
            except ValueError:
                pass
            return None, f"{response.status_code}: {detail}"
        if not response.text:
            return {}, None
        return response.json(), None
    except requests.RequestException as exc:
        return None, str(exc)


def render_sidebar_auth_and_controls():
    st.sidebar.markdown("## Access")
    st.sidebar.caption("Sign in to unlock role-based views.")

    if st.session_state.token:
        st.sidebar.success(
            f"Signed in as {st.session_state.email} ({st.session_state.role})"
        )
        if st.sidebar.button("Logout"):
            st.session_state.token = None
            st.session_state.role = None
            st.session_state.email = None
            st.rerun()

        st.sidebar.markdown("---")
        st.sidebar.markdown("### Monthly Budget")
        st.session_state.monthly_budget = st.sidebar.number_input(
            "Set target ($)",
            min_value=0.0,
            step=100.0,
            value=float(st.session_state.monthly_budget),
        )
        return

    with st.sidebar.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        data, error = api_request(
            "POST",
            "/auth/login",
            data={"username": email, "password": password},
        )
        if error or data is None:
            if error and error.startswith("401:"):
                st.sidebar.error(
                    "Login failed: check the demo credentials or seed the database on the deployed backend.")
            else:
                st.sidebar.error(f"Login failed: {error}")
            return

        st.session_state.token = data["access_token"]
        st.session_state.role = data["role"]
        st.session_state.email = data["email"]
        st.sidebar.success("Login successful")
        st.rerun()


def render_logged_out_message():
    st.markdown(
        """
        <div class="hero">
            <h1>Finance Dashboard Demo</h1>
            <p>Secure financial analytics with role-based access, records governance, and executive-ready insights.</p>
        </div>
        <div class="auth-note">
            <div><strong>Demo Login Accounts</strong></div>
            <div>Admin: <code>admin@example.com</code> / <code>password123</code></div>
            <div>Analyst: <code>analyst@example.com</code> / <code>password123</code></div>
            <div>Viewer: <code>viewer@example.com</code> / <code>password123</code></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_money(value: float) -> str:
    return f"${value:,.2f}"


def render_dashboard():
    st.markdown(
        """
        <div class="hero">
            <h1>Executive Dashboard</h1>
            <p>Track profitability, budget health, and financial momentum in one screen.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 2])
    use_start_date = filter_col1.checkbox("Use start date", value=False)
    start_date = filter_col1.date_input(
        "From date", value=date.today(), disabled=not use_start_date)
    use_end_date = filter_col2.checkbox("Use end date", value=False)
    end_date = filter_col2.date_input(
        "To date", value=date.today(), disabled=not use_end_date)
    filter_col3.caption(
        "Feature 1: Date-range analytics for summary and trends")

    params = {}
    if use_start_date and isinstance(start_date, date):
        params["start_date"] = start_date.isoformat()
    if use_end_date and isinstance(end_date, date):
        params["end_date"] = end_date.isoformat()

    summary, error = api_request(
        "GET", "/dashboard/summary", headers=auth_headers(), params=params)
    if error or summary is None:
        st.error(f"Failed to load dashboard: {error}")
        return

    total_income = float(summary["total_income"])
    total_expenses = float(summary["total_expenses"])
    net_balance = float(summary["net_balance"])

    budget = float(st.session_state.monthly_budget)
    budget_ratio = (total_expenses / budget) if budget > 0 else 0
    savings_ratio = ((net_balance / total_income) *
                     100) if total_income > 0 else 0

    top_expense_category = "-"
    if summary["by_category_expense"]:
        top_expense_category = summary["by_category_expense"][0]["category"]

    st.markdown(
        f"""
        <div class="kpi-grid">
            <div class="kpi"><div class="label">Total Income</div><div class="value">{format_money(total_income)}</div></div>
            <div class="kpi"><div class="label">Total Expenses</div><div class="value">{format_money(total_expenses)}</div></div>
            <div class="kpi"><div class="label">Net Balance</div><div class="value">{format_money(net_balance)}</div></div>
            <div class="kpi"><div class="label">Savings Ratio</div><div class="value">{savings_ratio:.1f}%</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Budget Health")
    st.caption("Feature 2: Monthly budget tracker with utilization indicator")
    st.progress(min(max(budget_ratio, 0.0), 1.0) if budget > 0 else 0.0)
    if budget <= 0:
        st.warning("Set a monthly budget in the sidebar to enable tracking.")
    elif total_expenses <= budget:
        st.success(f"Under budget by {format_money(budget - total_expenses)}")
    else:
        st.error(f"Over budget by {format_money(total_expenses - budget)}")
    st.caption(f"Top expense category: {top_expense_category}")
    st.markdown('</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    income_df = pd.DataFrame(summary["by_category_income"])
    if not income_df.empty:
        c1.markdown('<div class="panel">', unsafe_allow_html=True)
        c1.subheader("Income by Category")
        c1.bar_chart(income_df.set_index("category")["total"])
        c1.markdown('</div>', unsafe_allow_html=True)

    expense_df = pd.DataFrame(summary["by_category_expense"])
    if not expense_df.empty:
        c2.markdown('<div class="panel">', unsafe_allow_html=True)
        c2.subheader("Expenses by Category")
        c2.bar_chart(expense_df.set_index("category")["total"])
        c2.markdown('</div>', unsafe_allow_html=True)

    trends_df = pd.DataFrame(summary["monthly_trends"])
    if not trends_df.empty:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("Monthly Trends")
        st.caption("Feature 3: Trendline view for income vs expense")
        st.line_chart(trends_df.set_index("month")[["income", "expenses"]])
        st.markdown('</div>', unsafe_allow_html=True)

    recent_df = pd.DataFrame(summary["recent_records"])
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Recent Activity")
    if recent_df.empty:
        st.info("No records found for selected period.")
    else:
        st.dataframe(recent_df, width="stretch")
    st.markdown('</div>', unsafe_allow_html=True)


def render_records_view():
    st.markdown(
        """
        <div class="hero">
            <h1>Records Explorer</h1>
            <p>Search, filter, and export transaction data for reporting workflows.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    f1, f2, f3, f4 = st.columns(4)
    search_text = f1.text_input("Search (category/notes)")
    record_type = f2.selectbox("Type", ["", "income", "expense"])
    use_start_date = f3.checkbox("Use start", value=False)
    start_date = f3.date_input(
        "From date", value=date.today(), disabled=not use_start_date)
    use_end_date = f4.checkbox("Use end", value=False)
    end_date = f4.date_input(
        "To date", value=date.today(), disabled=not use_end_date)

    params: dict[str, str | int] = {"limit": 200}
    if search_text:
        params["q"] = search_text
    if record_type:
        params["type"] = record_type
    if use_start_date and isinstance(start_date, date):
        params["start_date"] = start_date.isoformat()
    if use_end_date and isinstance(end_date, date):
        params["end_date"] = end_date.isoformat()

    records, error = api_request(
        "GET", "/records", headers=auth_headers(), params=params)
    if error or records is None:
        st.error(f"Could not load records: {error}")
        return

    records_df = pd.DataFrame(records)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Quick Insights")
    st.caption("Feature 4: Search + fast insight cards for filtered records")
    if records_df.empty:
        st.info("No records found for current filters.")
    else:
        income_total = records_df.loc[records_df["type"]
                                      == "income", "amount"].sum()
        expense_total = records_df.loc[records_df["type"]
                                       == "expense", "amount"].sum()
        rec_count = len(records_df)
        stat1, stat2, stat3 = st.columns(3)
        stat1.metric("Filtered Records", rec_count)
        stat2.metric("Income", format_money(float(income_total)))
        stat3.metric("Expenses", format_money(float(expense_total)))
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Records Table")
    if records_df.empty:
        st.info("No records found.")
    else:
        st.dataframe(records_df, width="stretch")

        csv_buffer = io.StringIO()
        records_df.to_csv(csv_buffer, index=False)
        st.download_button(
            "Download filtered CSV",
            data=csv_buffer.getvalue(),
            file_name="filtered_records.csv",
            mime="text/csv",
            width="content",
        )
        st.caption("Feature 5: One-click CSV export for current filtered view")
    st.markdown('</div>', unsafe_allow_html=True)


def render_add_record():
    st.markdown(
        """
        <div class="hero">
            <h1>Add Financial Record</h1>
            <p>Create structured transaction entries for governance and analytics.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("add_record", clear_on_submit=True):
        c1, c2 = st.columns(2)
        amount = c1.number_input("Amount", min_value=0.01, step=10.0)
        record_type = c2.selectbox("Type", ["income", "expense"])
        c3, c4 = st.columns(2)
        category = c3.text_input("Category")
        record_date = c4.date_input("Date", value=date.today())
        notes = st.text_area("Notes")
        submit = st.form_submit_button("Create Record")

    if submit:
        payload = {
            "amount": amount,
            "type": record_type,
            "category": category,
            "date": record_date.isoformat(),
            "notes": notes or None,
        }
        _, error = api_request(
            "POST", "/records", headers=auth_headers(), json=payload)
        if error:
            st.error(f"Create failed: {error}")
        else:
            st.success("Record created successfully")


def render_admin_users():
    st.markdown(
        """
        <div class="hero">
            <h1>User Management</h1>
            <p>Govern user accounts, roles, and access states.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    users, error = api_request("GET", "/users", headers=auth_headers())
    if error or users is None:
        st.error(f"Could not load users: {error}")
        return

    users_df = pd.DataFrame(users)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.dataframe(users_df, width="stretch")
    st.markdown('</div>', unsafe_allow_html=True)


render_sidebar_auth_and_controls()

if not st.session_state.token:
    render_logged_out_message()
    st.stop()

st.markdown(
    """
    <div class="hero">
        <h1>Finance Dashboard Demo</h1>
        <p>Professional full-stack demo with RBAC, analytics, export workflows, and budgeting insights.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

views = ["Dashboard"]
if st.session_state.role in {"analyst", "admin"}:
    views.append("View Records")
if st.session_state.role == "admin":
    views.extend(["Add Record", "Manage Users"])

selected = st.sidebar.selectbox("Navigate", views)

if selected == "Dashboard":
    render_dashboard()
elif selected == "View Records":
    render_records_view()
elif selected == "Add Record":
    render_add_record()
else:
    render_admin_users()
