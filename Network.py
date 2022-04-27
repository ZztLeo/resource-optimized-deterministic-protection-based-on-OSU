# !usr/bin/env python
# -*- coding:utf-8 -*-

# this is for initalizing the network graph
# Jeyton Lee 2022-4-24 14:37:47


import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import os
import copy

from args import args


class Graph:
    def __init__(self):
        self.file_prefix = 'resource'
        self.G = None
        self.node_num = None
        self.link_num = None
        self.node_edge = None #node-edge relation ndarray
        self.link_capacity = 100000 #100Gbps of each link
        self.

    # initalize the graph
    def graph_init(self):
        G = nx.Graph()
        self.node_num = get_node_num(self.node_edge)
        self.link_num = get_link_num(self.node_edge)
        G.add_nodes_from([i for i in range(1, self.node_num+1)])
        G.add_weighted_edges_from(self.node_edge)
        self.G = G
        #print(type(self.G))

    # draw the graph topology
    def graph_draw(self):
        pos = nx.spring_layout(self.G) # choose a layout from https://networkx.github.io/documentation/latest/reference/drawing.html#module-networkx.drawing.layout
        weights = nx.get_edge_attributes(self.G, 'weight')
        nx.draw(self.G, pos, with_labels=True)
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=weights)
        plt.savefig('./topo.png')

    # read the graph file
    def graph_read(self, topo_file: str):
        """
        Format of file is md
        Content: |index|source|destination|weight|

        :param topo_file: network topology
        """
        file = os.path.join(self.file_prefix, topo_file)
        rtn = {}
        if os.path.isfile(file):
            datas = np.loadtxt(file, dtype = str, delimiter='|', skiprows=2)
            origin_data = datas[:, 1:(datas.shape[1]-1)]
            origin_data = np.array(origin_data, dtype = int) # change to int
            self.node_edge = origin_data[:, 1:(origin_data.shape[1])]
        else:
            raise FileNotFoundError

# get the number of network nodes
def get_node_num(node_edge) -> int:
    max_node_id = 0
    for i in node_edge:
        for j in i[1:2]:
            if j > max_node_id:
                max_node_id = j
    return max_node_id

# get the number of network links
def get_link_num(node_edge) -> int:
    max_link_id = node_edge.shape[0]
    return max_link_id


# main函数
if __name__ == '__main__':
    G = Graph()
    G.graph_read('NSFNET.md')
    G.graph_init()
    G.graph_draw()