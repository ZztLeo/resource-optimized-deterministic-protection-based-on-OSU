# !usr/bin/env python
# -*- coding:utf-8 -*-

# Construct a network
# Jeyton Lee 2022-4-24 14:37:47


import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import os
import copy as cp


class Network:
    def __init__(self):
        self.graph = None
        self.node_num = None
        self.link_num = None
        self.node_edge = None # node-edge relation ndarray
        self.link_capacity = 100000 # 100Gbps of each wavelength
        self.wavelength_num = 40 # 40 wavelength of each link
        self.network_status = dict() 
        # {A->B: {wavelength1: bandwidth, wavelength2: bandwidth, wavelength3: bandwidth...}...}

    # initialize a network graph
    def graph_init(self):
        g = nx.Graph()
        self.node_num = get_node_num(self.node_edge)
        self.link_num = get_link_num(self.node_edge)
        g.add_nodes_from([i for i in range(1, self.node_num+1)])
        g.add_weighted_edges_from(self.node_edge)
        g = g.to_directed()
        self.graph = g

        status_key = []
        status_value = []
        for link in self.node_edge:
            status_key.append(str(link[0])+'->'+str(link[1]))
            status_key.append(str(link[1])+'->'+str(link[0]))
            
            # construct wavelength dictionary
            wl_key = []
            wl_value = []
            for wl in range(self.wavelength_num):
                wl_key.append(wl)
                wl_value.append(self.link_capacity)
            status_value.append(dict(zip(wl_key, wl_value)))
            status_value.append(dict(zip(wl_key, wl_value)))
        self.network_status = dict(zip(status_key, status_value))
        # print(self.network_status)
        print('----->Bidirectional network initialization completed.\n', self.node_num,'nodes,', self.link_num, 'links,', self.wavelength_num, 'wavelengths of each link,', 'single-wavelength capacity:', self.link_capacity, '\n')
        
    def graph_remove_nodes(self, node_list):
        """
        Remove the specified node from the network graph (for computing protection path).
        
        Args:
            node_list: A list of nodes to remove.
        """
        self.graph.remove_nodes_from(node_list)

    # draw the graph topology
    def graph_draw(self):
        pos = nx.spring_layout(self.G) # choose a layout from https://networkx.github.io/documentation/latest/reference/drawing.html#module-networkx.drawing.layout
        weights = nx.get_edge_attributes(self.G, 'weight')
        nx.draw(self.G, pos, with_labels=True)
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=weights)
        plt.savefig('./topo.png')

    def graph_read(self, file_prefix: str, topo_file: str):
        """
        Read the graph file. 
        Format of file is md. Content: |index|source|destination|weight|
        
        Args:
            topo_file: A network topology file.
        """
        file = os.path.join(file_prefix, topo_file)
        print('----->The network file read is complete.\nTopology:', topo_file[:-3], '\n')

        if os.path.isfile(file):
            datas = np.loadtxt(file, dtype = str, delimiter='|', skiprows=2)
            origin_data = datas[:, 1:(datas.shape[1]-1)]
            origin_data = np.array(origin_data, dtype = int) # change to int
            self.node_edge = origin_data[:, 1:(origin_data.shape[1])]
        else:
            raise FileNotFoundError
    
    def network_status_reset(self):
        for key, value in self.network_status.items():
            for waveid, _ in value.items():
                self.network_status[key][waveid] = self.link_capacity

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


# main function
if __name__ == '__main__':
    g = Network()
    g.graph_read('NSFNET.md')
    g.graph_init()
    g.graph_draw()