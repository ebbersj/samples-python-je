# Continue-as-New (Python)

Demonstrates Temporal's [Continue-as-New](https://docs.temporal.io/develop/python/continue-as-new) API.

When a workflow calls `workflow.continue_as_new(...)`, Temporal closes the current
execution and immediately starts a brand-new execution of the same workflow with the
provided arguments. The new execution gets a fresh, empty event history — preventing
unbounded history growth in long-running or infinite workflows.

## Files

| File | Purpose |
|------|---------|
| `workflows.py` | Workflow definition — contains the looping logic and continue-as-new call |
| `worker.py` | Starts a Temporal worker that polls for and executes workflow tasks |
| `client.py` | Starts the workflow and waits for it to complete |

## Running the sample

### Prerequisites

- [Temporal CLI](https://docs.temporal.io/cli) installed
- Python 3.9+
- `temporalio` package installed (`pip install temporalio`)

### Steps

1. Start a local Temporal development server:
   ```bash
   temporal server start-dev
   ```

2. In a new terminal, start the worker:
   ```bash
   python worker.py
   ```

3. In another terminal, start the workflow:
   ```bash
   python client.py
   ```

## Expected output

The worker will log each iteration as it runs:

```
INFO  Running iteration 0 of 10
INFO  Running iteration 1 of 10
...
INFO  Running iteration 9 of 10
INFO  Reached max iterations (10). Done.
```

In the [Temporal Web UI](http://localhost:8233), you will see 10 completed workflow
executions all sharing the same Workflow ID (`looping-workflow`) but with
`ContinuedAsNew` status on the first 9 and `Completed` on the final one.
