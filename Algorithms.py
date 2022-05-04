# !usr/bin/env python
# -*- coding:utf-8 -*-

# this is for planing services
# Jeyton Lee 2022-4-28 22:59:32


from os import stat
import networkx as nx
import numpy as np
import copy as cp

from Network import Graph
from Service import Service
from operator import itemgetter

def heuristic(Net, Serv):
    print('----->启发式算法规划业务中...')
    
    pro_serv_block_num = 0
    traffic_block_num = 0
    
    # 业务规划
    for single_serv in Serv.serv_matrix:
        
        if single_serv[1] == 'P':
            # 为保护业务分配工作路径
            allo_flag_w, work_path = R_OSU_A(single_serv, Net, k=3, WB_flag=True)
        
            # 为保护业务分配保护路径
            remove_list = work_path[1:-1]
            Net.graph_remove_nodes(remove_list) # 保护路径与工作路径不得相交
            single_serv[4] = 2 # 保护管道带宽2M
            allo_flag_b, backup_path = R_OSU_A(single_serv, Net, k=3, WB_flag=False, work_path=work_path)
        
            if allo_flag_w & allo_flag_b == True:
                Serv.serv_matrix[single_serv[0]][5] = 'SUCC'
                Serv.serv_path[single_serv[0]] = [[work_path, 'work_path'], [backup_path, 'backup_path']]
                
            else:
                Serv.serv_matrix[single_serv[0]][5] = 'BLOCK'
                Serv.serv_path[single_serv[0]] = [[[], 'block']]
                pro_serv_block_num = pro_serv_block_num + 1

        elif single_serv[1] == 'T':
            allo_flag_t, traffic_path = R_OSU_A(single_serv, Net, k=5, WB_flag=True)
            if allo_flag_t ==True:
                Serv.serv_matrix[single_serv[0]][5] = 'SUCC'
                Serv.serv_path[single_serv[0]] = [[traffic_path, 'traffic_path']]
            else:
                Serv.serv_matrix[single_serv[0]][5] = 'BLOCK'
                Serv.serv_path[single_serv[0]] = [[[], 'block']]
                traffic_block_num = traffic_block_num + 1
    pro_serv_block_rate = pro_serv_block_num / Serv.pro_serv_num
    traffic_block_rate = traffic_block_num / Serv.traffic_num
    total_block_rate = (pro_serv_block_num + traffic_block_num) / (Serv.pro_serv_num + Serv.traffic_num)
    print('----->启发式算法业务部署完成')
    print('受保护业务阻塞数量：', pro_serv_block_num, '，阻塞率：{:.2%}'.format(pro_serv_block_rate) , '；其他流量阻塞数量：', traffic_block_num, '，阻塞率：{:.2%}'.format(traffic_block_rate), '，总体阻塞率：{:.2f}'.format(total_block_rate))

    rest_bw = 0
    key_num = 0
    for _, value in Net.network_status.items():
        rest_bw = rest_bw + value[0]
        key_num = key_num + 1
    total_bw = key_num * Net.link_capacity
    resource_utilization_rate = (total_bw - rest_bw) / total_bw

    print('整网资源利用率：{:.2%}'.format(resource_utilization_rate))

def statistics_link_status(Net, Serv) -> dict:
    link_status = Net.network_status
    
    for key_id, value_path in Serv.serv_path.items():
        if value_path[0][1] == 'block':
            continue
        else: 
            for sub_path in value_path:
                
                for j in range(len(sub_path[0])-1):
                    link_key = str(sub_path[0][j])+'->'+str(sub_path[0][j+1])
                    link_serv = [key_id, sub_path[1]]
                    curr_list = link_status[link_key]
                    curr_list.append(link_serv)
                    link_status[link_key] = curr_list


    return link_status


def R_OSU_A(single_serv, Net, k, WB_flag=True, work_path=[]):
    """
        为业务计算路径并分配OSU资源(包括工作路径和保护路径)

        :param single_serv: 单条业务的属性list
        :param Net: Network, 包括用于计算工作路径的图G和用于计算保护路径的图BG
        :param k: ksp算法的k
        :param WB_flag: True->计算保护业务工作路径或其他流量的路径; False->计算保护路径
        :param work_path: 用于确定保护路径与工作路径是否一直，默认为[]
        """

    if WB_flag == True:
        ksp_list, _ = k_shortest_paths(Net.G, single_serv[2], single_serv[3], k)
    else:
        ksp_list, _ = k_shortest_paths(Net.BG, single_serv[2], single_serv[3], k)
        
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

            if Net.network_status[link_key][0] < single_serv[4]:
                path_avail_flag = False
                break
            
        if path_avail_flag ==True:
            for key in link_key_list:
                Net.network_status[key][0] = Net.network_status[key][0]- single_serv[4]
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
    S.generate_service(G, 20, 40)

    np.set_printoptions(suppress=True)
    heuristic(G, S)