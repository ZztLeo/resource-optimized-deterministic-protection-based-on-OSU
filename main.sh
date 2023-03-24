#!/bin/bash


# Path to network topology
NetworkTopoPath='resource'
NetworkTopoFile='NSFNET.md'



python main.py --file_prefix $NetworkTopoPath --topo_file $NetworkTopoFile --fault_type 'link' --N 0 --pro_service_num 3000 --traffic_num 3500 --fault_time 100