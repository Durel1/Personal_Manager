"""Diagnostics without exception values, SQL payloads or passwords."""
import logging
import traceback
from logging.handlers import RotatingFileHandler
from backend.storage import application_directory

def record_error(context, error):
    try:
        logger = logging.getLogger('personalmanager')
        if not logger.handlers:
            folder = application_directory()/'logs'
            folder.mkdir(parents=True, exist_ok=True)
            handler = RotatingFileHandler(folder/'application.log',maxBytes=1_000_000,backupCount=3,encoding='utf-8')
            handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
            logger.addHandler(handler)
            logger.setLevel(logging.ERROR)
            logger.propagate = False
        frames = traceback.extract_tb(error.__traceback__)
        locations = ' > '.join(f'{frame.name}:{frame.lineno}' for frame in frames)
        logger.error('%s [%s] %s',context,type(error).__name__,locations)
    except Exception:
        pass

def startup_error(error):
    record_error('startup',error)
    text = 'PersonalManager ne peut pas démarrer. Vérifiez l’installation et le journal dans le dossier PersonalManager de vos données locales.'
    try:
        from tkinter import Tk,messagebox
        root = Tk()
        root.withdraw()
        try:
            messagebox.showerror('PersonalManager',text,parent=root)
        finally:
            root.destroy()
    except Exception:
        import sys
        if sys.platform == 'win32':
            import ctypes
            ctypes.windll.user32.MessageBoxW(None,text,'PersonalManager',0x10)
        elif sys.stderr is not None:
            print(text,file=sys.stderr)
