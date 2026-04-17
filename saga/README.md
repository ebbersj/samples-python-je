# Saga (Python)

Demonstrates the **Saga pattern** — a way to manage distributed transactions
across multiple services by pairing each forward step with a compensating
(rollback) action.

## The problem

Opening a bank account involves coordinating several independent services:

1. **Accounts service** — create the account record
2. **Post Office service** — register the customer's address
3. **Clients service** — link the customer's email
4. **Banking service** — attach a bank account

If step 4 fails after steps 2 and 3 have already succeeded, those changes need
to be undone. There is no distributed transaction spanning all four services, so
the workflow must explicitly call compensating activities to roll back.

## The solution

A **compensation list** is built up as each step succeeds. When a step fails,
the workflow runs every collected compensation in reverse order before
re-raising the error.

```
OpenAccountWorkflow
 │
 ├─ create_account()       ← fatal if this fails; no compensation needed
 │
 ├─ add_address()          ← registers compensation: clear_addresses()
 ├─ add_client()           ← registers compensation: remove_client()
 └─ add_bank_account()     ← FAILS (simulated)
      │
      └─ compensations run in reverse:
           ├─ remove_client()
           └─ clear_addresses()
```

## Files

| File | Purpose |
|------|---------|
| `activities.py` | Forward and compensating activity definitions |
| `workflows.py` | `OpenAccountWorkflow` — saga orchestration logic |
| `worker.py` | Starts the worker |
| `client.py` | Starts the workflow with sample data |

## Running the sample

### Prerequisites

- [Temporal CLI](https://docs.temporal.io/cli) installed
- Python 3.9+
- `temporalio` package (`pip install temporalio`)

### Steps

1. Start a local Temporal server:
   ```bash
   temporal server start-dev
   ```

2. In a new terminal, start the worker:
   ```bash
   python worker.py
   ```

3. In another terminal, run the client:
   ```bash
   python client.py
   ```

## Expected output

**Worker terminal** — you will see the forward steps followed by compensations:

```
INFO  Creating account '...'
INFO  Adding address '123 Temporal Street' to account '...'
INFO  Adding client 'bart@simpson.io' to account '...'
INFO  Linking bank account '...' to account '...'
ERROR Account setup failed: Bank account service is unavailable. Running compensations.
INFO  Compensating: remove client
INFO  [compensation] Removing client from account '...'
INFO  Compensating: clear addresses
INFO  [compensation] Clearing addresses for account '...'
```

**Client terminal**:

```
Starting OpenAccountWorkflow for account '...'
Workflow failed (expected): ...
Check the worker logs to see the compensation steps that ran.
```

The `add_bank_account` activity always raises an exception to demonstrate the
compensation flow. Remove the `raise` in `activities.py` to see a successful run.
