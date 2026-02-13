from tkinter import *
# import pymysql
from tkinter import messagebox as mb
from subprocess import call
from backend.requests_db import get_execute_request_with_params
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
              from pages.home.home_page import HomePage
              # recuperation des infos du user et test s'il existe
              request = "select * from User where fullname=?"
              params = (self.username.get(),)
              data = get_execute_request_with_params(request,params)
              
              # liste des contraintes ....
              if self.username.get() == "" and self.password.get() =="":
                     mb.showwarning("Attention ","Veillez remplir tous les champs")
              elif self.username.get() == "" and self.password.get() !="" :
                     mb.showwarning("Attention ","Veillez Entrer votre nom !")
              elif self.password.get() =="" :
                     mb.showwarning("Attention ","Veillez entrer votre mot de passe !")
              elif self.username.get() !="" and self.password.get() !="":
                     if len(data)==0:

                            mb.showinfo("Avertissement", "Vous n'etes pas inscrit !")
                     elif str(data[0][2]) == self.password.get():

                            call([HomePage(self.page,self.width,self.height,self.username.get())])
                     else:
                            print('erreur : ', data)
                            mb.showinfo("Avertissement","Mot de pase incorrect !")

              #call([HomePage(self.page,self.width,self.height)])
