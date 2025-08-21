# Meetscribe

**Audio-to-Meeting Notes Automation Tool**

Meetscribe is a command-line application designed to automate the process of turning audio recordings of meetings into structured, actionable notes. It integrates with Google Calendar and Jira to provide rich context to the notes, and uses Deepgram for transcription and an OpenAI model for note generation.

This project was built by Jules, an AI software engineer, based on a design document for Thiago, a Software Engineer at Indeed.

## Features

-   **Audio Ingestion**: Scans a folder for audio files (`.mp3`, `.wav`, `.m4a`).
-   **Contextual Enrichment**:
    -   Matches audio files to Google Calendar events based on timestamps.
    -   Pulls in associated Jira ticket details if referenced in the calendar event.
-   **AI-Powered Processing**:
    -   Transcribes audio using Deepgram's speech-to-text API.
    -   Generates structured notes (Summary, Key Decisions, Action Items) using an OpenAI LLM.
-   **CLI Interface**: Easy-to-use command-line interface powered by `click`.
-   **Daemon Mode**: Background service that automatically processes new audio files based on configurable rules.
-   **Smart Audio Analysis**: Intelligent silence detection to avoid processing low-quality recordings.

## Installation

### From Source

```bash
git clone https://github.com/madpin/Meetscribe.git
cd meetscribe
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/madpin/Meetscribe.git
cd meetscribe
pip install -e ".[dev]"
```

## Setup and Configuration

### 1. Configure Credentials

This tool requires API access to several services.

#### a) Google Calendar

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project or select an existing one.
3.  Enable the **Google Calendar API**.
4.  Go to "Credentials", click "Create Credentials", and choose "OAuth client ID".
5.  Select "Desktop app" as the application type.
6.  Click "Download JSON" to download your client secrets file.
7.  **Rename the downloaded file to `credentials.json` and place it in the root directory of this project.**

The first time you run the tool, it will open a browser window for you to authorize access to your calendar. This will create a `token.json` file to store your credentials for future runs.

#### b) Deepgram (for Transcription)

1.  Sign up for a [Deepgram account](https://deepgram.com/).
2.  Create an API key.
3.  Set it as an environment variable:
    ```bash
    export DEEPGRAM_API_KEY="your_deepgram_api_key"
    ```

#### c) OpenAI (for Note Generation)

1.  You need an [OpenAI API key](https://platform.openai.com/api-keys).
2.  Set it as an environment variable:
    ```bash
    export OPENAI_API_KEY="your_openai_api_key"
    ```
3.  (Optional) If you want to use a custom or self-hosted OpenAI-compatible API, set the base URL as an environment variable:
    ```bash
    export OPENAI_API_BASE_URL="https://api.openai.com/v1"
    ```
    By default, the tool uses `https://api.openai.com/v1` as the base URL.

#### d) Jira (Optional)

1.  You need a Jira API token. You can create one from your Atlassian account settings.
2.  Set the following environment variables:
    ```bash
    export JIRA_SERVER="https://your-domain.atlassian.net"
    export JIRA_USER_EMAIL="your-email@example.com"
    export JIRA_API_TOKEN="your_jira_api_token"
    ```

## Usage

Place your audio recordings in a folder. The tool can extract timestamps from filenames with a `YYYY-MM-DD` format (e.g., `meeting_2025-08-20.mp3`) or use the file's modification time.

### Command Line Usage

```bash
# Process all audio files in a directory
meetscribe process-meetings /path/to/your/audio/folder

# Or run directly with Python
python -m src.meetscribe process-meetings /path/to/your/audio/folder
```

### Daemon Mode

Meetscribe includes a daemon service that automatically monitors a folder for new audio files and processes them based on configurable rules:

```bash
# Start the daemon service
meetscribe daemon start /path/to/your/audio/folder

# Stop the daemon service
meetscribe daemon stop

# Check daemon status
meetscribe daemon status

# View daemon logs
meetscribe daemon logs
```

#### Daemon Configuration

The daemon automatically processes audio files that meet these criteria:
- **Duration**: Files shorter than 1 hour (configurable)
- **Quality**: Files with less than 30% silence content
- **Format**: Supported audio formats (`.mp3`, `.wav`, `.m4a`)

You can customize these rules by creating a configuration file:

```yaml
# ~/.meetscribe/config.yaml
daemon:
  max_duration_hours: 1.0
  max_silence_percentage: 30.0
  supported_formats: [".mp3", ".wav", ".m4a"]
  watch_folders:
    - /path/to/primary/audio/folder
    - /path/to/secondary/audio/folder
  processing:
    auto_transcribe: true
    auto_generate_notes: true
    delete_processed_files: false
```

#### Silence Detection

The daemon includes intelligent silence detection to avoid processing low-quality recordings:
- Analyzes audio files for silence patterns
- Skips files with more than 30% silence content
- Provides detailed silence analysis reports
- Configurable silence thresholds

### Programmatic Usage

```python
from meetscribe import find_audio_files, transcribe_audio, generate_notes

# Find audio files in a directory
audio_files = find_audio_files("/path/to/audio")

# Transcribe a single file
transcript = await transcribe_audio("/path/to/audio/meeting.mp3")

# Generate notes from context
notes = await generate_notes({
    'transcript': transcript,
    'calendar_event': {...},
    'jira_ticket': {...}
})
```

## Future Features

### Silence Removal

Planned for future releases, Meetscribe will include advanced audio preprocessing capabilities:

- **Automatic Silence Trimming**: Remove leading and trailing silence from audio files
- **Smart Silence Detection**: Identify and remove excessive silence within recordings
- **Configurable Thresholds**: Adjustable silence detection sensitivity
- **Batch Processing**: Process multiple files with silence removal
- **Quality Preservation**: Maintain audio quality while removing unwanted silence

This feature will help improve transcription accuracy and reduce processing time for recordings with long periods of silence.

## Project Structure

```
meetscribe/
├── src/
│   └── meetscribe/           # Main package
│       ├── __init__.py       # Package exports
│       ├── cli.py            # Command-line interface
│       ├── ingest.py         # Audio file ingestion
│       ├── transcribe.py     # Audio transcription
│       ├── gcal.py           # Google Calendar integration
│       ├── jira.py           # Jira integration
│       ├── llm.py            # LLM note generation
│       └── __main__.py       # Entry point
├── tests/                    # Test suite
├── sample_audio/             # Sample audio files
├── pyproject.toml           # Project configuration
├── requirements.txt          # Dependencies
└── README.md                # This file
```

## Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_logic.py

# Run with coverage
python -m pytest --cov=src.meetscribe
```

## Development

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## License

MIT License - see LICENSE file for details.
