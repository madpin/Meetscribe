import os
import asyncio
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
)

async def transcribe_audio(filepath: str) -> str:
    """
    Transcribes an audio file using the Deepgram API.

    This function requires the DEEPGRAM_API_KEY environment variable to be set.

    Args:
        filepath: The path to the audio file to transcribe.

    Returns:
        The transcribed text, or an empty string if transcription fails.
    """
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        print("Warning: DEEPGRAM_API_KEY not set. Skipping transcription.")
        return ""

    try:
        # STEP 1: Create a Deepgram client using the API key
        deepgram = DeepgramClient(api_key)

        with open(filepath, "rb") as file:
            buffer_data = file.read()

        payload = {"buffer": buffer_data}

        # STEP 2: Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
        )

        # STEP 3: Call the transcribe_file method with the options
        response = await deepgram.listen.prerecorded.v("1").transcribe_file(
            payload, options
        )

        # STEP 4: Extract the transcript
        transcript = response.results.channels[0].alternatives[0].transcript
        return transcript

    except Exception as e:
        print(f"Error during transcription for {filepath}: {e}")
        return ""
