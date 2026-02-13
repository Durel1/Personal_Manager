from tkinter import *
from tkinter import ttk
from tkinter.font import Font

from backend.requests_db import get_execute_request_without_params, get_execute_request_with_params
from pages.Gestion_des_finance.edit_invoice import EditInvoice


class all_spending:
    def __init__(self, root, width, height):
        self.fonts = ('Arial', 14, 'bold')
        self.width=width
        self.height=height
        ################# creation du canvas d'affichage ##################

        self.page = Canvas(root, width=self.width, height=self.height, bg="#05716c")
        self.font = Font(family="Helvetica", size=12, underline=True, slant="italic", weight="bold")
        Label(self.page, text="2.    Consulter la listes de vos factures ", fg="white", font=self.font, bg="#05716c").place(x=20, y=20)


        #creation de notre treeview

        fenetre = ttk.Treeview(self.page,columns = (1,2,3,4,5,6),heigh=5, show = "headings")

        fenetre.heading(1,text="ID")
        fenetre.heading(2,text="Motif de la facture")
        fenetre.heading(3,text="Montant")
        fenetre.heading(4,text="Date d'entrer")
        fenetre.heading(5,text="Status")
        fenetre.heading(6,text="type_transaction")


        fenetre.column(1,width=50)
        fenetre.column(2,width=100)
        fenetre.column(3,width=50)
        fenetre.column(4,width=50)
        fenetre.column(5,width=50)
        fenetre.column(6,width=50)



        fenetre.place(x=200,y=200,width=600,height=200)

        ################################  bouton pour modifier le status d'une facture ##############################
        Label(self.page, text="Pour modifier le status d'une factutre pré-enregistrez, entrez l'Id de la facture et cliquez sur Modif.stat : "
              , fg="black", font=("Arial", 9, "bold"), bg="#05716c").place(x=self.width / 8 - 60, y=self.height - 150)
        Entry(self.page,font=("Arial", 9, "bold")).place(x=self.width / 2 +80, y=self.height - 150)
        Button(self.page, text="  Modif.stat  ", font=("arial", 9, "italic"), bg="blue", fg="white",
               activebackground="#05716c", activeforeground="red",
               command=lambda: EditInvoice(self.page, width, height)).place(x=self.width / 2 + 235, y=self.height - 155)

        request="select * from Finance"
        self.select = get_execute_request_without_params(request)
        for item in self.select:
            #print('Recuperation du tuple : ', item)

            formater_data = list(item)
            #print('Conversion du tuple en liste  : ',formater_data)

            formater_data[2] = str(formater_data[2])+' Fcfa'
            #print('Recuperation du montant et ajustement avec la monnaie : ', formater_data)

            #print('Reconversion de la liste en tuple puis insertion dans le Treeview : ')
            new_data = tuple(formater_data)
            fenetre.insert("", END, values=new_data)


        # affichage du nombre d'évenements
        param1="Non Payée"
        param2="Payée"
        request1="select * from Finance where status=?"
        self.NbrFactureTraites = get_execute_request_with_params(request1, [param2])
        request2="select * from Finance where status=?"
        self.NbrFactureNonTraites = get_execute_request_with_params(request2,[param1])
        Label(self.page,text=f"vous avez {len(self.NbrFactureNonTraites)} factures impayée et {len(self.NbrFactureTraites)} factures  payée"
            , font=self.fonts, bg="#05716c", fg="white").place(x=self.width - 780, y=self.height - 100)


        self.page.place(x=200, y=51)