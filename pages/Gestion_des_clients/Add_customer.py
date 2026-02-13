from tkinter import *
from tkinter import messagebox as mb
import random as rd
from tkinter.font import Font

from backend.requests_db import set_execute_request_with_params


class ajout_clients:
    def __init__(self, root, width, height):
        self.fonts = ('Arial', 14, 'bold')
        self.page = Canvas(root, width=width, height=height, bg="#333333")
        self.font = Font(family="Helvetica", size=12, underline=True, slant="italic", weight="bold")
        
        self.label=Label(self.page, text="1.     Ajouter un nouveau client ", font=self.font, bg="#333333", fg="pink")
        self.label.place(x=20, y=20)

        self.label = Label(self.page, text="Entrer les informations du clients  a enregistrer . ", font=self.fonts, bg="#333333", fg="pink")
        self.label.place(x=130, y=80)
        
        Label(self.page, text="NOM : ", font=self.fonts, bg="#333333", fg="pink").place(x=200, y=120)
        self.nom=Entry(self.page, font=self.fonts)
        self.nom.place(x=380, y=120)
        
        Label(self.page, text="Email : ", font=self.fonts, bg="#333333", fg="pink").place(x=200, y=180)
        self.email=Entry(self.page, font=self.fonts)
        self.email.place(x=380, y=180)
        
        Label(self.page, text="TEL : ", font=self.fonts, bg="#333333", fg="pink").place(x=200, y=312)
        self.tel=Entry(self.page, font=self.fonts)
        self.tel.place(x=380, y=312)
        
        Label(self.page, text="Sexe : ", font=self.fonts, bg="#333333", fg="pink").place(x=200, y=230)
        self.i = StringVar()
        boutonhomme=Radiobutton(self.page, text=" Homme ", value=" Homme ", variable=self.i, bg="#333333", activebackground="#333333",activeforeground="black")
        boutonhomme.place(x=380, y=230)
        boutonfemme=Radiobutton(self.page, text="Femme", value="Femme", variable=self.i, bg="#333333", activebackground="#333333",activeforeground="black")
        boutonfemme.place(x=470, y=230)
        boutonhomme.invoke()
        
        self.bouton=Button(self.page, text="Enregistrer", font=self.fonts, bg="blue", fg="cadetblue1" , activebackground="#333333", activeforeground="blue", command=self.enregistre)
        self.bouton.place(x=215, y=450)
        
        self.bouton=Button(self.page, text="Vider les champs ", font=self.fonts, bg="orange", fg="cadetblue1" , activebackground="#333333", activeforeground="red", command=self.effacer)
        self.bouton.place(x=415, y=450)

        Label(self.page, text="Quartier: ", font=self.fonts, bg="#333333", fg="pink").place(x=200, y=270)
        self.quat=Entry(self.page, font=self.fonts)
        self.quat.place(x=380, y=270)
        
        Label(self.page, text="Ville: ", font=self.fonts, bg="#333333", fg="pink").place(x=200, y=360)
        self.ville=Entry(self.page, font=self.fonts)
        self.ville.place(x=380, y=360)
        
        Label(self.page, text="Secteur d'activité: ", font=self.fonts, bg="#333333", fg="pink").place(x=200, y=395)
        self.sect_acti=Entry(self.page, font=self.fonts)
        self.sect_acti.place(x=380, y=395)
        
        
        self.page.place(x=200, y=51)

    def enregistre(self):
        if (self.nom.get()=="" or self.email.get()=="" or self.tel.get()=="" or self.quat.get()=="" or self.ville.get()=="" or self.sect_acti.get()==""):
            mb.showwarning("Avertisement","veuillez remplir tout les champs.")
        elif self.email.get()[-10:] !="@gmail.com":
            mb.showwarning("Avertisement","Entrez un email correct.")
        elif (self.tel.get().isdigit()==False):
            mb.showwarning("Avertissement","Mauvais numero.")
        else :
            question = mb.askyesno("confirmation", "vous confirmer que les informations entrez sont correctes? ")
            if question:
                
                id = rd.randint(100,900) +  rd.randint(1,9) +  rd.randint(10,90)
                nom=self.nom.get()
                mail=self.email.get()
                phon=self.tel.get()
                sex=self.i.get()
                quartier=self.quat.get()
                ville=self.ville.get()
                sec_activi=self.sect_acti.get()
                params=(id,nom,mail,phon,ville,sec_activi,sex,quartier)
                request = "insert into Client values(?,?,?,?,?,?,?,?)"
                try:
                    info_user=set_execute_request_with_params(request,params)
                    mb.showinfo("Enregistrer","Le client a été  enregistré.")
                    self.quat.delete(0, END)
                    self.sect_acti.delete(0, END)
                    self.tel.delete(0, END)
                    self.email.delete(0, END)
                    self.nom.delete(0, END)
                    self.ville.delete(0, END)

                
                except Exception as e:
                    print('Erreur :',e)
                    
            else:
                mb.showinfo("Verification","Verifier donc les informations") 
            
            
    def effacer(self):
        test=mb.askyesno("confirmer", "Voulez- vous vraiment vider tous les champs ? ")
        if test:
            self.quat.delete(0,END)
            self.sect_acti.delete(0,END)
            self.tel.delete(0,END)
            self.email.delete(0,END)
            self.nom.delete(0,END)
            self.ville.delete(0,END)