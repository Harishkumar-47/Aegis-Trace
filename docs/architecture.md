# Aegis Trace MVP architecture

## Folder structure

```text
backend/
  app/api/             HTTP routes
  app/core/            configuration
  app/db/              database sessions
  app/models/          SQLAlchemy tables
  app/schemas/         Pydantic contracts
  app/services/        ledger and application logic
  app/sandbox/         isolated replay (Phase 3)
  app/scoring/         evidence-based score (Phase 4)
  app/monitoring/      outcome checks (Phase 5)
  alembic/             database migrations
frontend/src/
  components/          shared UI
  pages/               dashboard and decision view
  services/            typed API client
  hooks/               data loading
  types/               API types
sandbox/templates/     controlled replay inputs
demo/vulnerable-app/   demonstration fixture
docs/                  design and contracts
docker-compose.yml     local stack
```

Phase 1 uses `frontend -> backend -> PostgreSQL`. The API checks PostgreSQL through `GET /api/status`. Later phases add a replay worker that applies a submitted unified diff only inside a restricted Docker container, runs Semgrep and Trivy, persists scanner evidence, and computes a score from that evidence. Checkpoints append later evidence and a new score. A policy compares the latest score with allow and block thresholds. The UI reads all results from the API.

The backend must never execute a submitted diff on the host. Replay requires container isolation, no privileged mode, a non-root user, CPU and memory limits, disabled network by default, a timeout, and cleanup. The Docker daemon is powerful; its access must be limited to the replay service in a later phase.

## PostgreSQL schema

All primary keys are UUIDs. Existing migration `9d4e60fb7c76` creates `users`, `ai_models`, and `decisions`. The next decision migration must store the submitted prompt and diff content or immutable artifact references, affected files, and organization ownership. `decisions` carries `prev_hash` and `row_hash`; verification must recompute the chain. Hashes detect changes but cannot prevent a database administrator from rewriting the whole chain, so external checkpoints are needed for stronger assurance.

| Table | Key fields | Purpose |
| --- | --- | --- |
| organizations | id, name | Tenant and policy owner |
| users | id, org_id, email, role | Admin, Developer, Auditor, Viewer |
| ai_models | id, provider, model_name, version | Origin of recommendation |
| decisions | id, org_id, user_id, model_id, category, prompt, recommendation, diff, affected_files, created_at, prev_hash, row_hash | Immutable decision capture |
| decision_variants | id, decision_id, model_id, diff | Later multi-model work |
| sandbox_runs | id, decision_id, status, started_at, finished_at, scanner_evidence | Replay evidence |
| trust_scores | id, decision_id, sandbox_run_id, outcome_check_id, score, factors, created_at | Append-only score history |
| outcome_checks | id, decision_id, checkpoint_day, evidence, checked_at | Day 7/30/90 evidence |
| lineage_edges | id, decision_id, source_id, target_id, event_type, detail | History graph |
| policies | id, org_id, allow_min, warn_min | Gate thresholds |
| alerts | id, decision_id, severity, source, evidence | Later security events |
| compliance_tags | id, decision_id, tag | Later mapping |

Foreign keys connect decisions to user/model/org; replay, score, checkpoint, lineage, and alert rows to decisions. Use organization scoped queries and indexes on decision timestamps and foreign keys. Password hashes and JWT signing secrets belong in protected configuration, never source code.

## API contracts

Current Phase 1 endpoint: `GET /api/status -> {"api":"ready","database":"connected","phase":1}`. `GET /health` only confirms the API process. Existing decision creation and detail routes are partial; they require existing user/model IDs and do not yet capture a real diff.

| Later endpoint | Request | Response |
| --- | --- | --- |
| POST /api/decisions | model, developer, prompt, recommendation, unified diff, affected files, category | decision ID and captured record |
| GET /api/decisions | optional filters and page | decision summaries |
| GET /api/decisions/{id} | path ID | decision and latest evidence |
| POST /api/decisions/{id}/replay | path ID | sandbox run ID/status |
| GET /api/decisions/{id}/scores | path ID | ordered score/factor history |
| POST /api/decisions/{id}/checkpoint | `{"day":30}` | appended evidence and new score |
| GET /api/decisions/{id}/lineage | path ID | nodes and edges |
| POST /api/policies | allow/warn thresholds | policy record |
| POST /api/ci/gate-check | decision ID | score, ALLOW/WARN/BLOCK, reason |

All mutation endpoints will require JWT and role checks. The score is named **Evidence-Based Trust Score** and always includes factors and source evidence. It is a risk signal, never proof of safety. OSV/CVE feeds, ZAP, Wazuh, multi-model comparison, and integrations follow the working MVP.
