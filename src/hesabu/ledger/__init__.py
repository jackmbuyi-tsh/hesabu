"""The Hesabu ledger. Not built yet: this package is where the core goes.

Invariants it must keep, under concurrent writes and kill -9 crashes:

1. Money is never created or destroyed: the sum of all balances is zero.
2. A transaction is never applied twice.
3. A confirmed write is never lost after a crash.
4. Customer and wallet accounts never go negative. System accounts
   (provider clearing, external) may.

Bar before any gateway work: the sequential-replay match and the
kill-point crash tests pass on PostgreSQL.
"""
