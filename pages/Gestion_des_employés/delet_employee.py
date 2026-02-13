from tkinter import *
from tkinter import messagebox as mb
from tkinter.font import Font

from backend.requests_db import set_execute_request_with_params, get_execute_request_without_params,get_execute_request_with_params


class delete_employer :
    def __init__(self,root,width,height):
        self.fonts = ('Arial',14,'bold')
        self.page = Canvas(root,width=width,height=height,bg="#1978a5")
        self.font = Font(family="Helvetica", size=12, underline=True, slant="italic", weight="bold")
        Label(self.page,text="2.     Supprimer un employer " ,font=self.font, bg="#1978a5",fg="white" ).place(x=20,y=20)

        Label(self.page,text="Entrer les informations de l'employer a supprimer. " ,font=self.fonts, bg="#1978a5",fg="white" ).place(x=130,y=80)
        self.fonts = ('Arial',14,'bold')
        
        Label(self.page,text="NOM : ",font=self.fonts, bg="#1978a5",fg="white" ).place(x=200,y=150)
        self.nom=Entry(self.page,font=self.fonts)
        self.nom.place(x=290,y=150)
        
        Label(self.page,text="Email : ",font=self.fonts, bg="#1978a5",fg="white" ).place(x=200,y=240)
        self.email=Entry(self.page,font=self.fonts)
        self.email.place(x=290,y=240)
        
        Label(self.page, text="TEL : ", font=self.fonts, bg="#1978a5", fg="white").place(x=200, y=330)
        self.tel=Entry(self.page, font=self.fonts)
        self.tel.place(x=280, y=330)


        self.bouton=Button(self.page, text="Supprimer", font=self.fonts, bg="blue", fg="cadetblue1",activebackground="#1978a5",activeforeground="blue",command=self.enregistre)
        self.bouton.place(x=215, y=400)
        
        self.bouton=Button(self.page, text="vider le champs ", font=self.fonts, bg="orange", fg="cadetblue1",command=self.supprimer,activebackground="#1978a5",activeforeground="red")
        self.bouton.place(x=415, y=400)
        
        
        self.page.place(x=200,y=51)

    def enregistre(self):
        test = mb.askyesno("confirmer", "vous confirmer que les informations entrez sont correctes? ")
        if test:
            self.suppr_employee()

    def supprimer(self):
        test=mb.askyesno("confirmer", "Voulez- vous vraiment vider tous les champs ? ")
        if test:
            self.email.delete(0,END)
            self.nom.delete(0,END)
            self.tel.delete(0,END)

#vider les champ
    def suppr_employee(self):
        nom=self.nom.get()
        email=self.email.get()
        tel=self.tel.get()


        #testez si tous les champs sont remplies
        request = "select * from Employee where (fullname=? and email=? and phone=?)"
        params = (nom,email,tel)
        data = get_execute_request_with_params(request, params)

        if nom=="" or email=="" or tel=="" :
            mb.showwarning("Avertissement","Veuillez remplir tous les champs")
        elif email[-10:] != "@gmail.com":
            mb.showwarning("Erreur","Entrez un mail correct.")
        elif tel.isdigit()==False:
            mb.showwarning("Erreur","Mauvais numéro!!!")
        else:
            if len(data)==0:
                mb.showinfo("Avertissement","les informations entrez n'existe pas!!")

            else:
                request1="delete from Employee where (fullname=? and email=? and phone=?)"
                try:
                    set_execute_request_with_params(request1, params)
                    mb.showinfo("supprimer","l'employé a bien été supprimer!!!")
                    self.email.delete(0, END)
                    self.nom.delete(0, END)
                    self.tel.delete(0, END)
                except:
                    mb.showerror("Erreur","Erreur d'enregistrement")



