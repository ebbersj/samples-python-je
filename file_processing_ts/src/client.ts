import { Connection, Client } from '@temporalio/client';
import { loadClientConnectConfig } from '@temporalio/envconfig';
import { fileProcessingWorkflow, DEFAULT_TASK_QUEUE } from './workflows';

const SOURCE_URL = 'https://temporal.io/blog';
const DESTINATION_URL = 'https://example.com/upload';

async function run() {
  const config = loadClientConnectConfig();
  const connection = await Connection.connect(config.connectionOptions);
  const client = new Client({ connection });

  console.log(`Starting workflow: ${SOURCE_URL} → ${DESTINATION_URL}`);

  const result = await client.workflow.execute(fileProcessingWorkflow, {
    taskQueue: DEFAULT_TASK_QUEUE,
    workflowId: 'file-processing-workflow',
    args: [SOURCE_URL, DESTINATION_URL],
  });

  console.log(`Workflow completed with result: ${result}`);
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
