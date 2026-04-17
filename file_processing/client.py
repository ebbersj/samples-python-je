"""
Client

Starts a FileProcessingWorkflow execution and waits for it to complete.

Usage:
    python client.py <source_url> <destination_url>

Example:
    python client.py https://temporal.io/blog https://example.com/upload
"""

import asyncio
import logging
import sys

from temporalio.client import Client

from activities import DEFAULT_TASK_QUEUE
from workflows import FileProcessingWorkflow

WORKFLOW_ID = "file-processing-workflow"


async def main(source_url: str, destination_url: str) -> None:
    logging.basicConfig(level=logging.INFO)

    client = await Client.connect("localhost:7233")

    print(f"Starting workflow: {source_url!r} → {destination_url!r}")

    result = await client.execute_workflow(
        FileProcessingWorkflow.run,
        args=[source_url, destination_url],
        id=WORKFLOW_ID,
        task_queue=DEFAULT_TASK_QUEUE,
    )

    print(f"Workflow completed with result: {result!r}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python client.py <source_url> <destination_url>")
        sys.exit(1)

    asyncio.run(main(sys.argv[1], sys.argv[2]))
