# Finance Data Processing and Access Control Demo

A full-stack internship assignment demo built with a decoupled architecture:
- Backend API: FastAPI + SQLAlchemy + Postgres/SQLite + JWT auth
- Frontend dashboard: Streamlit + requests + pandas
- Free deployment targets: Render (backend) + Streamlit Community Cloud (frontend)

## What this demonstrates

- User management with roles (`viewer`, `analyst`, `admin`) and status (`active`, `inactive`)
- Role-based access control across API endpoints
- Financial records CRUD with validation and filtering
- Dashboard summary APIs for aggregates and trends
- Clean error handling and HTTP status usage
- Data persistence with SQLite locally or Postgres in production

## Newly added product features

1. Date-range analytics controls on dashboard summary and trends
2. Monthly budget tracker in the sidebar with utilization indicator
3. Search-enabled records explorer using `q` across category and notes
4. Quick insight cards for filtered records with count and totals
5. One-click CSV export for the filtered records table

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
  .env
  routers/
    auth.py
    users.py
    records.py
    dashboard.py
frontend/
  app.py
  requirements.txt
  .env
LICENSE
README.md
```

## Demo test accounts

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

### 3) Local `.env` files

These are already added in the repo for local development:

Backend `[backend/.env](backend/.env)`
```env
DATABASE_URL=sqlite:///./finance.db
SECRET_KEY=7f2c9e31d5b84a2e8c6f0b1a4d9e3c7f2a5b8e1c4d7f0a3b6e9c2d5f8a1b4c7
```

Frontend `[frontend/.env](frontend/.env)`
```env
API_URL=http://localhost:8000
```

The app loads these automatically with `python-dotenv`.

Optional: if you want local Postgres instead of SQLite, change `backend/.env` to:

```env
DATABASE_URL=postgresql://your_user:your_password@your_host:5432/your_db?sslmode=require
SECRET_KEY=7f2c9e31d5b84a2e8c6f0b1a4d9e3c7f2a5b8e1c4d7f0a3b6e9c2d5f8a1b4c7
```

Then run `python seed.py` again so the database is populated.

### 4) Tests

```bash
cd backend
pip install -r requirements.txt
pytest -q
```

Test coverage includes:
- register and login flow
- role-based records permissions
- dashboard summary aggregates
- record and summary filter compatibility

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
- `q` (search text on category/notes)
- `type` (`income` or `expense`)
- `start_date` and `end_date`
- pagination via `skip` and `limit`

### Dashboard
- `GET /dashboard/summary` - totals, category splits, recent records, monthly trends (all active roles)
- Optional query params: `start_date`, `end_date`

## Access control matrix

- Viewer: dashboard summary only
- Analyst: dashboard summary + record read APIs
- Admin: full access (users + records CRUD + dashboard)

## Assumptions and tradeoffs

- SQLite is used for simplicity and quick local testing.
- Register endpoint allows role selection for demo speed. In production, role assignment should be admin-controlled only.
- For free deployment, Render Postgres is recommended instead of a persistent disk.

## Free deployment guide

### 1) Deploy backend to Render

1. Push this repository to GitHub.
2. In Render: **New Web Service** -> connect repository.
3. Configure:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `SECRET_KEY` = `7f2c9e31d5b84a2e8c6f0b1a4d9e3c7f2a5b8e1c4d7f0a3b6e9c2d5f8a1b4c7`
   - `DATABASE_URL` = paste the Render Postgres internal connection string
5. Deploy.
6. Visit `https://<your-render-url>/docs` for API docs.

### 1b) Create the database on Render

1. In Render, create a **New PostgreSQL** database.
2. Copy the **Internal Database URL** from the database settings.
3. Paste that value into the backend web service `DATABASE_URL` environment variable.
4. If Render gives you a `postgres://...` URL, the app will automatically convert it for SQLAlchemy.

Optional: run seed once in Render shell after deploy:

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
