import { log } from '@temporalio/activity';
import * as fs from 'fs/promises';
import * as os from 'os';
import * as path from 'path';

export interface DownloadResult {
  /** The host-specific task queue (hostname) where the file was downloaded. */
  hostTaskQueue: string;
  /** The local path of the downloaded file. */
  localPath: string;
}

export interface UploadInput {
  localPath: string;
  destinationUrl: string;
}

/**
 * Activities that can run on any worker (no local file dependency).
 */
export function createDefaultActivities() {
  return {
    /**
     * Download a file from sourceUrl to a temporary local file.
     *
     * Returns the local path and this worker's hostname so the workflow can
     * pin the next activities to the same host.
     */
    async download(sourceUrl: string): Promise<DownloadResult> {
      log.info('Downloading file', { sourceUrl });

      const response = await fetch(sourceUrl);
      const content = await response.text();

      const localPath = path.join(os.tmpdir(), `temporal-${Date.now()}.tmp`);
      await fs.writeFile(localPath, content, 'utf8');

      log.info('Download complete', { sourceUrl, localPath });

      // Return the hostname so the workflow knows which task queue (host) to
      // target for the process and upload activities.
      return { hostTaskQueue: os.hostname(), localPath };
    },
  };
}

/**
 * Activities that must run on the same host that downloaded the file,
 * because they operate on the local filesystem.
 */
export function createHostActivities() {
  return {
    /**
     * Process the downloaded file.
     *
     * In a real scenario this might compress, transcode, or analyse the file.
     * Here we append a small metadata footer as a stand-in for real work.
     */
    async process(localPath: string): Promise<string> {
      const stat = await fs.stat(localPath);
      log.info('Processing file', { localPath, bytes: stat.size });

      await fs.appendFile(localPath, '\n-- processed --\n', 'utf8');

      log.info('Processing complete', { localPath });
      return localPath;
    },

    /**
     * Upload the processed file to the destination.
     *
     * Simulated here; swap in a real HTTP PUT or cloud SDK call for production.
     */
    async upload({ localPath, destinationUrl }: UploadInput): Promise<void> {
      const stat = await fs.stat(localPath);
      log.info('Uploading file', { localPath, bytes: stat.size, destinationUrl });

      // Replace with real upload logic (e.g. fetch PUT, AWS S3 putObject, etc.)
      log.info('Upload complete', { localPath, destinationUrl });

      // Clean up the temp file now that it has been "uploaded".
      await fs.rm(localPath, { force: true });
    },
  };
}
