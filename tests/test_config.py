import unittest
from unittest.mock import patch, mock_open
import yaml
from pathlib import Path

from src.meetscribe import config as config_module

class TestConfig(unittest.TestCase):

    @patch('src.meetscribe.config.yaml.dump')
    @patch('src.meetscribe.config.Path.mkdir')
    def test_get_config_creates_default(self, mock_mkdir, mock_yaml_dump):
        """
        Test that get_config creates a default file when none exists.
        """
        # Arrange
        # Patch is_file to return False, simulating file does not exist
        with patch('src.meetscribe.config.Path.is_file', return_value=False):
            # Patch open for file writing
            with patch('builtins.open', mock_open()) as mocked_file:
                # Act
                config = config_module.get_config()

                # Assert
                mock_mkdir.assert_called_once_with(exist_ok=True)
                mocked_file.assert_called_once_with(config_module.CONFIG_FILE, 'w')
                mock_yaml_dump.assert_called_once_with(
                    config_module.DEFAULT_CONFIG,
                    mocked_file(),
                    default_flow_style=False
                )
                self.assertEqual(config, config_module.DEFAULT_CONFIG)

    def test_get_config_merges_user_config(self):
        """
        Test that get_config correctly loads and merges a user's partial config.
        """
        # Arrange
        user_config_data = {
            'daemon': {
                'max_duration_hours': 5.0,
                'watch_folders': ['/my/test/folder'],
            }
        }
        user_config_yaml = yaml.dump(user_config_data)

        # Patch is_file to return True, open to return the yaml data
        with patch('src.meetscribe.config.Path.is_file', return_value=True), \
             patch('builtins.open', mock_open(read_data=user_config_yaml)):

            # Act
            config = config_module.get_config()

            # Assert
            # User values should override defaults
            self.assertEqual(config['daemon']['max_duration_hours'], 5.0)
            self.assertEqual(config['daemon']['watch_folders'], ['/my/test/folder'])

            # Default values should still exist
            self.assertEqual(config['daemon']['max_silence_percentage'], 30.0)
            self.assertTrue(config['daemon']['processing']['auto_generate_notes'])

if __name__ == '__main__':
    unittest.main()
