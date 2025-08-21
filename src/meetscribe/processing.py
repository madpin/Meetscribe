import asyncio
from pathlib import Path
from pprint import pprint

from .ingest import get_timestamp_from_path
from .transcribe import transcribe_audio
from .gcal import get_calendar_service, find_meeting_for_timestamp
from .jira import get_jira_client, extract_jira_key_from_text, get_jira_ticket_details
from .llm import generate_notes

async def process_single_file(audio_path: str | Path):
    """
    Orchestrates the full processing pipeline for a single audio file.
    Gathers context, transcribes, and generates notes.

    Args:
        audio_path: The path to the audio file.

    Returns:
        A dictionary containing the processed context, including the generated notes.
        Returns None if the file cannot be processed.
    """
    audio_path = Path(audio_path)
    timestamp = get_timestamp_from_path(str(audio_path))

    if not timestamp:
        print(f"Warning: Could not determine timestamp for {audio_path.name}. Skipping.")
        return None

    context = {'audio_path': str(audio_path), 'timestamp': timestamp}

    # Initialize services (they have built-in caching or singleton patterns)
    gcal_service = get_calendar_service()
    jira_client = get_jira_client()

    # --- Start processing steps ---
    print(f"Processing: {audio_path.name}")

    # 1. Transcription
    context['transcript'] = await transcribe_audio(str(audio_path))
    if not context.get('transcript'):
        print(f"Transcription failed for {audio_path.name}. Skipping note generation.")
        return context # Return what we have so far

    # 2. Calendar Matching
    if gcal_service:
        meeting = find_meeting_for_timestamp(gcal_service, timestamp)
        if meeting:
            context['calendar_event'] = {
                'summary': meeting.get('summary'),
                'start': meeting['start'].get('dateTime'),
                'description': meeting.get('description'),
            }
            # 3. Jira Matching (only if a calendar event is found)
            jira_key = extract_jira_key_from_text(meeting.get('description', ''))
            if jira_key and jira_client:
                context['jira_ticket'] = get_jira_ticket_details(jira_client, jira_key)

    # 4. LLM Note Generation
    print(f"Generating notes for {audio_path.name}...")
    context['notes'] = await generate_notes(context)

    print(f"Finished processing {audio_path.name}")
    return context
