from fastapi import FastAPI
import os, psycopg2

app = FastAPI()

def conn():
    return psycopg2.connect(
        dbname=os.getenv("PG_DB","appdb"),
        user=os.getenv("PG_USER","app"),
        password=os.getenv("PG_PASS","passw0rd"),
        host=os.getenv("PG_HOST","pg"),
        port=os.getenv("PG_PORT","5432")
    )

@app.get("/stats")
def stats():
    c = conn(); cur = c.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS hits(ts TIMESTAMP DEFAULT NOW());")
    cur.execute("INSERT INTO hits DEFAULT VALUES;")
    c.commit()
    cur.execute("SELECT COUNT(*) FROM hits;")
    n = cur.fetchone()[0]
    cur.close(); c.close()
    return {"hits": n, "env": os.getenv("APP_ENV","local")}
