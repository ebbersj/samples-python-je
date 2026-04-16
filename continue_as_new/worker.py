import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from workflows import TASK_QUEUE, LoopingWorkflow


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[LoopingWorkflow],
    )

    print(f"Worker started, polling task queue: {TASK_QUEUE!r}")
    print("Press Ctrl+C to stop.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
