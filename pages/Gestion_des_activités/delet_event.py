from tkinter import *
from tkinter.font  import Font
from tkinter import messagebox as mb

from backend.requests_db import set_execute_request_with_params, get_execute_request_with_params


class delete_event :
    def __init__(self,root,width,height):
        self.fonts = ('Arial',14,'bold')
        self.page = Canvas(root,width=width,height=height,bg="#333333")
        self.font = Font(family="Helvetica", size=12, underline=True, slant="italic", weight="bold")
        
        Label(self.page, text="2.       Suppresion d'un rendez-vous.", font=self.font, bg="#333333",
              fg="pink").place(x=20, y=20)
        
        Label(self.page,text="Quel Rendez-vous voulez vous supprimer?. " ,font=self.fonts, bg="#333333",fg="pink" ).place(x=130,y=80)
        self.fonts = ('Arial',14,'bold')
        
        Label(self.page, text="Entrez l'identifiant du rendez-vous (NB: se renseigner dans la liste de vos Rendez-vous)"
              , font=self.fonts, bg="#333333", fg="pink").place(x=130, y=150)
        
        self.id=Entry(self.page, font=self.fonts)
        self.id.place(x=130, y=199)

        Button(self.page,text="Supprimmer ",font=self.fonts, bg="blue",fg="cadetblue1",command=self.supprimer).place(x=215,y=400)
        Button(self.page, text="vider le champ ", font=self.fonts, bg="orange", fg="cadetblue1"
               , command=self.effacer, activebackground="#333333", activeforeground="red").place(x=415, y=400)

        self.page.place(x=200,y=51)
        
    def effacer(self):
        test=mb.askyesno("confirmer", "Voulez- vous vraiment vider tous les champs ? ")
        if test:
            self.id.delete(0,END)

    def supprimer(self):
        if (self.id.get() == ""):
            mb.showwarning("Avertissement", "Veuiller entrer l'Id du rendez-vous")
        else:
            question = mb.askyesno("Confirmation", "le rendez-vous vas etre definitivement supprimmer , confirmer vous? ")
            if question:
                Id= self.id.get()
                params = (Id)
                request_select = "select * from Event where id=?"
                info_request = get_execute_request_with_params(request_select, [params])
                if len(info_request) == 0:
                    mb.showinfo("Avertissement", "le Rendez-vous entré n'existe pas , recommencer.")
                else:
                    request_supprimer = "delete from Event where id=? "
                    try:
                        set_execute_request_with_params(request_supprimer, [params])
                        mb.showinfo("supprimer", "le rendez-vous a été supprimer.")
                        self.id.delete(0, END)

                    except:
                        mb.showerror("Erreur", " une erreur c'est produit")

            else:
                mb.showinfo("non confirmé", "verifier de nouveaux l'Id")

