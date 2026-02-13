from tkinter import *
# import pymysql
from tkinter import messagebox as mb
from subprocess import call
from backend.requests_db import get_execute_request_with_params



# creation de la class Loginpage
class ForgetPassword:
    def __init__(self, root, width, height):
        # dimensions de la fenetre
        self.width = width
        self.height = height
        # root = fenetre parent, width et height sont les dimensions de la fenetre

        # creation d'un canva de taille equale a la page Loginpage
        self.page = Canvas(root, width=width, height=height, bg="#1c141f")
        self.image = PhotoImage(file="login.png")
        Label(self.page, image=self.image, bg="#1c141f").place(x=30, y=150)

        # affichage de l image login avec ces caracteristiques
        Label(self.page, text=" Forget password ", fg="white", bg="#1c141f", font=("Arial", 40)).place(x=500, y=30)

        # insertion de l'image ....

        # affichage de la l'entree username

        Label(self.page, text="Utilisateur :", fg="white", bg="#1c141f", font=("Arial", 15)).place(x=600, y=180)
        self.username = Entry(self.page, text="", font=("Arial", 15, "bold"))
        self.username.place(x=760, y=180)

        # creation de la case password

        Label(self.page, text="Mot de passe :", fg="white", bg="#1c141f", font=("Arial", 15)).place(x=600, y=275)
        self.password = Entry(self.page, text="", font=("Arial", 15, "bold"))
        self.password.place(x=760, y=275)

        Button(self.page, text="      Recuperer le mot de passe       ", bg="#3711d1",
               font=("Arial", 15, "bold",), fg="white", bd=0,command=self.getPassword
             ).place(x=605, y=350)

        # demander a l'utilisateur si il a oublie son mot de passe

        Button(self.page, text=" Retour ", fg="#fff", font=("arial", 13), bg="#1c141f", bd=0,
               command=self.page.destroy).place(
            x=145, y=537)


        self.page.place(x=0, y=0)

    def getPassword(self):
        request = "select password from User where fullname=?"
        params = (self.username.get(),)
        password_data = get_execute_request_with_params(request,params)
        if len(password_data) == 0:
            mb.showwarning('Avertissement','Utilisateur non inscrit !')
        else:
            self.password.delete(0,END)
            self.password.insert(0,password_data[0][0])
