# CivicOS Deployment Guide

CivicOS is packaged for production using Docker Compose, orchestrating three main services:
1. **Frontend**: Next.js React application served on port `3000`.
2. **Backend API**: FastAPI server exposing the dashboard endpoints and PR endpoints on port `8000`.
3. **Backend Worker**: A background polling process that continuously orchestrates the multi-agent system.

## Requirements
- Docker
- Docker Compose

## Environment Variables
The system is configured securely out of the box with reasonable defaults.
You can modify behavior using standard environment variables:

- `NEXT_PUBLIC_API_URL`: (Frontend) The public URL of the backend (Default: `http://localhost:8000`)
- `POLL_INTERVAL_SECONDS`: (Worker) How frequently the autonomous agents poll sources in seconds (Default: `300` i.e. 5 minutes)
- `DATABASE_URL`: (Backend) Standard SQLAlchemy connection string (Default mapped to a persistent SQLite volume).

## Deployment

To build and start the entire stack in production mode:

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

### Checking Health
The backend provides a liveness and readiness probe:
- **Liveness**: `http://localhost:8000/api/healthz`
- **Readiness**: `http://localhost:8000/api/readiness` (Verifies DB connection)

### Database Persistence
The system uses SQLite for its Data Ledger. This is mapped via a Docker Volume (`civicos-data`) to ensure that data survives container restarts. The `init_db.py` script automatically runs on container boot to ensure schema migrations are applied idempotently without wiping existing data.

## Viewing Logs

**Backend API Logs:**
```bash
docker logs -f civicos-backend
```

**Agent Worker Logs (Trace autonomous behavior here):**
```bash
docker logs -f civicos-worker
```

**Frontend Logs:**
```bash
docker logs -f civicos-frontend
```
