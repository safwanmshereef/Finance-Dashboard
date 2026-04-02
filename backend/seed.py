from datetime import date

from database import Base, SessionLocal, engine
from models import FinancialRecord, User
from security import get_password_hash


def seed_users_and_records():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        users = {
            "admin@example.com": "admin",
            "analyst@example.com": "analyst",
            "viewer@example.com": "viewer",
        }

        created_users = {}
        for email, role in users.items():
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    email=email,
                    hashed_password=get_password_hash("password123"),
                    role=role,
                    status="active",
                    is_active=True,
                )
                db.add(user)
                db.flush()
            created_users[email] = user

        if db.query(FinancialRecord).count() == 0:
            sample_records = [
                FinancialRecord(
                    amount=12000,
                    type="income",
                    category="Salary",
                    date=date(2026, 1, 30),
                    notes="Monthly salary",
                    user_id=created_users["admin@example.com"].id,
                ),
                FinancialRecord(
                    amount=3500,
                    type="income",
                    category="Freelance",
                    date=date(2026, 2, 14),
                    notes="Side project payment",
                    user_id=created_users["admin@example.com"].id,
                ),
                FinancialRecord(
                    amount=1800,
                    type="expense",
                    category="Rent",
                    date=date(2026, 2, 1),
                    notes="Apartment rent",
                    user_id=created_users["admin@example.com"].id,
                ),
                FinancialRecord(
                    amount=420,
                    type="expense",
                    category="Utilities",
                    date=date(2026, 2, 7),
                    notes="Electricity and internet",
                    user_id=created_users["admin@example.com"].id,
                ),
                FinancialRecord(
                    amount=700,
                    type="expense",
                    category="Groceries",
                    date=date(2026, 2, 18),
                    notes="Monthly groceries",
                    user_id=created_users["admin@example.com"].id,
                ),
                FinancialRecord(
                    amount=14000,
                    type="income",
                    category="Salary",
                    date=date(2026, 3, 30),
                    notes="Monthly salary",
                    user_id=created_users["admin@example.com"].id,
                ),
            ]
            db.add_all(sample_records)

        db.commit()
        print("Seed completed. Demo users are ready.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_users_and_records()
