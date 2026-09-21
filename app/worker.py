import os
import time

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
QUEUE_NAME = "jobs"

client = redis.Redis.from_url(REDIS_URL)

while True:
    job = client.blpop(QUEUE_NAME, timeout=5)

    if job:
        _, payload = job
        print(f"Processed job: {payload.decode()}", flush=True)

    time.sleep(1)
