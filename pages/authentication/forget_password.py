from tkinter import Canvas, Label, Button
from tkinter import messagebox as mb


class ForgetPassword:
    def __init__(self, root, width, height):
        self.page = Canvas(root, width=width, height=height, bg="#1c141f")
        Label(self.page, text="Mot de passe oublié", fg="white", bg="#1c141f",
              font=("Arial", 28)).place(x=350, y=150)
        Label(self.page, text="Les mots de passe sont protégés et ne peuvent pas être affichés.\n"
              "La réinitialisation sécurisée n’est pas encore disponible.",
              fg="white", bg="#1c141f", font=("Arial", 14)).place(x=300, y=250)
        Button(self.page, text="Retour", command=self.page.destroy).place(x=550, y=350)
        self.page.place(x=0, y=0)

    def getPassword(self):
        # Compatibility with older callbacks; never queries or exposes a secret.
        mb.showinfo("Mot de passe", "La réinitialisation sécurisée n’est pas encore disponible.")
