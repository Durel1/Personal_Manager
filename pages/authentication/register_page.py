from tkinter import *
from subprocess import call
from tkinter.font import Font
from tkinter import messagebox as mb
# from PIL import Image, ImageTk
import random as rd
from tkinter import messagebox as mb
from tkinter import ttk

from backend.requests_db import get_execute_request_without_params, set_execute_request_with_params, \
    get_execute_request_with_params


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
        self.password=Entry(self.page,font=self.fonts)
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
        from pages.home.home_page import HomePage
        # generateur d'id
        id = rd.randint(100,900) +  rd.randint(1,9) +  rd.randint(10,90)
        
        # recuperation des entry
        fullname=self.fullname.get()
        password=self.password.get()
        email=self.email.get()
        phone=self.contact.get()
        gender=self.sexe.get()

        requetVerifie="select * from User where fullname=?"
        paramVerifie=fullname

        test=len(get_execute_request_with_params(requetVerifie,[paramVerifie]))

        #  test si tous les champ sont remplis

        if fullname=="" or password=="" or email=="" or phone=="" or gender=="" :
            mb.showwarning("Avertisement!!","veillez remplir tout les champs.")
        elif email[-10:] != "@gmail.com":
            mb.showwarning("Erreur","Entre un mail correct")
        elif (phone.isdigit()==False):
            mb.showwarning("Erreur","Mauvais numero!!!")

        elif test > 0:
            mb.showwarning("Erreur","Ce nom est déja utilisé veiullé entré un autre!!!")
        else:
            params = (id,fullname,password,email,phone,gender)
            #request = "select * from User"
            request = "insert into User values(?,?,?,?,?,?)"
            try :
                info_user=set_execute_request_with_params(request,params)
                mb.showinfo("enregitrer","vos information on bien ete enregistrer")  
                # user_info = get_execute_request_without_params(request)

                print("All username : ",info_user)              
                call([HomePage(self.page,self.width,self.height,fullname)])
            except Exception as e:
                print('Erreur :',e)
            
            
        

