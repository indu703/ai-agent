from app.db.session import SessionLocal
from app.models.models import Admin
from app.core.security import verify_password

def check_admin():
    db = SessionLocal()
    try:
        admin = db.query(Admin).filter(Admin.username == "admin").first()
        if admin:
            print(f"FOUND: User='{admin.username}', Hash='{admin.password_hash[:10]}...'")
            pwd = "Admin@123"
            valid = verify_password(pwd, admin.password_hash)
            print(f"Testing password '{pwd}': {'VALID' if valid else 'INVALID'}")
        else:
            print("ERROR: Admin user NOT FOUND in database.")
    except Exception as e:
        print(f"Error checking admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_admin()
