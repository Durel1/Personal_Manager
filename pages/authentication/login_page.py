from tkinter import *
# import pymysql
from tkinter import messagebox as mb
import sqlite3
from backend.auth import authenticate_user, AuthenticationError
from pages.authentication.forget_password import ForgetPassword

from pages.authentication.register_page import RegisterPage

# creation de la class Loginpage
class LoginPage:
       def __init__(self,root,width,height):
              # dimensions de la fenetre
              self.width = width
              self.height = height
              # root = fenetre parent, width et height sont les dimensions de la fenetre

              #creation d'un canva de taille equale a la page Loginpage
              self.page = Canvas(root,width=width,height=height,bg="#1c141f")
              self.image = PhotoImage(file="login.png")
              Label(self.page, image=self.image,bg="#1c141f").place(x=30,y=150)


              #affichage de l image login avec ces caracteristiques
              Label(self.page,text=" Login ",fg="white",bg="#1c141f",font=("Arial",40)).place(x=500, y=30)

              # insertion de l'image ....


              # affichage de la l'entree username

              Label(self.page,text="Utilisateur :",fg="white",bg="#1c141f",font=("Arial",15)).place(x=600, y=180)
              self.username = Entry(self.page ,text="",font=("Arial",15,"bold"))
              self.username.place(x=760, y=180)

              #creation de la case password

              Label(self.page,text="Mot de passe :",fg="white",bg="#1c141f",font=("Arial",15)).place(x=600, y=275)
              self.password = Entry(self.page, text="", font=("Arial",15,"bold"),show="*")
              self.password.place(x=760, y=275)

              Button(self.page,text="                    Se connecter                    ",bg="#3711d1",font=("Arial",15,"bold"),fg="white",bd=0
               ,command=self.connection).place(x=605,y=380)


              #demander a l'utilisateur si il a oublie son mot de passe

              Button(self.page, text=" Mot de passe oublie ? ",fg="#fff",font=("arial",13),
                     bg="#1c141f",bd=0,command = lambda: ForgetPassword(self.page,self.width,self.height)).place(x=745,y=317)
              Button(self.page, text=" Créer un compte ? ",fg="#fff",font=("arial",13),bg="#1c141f",bd=0,
                     command = lambda: RegisterPage(self.page,self.width,self.height)).place(x=690,y=460)

              self.page.place(x=0,y=0)


       def connection(self):
              username = self.username.get().strip()
              password = self.password.get()
              if not username or not password:
                     mb.showwarning("Attention", "Veuillez remplir tous les champs.")
                     return
              try:
                     user = authenticate_user(username, password)
              except (sqlite3.Error, AuthenticationError):
                     mb.showerror("Connexion impossible", "La base est indisponible ou doit être migrée.")
                     return
              if user is None:
                     mb.showwarning("Connexion", "Nom utilisateur ou mot de passe incorrect.")
                     return
              from pages.home.home_page import HomePage
              HomePage(self.page, self.width, self.height, user['fullname'])
