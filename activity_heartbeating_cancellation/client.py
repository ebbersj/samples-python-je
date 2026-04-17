import asyncio
import logging

from temporalio.client import Client, WorkflowFailureError
from temporalio.exceptions import CancelledError

from activities import TASK_QUEUE
from workflows import FakeProgressWorkflow

WORKFLOW_ID = "fake-progress-workflow"
# How long to let the workflow run before we cancel it.
SECONDS_BEFORE_CANCEL = 20


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    client = await Client.connect("localhost:7233")

    # Start the workflow without waiting for it to finish.
    handle = await client.start_workflow(
        FakeProgressWorkflow.run,
        id=WORKFLOW_ID,
        task_queue=TASK_QUEUE,
    )
    print(f"Started workflow: id={WORKFLOW_ID!r}, run_id={handle.result_run_id!r}")

    # Let the activity make some progress, then cancel the workflow.
    print(f"Waiting {SECONDS_BEFORE_CANCEL}s before cancelling…")
    await asyncio.sleep(SECONDS_BEFORE_CANCEL)

    await handle.cancel()
    print("Cancel request sent.")

    # Wait for the workflow to finish and surface the cancellation.
    try:
        await handle.result()
    except WorkflowFailureError as e:
        if isinstance(e.__cause__, CancelledError):
            print("Workflow was cancelled successfully — the activity cleaned up first.")
        else:
            raise


if __name__ == "__main__":
    asyncio.run(main())
