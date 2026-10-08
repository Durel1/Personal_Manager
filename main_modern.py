"""Alternate entry point for the modern application; main.py is now the default."""
from ui.application import PersonalManager

if __name__ == '__main__':
    PersonalManager().mainloop()
