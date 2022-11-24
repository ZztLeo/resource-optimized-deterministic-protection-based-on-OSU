#!/bin/bash


# Path to network topology
NetworkTopoPath='resource'
NetworkTopoFile='NSFNET.md'



python main.py --file_prefix $NetworkTopoPath --topo_file $NetworkTopoFile --pro_service_num 4000 --traffic_num 12000 --fault_time 200