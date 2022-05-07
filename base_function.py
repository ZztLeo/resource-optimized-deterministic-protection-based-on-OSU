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


def ksp_FF(single_serv, net, k, flag=True):
    """
    Calculate paths for services and allocate optical and OSU resources based on ksp + First Fit (including working path and backup path)

    Args:
        single_serv: A list of single service attribute.
        net: A instance of Network class (including graph for calculating working paths and graph_backip for calculating protection paths)
        k: The k of KSP 
        flag: True -> compute working paths for protected service or paths for other traffic; False -> compute backup paths for protected service
    
    Returns:
        allo_flag: True -> allocation succeeded; False -> allocation failed
        work_path: A list of allocated working path
        work_wave_avail_id: A wavelength id of allocated working path 
        backup_path: A list of allocated backup path
        backup_wave_avail_id: A wavelength id of allocated backup path 
    """

    allo_flag = False
    work_path = [] # list of service allocated paths: [service ID, [the allocated path]]
    backup_path = [] # list of service allocated paths: [service ID, [the allocated path]]
    work_wave_avail_id = None
    backup_wave_avail_id = None
    # alloc_path = [] # list of service allocated paths: [service ID, [the allocated path]]

    work_ksp_list, _ = k_shortest_paths(net.graph, single_serv[1], single_serv[2], k)

    for w_k_l in work_ksp_list:
        
        # Eliminate the situation where the direct connection of the working path leads to the same calculation result of the protection path
        if flag == True:
            remove_list = w_k_l[1:-1]

            net.graph_remove_nodes(remove_list) # Protection path and working path must not intersect
            backup_attribute = cp.deepcopy(single_serv)
            backup_attribute[3] = 2 # Protection pipeline bandwidth: 2M
            
            try:
                backup_ksp_list, _ = k_shortest_paths(net.graph_backup, single_serv[1], single_serv[2], k)
            except nx.NetworkXNoPath:
                continue

        work_path_avail_flag, work_wave_avail_id, work_link_key_list = first_fit(net, w_k_l, single_serv)
        
        if work_path_avail_flag == True:
            if flag == True:
                for b_k_l in backup_ksp_list:
                    backup_path_avail_flag, backup_wave_avail_id, backup_link_key_list = first_fit(net, b_k_l, backup_attribute)

                    if backup_link_key_list == work_link_key_list:
                        continue

                    if backup_path_avail_flag == True:

                        for key in backup_link_key_list:
                            net.network_status[key][backup_wave_avail_id] = net.network_status[key][backup_wave_avail_id]- backup_attribute[3]
                        backup_path = backup_link_key_list
                        break

            for key in work_link_key_list:
                net.network_status[key][work_wave_avail_id] = net.network_status[key][work_wave_avail_id]- single_serv[3]
            work_path = work_link_key_list
            allo_flag = True
            break
    
    return allo_flag, work_path, work_wave_avail_id, backup_path, backup_wave_avail_id



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

def first_fit(net, path_list, single_serv):
    """
    Allocate optical and OSU resources based on First Fit 

    Args:
        net: A instance of Network class
        path_list: A list of path of the resource to be allocated 
        single_serv: A list of single service attribute.
    
    Returns:
        path_avail_flag: True -> sufficient resource; False -> insufficient resource.
        wave_avail_id: The wavelength id with sufficient resource.
        link_key_list: The path list with sufficient resource (foramt: A->B). 
    """
    
    path_avail_flag = False
    wave_avail_id = None
    # First Fit
    
    for i in range(net.wavelength_num):
        resource_avail_flag = False

        link_key_list = []
        for j in range(len(path_list)-1):
            link_key = str(path_list[j])+'->'+str(path_list[j+1])
            link_key_list.append(link_key)

            if net.network_status[link_key][i] < single_serv[3]:
                wave_avail_id = None
                resource_avail_flag = False
                break
            else:
                resource_avail_flag = True
            
        if resource_avail_flag == True:
            wave_avail_id = i
            path_avail_flag = True
            break


    return path_avail_flag, wave_avail_id, link_key_list

# main function
if __name__ == '__main__':
    G = Network()
    G.graph_read('NSFNET.md')
    G.graph_init()
    S = Service()
    S.generate_service(G, 20, 40)