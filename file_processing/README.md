# File Processing (Python)

Demonstrates **task routing** — directing specific activities to a particular
worker host using a host-specific task queue.

## The problem

A file-processing pipeline has three steps:

1. **Download** — fetch a file from a URL and save it to the worker's local disk.
2. **Process**  — transform the file (e.g. compress, transcode, hash).
3. **Upload**   — send the processed file to a destination.

Steps 2 and 3 *must* run on the same machine as step 1, because the file only
exists on that host's filesystem.

## The solution

Each worker registers **two task queues**:

| Task queue | Who uses it | Activities |
|---|---|---|
| `file-processing-task-queue` | any worker | workflow + `download` |
| `<hostname>` | only this host | `process` + `upload` |

After `download` completes it returns the **hostname** of the machine it ran
on. The workflow uses that hostname as the task queue name for `process` and
`upload`, which pins those activities to the correct host.

```
Workflow
 │
 ├─ download(url)  ──→ any worker on DEFAULT_TASK_QUEUE
 │                         returns: { host_task_queue, local_path }
 │
 ├─ process(path)  ──→ pinned to host_task_queue
 │
 └─ upload(path)   ──→ pinned to host_task_queue
```

## Files

| File | Purpose |
|------|---------|
| `activities.py` | `download`, `process`, `upload` activity definitions |
| `workflows.py` | `FileProcessingWorkflow` — orchestrates the three activities |
| `worker.py` | Starts the default worker and the host-specific worker |
| `client.py` | Starts the workflow with a source URL and destination URL |

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
   python client.py https://temporal.io/blog https://example.com/upload
   ```

## Expected output

**Worker terminal**:
```
Default worker polling:    'file-processing-task-queue'
Host worker polling:       'my-hostname'
INFO  Downloading https://temporal.io/blog
INFO  Downloaded https://temporal.io/blog → /tmp/tmp1a2b3c.tmp
INFO  Processing /tmp/tmp1a2b3c.tmp (12345 bytes)
INFO  Processing complete: /tmp/tmp1a2b3c.tmp
INFO  Uploading /tmp/tmp1a2b3c.tmp → https://example.com/upload
INFO  Upload complete
```

**Client terminal**:
```
Starting workflow: 'https://temporal.io/blog' → 'https://example.com/upload'
Workflow completed with result: 'OK'
```
