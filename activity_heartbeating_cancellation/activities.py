import time

from temporalio import activity
from temporalio.exceptions import CancelledError

TASK_QUEUE = "activity-heartbeating-cancellation-task-queue"


@activity.defn
def fake_progress(sleep_interval_seconds: float = 1.0) -> None:
    """
    Simulates long-running work that reports progress from 1 to 100.

    On retry the activity resumes from the last heartbeated progress value
    instead of restarting at 1.
    """
    info = activity.info()

    # Resume from the last checkpoint when the activity is being retried.
    start = int(info.heartbeat_details[0]) if info.heartbeat_details else 1

    activity.logger.info(f"Starting activity at progress: {start}%")

    try:
        for progress in range(start, 101):
            # Do one unit of work (represented here as a short sleep).
            time.sleep(sleep_interval_seconds)

            activity.logger.info(f"Progress: {progress}%")

            # Heartbeat two things in one call:
            #   - tells the server the activity is still alive
            #   - records the current progress so a retry can resume here
            # Raises CancelledError if the workflow has been cancelled.
            activity.heartbeat(progress)

    except CancelledError:
        activity.logger.info(f"Activity cancelled at progress: {progress}%")
        raise  # Must re-raise so Temporal records the cancellation

    activity.logger.info("Activity completed — 100% done")
