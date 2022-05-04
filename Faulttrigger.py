from os import stat
import networkx as nx
import numpy as np
import copy as cp
import random

from Network import Graph

def random_fault(Net) -> str:
    rand_faultlink = random.randint(0,Net.link_num - 1) # 随机选择链路故障
    rand_faultdir = random.randint(0,1) # 随机选择正向或反向链路故障(0表示正向链路故障，1为反向链路故障)
    
    if rand_faultdir == 0:
        fault_link = str(Net.node_edge[rand_faultlink][0])+'->'+str(Net.node_edge[rand_faultlink][1])
    else:
        fault_link = str(Net.node_edge[rand_faultlink][1])+'->'+str(Net.node_edge[rand_faultlink][0])

    return fault_link



# main函数
if __name__ == '__main__':
    G = Graph()
    G.graph_read('NSFNET.md')
    G.graph_init()