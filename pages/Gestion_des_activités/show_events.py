from tkinter import *
from tkinter import ttk
from tkinter.font import Font

from backend.requests_db import get_execute_request_without_params, get_execute_request_with_params


class all_event:
    def __init__(self, root, width, height):
        self.fonts = ('Arial', 14, 'bold')
        self.width=width
        self.height=height
        ################# creation du canvas d'affichage ##################
        self.font = Font(family="Helvetica", size=12, underline=True, slant="italic", weight="bold")

        self.page = Canvas(root, width=self.width, height=self.height, bg="#333333")
        Label(self.page, text="3.       Consulter vos different rendez-vous.", font=self.font, bg="#333333",
              fg="pink").place(x=20, y=20)

        #creation de notre treeview

        fenetre=ttk.Treeview(self.page,columns = (1,2,3,4,5,6,7,8,9),heigh=5, show = "headings")

        fenetre.heading(1,text="ID")
        fenetre.heading(2,text="Nom")
        fenetre.heading(3,text="Sexe")
        fenetre.heading(4,text="Contact")
        fenetre.heading(5,text="Lieu")
        fenetre.heading(6,text="Status")
        fenetre.heading(7,text="Motif")
        fenetre.heading(8,text="Date")
        fenetre.heading(9,text="Heure")




        fenetre.column(1,width=55)
        fenetre.column(2,width=70)
        fenetre.column(3,width=50)
        fenetre.column(4,width=70)
        fenetre.column(5,width=70)
        fenetre.column(6,width=60)
        fenetre.column(7,width=80)
        fenetre.column(8,width=50)
        fenetre.column(9,width=50)

        fenetre.place(x=self.width/7,y=self.height/3,width=700,height=200)

        request = "select * from Event"

        self.select = get_execute_request_without_params(request)
        for i in self.select:
            fenetre.insert('', END, values=i)


        # affichage du nombre d'employer
        param1="Non Effectué"
        param2="Effectué"

        request1 = "select * from Event where event_status=?"


        NbreRendezVousNonTraites = len(get_execute_request_with_params(request1,[param1]))
        NbreRendezVousTraites = len(get_execute_request_with_params(request1,[param2]))

        Label(self.page,
                text=f"vous avez {str(NbreRendezVousNonTraites)} Rendez-vous en cour \n et {str(NbreRendezVousTraites)} déja effectués"
                , font=self.fonts, bg="#333333",
                  fg="pink").place(x=self.width - 650, y=self.height - 100)

        self.page.place(x=200, y=51)