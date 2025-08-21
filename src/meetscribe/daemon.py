import daemon
import lockfile
import logging
import time
import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import asyncio
from .config import CONFIG, CONFIG_DIR
from .audio import get_silence_percentage, get_audio_duration_seconds
from .processing import process_single_file

# --- Daemon Configuration ---
PID_FILE = CONFIG_DIR / "meetscribe_daemon.pid"
LOG_FILE = CONFIG_DIR / "meetscribe_daemon.log"
DAEMON_CONFIG = CONFIG.get('daemon', {})

# --- Logging Setup ---
def setup_logging():
    """Sets up logging for the daemon."""
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    # Also log to console for visibility when not detached
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

# --- File Handler for Watchdog ---
class NewFileHandler(FileSystemEventHandler):
    """Handles new file events from watchdog."""
    def on_created(self, event):
        if not event.is_directory:
            logging.info(f"New file detected: {event.src_path}")
            process_file(Path(event.src_path))

def process_file(filepath: Path):
    """
    Validates and processes a single audio file based on daemon config.
    """
    logging.info(f"Starting to process {filepath.name}")

    # 1. Check format
    if filepath.suffix not in DAEMON_CONFIG.get('supported_formats', []):
        logging.warning(f"Skipping {filepath.name}: Unsupported format '{filepath.suffix}'")
        return

    # 2. Check duration
    max_hours = DAEMON_CONFIG.get('max_duration_hours', 1.0)
    duration_secs = get_audio_duration_seconds(filepath)
    if duration_secs > max_hours * 3600:
        logging.warning(f"Skipping {filepath.name}: Exceeds max duration of {max_hours}h.")
        return

    # 3. Check silence
    max_silence = DAEMON_CONFIG.get('max_silence_percentage', 30.0)
    silence_perc = get_silence_percentage(filepath)
    if silence_perc > max_silence:
        logging.warning(f"Skipping {filepath.name}: Exceeds max silence of {max_silence}% (detected: {silence_perc:.1f}%)")
        return

    logging.info(f"File {filepath.name} passed all checks. Queueing for processing.")

    # 4. Call the main processing logic
    try:
        # Running the async function in a new event loop for each file
        asyncio.run(process_single_file(filepath))
        logging.info(f"Successfully processed {filepath.name}.")

        # 5. Optionally delete file
        if DAEMON_CONFIG.get('processing', {}).get('delete_processed_files', False):
            logging.info(f"Deleting {filepath.name} as per configuration.")
            os.remove(filepath)

    except Exception as e:
        logging.error(f"An error occurred while processing {filepath.name}: {e}", exc_info=True)

# --- Main Daemon Loop ---
def run_daemon():
    """The main entry point for the daemon's execution."""
    setup_logging()
    logging.info("Daemon started.")

    watch_folders = DAEMON_CONFIG.get('watch_folders', [])
    if not watch_folders:
        logging.error("No 'watch_folders' specified in the configuration. Daemon exiting.")
        return

    observer = Observer()
    event_handler = NewFileHandler()
    for folder in watch_folders:
        if not os.path.isdir(folder):
            logging.error(f"Watch folder '{folder}' does not exist or is not a directory. Skipping.")
            continue
        observer.schedule(event_handler, folder, recursive=True)
        logging.info(f"Watching folder: {folder}")

    if not observer.emitters:
        logging.error("No valid folders to watch. Daemon exiting.")
        return

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    logging.info("Daemon stopped.")


# --- Daemon Control Functions ---
class DaemonRunner:
    def __init__(self):
        self.pidfile_path = str(PID_FILE)
        self.pidfile_timeout = 5
        self.context = daemon.DaemonContext(
            working_directory=os.getcwd(),
            umask=0o022,
            pidfile=lockfile.FileLock(self.pidfile_path),
            stdout=open(LOG_FILE, 'a+'),
            stderr=open(LOG_FILE, 'a+'),
        )

    def start(self):
        """Starts the daemon."""
        print("Starting Meetscribe daemon...")
        try:
            self.context.open()
            run_daemon()
        except daemon.daemon.DaemonError as e:
            print(f"Error starting daemon: {e}")
            self.stop() # Clean up if something went wrong

    def stop(self):
        """Stops the daemon."""
        print("Stopping Meetscribe daemon...")
        try:
            with open(self.pidfile_path, 'r') as f:
                pid = int(f.read().strip())
            os.kill(pid, 15) # Terminate
            # Wait for pidfile to be released
            time.sleep(1)
        except FileNotFoundError:
            print("Daemon is not running (PID file not found).")
        except (ProcessLookupError, ValueError):
             print("Daemon process not found. Cleaning up stale PID file.")
             os.remove(self.pidfile_path)
        except Exception as e:
            print(f"Error stopping daemon: {e}")

    def get_status(self):
        """Checks the daemon status."""
        try:
            with open(self.pidfile_path, 'r') as f:
                pid = int(f.read().strip())
            os.kill(pid, 0) # Check if process exists
            return f"Daemon is running with PID {pid}."
        except (FileNotFoundError, ValueError):
            return "Daemon is not running."
        except ProcessLookupError:
            return "Daemon is not running (stale PID file found)."
        except Exception as e:
            return f"Could not determine status: {e}"

    def show_logs(self, tail_lines=50):
        """Shows the last N lines of the daemon log."""
        if not LOG_FILE.is_file():
            return "Log file not found."
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            for line in lines[-tail_lines:]:
                print(line.strip())
