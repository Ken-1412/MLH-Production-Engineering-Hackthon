#!/bin/bash
set -euo pipefail

echo "=== MLH PE Hackathon — Chaos Engineering Test ==="
BASE="http://localhost:5000"

step() { echo; echo "── $1 ──"; }

step "1: Verify service is UP before chaos"
curl -sf "$BASE/health" | python -m json.tool
echo "✅ Service is up"

step "2: Send malformed JSON — expect clean error, not traceback"
BAD=$(curl -s -X POST "$BASE/urls" \
  -H "Content-Type: application/json" \
  -d 'this is not json')
echo "Response: $BAD"
echo "$BAD" | python -c "
import sys, json
d = json.load(sys.stdin)
assert 'error' in d, 'FAIL: response has no error key'
print('✅ Got clean JSON error:', d.get('error'))
"

step "3: Send missing required field — expect 400"
MISSING=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST "$BASE/urls" \
  -H "Content-Type: application/json" \
  -d '{}')
[ "$MISSING" = "400" ] && echo "✅ Missing field → 400" \
  || echo "FAIL: expected 400, got $MISSING"

step "4: Kill the web container"
WEB_ID=$(docker ps --filter "name=web" -q | head -1)
echo "Killing container: $WEB_ID"
docker kill "$WEB_ID"
echo "Container killed"

step "5: Wait 10s for Docker restart policy to recover it"
sleep 10

step "6: Verify auto-recovery"
curl -sf "$BASE/health" | python -m json.tool
echo "✅ Service auto-recovered — chaos test PASSED"
