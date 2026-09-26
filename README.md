# Pothole Detection System

## Overview
A demo-scale pothole detection system designed for live infrastructure monitoring. A phone captures road frames and GPS data while moving, and a backend service evaluates each frame through a pothole-detection model via the Roboflow API. Confirmed detections (along with severity, confidence, and annotated images) are stored in a cloud database, while a web dashboard plots them in real-time on a map for a "road authority" viewer.

## Repository Structure
```
repo/
├── backend/
│   ├── main.py                # FastAPI app + route registration + static file mounting
│   ├── routes/
│   │   ├── upload.py          # POST /api/upload_frame
│   │   └── results.py         # GET /api/results, /api/results/:id
│   ├── services/
│   │   ├── detection.py       # Roboflow API call + confidence check
│   │   ├── severity.py        # bbox-area -> severity bucket logic (BR-4)
│   │   └── db.py              # DB connection pooling + queries
│   └── .env                   # Environment variables (not tracked in git)
├── static/
│   ├── capture/
│   │   └── index.html         # Phone capture client (Vanilla HTML/JS)
│   └── dashboard/
│       └── index.html         # Dashboard map client (Vanilla HTML/JS + Leaflet)
└── docs/                      # Architectural specifications and guides
```

## Running Locally

### 1. Requirements
- Python 3.9+
- A free Neon or Supabase PostgreSQL database
- A Roboflow account and API key for pothole detection
- Node.js (optional, required if using `npx localtunnel`)

### 2. Setup the Virtual Environment
Navigate to the root directory and set up a Python virtual environment:
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Environment Variables
Create a `.env` file inside the `backend/` folder and populate it with the following credentials:
```ini
ROBOFLOW_API_KEY="your_roboflow_key"
ROBOFLOW_MODEL_ID="pothole-model-id"
DATABASE_URL="postgresql://user:pass@host/dbname"
```
*(The backend handles database table migration automatically on startup).*

### 5. Start the Backend Server
Run the FastAPI application via uvicorn from the root directory:
```bash
uvicorn backend.main:app --port 8000 --reload
```
The server will start at `http://localhost:8000`.

### 6. Accessing the Clients
- **Dashboard**: Open `http://localhost:8000/dashboard` in your browser.
- **Phone Capture**: Open `http://localhost:8000/capture` in your browser. 
  *(Note: For the phone client to actually access the camera and GPS, it must be accessed via `https://` or `localhost`. To test on an actual mobile device, use a tunnel like localtunnel).*

#### Using a Tunnel for Mobile Testing
To securely expose your local server to your phone:
```bash
npx -y localtunnel --port 8000
```
Open the generated `https://*.loca.lt/capture` link on your phone browser.

## Deployment
This project is designed to be deployed as a single Web Service on Render's free tier, avoiding cold starts between separate frontend/backend instances.

For full step-by-step instructions on deploying the API and static sites, see the [Deployment Guide](docs/09-deployment-guide.md).

## Verification and Testing
To verify the DB migrations, endpoint contracts, and detection thresholds, refer to the manual cURL tests and scenarios outlined in the [Testing Guide](docs/10-testing.md).
