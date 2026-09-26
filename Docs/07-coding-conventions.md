# 07 — Coding Conventions

## Repository structure
```
repo/
├── backend/
│   ├── main.py                # FastAPI app + route registration
│   ├── routes/
│   │   ├── upload.py          # POST /api/upload_frame
│   │   └── results.py         # GET /api/results, /api/results/:id
│   ├── services/
│   │   ├── detection.py       # Roboflow API call + confidence check
│   │   ├── severity.py        # bbox-area -> severity bucket logic (BR-4)
│   │   └── db.py              # DB connection + queries
│   ├── models/
│   │   └── detection.py       # request/response schemas (pydantic)
│   ├── requirements.txt
│   └── .env.example
├── static/
│   ├── capture/
│   │   └── index.html         # phone client
│   └── dashboard/
│       └── index.html         # dashboard
└── docs/                      # this folder
```

## Backend (Python)
- **Framework**: FastAPI preferred (built-in request validation via pydantic, async support); Flask is an acceptable substitute if more familiar.
- **Style**: `snake_case` for functions/variables, `PascalCase` for classes, 4-space indentation.
- **Formatting/linting**: `black` for formatting, `ruff` (or `flake8`) for linting. Run both before committing.
- **Type hints**: use them on function signatures, especially for anything touching the DB or the Roboflow response — this is the kind of code that's easy to get subtly wrong without types.
- **Config**: all secrets and tunables (API keys, DB URL, confidence threshold) come from environment variables, loaded once at startup (e.g. via `python-dotenv` locally, native env vars on Render). Never hardcode a key or read `.env` mid-request.
- **Error handling**: catch and log Roboflow API failures distinctly from DB failures — you want to be able to tell "detection service down" from "database down" at a glance during a live demo.
- **Logging**: use Python's standard `logging` module, not bare `print()`. Log at minimum: each incoming frame (debug level), each accepted detection (info level), any upstream failure (error level).

## Frontend (phone client + dashboard)
- Plain HTML + vanilla JS — no build step, no framework, so both pages can be opened/debugged directly without tooling.
- **Style**: `camelCase` for JS variables/functions, 2-space indentation.
- Keep the phone client and dashboard as **single self-contained HTML files** (inline `<script>`/`<style>`) — simplest to deploy as static files, easiest to hand off to an AI coding tool as one unit each.
- No client-side framework, no npm dependencies for v1 — Leaflet.js is loaded via CDN `<script>` tag.

## Git conventions
- Commit messages: short imperative summary line (`Add severity bucket logic`, not `Added` or `Adding`), optional body for context.
- `.env` is git-ignored; commit `.env.example` with variable names but no real values.
- Branch per feature/doc-section if working incrementally (e.g. `feat/upload-endpoint`, `feat/dashboard-map`); fine to work directly on `main` for a solo demo project if that's simpler.

## Testing
- Given demo scope, exhaustive test coverage isn't required. At minimum, manually verify:
  - `/api/upload_frame` with a known pothole image returns `detected: true`.
  - `/api/upload_frame` with a clean road image returns `detected: false`.
  - `/api/results` reflects a just-inserted row within a few seconds.
- If you do want automated tests, `pytest` for the backend is the natural choice — but treat this as optional polish, not a blocker for the demo.

## Secrets checklist before pushing to a public repo
- [ ] No `ROBOFLOW_API_KEY` in source
- [ ] No `DATABASE_URL` (with credentials) in source
- [ ] `.env` present in `.gitignore`
