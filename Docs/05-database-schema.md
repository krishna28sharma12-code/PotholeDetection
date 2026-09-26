# 05 — Database Schema

## Choice: PostgreSQL (primary), MongoDB (alternative)
The data is a single, fixed-shape record per detection — a natural fit for one relational table. Postgres is the primary recommendation; a MongoDB collection schema is included below if you'd rather use that instead. Pick one — don't run both.

**Free hosting options:**
- **Postgres**: [Neon](https://neon.tech) or [Supabase](https://supabase.com) — both have a permanent free tier. (Render's own free Postgres add-on expires after 90 days, so it's not recommended for anything you want to keep working past that window.)
- **MongoDB**: [MongoDB Atlas](https://www.mongodb.com/atlas) free M0 cluster (512MB storage).

---

## Option A — PostgreSQL

### Table: `detections`

```sql
CREATE TABLE detections (
    id              SERIAL PRIMARY KEY,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    captured_at     TIMESTAMPTZ NOT NULL,           -- timestamp from the phone client
    latitude        DOUBLE PRECISION NOT NULL,
    longitude       DOUBLE PRECISION NOT NULL,
    severity        TEXT NOT NULL CHECK (severity IN ('Low', 'Medium', 'High')),
    confidence      REAL NOT NULL,
    bbox_area_pct   REAL,                           -- nullable: may fall back to confidence-only (BR-4)
    normal_image    TEXT NOT NULL,                  -- base64-encoded JPEG
    annotated_image TEXT NOT NULL                   -- base64-encoded JPEG with bounding box drawn
);

CREATE INDEX idx_detections_created_at ON detections (created_at DESC);
CREATE INDEX idx_detections_severity ON detections (severity);
```

### Sample row (abbreviated)
```json
{
  "id": 17,
  "created_at": "2026-09-26T10:15:32Z",
  "captured_at": "2026-09-26T10:15:31Z",
  "latitude": 28.6519,
  "longitude": 77.1927,
  "severity": "Medium",
  "confidence": 0.78,
  "bbox_area_pct": 9.4,
  "normal_image": "<base64 string>",
  "annotated_image": "<base64 string>"
}
```

### Notes
- `SERIAL` auto-incrementing integer ID is fine at this scale; no need for UUIDs.
- Storing base64 in `TEXT` columns is simple and works well under ~1,000 rows; if this ever needs to scale up, move images to object storage (e.g., Supabase Storage, Cloudinary) and store just a URL instead.
- No foreign keys / related tables needed for v1 — everything lives in one table.

---

## Option B — MongoDB

### Collection: `detections`

```json
{
  "_id": "ObjectId(...)",
  "created_at": "2026-09-26T10:15:32Z",
  "captured_at": "2026-09-26T10:15:31Z",
  "location": {
    "lat": 28.6519,
    "lon": 77.1927
  },
  "severity": "Medium",
  "confidence": 0.78,
  "bbox_area_pct": 9.4,
  "normal_image": "<base64 string>",
  "annotated_image": "<base64 string>"
}
```

### Indexes
```js
db.detections.createIndex({ created_at: -1 });
db.detections.createIndex({ severity: 1 });
```

### Notes
- If you want to use MongoDB's native geospatial queries later (e.g. "detections within X meters"), store `location` as a GeoJSON `Point` (`{type: "Point", coordinates: [lon, lat]}`) and add a `2dsphere` index instead — not needed for v1's simple "show everything" dashboard, but worth knowing if the roadmap's dedup feature ([08-roadmap.md](./08-roadmap.md)) gets picked up.

---

## Environment variable
Whichever you choose, the backend expects one connection string:
```
DATABASE_URL=postgresql://user:password@host:port/dbname
# or
DATABASE_URL=mongodb+srv://user:password@cluster.mongodb.net/dbname
```
