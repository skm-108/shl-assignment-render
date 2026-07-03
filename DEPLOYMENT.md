# Deployment Guide

## Local Run

1. Install Python 3.12.
2. From the repository root, start the API with:

```bash
uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

3. Verify readiness at `GET /health`.
4. Send a stateless conversation payload to `POST /chat`.

## Hosting Target

- Render is the recommended baseline target.
- Any container host that can run Uvicorn will work.

## Runtime Notes

- The service is stateless across chat requests.
- The catalog is loaded from `New folder/shl_product_catalog.json` at startup.
- The current implementation does not require external model credentials to serve the API.

## Endpoints

- `GET /health` returns `{"status": "ok"}`.
- `POST /chat` returns the exact response schema required by the assignment.

## Operational Checks

- Confirm the catalog file is present in the deployment artifact.
- Confirm the process can read the catalog file on startup.
- Confirm `/health` responds before enabling traffic.
- Run the public trace regression suite before release if the environment supports it.
