


import numpy as np
import transcription as tr
from itertools import compress
        

def verif_doublon(l,M):
    """
    Verifie si la liste l est dans la matrice M
    (list,ndarray) -> Bool
    """
    for elt in M:
        if np.all(l==elt) :
            return True
    return False

#à quelle noeud correspond le client A ?
def trouver_indice(liste_noeuds,vecteur_client):
    """
    Renvoie le numéro de l'equipement correspondant à 
    l'equipement vecteur_client
    (list,ndarray) -> int
    """
    for client in range(len(liste_noeuds)):
        if np.all(liste_noeuds[client] == vecteur_client):
            return client


def ajouter_matrice_sommets(matrice_client,matrice_sommets):
    """
    Ajoute les nouveaux équipements de matrice_client
    à la matrice des sommets
    (ndarray,ndarray) -> ndarray
    """
    d=len(matrice_client[0])
    for j in range(d):
        if not(verif_doublon(matrice_client[:,j],matrice_sommets)):
              matrice_sommets.append(matrice_client[:,j])
    return matrice_sommets


def remplir_graphe_inter(matrice_client_avant,matrice_client_après,matrice_adj,matrice_sommmets):
    """
    incremente les arretes du graphe en regardant les changements
    dans les matrice clients d'un mois à l'autre
    (ndarray,ndarray,ndarray,list) -> list
    """
    d= len(matrice_client_avant[0])
    liste_client_changeant = [] 
    #Garder une trace des clients ayant changé d'équipements
    for i in range(d):
        if not(np.all(matrice_client_avant[:,i] == matrice_client_après[:,i])):
            matrice_adj[trouver_indice(matrice_sommmets,matrice_client_avant[:,i])][trouver_indice(matrice_sommmets,matrice_client_après[:,i])] += 1
            liste_client_changeant.append(i)
    return liste_client_changeant

def remplir_graphe(liste_matrices_clients):
    """
    Créer à partir de la liste des matrices clients d'une periode donnée 
    une instance de graph dont les noeuds sont les equipements et les arrêtes les 
    passage d'un noeud à l'autre
    list -> graph
    """
    
    liste_client_changeant=[]
    #Garder une trace des clients ayant changé d'équipements
    matrice_sommets = []
    #Création d'une matrice sommet complète
    for elt in liste_matrices_clients[0]:
        matrice_sommets = ajouter_matrice_sommets(elt,matrice_sommets)
    
    #Création des arrêtes
    m = len(matrice_sommets)
    matrice_adjacence = np.zeros((m,m),dtype='int8')
    for i in range(1,len(liste_matrices_clients[0])):
        liste_client_changeant.append(remplir_graphe_inter(liste_matrices_clients[0][i-1],liste_matrices_clients[0][i],matrice_adjacence,matrice_sommets))
    
    return tr.graph((liste_client_changeant,np.array(matrice_adjacence),matrice_sommets,liste_matrices_clients[1],liste_matrices_clients[2]))


def creation_liste_produits(L):
    """
    Renvoie la liste des codes produits unique
    list -> list
    """
    liste_produits = []
    for elt in L:
        elt = elt.fillna('')
        liste_produits = liste_produits + list((elt['CODE_PRDT']).unique())
        liste_produits = list(set(liste_produits))
    return liste_produits


def creation_matrice_clients(L,liste_produits):
    """
    Renvoie la liste des matrices clients sur les 16 derniers mois ainsi que la liste des produits 
    et la liste des clients
    (list,list) -> (list,list,list)
    """
    Liste_matrices_clients = []
    for table in L:
        
        #On crée un objet groupby qui permettra de sortir un dictionnaire dont les clés sont les valeurs distinctes
        #de CODE_ORGN_FINN, NUMR_PERS et les valeurs, les indices des lignes dont la valeur de
        #CODE_ORGN_FINN, NUMR_PERS est la valeur de la clé
        gb = table.groupby(by=['CODE_ORGN_FINN','NUMR_PERS'])
        
        #Obligé de repasser par de recréer une liste produit car la création de celle ci
        #dans la fonction juste au dessus n'est pas forcement trié dans le bonne ordre
        #i.e. celui de gb
        df_prod = table['CODE_PRDT']
        matrice_clients = np.zeros((len(liste_produits), len(gb.groups)),dtype='int8')
        
        #Ainsi on peut créer la liste liste_clients en y mettant toutes les clés du dictionnaire gb.groups
        liste_clients = []
        
        #idx_clients permets de ranger les clients dans la matrice client puisque
        #le dictionnaire gb.groups n'est pas indicé
        idx_clients = 0
        
        for k, v in gb.groups.items():
            liste_clients.append(k)
            
            #La liste client_produit va contenir tout les code produits du client k
            client_produits = df_prod[v].tolist()
            
            #idx_produit va contenir la liste des indices de liste_produits 
            #pour lesquelles le client k possède 
            idx_produit = list(compress(range(len(liste_produits)), [x in client_produits for x in liste_produits]))
            
            matrice_clients[idx_produit, idx_clients] = 1
            idx_clients += 1
        Liste_matrices_clients.append(matrice_clients)
        
    return (Liste_matrices_clients,liste_produits,liste_clients)
