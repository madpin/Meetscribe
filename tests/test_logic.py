import unittest
import os
import tempfile
import shutil
from datetime import datetime

# Import the functions to be tested
from src.meetscribe.ingest import find_audio_files
from src.meetscribe.jira import extract_jira_key_from_text
from src.meetscribe.llm import _build_prompt

class TestLogic(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing ingestion
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_find_audio_files(self):
        # Create dummy files
        open(os.path.join(self.test_dir, 'meeting_2024-01-01.mp3'), 'a').close()
        open(os.path.join(self.test_dir, 'no_date.wav'), 'a').close()
        open(os.path.join(self.test_dir, 'document.txt'), 'a').close()

        files = find_audio_files(self.test_dir)
        self.assertEqual(len(files), 2)

        # Check the file with the date in the name
        dated_file = next((f for f in files if 'meeting' in f['path']), None)
        self.assertIsNotNone(dated_file)
        self.assertEqual(dated_file['timestamp'], datetime(2024, 1, 1))

    def test_extract_jira_key_from_text(self):
        self.assertEqual(extract_jira_key_from_text("Here is the ticket PROJ-123."), "PROJ-123")
        self.assertEqual(extract_jira_key_from_text("Let's discuss proj-456 in the meeting."), "PROJ-456")
        self.assertEqual(extract_jira_key_from_text("No ticket here."), None)
        self.assertEqual(extract_jira_key_from_text("This is for APP-1 and also WEB-2."), "APP-1") # Finds first
        self.assertEqual(extract_jira_key_from_text(None), None)
        self.assertEqual(extract_jira_key_from_text(""), None)

    def test_build_prompt_basic(self):
        context = {'transcript': 'Hello world'}
        prompt = _build_prompt(context)
        self.assertIn("Hello world", prompt)
        self.assertNotIn("Google Calendar", prompt)
        self.assertNotIn("Jira ticket", prompt)

    def test_build_prompt_full_context(self):
        context = {
            'transcript': 'Discussion about the bug.',
            'calendar_event': {
                'summary': 'Bug Bash',
                'start': '2024-01-01T10:00:00',
                'description': 'Let us find some bugs.'
            },
            'jira_ticket': {
                'key': 'FIX-42',
                'summary': 'Fix the main button',
                'status': 'In Progress',
                'url': 'http://jira.example.com/FIX-42'
            }
        }
        prompt = _build_prompt(context)
        self.assertIn("Discussion about the bug.", prompt)
        self.assertIn("Bug Bash", prompt)
        self.assertIn("FIX-42", prompt)
        self.assertIn("Fix the main button", prompt)

if __name__ == '__main__':
    unittest.main()
