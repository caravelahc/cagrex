import json
from pathlib import Path

_PATH = Path(__file__).parent / 'credentials.json'


def load_credentials():
    try:
        with _PATH.open() as f:
            return json.load(f)

    except IOError:
        return None
