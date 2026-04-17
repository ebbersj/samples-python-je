from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import (
        AccountIdInput,
        AddAddressInput,
        AddBankAccountInput,
        AddClientInput,
        BankDetails,
        CreateAccountInput,
        PostalAddress,
        add_address,
        add_bank_account,
        add_client,
        clear_addresses,
        create_account,
        disconnect_bank_accounts,
        remove_client,
    )

# (description, activity_function, activity_input)
Compensation = tuple[str, Any, Any]

ACTIVITY_TIMEOUT = timedelta(seconds=10)


@dataclass
class OpenAccountInput:
    account_id: str
    client_email: str
    address: PostalAddress
    bank_details: BankDetails


@workflow.defn
class OpenAccountWorkflow:
    @workflow.run
    async def run(self, input: OpenAccountInput) -> None:
        compensations: list[Compensation] = []

        # Step 1: Create the account.
        # This is a prerequisite — if it fails we stop immediately with no compensations.
        await workflow.execute_activity(
            create_account,
            CreateAccountInput(account_id=input.account_id),
            start_to_close_timeout=ACTIVITY_TIMEOUT,
        )

        # Steps 2-4: Each step registers a compensating action before moving on.
        # If any step fails, the compensations collected so far run in reverse order.
        try:
            # Step 2: Add the postal address.
            await workflow.execute_activity(
                add_address,
                AddAddressInput(account_id=input.account_id, address=input.address),
                start_to_close_timeout=ACTIVITY_TIMEOUT,
            )
            compensations.insert(
                0, ("clear addresses", clear_addresses, AccountIdInput(input.account_id))
            )

            # Step 3: Register the client.
            await workflow.execute_activity(
                add_client,
                AddClientInput(account_id=input.account_id, client_email=input.client_email),
                start_to_close_timeout=ACTIVITY_TIMEOUT,
            )
            compensations.insert(
                0, ("remove client", remove_client, AccountIdInput(input.account_id))
            )

            # Step 4: Link a bank account.
            await workflow.execute_activity(
                add_bank_account,
                AddBankAccountInput(account_id=input.account_id, details=input.bank_details),
                start_to_close_timeout=ACTIVITY_TIMEOUT,
            )
            compensations.insert(
                0,
                (
                    "disconnect bank accounts",
                    disconnect_bank_accounts,
                    AccountIdInput(input.account_id),
                ),
            )

        except Exception as err:
            workflow.logger.error(f"Account setup failed: {err}. Running compensations.")
            await _compensate(compensations)
            raise


async def _compensate(compensations: list[Compensation]) -> None:
    """Run each compensation in order (which is reverse of the original steps)."""
    for description, activity_fn, activity_input in compensations:
        try:
            workflow.logger.info(f"Compensating: {description}")
            await workflow.execute_activity(
                activity_fn,
                activity_input,
                start_to_close_timeout=ACTIVITY_TIMEOUT,
            )
        except Exception as err:
            # Log and continue — a failed compensation should not block the others.
            workflow.logger.error(f"Compensation '{description}' failed: {err} — continuing")
