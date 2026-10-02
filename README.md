# Aegis Trace

AI Security Decision Auditor. Phase 1 connects a React frontend, FastAPI backend, and PostgreSQL database. The security decision lifecycle is designed in [docs/architecture.md](docs/architecture.md); replay and scoring are not implemented yet.

## Run Phase 1

1. `cp .env.example .env` — creates local database settings; replace the example password before sharing a deployment. Expected: a new ignored `.env` file.
2. `docker compose up --build -d` — builds the UI and API, starts PostgreSQL, and applies the existing Alembic migration. Expected: three healthy/running services.
3. `docker compose ps` — confirms service state. Expected: `postgres`, `backend`, and `frontend` running; backend and postgres healthy.
4. `curl http://localhost:8000/api/status` — tests API-to-database communication. Expected: `{"api":"ready","database":"connected","phase":1}`.
5. Open `http://localhost:5173` — tests frontend-to-API communication. Expected: a green “API ready · PostgreSQL connected” message.

`docker compose down` stops the services. Add `-v` only when deliberately deleting local database data.

## Phase sequence

1. Stack communication (this branch).
2. Complete decision capture, migration, ledger verification, and list UI.
3. Restricted Docker replay with Semgrep and Trivy.
4. Evidence-based initial score.
5. Day 30 simulation and outcome evidence.
6. Score history chart.
7. Decision history graph.
8. Security rules and deployment gate.

The existing decision API is an incomplete scaffold; it is not part of the Phase 1 verification path.
