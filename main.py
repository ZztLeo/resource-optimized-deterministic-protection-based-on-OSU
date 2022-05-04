# !usr/bin/env python
# -*- coding:utf-8 -*-

# this is for planing services
# Jeyton Lee 2022-4-28 22:59:32


from os import stat
import networkx as nx
import numpy as np
import Algorithms as Algo
import Faulttrigger as Ft

from Network import Graph
from Service import Service


def simulation():
    print('----->开始仿真...')
    Net = Graph()
    topo_file = 'NSFNET.md'
    Net.graph_read(topo_file)
    Net.graph_init()
    
    S = Service()
    S.generate_service(Net, 300, 200)

    np.set_printoptions(suppress=True)
    Algo.heuristic(Net, S)

    link_status = dict()
    link_status = Algo.statistics_link_status(Net, S)
    np.set_printoptions(suppress=True)

    fault_num = 1

    print('----->随机触发%d次故障'%fault_num)
    for i in range(fault_num):
        fault_link = Ft.random_fault(Net)
        print(fault_link)
        impact = link_status[fault_link][1:] # 所有故障导致中断的业务

        switch_serv = [] # 待倒换的保护业务
        interr_traffic = [] # 故障引起中断的流量
        # 统计故障引起的待倒换保护业务和中断的流量列表
        for im in impact:
            
            if im[1] == 'work_path':
                switch_serv.append(im[0])
                
            elif im[1] == 'traffic_path':
                interr_traffic.append(im[0])

        print(switch_serv)
        # 统计故障引起的待倒换保护业务倒换会影响的流量数量
        for sw_s_id in switch_serv:
            print(S.serv_path[sw_s_id])


        




if __name__ == '__main__':
    simulation()
