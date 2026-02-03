from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.db.session import get_db
from app.models.models import FaceEmbedding, Staff
from app.services.face_service import face_service
import numpy as np
from app.core.config import settings
from datetime import datetime

router = APIRouter()

@router.post("/identify")
async def identify_person(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    img = face_service.process_image_bytes(content)
    
    # Step B3: Face Quality Check
    quality = face_service.check_face_quality(img)
    if not quality["is_quality_pass"]:
        return {
            "identity": "unknown",
            "reason": "poor_quality",
            "quality_metrics": quality,
            "status": "rejected"
        }
    
    # Step B4: Alignment
    aligned_img = face_service.align_face(img)
    
    # Step B5: Embedding
    embedding, error = face_service.get_embedding(aligned_img)
    
    if not embedding:
        return {"identity": "unknown", "reason": "No face detected", "status": "failed"}
    
    # Search in DB
    # We want to find the closest match and get the distance
    threshold = 0.6 # Adjustable threshold for L2 distance (lower is more strict)
    
    # --- LITE MODE MOCK ---
    if settings.LITE_MODE:
        # In Lite Mode, random embeddings never match. 
        # For testing purposes, we return the most recently enrolled person as a "Match".
        print("LITE_MODE: Simulating match for testing...")
        last_enrolled = db.query(Staff).order_by(Staff.id.desc()).first()
        if last_enrolled:
            return create_identity_response(last_enrolled, 0.15, "mock_success") # Fake low distance
    # ----------------------
    
    try:
        # Try pgvector search (optimized)
        dist_stmt = select(FaceEmbedding, FaceEmbedding.embedding.l2_distance(embedding).label("distance")) \
                    .order_by("distance").limit(1)
        
        match_row = db.execute(dist_stmt).first()
        
        if match_row:
            match_emb, distance = match_row
            if distance < threshold:
                staff = match_emb.staff
                # Step B7/B8: Identity Decision & Track State Update
                return create_identity_response(staff, distance, "success")
            else:
                return {
                    "identity": "unknown", 
                    "distance": float(distance), 
                    "reason": "low_confidence",
                    "status": "unverified",
                    "decision": "match_above_threshold"
                }
                
    except Exception as e:
        print(f"pgvector search failed, using Python fallback: {e}")
        # Fallback logic remains same but returns enhanced response
        all_embeddings = db.query(FaceEmbedding).all()
        if not all_embeddings:
             return {"identity": "unknown", "reason": "database_empty", "status": "failed"}
             
        best_match = None
        min_dist = float('inf')
        
        target_emb = np.array(embedding)
        for emb_obj in all_embeddings:
            curr_emb = np.array(emb_obj.embedding)
            dist = np.linalg.norm(target_emb - curr_emb)
            if dist < min_dist:
                min_dist = dist
                best_match = emb_obj
        
        if best_match and min_dist < threshold:
            return create_identity_response(best_match.staff, min_dist, "success_fallback")
        elif best_match:
            return {
                "identity": "unknown", 
                "distance": float(min_dist), 
                "reason": "low_confidence_fallback",
                "status": "unverified"
            }

    return {"identity": "unknown", "reason": "no_candidate_match", "status": "failed"}

def create_identity_response(staff, distance, decision_type):
    # Step B9: Behavior Engine Input
    return {
        "identity": "known",
        "staff_id": staff.staff_id,
        "name": staff.name,
        "role": staff.role,
        "distance": float(distance),
        "status": staff.status,
        "decision_type": decision_type,
        "timestamp": datetime.now().isoformat() # Just for reference
    }
