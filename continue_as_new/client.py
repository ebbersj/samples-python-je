import asyncio
import logging

from temporalio.client import Client

from workflows import TASK_QUEUE, WORKFLOW_ID, LoopingWorkflow


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    client = await Client.connect("localhost:7233")

    print(f"Starting workflow: id={WORKFLOW_ID!r}, task_queue={TASK_QUEUE!r}")

    await client.execute_workflow(
        LoopingWorkflow.run,
        0,  # start at iteration 0
        id=WORKFLOW_ID,
        task_queue=TASK_QUEUE,
    )

    print("Workflow completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
