# importation de tkinter ...
from tkinter import *
from backend.create_database import Database
#importation de la page login
from pages.authentication.login_page import LoginPage

#creation de la class (pion d'entre de l'appli)
class MainApp:
    def __init__(self):
        # appel de la classe qui cree la BD et ses tables 
        Database()
        self.root = Tk()
        self.root.title("PersonalManager")
        self.root.geometry("1200x600+75+60")
        # self.root.iconbitmap("icone.ico")
        self.root.resizable(width=False,height=False)
        # appel de la premiere page ....
        self.first_window = LoginPage(self.root,width=1200,height=600)


        # adffichage de la fenetre
        self.root.mainloop()

#appel de la class mainapp
ma_fenetre = MainApp()
print(ma_fenetre)




