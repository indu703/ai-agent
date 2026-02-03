from app.db.session import engine
from sqlalchemy import text

def reset_database():
    print("Resetting database (forcing clean slate)...")
    try:
        with engine.connect() as conn:
            # Disable vector extension references if possible, but mainly drop tables
            print("Dropping tables...")
            conn.execute(text("DROP TABLE IF EXISTS face_embeddings CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS staff CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS admins CASCADE"))
            conn.commit()
        print("All tables dropped successfully using Raw SQL.")
        print("Now please run 'python app/db/seed.py' to recreate them correctly.")
    except Exception as e:
        print(f"Error resetting database: {e}")

if __name__ == "__main__":
    reset_database()
