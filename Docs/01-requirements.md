# 01 — Requirements

## Functional requirements

| ID | Requirement |
|---|---|
| FR-1 | The phone client shall capture a camera frame and the current GPS coordinates approximately every 2 seconds while a capture session is active. |
| FR-2 | The phone client shall send each captured frame + GPS + client timestamp to the backend via an HTTP POST request. |
| FR-3 | The backend shall forward each received frame to the Roboflow detection API and read back detection results (bounding boxes + confidence). |
| FR-4 | If no pothole is detected in a frame, the backend shall discard the frame and shall not write anything to the database. |
| FR-5 | If a pothole is detected, the backend shall compute a severity bucket (Low / Medium / High) from the detection's bounding box size relative to frame area (or confidence, as fallback). |
| FR-6 | If a pothole is detected, the backend shall persist: the frame image, the GPS coordinates, the severity, the confidence score, and a timestamp. |
| FR-7 | The backend shall expose an endpoint returning all stored detections as JSON, for the dashboard to consume. |
| FR-8 | The backend shall expose an endpoint returning a single detection's full detail (including its image) by ID. |
| FR-9 | The dashboard shall render all detections as map pins, colored by severity, using Leaflet.js. |
| FR-10 | The dashboard shall render a list view of detections alongside the map (thumbnail, GPS, severity, timestamp). |
| FR-11 | Clicking a list entry shall focus/open the corresponding map pin, and vice versa. |
| FR-12 | The dashboard shall periodically re-fetch results (polling) so new detections appear without a manual page refresh. |

## Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-1 | The system must run entirely on free-tier services (Render, Roboflow, Neon/Supabase or MongoDB Atlas) for two demo sessions of ~10 minutes each. |
| NFR-2 | End-to-end latency from frame capture to a detection appearing available via the API should stay under ~5 seconds under normal conditions (excludes Render cold starts). |
| NFR-3 | The backend must handle a sustained request rate of roughly one frame every 2 seconds without dropping requests. |
| NFR-4 | API keys and database credentials must be provided via environment variables, never hardcoded or committed to source control. |
| NFR-5 | The system does not need to survive process restarts with all in-flight state intact — a restart mid-session losing the current frame is acceptable for v1. |
| NFR-6 | The dashboard must be usable on a laptop browser at minimum; mobile-responsive dashboard is not required for v1. |

## Assumptions
- Only one person (operator) will run the phone client at a time; no concurrent multi-device capture for v1.
- The phone and the demo location have a working internet connection (mobile data or WiFi) throughout each session.
- Two demo sessions, ~10 minutes each, at two different physical locations — not continuous 24/7 operation.
- Roboflow's free tier (10,000 inferences/month) is sufficient; expected usage is roughly 300 calls per session (~600 total).
- Render's free web service tier is acceptable despite cold starts and ephemeral disk (see Constraints below).

## Constraints
- **Render free tier has no persistent disk** — any file written to the local filesystem is lost on restart/redeploy. Images must therefore be stored as data (e.g., base64) in the database rather than on local disk. See [05-database-schema.md](./05-database-schema.md).
- **Render free web services spin down after ~15 minutes of inactivity** and take up to ~30–50 seconds to cold-start on the next request. The demo plan must include a warm-up step before each live session (see [09-deployment-guide.md](./09-deployment-guide.md)).
- **Roboflow free tier data is public** (Public plan). Acceptable for a demo; would need a paid plan to keep data private.
- Browser camera/GPS access requires HTTPS (or `localhost`) — Render deployments are HTTPS by default, so this is satisfied once deployed.

## Out of scope
See [00-overview.md](./00-overview.md) → Non-goals.
