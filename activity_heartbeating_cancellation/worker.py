import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from temporalio.client import Client
from temporalio.worker import Worker

from activities import TASK_QUEUE, fake_progress
from workflows import FakeProgressWorkflow


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[FakeProgressWorkflow],
        activities=[fake_progress],
        activity_executor=ThreadPoolExecutor(max_workers=5),
    )

    print(f"Worker started, polling task queue: {TASK_QUEUE!r}")
    print("Press Ctrl+C to stop.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
