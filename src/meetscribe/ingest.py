import os
import re
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

SUPPORTED_FORMATS = ('.mp3', '.wav', '.m4a')

def _extract_timestamp_from_filename(filename: str) -> Optional[datetime]:
    """Tries to extract a timestamp from a filename (e.g., YYYY-MM-DD)."""
    # Regex to find a date in YYYY-MM-DD format
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        try:
            # Return datetime object with time set to start of the day
            return datetime.strptime(match.group(1), '%Y-%m-%d')
        except ValueError:
            return None
    return None

def find_audio_files(directory: str) -> List[Dict]:
    """
    Scans a directory for audio files and extracts their timestamps.

    Args:
        directory: The path to the directory to scan.

    Returns:
        A list of dictionaries, where each dictionary represents an audio file
        and contains its path and timestamp.
    """
    audio_files = []
    for filename in os.listdir(directory):
        if filename.lower().endswith(SUPPORTED_FORMATS):
            filepath = os.path.join(directory, filename)

            timestamp = _extract_timestamp_from_filename(filename)

            if not timestamp:
                try:
                    # Fallback to file's modification time
                    mtime = os.path.getmtime(filepath)
                    timestamp = datetime.fromtimestamp(mtime)
                except OSError:
                    continue  # Skip if file metadata is inaccessible

            audio_files.append({
                'path': filepath,
                'timestamp': timestamp
            })

    return audio_files


def get_timestamp_from_path(filepath: str) -> Optional[datetime]:
    """
    Extracts a timestamp from a single file's name or modification time.
    """
    path = Path(filepath)
    filename = path.name

    timestamp = _extract_timestamp_from_filename(filename)

    if not timestamp:
        try:
            # Fallback to file's modification time
            mtime = os.path.getmtime(filepath)
            timestamp = datetime.fromtimestamp(mtime)
        except OSError:
            return None # Could not get timestamp

    return timestamp
