import psycopg2
try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="admin",
        password="password",
        host="localhost",
        port="5433"
    )
    print("SUCCESS: Connected with admin/password")
    conn.close()
except Exception as e:
    print(f"FAILURE: {e}")
