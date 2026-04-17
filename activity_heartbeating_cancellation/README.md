# Activity Heartbeating & Cancellation (Python)

Demonstrates two closely related Temporal activity concepts:

**Heartbeating** — a long-running activity periodically calls `activity.heartbeat(progress)` to:
1. Prove to the Temporal server it is still alive (so the server won't time it out).
2. Checkpoint its progress so a retry after a crash can *resume* from the last checkpoint instead of starting over.

**Cancellation** — when the workflow is cancelled the server stops acknowledging heartbeats. The next `activity.heartbeat()` call raises `CancelledError`, giving the activity a chance to clean up before re-raising the error.

## Files

| File | Purpose |
|------|---------|
| `activities.py` | `fake_progress` activity — heartbeats progress 1–100, handles cancellation |
| `workflows.py` | `FakeProgressWorkflow` — runs the activity with a heartbeat timeout |
| `worker.py` | Starts a Temporal worker |
| `client.py` | Starts the workflow, waits 20 s, then cancels it |

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

3. In another terminal, start and cancel the workflow:
   ```bash
   python client.py
   ```

## Expected output

**Worker terminal** — shows progress ticking up, then cancellation:

```
INFO  Starting activity at progress: 1
INFO  Progress: 1%
INFO  Progress: 2%
...
INFO  Progress: 20%
INFO  Activity cancelled at progress: 21%
INFO  Workflow cancelled along with its activity
```

**Client terminal**:

```
Started workflow: id='fake-progress-workflow', run_id='...'
Waiting 20s before cancelling…
Cancel request sent.
Workflow was cancelled successfully — the activity cleaned up first.
```

## How heartbeat resumption works

Stop the worker mid-run (`Ctrl+C`), then restart it. The activity will log
`Starting activity at progress: N` where `N` is the last heartbeated value —
not 1 — demonstrating that progress is preserved across retries.
