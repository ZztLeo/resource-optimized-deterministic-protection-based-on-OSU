from mimetypes import init
import networkx as nx
import function as ft
import copy as cp
import base_line as bl

from network import Network
from service import Service
from itertools import combinations




def heuristic_pro(net, serv_matrix: dict, fault_type:str, N: int, pro_serv_num: int, traffic_num: int):

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
        bias = None
        if N == 0:
            bias = 2
        else:
            if pro_serv['bw'] != 2:
                bias = N * pro_serv['bw']
            else:
                bias = 2
        
        flag, work_path, backup_path = pro_serv_algorithm(net, pro_serv, bias, fault_type)
        i = i + 1
        if flag == 'succeed':
            for link in work_path[0]:
                net.network_status[link][work_path[1]] = net.network_status[link][work_path[1]] - pro_serv['bw']
                #fake_network_status[link][work_path[1]] = fake_network_status[link][work_path[1]] - pro_serv['bw']
            for link in backup_path[0]:
                net.network_status[link][backup_path[1]] = net.network_status[link][backup_path[1]] - bias
                #fake_network_status[link][backup_path[1]] = fake_network_status[link][backup_path[1]] - pro_serv['bw']
            serv_path[pro_serv['id']] = {'work_path': [work_path[0], work_path[1], pro_serv['bw']], 'backup_path': [backup_path[0], backup_path[1], bias]}
            total_allo_pro_serv_bw = total_allo_pro_serv_bw + (bias * len(backup_path))
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

def pro_serv_algorithm(net, pro_serv: dict, bias: int, fault_type: str):

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
        if s[3][0][2] >= bias:
            Flag = 'succeed'
            work_path = [s[0], s[1]]
            backup_path = [s[3][0][0], s[3][0][1]]
            return Flag, work_path, backup_path
        else:
            continue

    return 'block', [], []

def heuristic_tra(net, serv: dict, serv_path: dict, link_status, serv_matrix_tra:list, pro_serv_num: int, traffic_num: int, total_allo_pro_serv_bw: int, pro_block_num:int, is_share:True):

    #规划流量业务
    traffic_block_num = 0
    remain_bw = 0
    remain_bw_ = 0
    total_bw = 2 * net.link_num * net.link_capacity * net.wavelength_num
    id_set = []
    shared_list = dict()
    
    for __, value in net.network_status.items():
        for __, re_bw in value.items():
            remain_bw = remain_bw + re_bw
    #计算overlap值
    overlap_value_matrix = dict()
    overlap_value_matrix = caculate_overlap(net, serv.serv_matrix, link_status, serv_path)
    

    for traffic in serv_matrix_tra:
        allo_flag = False
        src = traffic['src_dst'][0]
        dst = traffic['src_dst'][1]
        if is_share == True:
            for s in serv.serv_matrix[:pro_serv_num]:
                if serv_path[s['id']] != {'block': []}:
                    if (traffic['src_dst'] == s['src_dst']) and (traffic['bw'] <= serv_path[s['id']]['backup_path'][2]):
                        if s['id'] not in id_set :
                            path = serv_path[s['id']]['backup_path']
                            id = s['id']
                            allo_flag = True
                            #tra_wave_avail_id = path[1]
                            tra_path = path[0]
                            id_set.append(id)
                            
                            shared_list[id] = traffic['id']
                            serv_path[traffic['id']] = {'shared_path': id}
                            total_allo_pro_serv_bw = total_allo_pro_serv_bw - (traffic['bw'] * (len(tra_path)))
                            break
        
        if allo_flag == False or is_share == False:

            tra_path_list, __ = ft.k_shortest_paths(net.graph, src, dst, 3)

            candidate_tra_path = []
            for tra_path in tra_path_list:
                tp = ft.path_to_link(tra_path)
                candidate_wave_set = []
                res_flag = None
                for wave_id in range(net.wavelength_num):

                    max_overlap = 0
                    flag = None
                    for link in tp:
                        if net.network_status[link][wave_id] > traffic['bw']:
                            if overlap_value_matrix[link][wave_id] > max_overlap:
                                max_overlap = overlap_value_matrix[link][wave_id]
                        else:
                            flag = 'unavailable'
                            break
                    if flag != 'unavailable':
                        res_flag = 'available'
                        candidate_wave_set.append([wave_id,max_overlap])    
                if res_flag != None:
                
                    min_overlap = 100000
                    min_wave = None
                    for c_w in candidate_wave_set:
                        if c_w[1] < min_overlap:
                            min_wave = c_w[0]
                            min_overlap = c_w[1]
                    candidate_tra_path.append([tp, min_wave, min_overlap])

            if candidate_tra_path == []:
                serv_path[traffic['id']] = {'block': []}
                traffic_block_num = traffic_block_num + 1
            else:
                total_min_overlap = 100000
                for c_t_p in candidate_tra_path:
                    if c_t_p[2] < total_min_overlap:
                        total_min_overlap = c_t_p[2]
                        ava_path = c_t_p
                
                #开始资源分配
                for link in ava_path[0]:
                    overlap_value_matrix[link][ava_path[1]] = overlap_value_matrix[link][ava_path[1]] * net.network_status[link][ava_path[1]]
                    net.network_status[link][ava_path[1]] = net.network_status[link][ava_path[1]] - traffic['bw']
                    overlap_value_matrix[link][ava_path[1]] =  overlap_value_matrix[link][ava_path[1]] / net.network_status[link][ava_path[1]] #overlap度更新
                serv_path[traffic['id']] = {'traffic_path': [ava_path[0], ava_path[1], traffic['bw']]}
        
    for __, value in net.network_status.items():
        for __, re_bw in value.items():
            remain_bw_ = remain_bw_ + re_bw
                
        
    try:
        traffic_block_rate = traffic_block_num /  traffic_num
    except Exception as e:
        traffic_block_rate = 0

    print('Number of traffic services blocked:', traffic_block_num, ', blocking rate:{:.2%}'.format(traffic_block_rate))

    resource_sharing_rate = (remain_bw - remain_bw_) / remain_bw

    total_block_rate = (pro_block_num + traffic_block_num) / len(serv.serv_matrix)
    print('Total blocking rate:{:.2%}'.format(total_block_rate))
        
    Proportion_of_redundant_resources = total_allo_pro_serv_bw / total_bw
        
    print('The proportion of redundant resources:{:.2%}'.format(Proportion_of_redundant_resources))
        
    print('Resource sharing rate of traffic:{:.2%}\n'.format(resource_sharing_rate))

    resource_utilization_rate = (total_bw - remain_bw_) / total_bw

    print('Resource utilization rate of the whole network:{:.2%}\n'.format(resource_utilization_rate))
        
    return serv_path, shared_list


def caculate_overlap(net, serv_matrix:dict, link_status: dict, serv_path: list):
    flag = 0
    link_key_set = []
    overlap_value_set = []

    for link_key, link_value in link_status.items():

        wavelength_key_set = []
        max_overlap_value_set = []
        for wavelength_key, wavelength_value in link_value.items():

            temp_list = [] #统计该链路该波长上的备份路径的业务
            max_overlap_value = 0

            for temp in wavelength_value:
                if temp[1] == 'backup_path':
                    temp_list.append(temp[0])

            temp_wk_path = []
            temp_wave = []
            for t_l in temp_list:
                temp_wk_path.append([t_l, serv_path[t_l]['work_path'][0]])
                temp_wave.append(serv_path[t_l]['work_path'][1])

            delete = []

            '''for t_w in temp_wave:
                
                if t_w not in delete:
                    if temp_wave.count(t_w) > 1:
                        
                        delete.append(t_w)
                        wave_index_list = [a for a, b in enumerate(temp_wave) if b == t_w]
                        
                        wk_path = [temp_wk_path[i] for i in wave_index_list]
                        #print(wk_path)'''
            result = intersection(temp_wk_path)
            #print(result)
            if result != []:
                flag = flag + 1
                middle_overlap_value = 0
                for rl in result:

                    overlap_length = len(rl[0])
                    sumbw = 0
                    for sid in rl[1]:
                        sumbw = sumbw + serv_matrix[sid]['bw'] - serv_path[sid]['backup_path'][2]
                    temp_overlap_value = (overlap_length / net.link_num) * (sumbw / net.network_status[link_key][wavelength_key])
                    if temp_overlap_value > middle_overlap_value:
                        middle_overlap_value = temp_overlap_value
                    if middle_overlap_value > max_overlap_value:
                        max_overlap_value = middle_overlap_value
            wavelength_key_set.append(wavelength_key)
            max_overlap_value_set.append(max_overlap_value)
        overlap_wave_dict = dict(zip(wavelength_key_set, max_overlap_value_set))
        link_key_set.append(link_key)
        overlap_value_set.append(overlap_wave_dict)
    overlap_value_matrix = dict(zip(link_key_set, overlap_value_set))
    
    return overlap_value_matrix        



def intersection(big_list):          #排列组合，寻找重叠的工作路径/列表嵌套列表，找内部列表中相同的元素。
    if len(big_list) >= 17:
        big_list = big_list[:17]
    
    index = []
    for i in range(len(big_list)):
        index.append(i)

    #print(len(big_list))
    res_list = []

    for i in range(len(index) + 1):
        
        res_list += list(combinations(index, i))
        #print(res_list)

    all_cb = res_list[len(big_list)+1:]
    #print(all_cb)

    result = []
    for cb in all_cb:
        A_id = []
        
        count = 0
        A = big_list[cb[0]][1]
        A_id.append(big_list[cb[0]][0])
        for j in cb:
            count = count + 1

            if count < len(cb):
                A = set(A)&set(big_list[j+1][1])
                A_id.append(big_list[j+1][0])
            else:
                if A != set():

                    result.append([list(A),A_id])
    
    return result


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
    test_list = [[32,[21212,213213,454545,5454554]],[48,[5454554,454545,213213,543534534,5435345435]],[87,[4545453,45656546,213213]]]
    result = intersection(test_list)
    print(result)

    
    