import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from activities import (
    TASK_QUEUE,
    add_address,
    add_bank_account,
    add_client,
    clear_addresses,
    create_account,
    disconnect_bank_accounts,
    remove_client,
)
from workflows import OpenAccountWorkflow


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[OpenAccountWorkflow],
        activities=[
            create_account,
            add_address,
            add_client,
            add_bank_account,
            clear_addresses,
            remove_client,
            disconnect_bank_accounts,
        ],
    )

    print(f"Worker polling on task queue: {TASK_QUEUE!r}")
    print("Press Ctrl+C to stop.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
