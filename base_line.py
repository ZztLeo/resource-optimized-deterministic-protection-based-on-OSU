# !usr/bin/env python
# -*- coding:utf-8 -*-

# All kinds of service planning algorithms
# Jeyton Lee 2022-05-05 21:03:37

import copy as cp
import function as ft
import networkx as nx

from network import Network
from service import Service

def baseline(net, serv, serv_path, serv_matrix: dict, N: int, fault_type: str, pro_serv_num: int, traffic_num: int, total_allo_pro_serv_bw: int, pro_serv_block_num: int, flag: int, is_share) ->dict:

    """
    KSP-based planning algorithm (baseline).
        
    Args:
        net: An instance of Network class.
        serv_matrix: A dictionary of service matrix.
        pro_serv_num: Number of protected services.
        traffic_num: Number of traffic.

    Returns:
        serv_path: A dictionary of service path (key: service id, value :service path (dict)).
    """
    
    # Three formats of value in serv_path:
    # protected service: {'work_path': [work path, wavelength_id], 'backup_path': [backup path, wavelength_id]}
    # traffic: {'traffic_path': [traffic path, wavelength_id]}
    # block: {'block': []}

    total_bw = 2 * net.link_num * net.link_capacity * net.wavelength_num

    if flag == 1:
        rest_bw_ = 0
        for __, value in net.network_status.items():
            for __, re_bw in value.items():
                rest_bw_ = rest_bw_ + re_bw
        
    else:
        total_allo_pro_serv_bw = 0
        pro_serv_block_num = 0
        serv_path = dict()
        net.network_status_reset()
    
    pro_block_bw = 0
    traffic_block_num = 0
    total_allo_traffic_bw = 0
    id_set = []
    shared_list = dict()
    # Service planning
    for service in serv_matrix:
        bias = None
        if service['type'] == 'P':
            if N == 0:
                bias = 2
            else:
                if service['bw'] != 2:
                    bias = N * service['bw']
                else:
                    bias = 2
            # Allocate work path for protection services
            allo_flag, work_path, work_wave_id, backup_path, backup_wave_id, _ = ksp_FF(id_set, fault_type, serv, serv_path, pro_serv_num, service, net, bias, is_share, k=3, flag=True)
        
            if allo_flag == True:
                serv_path[service['id']] = {'work_path': [work_path, work_wave_id, service['bw']], 'backup_path': [backup_path, backup_wave_id, bias]}
                total_allo_pro_serv_bw = total_allo_pro_serv_bw + (bias * len(backup_path))
                
            else:
                serv_path[service['id']] = {'block': []}
                pro_serv_block_num = pro_serv_block_num + 1
                pro_block_bw = pro_block_bw + service['bw']

        elif service['type'] == 'T':
            if is_share == True:
                allo_flag, traffic_path, traffic_wave_id, _, _, id = ksp_FF(id_set, fault_type, serv, serv_path, pro_serv_num, service, net, bias, is_share, k=3, flag=False)
                #print(len(id_set))
                if allo_flag ==True:
                    if id != None:
                        id_set.append(id)
                        shared_list[id] = service['id']
                        serv_path[service['id']] = {'shared_path': id}
                        total_allo_pro_serv_bw = total_allo_pro_serv_bw - (service['bw'] * (len(traffic_path)))

                    else:
                        serv_path[service['id']] = {'traffic_path': [traffic_path, traffic_wave_id, service['bw']]}
                else:
                    serv_path[service['id']] = {'block': []}
                    traffic_block_num = traffic_block_num + 1
            else:    
                allo_flag, traffic_path, traffic_wave_id, _, _, _ = ksp_FF(id_set, fault_type, serv, serv_path, pro_serv_num, service, net, bias, is_share, k=3, flag=False)
                if allo_flag ==True:
                    serv_path[service['id']] = {'traffic_path': [traffic_path, traffic_wave_id, service['bw']]}
                    total_allo_traffic_bw = total_allo_traffic_bw + (service['bw'] * len(traffic_path))
                else:
                    serv_path[service['id']] = {'block': []}
                    traffic_block_num = traffic_block_num + 1
    
    pro_serv_block_rate = pro_serv_block_num / pro_serv_num

    try:
        traffic_block_rate = traffic_block_num /  traffic_num
    except Exception as e:
        traffic_block_rate = 0
    
    total_block_rate = (pro_serv_block_num + traffic_block_num) / (pro_serv_num + traffic_num)
    

    if flag == 1:
        print('Number of traffic services blocked:', traffic_block_num, ', blocking rate:{:.2%}'.format(traffic_block_rate), '\nTotal blocking rate:{:.2%}'.format(total_block_rate))
        Proportion_of_redundant_resources = total_allo_pro_serv_bw / total_bw
        print('The proportion of redundant resources:{:.2%}'.format(Proportion_of_redundant_resources))

        rest_bw = 0
        key_num = 0
        for _, value in net.network_status.items():
            rest_bw = rest_bw + sum(value.values())
            key_num = key_num + 1



        resource_utilization_rate = (total_bw - rest_bw) / total_bw

        traffic_resource_utilization_rate = (rest_bw_ - rest_bw) / rest_bw_
        print('Resource sharing rate of traffic:{:.2%}'.format(traffic_resource_utilization_rate))

        print('Resource utilization rate of the whole network:{:.2%}'.format(resource_utilization_rate),'\n')
    else:
        print('Number of protected services blocked:', pro_serv_block_num, ', blocking rate:{:.2%}'.format(pro_serv_block_rate))

        rest_bw_ = 0
        for __, value in net.network_status.items():
            for __, re_bw in value.items():
                rest_bw_ = rest_bw_ + re_bw
        resource_utilization_rate = (total_bw - rest_bw_) / total_bw
        print('Resource utilization rate of protected services:{:.2%}\n'.format(resource_utilization_rate))

    return serv_path, pro_serv_block_num, total_allo_pro_serv_bw, shared_list

def ksp_FF(id_set, fault_type, serv, serv_path, pro_serv_num, single_serv, net, bias, is_share, k, flag=True):
    
    src = single_serv['src_dst'][0]
    dst = single_serv['src_dst'][1]
    

    if flag == True:
        allo_flag = False
        work_path = []
        backup_path = [] # list of service allocated paths: [service ID, [the allocated path]]
        work_wave_avail_id = None
        backup_wave_avail_id = None

        work_ksp_list, _ = ft.k_shortest_paths(net.graph, src, dst, k)
        for w_k_l in work_ksp_list:
            backup_attribute = cp.deepcopy(single_serv)
            backup_attribute['bw'] = bias
            if fault_type == 'link':
                remove= w_k_l[1:-1]
                net_bp = cp.deepcopy(net)
                net_bp.graph_remove_nodes(remove) # Protection path and working path must not intersect    
                try:
                    backup_ksp_list, _ = ft.k_shortest_paths(net_bp.graph, src, dst, k)
                except nx.NetworkXNoPath:
                    continue
            elif fault_type == 'port':
                backup_ksp_list, _ = ft.k_shortest_paths(net.graph, src, dst, k)

            work_path_avail_flag, work_wave_avail_id, work_link_key_list = first_fit(net, w_k_l, single_serv)

            if work_path_avail_flag == True:
                for b_k_l in backup_ksp_list:
                    backup_path_avail_flag, backup_wave_avail_id, backup_link_key_list = first_fit(net, b_k_l, backup_attribute)

                    if fault_type == 'link':
                        if backup_link_key_list == work_link_key_list:
                            continue
                    elif fault_type == 'port':
                        if (backup_link_key_list == work_link_key_list) & (backup_wave_avail_id == work_wave_avail_id):
                            continue
                    
                    if backup_path_avail_flag == True:
                        allo_flag = True
                        break
            
            if allo_flag == True:
                for key in work_link_key_list:
                    net.network_status[key][work_wave_avail_id] = net.network_status[key][work_wave_avail_id] - single_serv['bw']
                work_path = work_link_key_list
                for key in backup_link_key_list:
                    net.network_status[key][backup_wave_avail_id] = net.network_status[key][backup_wave_avail_id] - bias
                backup_path = backup_link_key_list
                break
    
        return allo_flag, work_path, work_wave_avail_id, backup_path, backup_wave_avail_id, None


    elif flag == False:
        allo_flag = False
        tra_path = []
        tra_wave_avail_id = None

        if is_share == True:
            for s in serv.serv_matrix[:pro_serv_num]:
                if serv_path[s['id']] != {'block': []}:
                    if (single_serv['src_dst'] == s['src_dst']) and (single_serv['bw'] <= serv_path[s['id']]['backup_path'][2]):
                        if s['id'] not in id_set :
                            path = serv_path[s['id']]['backup_path']
                            id = s['id']
                            allo_flag = True
                            tra_wave_avail_id = path[1]
                            tra_path = path[0]

                            return allo_flag, tra_path, tra_wave_avail_id, [], None, id
            
            tra_ksp_list, _ = ft.k_shortest_paths(net.graph, src, dst, k)
                
            for t_k_l in tra_ksp_list:
                
                tra_path_avail_flag, tra_wave_avail_id, tra_link_key_list = first_fit(net, t_k_l, single_serv)

                if tra_path_avail_flag == True:
                    allo_flag = True
                    for key in tra_link_key_list:
                        net.network_status[key][tra_wave_avail_id] = net.network_status[key][tra_wave_avail_id] - single_serv['bw']
                    tra_path = tra_link_key_list
                    break
            
            return allo_flag, tra_path, tra_wave_avail_id, [], None, None

        else:
            tra_ksp_list, _ = ft.k_shortest_paths(net.graph, src, dst, k)
                
            for t_k_l in tra_ksp_list:
                
                tra_path_avail_flag, tra_wave_avail_id, tra_link_key_list = first_fit(net, t_k_l, single_serv)

                if tra_path_avail_flag == True:
                    allo_flag = True
                    for key in tra_link_key_list:
                        net.network_status[key][tra_wave_avail_id] = net.network_status[key][tra_wave_avail_id] - single_serv['bw']
                    tra_path = tra_link_key_list
                    break
            
            return allo_flag, tra_path, tra_wave_avail_id, [], None, None

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

            if net.network_status[link_key][i] < single_serv['bw']:
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

if __name__ == '__main__':
    net = Network()

    net.graph_read('resource', 'NSFNET.md')
    net.graph_init()


    serv = Service()
    serv.generate_service(net, 50, 300)


