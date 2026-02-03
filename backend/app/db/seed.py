import sys
import os

# Add the project root to sys.path to allow imports from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.db.session import SessionLocal, engine
from app.models.models import Admin, Base
from app.core.security import get_password_hash
from sqlalchemy import text

def seed_admin():
    print("Connecting to database...")
    db = SessionLocal()
    try:
        # Check if Admin table exists, if not create all
        print("Checking tables...")
        Base.metadata.create_all(bind=engine)
        
        # Ensure vector extension
        with engine.connect() as conn:
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
            except Exception as e:
                print(f"Warning: Could not create pgvector extension: {e}")
            
        # Check if admin already exists
        admin = db.query(Admin).filter(Admin.username == "admin").first()
        if not admin:
            print("Creating super admin user...")
            new_admin = Admin(
                username="admin",
                password_hash=get_password_hash("Admin@123")
            )
            db.add(new_admin)
            db.commit()
            print("Super admin created successfully: admin / Admin@123")
        else:
            print("Admin user already exists. Updating password to  Admin@123...")
            admin.password_hash = get_password_hash("Admin@123")
            db.commit()
            print("Admin password updated.")
            
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
