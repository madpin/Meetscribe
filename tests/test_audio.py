import unittest
import os
from pathlib import Path
from pydub import AudioSegment

# Import the functions to be tested
from src.meetscribe.audio import get_audio_duration_seconds, get_silence_percentage

class TestAudioProcessing(unittest.TestCase):

    def setUp(self):
        """
        Create temporary audio files for testing.
        """
        self.test_dir = Path("tests/temp_audio")
        self.test_dir.mkdir(exist_ok=True)

        # Create a 2-second silent WAV file
        self.silent_file = self.test_dir / "silent.wav"
        silent_segment = AudioSegment.silent(duration=2000) # 2000 ms = 2s
        silent_segment.export(self.silent_file, format="wav")

        # Create a 2-second noisy WAV file (simple sine wave)
        self.noisy_file = self.test_dir / "noisy.wav"
        # Create a 2-second noisy WAV file by generating random bytes
        sample_rate = 44100
        channels = 1
        sample_width = 2  # 16-bit
        num_samples = 2 * sample_rate
        noise_bytes = os.urandom(num_samples * sample_width)

        noisy_segment = AudioSegment(
            data=noise_bytes,
            sample_width=sample_width,
            frame_rate=sample_rate,
            channels=channels
        )
        noisy_segment.export(self.noisy_file, format="wav")

    def tearDown(self):
        """
        Remove the temporary audio files and directory.
        """
        os.remove(self.silent_file)
        os.remove(self.noisy_file)
        os.rmdir(self.test_dir)

    def test_get_audio_duration(self):
        """
        Test that the duration of audio files is correctly identified.
        """
        duration_silent = get_audio_duration_seconds(self.silent_file)
        duration_noisy = get_audio_duration_seconds(self.noisy_file)

        self.assertAlmostEqual(duration_silent, 2.0, places=1)
        self.assertAlmostEqual(duration_noisy, 2.0, places=1)

    def test_get_silence_percentage(self):
        """
        Test that the silence percentage is calculated correctly.
        """
        # The silent file should be 100% silent
        silence_perc_silent = get_silence_percentage(self.silent_file, silence_db_threshold=-60)
        self.assertGreater(silence_perc_silent, 99.0)

        # The noisy file should have very little silence
        silence_perc_noisy = get_silence_percentage(self.noisy_file, silence_db_threshold=-60)
        self.assertLess(silence_perc_noisy, 1.0)


if __name__ == '__main__':
    unittest.main()
