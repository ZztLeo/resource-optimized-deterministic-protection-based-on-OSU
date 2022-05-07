# !usr/bin/env python
# -*- coding:utf-8 -*-

# All kinds of service planning algorithms
# Jeyton Lee 2022-05-05 21:03:37

import copy as cp
import base_function as bf

def baseline(net, serv_matrix: dict, pro_serv_num: int, traffic_num: int) ->dict:
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
    
    print('----->KSP-based baseline algorithm planning services...')
    serv_path = dict()
    # Three formats of value in serv_path:
    # protected service: {'work_path': [work path, wavelength_id], 'backup_path': [backup path, wavelength_id]}
    # traffic: {'traffic_path': [traffic path, wavelength_id]}
    # block: {'block': []}

    pro_serv_block_num = 0
    traffic_block_num = 0  
    
    # Service planning
    for serv_id, serv_attribute in serv_matrix.items():
        
        if serv_attribute[0] == 'P':
            # Allocate work path for protection services
            allo_flag, work_path, work_wave_id, backup_path, backup_wave_id, = bf.ksp_FF(serv_attribute, net, k=3, flag=True)
        
        
            if allo_flag == True:
                serv_path[serv_id] = {'work_path': [work_path, work_wave_id], 'backup_path': [backup_path, backup_wave_id]}
                
            else:
                serv_path[serv_id] = {'block': []}
                pro_serv_block_num = pro_serv_block_num + 1

        elif serv_attribute[0] == 'T':
            allo_flag, traffic_path, traffic_wave_id, _, _ = bf.ksp_FF(serv_attribute, net, k=5, flag=False)
            if allo_flag ==True:
                serv_path[serv_id] = {'traffic_path': [traffic_path, traffic_wave_id]}
            else:
                serv_path[serv_id] = {'block': []}
                traffic_block_num = traffic_block_num + 1
    pro_serv_block_rate = pro_serv_block_num / pro_serv_num
    traffic_block_rate = traffic_block_num / traffic_num
    total_block_rate = (pro_serv_block_num + traffic_block_num) / (pro_serv_num + traffic_num)
    print('----->The service deployment of KSP-based baseline algorithm is completed.')
    print('Number of protected services blocked:', pro_serv_block_num, ', blocking rate:{:.2%}'.format(pro_serv_block_rate) , '\nNumber of protected services blocked:', traffic_block_num, ', blocking rate:{:.2%}'.format(traffic_block_rate), '\nTotal blocking rate:{:.2f}'.format(total_block_rate))
    # print(serv_path)
    rest_bw = 0
    key_num = 0
    for _, value in net.network_status.items():
        rest_bw = rest_bw + sum(value.values())
        key_num = key_num + 1
    total_bw = key_num * net.link_capacity * net.wavelength_num
    resource_utilization_rate = (total_bw - rest_bw) / total_bw

    print('Resource utilization rate of the network:{:.2%}'.format(resource_utilization_rate), '\n')
    #print(net.network_status)

    return serv_path