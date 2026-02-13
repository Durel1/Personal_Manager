from tkinter import *
from tkinter import messagebox as mb
from tkinter.font import Font
import random as rd
from tkinter import ttk
from tkinter import messagebox as mb
from backend.requests_db import set_execute_request_with_params

class ajout_employer :

    def __init__(self,root,width,height):
        self.width = width
        self.height = height
        self.fonts = ('Arial',14,'bold')
        self.page = Canvas(root,width=width,height=height,bg="#1978a5")
        self.font = Font(family="Helvetica", size=12, underline=True, slant="italic", weight="bold")
        
        Label(self.page,text="1.     Ajouter un nouvelle Employer " ,font=self.font, bg="#1978a5",fg="white" ).place(x=20,y=20)

        Label(self.page,text="Entrer les informations de l'employer a enregistrer . "
              ,font=self.fonts, bg="#1978a5",fg="white" ).place(x=130,y=80)
        
        Label(self.page,text="NOM : ",font=self.fonts, bg="#1978a5",fg="white" ).place(x=200,y=150)
        self.nom=Entry(self.page,font=self.fonts)
        self.nom.place(x=280,y=150)
        
        Label(self.page,text="Email : ",font=self.fonts, bg="#1978a5",fg="white" ).place(x=200,y=210)
        self.email=Entry(self.page,font=self.fonts)
        self.email.place(x=280,y=210)
        
        Label(self.page, text="TEL : ", font=self.fonts, bg="#1978a5", fg="white").place(x=200, y=330)
        self.tel=Entry(self.page, font=self.fonts)
        self.tel.place(x=280, y=330)
        
        Label(self.page,text="Sexe : ",font=self.fonts, bg="#1978a5",fg="white" ).place(x=200,y=260)
        self.i = StringVar()
        bouton1=Radiobutton(self.page, text=" Homme ", value="Homme", variable=self.i, bg="#1978a5",activebackground="#1978a5",activeforeground="black")
        bouton1.place(x=270, y=260)
        bouton2=Radiobutton(self.page, text="Femme", value="Femme", variable=self.i, bg="#1978a5",activebackground="#1978a5",activeforeground="black")
        bouton2.place(x=400, y=260)
        bouton1.invoke()
        
        Button(self.page,text="Enregistrer",font=self.fonts, bg="blue",fg="cadetblue1"
               ,activebackground="#1978a5",activeforeground="blue",command=self.enregistre).place(x=215,y=450)
        
        Button(self.page,text="vider les champs ",font=self.fonts, bg="orange",fg="cadetblue1"
               ,activebackground="#1978a5",activeforeground="red",command=self.supprimer).place(x=415,y=450)

        
        
        self.page.place(x=200,y=51)

    def supprimer(self):
        text=mb.askyesno("confirmer","voulez vous vider tout les champ? ")
        if text:
            self.email.delete(0, END)
            self.nom.delete(0, END)
            self.tel.delete(0, END)

    def enregistre(self):

        id = rd.randint(100,900) +  rd.randint(1,9) +  rd.randint(10,90)

        nom=self.nom.get()
        email=self.email.get()
        tel=self.tel.get()
        sexe=self.i.get()


        #testez si tous les champs sont remplie

        if nom=="" or email=="" or tel=="":
            mb.showwarning("Avertissement","Veuiller remplir tous les champs")
        elif email[-10:] != "@gmail.com":
            mb.showwarning("Erreur", "Entrer un mail correct")
        elif (tel.isdigit()==False):
            mb.showwarning("Avertissement","Mauvais numero.")
        else :
            params=(id,nom,email,tel,sexe)
            request="insert into Employee values(?,?,?,?,?)"
            try :
                test=set_execute_request_with_params(request,params)
                mb.showinfo("enregistrer", "vos informations ont bien été enregistrer")
                self.email.delete(0, END)
                self.nom.delete(0, END)
                self.tel.delete(0, END)
                #data = get_execute_request_without_params(request1)

                #print("All clients : ",data)

            except Exception as e:
                print('Erreur :', e)
