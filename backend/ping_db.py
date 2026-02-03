import psycopg2
import sys

def ping():
    try:
        print("Pinging DB...")
        conn = psycopg2.connect(
            dbname="face_db",
            user="admin",
            password="password",
            host="localhost",
            port="5433",
            connect_timeout=3
        )
        print("PING SUCCESS")
        conn.close()
    except Exception as e:
        print(f"PING FAILED: {e}")

if __name__ == "__main__":
    ping()
