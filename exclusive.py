# !usr/bin/env python
# -*- coding:utf-8 -*-

# All kinds of service planning algorithms
# Jeyton Lee 2022-05-05 21:03:37

import copy as cp
import function as ft
import networkx as nx

from network import Network
from service import Service

def heuristic_pro(net, serv_matrix: dict, fault_type:str, pro_serv_num: int):

    serv_path = dict()
    key_num = 0
    total_allo_pro_serv_bw = 0
    #先规划受保护业务
    pro_serv_list = serv_matrix
    #pro_serv_list = ft.serv_sort(pro_serv_list)
    net.network_status_reset()
    #print(pro_serv_list)
    #fake_network_status = cp.deepcopy(net.network_status)
    pro_block_num = 0
    pro_block_bw = 0
    traffic_block_num = 0
    i = 0
    # print(pro_serv_list)
    for pro_serv in pro_serv_list:
        
        flag, work_path, backup_path = pro_serv_algorithm(net, pro_serv, fault_type)
        i = i + 1
        if flag == 'succeed':
            for link in work_path[0]:
                net.network_status[link][work_path[1]] = net.network_status[link][work_path[1]] - pro_serv['bw']
                #fake_network_status[link][work_path[1]] = fake_network_status[link][work_path[1]] - pro_serv['bw']
            for link in backup_path[0]:
                net.network_status[link][backup_path[1]] = net.network_status[link][backup_path[1]] - pro_serv['bw']
                #fake_network_status[link][backup_path[1]] = fake_network_status[link][backup_path[1]] - pro_serv['bw']
            serv_path[pro_serv['id']] = {'work_path': [work_path[0], work_path[1], pro_serv['bw']], 'backup_path': [backup_path[0], backup_path[1], pro_serv['bw']]}
            total_allo_pro_serv_bw = total_allo_pro_serv_bw + (pro_serv['bw'] * len(backup_path))
        else:
            serv_path[pro_serv['id']] = {'block': []}
            pro_block_num = pro_block_num + 1
            pro_block_bw = pro_block_bw + pro_serv['bw']
    
    pro_block_num_rate = pro_block_num / pro_serv_num


    #输出打印启发式算法结果
    print('Number of protected services blocked:', pro_block_num, ', blocking rate:{:.2%}'.format(pro_block_num_rate))
    key_num = 0
    remain_bw = 0
    for __, value in net.network_status.items():
        key_num = key_num + 1
        for __, re_bw in value.items():
            remain_bw = remain_bw + re_bw
    total_bw = key_num * net.link_capacity * net.wavelength_num
    resource_utilization_rate = (total_bw - remain_bw) / total_bw

    print('Resource utilization rate of protected services:{:.2%}\n'.format(resource_utilization_rate))

    return serv_path, total_allo_pro_serv_bw, pro_block_num

def pro_serv_algorithm(net, pro_serv: dict, fault_type: str):

    src = pro_serv['src_dst'][0]
    dst = pro_serv['src_dst'][1]
    wk_k_path_list, __ = ft.k_shortest_paths(net.graph, src, dst, 3)
    work_path = []
    backup_path = []
    path_set = []
    for wk_p in wk_k_path_list:
        

        #wk_avail_flag = None
        wk_link_list = ft.path_to_link(wk_p)
        if fault_type == 'link':
            remove = wk_p[1:-1]
            net_bp = cp.deepcopy(net)
            net_bp.graph_remove_nodes(remove)
                
            try:
                bp_k_path_list, __ = ft.k_shortest_paths(net_bp.graph, src, dst, 3)
            except nx.NetworkXNoPath:
                continue
        elif fault_type == 'port':
            bp_k_path_list, __ = ft.k_shortest_paths(net.graph, src, dst, 3)
        
        bp_set = []
        for bp_p in bp_k_path_list:
            if fault_type == 'link':
                if bp_p == wk_link_list:
                    continue
            bp_link_list = ft.path_to_link(bp_p)
            bp_set.append(bp_link_list)

        path_set.append({'wk_candidate': wk_link_list, 'bp_candidate': bp_set})
    
    set_r = []
    for candidate in path_set:
        max_bw_wave_wk, max_bw_waveid_wk = get_max_bw(net.network_status, net.wavelength_num, candidate['wk_candidate'])      
        
        bp_set_ = []
        for bp_candidate in candidate['bp_candidate']:
            max_bw_wave_bp, max_bw_waveid_bp = get_max_bw(net.network_status, net.wavelength_num, bp_candidate)
            if fault_type == 'port':
                if (bp_candidate == candidate['wk_candidate']) & (max_bw_waveid_bp == max_bw_waveid_wk):
                    continue
            bp_set_.append([bp_candidate, max_bw_waveid_bp, max_bw_wave_bp])
        bp_set_.sort(key=lambda x: x[2], reverse=True)
        set_r.append([candidate['wk_candidate'], max_bw_waveid_wk, max_bw_wave_wk, bp_set_])

    set_r.sort(key=lambda x: x[2], reverse=True)

    for s in set_r:
        if s[2] < pro_serv['bw']:
            return 'block', [], []
        else:
            if s[3][0][2] >= pro_serv['bw']:
                Flag = 'succeed'
                work_path = [s[0], s[1]]
                backup_path = [s[3][0][0], s[3][0][1]]
                return Flag, work_path, backup_path
            else:
                continue
    for s in set_r:
        if s[3][0][2] >= pro_serv['bw']:
            Flag = 'succeed'
            work_path = [s[0], s[1]]
            backup_path = [s[3][0][0], s[3][0][1]]
            return Flag, work_path, backup_path
        else:
            continue

    return 'block', [], []

def get_max_bw(network_status: dict, wavelength_num: int, link_path: list):
    wave_set = []
    for wave_id in range(wavelength_num):
        link_bw = []
        for link in link_path:
            link_bw.append(network_status[link][wave_id])
        min_bw_link = min(link_bw)
        wave_set.append(min_bw_link)
    max_wave_bw = max(wave_set)
    max_wave_id = wave_set.index(max_wave_bw)

    return max_wave_bw, max_wave_id

if __name__ == '__main__':
    net = Network()

    net.graph_read('resource', 'NSFNET.md')
    net.graph_init()