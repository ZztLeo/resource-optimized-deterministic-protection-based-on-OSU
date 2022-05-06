# !usr/bin/env python
# -*- coding:utf-8 -*-

# Parameter setup
# Jeyton Lee 2022-05-06 16:04:52


import argparse

parser = argparse.ArgumentParser(description='OSU Protection')

parser.add_argument('--file_prefix', type=str , default = 'resource', metavar='PATH', help='path to network topology file')
parser.add_argument('--topo_file', type=str , default = 'NSFNET.md', metavar='PATH', help='network topology file name')
parser.add_argument('--pro_service_num', type=int, help='number of protected services')
parser.add_argument('--traffic_num', type=int, help='number of traffic')
parser.add_argument('--fault_time', type=int, help='times of fault')



args = parser.parse_args()