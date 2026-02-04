import sys
import os
from sqlalchemy import text

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.db.session import SessionLocal, engine
from app.models.models import Base

def reset_db_for_real_ai():
    print("Connecting to database...")
    db = SessionLocal()
    try:
        # 1. Enable pgvector extension
        print("Checking/Enabling pgvector extension...")
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        db.commit()
        
        # 2. Drop existing face tables to clear incompatible schema
        print("Dropping face_embeddings and staff tables...")
        db.execute(text("DROP TABLE IF EXISTS face_embeddings CASCADE"))
        db.execute(text("DROP TABLE IF EXISTS staff CASCADE"))
        db.commit()
        
        # 3. Recreate tables with new schema
        print("Recreating tables with correct Vector(512) type...")
        Base.metadata.create_all(bind=engine)
        
        print("\nSUCCESS: Database is now ready for Real AI!")
        print("Please restart your backend server now.")
        
    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_db_for_real_ai()
