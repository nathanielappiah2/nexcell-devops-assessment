#!/usr/bin/env bash

set -u

FAILED=0

pass() {
  echo "PASS: $1"
}

fail() {
  echo "FAIL: $1"
  FAILED=1
}

echo "Running NexCell smoke tests..."

if curl --fail --silent --max-time 5 http://localhost:8000/health > /dev/null; then
  pass "API liveness"
else
  fail "API liveness"
fi

if curl --fail --silent --max-time 5 http://localhost:8000/ready > /dev/null; then
  pass "API readiness"
else
  fail "API readiness"
fi

if docker compose exec -T redis redis-cli ping | grep -q "PONG"; then
  pass "Redis"
else
  fail "Redis"
fi

TEST_JOB="smoke-test-$(date +%s)"

WORKER_OK=0

for attempt in {1..10}; do
  if docker compose logs worker 2>&1 | grep -q "$TEST_JOB"; then
    WORKER_OK=1
    break
  fi

  sleep 1
done

if [ "$WORKER_OK" -eq 1 ]; then
  pass "Worker consumed Redis job"
else
  fail "Worker did not consume Redis job"
fi

if [ "$FAILED" -ne 0 ]; then
  echo "Smoke tests failed."
  exit 1
fi

echo "All smoke tests passed."
