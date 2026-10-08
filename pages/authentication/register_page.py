from tkinter import *
from tkinter.font import Font
from tkinter import messagebox as mb
# from PIL import Image, ImageTk
import sqlite3
from backend.auth import register_user, AuthenticationError
from tkinter import messagebox as mb
from tkinter import ttk




class RegisterPage:

    def __init__(self, root, width, height):
        # dimensions de la fenetre
        self.fonts = ('Arial',14)
        self.width = width
        self.height = height

        # partie de vos interfaces .....

        # root = fenetre parent, width et height sont les dimensions de la fenetre

        self.page = Canvas(root, width=width, height=height, bg="#1c141f")
        self.image = PhotoImage(file="signup.png")
        Label(self.page, image=self.image, bg="#1c141f").place(x=30, y=60)

        Label(self.page,text="Créer un compte. " ,font=self.fonts ,bg="#1c141f",fg="pink" ).place(x=580,y=80)
        Label(self.page,text="NOM UTILISATEUR : ",font=self.fonts,bg="#1c141f",fg="pink" ).place(x=580,y=160)
        self.fullname=Entry(self.page,font=self.fonts)
        self.fullname.place(x=790,y=160)
        Label(self.page,text="EMAIL : ",font=self.fonts,bg="#1c141f",fg="pink").place(x=580,y=215)
        self.email=Entry(self.page,font=self.fonts)
        self.email.place(x=790,y=215)
        Label(self.page,text="TELEPHONE : ",font=self.fonts,bg="#1c141f",fg="pink" ).place(x=580,y=265)
        self.contact=Entry(self.page,font=self.fonts)
        self.contact.place(x=790,y=265)
        Label(self.page,text="MOT DE PASS : ",font=self.fonts,bg="#1c141f",fg="pink" ).place(x=580,y=315)
        self.password=Entry(self.page,font=self.fonts,show="*")
        self.password.place(x=790,y=315)
        Label(self.page,text="GENRE : ",font=self.fonts,bg="#1c141f",fg="pink" ).place(x=580,y=370)
        self.sexe=ttk.Combobox(self.page,values=("Homme","Femme"),width=34,state="readonly")
        self.sexe.current(0)
        self.sexe.place(x=790,y=370)
        Button(self.page,text="         Effacer         ",font=self.fonts,bg="orange",fg="white",bd=0,command=self.effacer
               ).place(x=580,y=440)


        Button(self.page,text="        S'inscrire        ",font=self.fonts,bg="blue",fg="white",bd=0,command=self.register
            ).place(x=829,y=440)

        Button(self.page, text=" Vous avez un compte? ",fg="#fff",font=("arial",13),bg="#1c141f",bd=0,
               command=self.page.destroy).place(x=700,y=500)

        # bouton de transition ver le register_page
        #from pages.authentication.login_page import LoginPage
        #Button(
            #self.page, text="Se connecter",
            #command=lambda: LoginPage(self.page, width=800, height=500)).place(x=90, y=60)

        # bouton de transition ver le register_page approche 2

        self.page.place(x=0,y=0)

    def effacer(self):
        test=mb.askyesno("Effacer","Tous les champs vont etre effacer!!")
        if test:
            self.fullname.delete(0,END)
            self.email.delete(0,END)
            self.sexe.delete(0,END)
            self.password.delete(0,END)
            self.contact.delete(0,END)

    def register(self):
        try:
            register_user(self.fullname.get(), self.password.get(), self.email.get(),
                          self.contact.get(), self.sexe.get())
        except AuthenticationError as error:
            mb.showwarning("Inscription", str(error))
            return
        except sqlite3.Error:
            mb.showerror("Inscription impossible", "La base de données est indisponible. Réessayez.")
            return
        mb.showinfo("Inscription", "Compte créé. Vous pouvez vous connecter.")
        self.page.destroy()
