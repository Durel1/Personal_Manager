# importation de tkinter ...
from tkinter import *
import sqlite3
from tkinter import messagebox
from backend.migrations import migrate_passwords, MigrationError
from backend.auth import AuthenticationError
from backend.connection import connect_database
#importation de la page login
from pages.authentication.login_page import LoginPage

#creation de la class (pion d'entre de l'appli)
class MainApp:
    def __init__(self):
        # appel de la classe qui cree la BD et ses tables
        self.root = Tk()
        self.root.withdraw()
        try:
            with connect_database() as connection:
                if connection.execute('PRAGMA user_version').fetchone()[0] >= 3:
                    raise MigrationError('Les rôles nécessitent l’interface moderne. Lancez main.py.')
            migrate_passwords()
        except (sqlite3.Error, MigrationError, AuthenticationError) as error:
            messagebox.showerror("Initialisation impossible", str(error), parent=self.root)
            self.root.destroy()
            return
        self.root.deiconify()
        self.root.title("PersonalManager")
        self.root.geometry("1200x600+75+60")
        # self.root.iconbitmap("icone.ico")
        self.root.resizable(width=False,height=False)
        # appel de la premiere page ....
        self.first_window = LoginPage(self.root,width=1200,height=600)


        # adffichage de la fenetre
        self.root.mainloop()

if __name__ == '__main__':
    MainApp()
