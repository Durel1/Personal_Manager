from tkinter import *
from tkcalendar import *
from tkinter import messagebox as mb
from tkinter.font import Font
import random as rd

from backend.requests_db import set_execute_request_with_params
from pages.Gestion_des_finance.edit_invoice import EditInvoice


class ajout_facture:

    def __init__(self,root,width,height):

        self.width = width
        self.height = height
############################   création du canvas d'affichage   ######################
        self.page = Canvas(root, width=self.width, height=self.height, bg="#05716c")
        self.font=Font(family="Helvetica",size=12,underline=True,slant="italic",weight="bold")
        Label(self.page, text="2.    Enregistrez les informations de votre facture", fg="black", font=self.font, bg="#05716c").place(x=20, y=20)
        ############### creation du formulaire de renseignement ########################

        ############### entrer la date d'enregistrement de la facture ########################
        Label(self.page, text="Date d'entrer :",fg="black", font=("Arial",14,"bold"),bg="#05716c").place(x=120,y=80)
        self.dat = DateEntry(self.page, bg="#05716c",state="readonly")
        self.dat.place(x=290,y=84)

        ############################## choisissez si c'est un encaissement ou un decaissement #######################
        Label(self.page, text="Est-ce un encaissement ou un décaissement? ",fg="black", font=("Arial",14,"bold"),bg="#05716c").place(x=120,y=120)
        self.i=StringVar()
        button1 = Radiobutton(self.page, text="Encaissement",value="Encaissement",variable=self.i,activeforeground="black",activebackground="#05716c",fg="black", bg="#05716c",font=("Arial",14,"italic"))
        button1.place(x=120,y=150)
        button2=Radiobutton(self.page, text="Décaissement",value="Décaissement", variable=self.i,activeforeground="black",activebackground="#05716c",fg="black", bg="#05716c",font=("Arial",14,"italic"))
        button2.place(x=280,y=150)
        button1.invoke()

##################### bouton des facture traités et non traités ###############################
        Label(self.page, text="STATUS : ",fg="black", font=("Arial",14,"bold"),bg="#05716c").place(x=120,y=200)
        self.j=StringVar()
        bouton1 = Radiobutton(self.page, text="Payée", value="Payée", variable=self.j,activebackground="#05716c",activeforeground="black",fg="black", bg="#05716c", font=("Arial", 12, "italic"))
        bouton1.place(x=250, y=200)
        bouton2 = Radiobutton(self.page, text="Non Payée",value="Non Payée", variable=self.j,activebackground="#05716c",fg="black",activeforeground="white", bg="#05716c", font=("Arial", 12, "italic"))
        bouton2.place(x=350, y=200)
        bouton2.invoke()

        ####################  entrer la date de payement si disponible ####################################
        #Label(self.page, text="Date de payement(facultative) :", fg="black", font=("Arial",14, "bold"), bg="yellow").place(x=120, y=180)
        #self.dat = DateEntry(self.page, bg="yellow").place(x=450, y=184)

        ################# entrez le montant de la facture ##################################
        Label(self.page, text="Entrer le montant de la facture ", fg="black", font=("Arial",14, "bold"), bg="#05716c").place(x=120, y=245)
        self.montant=Entry(self.page, font=("Arial",14,"bold"))
        self.montant.place(x=425,y=245)

        ############################### entrez un identifiant pour differencier les factures #############################
        Label(self.page, text="Motif de la trancactions ", fg="black", font=("Arial",14, "bold"), bg="#05716c").place(x=120, y=300)
        self.motif=Entry(self.page, font=("Arial",14,"bold"))
        self.motif.place(x=425,y=300)

        ##################### bouton d'enregistrement et pour vider les champs #######################################

        Button(self.page,text="        Enregistrer        ",font=("Arial",14,"italic"),fg="white",
               bg="blue",activebackground="#05716c",activeforeground="blue",command=self.enregistre).place(x=215,y=375)
        Button(self.page, text="          Effacer          ", font=("arial",14,"italic"), bg="orange", fg="white",
               activebackground="#05716c", activeforeground="red", command=self.supprimer).place(x=430, y=375)

        #################################  affichage du canvas principale #####################
        self.page.place(x=200, y=51)

    def enregistre(self):
            test=mb.askyesno("confirmer","vous confirmer que les informations entrez sont correctes? ")
            if test:
                self.finance_ajout()
    def supprimer(self):
            test=mb.askyesno("confirmer","Voulez- vous vraiment vider tous les champs ? ")
            if test:
                self.motif.delete(0,END)
                self.montant.delete(0,END)
                self.dat.delete(0,END)

    def finance_ajout(self):

        id = rd.randint(100,900) +  rd.randint(1,9) +  rd.randint(10,90)

        date = self.dat.get()
        type = self.i.get()
        status = self.j.get()
        montant = self.montant.get()
        motif = self.motif.get()

        if date == "" or montant == "" or motif == "":
            mb.showwarning("Avertissement","Veuillez remplir tous les champs")
        elif montant.isdigit()==False:
            mb.showwarning("Erreur","Montant incorrect")
        else:
            params=(id,motif,montant,date,status,type)
            request="insert into Finance values(?,?,?,?,?,?)"

            try:
                set_execute_request_with_params(request, params)
                mb.showinfo("enregistrer", "vos informations ont bien été enregistrer")
                self.motif.delete(0, END)
                self.montant.delete(0, END)
                self.dat.delete(0, END)

            except Exception :
                mb.showwarning('Erreur', "Erreur d'enregistrement")

