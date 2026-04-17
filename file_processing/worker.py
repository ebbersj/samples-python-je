import asyncio
import logging
import socket

from temporalio.client import Client
from temporalio.worker import Worker

from activities import DEFAULT_TASK_QUEUE, download, process, upload
from workflows import FileProcessingWorkflow

# The host-specific task queue is simply this machine's hostname.
HOST_TASK_QUEUE = socket.gethostname()


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    client = await Client.connect("localhost:7233")

    # Worker 1 — handles workflows and the download activity (any host).
    default_worker = Worker(
        client,
        task_queue=DEFAULT_TASK_QUEUE,
        workflows=[FileProcessingWorkflow],
        activities=[download],
    )

    # Worker 2 — handles process and upload activities on this specific host.
    host_worker = Worker(
        client,
        task_queue=HOST_TASK_QUEUE,
        activities=[process, upload],
    )

    print(f"Default worker polling:    {DEFAULT_TASK_QUEUE!r}")
    print(f"Host worker polling:       {HOST_TASK_QUEUE!r}")
    print("Press Ctrl+C to stop.")

    # Run both workers concurrently.
    await asyncio.gather(default_worker.run(), host_worker.run())


if __name__ == "__main__":
    asyncio.run(main())
