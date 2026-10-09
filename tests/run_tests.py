"""Release checks with isolated Tk interpreters and bounded worker lifetimes."""
import faulthandler
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'tests'))


def cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from cases(item)
        else:
            yield item


def worker(target):
    try:
        import bcrypt
    except ModuleNotFoundError:
        print('bcrypt absent : installez requirements-dev.txt', flush=True)
        return 1
    if target == 'backend':
        discovered = unittest.defaultTestLoader.discover(str(ROOT/'tests'))
        suite = unittest.TestSuite(test for test in cases(discovered)
                                   if not test.id().startswith('test_modern_widgets.'))
    else:
        suite = unittest.defaultTestLoader.loadTestsFromName(target)
    faulthandler.dump_traceback_later(45, repeat=True)
    try:
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() and not result.skipped else 1
    finally:
        faulthandler.cancel_dump_traceback_later()


def main():
    if len(sys.argv) == 3 and sys.argv[1] == '--worker':
        return worker(sys.argv[2])
    suite = unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    discovered = list(cases(suite))
    widget_ids = [test.id() for test in discovered
                  if test.id().startswith('test_modern_widgets.')]
    targets = [('backend', 300)] + [(identifier, 60) for identifier in widget_ids]
    failed = []
    for target, timeout in targets:
        print(f'\n--- {target} (maximum {timeout}s) ---', flush=True)
        try:
            result = subprocess.run([sys.executable, '-u', str(Path(__file__).resolve()),
                                     '--worker', target], cwd=ROOT, timeout=timeout)
            if result.returncode:
                failed.append(target)
        except subprocess.TimeoutExpired:
            print(f'ECHEC : délai dépassé pour {target}', flush=True)
            failed.append(target)
    print(f'\n{len(discovered)} tests découverts ; {len(failed)} groupe(s) en échec.', flush=True)
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
