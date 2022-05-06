# !usr/bin/env python
# -*- coding:utf-8 -*-

# Main function
# Jeyton Lee 2022-4-28 22:59:32


import base_function as bf
import fault_trigger as Ft
import algorithm as algo

from network import Network
from service import Service
from collections import Counter


def simulation():


    print('----->Start Simulation...')
    net = Network()
    topo_file = 'NSFNET.md'
    net.graph_read(topo_file)
    net.graph_init()
    
    serv = Service()
    serv.generate_service(net, 300, 200)

    algo.baseline(net, serv)

    link_status = dict()
    link_status = bf.link_status_statistics(net, serv)

    fault_num = 500
    total_fail_num = 0
    total_impact_num = 0

    print('----->Randomly trigger a single-port fault %d times...'%fault_num)
    for _ in range(fault_num):
        fault_link = Ft.random_fault(net)
        
        fail_serv, impact_traffic = Ft.fault_impact_statistics(link_status, fault_link, serv. serv_path, serv.serv_matrix)

        total_fail_num = total_fail_num + len(fail_serv)

        total_impact_num = total_impact_num + len(impact_traffic)
        # print('----->第%d次故障\n导致%d条受保护业务倒换失败，'%(i+1, len(fail_serv)),'业务id为：', fail_serv, '；导致%d条流量受到影响，'%(len(impact_traffic)),'流量id为：', impact_traffic)

    avg_fail_num = total_fail_num / fault_num
    avg_impact_num = total_impact_num / fault_num

    print('----->After %d faults, the average %.2f protected services fail to switch due to insufficient resources (even if all traffic bandwidth is preempted), average %.2f traffics are affected'%(fault_num, avg_fail_num, avg_impact_num))





if __name__ == '__main__':
    simulation()
