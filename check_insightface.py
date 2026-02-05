
try:
    import insightface
    print(f"insightface version: {insightface.__version__}")
    from insightface.app import FaceAnalysis
    print("FaceAnalysis imported successfully")
except ImportError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Other error: {e}")
