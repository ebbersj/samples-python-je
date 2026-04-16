import asyncio

from temporalio import workflow

TASK_QUEUE = "continue-as-new-task-queue"
WORKFLOW_ID = "looping-workflow"
MAX_ITERATIONS = 10


@workflow.defn
class LoopingWorkflow:
    @workflow.run
    async def run(self, iteration: int = 0) -> None:
        """
        Run one iteration of the loop.

        Args:
            iteration: The current iteration number (default 0 on first start).
        """
        if iteration >= MAX_ITERATIONS:
            workflow.logger.info(f"Reached max iterations ({MAX_ITERATIONS}). Done.")
            return

        workflow.logger.info(f"Running iteration {iteration} of {MAX_ITERATIONS}")

        # Simulate doing some work each iteration.
        await asyncio.sleep(1)

        # Continue as new: ends this execution and starts a fresh one with
        # an incremented iteration counter.
        workflow.continue_as_new(iteration + 1)
