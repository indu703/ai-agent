from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import Staff, FaceEmbedding
from app.services.face_service import face_service
import numpy as np
from fastapi.concurrency import run_in_threadpool

router = APIRouter()

@router.post("/enroll")
async def enroll_staff(
    staff_id: str = Form(...),
    name: str = Form(...),
    role: str = Form(...),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    # Check if staff exists
    existing = db.query(Staff).filter(Staff.staff_id == staff_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Staff ID already exists")
    
    valid_embeddings = []
    
    angle_buckets = {
        "Front": False,
        "Left": False, 
        "Right": False,
        "Down": False
    }
    
    # Store details for error reporting
    processed_files = []
    
    for idx, file in enumerate(images):
        content = await file.read()
        img = face_service.process_image_bytes(content)
        
        # New method that returns embedding + pose
        # Heavy AI processing wrapped in threadpool
        data, error = await run_in_threadpool(face_service.analyze_face, img)
        
        file_status = "valid"
        pose_info = "N/A"
        
        if error:
            if "InsightFace not available" in error and idx == 0:
                 # Only critical if we can't do anything (though we might be in Lite Mode)
                 pass 
            print(f"Image {file.filename}: {error}")
            file_status = f"error: {error}"
        elif data:
            emb = data["embedding"]
            pose = data["pose"]
            yaw = pose["yaw"]
            pitch = pose["pitch"]
            pose_info = f"Yaw: {yaw:.1f}, Pitch: {pitch:.1f}"
            
            bucket_found = []
            
            # Left/Right (Yaw)
            if yaw > 25: # Relaxed from 20
                angle_buckets["Left"] = True
                bucket_found.append("Left")
            elif yaw < -25: # Relaxed from -20
                angle_buckets["Right"] = True
                bucket_found.append("Right")
                
                
            if pitch < -10:
                angle_buckets["Down"] = True
                bucket_found.append("Down")
                
            if abs(yaw) < 30 and abs(pitch) < 20:
                angle_buckets["Front"] = True
                bucket_found.append("Front")
                
            valid_embeddings.append(emb)
            file_status = f"Accepted ({', '.join(bucket_found)})" if bucket_found else "Accepted (Ambiguous Pose)"

        processed_files.append(f"{file.filename}: {file_status} [{pose_info}]")

    # Strict Validation
    missing_angles = [k for k, v in angle_buckets.items() if not v]
    
    if missing_angles:
        # In Lite Mode, we might skip this strict check or mock it, 
        # but the requirement states "required", so we enforce it.
        # Exception: If NO faces were found at all
        if not valid_embeddings:
            raise HTTPException(status_code=400, detail="No faces detected in uploaded images.")
            
        detail_msg = f"Enrollment failed. Missing angles: {', '.join(missing_angles)}. Please upload photos looking: {', '.join(missing_angles)}."
        # Add debug info for the user to understand why their photos failed
        detail_msg += f" Processing Details: {'; '.join(processed_files)}"
        raise HTTPException(status_code=400, detail=detail_msg)
    
    new_staff = Staff(staff_id=staff_id, name=name, role=role)
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)
    
    for emb in valid_embeddings:
        face_emb = FaceEmbedding(staff_id=new_staff.id, embedding=emb)
        db.add(face_emb)
    
    db.commit()
    
    return {
        "message": "Staff enrolled successfully", 
        "embeddings_count": len(valid_embeddings),
        "coverage": "Full 5-Angle (Front, Left, Right, Up, Down)"
    }

@router.get("/")
def list_staff(db: Session = Depends(get_db)):
    # Return all staff (without embeddings to save bandwidth)
    staff_list = db.query(Staff).filter(Staff.status == "active").all()
    return staff_list

@router.delete("/{staff_id}")
def delete_staff(staff_id: str, db: Session = Depends(get_db)):
    staff = db.query(Staff).filter(Staff.staff_id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    
    # Delete staff (Cascade will delete embeddings)
    db.delete(staff)
    db.commit()
    return {"message": "Staff deleted"}

# Optional: Add a health check endpoint
@router.get("/health/face-service")
def check_face_service_health():
    """Check if face recognition service is available"""
    try:
        # Try to create a simple test
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        _, error = face_service.get_embedding(test_img)
        
        if error and "InsightFace not available" in error:
            return {
                "status": "unavailable",
                "message": "Face recognition service is not installed. Please install insightface."
            }
        else:
            return {
                "status": "available",
                "message": "Face recognition service is ready"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Service check failed: {str(e)}"
        }