import sys
import os
import cv2
import numpy as np

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

print("Attempting to load Real AI models...")
try:
    from app.services.face_service import face_service
    from app.core.config import settings
    
    print(f"LITE_MODE is: {settings.LITE_MODE}")
    
    # Create a blank image to test detection
    test_img = np.zeros((400, 400, 3), dtype=np.uint8)
    cv2.putText(test_img, "Test", (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    print("Initializing face service (this may download models)...")
    embedding, error = face_service.get_embedding(test_img)
    
    if error and "No face detected" in error:
        print("SUCCESS: AI Engine loaded correctly! (No face detected in blank image as expected)")
    elif error:
        print(f"ERROR: {error}")
    else:
        print("SUCCESS: Embedding generated!")
        
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
