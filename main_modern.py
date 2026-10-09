"""Alternate entry point for the modern application; main.py is now the default."""
from main import main

if __name__ == '__main__':
    raise SystemExit(main())
