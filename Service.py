# !usr/bin/env python
# -*- coding:utf-8 -*-

# Generate protected service and traffic matrix
# Jeyton Lee 2022-4-24 14:37:47

import numpy as np
import random

from network import Network
from operator import itemgetter

class Service:
    def __init__(self):
        self.serv_proportion = {
            2: 0.1,    100: 0.4, 
            1000: 0.3, 10000: 0.2}

        self.serv_matrix = dict() # key: servie id, value: service attributes
        # ['P/T', src, dst, bandwidth, reliability]
        self.pro_serv_num = None
        self.total_pro_bw = None
        self.traffic_num = None
        self.total_traffic_bw = None

    def service_init(self, net, pro_serv_num, traffic_num):
        """
        Generate protected services and traffic randomly.

        Args:
            net: A network class.
            pro_serv_num: Number of protected service.
            traffic_num: Number of traffic.
        """
        
        print('----->Generating services...\nProportion of services with different bandwidths:', self.serv_proportion, '\n')
        self.pro_serv_num = pro_serv_num
        self.traffic_num = traffic_num
        pro_service = []
        traffic = []
        #total_service = []
        pro_service, self.total_pro_bw = generate_pro_service(net, self.serv_proportion, pro_serv_num)
        traffic, self.total_traffic_bw = generate_unpro_service(net, self.serv_proportion, traffic_num)
        #total_service = pro_service + traffic #a attribute list of all services

        #Construct a service matrix dictionary
        '''serv_id = []
        for i in range(pro_serv_num+traffic_num):
            serv_id.append(i)
        self.serv_matrix = dict(zip(serv_id, total_service))'''
        self.serv_matrix = pro_service + traffic
        #print(self.serv_matrix)

        print('----->The service initialization is completed.\nTotal number of service:', self.pro_serv_num + self.traffic_num,', number of protected services:', self.pro_serv_num, ', number of other traffic:', self.traffic_num, '\n')

def generate_pro_service(net, serv_prop: dict, pro_serv_num: int) -> list:
    """
        Generate protected servicesrandomly.

        Args:
            net: A network class.
            serv_prop: The proportion of services with different bandwidths.
            pro_serv_num: Number of protected service.

        Return:
            pro_serv_list: A list of protected service. Content: ['P', src, dst, bandwidth, reliability, None]
    """
    np.set_printoptions(suppress=True)
    total_pro_bw = 0
    # Chose service bandwidth from the bandwidth set according to the service proportion
    serv_band = np.array([])
    for key, value in serv_prop.items():
        band = np.array([key]*int(value*pro_serv_num))
        serv_band = np.concatenate([serv_band, band])
        total_pro_bw = total_pro_bw + pro_serv_num * key * value
    np.random.shuffle(serv_band)
    #print(serv_band)
    
    #Construct random protected service list
    pro_serv_list = []
    for i in range(pro_serv_num):
        rand_src = random.randint(1,net.node_num)
        rand_dst = random.randint(1,net.node_num)
        while(rand_src == rand_dst):
            rand_dst = random.randint(1,net.node_num)
        rand_reli = round(random.uniform(0.5,1),2)
        pro_serv = {'id': i, 'type': 'P', 'src_dst': [rand_src, rand_dst], 'bw': serv_band[i], 'reli': rand_reli}
        #pro_serv = ['P', rand_src, rand_dst, serv_band[i], rand_reli]
        pro_serv_list.append(pro_serv)
    
    return pro_serv_list, total_pro_bw

def generate_unpro_service(net, serv_prop: dict, traffic_num: int) -> list:
    """
        Generate protected servicesrandomly.

        Args:
            net: A network class.
            serv_prop: The proportion of services with different bandwidths.
            traffic_num: Number of traffic.

        Return:
            traffic_list: A list of traffic. Content: ['T', src, dst, bandwidth, 0, None]
    """
    np.set_printoptions(suppress=True)
    
    total_traffic_bw = 0
    # Chose service bandwidth from the bandwidth set according to the service proportion
    serv_band = np.array([])
    for key, value in serv_prop.items():
        band = np.array([key]*int(value*traffic_num))
        serv_band = np.concatenate([serv_band, band])
        total_traffic_bw = total_traffic_bw + traffic_num * key * value
    np.random.shuffle(serv_band)
    
    #Construct random unprotected service list
    traffic_list = []
    for i in range(traffic_num):
        rand_src = random.randint(1,net.node_num)
        rand_dst = random.randint(1,net.node_num)
        while(rand_src == rand_dst):
            rand_dst = random.randint(1,net.node_num)
        single_traffic = {'id': i, 'type': 'T', 'src_dst': [rand_src, rand_dst], 'bw': serv_band[i], 'reli': 0}
        #single_traffic = ['T', rand_src, rand_dst, serv_band[i], 0]
        traffic_list.append(single_traffic)
    
    return traffic_list, total_traffic_bw

if __name__ == '__main__':
    net = Network()
    net.graph_read('NSFNET.md')
    net.graph_init()

    serv = Service()

    keys = [2,100,500]
    print(itemgetter(*keys)(serv.serviceProportion))
    serv.generate_service(net, 200, 300)