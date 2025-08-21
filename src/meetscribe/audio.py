from pydub import AudioSegment, silence
from pathlib import Path

# pydub's silence detection is configured here.
# - min_silence_len: minimum length of silence to be detected in ms.
# - silence_thresh: threshold in dBFS below which audio is considered silence.
# A good starting point is to use the average volume of the audio as a threshold.
SILENCE_DETECTION_MIN_LEN_MS = 500 # 0.5 seconds

def get_audio_duration_seconds(filepath: str | Path) -> float:
    """
    Returns the duration of an audio file in seconds.
    """
    try:
        audio = AudioSegment.from_file(filepath)
        return len(audio) / 1000.0
    except Exception as e:
        print(f"Warning: Could not read audio duration from {filepath}. Error: {e}")
        return 0.0

def get_silence_percentage(filepath: str | Path, silence_db_threshold: int = -40) -> float:
    """
    Calculates the percentage of silence in an audio file.

    Args:
        filepath: Path to the audio file.
        silence_db_threshold: The threshold (in dBFS) below which audio is
                              considered silent. Defaults to -40 dBFS.

    Returns:
        The percentage of the audio file that is silent (0.0 to 100.0).
        Returns 0.0 if the file cannot be processed.
    """
    try:
        audio = AudioSegment.from_file(filepath)
    except Exception as e:
        print(f"Warning: Could not process audio file {filepath}. Error: {e}")
        return 0.0

    if not audio:
        return 0.0

    # Use a dynamic threshold based on the audio's average volume, but don't go
    # above a certain "loudness" to avoid misclassifying speech as silence.
    # A common approach is to use the audio's average dBFS and subtract a buffer.
    # Here, we will use the provided silence_db_threshold for simplicity, as
    # recommended in the config.
    silence_thresh = silence_db_threshold

    # Find silent chunks
    silent_chunks = silence.detect_silence(
        audio,
        min_silence_len=SILENCE_DETECTION_MIN_LEN_MS,
        silence_thresh=silence_thresh
    )

    # Calculate total duration of silence in ms
    total_silence_ms = sum(stop - start for start, stop in silent_chunks)

    # Calculate total duration of the audio in ms
    total_duration_ms = len(audio)

    if total_duration_ms == 0:
        return 0.0

    # Calculate percentage
    percentage_silence = (total_silence_ms / total_duration_ms) * 100
    return percentage_silence
