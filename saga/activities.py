from dataclasses import dataclass

from temporalio import activity
from temporalio.exceptions import ApplicationError

TASK_QUEUE = "saga-task-queue"


# --- Shared value types ---


@dataclass
class PostalAddress:
    address1: str
    postal_code: str


@dataclass
class BankDetails:
    account_number: str
    routing_number: str
    account_type: str
    owner_name: str


# --- Activity input types ---


@dataclass
class CreateAccountInput:
    account_id: str


@dataclass
class AddAddressInput:
    account_id: str
    address: PostalAddress


@dataclass
class AddClientInput:
    account_id: str
    client_email: str


@dataclass
class AddBankAccountInput:
    account_id: str
    details: BankDetails


@dataclass
class AccountIdInput:
    account_id: str


# --- Forward activities ---


@activity.defn
async def create_account(input: CreateAccountInput) -> None:
    activity.logger.info(f"Creating account {input.account_id!r}")


@activity.defn
async def add_address(input: AddAddressInput) -> None:
    activity.logger.info(
        f"Adding address {input.address.address1!r} to account {input.account_id!r}"
    )


@activity.defn
async def add_client(input: AddClientInput) -> None:
    activity.logger.info(
        f"Adding client {input.client_email!r} to account {input.account_id!r}"
    )


@activity.defn
async def add_bank_account(input: AddBankAccountInput) -> None:
    activity.logger.info(
        f"Linking bank account {input.details.account_number!r} to account {input.account_id!r}"
    )
    # Simulate a downstream service failure to demonstrate saga compensation.
    # non_retryable=True tells Temporal to fail immediately without retrying,
    # so the workflow can run compensations right away.
    raise ApplicationError("Bank account service is unavailable", non_retryable=True)


# --- Compensating activities (run in reverse order on failure) ---


@activity.defn
async def clear_addresses(input: AccountIdInput) -> None:
    activity.logger.info(f"[compensation] Clearing addresses for account {input.account_id!r}")


@activity.defn
async def remove_client(input: AccountIdInput) -> None:
    activity.logger.info(f"[compensation] Removing client from account {input.account_id!r}")


@activity.defn
async def disconnect_bank_accounts(input: AccountIdInput) -> None:
    activity.logger.info(
        f"[compensation] Disconnecting bank accounts for account {input.account_id!r}"
    )
