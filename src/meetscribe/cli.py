import click
import os
import asyncio
from pprint import pprint
from .ingest import find_audio_files
from .transcribe import transcribe_audio
from .gcal import get_calendar_service, find_meeting_for_timestamp
from .jira import get_jira_client, extract_jira_key_from_text, get_jira_ticket_details
from .llm import generate_notes

@click.group()
def cli():
    """
    A command-line tool to automate meeting notes from audio recordings.
    """
    pass

@cli.command("process-meetings")
@click.argument('audio_folder', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def process_meetings(audio_folder):
    """
    Processes all audio files in a given folder, linking them to calendar
    events and Jira tickets, transcribing them, and generating notes.
    """
    click.echo(f"Processing audio files from: {audio_folder}")

    # --- Step 1: Ingest Audio Files ---
    audio_files = find_audio_files(audio_folder)
    if not audio_files:
        click.echo("No audio files found in the directory.")
        return
    click.echo(f"Found {len(audio_files)} audio file(s).")

    # --- Step 2: Initialize Services ---
    click.echo("\nInitializing external services...")
    gcal_service = get_calendar_service()
    jira_client = get_jira_client()

    # --- Step 3: Process each file ---
    async def run_processing():
        processing_tasks = []
        for audio_file in audio_files:
            processing_tasks.append(process_single_file(audio_file))

        processed_data = await asyncio.gather(*processing_tasks)

        click.echo("\n--- Processing Complete ---")
        for data in processed_data:
            click.echo(f"\n--- Results for {data['audio_path']} ---")
            # Print context, but handle notes separately for better formatting
            notes = data.pop('notes', 'No notes generated.')
            pprint(data)
            click.echo("\n--- Generated Notes ---")
            click.echo(notes)
            click.echo("---------------------------------")

    async def process_single_file(audio_file):
        """Orchestrates processing for a single audio file."""
        path = audio_file['path']
        timestamp = audio_file['timestamp']
        context = {'audio_path': path, 'timestamp': timestamp}

        # Transcription
        context['transcript'] = await transcribe_audio(path)

        # Calendar Matching
        if gcal_service:
            meeting = find_meeting_for_timestamp(gcal_service, timestamp)
            if meeting:
                context['calendar_event'] = {
                    'summary': meeting.get('summary'),
                    'start': meeting['start'].get('dateTime'),
                    'description': meeting.get('description'),
                }
                # Jira Matching (if calendar event found)
                jira_key = extract_jira_key_from_text(meeting.get('description', ''))
                if jira_key and jira_client:
                    context['jira_ticket'] = get_jira_ticket_details(jira_client, jira_key)

        # LLM Note Generation
        context['notes'] = await generate_notes(context)
        return context

    asyncio.run(run_processing())


# This script is now run via __main__.py
