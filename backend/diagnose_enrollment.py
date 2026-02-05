import psycopg2
import sys

def check_staff():
    try:
        conn = psycopg2.connect(
            dbname="face_db",
            user="admin",
            password="password",
            host="localhost",
            port="5433"
        )
        cur = conn.cursor()
        cur.execute("SELECT staff_id, name, role FROM staff;")
        rows = cur.fetchall()
        print(f"TOTAL ENROLLED: {len(rows)}")
        for row in rows:
            print(f" - ID: {row[0]}, Name: {row[1]}, Role: {row[2]}")
        
        cur.execute("SELECT count(*) FROM face_embeddings;")
        emb_count = cur.fetchone()[0]
        print(f"TOTAL EMBEDDINGS: {emb_count}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DATABASE ERROR: {e}")

if __name__ == "__main__":
    check_staff()
