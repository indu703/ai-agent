import psycopg2
import sys

# Hardcoded test for postgres/root
try:
    print("Testing postgres/root connection...")
    conn = psycopg2.connect(
        dbname="ai-agent",
        user="postgres",
        password="root",
        host="localhost",
        port="5432"
    )
    print("SUCCESS: Connected as postgres/root")
    conn.close()
except Exception as e1:
    print(f"FAILED postgres/root: {e1}")
    
    # Try admin/password
    try:
        print("Testing admin/password connection...")
        conn = psycopg2.connect(
            dbname="ai-agent",
            user="admin",
            password="password",
            host="localhost",
            port="5432"
        )
        print("SUCCESS: Connected as admin/password")
        conn.close()
    except Exception as e2:
        print(f"FAILED admin/password: {e2}")

print("Python version:", sys.version)
