# 02 — Business Rules

These are the decision rules the system must apply — distinct from requirements (what the system must do) and architecture (how it's built).

## BR-1: Capture cadence
The phone client captures and sends a frame + GPS pair every **2 seconds** while a session is active. This cadence is fixed for v1 (not user-configurable).

## BR-2: Detection acceptance threshold
A frame is only treated as "pothole detected" if Roboflow returns at least one bounding box with **confidence ≥ 0.5**. Detections below this threshold are treated the same as "no detection" (discarded). This threshold is a config value, not hardcoded, so it can be tuned after seeing real demo data.

## BR-3: Discard rule
If no detection clears the confidence threshold (BR-2), the frame and its GPS data are **discarded immediately** — not stored anywhere, not logged beyond a debug-level log line. Only positive detections reach the database.

## BR-4: Severity classification
Severity is derived from the detected bounding box's area relative to the total frame area:

| Bounding box area (% of frame) | Severity |
|---|---|
| < 5% | Low |
| 5% – 15% | Medium |
| > 15% | High |

If a frame contains multiple bounding boxes, use the **largest** one to determine severity for that detection record. These thresholds are starting values — expect to tune them once you see real bounding box sizes from your demo footage.

**Fallback:** if bounding box area isn't reliably available from the API response, fall back to confidence score as a proxy (higher confidence → higher severity bucket), using the same three-tier split.

## BR-5: One detection record per accepted frame
Each accepted (positive) frame produces exactly **one** database row, even if multiple potholes appear in that frame. Multi-pothole-per-frame handling is out of scope for v1 (see BR-4 for how severity is chosen in that case).

## BR-6: No deduplication
The same physical pothole photographed multiple times (e.g., the vehicle idles near it, or two passes cover the same stretch of road) will produce **multiple separate records**. Deduplicating by GPS proximity is explicitly out of scope for v1 — see [08-roadmap.md](./08-roadmap.md).

## BR-7: Image storage format
Given Render's free tier has no persistent disk, both the normal and annotated images are stored as **base64-encoded strings directly in the database record**, not as file paths. This trades some database size efficiency for deployment simplicity — acceptable at demo scale (~600 records max).

## BR-8: API quota awareness
The backend should log (at minimum) a running count of Roboflow API calls made per session, so usage against the 10,000/month free quota is visible during testing. No hard cutoff is required for v1 given the demo's small expected volume, but visibility avoids surprises.

## BR-9: Data retention
No retention/expiry policy for v1 — records persist indefinitely on the free database tier until manually cleared. Acceptable given demo-scale data volume (a few hundred rows, each a few hundred KB at most).

## BR-10: Session boundaries
There is no explicit "start/stop session" concept enforced by the backend — the phone client simply starts and stops sending frames. All accepted detections land in the same table regardless of which physical location/session they came from (no session ID for v1).
