import psycopg2
import sys

def test_connection(user, password, dbname="postgres"):
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host="localhost",
            port="5432",
            connect_timeout=3
        )
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

credentials = [
    ("postgres", "postgres"),
    ("postgres", "root"),
    ("postgres", "admin"),
    ("postgres", "password"),
    ("admin", "admin"),
    ("admin", "password"),
    ("root", "root"),
    ("root", "password"),
]

print("Starting Database Credential Discovery...")
print("---------------------------------------")

found = False
for user, password in credentials:
    print(f"Testing {user} / {password} ... ", end="", flush=True)
    success, error = test_connection(user, password)
    if success:
        print("SUCCESS!")
        print(f"\n>>> FOUND WORKING CREDENTIALS: USER='{user}', PASSWORD='{password}' <<<")
        found = True
        
        # Now check if face_db exists
        print(f"Checking if 'face_db' exists using these credentials...")
        try:
             conn = psycopg2.connect(dbname="postgres", user=user, password=password, host="localhost")
             conn.autocommit = True
             cur = conn.cursor()
             cur.execute("SELECT 1 FROM pg_database WHERE datname='face_db'")
             exists = cur.fetchone()
             if not exists:
                 print("'face_db' does not exist. Creating it now...")
                 cur.execute("CREATE DATABASE face_db")
                 print("'face_db' created successfully.")
             else:
                 print("'face_db' already exists.")
             cur.close()
             conn.close()
        except Exception as e:
             print(f"Error while ensuring database exists: {e}")
        break
    else:
        # Check if it's just a wrong password or something else
        if "authentication failed" in error.lower():
            print("Failed (Auth)")
        else:
            print(f"Failed (Other: {error})")

if not found:
    print("\n---------------------------------------")
    print("CRITICAL: No common credentials worked.")
    print("Please verify your local PostgreSQL installation and password.")
    print("Alternatively, if you have any other DB info, please let me know.")
