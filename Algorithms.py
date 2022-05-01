# !usr/bin/env python
# -*- coding:utf-8 -*-

# this is for planing services
# Jeyton Lee 2022-4-28 22:59:32


import networkx as nx
import numpy as np
import copy as cp

from Network import Graph
from Service import Service
from operator import itemgetter

def heuristic(Net, Serv):
    
    # Protection services plan
    for pserv_list in Serv.pro_service:
        # Allocate work path for protection service
        allo_flag_w, work_path = R_OSU_A(pserv_list, Net, k=3, WB_flag=True)
        
        # Allocate backup path for protection service
        remove_list = work_path[1:-1]
        Net.graph_remove_nodes(remove_list) # Protection path and working path are disjoint
        pserv_list[3] = 2 # The protection path allocates 2M bandwidth
        # Allocate backup path for protection service
        allo_flag_b, backup_path = R_OSU_A(pserv_list, Net, k=3, WB_flag=False, work_path=work_path)
        
        if allo_flag_w & allo_flag_b == True:
            Serv.pro_service[pserv_list[0]][5] = 'SUCC'
            Serv.serv_path.append([pserv_list[0], work_path, 'W'])
            Serv.serv_path.append([pserv_list[0], backup_path, 'B'])
        else:
            Serv.pro_service[pserv_list[0]][5] = 'BLOCK'
            Serv.serv_path.append([pserv_list[0], [], None])
            Serv.serv_path.append([pserv_list[0], [], None])

    print(Serv.serv_path)

def R_OSU_A(single_serv, Net, k, WB_flag=True, work_path=[]):
    """
        Calculate paths for service and allocate OSU resources (including working paths or protection paths)

        :param single_serv: List of single service
        :param Net: Network, including graph G for computing working paths and BG for computing protection paths
        :param k: k of ksp
        :param WB_flag: True->caculate work path; False->caculate backup path
        :param work_path: Used to determine whether the backup path and the working path are the same, the default is []
        """

    if WB_flag == True:
        ksp_list, _ = k_shortest_paths(Net.G, single_serv[1], single_serv[2], k)
    else:
        ksp_list, _ = k_shortest_paths(Net.BG, single_serv[1], single_serv[2], k)
        
    allo_flag = False
    alloc_path = [] # list of service allocated paths: [service ID, [the allocated path]]
    for path_list in ksp_list:
        
        # Eliminate the situation where the direct connection of the working path leads to the same calculation result of the protection path
        if (WB_flag == False) & (path_list == work_path):
            continue
        
        path_avail_flag = True
        
        link_key_list = []
        for i in range(len(path_list)-1):
            link_key = str(path_list[i])+'->'+str(path_list[i+1])
            link_key_list.append(link_key)

            if Net.network_status[link_key] < single_serv[3]:
                path_avail_flag = False
                break
            
        if path_avail_flag ==True:
            for key in link_key_list:
                Net.network_status[key] = Net.network_status[key]- single_serv[3]
            allo_flag = True
            alloc_path = path_list
            break
    
    return allo_flag, alloc_path



def k_shortest_paths(G, source, target, k = 1, weight = 'weight'):
    # G is a networkx graph.
    # source and target are the labels for the source and target of the path.
    # k is the amount of desired paths.
    # weight = 'weight' assumes a weighed graph. If this is undesired, use weight = None.
    
    A = [nx.dijkstra_path(G, source, target, weight = 'weight')]
    A_len = [sum([G[A[0][l]][A[0][l + 1]]['weight'] for l in range(len(A[0]) - 1)])]
    B = []

    for i in range(1, k):
        for j in range(0, len(A[-1]) - 1):
            Gcopy = cp.deepcopy(G)
            spurnode = A[-1][j]
            rootpath = A[-1][:j + 1]
            for path in A:
                if rootpath == path[0:j + 1]: #and len(path) > j?
                    if Gcopy.has_edge(path[j], path[j + 1]):
                        Gcopy.remove_edge(path[j], path[j + 1])
                    if Gcopy.has_edge(path[j + 1], path[j]):
                        Gcopy.remove_edge(path[j + 1], path[j])
            for n in rootpath:
                if n != spurnode:
                    Gcopy.remove_node(n)
            try:
                spurpath = nx.dijkstra_path(Gcopy, spurnode, target, weight = 'weight')
                totalpath = rootpath + spurpath[1:]
                if totalpath not in B:
                    B += [totalpath]
            except nx.NetworkXNoPath:
                continue
        if len(B) == 0:
            break
        lenB = [sum([G[path[l]][path[l + 1]]['weight'] for l in range(len(path) - 1)]) for path in B]
        B = [p for _,p in sorted(zip(lenB, B))]
        A.append(B[0])
        A_len.append(sorted(lenB)[0])
        B.remove(B[0])
        
    return A, A_len

# main函数
if __name__ == '__main__':
    G = Graph()
    G.graph_read('NSFNET.md')
    G.graph_init()
    S = Service()
    S.generate_service(G, 20, 0)

    np.set_printoptions(suppress=True)
    heuristic(G, S)