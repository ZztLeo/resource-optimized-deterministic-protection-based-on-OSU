# !usr/bin/env python
# -*- coding:utf-8 -*-

# Main function
# Jeyton Lee 2022-4-28 22:59:32


import function as fc
import fault_trigger as Ft
import base_line as bl
import heuristic as hr
import copy as cp

from network import Network
from service import Service
from args import args


def simulation():
    
    file_prefix = args.file_prefix
    topo_file = args.topo_file
    pro_serv_num = args.pro_service_num
    traffic_num = args.traffic_num
    fault_time = args.fault_time

    print('----->Start Simulation...')
    net = Network()

    net.graph_read(file_prefix, topo_file)
    net.graph_init()


    serv = Service()
    serv.service_init(net, pro_serv_num, traffic_num)

    serv_matrix_pro = serv.serv_matrix[:pro_serv_num]
    serv_matrix_tra = serv.serv_matrix[-traffic_num:]

    # ksp + ksp
    print('----->KSP+KSP algorithm is planning services...')
    serv_path_kk = dict()
    serv_path_kk_ = dict()
    serv_path_kk, _ = bl.baseline(net, serv_matrix_pro, pro_serv_num, traffic_num, 0)
    serv_path_kk_, _ = bl.baseline(net, serv_matrix_tra, pro_serv_num, traffic_num, 1)

    serv_path_kk.update(serv_path_kk_)
    
    link_status_kk = dict()
    link_status_kk = fc.link_status_statistics(net, serv_path_kk)

    net_kk = cp.deepcopy(net)
    
    
    # ksp + TPA-ORA
    print('----->KSP+TPA-ORA algorithm is planning services...')
    serv_path_kt = dict()
    serv_path_kt, pro_block_num_kt = bl.baseline(net, serv_matrix_pro, pro_serv_num, traffic_num, 0)

    link_status_kt = dict()
    link_status_kt = fc.link_status_statistics(net, serv_path_kt)


    serv_path_kt = hr.heuristic_tra(net, serv.serv_matrix, traffic_num, link_status_kt, serv_path_kt, pro_block_num_kt)

    link_status_kt = dict()
    link_status_kt = fc.link_status_statistics(net, serv_path_kt)

    net_kt = cp.deepcopy(net)

    # DPA + ksp
    print('----->DPA+ksp algorithm is planning services...')
    serv_path_dk = dict()
    serv_path_dk, _ = hr.heuristic_pro(net, serv_matrix_pro, pro_serv_num, traffic_num)

    serv_path_dk_, _ = bl.baseline(net, serv_matrix_tra, pro_serv_num, traffic_num, 1)

    serv_path_dk.update(serv_path_dk_)

    link_status_dk = dict()
    link_status_dk = fc.link_status_statistics(net, serv_path_dk)
    net_dk = cp.deepcopy(net)


    # DPA + TPA-ORA
    print('----->DPA+TPA-ORA algorithm is planning services...')
    serv_path_dt = dict()
    serv_path_dt, pro_block_num_dt = hr.heuristic_pro(net, serv_matrix_pro, pro_serv_num, traffic_num)
    # print(serv_path_dt)
    link_status_dt = dict()
    link_status_dt = fc.link_status_statistics(net, serv_path_dt)
    
    #print(link_status_he)
    serv_path_dt = hr.heuristic_tra(net, serv.serv_matrix, traffic_num, link_status_dt, serv_path_dt, pro_block_num_dt)
    #print(serv_path_dt)
    link_status_dt = dict()
    link_status_dt = fc.link_status_statistics(net, serv_path_dt)
    net_dt = cp.deepcopy(net)

    total_fail_num_kk = 0
    total_impact_num_kk = 0
    total_fail_num_kt = 0
    total_impact_num_kt = 0
    total_fail_num_dk = 0
    total_impact_num_dk = 0
    total_fail_num_dt = 0
    total_impact_num_dt = 0


    print('----->Randomly trigger a single-port fault %d times...'%fault_time)
    for _ in range(fault_time):
        
        fault_link, fault_wavelength = Ft.random_fault(net)
        
        fail_serv_kk, impact_traffic_kk = Ft.fault_impact_statistics(net_kk, link_status_kk, fault_link, fault_wavelength, serv_path_kk, serv.serv_matrix)

        fail_serv_kt, impact_traffic_kt = Ft.fault_impact_statistics(net_kt, link_status_kt, fault_link, fault_wavelength, serv_path_kt, serv.serv_matrix)

        fail_serv_dk, impact_traffic_dk = Ft.fault_impact_statistics(net_dk, link_status_dk, fault_link, fault_wavelength, serv_path_dk, serv.serv_matrix)
        
        fail_serv_dt, impact_traffic_dt = Ft.fault_impact_statistics(net_dt, link_status_dt, fault_link, fault_wavelength, serv_path_dt, serv.serv_matrix)


        total_fail_num_kk = total_fail_num_kk + len(fail_serv_kk)
        total_fail_num_kt = total_fail_num_kt + len(fail_serv_kt)
        total_fail_num_dk = total_fail_num_dk + len(fail_serv_dk)
        total_fail_num_dt = total_fail_num_dt + len(fail_serv_dt)
        
        total_impact_num_kk = total_impact_num_kk + len(impact_traffic_kk)
        total_impact_num_kt = total_impact_num_kt + len(impact_traffic_kt)
        total_impact_num_dk = total_impact_num_dk + len(impact_traffic_dk)
        total_impact_num_dt = total_impact_num_dt + len(impact_traffic_dt)
        
        # print('----->第%d次故障\n导致%d条受保护业务倒换失败，'%(i+1, len(fail_serv)),'业务id为：', fail_serv, '；导致%d条流量受到影响，'%(len(impact_traffic)),'流量id为：', impact_traffic)

    avg_fail_num_kk = total_fail_num_kk / fault_time
    avg_impact_num_kk = total_impact_num_kk / fault_time

    avg_fail_num_kt = total_fail_num_kt / fault_time
    avg_impact_num_kt = total_impact_num_kt / fault_time

    avg_fail_num_dk = total_fail_num_dk / fault_time
    avg_impact_num_dk = total_impact_num_dk / fault_time

    avg_fail_num_dt = total_fail_num_dt / fault_time
    avg_impact_num_dt = total_impact_num_dt / fault_time

    print('----->ksp+ksp: after %d faults, the average %.2f protected services fail to switch due to insufficient resources (even if all traffic bandwidth is preempted), average %.2f traffic are affected'%(fault_time, avg_fail_num_kk, avg_impact_num_kk))

    print('----->ksp+TPA-ORA: after %d faults, the average %.2f protected services fail to switch due to insufficient resources (even if all traffic bandwidth is preempted), average %.2f traffic are affected'%(fault_time, avg_fail_num_kt, avg_impact_num_kt))

    print('----->DPA+ksp: after %d faults, the average %.2f protected services fail to switch due to insufficient resources (even if all traffic bandwidth is preempted), average %.2f traffic are affected'%(fault_time, avg_fail_num_dk, avg_impact_num_dk))

    print('----->DPA+TPA-ORA: after %d faults, the average %.2f protected services fail to switch due to insufficient resources (even if all traffic bandwidth is preempted), average %.2f traffic are affected'%(fault_time, avg_fail_num_dt, avg_impact_num_dt))



if __name__ == '__main__':
    simulation()
