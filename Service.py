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

class Service:
    def __init__(self):
        self.serviceProportion = {
            2: 0.1,    100: 0.3,    500: 0.1, 
            1000: 0.2, 100000: 0.2, 250000: 0.1}
        self.pro_service = []
        self.unpro_service = []

    def generate_service(self, g, pro_serv_num, unpro_serv_num):
        self.pro_service = generate_proservice(g, self.serviceProportion, pro_serv_num)
        self.unpro_service = generate_unproservice(g, self.serviceProportion, unpro_serv_num)

        
        #print("=====>Protection Service List:", *self.pro_service,  sep='\n')
        #print("=====>unProtection Service List:",*self.unpro_service, sep='\n')


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
        pro_serv = [i, rand_src, rand_dst, serv_band[i], rand_reli, 'P']
        pro_serv_list.append(pro_serv)
    
    return(pro_serv_list)

def generate_unproservice(g, serv_prop: dict, unpro_serv_num: int) -> list:
    
    np.set_printoptions(suppress=True)
    
    # Chose service bandwidth from the bandwidth set according to the service proportion
    serv_band = np.array([])
    for key, value in serv_prop.items():
        band = np.array([key]*int(value*unpro_serv_num))
        serv_band = np.concatenate([serv_band, band])
    np.random.shuffle(serv_band)
    
    #Construct random unprotected service list
    unpro_serv_list = []
    for i in range(unpro_serv_num):
        rand_src = random.randint(1,g.node_num)
        rand_dst = random.randint(1,g.node_num)
        while(rand_src == rand_dst):
            rand_dst = random.randint(1,g.node_num)
        unpro_serv = [i, rand_src, rand_dst, serv_band[i], 0, 'U']
        unpro_serv_list.append(unpro_serv)
    
    return(unpro_serv_list)

if __name__ == '__main__':
    g = Graph()
    g.graph_read('NSFNET.md')
    g.graph_init()

    s = Service()
    s.generate_service(g, 200, 300)