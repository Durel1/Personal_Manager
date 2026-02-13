import sqlite3 as sq


# connexion a la base de donnees ...
my_database = sq.connect("projet_stage.db")

# creation du curseur ....
curseur = my_database.cursor()

# creation de la fonction sans parametre ...

def get_execute_request_with_params(request,params):
    curseur.execute(request, params)
    result = curseur.fetchall()
    
    # retour du resultat de la requete ...
    return result

def get_execute_request_without_params(request):
    curseur.execute(request)
    result = curseur.fetchall()
    
    # retour du resultat de la requete ...
    return result


# requetes ayant pour but d'ajouter les donnees dans la base de donnees 
def set_execute_request_with_params(request,params):
    curseur.execute(request,params)
    my_database.commit()
    
def set_execute_request_without_params(request):
    curseur.execute(request)
    my_database.commit()