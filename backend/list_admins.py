from app.db.session import SessionLocal
from app.models.models import Admin

def list_admins():
    db = SessionLocal()
    try:
        admins = db.query(Admin).all()
        print(f"Total Admins: {len(admins)}")
        for a in admins:
            print(f"ID: {a.id}, Username: '{a.username}', Hash: {a.password_hash[:10]}...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_admins()
