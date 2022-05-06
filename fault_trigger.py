
import random

from network import Network


def random_fault(net) -> str:
    """
    Randomly trigger a single-port fault.

    Args:
        net: A instance of Network class. 
    
    Returns:
        fault_link: The fault link string (A->B).
    """
    rand_faultlink = random.randint(0,net.link_num - 1) # 随机选择链路故障
    rand_faultdir = random.randint(0,1) # 随机选择正向或反向链路故障(0表示正向链路故障，1为反向链路故障)
    
    if rand_faultdir == 0:
        fault_link = str(net.node_edge[rand_faultlink][0])+'->'+str(net.node_edge[rand_faultlink][1])
    else:
        fault_link = str(net.node_edge[rand_faultlink][1])+'->'+str(net.node_edge[rand_faultlink][0])

    return fault_link

def fault_impact_statistics(link_status: dict, fault_link: str, serv_path: dict, serv_matrix: dict):
        
    impact = link_status[fault_link][1:] # All service disruptions caused by fault

    switch_serv = [] # Protection services to be switched
    interr_traffic = [] # Traffic disrupted by fault
    # Count services to be switched and interrupted traffic caused by fault (list)
    for im in impact:
        
        if im[1] == 'work_path':
            switch_serv.append(im[0])
            
        elif im[1] == 'traffic_path':
            interr_traffic.append(im[0])

    #print(switch_serv)
    # Statistics on the number of traffic affected by the protection service switching
    backup_path_list = []
    for sw_s_id in switch_serv:
        backup_path = serv_path[sw_s_id]['backup_path']
        for j in range(len(backup_path) - 1):
            l = str(backup_path[j])+'->'+str(backup_path[j + 1])
            if l not in backup_path_list:
                backup_path_list.append(l)
    # count = dict(Counter(backup_path_list))
    # multi_serv_link = [key for key, value in count.items() if value > 1]
    # print(backup_path_list)
    fail_serv = []
    impact_traffic = []
    for bl in backup_path_list:
        rest_bw = link_status[bl][0]
        # print(rest_bw)
        total_serv_bw = 0
        total_traff_bw = 0
        traffic_list = []
        serv_list = []

        for ls in link_status[bl][1:]:
            if ls[1] == 'backup_path':
                if ls[0] in switch_serv:
                    serv_list.append(ls[0])
                    # print(S.serv_matrix[ls[0]])
                    total_serv_bw = total_serv_bw + (serv_matrix[ls[0]][3] - 2)
            elif ls[1] == 'traffic_path':
                traffic_list.append(ls[0])
                total_traff_bw = total_traff_bw + serv_matrix[ls[0]][3]
            
        # print(total_serv_bw)
        if rest_bw < total_serv_bw:

            d_value = total_serv_bw - rest_bw
            if d_value > total_traff_bw:
                fail_serv.append(serv_list)
            else:
                impact_traffic.append(traffic_list)

    fail_serv = sum(fail_serv, [])
    fail_serv = set(fail_serv)

    impact_traffic = sum(impact_traffic, [])
    impact_traffic = set(impact_traffic)
    
    return fail_serv, impact_traffic

# main function
if __name__ == '__main__':
    G = Network()
    G.graph_read('NSFNET.md')
    G.graph_init()