import io
import json

DEFAULT_CONFIG = {
    'recent_databases': [],
    'requests_headers': []
}

def _merge_two_dicts(x, y):
    """Given two dictionaries, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

def loadConfiguration():
    if not os.path.isfile('configuration.json'):
        return DEFAULT_CONFIG

    with open('config.json', 'r') as f:
        return _merge_two_dicts(DEFAULT_CONFIG, json.load(f))

def writeConfiguration():
    with open('config.json', 'r') as f:
        return json.load(f)