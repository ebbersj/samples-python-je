from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import DEFAULT_TASK_QUEUE, DownloadResult, UploadInput, download, process, upload


@workflow.defn
class FileProcessingWorkflow:
    @workflow.run
    async def run(self, source_url: str, destination_url: str) -> str:
        # Step 1 — download on any available worker.
        result: DownloadResult = await workflow.execute_activity(
            download,
            source_url,
            start_to_close_timeout=timedelta(minutes=5),
            task_queue=DEFAULT_TASK_QUEUE,
        )
        workflow.logger.info(
            f"File downloaded to {result.local_path} on worker {result.host_task_queue}"
        )

        # Steps 2 & 3 — pin to the host that holds the file by targeting its
        # unique task queue.
        host_queue = result.host_task_queue

        processed_path = await workflow.execute_activity(
            process,
            result.local_path,
            start_to_close_timeout=timedelta(minutes=5),
            task_queue=host_queue,
        )
        workflow.logger.info(f"File processed: {processed_path}")

        await workflow.execute_activity(
            upload,
            UploadInput(local_path=processed_path, destination_url=destination_url),
            start_to_close_timeout=timedelta(minutes=5),
            task_queue=host_queue,
        )
        workflow.logger.info(f"File uploaded to {destination_url}")

        return "OK"
