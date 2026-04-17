# Child Workflows (Python)

Demonstrates how to start child workflows from a parent workflow, including
running multiple children **in parallel**.

## How it works

`ParentWorkflow` receives a list of names. For each name it calls
`workflow.execute_child_workflow(ChildWorkflow.run, name, ...)` and wraps all
of those calls in `asyncio.gather()` so every child workflow runs concurrently.
Once all children complete, the parent joins their results and returns.

```
ParentWorkflow
├── ChildWorkflow (Alice)  ─┐
├── ChildWorkflow (Bob)    ─┼─ run in parallel
└── ChildWorkflow (Charlie)─┘
```

## Files

| File | Purpose |
|------|---------|
| `workflows.py` | `ChildWorkflow` and `ParentWorkflow` definitions |
| `worker.py` | Starts a Temporal worker — registers both workflows |
| `client.py` | Starts `ParentWorkflow` and prints the results |

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

3. In another terminal, run the workflow:
   ```bash
   python client.py
   ```

## Expected output

```
Starting parent workflow with names: ['Alice', 'Bob', 'Charlie']
Result:
I am a child named Alice
I am a child named Bob
I am a child named Charlie
```

In the [Temporal Web UI](http://localhost:8233) you will see four workflow
executions: one `ParentWorkflow` and one `ChildWorkflow` per name, each with
its own run ID. The parent's event history will contain `ChildWorkflowExecutionStarted`
and `ChildWorkflowExecutionCompleted` events linking them together.
