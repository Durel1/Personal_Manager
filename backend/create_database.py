# importation des dependances...
import sqlite3 as sq

# creation de la table User
cree_table_utilisateur = """ 
CREATE TABLE IF NOT EXISTS User  (
    id INTEGER  PRIMARY KEY,
    fullname text NOT NULL,
    password MOT NULL,
    email text NOT NULL, 
    phone text NOT NULL,
    gender text NOT NULL
    )"""

# creation de la table evenement
cree_table_Event = """
CREATE TABLE IF NOT EXISTS Event (
    id integer  PRIMARY KEY,
    meet_with text NOT NULL,
    gender text NOT NULL,
    phone text NOT NULL,
    place text NOT NULL,
    event_status text NOT NULL,
    reason_event text NOT NULL, 
    eventdate text NOT NULL ,
    hour_event text NOT NULL 
    )"""

# creation table client
cree_table_client = """
CREATE TABLE IF NOT EXISTS Client (
    id integer  PRIMARY KEY,
    fullname text NOT NULL , 
    email text NOT NULL , 
    phone interger NOT NULL , 
    city text NOT NULL ,
    sector text NOT NULL ,
    gender text NOT NULL , 
    quater text NOT NULL 
    )"""

cree_table_employer = """ 
CREATE TABLE IF NOT EXISTS Employee (
    id integer PRIMARY KEY,
    fullname text NOT NULL ,
    email text NOT NULL ,
    phone interger NOT NULL ,
    gender text NOT NULL 
    )"""

# creation table finance
cree_table_finance = """
CREATE TABLE IF NOT EXISTS Finance (
    id  integer PRIMARY KEY,
    reason text NOT NULL , 
    amount integer NOT NULL,
    date text NOT NULL,
    status text NOT NULL,
    type text NOT NULL
    )"""


# creation de la classe database 

class Database:
    def __init__(self):
        # creation de la base de donnees .
        self.my_database = sq.connect("projet_stage.db")
        
        # creation du curseur pour executer/parcourir notre base de donnees ...
        self.curseur = self.my_database.cursor()
        
        # appel de la fonction de creation des tables.
        self.CreateTable()
    
    def CreateTable(self):
        # execution de nos requetes
        self.curseur.execute(cree_table_utilisateur)
        self.curseur.execute(cree_table_finance)
        self.curseur.execute(cree_table_employer)
        self.curseur.execute(cree_table_client)
        self.curseur.execute(cree_table_Event)
        
        # mise a jour des modifications dans la base de donnees ...
        self.my_database.commit()
        
            
        