from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.db.session import get_db
from app.models.models import FaceEmbedding, Staff, HAS_PGVECTOR
from app.services.face_service import face_service
import numpy as np
from app.core.config import settings
from datetime import datetime
from fastapi.concurrency import run_in_threadpool

router = APIRouter()

@router.post("/identify")
async def identify_person(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    img = face_service.process_image_bytes(content)
    
    if img is None:
        return {"identity": "unknown", "reason": "Invalid image file", "status": "failed"}
    
    quality = face_service.check_face_quality(img)
    if not quality["is_quality_pass"]:
        return {
            "identity": "unknown",
            "reason": "poor_quality",
            "quality_metrics": quality,
            "status": "rejected"
        }
    
    embeddings, error = await run_in_threadpool(face_service.get_all_embeddings, img)
    
    if not embeddings:
        return {"identity": "unknown", "reason": "No face detected", "status": "failed"}
    
    VERIFIED_THRESHOLD = 1.05
    CANDIDATE_THRESHOLD = 1.15

    all_vetted_matches = []
    
    for face_data in embeddings:
        try:
            embedding = face_data["embedding"]
            area = face_data.get("area", 0)
            
            candidate_staff = None
            candidate_dist = float('inf')
            
            if HAS_PGVECTOR:
                dist_stmt = select(FaceEmbedding, FaceEmbedding.embedding.l2_distance(embedding).label("dist")) \
                            .order_by("dist").limit(1)
                match_row = db.execute(dist_stmt).first()
                if match_row:
                    candidate_staff = match_row[0].staff
                    candidate_dist = float(match_row[1])
            else:
                all_embeddings_objs = db.query(FaceEmbedding).all()
                target_emb = np.array(embedding)
                for emb_obj in all_embeddings_objs:
                    curr_emb = np.array(emb_obj.embedding)
                    dist = np.linalg.norm(target_emb - curr_emb)
                    if dist < candidate_dist:
                        candidate_dist = dist
                        candidate_staff = emb_obj.staff

            if candidate_staff:
                if candidate_dist < VERIFIED_THRESHOLD:
                    match = create_identity_response(candidate_staff, candidate_dist, "success")
                    match["is_verified"] = True
                elif candidate_dist < CANDIDATE_THRESHOLD:
                    match = {
                        "identity": "unknown",
                        "distance": candidate_dist,
                        "reason": "low_confidence",
                        "status": "unverified",
                        "candidate_name": candidate_staff.name,
                        "staff_id": candidate_staff.staff_id,
                        "is_verified": False,
                        "decision_type": "uncertain"
                    }
                else:
                    match = {
                        "identity": "unknown",
                        "distance": candidate_dist,
                        "reason": "no_match",
                        "status": "failed",
                        "is_verified": False
                    }
                
                match["area"] = area
                all_vetted_matches.append(match)
                
        except Exception as e:
            print(f"Recognition search error: {e}")
            db.rollback()

    if not all_vetted_matches:
        return {"identity": "unknown", "reason": "no_candidate_match", "status": "failed"}

    all_vetted_matches.sort(
        key=lambda x: (
            not x.get("is_verified", False),
            x.get("decision_type") != "uncertain",
            -x.get("area", 0),
            x["distance"]
        )
    )
    
    primary_match = all_vetted_matches[0]

    response_data = primary_match.copy()
    response_data["all_identities"] = all_vetted_matches
    # Confidence threshold for the 'Low Confidence' badge in UI
    response_data["is_low_confidence"] = primary_match["distance"] > 0.95 
    
    return response_data

def create_identity_response(staff, distance, decision_type):
    return {
        "identity": "known",
        "staff_id": staff.staff_id,
        "name": staff.name,
        "role": staff.role,
        "distance": float(distance),
        "status": staff.status,
        "decision_type": decision_type,
        "timestamp": datetime.now().isoformat()
    }
