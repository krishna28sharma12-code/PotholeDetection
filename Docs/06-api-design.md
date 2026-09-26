# 06 — API Design

## Base URL
```
https://<your-app>.onrender.com/api
```

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/upload_frame` | Phone client submits a frame + GPS for detection |
| GET | `/results` | Dashboard fetches all (or filtered) detections |
| GET | `/results/:id` | Dashboard fetches one detection's full detail |
| GET | `/health` | Uptime/warm-up check (also used to pre-warm the service before a demo) |

---

### `POST /upload_frame`

**Request:** `multipart/form-data`

| Field | Type | Notes |
|---|---|---|
| `image` | file (JPEG) | The captured frame |
| `lat` | float | GPS latitude |
| `lon` | float | GPS longitude |
| `captured_at` | ISO 8601 string | Client-side timestamp |

**Response — no detection:**
```json
{ "detected": false }
```

**Response — detection accepted:**
```json
{
  "detected": true,
  "id": 17,
  "severity": "Medium",
  "confidence": 0.78
}
```

**Status codes:** `200` on success (whether or not a pothole was detected — "no detection" is a normal outcome, not an error). `400` for a malformed request (e.g. missing `lat`/`lon`). `502` if the Roboflow call itself fails.

---

### `GET /results`

**Query parameters (all optional):**

| Param | Type | Notes |
|---|---|---|
| `severity` | `Low` \| `Medium` \| `High` | Filter to one severity level |
| `since` | ISO 8601 string | Only detections after this timestamp |
| `limit` | integer | Cap the number of rows returned (default: no cap, given demo scale) |

**Response:**
```json
[
  {
    "id": 17,
    "captured_at": "2026-09-26T10:15:31Z",
    "lat": 28.6519,
    "lon": 77.1927,
    "severity": "Medium",
    "confidence": 0.78,
    "annotated_image": "<base64 string>"
  }
]
```

**Design note:** this endpoint includes the annotated image inline (base64) rather than requiring a second call per row, since the dashboard needs the image for popups anyway and demo-scale row counts (a few hundred) keep the payload manageable. If this list grows large, switch to returning just metadata here and use `GET /results/:id` for the image on demand.

---

### `GET /results/:id`

**Response:**
```json
{
  "id": 17,
  "captured_at": "2026-09-26T10:15:31Z",
  "lat": 28.6519,
  "lon": 77.1927,
  "severity": "Medium",
  "confidence": 0.78,
  "bbox_area_pct": 9.4,
  "normal_image": "<base64 string>",
  "annotated_image": "<base64 string>"
}
```
`404` if the ID doesn't exist.

---

### `GET /health`
```json
{ "status": "ok" }
```
Used both as a standard liveness check and deliberately as the warm-up ping before a demo session (see [09-deployment-guide.md](./09-deployment-guide.md)) — hitting this endpoint a minute or two before starting wakes the Render service up so the first real frame isn't slowed by a cold start.

---

## Error format
All non-2xx responses use a consistent shape:
```json
{ "error": "description of what went wrong" }
```

## CORS
The backend must allow cross-origin requests from wherever the phone client and dashboard are hosted (same origin if served by the backend itself; a separate origin if using a Render Static Site). Enable CORS for `GET` and `POST` on the `/api/*` routes.

## Environment variables

| Variable | Purpose |
|---|---|
| `ROBOFLOW_API_KEY` | Auth for the Roboflow inference API |
| `ROBOFLOW_MODEL_ID` | Which trained/public model to call |
| `DATABASE_URL` | Postgres or MongoDB connection string |
| `DETECTION_CONFIDENCE_THRESHOLD` | Default `0.5` — see BR-2 |
| `PORT` | Provided by Render automatically |
