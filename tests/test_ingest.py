import unittest
import os
from pathlib import Path
from datetime import datetime, timedelta

from src.meetscribe.ingest import get_timestamp_from_path

class TestIngest(unittest.TestCase):

    def setUp(self):
        """
        Create temporary files for testing timestamp extraction.
        """
        self.test_dir = Path("tests/temp_ingest")
        self.test_dir.mkdir(exist_ok=True)

        # File with a date in the name
        self.dated_filename = "meeting_notes_2023-10-26.mp3"
        self.dated_filepath = self.test_dir / self.dated_filename
        self.dated_filepath.touch()

        # File without a date in the name
        self.undated_filename = "random_audio.wav"
        self.undated_filepath = self.test_dir / self.undated_filename
        self.undated_filepath.touch()
        # Set its modification time to a known value (e.g., yesterday)
        yesterday = datetime.now() - timedelta(days=1)
        os.utime(self.undated_filepath, (yesterday.timestamp(), yesterday.timestamp()))


    def tearDown(self):
        """
        Remove temporary files and directory.
        """
        os.remove(self.dated_filepath)
        os.remove(self.undated_filepath)
        os.rmdir(self.test_dir)

    def test_timestamp_from_filename(self):
        """
        Tests extracting the timestamp from a filename like '...YYYY-MM-DD...'.
        """
        timestamp = get_timestamp_from_path(str(self.dated_filepath))
        self.assertIsNotNone(timestamp)
        self.assertEqual(timestamp.year, 2023)
        self.assertEqual(timestamp.month, 10)
        self.assertEqual(timestamp.day, 26)

    def test_timestamp_from_modification_time(self):
        """
        Tests falling back to the file's modification time for the timestamp.
        """
        timestamp = get_timestamp_from_path(str(self.undated_filepath))
        self.assertIsNotNone(timestamp)

        # Check if it's close to "yesterday"
        expected_mtime = datetime.now() - timedelta(days=1)
        self.assertAlmostEqual(timestamp.timestamp(), expected_mtime.timestamp(), delta=1)


if __name__ == '__main__':
    unittest.main()
