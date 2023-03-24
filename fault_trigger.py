# !usr/bin/env python
# -*- coding:utf-8 -*-

# Trigger network fault and statistics
# Jeyton Lee 2022-4-24 14:37:47


import random

from network import Network


def random_fault(net, fault_type) -> str:
    """
    Randomly trigger a single-port fault.

    Args:
        net: A instance of Network class. 
    
    Returns:
        fault_link: The fault link string (A->B).
        rand_faultwavelength: The fault port on the fault link (wavelength id).
    """
    rand_faultlink = random.randint(0,net.link_num - 1) # 随机选择链路故障
    rand_faultdir = random.randint(0,1) # 随机选择正向或反向链路故障(0表示正向链路故障，1为反向链路故障)
        
    if rand_faultdir == 0:
        fault_link = str(net.node_edge[rand_faultlink][0])+'->'+str(net.node_edge[rand_faultlink][1])
    else:
        fault_link = str(net.node_edge[rand_faultlink][1])+'->'+str(net.node_edge[rand_faultlink][0])
    
    if fault_type == 'link':
        fault_point = [fault_link]
    elif fault_type == 'port':
        rand_faultwavelength = random.randint(0,net.wavelength_num - 1)    
        fault_point = [fault_link, rand_faultwavelength]
    
    return fault_point

def fault_impact_statistics(net, link_status: dict, fault_point: str, serv_path: dict, serv_matrix: dict, shared_list: dict):
    """
    Count services affected after the fault.

    Args:
        net: A instance of Network class.
        link_status: A dictionary of network link status.
        fault_link: A string of fault link.
        fault_wavelength: An id of fault wavelength on the link
        serv_path: A dictionary of service path.
        serv_matrix: A dictionary of service matrix.
    
    Returns:
        fail_serv: The list of failure switching services id. 
        impact_traffic: The list of affected traffic id.
    """


    impact = []

    if len(fault_point) == 1:
        for f_w in range(net.wavelength_num):
            if link_status[fault_point[0]][f_w] != []:
                impact.append(link_status[fault_point[0]][f_w]) # All service disruptions caused by fault
    elif len(fault_point) == 2:
        impact.append(link_status[fault_point[0]][fault_point[1]])


    impact_serv = [] # Protection services to be switched
    interr_traffic = [] # Traffic disrupted by fault
    # Count services to be switched and interrupted traffic caused by fault (list)
    
    for im in impact:
        for im_ in im:
            if im_[1] == 'work_path':
                impact_serv.append(im_[0])
            
            elif im_[1] == 'traffic_path' or 'shared_path':
                interr_traffic.append(im_[0])

    num_switch = len(impact_serv)
    
    # Statistics on the number of traffic affected by the protection service switching
    backup_link_list = []
    switch_serv = []
    impact_traffic = []
    for sw_s_id in impact_serv:
        if shared_list.get(sw_s_id) != None:
            impact_traffic.append([shared_list.get(sw_s_id)])
        
        backup_path = serv_path[sw_s_id]['backup_path']
        if backup_path[2] >= serv_matrix[sw_s_id]['bw']:
            continue
        
        else:
            #print(backup_path[2],serv_matrix[sw_s_id]['bw'])
            switch_serv.append(sw_s_id)
            for j in range(len(backup_path[0])):
                l = str(backup_path[0][j])
                if l not in backup_link_list:
                    backup_link_list.append([l, backup_path[1]])

    fail_serv = []
    for bl in backup_link_list:
        rest_bw = net.network_status[bl[0]][bl[1]]

        total_serv_bw = 0
        total_traff_bw = 0
        traffic_list = []
        serv_list = []

        for ls in link_status[bl[0]][bl[1]]:

            if ls[1] == 'backup_path':
                if ls[0] in switch_serv:
                    total_serv_bw = total_serv_bw + (serv_matrix[ls[0]]['bw'] - ls[2])
                    serv_list.append([ls[0], serv_matrix[ls[0]]['bw'] - ls[2]])          

            elif ls[1] == 'traffic_path':
                traffic_list.append([ls[0],ls[2]])
                total_traff_bw = total_traff_bw + serv_matrix[ls[0]]['bw']

        # print(total_serv_bw)
        if rest_bw >= total_serv_bw:
            continue
        elif (rest_bw + total_traff_bw) >= total_serv_bw:
            d_value = total_serv_bw - rest_bw
            temp_t = 0
            for t in traffic_list:
                temp_t = temp_t + t[1]
                impact_traffic.append([t[0]])
                if temp_t >= d_value:
                    break
        elif (rest_bw + total_traff_bw) < total_serv_bw:
            impact_traffic.append([item[0] for item in traffic_list])
            d_value = total_serv_bw - (rest_bw + total_traff_bw)
            temp_s = 0
            for s in serv_list:
                temp_s = temp_s + s[1]
                fail_serv.append([s[0]])
                if temp_s >= d_value:
                    break

    fail_serv = sum(fail_serv, [])
    fail_serv = set(fail_serv)

    impact_traffic = sum(impact_traffic, [])
    impact_traffic = set(impact_traffic)

    return fail_serv, impact_traffic, num_switch

# main function
if __name__ == '__main__':
    G = Network()
    G.graph_read('NSFNET.md')
    G.graph_init()