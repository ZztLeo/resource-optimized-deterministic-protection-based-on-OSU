# !usr/bin/env python
# -*- coding:utf-8 -*-

# All kinds of service planning algorithms
# Jeyton Lee 2022-05-05 21:03:37

import copy as cp
import base_function as bf

def baseline(net, serv):
    """
    KSP-based planning algorithm (baseline).
        
    Args:
        net: An instance of Network class.
        serv: An instance of Service class.
    """
    print('----->KSP-based baseline algorithm planning services...')
    
    pro_serv_block_num = 0
    traffic_block_num = 0
    
    # Service planning
    for serv_id, serv_attribute in serv.serv_matrix.items():
        
        if serv_attribute[0] == 'P':
            # Allocate work path for protection services
            allo_flag_w, work_path = bf.resource_allocation(serv_attribute, net, k=3, flag=True)
        
            # Allocate backup path for protection services
            remove_list = work_path[1:-1]
            net.graph_remove_nodes(remove_list) # Protection path and working path must not intersect
            backup_attribute = cp.deepcopy(serv_attribute)
            backup_attribute[3] = 2 # Protection pipeline bandwidth: 2M
            allo_flag_b, backup_path = bf.resource_allocation(backup_attribute, net, k=5, flag=False, work_path=work_path)
        
            if allo_flag_w & allo_flag_b == True:
                serv.serv_matrix[serv_id][5] = 'SUCC'
                serv.serv_path[serv_id] = {'work_path': work_path, 'backup_path': backup_path}
                
            else:
                serv.serv_matrix[serv_id][5] = 'BLOCK'
                serv.serv_path[serv_id] = {'block': []}
                pro_serv_block_num = pro_serv_block_num + 1

        elif serv_attribute[0] == 'T':
            allo_flag_t, traffic_path = bf.resource_allocation(serv_attribute, net, k=5, flag=True)
            if allo_flag_t ==True:
                serv.serv_matrix[serv_id][5] = 'SUCC'
                serv.serv_path[serv_id] = {'traffic_path': traffic_path}
            else:
                serv.serv_matrix[serv_id][5] = 'BLOCK'
                serv.serv_path[serv_id] = {'block': []}
                traffic_block_num = traffic_block_num + 1
    pro_serv_block_rate = pro_serv_block_num / serv.pro_serv_num
    traffic_block_rate = traffic_block_num / serv.traffic_num
    total_block_rate = (pro_serv_block_num + traffic_block_num) / (serv.pro_serv_num + serv.traffic_num)
    print('----->The service deployment of KSP-based baseline algorithm is completed.')
    print('Number of protected services blocked:', pro_serv_block_num, ', blocking rate:{:.2%}'.format(pro_serv_block_rate) , '\nNumber of protected services blocked:', traffic_block_num, ', blocking rate:{:.2%}'.format(traffic_block_rate), '\nTotal blocking rate:{:.2f}'.format(total_block_rate))
    #print(Serv.serv_path)
    rest_bw = 0
    key_num = 0
    for _, value in net.network_status.items():
        rest_bw = rest_bw + value[0]
        key_num = key_num + 1
    total_bw = key_num * net.link_capacity
    resource_utilization_rate = (total_bw - rest_bw) / total_bw

    print('Resource utilization rate of the network:{:.2%}'.format(resource_utilization_rate), '\n')