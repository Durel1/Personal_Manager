from tkinter import *
import random as rd
import tkcalendar as tk
from tkinter.font import Font
from tkinter import messagebox as mb

from backend.requests_db import set_execute_request_with_params

class add_event:
    def __init__(self, root, width, height):
        self.fonts = ('Arial', 14, 'bold')
        self.page = Canvas(root, width=width, height=height,bg="#1978a5")
        self.font = Font(family="Helvetica", size=12, underline=True, slant="italic", weight="bold")
        Label(self.page, text="1.       Enregitrement de vos rendez vous.", font=self.font, bg="#1978a5",
              fg="pink").place(x=20, y=20)
        
        Label(self.page, text="Entrer les informations du nouveau rendez-vous. ", font=self.fonts, bg="#1978a5",
              fg="pink").place(x=130, y=80)
        
        Label(self.page, text="vous aurez rendez-vous avec : Mr / Mme ", font=self.fonts, bg="#1978a5", fg="pink").place(x=175, y=150)
        self.meet_with=Entry(self.page, font=self.fonts)
        self.meet_with.place(x=560, y=150, width=200)
        
        Label(self.page, text="Sexe: ", font=self.fonts, bg="#1978a5", fg="pink").place(x=175, y=180)
        self.i = StringVar()
        boutonhomme=Radiobutton(self.page, text=" Homme ", value="Homme", variable=self.i, bg="#1978a5", activebackground="#333333",activeforeground="black")
        boutonhomme.place(x=270, y=180)
        boutonfemme=Radiobutton(self.page, text="Femme", value="Femme", variable=self.i, bg="#1978a5", activebackground="#333333",activeforeground="black")
        boutonfemme.place(x=400, y=180)
        boutonhomme.invoke()

        Label(self.page, text="Lieu du rendez-vous : ", font=self.fonts, bg="#1978a5", fg="pink").place(x=175, y=215)
        self.lieu=Entry(self.page, font=self.fonts)
        self.lieu.place(x=420, y=215,width=200)
        
        Label(self.page, text="STATUS : ", fg="pink", font=("Arial", 14, "bold"), bg="#1978a5").place(x=175, y=245)
        self.j = StringVar()
        boutontraite=Radiobutton(self.page, text="Traité", value="Effectué", variable=self.j, bg="#1978a5", font=("Arial", 12, "italic"),activebackground="#333333")
        boutontraite.place(x=270, y=245)
        boutonNontraite=Radiobutton(self.page, text="Non Traité", value="Non Effectué", variable=self.j, bg="#1978a5", font=("Arial", 12, "italic"),activebackground="#333333")
        boutonNontraite.place(x=350, y=245)
        boutonNontraite.invoke()
        
        Label(self.page, text="Date du rendez-vous: ", font=self.fonts,bg="#1978a5", fg="pink").place(x=175, y=295)
        self.date=tk.DateEntry(self.page,state="readonly")
        self.date.place(x=420, y=295,width=160)
        
        Label(self.page, text="Heure du rendez-vous : ", font=self.fonts, bg="#1978a5", fg="pink").place(x=175, y=340)
        self.heur=Spinbox(self.page,from_=00, to=24, width=3)
        self.heur.place(x=420, y=345)
        Label(self.page,text="H",bg="#1978a5",fg="pink",width=1).place(x=450,y=345)
        self.min=Spinbox(self.page, from_=00, to=60, width=3)
        self.min.place(x=465, y=345)
        Label(self.page, text="Mins",width=3,bg="#1978a5",fg="pink").place(x=500,y=345)

        Label(self.page, text="Motif du rendez-vous : ", font=self.fonts, bg="#1978a5", fg="pink").place(x=175, y=380)
        self.reason_event=Entry(self.page, font=self.fonts)
        self.reason_event.place(x=420, y=380, width=200)
        
        Label(self.page, text="Contact: ", font=self.fonts, bg="#1978a5", fg="pink").place(x=175, y=420)
        self.phone=Entry(self.page, font=self.fonts)
        self.phone.place(x=420, y=420, width=200)
        
        Button(self.page, text="  Enregistrer  ", font=self.fonts, bg="blue", fg="white",activebackground="#1978a5"
               ,command=self.enregistre).place(x=220, y=490)
        
        Button(self.page, text="    Effacer    ", font=("arial", 14, "italic"), bg="orange", fg="white",
               activebackground="#333333", activeforeground="white", command=self.effacer).place(x=390, y=490)

        Label(self.page, text="Pour modifier le status d'une factutre pré-enregistrez, cliquez ici : "
              , fg="white", font=("Arial", 9, "bold"), bg="yellow").place(x=width- 200, y=height - 100)

        #Button(self.page, text="  Modif.stat  ", font=("arial", 9, "italic"), bg="blue", fg="white",
         #      activebackground="#1978a5").place(x=width / 2 + 70, y=height - 100)

        self.page.place(x=200, y=51)
    def effacer(self):
        test=mb.askyesno("confirmer", "Voulez- vous vraiment vider tous les champs ? ")
        if test:
            self.reason_event.delete(0,END)
            self.meet_with.delete(0,END)
            self.lieu.delete(0,END)
            self.phone.delete(0,END)

    def enregistre(self):
        if self.meet_with=="" or self.phone=="" or self.lieu.get()=="" or self.reason_event.get()=="" or self.heur=="0"  :
            mb.showwarning("Avertissement","Veuiller remplir tous les champs")
        elif self.phone.get().isdigit()==False:
            mb.showwarning("Erreur","Numéro incorrect")

        else:
            id = rd.randint(100, 900) + rd.randint(1, 9) + rd.randint(10, 90)
            sexe = self.i.get()
            statu = self.j.get()
            params = (id, self.meet_with.get(), sexe, self.phone.get(), self.lieu.get(), statu, self.reason_event.get(),
                      self.date.get(), f"{self.heur.get()} : {self.min.get()}")
            request = "insert into Event values(?,?,?,?,?,?,?,?,?)"
            try:
                info_user = set_execute_request_with_params(request, params)
                mb.showinfo("Enregitrer", "L'événement a été enregistré")
                self.reason_event.delete(0, END)
                self.meet_with.delete(0, END)
                self.lieu.delete(0, END)
                self.phone.delete(0, END)
            except Exception as e:
                print('Erreur :', "Erreur d'enregistrement!!!")

    
             
