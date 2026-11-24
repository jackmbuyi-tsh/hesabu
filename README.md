# mobile-money-gateway

A Python service that puts M-Pesa, Orange Money and Airtel Money behind one
API for businesses in the DR Congo: payment requests, provider callbacks,
idempotency (no double charges), reconciliation and a transaction ledger.
The first user will be [Uzuritech](https://uzuritech.com), a multi-tenant
platform for schools and hotels.

> **Status:** early scaffolding. Payments can be created and read through the
> API against mock providers. Callbacks, realistic provider simulation,
> reconciliation and the ledger are still to be built.

## Why mock providers

Real provider APIs need merchant accounts and sandbox credentials, and the
machine this is built on has no internet. Every provider sits behind one
adapter interface (`mmgateway.providers.ProviderAdapter`), so mock adapters
are used for development and tests, and real ones plug in later without
touching the rest of the code.

## What's here

| Path | Contents |
|---|---|
| `src/mmgateway/status.py` | Payment lifecycle: `pending` → `succeeded` / `failed` / `expired`, final statuses never change |
| `src/mmgateway/models.py` | `Payment` table (SQLAlchemy 2), providers and currencies (USD, CDF) |
| `src/mmgateway/providers/` | Adapter interface, a minimal mock adapter, and the registry |
| `src/mmgateway/api/main.py` | FastAPI app: `GET /health`, `POST /payments`, `GET /payments/{id}` |
| `tests/` | API and status-transition tests |

`POST /payments` requires an `Idempotency-Key` header. Sending the same key
again returns the first payment instead of creating a second one.

## Stack

Python 3.12+, FastAPI, SQLAlchemy 2, PostgreSQL (via psycopg 3), pytest.

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# PostgreSQL
createuser mmgateway --pwprompt          # password: change-me
createdb mmgateway --owner mmgateway
export MMG_DATABASE_URL="postgresql+psycopg://mmgateway:change-me@127.0.0.1:5432/mmgateway"

python -c "from mmgateway.db import Base, engine; import mmgateway.models; Base.metadata.create_all(engine)"
uvicorn mmgateway.api.main:app --reload
```

The interactive API docs are at http://127.0.0.1:8000/docs.

Database migrations (Alembic) are not set up yet; the command above creates
the tables directly.

## Tests

```bash
pytest                                      # SQLite in memory
MMG_TEST_DATABASE_URL="postgresql+psycopg://user:pass@127.0.0.1:5432/mmgateway_test" pytest
```

The second form runs the same tests on an empty PostgreSQL database.

## Licence

MIT. See [LICENSE](LICENSE).
