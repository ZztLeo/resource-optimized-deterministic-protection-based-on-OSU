# !usr/bin/env python
# -*- coding:utf-8 -*-

# Main function
# Jeyton Lee 2022-4-28 22:59:32


import function as fc
import fault_trigger as Ft
import exclusive as ec
import base_line as bl
import heuristic as hr
import shared as sd
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


    #link_status_bl = dict()
    #link_status_bl = fc.link_status_statistics(net, serv_path_bl)

    serv_path_bl = dict()
    serv_path_bl = ec.baseline(net, serv.serv_matrix, pro_serv_num, traffic_num, serv.total_pro_bw, serv.total_traffic_bw)

    #link_status_bl = dict()
    #link_status_bl = fc.link_status_statistics(net, serv_path_bl)
    #print(link_status)

    net_bl = cp.deepcopy(net)

    serv_path_bl = dict()
    serv_path_bl = sd.baseline(net, serv.serv_matrix, pro_serv_num, traffic_num, serv.total_pro_bw, serv.total_traffic_bw)

    serv_path_he = dict()
    serv_path_he = bl.baseline(net, serv.serv_matrix, pro_serv_num, traffic_num, serv.total_pro_bw, serv.total_traffic_bw)

    #link_status_he = dict()
    #link_status_he = fc.link_status_statistics(net, serv_path_he)

    total_fail_num_bl = 0
    total_impact_num_bl = 0
    total_fail_num_he = 0
    total_impact_num_he = 0


    '''print('----->Randomly trigger a single-port fault %d times...'%fault_time)
    for _ in range(fault_time):
        
        fault_link, fault_wavelength = Ft.random_fault(net)
        
        fail_serv_bl, impact_traffic_bl = Ft.fault_impact_statistics(net_bl, link_status_bl, fault_link, fault_wavelength, serv_path_bl, serv.serv_matrix)
        fail_serv_he, impact_traffic_he = Ft.fault_impact_statistics(net, link_status_he, fault_link, fault_wavelength, serv_path_he, serv.serv_matrix)

        total_fail_num_bl = total_fail_num_bl + len(fail_serv_bl)
        total_fail_num_he = total_fail_num_he + len(fail_serv_he)

        total_impact_num_bl = total_impact_num_bl + len(impact_traffic_bl)
        total_impact_num_he = total_impact_num_he + len(impact_traffic_he)
        
        # print('----->第%d次故障\n导致%d条受保护业务倒换失败，'%(i+1, len(fail_serv)),'业务id为：', fail_serv, '；导致%d条流量受到影响，'%(len(impact_traffic)),'流量id为：', impact_traffic)

    avg_fail_num_bl = total_fail_num_bl / fault_time
    avg_impact_num_bl = total_impact_num_bl / fault_time

    avg_fail_num_he = total_fail_num_he / fault_time
    avg_impact_num_he = total_impact_num_he / fault_time

    print('----->Baseline: after %d faults, the average %.2f protected services fail to switch due to insufficient resources (even if all traffic bandwidth is preempted), average %.2f traffic are affected'%(fault_time, avg_fail_num_bl, avg_impact_num_bl))


    print('----->Heuristic: after %d faults, the average %.2f protected services fail to switch due to insufficient resources (even if all traffic bandwidth is preempted), average %.2f traffic are affected'%(fault_time, avg_fail_num_he, avg_impact_num_he))'''




if __name__ == '__main__':
    simulation()