import numpy as np
from itertools import compress
import transcription as tr       
import pandas as pd
import analyse_profile as ap
import analyse_type as at


def generation_graphe_complet(nb,calcul_1=True,liste_matrice_clients_backup = None,juste_graphe = False):
    """
    Genere tout les objets créer au cours des dernières semaines pour nb clients
    int -> unit
    """
    
    nbk = int(nb/1000)
    if calcul_1 :
        #Ouverture des tables detentions
        
        liste_matrice_detention = []
        for i in range(1,17):
            liste_matrice_detention.append(tr.open_file_extract('detention',i))
            print('Avancement : ',100*i/16, ' %', end = '\r')
    
        print('Tables de detentions ouvertes')
    
        #Creation des matrices clients
    
        liste_produits = creation_liste_produits(liste_matrice_detention)
        liste_clients = creation_liste_clients(liste_matrice_detention,nb)
        liste_matrice_clients = creation_matrice_clients(liste_matrice_detention,liste_produits,liste_clients)
    
        tr.save_file(liste_matrice_clients,('liste_matrice_clients_{}k').format(nbk))
    
        print('Matrices clients créées')
    
        liste_matrice_detention = []
    
    #Generation du graphe
    if liste_matrice_clients_backup == None :
        Graphe = remplir_graphe2(liste_matrice_clients)
        
    else :
        Graphe = remplir_graphe2(liste_matrice_clients_backup)
        
    tr.save_file(Graphe,'Graphe_{}k'.format(nbk))

    print('Graphe créé')
    
    #Ouverture des tables profil
    if not(juste_graphe):
        liste_prof_comp = []
        for i in range(1,17):
            liste_prof_comp.append(tr.open_file_extract('profil',i))
            print('Avancement : ',100*i/16, ' %', end = '\r')

        
        print('Tables profil ouvertes')
        
        #Generation de la table des changements sur le profil ainsi que la liste des clients par type

        liste_prof = [] 
        for i in range(1,17):
            liste_prof.append(ap.simplification_df(liste_prof_comp[i],liste_clients))
        tr.save_file(liste_prof,('liste_prof_{}k').format(nbk))
    
        df_final = ap.importance_col_gal(liste_prof,Graphe.liste_client_changeant)
        df_final_expl = ap.changements(liste_prof,Graphe)
    
        tr.save_file(df_final,('df_final_{}k').format(nbk))
        tr.save_file(df_final_expl,('df_final_expl_{}k').format(nbk))
    
        numr_pers_type_1 =at.segmentation_type_1(liste_prof)
        numr_pers_type_2 =at.segmentation_type_2(liste_prof)
        numr_pers_type_3 =at.segmentation_type_3(liste_prof)
        tr.save_file([numr_pers_type_1,numr_pers_type_2,numr_pers_type_3],('numr_pers_type_{}k').format(nbk))

        liste_prof_comp = []
        liste_prof = []
    
        print('DataFrame changements créés')
    print('Generation',nbk,'k terminée')    
	
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

def trouver_indice2(liste_noeuds,vecteur_client):
    """
    Renvoie le numéro de l'equipement correspondant à 
    l'equipement vecteur_client
    (list,ndarray) -> int
    """    
    return np.argwhere(np.all(liste_noeuds == vecteur_client,axis = 1))[0, 0]    

def ajouter_matrice_sommets2(matrice_client,matrice_sommets):
    """
    Ajoute les nouveaux équipements de matrice_client
    à la matrice des sommets
    (ndarray,ndarray) -> ndarray
    """
    d=len(matrice_client[0])
    if not matrice_sommets:
        matrice_sommets.append(matrice_client[:,0]) 
    for jj in range(d):
        #pdb.set_trace()
        if not(np.any(np.all(matrice_sommets == matrice_client[:,jj],axis = 1))) : 
              matrice_sommets.append(matrice_client[:,jj]) 
    return matrice_sommets

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

def remplir_graphe_inter2(matrice_client_avant,matrice_client_apres,matrice_adj,matrice_sommmets,
                         liste_clients):
    """
    incremente les arretes du graphe en regardant les changements
    dans les matrice clients d'un mois à l'autre
    (ndarray,ndarray,ndarray,list) -> list
    """
    liste_client_changeant = [] 
    #Garder une trace des clients ayant changé d'équipements
    for client in liste_clients:
        i_client = liste_clients.index(client)
        if not(np.all(matrice_client_avant[:,i_client] == matrice_client_apres[:,i_client])):
            i0 = trouver_indice2(matrice_sommmets,matrice_client_avant[:,i_client])
            j0 = trouver_indice2(matrice_sommmets,matrice_client_apres[:,i_client])
            matrice_adj[i0][j0] += 1
            liste_client_changeant.append((client,(i0,j0)))
    return liste_client_changeant

def remplir_graphe2(liste_matrices_clients):
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
        matrice_sommets = ajouter_matrice_sommets2(elt,matrice_sommets)
    
    #Création des arrêtes
    m = len(matrice_sommets)
    matrice_adjacence = np.zeros((m,m),dtype='int8')
    n = len(liste_matrices_clients[0])
    for i in range(1, n):
        liste_client_changeant_temp = remplir_graphe_inter2(liste_matrices_clients[0][i-1],liste_matrices_clients[0][i],
                                                           matrice_adjacence,matrice_sommets,liste_matrices_clients[2])
        liste_client_changeant.append(liste_client_changeant_temp)
        print('Avancement : ',100*i/(n-1), ' %', end = '\r')
        
    return tr.graph((liste_client_changeant,np.array(matrice_adjacence),matrice_sommets,liste_matrices_clients[1],liste_matrices_clients[2]))



def remplir_graphe_inter(matrice_client_avant,matrice_client_apres,matrice_adj,matrice_sommmets,
                         liste_clients_avant,liste_clients_apres):
    """
    incremente les arretes du graphe en regardant les changements
    dans les matrice clients d'un mois à l'autre
    (ndarray,ndarray,ndarray,list) -> list
    """
    liste_client_changeant = [] 
    #Garder une trace des clients ayant changé d'équipements
    for client in liste_clients_avant:
        i_client_avant = liste_clients_avant.index(client)
        i_client_apres = liste_clients_apres.index(client)
        if not(np.all(matrice_client_avant[:,i_client_avant] == matrice_client_apres[:,i_client_apres])):
            i0 = trouver_indice(matrice_sommmets,matrice_client_avant[:,i_client_avant])
            j0 = trouver_indice(matrice_sommmets,matrice_client_apres[:,i_client_apres])
            matrice_adj[i0][j0] += 1
            liste_client_changeant.append((client,(i0,j0)))
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
        liste_client_changeant_temp = remplir_graphe_inter(liste_matrices_clients[0][i-1],liste_matrices_clients[0][i],
                                                           matrice_adjacence,matrice_sommets,liste_matrices_clients[2][i-1],
                                                           liste_matrices_clients[2][i])
        liste_client_changeant.append(liste_client_changeant_temp)
    
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



def creation_liste_clients(L,nb = 1000):
    """
    Renvoie la liste des nb premiers NUMR_PERS 
    présent chaque mois
    (list,int) -> list
    """
    liste_clients = L[0]['NUMR_PERS'].unique().tolist()
    for table in L[1:] :
        liste_clients = list(set(list(liste_clients)).intersection(table['NUMR_PERS'].unique().tolist()))
    return liste_clients[:nb]



def creation_matrice_clients(L,liste_produits,liste_clients):
    """
    Renvoie la liste des matrices clients sur les 16 derniers mois ainsi que la liste des produits 
    et la liste des clients
    (list,list) -> (list,list,list)
    """
    Liste_matrices_clients = []
    for table in L:
        table = pd.concat([table.loc[table.NUMR_PERS == i] for i in liste_clients])
        #On crée un objet groupby qui permettra de sortir un dictionnaire dont les clés sont les valeurs distinctes
        #de CODE_ORGN_FINN, NUMR_PERS et les valeurs, les indices des lignes dont la valeur de
        #CODE_ORGN_FINN, NUMR_PERS est la valeur de la clé
        gb = table.groupby(by=['CODE_ORGN_FINN','NUMR_PERS'])
        
        #Obligé de repasser par de recréer une liste produit car la création de celle ci
        #dans la fonction juste au dessus n'est pas forcement trié dans le bonne ordre
        #i.e. celui de gb
        df_prod = table['CODE_PRDT']
        matrice_clients = np.zeros((len(liste_produits),len(liste_clients)),dtype='int8')
        
        #Ainsi on peut créer la liste liste_clients en y mettant toutes les clés du dictionnaire gb.groups
        
        #idx_clients permets de ranger les clients dans la matrice client puisque
        #le dictionnaire gb.groups n'est pas indicé
        idx_clients = 0
        
        for k, v in gb.groups.items():
            #La liste client_produit va contenir tout les code produits du client k
            client_produits = df_prod[v].tolist()
            #idx_produit va contenir la liste des indices de liste_produits 
            #pour lesquelles le client k possède 
            idx_produit = list(compress(range(len(liste_produits)), [x in client_produits for x in liste_produits]))
                
            matrice_clients[idx_produit, idx_clients] = 1
            idx_clients += 1
        Liste_matrices_clients.append(matrice_clients)
    return (Liste_matrices_clients,liste_produits,liste_clients)
