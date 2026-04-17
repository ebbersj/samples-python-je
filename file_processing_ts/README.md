# File Processing (TypeScript)

Demonstrates **task routing** — directing specific activities to a particular
worker host using a host-specific task queue.

## The problem

A file-processing pipeline has three steps:

1. **download** — fetch a file from a URL and save it to the worker's local disk.
2. **process**  — transform the file (e.g. compress, transcode, hash).
3. **upload**   — send the processed file to a destination.

Steps 2 and 3 *must* run on the same machine as step 1, because the file only
exists on that host's filesystem.

## The solution

Each worker registers **two task queues**:

| Task queue | Who uses it | Activities |
|---|---|---|
| `file-processing-task-queue` | any worker | workflow + `download` |
| `<hostname>` | only this host | `process` + `upload` |

After `download` completes it returns the **hostname** of the worker it ran on.
The workflow creates a second activity proxy targeting that hostname as the task
queue, which pins `process` and `upload` to the correct host.

```
fileProcessingWorkflow
 │
 ├─ download(url)  ──→ any worker on DEFAULT_TASK_QUEUE
 │                         returns: { hostTaskQueue, localPath }
 │
 ├─ process(path)  ──→ pinned to hostTaskQueue
 │
 └─ upload(input)  ──→ pinned to hostTaskQueue
```

## Files

| File | Purpose |
|------|---------|
| `src/activities.ts` | `download`, `process`, `upload` activity definitions |
| `src/workflows.ts` | `fileProcessingWorkflow` — orchestrates the three activities |
| `src/worker.ts` | Starts the default worker and the host-specific worker |
| `src/client.ts` | Starts the workflow with a source URL and destination URL |

## Running the sample

### Prerequisites

- [Temporal CLI](https://docs.temporal.io/cli) installed
- Node.js 18+
- `npm install` to install dependencies

### Steps

1. Start a local Temporal server:
   ```bash
   temporal server start-dev
   ```

2. In a new terminal, install dependencies and start the worker:
   ```bash
   npm install
   npm run start
   ```

3. In another terminal, run the workflow:
   ```bash
   npm run workflow
   ```

## Expected output

**Worker terminal**:
```
Default worker polling: file-processing-task-queue
Host worker polling:    my-hostname
info  Downloading file  { sourceUrl: 'https://temporal.io/blog' }
info  Download complete { sourceUrl: '...', localPath: '/tmp/temporal-....tmp' }
info  Processing file   { localPath: '/tmp/temporal-....tmp', bytes: 12345 }
info  Processing complete
info  Uploading file    { localPath: '...', destinationUrl: 'https://example.com/upload' }
info  Upload complete
```

**Client terminal**:
```
Starting workflow: https://temporal.io/blog → https://example.com/upload
Workflow completed with result: OK
```
