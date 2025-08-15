# Audio-to-Meeting Notes Automation Tool

This tool is a command-line application designed to automate the process of turning audio recordings of meetings into structured, actionable notes. It integrates with Google Calendar and Jira to provide rich context to the notes, and uses Deepgram for transcription and an OpenAI model for note generation.

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

## Setup and Installation

### 1. Clone the Repository

```bash
git clone <repository_url>
cd <repository_directory>
```

### 2. Install Dependencies

It is recommended to use a virtual environment.

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 3. Configure Credentials

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

To run the tool, use the `process-meetings` command, passing the path to your audio folder:

```bash
python -m src.autonotes process-meetings /path/to/your/audio/folder
```

The tool will process each audio file and print the context and generated notes to the console.

## Running Tests

To run the unit tests:

```bash
python -m unittest tests/test_logic.py
```
