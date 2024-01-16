# -*- coding: utf-8 -*-
"""
Created on Wed May 18 09:21:30 2022

@author: regina
"""

import numpy as np
import networkx as nx
import itertools as it


class ConnectedSubgraphs:
    
    def __init__(self,coupling_map):
        self.coupling_map = coupling_map
        
    def find_connected_subgraphs(self):
        G = nx.Graph()
        G.add_nodes_from(list(np.arange(27)))
        G.add_edges_from(self.coupling_map)
        
        all_connected_subgraphs = []
        layout_list = []
        nb_nodes=5
        for SG in (G.subgraph(selected_nodes) for selected_nodes in it.combinations(G, nb_nodes)):
            if nx.is_connected(SG):
                #print(SG.nodes)
                all_connected_subgraphs.append(SG)
                cnots = list(SG.edges) + [x[1] for x in (list(it.permutations(tup)) for tup in SG.edges)]
                layout_list.append([list(SG.nodes),cnots])
        
        
        cnot_layout_list = []
        for item in layout_list:
            permuts = list(it.permutations(item[0]))
            for permut in permuts:
                #cnot_gate_list = [(permut[0],permut[3]),(permut[1],permut[3]),(permut[1],permut[4]),(permut[2],permut[4])]
                cnot_gate_list = [(permut[0],permut[3]),(permut[1],permut[0]),(permut[1],permut[2]),(permut[2],permut[4])]
                counter_cnots = 0
                for el in cnot_gate_list:
                    if (el in item[1]):
                        counter_cnots+=1
                if counter_cnots==len(cnot_gate_list):
                    cnot_layout_list.append([permut,cnot_gate_list])
        #trow away duplicates
        checklist = []
        for item in cnot_layout_list:
            if item not in checklist:
                checklist.append(item)
        
        return checklist