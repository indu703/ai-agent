from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.db.session import get_db
from app.models.models import FaceEmbedding, Staff, HAS_PGVECTOR
from app.services.face_service import face_service
import numpy as np
from app.core.config import settings
from datetime import datetime

router = APIRouter()

@router.post("/identify")
async def identify_person(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    img = face_service.process_image_bytes(content)
    
    if img is None:
        return {"identity": "unknown", "reason": "Invalid image file", "status": "failed"}
    
    # Step B3: Face Quality Check
    quality = face_service.check_face_quality(img)
    if not quality["is_quality_pass"]:
        return {
            "identity": "unknown",
            "reason": "poor_quality",
            "quality_metrics": quality,
            "status": "rejected"
        }
    
    # Step B4/B5: Embedding Generation
    # We pass the full image to InsightFace to allow it to handle alignment internally
    # with maximum resolution, ensuring much better accuracy for side profiles.
    embedding, error = face_service.get_embedding(img)
    
    if not embedding:
        return {"identity": "unknown", "reason": "No face detected", "status": "failed"}
    
    # threshold for real models (normalized)
    # 0.6 is strict (high security). 1.25 provides the "convenient" robustness for side angles.
    threshold = 1.6 if settings.LITE_MODE else 1.25

    match_found = False
    result_data = None

    try:
        if HAS_PGVECTOR:
            # Try pgvector search (optimized) if the model says we have it
            dist_stmt = select(FaceEmbedding, FaceEmbedding.embedding.l2_distance(embedding).label("distance")) \
                        .order_by("distance").limit(1)
            
            match_row = db.execute(dist_stmt).first()
            
            if match_row:
                match_emb, distance = match_row
                if distance < threshold:
                    match_found = True
                    result_data = create_identity_response(match_emb.staff, distance, "success")
                else:
                    result_data = {
                        "identity": "unknown", 
                        "distance": float(distance), 
                        "reason": "low_confidence",
                        "status": "unverified",
                        "decision": "match_above_threshold"
                    }
        else:
            print("HAS_PGVECTOR is False, skipping optimized vector search.")
                
    except Exception as e:
        print(f"pgvector search failed, using Python fallback: {e}")
        db.rollback() 
    
    # FALLBACK SEARCH (Runs if no match found yet or vector search failed/skipped)
    if not match_found and result_data is None:
        all_embeddings = db.query(FaceEmbedding).all()
        if not all_embeddings:
            return {"identity": "unknown", "reason": "database_empty", "status": "failed"}
            
        # Optional: Shuffle if in Lite Mode to make simulated matches more diverse
        if settings.LITE_MODE:
            import random
            random.shuffle(all_embeddings)
            
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

    if result_data:
        return result_data

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
