from tkinter import *
from tkinter import ttk
from tkinter.font import Font
from backend.requests_db import get_execute_request_without_params


class all_employer:
    def __init__(self, root, width, height):
        self.fonts = ('Arial', 14, 'bold')
        self.width=width
        self.height=height
        ################# creation du canvas d'affichage ##################

        self.page = Canvas(root, width=self.width, height=self.height, bg="#1978a5")
        self.font = Font(family="Helvetica", size=12, underline=True, slant="italic", weight="bold")
        Label(self.page,text="3.   Consulter la liste de vos employers " ,font=self.font, bg="#1978a5",fg="white" ).place(x=20,y=20)


        #creation de notre treeview

        fenetre=ttk.Treeview(self.page,columns = (1,2,3,4,5),heigh=5, show = "headings")

        fenetre.heading(1,text="Id")
        fenetre.heading(2,text="Nom")
        fenetre.heading(3,text="Email")
        fenetre.heading(4,text="Contacts")
        fenetre.heading(5,text="sexe")


        fenetre.column(1,width=50)
        fenetre.column(2,width=50)
        fenetre.column(3,width=100)
        fenetre.column(4,width=50)
        fenetre.column(5,width=50)




        fenetre.place(x=200,y=150,width=450,height=250)

        request="select * from Employee "

        self.select = get_execute_request_without_params(request)
        for i in self.select:
            fenetre.insert('',END,values=i)

         # affichage du nombre d'employer
        self.nbreemployes = len(self.select)
        Label(self.page, text=f"vous avez {str(self.nbreemployes)} Employés", font=self.fonts, bg="#1978a5",
                  fg="white").place(x=self.width - 500, y=self.height - 110)


        self.page.place(x=200, y=51)




