import { proxyActivities, log } from '@temporalio/workflow';
import type { createDefaultActivities, createHostActivities } from './activities';

export const DEFAULT_TASK_QUEUE = 'file-processing-task-queue';

// Proxy for activities that run on any available worker.
const { download } = proxyActivities<ReturnType<typeof createDefaultActivities>>({
  taskQueue: DEFAULT_TASK_QUEUE,
  startToCloseTimeout: '5 minutes',
});

/**
 * Orchestrates the file-processing pipeline:
 *
 *  1. download  — runs on any worker; returns the local path and the
 *                 hostname of the worker that downloaded the file.
 *  2. process   — must run on the *same* host (file is on that disk).
 *  3. upload    — same host requirement.
 *
 * After download we know the host-specific task queue and create a second
 * proxy that targets it, pinning process and upload to the correct worker.
 */
export async function fileProcessingWorkflow(sourceUrl: string, destinationUrl: string): Promise<string> {
  // Step 1 — download on any available worker.
  const { hostTaskQueue, localPath } = await download(sourceUrl);
  log.info('File downloaded', { localPath, hostTaskQueue });

  // Steps 2 & 3 — target the exact host that holds the file.
  const { process, upload } = proxyActivities<ReturnType<typeof createHostActivities>>({
    taskQueue: hostTaskQueue,
    startToCloseTimeout: '5 minutes',
  });

  const processedPath = await process(localPath);
  log.info('File processed', { processedPath });

  await upload({ localPath: processedPath, destinationUrl });
  log.info('File uploaded', { destinationUrl });

  return 'OK';
}
