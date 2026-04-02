import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routers import auth, dashboard, records, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Finance Data Processing API",
    description="Internship assignment demo backend with role-based access control.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(records.router)
app.include_router(dashboard.router)


@app.on_event("startup")
def maybe_seed_on_startup():
    if os.getenv("SEED_ON_STARTUP", "false").lower() != "true":
        return

    # This is idempotent and safe to run repeatedly for demo environments.
    from seed import seed_users_and_records

    seed_users_and_records()


@app.get("/")
def health_check():
    return {"status": "ok", "service": "finance-backend"}
