import click
import asyncio
from pprint import pprint

from .ingest import find_audio_files
from .processing import process_single_file
from .daemon import DaemonRunner

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
    Processes all audio files in a folder, generating notes for each.
    """
    click.echo(f"Scanning for audio files in: {audio_folder}")
    audio_files_to_process = find_audio_files(audio_folder)

    if not audio_files_to_process:
        click.echo("No audio files found.")
        return

    click.echo(f"Found {len(audio_files_to_process)} audio file(s). Starting processing...")

    async def run_all():
        tasks = [process_single_file(f['path']) for f in audio_files_to_process]
        results = await asyncio.gather(*tasks)

        click.echo("\n--- Processing Complete ---")
        for data in results:
            if data:
                click.echo(f"\n--- Results for {data.get('audio_path', 'N/A')} ---")
                notes = data.pop('notes', 'No notes generated.')
                pprint(data)
                click.echo("\n--- Generated Notes ---")
                click.echo(notes)
                click.echo("---------------------------------")

    asyncio.run(run_all())


# --- Daemon Commands ---

@click.group(name="daemon")
def daemon_group():
    """Manage the Meetscribe background service."""
    pass

@daemon_group.command("start")
def start_daemon():
    """Starts the Meetscribe daemon."""
    runner = DaemonRunner()
    runner.start()

@daemon_group.command("stop")
def stop_daemon():
    """Stops the Meetscribe daemon."""
    runner = DaemonRunner()
    runner.stop()

@daemon_group.command("status")
def status_daemon():
    """Checks the status of the Meetscribe daemon."""
    runner = DaemonRunner()
    status = runner.get_status()
    click.echo(status)

@daemon_group.command("logs")
@click.option('--lines', '-n', default=50, help='Number of log lines to show.')
def logs_daemon(lines):
    """Shows the latest logs from the daemon."""
    runner = DaemonRunner()
    runner.show_logs(tail_lines=lines)

# Add the daemon command group to the main CLI
cli.add_command(daemon_group)
