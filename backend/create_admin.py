"""
Run once after deployment to create your first agency admin login:
    python create_admin.py you@youragency.com yourpassword
"""
import sys

from app.database import SessionLocal, Base, engine
from app.models import User, UserRole
from app.security import hash_password

Base.metadata.create_all(bind=engine)


def main():
    if len(sys.argv) != 3:
        print("Usage: python create_admin.py <email> <password>")
        sys.exit(1)

    email, password = sys.argv[1], sys.argv[2]
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            print("A user with that email already exists.")
            return
        user = User(email=email, hashed_password=hash_password(password), role=UserRole.agency_admin)
        db.add(user)
        db.commit()
        print(f"Created agency admin: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
