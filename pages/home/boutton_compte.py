from tkinter import *
from tkinter.font import Font

from backend.requests_db import get_execute_request_with_params


class mon_compte:

    def __init__(self, root, width, height,name):

        self.width=width
        self.height=height
        self.fonts=Font(family="Helvetica",size=13,underline=True,slant="italic",weight="bold")
        self.page=Canvas(root,width=self.width,height=self.height,bg="#7fc3c0")
        self.Nom=name

        Label(self.page, text="consulter vos informations personelles: ",font=self.fonts
              ,bg="#7fc3c0" ,fg="white").place(x=self.width/4,y=60)

        selectName = "select * from User where fullname=?"
        paramName = self.Nom

        selectUser = get_execute_request_with_params(selectName, [paramName])

        Label(self.page,text="NOM Utilisateur : ",font=self.fonts,bg="#7fc3c0").place(x=50,y=200)
        nom= selectUser[0][1]
        Label(self.page,text=f"{nom}" ,font=("arial",12,"roman"),bg="#7fc3c0").place(x=250,y=200)
        tel=selectUser[0][4]
        Label(self.page,text="TEL : ",font=self.fonts,bg="#7fc3c0").place(x=50,y=280)
        Label(self.page,text=f" {tel}" ,font=("arial",12,"roman"),bg="#7fc3c0").place(x=250,y=280)

        Label(self.page, text="Email : ",font=self.fonts,bg="#7fc3c0").place(x=50, y=350)
        email = selectUser[0][3]
        Label(self.page, text=f"{email} ",font=("arial",12,"roman"),bg="#7fc3c0").place(x=250, y=350)

        Label(self.page, text="Mot de passe : ",font=self.fonts,bg="#7fc3c0").place(x=50, y=430)
        password = selectUser[0][2]
        Label(self.page, text=f"{password} ",font=("arial",12,"roman"),bg="#7fc3c0").place(x=250, y=430)



        self.page.place(x=200,y=51)