from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import Staff, FaceEmbedding
from app.services.face_service import face_service
import numpy as np

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
    
    # Process images
    valid_embeddings = []
    for file in images:
        content = await file.read()
        img = face_service.process_image_bytes(content)
        embedding, error = face_service.get_embedding(img)
        
        if error:
            if "InsightFace not available" in error:
                # Return a proper error if insightface is not installed
                raise HTTPException(
                    status_code=503, 
                    detail="Face recognition service is not available. Please install required dependencies."
                )
            elif "No face detected" in error:
                # Skip images without faces
                continue
            else:
                # For other errors, skip the image with a warning
                print(f"Warning: {error}")
                continue
        
        if embedding:
            valid_embeddings.append(embedding)
    
    if not valid_embeddings:
        raise HTTPException(status_code=400, detail="No faces detected in uploaded images")
    
    # Create Staff
    new_staff = Staff(staff_id=staff_id, name=name, role=role)
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)
    
    # Save embeddings
    for emb in valid_embeddings:
        face_emb = FaceEmbedding(staff_id=new_staff.id, embedding=emb)
        db.add(face_emb)
    
    db.commit()
    
    return {"message": "Staff enrolled successfully", "embeddings_count": len(valid_embeddings)}

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