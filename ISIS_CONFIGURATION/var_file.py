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
SW11 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.11", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
SW12 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.12", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
SW13 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.13", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}


# A list with dictionaries of all the DEVICES.
HOSTS_LIST = [R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, SW11, SW12, SW13]


# Lists with ipv4 management addresses of DEVICES per ISIS LEVEL.
L1_ONLY_TARGETS_LIST = []
L2_ONLY_TARGETS_LIST = []
L1L2_TARGETS_LIST = []


# Lists with dictionaries of DEVICES per ISIS LEVEL.
L1_ONLY_HOSTS_LIST = []
L2_ONLY_HOSTS_LIST = []
L1L2_HOSTS_LIST = []


# List with pairs of ipv4 management address and 4-digits area.
TARGET_AREA_PAIRS_LIST = []


# Lists with networks per ISIS LEVEL.
L1_NETWORKS_LIST = []
L2_NETWORKS_LIST = []
L1L2_NETWORKS_LIST = []
