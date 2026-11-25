# Hesabu

*Hesabu* is Swahili for "accounts" or "calculation".

Hesabu is a double-entry ledger that must stay exact under concurrent writes
and `kill -9` crashes. Mobile-money providers (M-Pesa, Orange Money, Airtel
Money) will feed it through a thin gateway; the ledger is the core. Its first
intended consumer is Uzuritech, a multi-tenant platform for schools and hotels
in the DR Congo.

> **Status:** early scaffolding. The ledger is not built yet. A first version
> of the gateway exists: payments can be created and read against mock
> providers.

## The invariants

The ledger must never:

1. create or destroy money (the sum of all balances stays zero),
2. apply the same transaction twice,
3. lose a confirmed write after a crash,
4. let a customer or wallet account go negative (system accounts, such as
   provider clearing and external accounts, may).

## How it will be checked

- Concurrent stress tests: thousands of transfers in parallel; total money is
  conserved and no customer or wallet balance goes negative.
- Crash tests: the ledger runs in a separate process, is killed with `kill -9`
  at chosen points during a write, restarts, and must still be consistent.
- Reference result: replaying the whole transaction log one transaction at a
  time must give exactly the balances the concurrent ledger produced.
- A benchmark of throughput and latency at the target load: a few hundred
  accounts, 20–50 concurrent transfers, a few hundred operations per second.

The write path and crash recovery come first. The replay match and the
kill-point tests are the bar before more gateway work.

## Layout

| Path | Contents |
|---|---|
| `src/hesabu/ledger/` | The ledger. Empty for now, apart from its invariants |
| `src/hesabu/gateway/status.py` | Payment lifecycle: `pending` → `succeeded` / `failed` / `expired` |
| `src/hesabu/gateway/models.py` | `Payment` table, providers, currencies (USD, CDF) |
| `src/hesabu/gateway/providers/` | Provider adapter interface and a minimal mock adapter |
| `src/hesabu/api/main.py` | FastAPI app: `GET /health`, `POST /payments`, `GET /payments/{id}` |
| `tests/` | Gateway API and status-transition tests |

## Why mock providers

Real provider APIs need merchant accounts and sandbox credentials, and the
build machine has no internet. Providers sit behind one adapter interface
(`hesabu.gateway.providers.ProviderAdapter`), so mock adapters are used now
and real ones can be plugged in later.

## Stack

Python 3.12+, FastAPI, SQLAlchemy 2, PostgreSQL (psycopg 3), pytest.
Quick unit tests run on SQLite; concurrency and crash tests will run on
PostgreSQL.

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

createuser hesabu --pwprompt              # password: change-me
createdb hesabu --owner hesabu
export HESABU_DATABASE_URL="postgresql+psycopg://hesabu:change-me@127.0.0.1:5432/hesabu"

python -c "from hesabu.db import Base, engine; import hesabu.gateway.models; Base.metadata.create_all(engine)"
uvicorn hesabu.api.main:app --reload
```

API docs: http://127.0.0.1:8000/docs. Alembic migrations are not set up yet.

## Tests

```bash
pytest                                       # SQLite in memory
HESABU_TEST_DATABASE_URL="postgresql+psycopg://user:pass@127.0.0.1:5432/hesabu_test" pytest
```

## Licence

MIT. See [LICENSE](LICENSE).
