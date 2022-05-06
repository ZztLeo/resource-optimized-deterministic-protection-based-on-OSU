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
    
    for serv_id, s_p in serv_path.items():
        for key, value in s_p.items():
            if key == 'block':
                break
            else: 
                for j in range(len(value)-1):
                    link_key = str(value[j])+'->'+str(value[j+1])
                    link_serv = [serv_id, key]
                    curr_list = link_status[link_key]
                    curr_list.append(link_serv)
                    link_status[link_key] = curr_list
    
    return link_status
    # key: link string (A->B)
    # value: [remain badwidth, [serv 1, path_type 1], [serv 2, path_type 2]...]
    # path_type: 'work_path' or 'backup_path' or 'traffic_path'


def resource_allocation(single_serv, net, k, flag=True, work_path=[]):
    """
    Calculate paths for services and allocate optical and OSU resources (including working path and backup path)

    Args:
        single_serv: A list of single service attribute.
        net: A instance of Network class (including graph for calculating working paths and graph_backip for calculating protection paths)
        k: The k of KSP 
        flag: True -> compute working paths for protected service or paths for other traffic; False -> compute backup paths for protected service
        work_path: Used to distinguish backup paths from working paths, default: []
    
    Returns:
        allo_flag: True -> allocation succeeded; False -> allocation failed
        alloc_path: A list of allocated path
    """

    allo_flag = False
    alloc_path = [] # list of service allocated paths: [service ID, [the allocated path]]
    try:
        if flag == True:
            ksp_list, _ = k_shortest_paths(net.graph, single_serv[1], single_serv[2], k)
        else:
            ksp_list, _ = k_shortest_paths(net.graph_backup, single_serv[1], single_serv[2], k)
    except nx.NetworkXNoPath:
        return allo_flag, alloc_path

    for path_list in ksp_list:
        
        # Eliminate the situation where the direct connection of the working path leads to the same calculation result of the protection path
        if (flag == False) & (path_list == work_path):
            continue
        
        path_avail_flag = True
        
        link_key_list = []
        for i in range(len(path_list)-1):
            link_key = str(path_list[i])+'->'+str(path_list[i+1])
            link_key_list.append(link_key)

            if net.network_status[link_key][0] < single_serv[3]:
                path_avail_flag = False
                break
            
        if path_avail_flag ==True:
            for key in link_key_list:
                net.network_status[key][0] = net.network_status[key][0]- single_serv[3]
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

# main function
if __name__ == '__main__':
    G = Network()
    G.graph_read('NSFNET.md')
    G.graph_init()
    S = Service()
    S.generate_service(G, 20, 40)