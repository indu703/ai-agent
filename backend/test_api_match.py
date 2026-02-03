import requests

# This is the image you uploaded earlier
IMAGE_PATH = r"C:/Users/DELL/.gemini/antigravity/brain/dd5a3628-eff4-4be7-ae63-fccac13b4fd8/uploaded_media_1770115077318.png"
API_URL = "http://localhost:8000/api/recognition/identify"

def test_upload():
    print(f"Testing API with real image: {IMAGE_PATH}")
    try:
        with open(IMAGE_PATH, 'rb') as f:
            files = {'file': f}
            response = requests.post(API_URL, files=files)
            
        print("\n--- API RESPONSE ---")
        print(f"Status Code: {response.status_code}")
        print("Body:", response.json())
        print("--------------------")
        
        data = response.json()
        if data.get("identity") == "known":
            print("\nRESULT: SUCCESS (Simulated)")
            print(f"Why? Because Lite Mode logic returned the last enrolled user: {data.get('name')}")
        else:
            print("\nRESULT: UNKNOWN")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_upload()
