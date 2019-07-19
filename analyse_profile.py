# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 10:58:48 2019

@author: GIACOMONI
"""

import pandas as pd
import matplotlib.pyplot as plt



def changements(liste_prof_16,g):
    """
    Identifie et explicite tout les changements dans la table profil
    pour les clients ayant changés d'équipement 
    sur les 16 derniers mois
    (list,list) -> DataFrame
    """
    
    #Initialisation

    columns =['ND_DPRT','ND_ARRV'] + list(liste_prof_16[0].columns)
    df = pd.DataFrame(0,index = [],columns = columns)
    index_df = 0
    #Remplissage
    n = len(liste_prof_16)
    for mois in range(1,n):
        for client_changeant in g.liste_client_changeant[mois-1]:
            numr_pers = client_changeant[0] 
            statut_depart = liste_prof_16[mois - 1][liste_prof_16[mois - 1].NUMR_PERS == numr_pers].fillna('')
            statut_mois = liste_prof_16[mois][liste_prof_16[mois].NUMR_PERS == numr_pers].fillna('')     
            diff = list((statut_depart.values != statut_mois.values)[0])
            det_depart = g.lire_noeud_complet(client_changeant[1][0])
            det_arrivee = g.lire_noeud_complet(client_changeant[1][1])
            diff_temp = [[det_depart,det_arrivee] +
                         [[statut_depart[columns[i+2]],statut_mois[columns[i+2]]] if diff[i] 
                         else None for i in range(len(diff))]]
            diff_final = pd.DataFrame(diff_temp,index = [index_df], columns=columns)
            df = pd.concat([df,diff_final])
            index_df += 1
        print('Avancement : ',100*mois/(n-1), ' %', end = '\r')
    return df


def changements_custom(liste_prof_16,liste,g):
    """
    Identifie et explicite tout les changements dans la table profil
    pour les clients ayant changés d'équipement 
    sur les 16 derniers mois
    (list,list) -> DataFrame
    """
    
    #Initialisation

    columns =['ND_DPRT','ND_ARRV'] + list(liste_prof_16[0].columns)
    df = pd.DataFrame(0,index = [],columns = columns)
    index_df = 0
    #Remplissage
    for mois in range(1,16):
        for client_changeant in liste[mois-1]:
            numr_pers = client_changeant[0] 
            statut_depart = liste_prof_16[mois - 1][liste_prof_16[mois - 1].NUMR_PERS == numr_pers]
            statut_mois = liste_prof_16[mois][liste_prof_16[mois].NUMR_PERS == numr_pers]        
            diff = list((statut_depart.values != statut_mois.values)[0])
            det_depart = g.lire_noeud_complet(client_changeant[1][0])
            det_arrivee = g.lire_noeud_complet(client_changeant[1][1])
            diff_temp = [[det_depart,det_arrivee] +
                         [[statut_depart[columns[i+2]],statut_mois[columns[i+2]]] if diff[i] 
                         else None for i in range(len(diff))]]
            diff_final = pd.DataFrame(diff_temp,index = [index_df], columns=columns)
            df = pd.concat([df,diff_final])
            index_df += 1
    return df

def importance_col_partiel(liste_prof_16,liste_clients_changeant,mois):
    """
    Identifie tout les changements dans la table profil pour les clients ayant changés d'équipement 
    entre mois - 1 et mois
    (list,list,int) -> (DataFrame,int)
    """
    
    #Initialisation

    columns =['ND_DPRT','ND_ARRV'] + list(liste_prof_16[0].columns)
    index_df = []
    
    for changement in liste_clients_changeant[mois - 1]:
        index_df.append(changement[1])
    index_df = list(set(index_df))
    
    df = pd.DataFrame(0,index =range(len(index_df)),columns = columns)
    for  index in range(len(index_df)) :
        df['ND_DPRT'][index] = index_df[index][0]
        df['ND_ARRV'][index] = index_df[index][1]
        
    #Remplissage
    
    for client_changeant in liste_clients_changeant[mois-1]:
        numr_pers = client_changeant[0]
        statut_depart = liste_prof_16[mois - 1][liste_prof_16[mois - 1].NUMR_PERS == numr_pers]
        statut_mois = liste_prof_16[mois][liste_prof_16[mois].NUMR_PERS == numr_pers]
        diff = list((statut_depart.values != statut_mois.values).astype(int)[0])
        diff = [0, 0] + diff
        sel = (df.ND_DPRT == client_changeant[1][0]) & (df.ND_ARRV == client_changeant[1][1])
        df.loc[sel] =  df.loc[sel]  + diff
        
    return df

def importance_col_gal(liste_prof_16,liste_clients_changeant):
    """
    Identifie tout les changements dans la table profil pour les clients ayant changés d'équipement 
    entre janvier 2018 et avril 2019
    (list,list,list) -> (DataFrame,int)
    """
    
    #Initialisation

    columns =['ND_DPRT','ND_ARRV'] + list(liste_prof_16[0].columns)
    index_df = []
    for mois in range(1,16):
        for changement in liste_clients_changeant[mois - 1]:
            index_df.append(changement[1])
        index_df = list(set(index_df))
    
    df = pd.DataFrame(0,index =range(len(index_df)),columns = columns)
    for  index in range(len(index_df)) :
        df['ND_DPRT'][index] = index_df[index][0]
        df['ND_ARRV'][index] = index_df[index][1]
        
    #Remplissage
    for mois in range(1,16):
        for client_changeant in liste_clients_changeant[mois-1]:
            numr_pers = client_changeant[0] 
            statut_depart = liste_prof_16[mois - 1][liste_prof_16[mois - 1].NUMR_PERS == numr_pers]
            statut_mois = liste_prof_16[mois][liste_prof_16[mois].NUMR_PERS == numr_pers]
            diff = list((statut_depart.values != statut_mois.values).astype(int)[0])
            diff = [0, 0] + diff
            sel = (df.ND_DPRT == client_changeant[1][0]) & (df.ND_ARRV == client_changeant[1][1])
            df.loc[sel] =  df.loc[sel]  + diff
        
        print('Avancement : ',100*mois/15, ' %', end = '\r')
    
    return df

def simplification_df(df,liste_clients):
    """
    Supprime les clients inactifs et 
    réduit la base pour la faire correspondre à celle de detention
    DataFrame -> DataFrame
    """
    """
    df = df.drop(df.loc[df.CODE_SEGM_COMP.str.strip() == 'SAI' ].index.values.tolist(),axis = 0)
    df = df.drop(df.loc[df.CODE_SEGM_COMP.isnull()].index.values.tolist(),axis = 0)
    df = df.drop(df.loc[df.CODE_SEGM_COMP.str.strip() == 'SA' ].index.values.tolist(),axis = 0)
    """
    
    return pd.concat([df.loc[df.NUMR_PERS == i] for i in liste_clients])

def traduire_df(df,Graphe):
    """
    Remplace les numeros des noeuds par leur contenu dans le dataframe df
    et renvoie le dataframe ainsi traduit
    (DataFrame,graph) -> DataFrame
    """
    for i in range(len(df)):
        index_df = df.index
        df.ND_DPRT.loc[index_df[i]] = Graphe.lire_noeud_complet(df.ND_DPRT.loc[index_df[i]])
        df.ND_ARRV.loc[index_df[i]] = Graphe.lire_noeud_complet(df.ND_ARRV.loc[index_df[i]])
    return df

def col_dispensables(df,valeur_min = 0, valeur_max = 1):
    """
    Renvoie un dictionaire dont les clés sont des colonnes du 
    DataFrame où le pourcentage de changement est compris entre valeur_min et valeur_max
    et les valeurs ce pourcentage.
    Le pourcentage de changement représente le nombre de changements dans la colonne ramené
    au nombre de mois et sur 100
    (DataFrame,int,int) -> dict
    """
    col_dispensables = []
    maximum = sum(df['PERD_ARRT_INFO'])
    for col in df.columns[3:]:
        if (sum(df[col]) < valeur_min*maximum) or (sum(df[col]) > valeur_max*maximum):
            col_dispensables.append(col)
    
    return col_dispensables
    
def suppression_col_inutiles(df,liste_colonnes):
    """
    Renvoie le DataFrame df sans les colonnes de liste_colonnes
    (DataFrame,list) -> DataFrame
    """
    return df[[col for col in df.columns if (not(col in liste_colonnes))]]

def suppresion_ligne_vide(df,debut=3):
    """
    Renvoie le DataFrame df sans les lignes composées uniquement de None entre debut et le nombre de colonnes
    (DataFrame,int) -> DataFramme
    """
    return df.loc[(~df.iloc[:,debut:].isnull()).any(axis=1)]


def df_sans_cols_lignes_inutiles(df_num,df_expl,valeur_min = 0,valeur_max = 1):
    """
    Renvoie le DataFrame df_expl sans les lignes inutiles et les 
    colonnes trop corélées ou pas assez (entre valeur_min et valeur_max)
    (DataFrame,DataFrame,int,int) -> DataFrame
    """
    return suppresion_ligne_vide((suppression_col_inutiles(df_expl,col_dispensables(df_num,valeur_min,valeur_max))))


def tracer_histogramme(dico,log=False):
    plt.barh(list(dico.keys()), dico.values(), color = 'g', log = log)

def max_dico(dico):
    """
    Renvoie la cle qui donne la valeur max parmis les valeurs de dico 
    dict -> str | int
    """
    max = 0
    res = 'Pas de max'
    for cle in dico.keys():
        if dico[cle] > max :
            max = dico[cle]
            res = cle
    return res,dico[res]

def top_dico(dico,nb=10):
    """
    Renvoie les nb premières valeurs max du dico dico
    (dict,int) -> list
    """
    res = []
    for i in range(nb):
        cle,valeur = max_dico(dico)
        res.append(valeur)
        dico[cle] = 0
    
