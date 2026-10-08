"""Release check: fail if a dependency is missing or a test is skipped."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import bcrypt
except ModuleNotFoundError:
    raise SystemExit('bcrypt absent : installez les dépendances avec python -m pip install -r requirements.txt')

if __name__ == '__main__':
    suite = unittest.defaultTestLoader.discover(str(Path(__file__).parent))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() and not result.skipped else 1)
