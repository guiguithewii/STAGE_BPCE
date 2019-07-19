import numpy as np
import joblib
from os import path

#Maj le 01/07/19 à 12:34


#Maj le 01/07/19 à 15:00

#Maj le 03/07/19 à 17:53



class graph:
    def __init__(self,sortie_graphe):
        self.traducteur = open_file('fichier_traduction')
        self.liste_client_changeant = sortie_graphe[0]
        self.matrice_adj = sortie_graphe[1]
        self.matrice_sommets = sortie_graphe[2]
        self.liste_produits = sortie_graphe[3]
        self.liste_clients = sortie_graphe[4]
        self.nombre_clients = len(self.liste_clients)

    def init_complet(self):
        self.importance_produits() 
        self.clients_non_changeant()
    
    def lire_noeud(self,noeud):
        """
        renvoie la liste des produits qui composent l'equipement du noeud
        int -> list
        """
        res =[]
        for produit in range(len(self.matrice_sommets[noeud])):
            if self.matrice_sommets[noeud][produit] == 1:
                res.append(self.liste_produits[produit])
        return res        
    
    def lire_noeud_complet(self,noeud):
        """
        renvoie la liste des produits qui composent l'equipement du noeud
        int -> list
        """
        res =[]
        for produit in range(len(self.matrice_sommets[noeud])):
            if self.matrice_sommets[noeud][produit] == 1:
                res.append(self.liste_produits[produit])
        return traduire_code_prdt(res,self.traducteur)
           
    
    def changement_produit(self, noeud_i, noeud_j):
        """
        Renvoie la liste des produits perdus du noeud i au noeud j 
        ainsi que la liste des produits gagnes du noeud i au noeud j
        ainsi que le poids de l'arrête allant du noeud i au noeud j
        (int,int,list,list,ndarray) -> (list,list,int)
        """
        liste_produit_i = self.lire_noeud(noeud_i)
        liste_produit_j = self.lire_noeud(noeud_j) 
        return difference_listes(liste_produit_i,liste_produit_j,self.matrice_adj[noeud_i][noeud_j])
    
    def analyse_changements(self,nb=10,pr=False):
        """
        Renvoie la liste  des nb premiers nouveaux equipements
        et anciens equipements
        Si pr est vraie, la fonction affiche la frequence de changements de ce nombre de clients
        (graph,int,int,bool) -> list
        """
        M=np.copy(self.matrice_adj)
        res = []
        
        for i in range(nb):
            i_max,j_max = np.where(M == M.max())[0][0],np.where(M == M.max())[1][0]
            res.append(self.changement_produit(i_max,j_max))
            if pr == True :
                    if res[-1][1] != []:
                        print('Le(s) produit(s)',traduire_code_prdt(res[-1][1],self.traducteur), 'a(ont) ete mis de cote par',100*M[i_max][j_max]/self.nombre_clients,
                              '% des clients de la CEIDF au cours des 16 derniers mois')
                    if res[-1][0] != []:
                        print('Le(s) produit(s)',traduire_code_prdt(res[-1][0],self.traducteur), 'a(ont) ete achetes',100*M[i_max][j_max]/self.nombre_clients,
                              '% des clients de la CEIDF au cours des 16 derniers mois')
            M[i_max][j_max] = -1    
            print('Avancement : ',(i+1)*100/nb, ' %', end = '\r')
        return res
    def noeuds_important(self,nb=10):
        res = (-np.sum(self.matrice_adj,axis = 1)).argsort()[:nb]
        nvres = []
        for elt in res:
            nvres.append(self.lire_noeud_complet(elt))
        return nvres

    def clients_non_changeant(self):
        """
        Renvoie la liste des clients qui ne changent
        pas d'equipement au fil des mois
        graph -> unit
        """
        self.liste_client_non_changeant = []
        self.liste_client_changeant_simple = []
        for liste_mensuel in self.liste_client_changeant:
            liste_mensuel_simple = []
            for client_changeant in liste_mensuel:
                liste_mensuel_simple.append(client_changeant[0])
            self.liste_client_changeant_simple.append(liste_mensuel_simple)
        
        for elt in self.liste_client_changeant_simple:
            res = []
            for client in self.liste_clients:
                if not(client in elt):
                    res.append(client)
            self.liste_client_non_changeant.append(res)
    
    def importance_produits(self):
        """
        Renvoie un dictionnaire dont les cles sont les produits de la CE et les
        valeurs le nombre de clients ayant achetes ce produit au cours de 16 derniers mois
        Une valeur negative indique qu'il y a eu plus de clients s'en debarassant au cours des 16 derniers mois
        que de clients en achetant
        graph -> dict
        """
        produits_changeants = self.analyse_changements(len(np.where(self.matrice_adj > 0)[0]))
        dico = {}
        for produit in self.liste_produits:
            dico[self.traducteur[produit]] =0
        for produit_changeant in produits_changeants:
            for produit_plus in produit_changeant[0]:
                    dico[self.traducteur[produit_plus]] += produit_changeant[2]
            for produit_moins in produit_changeant[1]:
                    dico[self.traducteur[produit_moins]] -= produit_changeant[2]
        self.produits_notes = dico
        return dico

    
    def meilleurs_produits(self,nb=10):
        """
        Renvoie la liste des nb produits avec le meilleur score dans
        self.produits_notes
        (graph,int) ->list
        """
        
        if self.produits_notes is None:
            ValueError("produits_notes not set, run importance_produits")
        
        dico = self.produits_notes.copy()

        maxi = 0
        liste_meilleurs_produits = []
        prd = ''
        for itera in range(nb):
            for cle in self.produits_notes.keys():
                if dico[cle] > maxi:
                    maxi = dico[cle]
                    prd = cle
            dico[prd] = -1000
            maxi = 0
            liste_meilleurs_produits.append(prd)
        self.mieux_notes = liste_meilleurs_produits
        return self.mieux_notes   
    
    def pires_produits(self,nb=10):
        """
        Renvoie la liste des nb produits avec le moins bon score dans
        self.produits_notes
        (graph,int) ->list
        """
  
        if self.produits_notes is None:
            ValueError("produits_notes not set, run importance_produits")
      
        dico = self.produits_notes.copy()

        mini = 1000
        liste_pires_produits = []
        prd = ''
        for itera in range(nb):
            for cle in self.produits_notes.keys():
                if dico[cle] < mini:
                    mini = dico[cle]
                    prd = cle
            dico[prd] = 1000
            mini = 1000
            liste_pires_produits.append(prd)
        self.moins_bien_notes = liste_pires_produits
        return self.moins_bien_notes
    
    def trouver_noeud(self,tableau_det):
        """
        Renvoie le numero du noeud auquel correspond l'equipement
        decrit dans tableau_det
        (graph,ndarray) -> int
        """
        for i in range(len(self.matrice_sommets)):
            if (tableau_det == self.matrice_sommets[i]).all():
                return i 
            
            
    def produits_clients_non_changeants(self,liste_matrice_clients):
        """
        Renvoie un dictionnaire dont les cles sont les produits 
        et les valeurs le nombre de clients non changeant ayant 
        le produit cle
        (graph,list) -> dict
        """
        dico = {}
        for produit in traduire_code_prdt((self.liste_produits),self.traducteur):
            dico[produit] = 0
        for mois in range(len(self.liste_client_non_changeant)):
            for client in self.liste_client_non_changeant[mois]:
                client = self.liste_clients.index(client)
                liste_detention = self.lire_noeud_complet(self.trouver_noeud(liste_matrice_clients[mois][:,client]))
                for produit in liste_detention:
                    dico[produit] += 1
        self.dico_produit_clients_non_changeant = dico
        return dico
    
    def detentions_clients_non_changeants(self,liste_matrice_clients,nb=10):
        """
        Renvoie la liste des nb premiers equipements des clients non changeants
        (graph,list) -> list
        """
        liste_detention = []
        liste_detention_compteur = [0 for i in range(len(self.matrice_sommets))]
        for mois in range(len(self.liste_client_non_changeant)):
            for client in self.liste_client_non_changeant[mois]:
                detention = (self.lire_noeud(self.trouver_noeud(liste_matrice_clients[mois][:,client])))
                if detention in liste_detention:
                    liste_detention_compteur[liste_detention.index(detention)] += 1
                else :
                    liste_detention.append(detention)
        index_liste_detention = sorted(range(len(liste_detention_compteur)), key=lambda k: liste_detention_compteur[k])
        self.equipement_clients_non_changeant = traduire_equipement(tri_par_liste(liste_detention,index_liste_detention,nb),self.traducteur)
        return self.equipement_clients_non_changeant
    
    
    
def tri_par_liste(liste,index,nb):
    liste_trie = liste.copy()
    for i in range(nb):
        liste_trie[i] = liste[index[i]]
    return liste_trie[:nb]
    
def traduire_code_prdt(liste_non_traduite,dico):
    """
    Traduit une liste de code produit en français
    (list,dict) -> list
    """
    liste_traduite = liste_non_traduite.copy()
    for i in range(len(liste_traduite)):
        liste_traduite[i] = str(dico[liste_non_traduite[i]])
    return liste_traduite

def traduire_equipement(liste_equipement,dico):
    """
    Traduit une liste d'equipements en français
    (list,dict) -> list
    """
    liste_traduite = []
    for equipement in liste_equipement:
        liste_traduite.append(traduire_code_prdt(equipement,dico))
    return liste_traduite

def difference_listes(liste_1,liste_2,poids_1_2):
    """
    Renvoie l'ensemble des produits qui apparaissent dans la liste_2 mais pas la 1
    et inversement ainsi que le poids de l'arrête allant de la liste 1 à la liste 2
    (list,list,int) -> (list,list,int)
    """
    for elt1 in liste_1:
        for elt2 in liste_2:
            if elt1 == elt2 :
                liste_1.pop(liste_1.index(elt1))
                liste_2.pop(liste_2.index(elt2))
    return (liste_2,liste_1,poids_1_2)





def save_file(M,nom,mois=16,
    output_dir = r"/data/usersR/jkerboul/tmp/stage_graph/notebooks/Ressources"):
    """
    Enregistre la variable M qui correspond au mois mois et qui s'appelle nom
    """
    output_dir = r"/data/usersR/jkerboul/tmp/stage_graph/notebooks/Ressources"
    if mois < 10:
        outfile = "20180{}_{}_{}.gzip".format(mois,nom, '17515')
        outfile = path.join(output_dir, outfile)

        with open(outfile, "wb+") as fid:
            joblib.dump(M, fid, compress="zlib")
    if mois > 9 and mois < 13:
        outfile = "2018{}_{}_{}.gzip".format(mois,nom, '17515')
        outfile = path.join(output_dir, outfile)

        with open(outfile, "wb+") as fid:
            joblib.dump(M, fid, compress="zlib")
    
    if mois > 12:
        outfile = "20190{}_{}_{}.gzip".format(mois-12,nom, '17515')
        outfile = path.join(output_dir, outfile)

        with open(outfile, "wb+") as fid:
            joblib.dump(M, fid, compress="zlib")


            
def open_file(nom,mois=16,
    output_dir = r"/data/usersR/jkerboul/tmp/stage_graph/notebooks/Ressources"):
    """
    ouvre le fichier qui a pour nom nom au mois mois
    (string,int) -> type(fichier_ouvert)
    """
    if mois < 10:
        outfile = "20180{}_{}_{}.gzip".format(mois,nom, '17515')
        outfile = path.join(output_dir, outfile)
        with open(outfile, "rb") as fid:
            fichier_ouvert = joblib.load(fid)
            return fichier_ouvert
    if mois > 9 and mois < 13:
        outfile = "2018{}_{}_{}.gzip".format(mois,nom, '17515')
        outfile = path.join(output_dir, outfile)
        with open(outfile, "rb") as fid:
            fichier_ouvert = joblib.load(fid)
            return fichier_ouvert 
    
    if mois > 12:
        outfile = "20190{}_{}_{}.gzip".format(mois -12,nom, '17515')
        outfile = path.join(output_dir, outfile)
        with open(outfile, "rb") as fid:
            fichier_ouvert = joblib.load(fid)
            return fichier_ouvert 

def open_file_extract(nom,mois=16):
    """
    ouvre le fichier qui a pour nom nom au mois mois
    (string,int) -> type(fichier_ouvert)
    """
    dir_data2018 = r"/data/usersR/jkerboul/tmp/stage_graph/graph/extraction"
    file_det2018 = r"{dafms}_extract_{nom}_part_vecep_17515.gzip"
    full_det_file2018 = path.join(dir_data2018, file_det2018)
    if mois < 10:
        date='20180{}'
        dafms = date.format(mois)
        with open(full_det_file2018.format(dafms=dafms,nom=nom), "rb") as fid:
            pro2018 = joblib.load(fid)
            return pro2018
    if mois > 9 and mois < 13:
        date='2018{}'
        dafms = date.format(mois)
        with open(full_det_file2018.format(dafms=dafms,nom=nom), "rb") as fid:
            pro2018 = joblib.load(fid)
            return pro2018 
    
    if mois > 12:
        date='20190{}'
        dafms = date.format(mois-12)
        with open(full_det_file2018.format(dafms=dafms,nom=nom), "rb") as fid:
            pro2018 = joblib.load(fid)
            return pro2018 

def save_file_extract(file,nom,mois=16):
    """
    Enregistre le fichier file avec le nom nom au mois mois
    (string,int) -> type(fichier_ouvert)
    """
    dir_data2018 = r"/data/usersR/jkerboul/tmp/stage_graph/graph/extraction"
    file_det2018 = r"{dafms}_extract_{nom}_part_vecep_17515.gzip"
    full_det_file2018 = path.join(dir_data2018, file_det2018)
    if mois < 10:
        date='20180{}'
        dafms = date.format(mois)
        with open(full_det_file2018.format(dafms=dafms,nom=nom), "wb+") as fid:
            joblib.dump(file, fid, compress="zlib")
            
    if mois > 9 and mois < 13:
        date='2018{}'
        dafms = date.format(mois)
        with open(full_det_file2018.format(dafms=dafms,nom=nom), "wb+") as fid:
            joblib.dump(file, fid, compress="zlib")
            
    if mois > 12:
        date='20190{}'
        dafms = date.format(mois-12)
        with open(full_det_file2018.format(dafms=dafms,nom=nom), "wb+") as fid:
            joblib.dump(file, fid, compress="zlib")