"""
Meetscribe - Audio-to-Meeting Notes Automation Tool

A command-line application that automates the process of turning audio recordings
of meetings into structured, actionable notes using AI transcription and LLM processing.
"""

from .cli import cli
from .ingest import find_audio_files
from .transcribe import transcribe_audio
from .gcal import get_calendar_service, find_meeting_for_timestamp
from .jira import get_jira_client, extract_jira_key_from_text, get_jira_ticket_details
from .llm import generate_notes

__version__ = "0.1.0"
__author__ = "Thiago Pinto"

__all__ = [
    "cli",
    "find_audio_files",
    "transcribe_audio", 
    "get_calendar_service",
    "find_meeting_for_timestamp",
    "get_jira_client",
    "extract_jira_key_from_text",
    "get_jira_ticket_details",
    "generate_notes",
]

