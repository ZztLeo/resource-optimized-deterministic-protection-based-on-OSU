# !usr/bin/env python
# -*- coding:utf-8 -*-

# this is for planing services
# Jeyton Lee 2022-4-28 22:59:32

import networkx as nx
import copy as cp

from network import Network
from service import Service

def link_status_statistics(net, serv_path: dict) -> dict:
    """
    Collect statistics on the service information on each link after planning the services.
        
    Args:
        net: An instance of Network class.
        serv_path: A dictionary of service path.
    Returns:
        link_status: A dictionary of each link status.
    """
    
    link_status = cp.deepcopy(net.network_status)

    for key, value in link_status.items():
        for key_ in value.keys():
            link_status[key][key_] = []
    #print(link_status)

    for serv_id, s_p in serv_path.items():
        for key, value in s_p.items():
            if key == 'block':
                break
            else: 
                for j in range(len(value[0])):
                    link_key = str(value[0][j])
                    link_serv = [serv_id, key]
                    curr_list = link_status[link_key][value[1]]
                    curr_list.append(link_serv)
                    link_status[link_key][value[1]] = curr_list
    
    return link_status
    # key: link string (A->B)
    # value: {wavelength_id 1: [serv 1, path_type 1], wavelength_id 2: [serv 2, path_type 2]...]}
    # path_type: 'work_path' or 'backup_path' or 'traffic_path'


def serv_sort(serv_matrix: list) -> list:
    a = sorted(serv_matrix, key=lambda row: (-row['bw'], row['src_dst']))
    bw_list =[]
    for c in a:
        bw_list.append(c['bw'])
    bw_count = [ bw_list.count(i) for i in bw_list]
    bw_count_ = list(set(bw_count))
    bw_count_.sort(key = bw_count.index)



    temp = 0
    new_serv_matrix = []
    for k in bw_count_:
        sd_list = []
        for i in range(k):
            sd_list.append(a[i+temp]['src_dst'])



        count_time = []
        count = 0
        for i in sd_list:
            count_time.append([count + temp, sd_list.count(i)]) 
            count = count + 1
        count_time.sort(key=lambda x: x[1], reverse=True)

        for i in count_time:
            new_serv_matrix.append(a[i[0]])
        temp = k + temp

    return new_serv_matrix

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
                #print(source, target)
                continue
        if len(B) == 0:
            break
        lenB = [sum([G[path[l]][path[l + 1]]['weight'] for l in range(len(path) - 1)]) for path in B]
        B = [p for _,p in sorted(zip(lenB, B))]
        A.append(B[0])
        A_len.append(sorted(lenB)[0])
        B.remove(B[0])


    return A, A_len

def path_to_link(path: list):
    link_list = []
    for i in range(len(path)-1):
        link_key = str(path[i])+'->'+str(path[i+1])
        link_list.append(link_key)

    return link_list

# main function
if __name__ == '__main__':
    G = Network()
    G.graph_read('NSFNET.md')
    G.graph_init()
    S = Service()
    S.generate_service(G, 20, 40)