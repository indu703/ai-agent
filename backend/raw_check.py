import psycopg2
from passlib.context import CryptContext

# Database settings
DB_NAME = "face_db"
DB_USER = "admin"
DB_PASS = "password"
DB_HOST = "localhost"
DB_PORT = "5433"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def check_raw():
    try:
        print(f"Connecting to {DB_HOST}:{DB_PORT}...")
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        
        cur.execute("SELECT username, password_hash FROM admins WHERE username = 'admin';")
        row = cur.fetchone()
        
        if row:
            username, pw_hash = row
            print(f"FOUND: {username}")
            
            test_pw = "Admin@123"
            try:
                valid = pwd_context.verify(test_pw, pw_hash)
                print(f"Password '{test_pw}' is {'VALID' if valid else 'INVALID'}")
            except Exception as e:
                print(f"Hash verification error: {e}")
        else:
            print("NOT FOUND: User 'admin' does not exist in 'admins' table.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_raw()
