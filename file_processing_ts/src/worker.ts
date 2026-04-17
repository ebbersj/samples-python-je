import { Worker } from '@temporalio/worker';
import { createDefaultActivities, createHostActivities } from './activities';
import { DEFAULT_TASK_QUEUE } from './workflows';
import * as os from 'os';

/**
 * Starts two workers:
 *
 *  1. Default worker  — polls DEFAULT_TASK_QUEUE; handles the workflow and
 *                       the `download` activity (any host can download).
 *
 *  2. Host worker     — polls a queue named after this machine's hostname;
 *                       handles `process` and `upload` (needs the local file).
 *
 * Using the hostname as the host-specific task queue name is what ties the
 * process and upload activities to the machine that ran the download.
 */
async function run() {
  const hostTaskQueue = os.hostname();

  const [defaultWorker, hostWorker] = await Promise.all([
    Worker.create({
      workflowsPath: require.resolve('./workflows'),
      activities: createDefaultActivities(),
      taskQueue: DEFAULT_TASK_QUEUE,
    }),
    Worker.create({
      activities: createHostActivities(),
      taskQueue: hostTaskQueue,
    }),
  ]);

  console.log(`Default worker polling: ${DEFAULT_TASK_QUEUE}`);
  console.log(`Host worker polling:    ${hostTaskQueue}`);
  console.log('Press Ctrl+C to stop.');

  await Promise.all([defaultWorker.run(), hostWorker.run()]);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
