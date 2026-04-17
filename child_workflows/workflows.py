import asyncio
from typing import List

from temporalio import workflow

TASK_QUEUE = "child-workflows-task-queue"


@workflow.defn
class ChildWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        workflow.logger.info(f"Child workflow running for: {name}")
        return f"I am a child named {name}"


@workflow.defn
class ParentWorkflow:
    @workflow.run
    async def run(self, names: List[str]) -> str:
        workflow.logger.info(f"Parent workflow starting {len(names)} child workflow(s)")

        # Start all child workflows concurrently and wait for every one to
        # finish.  Each child gets a unique workflow ID derived from the name.
        results = await asyncio.gather(
            *[
                workflow.execute_child_workflow(
                    ChildWorkflow.run,
                    name,
                    id=f"child-workflow-{name.lower()}",
                )
                for name in names
            ]
        )

        workflow.logger.info("All child workflows completed")
        return "\n".join(results)
