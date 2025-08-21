import yaml
import os
from pathlib import Path

# Define the path for the configuration directory and file
CONFIG_DIR = Path.home() / ".meetscribe"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

# Default configuration values as described in the README
DEFAULT_CONFIG = {
    'daemon': {
        'max_duration_hours': 1.0,
        'max_silence_percentage': 30.0,
        'supported_formats': ['.mp3', '.wav', '.m4a'],
        'watch_folders': [], # User must specify this
        'processing': {
            'auto_transcribe': True,
            'auto_generate_notes': True,
            'delete_processed_files': False,
        },
    }
}

def get_config():
    """
    Loads the user's configuration from ~/.meetscribe/config.yaml.
    If the file doesn't exist, it creates it with default values.
    If parts of the config are missing, it merges them with defaults.
    """
    # Ensure the config directory exists
    CONFIG_DIR.mkdir(exist_ok=True)

    # If the config file doesn't exist, create it with default values
    if not CONFIG_FILE.is_file():
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
        return DEFAULT_CONFIG

    # Load existing config file
    with open(CONFIG_FILE, 'r') as f:
        try:
            user_config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            print(f"Warning: Could not parse config file at {CONFIG_FILE}. Error: {e}")
            return DEFAULT_CONFIG # Return defaults if config is malformed

    # Deep merge user config with defaults
    config = _deep_merge(DEFAULT_CONFIG, user_config)

    return config

def _deep_merge(default: dict, user: dict) -> dict:
    """
    Recursively merges user config into default config.
    Overwrites default values with user-provided ones.
    """
    merged = default.copy()
    for key, value in user.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged

# Load config on module import to be used by other parts of the application
CONFIG = get_config()
