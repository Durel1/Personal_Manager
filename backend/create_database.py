# importation des dependances...
from backend.connection import connect_database

# creation de la table User
cree_table_utilisateur = """
CREATE TABLE IF NOT EXISTS User  (
    id INTEGER  PRIMARY KEY,
    fullname text NOT NULL,
    password TEXT NOT NULL,
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
    phone TEXT NOT NULL ,
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
    phone TEXT NOT NULL ,
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
    type text NOT NULL,
    due_date TEXT
    )"""


# creation de la classe database

class Database:
    def __init__(self, path=None):
        self.path = path
        self.CreateTable()

    def CreateTable(self):
        with connect_database(self.path) as connection:
            connection.execute('BEGIN IMMEDIATE')
            for sql in (cree_table_utilisateur, cree_table_finance,
                        cree_table_employer, cree_table_client, cree_table_Event):
                connection.execute(sql)
