"""Desktop entry point and isolated packaged-build self-test."""
import argparse

def main():
    parser = argparse.ArgumentParser(description='PersonalManager')
    parser.add_argument('--self-test-result',metavar='JSON',help='Run an isolated self-test and write its result')
    args = parser.parse_args()
    if args.self_test_result:
        from tools.frozen_check import run_self_test
        return run_self_test(args.self_test_result)
    try:
        from ui.application import PersonalManager
        PersonalManager().mainloop()
    except Exception as error:
        from backend.diagnostics import startup_error
        startup_error(error)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
