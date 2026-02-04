import sys
import os
import cv2
import numpy as np
from sqlalchemy.orm import Session

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.db.session import SessionLocal
from app.models.models import Staff, FaceEmbedding
from app.services.face_service import face_service
from app.core.config import settings

def debug_enroll():
    print(f"LITE_MODE: {settings.LITE_MODE}")
    db = SessionLocal()
    try:
        # Create a dummy face-like image (or just use zeros)
        # Real insightface might reject total zeros, let's make it look like something
        test_img = np.zeros((400, 400, 3), dtype=np.uint8)
        cv2.rectangle(test_img, (150, 150), (250, 250), (255, 255, 255), -1)
        
        print("1. Getting embedding...")
        embedding, error = face_service.get_embedding(test_img)
        
        if error:
            print(f"Embedding error: {error}")
            return
            
        print(f"Embedding size: {len(embedding)}")
        
        print("2. Creating staff record...")
        staff_id = "DEBUG_001"
        # Cleanup if exists
        db.query(Staff).filter(Staff.staff_id == staff_id).delete()
        db.commit()
        
        new_staff = Staff(staff_id=staff_id, name="Debug User", role="Tester")
        db.add(new_staff)
        db.commit()
        db.refresh(new_staff)
        
        print(f"3. Saving embedding for staff_id={new_staff.id}...")
        face_emb = FaceEmbedding(staff_id=new_staff.id, embedding=embedding)
        db.add(face_emb)
        db.commit()
        
        print("SUCCESS! Enrollment worked in debug mode.")
        
    except Exception as e:
        print("\n!!! ERROR CAUGHT !!!")
        print(str(e))
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    debug_enroll()
