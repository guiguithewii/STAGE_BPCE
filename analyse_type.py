# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 16:29:43 2019

@author: GIACOMONI
"""


def clients_inactif(table):
    """
    Renvoie la liste des clients inactifs dans la table table
    DataFrame -> list
    """
    res = []
    res += table.loc[table.CODE_SEGM_COMP.str.strip() == 'SAI'].NUMR_PERS.tolist()
    res += table.loc[table.CODE_SEGM_COMP.str.strip() == 'SA'].NUMR_PERS.tolist()
    res += table.loc[table.CODE_SEGM_COMP.isnull()].NUMR_PERS.tolist()
    
    return res

def clients_actif(table):
    """
    Renvoie la liste des clients actifs dans la table table
    DataFrame -> list
    """
    return list(set(table.NUMR_PERS)-set(clients_inactif(table)))

def segmentation_type_1(liste_tables):
    """
    Renvoie la liste des clients de type 1
    list -> list
    """
    clients_type_1 = []
    for mois in range(len(liste_tables)-1) :
        actifs0 = clients_actif(liste_tables[mois])
        clients1 = liste_tables[mois + 1].NUMR_PERS.tolist()
        actifs1 = clients_actif(liste_tables[mois + 1])
        clients_type_1.append(list(set(actifs0).intersection(clients1).difference(actifs1)))
    return clients_type_1
        
        
def segmentation_type_2(liste_tables):
    """
    Renvoie la liste des clients de type 2
    list -> list
    """
    clients_type_2 = []
    for mois in range(len(liste_tables)-1) :
        inactifs0 = clients_inactif(liste_tables[mois])
        clients1 = liste_tables[mois + 1].NUMR_PERS.tolist()
        actifs1 = clients_actif(liste_tables[mois + 1])
        clients_type_2.append(list(set(inactifs0).intersection(clients1).intersection(actifs1)))
    return clients_type_2 

    
def segmentation_type_3(liste_tables):
    """
    Renvoie la liste des clients de type 3
    list -> list
    """
    clients_type_3 = []
    for mois in range(len(liste_tables)-1) :
        actifs0 = clients_actif(liste_tables[mois])
        actifs1 = clients_actif(liste_tables[mois + 1])
        clients_type_3.append(list(set(actifs0).intersection(actifs1)))
    return clients_type_3      

def croisement_slicing(liste_numr_pers,liste_clients):
    """
    Renvoie la liste des clients de type
    1, 2, 3 compris dans liste_clients
    (list,list) -> list
    """
    
    for i in range(3):
        liste_numr_pers[i] = set(liste_clients).intersection(liste_numr_pers[i])
    
    return liste_numr_pers
      