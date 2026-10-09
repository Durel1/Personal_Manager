"""Writable per-user storage outside the packaged application."""
import os
import sys
from pathlib import Path

def application_directory():
    if sys.platform == 'win32':
        base = Path(os.environ.get('LOCALAPPDATA') or Path.home()/'AppData'/'Local')
    else:
        base = Path(os.environ.get('XDG_DATA_HOME') or Path.home()/'.local'/'share')
    return base/'PersonalManager'
