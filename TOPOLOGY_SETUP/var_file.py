# This file keeps all the variables.


# These lines DEFINE the variables for all DEVICES of the TOPOLOGY.
# Every device stores its access information in a dictionary.
# The "device_type" can be "cisco_ios","cisco_ios_telnet", "arista_eos", "arista_eos_telnet", "cisco_xe", "cisco_xr", "cisco_nxos".
# The "host" can be an ipv4 address (used for device management).
# The "username" can be defined.
# The "password" can be defined.
# The "secret" can be defined.
R1 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.1", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R2 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.2", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R3 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.3", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R4 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.4", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R5 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.5", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R6 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.6", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R7 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.7", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R8 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.8", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R9 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.9", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R10 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.10", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}


# A list with dictionaries of all the DEVICES.
HOSTS_LIST = [R1, R2, R3, R4, R5, R6, R7, R8, R9, R10]


# List with interconnections (interface/network pairs) of the topology.
INTERCONNECTIONS_LIST_STRING = []
INTERCONNECTIONS_LIST_LIST = []


# List with loopbacks (interface/network pairs) of the topology.
LOOPBACKS_LIST_STRING = []
LOOPBACKS_LIST_LIST = []


# List with segments of the topology.
SEGMENTS_LIST_STRING = []
SEGMENTS_LIST_LIST = []


# List for IGPs configuration.
RIP_LIST = []
EIGRP_LIST = []
OSPF_LIST = []
ISIS_AREAS_LIST = []
ISIS_LEVELS_LIST = []
ISIS_NETWORKS_LIST = []
