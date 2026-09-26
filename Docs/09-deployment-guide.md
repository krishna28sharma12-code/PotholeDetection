# 09 — Deployment Guide

Step-by-step for deploying this project on Render with a free-tier cloud database, plus a pre-demo checklist to avoid cold-start surprises.

## 1. Provision the database

**Option A — Postgres via Neon (recommended)**
1. Sign up at neon.tech (free, no credit card).
2. Create a new project → it gives you a connection string immediately.
3. Run the DDL from [05-database-schema.md](./05-database-schema.md) against it (via Neon's SQL editor, or `psql`).
4. Copy the connection string — this is your `DATABASE_URL`.

**Option B — Postgres via Supabase**
1. Sign up at supabase.com, create a new project.
2. Use the SQL editor to run the DDL from [05-database-schema.md](./05-database-schema.md).
3. Grab the connection string from Project Settings → Database.

**Option C — MongoDB Atlas**
1. Sign up at mongodb.com/atlas, create a free M0 cluster.
2. Create a database user + allow-list your IP (or `0.0.0.0/0` for simplicity in a demo).
3. Copy the `mongodb+srv://...` connection string.

## 2. Get a Roboflow API key
1. Sign up at roboflow.com (free, no credit card).
2. Find or fork the pothole detection model you're using (e.g. from Roboflow Universe).
3. Grab your API key from workspace settings, and note the model ID/version you're calling.

## 3. Deploy the backend on Render
1. Push the repo (structure per [07-coding-conventions.md](./07-coding-conventions.md)) to GitHub.
2. In Render: New → Web Service → connect the repo.
3. Set the build/start commands (e.g. `pip install -r backend/requirements.txt` / `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`).
4. Add environment variables (Render dashboard → Environment):
   - `ROBOFLOW_API_KEY`
   - `ROBOFLOW_MODEL_ID`
   - `DATABASE_URL`
   - `DETECTION_CONFIDENCE_THRESHOLD` (e.g. `0.5`)
5. Deploy, then hit `https://<your-app>.onrender.com/api/health` to confirm it's live.

## 4. Serve the phone client and dashboard
Either:
- Serve `static/capture/index.html` and `static/dashboard/index.html` directly from the same backend service (simplest — one URL, no CORS to configure), **or**
- Deploy them as a separate Render Static Site (free), and enable CORS on the backend for that origin.

## 5. Pre-demo checklist (do this 5–10 minutes before each session)
- [ ] Hit `/api/health` once to wake the Render service from any cold sleep.
- [ ] Open the dashboard and confirm it loads with whatever test data already exists (clear old rows first if you want a clean demo).
- [ ] Open the phone capture page on the actual demo phone, grant camera + GPS permissions **before** you're on the move.
- [ ] Do one manual test frame (point the phone at a real or printed pothole photo) and confirm it shows up on the dashboard within a few seconds.
- [ ] Confirm the phone has a solid data/WiFi connection at the demo location.

## 6. During the demo
- Start capture on the phone, do your route (~10 minutes), stop capture.
- Switch to the dashboard to show the pins/list that accumulated.
- Repeat steps 5–6 for the second location — no redeploy needed, just a fresh capture session.

## 7. After the demo
- Optionally clear the `detections` table/collection if you want a clean slate for a future run:
  ```sql
  TRUNCATE detections;
  ```
  or, for MongoDB:
  ```js
  db.detections.deleteMany({});
  ```
