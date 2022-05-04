# !usr/bin/env python
# -*- coding:utf-8 -*-

# this is for initalizing the network graph
# Jeyton Lee 2022-4-24 14:37:47


import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random
import os
import copy

from args import args
from Network import Graph
from operator import itemgetter

class Service:
    def __init__(self):
        self.serviceProportion = {
            2: 0.1,    100: 0.3,    500: 0.1, 
            1000: 0.2, 10000: 0.2, 25000: 0.1}

        self.serv_matrix = []
        self.serv_path = dict()
        self.pro_serv_num = None
        self.traffic_num = None

    def generate_service(self, g, pro_serv_num, traffic_num):
        print('----->正在按照比例随机生成业务，不同带宽的业务数量比例为：', self.serviceProportion)
        self.pro_serv_num = pro_serv_num
        self.traffic_num = traffic_num
        pro_service = []
        traffic = []
        pro_service = generate_proservice(g, self.serviceProportion, pro_serv_num)
        traffic = generate_unproservice(g, self.serviceProportion, traffic_num)
        self.serv_matrix = pro_service + traffic

        for i in range(pro_serv_num+traffic_num):
            self.serv_matrix[i].insert(0,i)

        print('----->业务初始化完成，总业务数量：', self.pro_serv_num + self.traffic_num,'，其中保护类业务数量：', self.pro_serv_num, '，其他流量数量：', self.traffic_num)

def generate_proservice(g, serv_prop: dict, pro_serv_num: int):
    
    np.set_printoptions(suppress=True)
    
    # Chose service bandwidth from the bandwidth set according to the service proportion
    serv_band = np.array([])
    for key, value in serv_prop.items():
        band = np.array([key]*int(value*pro_serv_num))
        serv_band = np.concatenate([serv_band, band])
    np.random.shuffle(serv_band)
    
    #Construct random protected service list
    pro_serv_list = []
    for i in range(pro_serv_num):
        rand_src = random.randint(1,g.node_num)
        rand_dst = random.randint(1,g.node_num)
        while(rand_src == rand_dst):
            rand_dst = random.randint(1,g.node_num)
        rand_reli = round(random.uniform(0.5,1),2)
        pro_serv = ['P', rand_src, rand_dst, serv_band[i], rand_reli, None]
        pro_serv_list.append(pro_serv)
    
    return(pro_serv_list)

def generate_unproservice(g, serv_prop: dict, traffic_num: int) -> list:
    
    np.set_printoptions(suppress=True)
    
    # Chose service bandwidth from the bandwidth set according to the service proportion
    serv_band = np.array([])
    for key, value in serv_prop.items():
        band = np.array([key]*int(value*traffic_num))
        serv_band = np.concatenate([serv_band, band])
    np.random.shuffle(serv_band)
    
    #Construct random unprotected service list
    traffic_list = []
    for i in range(traffic_num):
        rand_src = random.randint(1,g.node_num)
        rand_dst = random.randint(1,g.node_num)
        while(rand_src == rand_dst):
            rand_dst = random.randint(1,g.node_num)
        single_traffic = ['T', rand_src, rand_dst, serv_band[i], 0, None]
        traffic_list.append(single_traffic)
    
    return(traffic_list)

if __name__ == '__main__':
    g = Graph()
    g.graph_read('NSFNET.md')
    g.graph_init()

    s = Service()

    keys = [2,100,500]
    print(itemgetter(*keys)(s.serviceProportion))
    s.generate_service(g, 200, 300)