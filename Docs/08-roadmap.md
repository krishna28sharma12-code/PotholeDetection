# 08 — Roadmap

## v1 — Demo (current scope)
Everything described in docs 00–07: phone capture → Roboflow detection → Postgres/Mongo storage → Leaflet dashboard, deployed on Render free tier, sized for two ~10-minute sessions.

## v1.1 — Near-term improvements (post-demo, still small-scale)
- **Deduplication**: collapse multiple detections of the same physical pothole (GPS proximity + time window) into one dashboard entry.
- **Reverse geocoding**: turn raw GPS into a human-readable street address (e.g. via a free geocoding API) for the dashboard list view.
- **Session grouping**: tag detections with a session ID so multiple demo runs can be viewed/filtered separately.
- **Configurable severity thresholds**: move the BR-4 bbox-area cutoffs into an admin-editable config rather than a fixed constant, once real data shows whether 5%/15% are the right splits.
- **Local model inference**: swap the Roboflow hosted API call for a locally-run YOLOv8 model (via `ultralytics`) on the backend — removes the external API dependency and its rate limits, at the cost of managing model weights and compute in the deployment.

## v2 — Longer-term / production-direction ideas
- **Manual review queue**: let an authority approve/reject a detection before it appears on the public-facing dashboard.
- **Native mobile app**: replace the browser-based capture page with a proper Android/iOS app for more reliable background capture and offline queuing when connectivity drops.
- **Multi-vehicle / multi-operator support**: multiple phones reporting concurrently, with per-device identification.
- **Authentication**: login for dashboard viewers, API keys per client for the upload endpoint.
- **Cloud object storage for images**: move off base64-in-database once volume grows past what's comfortable in a single table (e.g. Supabase Storage, S3-compatible free tier).
- **Status workflow**: Reported → Verified → In Progress → Fixed → Closed lifecycle per detection, with dashboard filtering by status.
- **Analytics dashboard**: aggregate stats — detections per week, severity breakdown, hotspot heatmap.
- **Horizontal scaling**: move off a single free Render instance once traffic exceeds what one instance + free-tier DB can handle.

## Explicitly not planned
- Privacy handling (face/license-plate blurring) — flagged in v1 as out of scope and not currently on the roadmap; would need to be added before any real-world (non-demo) deployment involving public roads.
