import numpy as np
import cv2
from typing import Optional, List
import os
import sys

try:
    import insightface
    from insightface.app import FaceAnalysis
    HAS_INSIGHTFACE = True
except ImportError:
    HAS_INSIGHTFACE = False
    class FaceAnalysis:
        def __init__(self, **kwargs): pass
        def prepare(self, **kwargs): pass
        def get(self, img): return []

class FaceService:
    def __init__(self):
        global HAS_INSIGHTFACE
        if HAS_INSIGHTFACE:
            try:
                self.app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
                self.app.prepare(ctx_id=0, det_size=(640, 640), det_thresh=0.3)
            except Exception as e:
                print(f"Error loading InsightFace model: {e}")
                HAS_INSIGHTFACE = False
                self.app = None
        else:
            self.app = None
    
    def process_image_bytes(self, file_bytes):
        """Convert bytes to OpenCV image"""
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img

    def estimate_pose(self, face) -> dict:
        """
        Estimate Head Pose (Yaw, Pitch) using 5 landmarks.
        Landmarks: [RightEye, LeftEye, Nose, RightMouth, LeftMouth] (Index 0-4)
        Note: InsightFace keypoints are usually [LeftEye, RightEye, Nose, LeftMouth, RightMouth] or similar.
        Standard InsightFace 5-points:
        0: Left Eye
        1: Right Eye
        2: Nose
        3: Left Mouth Corner
        4: Right Mouth Corner
        """
        if face is None or face.kps is None:
            return {"yaw": 0.0, "pitch": 0.0}
            
        kps = face.kps
        le, re, n, lm, rm = kps[0], kps[1], kps[2], kps[3], kps[4]
        
        eye_dist = np.linalg.norm(re - le) + 1e-6
        left_dist = np.linalg.norm(n - le)
        right_dist = np.linalg.norm(n - re)
        
        yaw_ratio = (right_dist - left_dist) / (eye_dist / 2)
        yaw = yaw_ratio * 70.0
        
        eyes_center = (le + re) / 2
        mouth_center = (lm + rm) / 2
        face_height = np.linalg.norm(eyes_center - mouth_center) + 1e-6
        
        dist_nose_eyes = np.linalg.norm(n - eyes_center)
        pitch_ratio = dist_nose_eyes / face_height
        pitch = (0.5 - pitch_ratio) * 100
        
        return {"yaw": float(yaw), "pitch": float(pitch)}

    def check_face_quality(self, img) -> dict:
        """Returns a dict with quality metrics."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        angle = {"yaw": 0.0, "pitch": 0.0}
        
        if HAS_INSIGHTFACE and self.app is not None:
             faces = self.app.get(img)
             if faces:
                 faces = sorted(faces, key=lambda x: (x.bbox[2]-x.bbox[0]) * (x.bbox[3]-x.bbox[1]), reverse=True)
                 angle = self.estimate_pose(faces[0])

        return {
            "is_quality_pass": blur_score > 50,
            "blur_score": float(blur_score),
            "angle": angle, 
            "occlusion": False 
        }

    def align_face(self, img):
        """Normalize size to 112x112."""
        aligned_img = cv2.resize(img, (112, 112))
        return aligned_img

    def get_all_embeddings(self, img):
        """Get all face embeddings from image (for group photos)"""
        if not HAS_INSIGHTFACE or self.app is None:
            # Fallback for Lite Mode: return a single dummy embedding
            emb, _ = self.get_embedding(img)
            return [emb], None
        
        try:
            faces = self.app.get(img)
            if not faces:
                return [], "No face detected"
            
            for face in faces:
                bbox = face.bbox
                area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                face.area_calculated = float(area)
            
            faces = sorted(faces, key=lambda x: x.area_calculated, reverse=True)[:10]
            
            results = []
            for face in faces:
                embedding = face.embedding
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm
                
                results.append({
                    "embedding": embedding.tolist(),
                    "area": face.area_calculated
                })
                
            return results, None
        except Exception as e:
            return [], f"Error processing faces: {str(e)}"

    def get_embedding(self, img):
        """Get face embedding from image"""
        if not HAS_INSIGHTFACE or self.app is None:
            # Fallback for Lite Mode: return a dummy 512-dim vector
            # We normalize it so L2 distance logic (threshold 0.6-1.0) works consistently
            dummy_embedding = np.random.normal(0, 0.1, 512)
            dummy_embedding = (dummy_embedding / np.linalg.norm(dummy_embedding)).tolist()
            return dummy_embedding, None
        
        try:
            faces = self.app.get(img)
            if not faces:
                return None, "No face detected"
            
            faces = sorted(faces, key=lambda x: (x.bbox[2]-x.bbox[0]) * (x.bbox[3]-x.bbox[1]), reverse=True)
            target_face = faces[0]
            
            embedding = target_face.embedding
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
                
            return embedding.tolist(), None
        except Exception as e:
            return None, f"Error processing face: {str(e)}"

    def analyze_face(self, img):
        """
        Get embedding and pose for enrollment.
        Returns (data, error)
        data = { "embedding": [], "pose": {"yaw": 0, "pitch": 0} }
        """
        if not HAS_INSIGHTFACE or self.app is None:
            # Reuse get_embedding fallback logic
            emb, err = self.get_embedding(img)
            return {
                "embedding": emb,
                "pose": {"yaw": 0.0, "pitch": 0.0} # Mock pose
            }, None
            
        try:
            faces = self.app.get(img)
            if not faces:
                return None, "No face detected"
            
            # Largest face
            faces = sorted(faces, key=lambda x: (x.bbox[2]-x.bbox[0]) * (x.bbox[3]-x.bbox[1]), reverse=True)
            target_face = faces[0]
            
            # Embedding
            embedding = target_face.embedding
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            # Pose
            pose = self.estimate_pose(target_face)
            
            return {
                "embedding": embedding.tolist(),
                "pose": pose
            }, None
        except Exception as e:
            return None, f"Error analyzing face: {str(e)}"

    def detect_all(self, img):
        """Detect all faces in image"""
        if not HAS_INSIGHTFACE or self.app is None:
            return []
        
        try:
            faces = self.app.get(img)
            return faces
        except Exception as e:
            print(f"Error detecting faces: {e}")
            return []

# Global instance
face_service = FaceService()