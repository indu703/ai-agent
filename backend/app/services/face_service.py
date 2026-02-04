import numpy as np
import cv2
from typing import Optional, List
import os

# Try to import insightface, but handle if it's not available
try:
    import insightface
    from insightface.app import FaceAnalysis
    HAS_INSIGHTFACE = True
except ImportError:
    HAS_INSIGHTFACE = False
    print("Warning: insightface not installed. Face recognition features will be disabled.")
    # Create dummy classes for type hints
    class FaceAnalysis:
        def __init__(self, **kwargs):
            pass
        def prepare(self, **kwargs):
            pass
        def get(self, img):
            return []

class FaceService:
    def __init__(self):
        global HAS_INSIGHTFACE
        if HAS_INSIGHTFACE:
            try:
                # Defaulting to CPU. If GPU is available, changing providers to ['CUDAExecutionProvider'] is recommended.
                self.app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
                self.app.prepare(ctx_id=0, det_size=(640, 640))
                print("InsightFace model loaded successfully.")
            except Exception as e:
                print(f"Error loading InsightFace model: {e}")
                HAS_INSIGHTFACE = False
                self.app = None
        else:
            self.app = None
            print("FaceService initialized without insightface - face recognition disabled")
    
    def process_image_bytes(self, file_bytes):
        """Convert bytes to OpenCV image"""
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img

    def check_face_quality(self, img) -> dict:
        """
        Step B3: Face Quality Check
        Returns a dict with quality metrics.
        In Lite Mode, we simulate a 'pass'.
        """
        # Calculate blur using Laplacian variance
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Simple heuristics for angle would need landmarks (insightface)
        # So we mock those for now
        return {
            "is_quality_pass": blur_score > 50, # Arbitrary threshold
            "blur_score": float(blur_score),
            "angle": 0.0, # Mock
            "occlusion": False # Mock
        }

    def align_face(self, img):
        """
        Step B4: Face Alignment & Normalization
        Normalize size to 112x112 as per Step A3/B4.
        """
        # In real scenario, would use facial landmarks (eyes) to rotate/crop.
        # For now, we just resize to the standard format.
        aligned_img = cv2.resize(img, (112, 112))
        return aligned_img

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
            
            # Sort by area to get the largest face (main subject)
            faces = sorted(faces, key=lambda x: (x.bbox[2]-x.bbox[0]) * (x.bbox[3]-x.bbox[1]), reverse=True)
            target_face = faces[0]
            
            # Normalize embedding to unit length (L2 norm = 1.0)
            # This makes the 0.6 threshold standard and highly accurate.
            embedding = target_face.embedding
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
                
            return embedding.tolist(), None
        except Exception as e:
            return None, f"Error processing face: {str(e)}"

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