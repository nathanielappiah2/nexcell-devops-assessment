import os
import time

import psycopg2

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@postgres:5432/nexcell"
)

for attempt in range(10):
    try:
        connection = psycopg2.connect(DATABASE_URL)

        with connection.cursor() as cursor:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS migration_check "
                "(id SERIAL PRIMARY KEY, created_at TIMESTAMP DEFAULT NOW())"
            )

        connection.commit()
        connection.close()

        print("Migration completed successfully")
        break

    except psycopg2.OperationalError:
        if attempt == 9:
            raise

        print("Postgres not ready, retrying...")
        time.sleep(2)
