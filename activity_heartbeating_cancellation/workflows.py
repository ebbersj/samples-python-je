from datetime import timedelta
from temporalio.exceptions import ActivityError, CancelledError
from temporalio import workflow
from temporalio.workflow import ActivityCancellationType

with workflow.unsafe.imports_passed_through():
    from activities import fake_progress


@workflow.defn
class FakeProgressWorkflow:
    @workflow.run
    async def run(self) -> None:
        try:
            await workflow.execute_activity(
                fake_progress,
                start_to_close_timeout=timedelta(minutes=5),
                # If the activity stops heartbeating for 3 s, mark it as failed.
                heartbeat_timeout=timedelta(seconds=3),
                # Wait for the activity to finish its cancellation handler
                # before closing the workflow.
                cancellation_type=ActivityCancellationType.WAIT_CANCELLATION_COMPLETED,
            )
        except ActivityError as e:
            # Check if the cause of the ActivityError was a cancellation
            if isinstance(e.__cause__, CancelledError):
                workflow.logger.info("Workflow cancelled along with its activity")
            
            # Re-raise the exception to Cancel the Workflow
            raise
        except Exception as e:
            raise
