"""
Client

Starts an OpenAccountWorkflow and waits for it to complete.

The workflow intentionally fails at the "add bank account" step to demonstrate
that previously completed steps (add address, add client) are rolled back via
compensating activities.
"""

import asyncio
import logging
import uuid

from temporalio.client import Client

from activities import TASK_QUEUE, BankDetails, PostalAddress
from workflows import OpenAccountInput, OpenAccountWorkflow


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    client = await Client.connect("localhost:7233")

    account_id = str(uuid.uuid4())

    input = OpenAccountInput(
        account_id=account_id,
        client_email="bart@simpson.io",
        address=PostalAddress(
            address1="123 Temporal Street",
            postal_code="98006",
        ),
        bank_details=BankDetails(
            account_number="9876543210",
            routing_number="021000021",
            account_type="Checking",
            owner_name="Bart Simpson",
        ),
    )

    print(f"Starting OpenAccountWorkflow for account {account_id!r}")

    try:
        await client.execute_workflow(
            OpenAccountWorkflow.run,
            input,
            id=f"saga-{account_id}",
            task_queue=TASK_QUEUE,
        )
        print("Workflow completed successfully.")
    except Exception as err:
        print(f"Workflow failed (expected): {err}")
        print("Check the worker logs to see the compensation steps that ran.")


if __name__ == "__main__":
    asyncio.run(main())
