# 10 — Testing

Manual, command-line ways to exercise every endpoint without needing the phone or dashboard — useful for verifying each piece works in isolation, both locally and against the deployed Render URL.

Set a variable once so the commands below are copy-pasteable either way:
```bash
# local
export BASE_URL="http://localhost:8000/api"
# or, once deployed
export BASE_URL="https://<your-app>.onrender.com/api"
```

---

## 1. Health check
Confirms the service is up (and, against Render, wakes it from a cold sleep — see [09-deployment-guide.md](./09-deployment-guide.md)).

```bash
curl -s "$BASE_URL/health"
```
Expected:
```json
{ "status": "ok" }
```

---

## 2. Upload a test frame — no pothole expected
Use any clean road photo (no pothole) to confirm the discard path (BR-3) works.

```bash
curl -s -X POST "$BASE_URL/upload_frame" \
  -F "image=@./test-images/clean-road.jpg" \
  -F "lat=28.6519" \
  -F "lon=77.1927" \
  -F "captured_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```
Expected:
```json
{ "detected": false }
```

## 3. Upload a test frame — pothole expected
Use a clear pothole photo to confirm the full accept path (detection → severity → DB write).

```bash
curl -s -X POST "$BASE_URL/upload_frame" \
  -F "image=@./test-images/pothole-1.jpg" \
  -F "lat=28.6520" \
  -F "lon=77.1930" \
  -F "captured_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```
Expected:
```json
{ "detected": true, "id": 1, "severity": "Medium", "confidence": 0.78 }
```

**Edge cases worth trying:**
- A pothole photo shot at an angle / partially in shadow — checks the confidence threshold (BR-2) isn't too strict.
- A manhole cover or tar patch (common false-positive triggers, per the original project plan) — confirms the model isn't over-triggering.
- A very large, close-up pothole — should land in the "High" severity bucket (BR-4).
- A distant, small pothole — should land in "Low".

---

## 4. Fetch all results
```bash
curl -s "$BASE_URL/results" | jq '.'
```
Confirms the row from step 3 comes back, and that image data is included (per the API design note in [06-api-design.md](./06-api-design.md)).

## 5. Fetch results filtered by severity
```bash
curl -s "$BASE_URL/results?severity=High" | jq '.'
```

## 6. Fetch results since a timestamp
```bash
curl -s "$BASE_URL/results?since=2026-09-26T00:00:00Z" | jq '.'
```

## 7. Fetch a single result by ID
```bash
curl -s "$BASE_URL/results/1" | jq '.'
```
Expected: `404` with `{ "error": "..." }` if you use an ID that doesn't exist — worth checking this explicitly.

---

## 8. Simulate a full capture session (without the phone)
A small script to hammer `/upload_frame` every 2 seconds using a folder of test images, standing in for the phone client. Useful for a dry run of a full ~10-minute session before the real demo.

```bash
#!/usr/bin/env bash
# simulate-session.sh — cycles through test-images/, posting one every 2s
IMAGES=(./test-images/*.jpg)
LAT=28.6519
LON=77.1927

for img in "${IMAGES[@]}"; do
  ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  echo "Posting $img at $ts"
  curl -s -X POST "$BASE_URL/upload_frame" \
    -F "image=@$img" \
    -F "lat=$LAT" \
    -F "lon=$LON" \
    -F "captured_at=$ts" | jq -c '.'
  # nudge GPS slightly each frame, to see pins spread out on the dashboard
  LAT=$(echo "$LAT + 0.0001" | bc)
  LON=$(echo "$LON + 0.0001" | bc)
  sleep 2
done
```
Run it, then open the dashboard and confirm pins appear roughly in real time as the loop runs.

---

## Pre-demo test checklist
- [ ] `/health` responds `ok` after waking a cold Render instance.
- [ ] A known clean-road image returns `detected: false` and adds nothing to `/results`.
- [ ] A known pothole image returns `detected: true` with a plausible severity.
- [ ] `/results` reflects a new row within a few seconds of posting.
- [ ] Dashboard shows the new pin at roughly the right map location without a manual refresh.
- [ ] `simulate-session.sh` runs end-to-end without dropped requests or timeouts.
- [ ] Confidence threshold (`DETECTION_CONFIDENCE_THRESHOLD`) doesn't cause obvious false positives/negatives on your actual test image set — adjust per BR-2 if needed before the live demo.
