# Aegis Trace

AI Security Decision Auditor. Phase 1 connects React, FastAPI, and PostgreSQL. Phase 2 captures AI security decisions, stores exact proposed diffs, and verifies a hash-chained ledger. Replay and scoring are not implemented yet. The security decision lifecycle is designed in [docs/architecture.md](docs/architecture.md).

## Run the current stack

1. `cp .env.example .env` — creates local database settings; replace the example password before sharing a deployment. Expected: a new ignored `.env` file.
2. `docker compose up --build -d` — builds the UI and API, starts PostgreSQL, and applies Alembic migrations. Expected: three healthy/running services.
3. `docker compose ps` — confirms service state. Expected: `postgres`, `backend`, and `frontend` running; backend and postgres healthy.
4. `curl http://localhost:8000/api/status` — tests API-to-database communication. Expected: `{"api":"ready","database":"connected","phase":1}`.
5. Open `http://localhost:5173` — tests frontend-to-API communication. Expected: the AI Security Decisions list.

The page now opens the Decisions list. Use **Capture Decision** to submit the title, model, category, recommendation, unified diff, and relative affected file paths. A demo developer and model are created by the Phase 2 migration. The detail page shows stored evidence and ledger verification. `GET /api/ledger/verify` reports the integrity result; `GET /docs` shows the API contract.

## Tests and migrations

1. `docker compose exec backend alembic current` — shows the applied schema revision. Expected: `2a01_decision_capture`.
2. `python -m pip install -r backend/requirements-dev.txt` — installs backend test dependencies in your active virtual environment. Expected: pytest and httpx installed.
3. `PYTHONPATH=backend python -m pytest backend/tests -q` — checks capture validation and ledger tamper detection. Expected: seven passing tests.
4. `cd frontend` — enters the React project. Expected: shell working directory changes.
5. `npm ci` — installs the locked frontend dependencies. Expected: zero audit findings.
6. `npm test` — runs the Decision list and capture UI tests. Expected: two passing tests.
7. `npm run build` — checks TypeScript and bundles the UI. Expected: a successful Vite build.

`docker compose down` stops the services. Add `-v` only when deliberately deleting local database data.

## Phase sequence

1. Stack communication (complete).
2. Decision capture, migration, ledger verification, and list UI (complete).
3. Restricted Docker replay with Semgrep and Trivy.
4. Evidence-based initial score.
5. Day 30 simulation and outcome evidence.
6. Score history chart.
7. Decision history graph.
8. Security rules and deployment gate.

Security limitation: Phase 2 endpoints currently have no authentication or tenant isolation. Keep this local demo stack private until JWT/RBAC and organization scoped queries are implemented. The hash chain detects changed Decision evidence but does not prevent a privileged database administrator from rewriting the entire chain; external checkpoints are a later hardening step.
