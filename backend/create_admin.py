from database import SessionLocal
from models import User, Cart
from auth import hash_password


# ============================================================
# ADMIN DETAILS
# ============================================================

ADMIN_NAME = "Admin"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"


# ============================================================
# CREATE ADMIN
# ============================================================

db = SessionLocal()

try:

    existing_user = db.query(User).filter(
        User.email == ADMIN_EMAIL
    ).first()

    if existing_user:

        existing_user.role = "ADMIN"

        db.commit()

        print("Existing user converted to ADMIN.")

    else:

        admin = User(
            name=ADMIN_NAME,
            email=ADMIN_EMAIL,
            password=hash_password(ADMIN_PASSWORD),
            role="ADMIN"
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        cart = Cart(
            user_id=admin.id
        )

        db.add(cart)
        db.commit()

        print("Admin user created successfully.")

finally:

    db.close()