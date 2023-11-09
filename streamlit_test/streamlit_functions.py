import os

from sqlalchemy import text

from database.db import FenologikDb

def query_filter():
    db = FenologikDb(os.environ["DATABASE_URL"])
    session = db.get_session()
    conn = session.connection().connection
    cur = conn.cursor()

    # Define the SQL query
    query = text(f"""
        SELECT 
    """)