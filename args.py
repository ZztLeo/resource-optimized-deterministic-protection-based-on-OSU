# !usr/bin/env python
# -*- coding:utf-8 -*-

# this is for Graph
# Jeyton Lee 2022-4-24 14:37:47


import argparse

parser = argparse.ArgumentParser(description='OSU Protection')

parser.add_argument('--file_prefix', type=str , default = 'resource', metavar='PATH', help='path to network topology file')
parser.add_argument('--topo_file', type=str , default = 'NSFNET.md', metavar='PATH', help='network topology file name')
parser.add_argument('--pro_service_num', type=int, help='number of protected services')
parser.add_argument('--traffic_num', type=int, help='number of traffic')
parser.add_argument('--fault_time', type=int, help='times of fault')

parser.add_argument('--print', default='True', help='write out or not')

args = parser.parse_args()