import sys
try:
    import psycopg2
    print("SUCCESS: psycopg2 is installed and importable.")
    print(f"Path: {psycopg2.__file__}")
except ImportError as e:
    print(f"FAILURE: Could not import psycopg2. Error: {e}")
    print("Available modules (partial list):")
    print(sys.path)

try:
    # Test connection if parameters are provided
    from app.core.config import settings
    print(f"Testing connection to: {settings.SQLALCHEMY_DATABASE_URI}")
    conn = psycopg2.connect(settings.SQLALCHEMY_DATABASE_URI)
    print("SUCCESS: Connected to database.")
    conn.close()
except Exception as e:
    print(f"FAILURE: Could not connect to database. Error: {e}")
