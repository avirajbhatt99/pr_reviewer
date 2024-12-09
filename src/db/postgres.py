import os
from psycopg2 import pool


# Create a global connection pool
def init_connection_pool():
    return pool.SimpleConnectionPool(
        1,
        10,
        host=os.getenv("PG_HOST", "localhost"),
        database=os.getenv("PG_DATABASE", "aviraj"),
        user=os.getenv("PG_USER", "root"),
        password=os.getenv("PG_PASSWORD"),
        port=os.getenv("PG_PORT", "5432"),
    )


connection_pool = init_connection_pool()


def insert_data(query, params=None):
    connection = connection_pool.getconn()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            connection.commit()
    finally:
        connection_pool.putconn(connection)


def fetch_data(query):
    connection = connection_pool.getconn()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]

        return result
    finally:
        connection_pool.putconn(connection)


# create tables if they don't exist

# table analyzed_pr
query = """
CREATE TABLE IF NOT EXISTS analyzed_pr (
    id SERIAL PRIMARY KEY,
    repo_url VARCHAR(255) NOT NULL,
    pr_number INTEGER NOT NULL,
    task_id VARCHAR(255) NOT NULL,
    result JSON,
    status VARCHAR(255) NOT NULL
);
"""
insert_data(query)
