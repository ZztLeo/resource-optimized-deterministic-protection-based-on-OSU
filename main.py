# !usr/bin/env python
# -*- coding:utf-8 -*-

# Main function
# Jeyton Lee 2022-4-28 22:59:32


import function as fc
import fault_trigger as Ft
import base_line as bl
import heuristic as he

import copy as cp
import exclusive as ec
import shared as sh

from network import Network
from service import Service
from args import args


def simulation():
    
    file_prefix = args.file_prefix
    topo_file = args.topo_file
    pro_serv_num = args.pro_service_num
    traffic_num = args.traffic_num
    fault_time = args.fault_time
    fault_type = args.fault_type
    N = args.N

    print('----->Start Simulation...')
    net = Network()

    net.graph_read(file_prefix, topo_file)
    net.graph_init()


    serv = Service()
    serv.service_init(net, pro_serv_num, traffic_num)

    serv_matrix_pro = serv.serv_matrix[:pro_serv_num]

    serv_matrix_tra = serv.serv_matrix[pro_serv_num + 1:]

    
    # OSU-P with heuristic

    print('----->OSU-P is working...')
    serv_path_1, total_allo_pro_serv_bw, pro_block_num_1 = he.heuristic_pro(net, serv_matrix_pro, fault_type, N, pro_serv_num, traffic_num)

    serv_path_1_, _, _, shared_list_1 = bl.baseline(net, serv, serv_path_1, serv_matrix_tra, N, fault_type, pro_serv_num, traffic_num, total_allo_pro_serv_bw, pro_block_num_1, 1, True)
    #print(len(shared_list_1))
    link_status_1 = fc.link_status_statistics(net, serv_path_1_)
    net_osu_p = cp.deepcopy(net)


    # OSU-P with heuristic for preempted traffic

    print('----->OSU-P_PTP is working...')
    serv_path_4, total_allo_pro_serv_bw, pro_block_num_4 = he.heuristic_pro(net, serv_matrix_pro, fault_type, N, pro_serv_num, traffic_num)
    link_status_4 = fc.link_status_statistics(net, serv_path_4)

    serv_path_4_, shared_list_4 = he.heuristic_tra(net, serv, serv_path_4, link_status_4, serv_matrix_tra, pro_serv_num, traffic_num, total_allo_pro_serv_bw, pro_block_num_4, True)
    link_status_4_ = fc.link_status_statistics(net, serv_path_4_)
    net_osu_p_ptp = cp.deepcopy(net)

    # 1+1 SNCP
    print('----->1+1 SNCP is working...')

    serv_path_2, total_allo_pro_serv_bw, pro_block_num_2 = ec.heuristic_pro(net, serv_matrix_pro, fault_type, pro_serv_num)
    serv_path_2_, _, _, _ = bl.baseline(net, serv, serv_path_2, serv_matrix_tra, N, fault_type, pro_serv_num, traffic_num, total_allo_pro_serv_bw, pro_block_num_2, 1, False)

    link_status_2 = fc.link_status_statistics(net, serv_path_2_)

    net_1plus1 = cp.deepcopy(net)


    # 1:1 SNCP
    print('----->1:1 SNCP is working...')
    serv_path_3, total_allo_pro_serv_bw, pro_block_num_3 = sh.heuristic_pro(net, serv_matrix_pro, fault_type, pro_serv_num)
    serv_path_3_, _, _, shared_list_3 = bl.baseline(net, serv, serv_path_3, serv_matrix_tra, N, fault_type, pro_serv_num, traffic_num, total_allo_pro_serv_bw, pro_block_num_3, 1, True)


    link_status_3 = fc.link_status_statistics(net, serv_path_3_)

    net_1to1 = cp.deepcopy(net)


    total_fail_num_1 = 0
    total_impact_num_1 = 0
    total_num_swtich_1 = 0

    total_fail_num_2 = 0
    total_impact_num_2 = 0
    total_num_swtich_2 = 0

    total_fail_num_3 = 0
    total_impact_num_3 = 0
    total_num_swtich_3 = 0

    total_fail_num_4 = 0
    total_impact_num_4 = 0
    total_num_swtich_4 = 0


    print('----->Randomly trigger a single-%s, fault %d times...' %(fault_type, fault_time))
    for _ in range(fault_time):
        #print(x)
        fault_point = Ft.random_fault(net, fault_type)
        
        fail_serv_1, impact_traffic_1, num_switch_1 = Ft.fault_impact_statistics(net_osu_p, link_status_1, fault_point, serv_path_1, serv.serv_matrix, shared_list_1)

        fail_serv_2, impact_traffic_2, num_switch_2 = Ft.fault_impact_statistics(net_1plus1, link_status_2, fault_point, serv_path_2, serv.serv_matrix, {})

        fail_serv_3, impact_traffic_3, num_switch_3 = Ft.fault_impact_statistics(net_1to1, link_status_3, fault_point, serv_path_3, serv.serv_matrix, shared_list_3)

        fail_serv_4, impact_traffic_4, num_switch_4 = Ft.fault_impact_statistics(net_osu_p_ptp, link_status_4_, fault_point, serv_path_4_, serv.serv_matrix, shared_list_4)


        total_fail_num_1 = total_fail_num_1 + len(fail_serv_1)
        total_fail_num_2 = total_fail_num_2 + len(fail_serv_2)
        total_fail_num_3 = total_fail_num_3 + len(fail_serv_3)
        total_fail_num_4 = total_fail_num_4 + len(fail_serv_4)

        
        total_impact_num_1 = total_impact_num_1 + len(impact_traffic_1)
        total_impact_num_2 = total_impact_num_2 + len(impact_traffic_2)
        total_impact_num_3 = total_impact_num_3 + len(impact_traffic_3)
        total_impact_num_4 = total_impact_num_4 + len(impact_traffic_4)
        
        total_num_swtich_1 = total_num_swtich_1 + num_switch_1
        total_num_swtich_2 = total_num_swtich_2 + num_switch_2
        total_num_swtich_3 = total_num_swtich_3 + num_switch_3
        total_num_swtich_4 = total_num_swtich_4 + num_switch_4
      

    avg_fail_num_1 = total_fail_num_1 / fault_time
    avg_impact_num_1 = total_impact_num_1 / fault_time
    avg_switch_1 = total_num_swtich_1 / fault_time

    avg_fail_num_2 = total_fail_num_2 / fault_time
    avg_impact_num_2 = total_impact_num_2 / fault_time
    avg_switch_2 = total_num_swtich_2 / fault_time

    avg_fail_num_3 = total_fail_num_3 / fault_time
    avg_impact_num_3 = total_impact_num_3 / fault_time
    avg_switch_3 = total_num_swtich_3 / fault_time

    avg_fail_num_4 = total_fail_num_4 / fault_time
    avg_impact_num_4 = total_impact_num_4 / fault_time
    avg_switch_4 = total_num_swtich_4 / fault_time

    try:
        per_unsuc_1 = avg_fail_num_1 / avg_switch_1
    except Exception as e:
        per_unsuc_1 = 0
    try:
        per_unsuc_2 = avg_fail_num_2 / avg_switch_2
    except Exception as e:
        per_unsuc_2 = 0
    try:
        per_unsuc_3 = avg_fail_num_3 / avg_switch_3
    except Exception as e:
        per_unsuc_3 = 0
    try:
        per_unsuc_4 = avg_fail_num_4 / avg_switch_4
    except Exception as e:
        per_unsuc_4 = 0


    print('----->OSU-P: after %d faults, the average %.2f protected services need to be switched, average %.2f protected services fail to switch due to insufficient resources (even if all traffic bandwidth is preempted), percentage of unsuccessful protection is %.2f, average %.2f traffic are affected'%(fault_time, avg_switch_1, avg_fail_num_1, per_unsuc_1, avg_impact_num_1))

    print('----->1+1 SNCP: after %d faults, the average %.2f protected services need to be switched, average %.2f protected services fail to switch due to insufficient resources (even if all traffic bandwidth is preempted), percentage of unsuccessful protection is %.2f, average %.2f traffic are affected'%(fault_time, avg_switch_2, avg_fail_num_2, per_unsuc_2, avg_impact_num_2))

    print('----->1:1 SNCP: after %d faults, the average %.2f protected services need to be switched, average %.2f protected services fail to switch due to insufficient resources (even if all traffic bandwidth is preempted), percentage of unsuccessful protection is %.2f, average %.2f traffic are affected'%(fault_time, avg_switch_3, avg_fail_num_3, per_unsuc_3, avg_impact_num_3))

    print('----->OSU-P_PTP: after %d faults, the average %.2f protected services need to be switched, average %.2f protected services fail to switch due to insufficient resources (even if all traffic bandwidth is preempted), percentage of unsuccessful protection is %.2f, average %.2f traffic are affected'%(fault_time, avg_switch_4, avg_fail_num_4, per_unsuc_4, avg_impact_num_4))


    '''print('----->ksp+TPA-ORA: after %d faults, the average %.2f protected services fail to switch due to insufficient resources (even if all traffic bandwidth is preempted), average %.2f traffic are affected'%(fault_time, avg_fail_num_kt, avg_impact_num_kt))

    print('----->DPA+ksp: after %d faults, the average %.2f protected services fail to switch due to insufficient resources (even if all traffic bandwidth is preempted), average %.2f traffic are affected'%(fault_time, avg_fail_num_dk, avg_impact_num_dk))

    print('----->DPA+TPA-ORA: after %d faults, the average %.2f protected services fail to switch due to insufficient resources (even if all traffic bandwidth is preempted), average %.2f traffic are affected'%(fault_time, avg_fail_num_dt, avg_impact_num_dt))'''



if __name__ == '__main__':
    simulation()
