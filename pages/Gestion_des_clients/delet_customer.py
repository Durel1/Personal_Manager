from tkinter import *
from tkinter.font import Font
from tkinter import messagebox as mb

from backend.requests_db import get_execute_request_with_params, set_execute_request_with_params

class delete_clients:
    def __init__(self, root, width, height):
        self.fonts = ('Arial', 14, 'bold')
        self.page = Canvas(root, width=width, height=height, bg="#333333")
        self.font = Font(family="Helvetica", size=12, underline=True, slant="italic", weight="bold")

        self.label=Label(self.page, text="2.     supprimer un  client :", font=self.font, bg="#333333", fg="pink")
        self.label.place(x=20, y=20)
        
        self.label=Label(self.page, text="Quels Clients voulez-vous supprimer?   . ", font=self.fonts, bg="#333333",fg="pink")
        self.label.place(x=130, y=80)
        
        self.label=Label(self.page, text="Email :  ", font=self.fonts, bg="#333333", fg="pink").place(x=200, y=210)
        self.email=Entry(self.page, font=self.fonts)
        self.email.place(x=360, y=210)
        
        Button(self.page, text="Supprimer", font=self.fonts, activebackground="#333333", activeforeground="blue", bg="blue", fg="cadetblue1",command=self.supprime_client).place(x=215, y=320)
        Button(self.page, text="vider le champ", activebackground="#333333", activeforeground="red", font=self.fonts, bg="orange", fg="cadetblue1",command=self.effacer).place(x=400, y=320)

        # Button(
        #   self.page, text="Go to home",
        #  command=lambda :HomePage(self.page, width=800, height=500),font=self.fonts, bg="#333333",fg="cadetblue1").place(x=510, y=320)
        self.page.place(x=200, y=51)


    def effacer(self):
        test=mb.askyesno("confirmer","vous confirmer que les informations entrez sont correctes? ")
        if test:
            self.email.delete(0,END)
    
    def supprime_client(self):
        if (self.email.get()==""):
            mb.showwarning("Avertissement","Veuiller entrer un email")
        else:
            question=mb.askyesno("Confirmation","le client vas etre definitivement supprimmer , confirmer vous? ")
            if question:
                email=self.email.get()
                params = (email)
                request_select = "select * from Client where email=?"
                info_request = get_execute_request_with_params(request_select,[params])
                if len(info_request)==0:
                    mb.showinfo("Avertissement","l'email entré n'existe pas , recommencer.")
                else:
                    request_supprimer="delete from Client where email=? " 
                    try:
                        set_execute_request_with_params(request_supprimer,[params])
                        mb.showinfo("supprimer","le cient a été supprimer.")
                        self.email.delete(0, END)

                    except:
                        mb.showerror("Erreur"," une erreur c'est produit")   
                        
            else:
                mb.showinfo("non confirmé","verifier de nouveaux l'email")
