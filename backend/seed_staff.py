import sys
import os
# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.db.session import SessionLocal
from app.models.models import Staff, FaceEmbedding
import numpy as np

def seed():
    try:
        db = SessionLocal()
        print("Checking if staff exists...")
        staff = db.query(Staff).first()
        if not staff:
            print("Seeding test staff member...")
            test_staff = Staff(
                staff_id="EMP_007",
                name="James Bond",
                role="Special Agent",
                status="active"
            )
            db.add(test_staff)
            db.commit()
            db.refresh(test_staff)
            
            # Add a dummy embedding so the DB isn't totally empty of embeddings
            # We use a normalized random vector so L2 distance logic works
            dummy_emb = np.random.normal(0, 0.1, 512)
            dummy_emb = (dummy_emb / np.linalg.norm(dummy_emb)).tolist()
            test_face = FaceEmbedding(
                staff_id=test_staff.id,
                embedding=dummy_emb,
                active=True
            )
            db.add(test_face)
            db.commit()
            print(f"SUCCESS: Seeded staff '{test_staff.name}' (ID: {test_staff.staff_id})")
        else:
            print(f"ALREADY EXISTS: Found staff '{staff.name}'")
        db.close()
    except Exception as e:
        print(f"SEED FAILED: {e}")
        print("\nTIP: Make sure your Docker container 'face_rec_db' is RUNNING in Docker Desktop!")

if __name__ == "__main__":
    seed()
