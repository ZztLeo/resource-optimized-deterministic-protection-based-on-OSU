#!/bin/bash


# Path to network topology
NetworkTopoPath='resource'
NetworkTopoFile='NSFNET.md'



python main.py --file_prefix $NetworkTopoPath --topo_file $NetworkTopoFile --pro_service_num 500 --traffic_num 400 --fault_time 200