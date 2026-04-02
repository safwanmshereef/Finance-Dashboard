from datetime import date
import os

import pandas as pd
import requests
import streamlit as st

# Priority: Streamlit secrets -> environment variable -> localhost for local dev.
API_URL = str(st.secrets.get("API_URL", os.getenv("API_URL", "http://localhost:8000"))).rstrip("/")
TIMEOUT_SECONDS = 15

st.set_page_config(page_title="Finance Dashboard Demo", page_icon="💼", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Manrope', sans-serif;
    }
    .stApp {
        background: radial-gradient(circle at top right, #f8fde6 0%, #e8f3ff 45%, #f6f8fa 100%);
    }
    .block-container {
        padding-top: 1.2rem;
    }
    .title-card {
        background: linear-gradient(120deg, #0b3d2e, #247a5f);
        border-radius: 18px;
        padding: 1.2rem 1.4rem;
        color: #ffffff;
        margin-bottom: 1rem;
        box-shadow: 0 10px 26px rgba(11, 61, 46, 0.25);
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


def render_login_sidebar():
    st.sidebar.header("Access")

    if st.session_state.token:
        st.sidebar.success(f"Signed in as {st.session_state.email} ({st.session_state.role})")
        if st.sidebar.button("Logout"):
            st.session_state.token = None
            st.session_state.role = None
            st.session_state.email = None
            st.rerun()
        return

    with st.sidebar.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        payload = {
            "username": email,
            "password": password,
        }
        data, error = api_request("POST", "/auth/login", data=payload)
        if error or data is None:
            st.sidebar.error(f"Login failed: {error}")
            return

        st.session_state.token = data["access_token"]
        st.session_state.role = data["role"]
        st.session_state.email = data["email"]
        st.sidebar.success("Login successful")
        st.rerun()


def render_dashboard():
    summary, error = api_request("GET", "/dashboard/summary", headers=auth_headers())
    if error or summary is None:
        st.error(f"Failed to load dashboard: {error}")
        return

    st.markdown(
        """
        <div class="title-card">
            <h2 style="margin: 0;">Finance Command Center</h2>
            <p style="margin: 6px 0 0 0; opacity: 0.9;">Real-time summary, trends, and category performance.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"${summary['total_income']:,.2f}")
    col2.metric("Total Expenses", f"${summary['total_expenses']:,.2f}")
    col3.metric("Net Balance", f"${summary['net_balance']:,.2f}")

    charts_col1, charts_col2 = st.columns(2)

    income_df = pd.DataFrame(summary["by_category_income"])
    if not income_df.empty:
        income_df = income_df.set_index("category")
        charts_col1.subheader("Income by Category")
        charts_col1.bar_chart(income_df["total"])

    expense_df = pd.DataFrame(summary["by_category_expense"])
    if not expense_df.empty:
        expense_df = expense_df.set_index("category")
        charts_col2.subheader("Expense by Category")
        charts_col2.bar_chart(expense_df["total"])

    trends_df = pd.DataFrame(summary["monthly_trends"])
    if not trends_df.empty:
        st.subheader("Monthly Trends")
        st.line_chart(trends_df.set_index("month")[["income", "expenses"]])

    recent_df = pd.DataFrame(summary["recent_records"])
    st.subheader("Recent Activity")
    if recent_df.empty:
        st.info("No records yet.")
    else:
        st.dataframe(recent_df, use_container_width=True)


def render_records_view():
    st.subheader("Financial Records")

    filter_col1, filter_col2, filter_col3 = st.columns(3)
    category = filter_col1.text_input("Category contains")
    record_type = filter_col2.selectbox("Type", ["", "income", "expense"])
    use_start_date = filter_col3.checkbox("Filter from date")
    start_date = filter_col3.date_input("Start date", value=date.today(), disabled=not use_start_date)

    params = {}
    if category:
        params["category"] = category
    if record_type:
        params["type"] = record_type
    if use_start_date and isinstance(start_date, date):
        params["start_date"] = start_date.isoformat()

    records, error = api_request("GET", "/records", headers=auth_headers(), params=params)
    if error or records is None:
        st.error(f"Could not load records: {error}")
        return

    records_df = pd.DataFrame(records)
    if records_df.empty:
        st.info("No records found.")
    else:
        st.dataframe(records_df, use_container_width=True)


def render_add_record():
    st.subheader("Add Record (Admin)")
    with st.form("add_record"):
        amount = st.number_input("Amount", min_value=0.01, step=10.0)
        record_type = st.selectbox("Type", ["income", "expense"])
        category = st.text_input("Category")
        record_date = st.date_input("Date", value=date.today())
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
        _, error = api_request("POST", "/records", headers=auth_headers(), json=payload)
        if error:
            st.error(f"Create failed: {error}")
        else:
            st.success("Record created successfully")


def render_admin_users():
    st.subheader("User Management (Admin)")
    users, error = api_request("GET", "/users", headers=auth_headers())
    if error or users is None:
        st.error(f"Could not load users: {error}")
        return

    st.dataframe(pd.DataFrame(users), use_container_width=True)


render_login_sidebar()

st.title("Finance Dashboard Demo")
st.caption("Internship assignment: data processing, access control, and dashboard analytics")

if not st.session_state.token:
    st.info("Use demo accounts after backend seeding: admin@example.com / analyst@example.com / viewer@example.com")
    st.stop()

base_views = ["Dashboard"]
if st.session_state.role in {"analyst", "admin"}:
    base_views.append("View Records")
if st.session_state.role == "admin":
    base_views.extend(["Add Record", "Manage Users"])

selected = st.sidebar.selectbox("Navigate", base_views)

if selected == "Dashboard":
    render_dashboard()
elif selected == "View Records":
    render_records_view()
elif selected == "Add Record":
    render_add_record()
else:
    render_admin_users()
