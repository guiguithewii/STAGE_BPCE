
# coding: utf-8

# In[63]:


import networkx as nx
import matplotlib.pyplot as plt
import random as r
import math as m
import time as t
import numpy as np



def generer_graphe(M):
    G = nx.DiGraph()
    G.add_nodes_from([l for l in range(len(M))])
    for i in range(len(M)):
        for j in range(len(M)):
             if M[i][j] != 0:
                G.add_edge(i,j,weight = M[i][j])
    return G   

def tracer_graphe(Graphe):
    edge_labels=dict([((u,v,),d['weight'])
                 for u,v,d in Graphe.edges(data=True)])

    pos=[nx.circular_layout(Graphe),nx.spring_layout(Graphe),nx.spectral_layout(Graphe)]

    for i in range(3):
    
        nx.draw_networkx_edge_labels(Graphe,pos[i],edge_labels=edge_labels)   
        nx.draw_networkx(Graphe,pos[i],with_labels=True,arrows=True)
        plt.show()


