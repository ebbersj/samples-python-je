import asyncio
import logging

from temporalio.client import Client

from workflows import TASK_QUEUE, ParentWorkflow

WORKFLOW_ID = "parent-workflow"
NAMES = ["Alice", "Bob", "Charlie"]


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    client = await Client.connect("localhost:7233")

    print(f"Starting parent workflow with names: {NAMES}")

    result = await client.execute_workflow(
        ParentWorkflow.run,
        NAMES,
        id=WORKFLOW_ID,
        task_queue=TASK_QUEUE,
    )

    print("Result:")
    print(result)
    # I am a child named Alice
    # I am a child named Bob
    # I am a child named Charlie


if __name__ == "__main__":
    asyncio.run(main())
