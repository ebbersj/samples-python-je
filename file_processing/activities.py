import socket
import ssl
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from temporalio import activity

# The shared task queue any worker can pick up.
DEFAULT_TASK_QUEUE = "file-processing-task-queue"


@dataclass
class DownloadResult:
    """Carries the host-specific task queue and the local path of the downloaded file."""

    host_task_queue: str
    local_path: str


@dataclass
class UploadInput:
    """Input for the upload activity."""

    local_path: str
    destination_url: str


@activity.defn
async def download(source_url: str) -> DownloadResult:
    """
    Download a file from source_url to a temporary local file.

    Returns the path and the task queue name for *this* worker so the workflow
    can pin the next activities to the same host.
    """
    activity.logger.info(f"Downloading {source_url}")

    # NOTE: SSL verification is disabled here for convenience and should not be used in production.
    # In production, remove the ssl_context argument to enforce certificate validation.
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(source_url, context=ssl_context) as response:
        content = response.read()

    # Write to a named temp file that persists after this function returns.
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".tmp")
    tmp.write(content)
    tmp.close()

    activity.logger.info(f"Downloaded {source_url} → {tmp.name}")

    # Tell the workflow which task queue (i.e. which host) now holds the file.
    host_task_queue = socket.gethostname()
    return DownloadResult(host_task_queue=host_task_queue, local_path=tmp.name)


@activity.defn
async def process(local_path: str) -> str:
    """
    Process the downloaded file.

    In a real scenario this might compress, transcode, or analyse the file.
    Here we simply count its bytes as a stand-in for real work and return the
    (unchanged) path so the upload activity knows where to find it.
    """
    path = Path(local_path)
    size = path.stat().st_size
    activity.logger.info(f"Processing {local_path} ({size} bytes)")

    # Simulate processing by appending a small metadata footer.
    with open(local_path, "ab") as f:
        f.write(b"\n-- processed --\n")

    activity.logger.info(f"Processing complete: {local_path}")
    return local_path


@activity.defn
async def upload(input: UploadInput) -> None:
    """
    Upload the processed file to the destination.

    Here we simulate the upload by logging the action; swap in a real HTTP PUT
    or cloud SDK call for production use.
    """
    path = Path(input.local_path)
    size = path.stat().st_size
    activity.logger.info(f"Uploading {input.local_path} ({size} bytes) → {input.destination_url}")

    # Simulate upload delay / work.
    # (Replace with actual upload logic, e.g. boto3 / requests.)
    activity.logger.info(f"Upload complete: {input.local_path} → {input.destination_url}")

    # Clean up the temporary file now that it has been "uploaded".
    path.unlink(missing_ok=True)
