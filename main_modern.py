"""Launch the modern preview; main.py keeps the complete legacy application."""
from ui.application import PersonalManager

if __name__ == '__main__':
    PersonalManager().mainloop()
