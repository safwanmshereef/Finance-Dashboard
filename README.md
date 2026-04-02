# Finance Data Processing and Access Control Demo

A full-stack internship assignment demo built with a decoupled architecture:
- Backend API: FastAPI + SQLAlchemy + SQLite + JWT auth
- Frontend dashboard: Streamlit + requests + pandas
- Free deployment targets: Render (backend) + Streamlit Community Cloud (frontend)

## What this demonstrates

- User management with roles (`viewer`, `analyst`, `admin`) and status (`active`, `inactive`)
- Role-based access control across API endpoints
- Financial records CRUD with validation and filtering
- Dashboard summary APIs for aggregates and trends
- Clean error handling and HTTP status usage
- Data persistence with SQLite

## Project structure

```text
backend/
  main.py
  database.py
  models.py
  schemas.py
  security.py
  seed.py
  requirements.txt
  routers/
    auth.py
    users.py
    records.py
    dashboard.py
frontend/
  app.py
  requirements.txt
LICENSE
README.md
```

## Demo test accounts

After running the seed script:

- `admin@example.com` / `password123`
- `analyst@example.com` / `password123`
- `viewer@example.com` / `password123`

## Local setup

### 1) Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
python seed.py
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`
Swagger docs: `http://localhost:8000/docs`

### 2) Frontend

Open a new terminal:

```bash
cd frontend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Frontend runs at `http://localhost:8501`

### 3) Configure frontend API URL via secrets or environment

The frontend reads API URL in this order:
- `st.secrets["API_URL"]`
- `API_URL` environment variable
- fallback: `http://localhost:8000`

Local options:

1. PowerShell environment variable:

```powershell
$env:API_URL = "http://localhost:8000"
streamlit run app.py
```

2. Streamlit secrets file (`frontend/.streamlit/secrets.toml`):

```toml
API_URL = "http://localhost:8000"
```

## Automated tests

```bash
cd backend
pip install -r requirements.txt
pytest -q
```

Test coverage includes:
- register and login flow
- role-based records permissions
- dashboard summary aggregates

## API overview

### Auth
- `POST /auth/register` - register a user
- `POST /auth/login` - login via form fields (`username` = email, `password`)

### Users (admin only)
- `GET /users` - list users
- `POST /users` - create users
- `PATCH /users/{user_id}` - update role/status

### Records
- `POST /records` - create record (admin)
- `GET /records` - list records with filters (analyst/admin)
- `GET /records/{record_id}` - get one record (analyst/admin)
- `PUT /records/{record_id}` - update record (admin)
- `DELETE /records/{record_id}` - delete record (admin)

Filters supported in `GET /records`:
- `category`
- `type` (`income` or `expense`)
- `start_date` and `end_date`
- pagination via `skip` and `limit`

### Dashboard
- `GET /dashboard/summary` - totals, category splits, recent records, monthly trends (all active roles)

## Access control matrix

- Viewer: dashboard summary only
- Analyst: dashboard summary + record read APIs
- Admin: full access (users + records CRUD + dashboard)

## Assumptions and tradeoffs

- SQLite is used for simplicity and quick local testing.
- Register endpoint allows role selection for demo speed. In production, role assignment should be admin-controlled only.
- Single SQLite file (`backend/finance.db`) is enough for assignment/demo scope.

## Free deployment guide

### 1) Deploy backend to Render

1. Push this repository to GitHub.
2. In Render: **New Web Service** -> connect repository.
3. Configure:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
  - Environment variable: `SECRET_KEY` (set a long random value)
  - Environment variable: `DATABASE_URL=sqlite:////var/data/finance.db`
4. Add a **Persistent Disk** and mount path `/var/data`.
5. Deploy.
6. Visit `https://<your-render-url>/docs` for API docs.

Optional: run seed once in Render shell:

```bash
python seed.py
```

### 2) Configure frontend to use deployed backend

In Streamlit Community Cloud app settings, add this secret:

```toml
API_URL = "https://<your-render-url>"
```

No code edit is required.

### 3) Deploy frontend to Streamlit Community Cloud

1. Go to `https://share.streamlit.io`
2. New app -> select your repo
3. Main file path: `frontend/app.py`
4. Deploy

Your live demo will be: `https://<your-streamlit-app>.streamlit.app`

## Evaluation checklist mapping

- Backend design: split routers/auth/models/schemas/database
- Logical thinking: explicit role guards and endpoint permissions
- Functionality: CRUD + filters + summary analytics + trends
- Code quality: typed schemas, modular files, clear naming
- Data modeling: user and financial record relationships
- Validation/reliability: pydantic constraints + structured HTTP errors
- Documentation: setup, API map, deployment, assumptions

## Future enhancements

- Add refresh tokens and password reset
- Add record-level audit logs
- Add soft delete and search index
