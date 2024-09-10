# This line imports the needed Functions from netmiko
from netmiko import ConnectHandler
# This line imports the os, sys, time, datetime, random, string, shutil, ipaddress, subprocess, concurrent.futures Modules
import os, sys, time, datetime, random, string, shutil, ipaddress, subprocess, concurrent.futures



# Devices access information (NETMIKO)
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
R11 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.11", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R12 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.12", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R13 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.13", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}
R14 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.14", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}



# Devices to be configured
HOSTS = [R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, R11, R12, R13, R14]



# GNS3 INTERFACES
MANAGEMENT_INTERFACE = ["Ethernet0/0", "10.0.0.0/24"]
TOPOLOGY_INTERFACE = ["Ethernet0/1"]



# INTRASITE (function)
INTRASITE = ["11.0.0.0/8", "12.0.0.0/8", "Loopback13-13.0.0.0/8", ["1-2-3-4-#1", "1-5-#1", "2-5-#1", "3-6-#1", "3-6-#2"]]



# PROTOCOLS (functions per protocol)
PROTOCOLS = ["RIP", "EIGRP", "OSPF", "ISIS", "IBGP", "MPLS"]
RIP = ["1", "2", "3", "4", "5", "6"]
EIGRP = ["1", ["1", "2", "3", "4", "5", "6"]]
OSPF = ["1", ["0", "1", "2", "3", "4"], ["1", "5"], ["2", "6"]]
INTERAREA_LINKS = ["1-5-#1", "2-5-#1", "3-6-#1", "3-6-#2"]
ISIS_L2 = [["4", "4"]]
ISIS_L1_L2 = [["125", "1", "2"], ["36", "3"]]
ISIS_L1 = [["125", "5"], ["36", "6"]]
IBGP = ["65001", "Loopback13", ["1", "2", "3", "4", "5", "6"]]
MPLS = ["Loopback13", ["1", "2", "3", "4", "5", "6"]]



# INTERSITE (function)
INTERSITE = ["101.0.0.0/8", "102.0.0.0/8", "Loopback103-103.0.0.0/8", ["1#65001", "7#65007"], ["1#65001", "8#65008", "9#65009"]]



"""
FUNCTIONS DEPENDENCIES
The INTERSITE function requires the INTRASITE List

FUNCTIONS ORDER
INTRASITE   ->  PROTOCOLS (RIP, EIGRP, OSPF, ISIS, IBGP, MPLS)  ->  INTERSITE
"""



"""
INTRASITE = ["11.0.0.0/8", "12.0.0.0/8", "Loopback13-13.0.0.0/8", ["1-2-3-4-#1", "1-5-#1", "2-5-#1", "3-6-#1", "3-6-#2"]]
The intersite configuration is described by a List having the following format:
INTRASITE = ["P2P_INTRASITE_NETWORK_X/8", "P2MP_INTRASITE_NETWORK_Y/8", "LoopbackZ-LOOPBACK_INTRASITE_NETWORK_Z/8", ["ID_X1-ID_X2-ID_X3-#LINK_INSTANCE", "ID_Y1-ID_Y2-#LINK_INSTANCE", "ID_Z1-ID_Z2-#LINK_INSTANCE" ...]]
CONSTRAINTS
Any p2p link (specific pair of devices) CANNOT have more than 2 instances (LINK_INSTANCE)!!!
Any p2mp link (specific set of devices) CANNOT have more than 1 instance (LINK_INSTANCE)!!!
Any p2mp link CANNOT have the same MAX_ID AND the same MIN_ID with any other p2mp link!!!

DOT1Qs
p2p and MAX_ID < 10 and LINK_INSTANCE == 1:                             for 1st ->                  str(MAX_ID) + str(MIN_ID)
p2p and MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 1:            for 1st ->                  str(1) + str(MAX_ID)[-1] + str(MIN_ID)
p2p and MIN_ID >= 10 and LINK_INSTANCE == 1:                            for 1st ->                  str(2) + str(MAX_ID)[-1] + str(MIN_ID)[-1]
p2p and MAX_ID < 10 and LINK_INSTANCE == 2:                             for 2nd ->                  str(3) + str(MAX_ID) + str(MIN_ID)
p2p and MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 2:            for 2nd ->                  str(4) + str(MAX_ID)[-1] + str(MIN_ID)
p2p and MIN_ID >= 10 and LINK_INSTANCE == 2:                            for 2nd ->                  str(5) + str(MAX_ID)[-1] + str(MIN_ID)[-1]
p2mp and MAX_ID < 10 and LINK_INSTANCE == 1:                                    ->                  str(6) + str(MAX_ID) + str(MIN_ID)
p2mp and MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 1:                   ->                  str(7) + str(MAX_ID) + str(MIN_ID)
p2mp and MIN_ID >= 10 and LINK_INSTANCE == 1:                                   ->                  str(8) + str(MAX_ID) + str(MIN_ID)
loopbacks                                                                       ->                  DO NOT NEEDED

IPs
p2p and MAX_ID < 10 and LINK_INSTANCE == 1:                             for 1st ->                  P2P_INTRASITE_NETWORK_X.str(100).dot1q.str(ID)/24
p2p and MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 1:            for 1st ->                  P2P_INTRASITE_NETWORK_X.str(100).dot1q.str(ID)/24
p2p and MIN_ID >= 10 and LINK_INSTANCE == 1:                            for 1st ->                  P2P_INTRASITE_NETWORK_X.str(100).dot1q.str(ID)/24
p2p and MAX_ID < 10 and LINK_INSTANCE == 2:                             for 2nd ->                  P2P_INTRASITE_NETWORK_X.str(200).str(MAX_ID) + str(MIN_ID).str(ID)/24
p2p and MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 2:            for 2nd ->                  P2P_INTRASITE_NETWORK_X.str(200).str(1) + str(MAX_ID)[-1] + str(MIN_ID).str(ID)/24
p2p and MIN_ID >= 10 and LINK_INSTANCE == 2:                            for 2nd ->                  P2P_INTRASITE_NETWORK_X.str(200).str(2) + str(MAX_ID)[-1] + str(MIN_ID)[-1].str(ID)/24
p2mp and MAX_ID < 10 and LINK_INSTANCE == 1:                                    ->                  P2MP_INTRASITE_NETWORK_Y.str(100).str(MAX_ID) + str(MIN_ID).str(ID)/24
p2mp and MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 1:                   ->                  P2MP_INTRASITE_NETWORK_Y.str(100).str(1) + str(MAX_ID)[-1] + str(MIN_ID).str(ID)/24
p2mp and MIN_ID >= 10 and LINK_INSTANCE == 1:                                   ->                  P2MP_INTRASITE_NETWORK_Y.str(100).str(2) + str(MAX_ID)[-1] + str(MIN_ID)[-1].str(ID)/24
loopbacks                                                                       ->                  LOOPBACK_INTRASITE_NETWORK_Z.str(ID).str(ID).str(ID)/24
"""



"""
PROTOCOLS = ["RIP", "EIGRP", "OSPF", "ISIS", "IBGP", "MPLS"]
The protocols used in topology are described by a List having the following format:
PROTOCOLS = ["PROTOCOL_1", "PROTOCOL_2" ...]
The values can be "RIP", "EIGRP", "OSPF", "ISIS", "IBGP", "MPLS"!!!

RIP = ["1", "2", "3", "4", "5", "6"]
The networks configured with RIP are described by a List having the following format:
RIP = ["ID_X1", "ID_X2", "ID_X3" ...]

EIGRP = ["1", ["1", "2", "3", "4", "5", "6"]]
The networks configured with EIGRP are described by a List having the following format:
EIGRP = ["AS", ["ID_X1", "ID_X2", "ID_X3" ...]]

OSPF = ["1", ["0", "1", "2", "3", "4"], ["1", "5"], ["2", "6"]]
INTERAREA_LINKS = ["1-5-#1", "2-5-#1", "3-6-#1", "3-6-#2"]
The networks configured with OSPF are described by 2 Lists having the following format:
OSPF = ["PROCESS_NUMBER", ["0", "ID_X1", "ID_X2" ...], ["AREA_NUMBER_Y", "ID_Y1", "ID_Y2" ...], ["AREA_NUMBER_Z", "ID_Z1", "ID_Z2" ...] ...]
INTERAREA_LINKS = ["ID_X1-ID_Y1-ID_Z1-#LINK_INSTANCE", "ID_X2-ID_Y2-#LINK_INSTANCE", "ID_X2-ID_Z2-#LINK_INSTANCE" ...]
The ABRS are in NON BACKBONE Areas!!!

ISIS_L2 = [["4", "4"]]
ISIS_L1_L2 = [["125", "1", "2"], ["36", "3"]]
ISIS_L1 = [["125", "5"], ["36", "6"]]
The networks configured with ISIS are described by 3 Lists having the following format:
ISIS_L2 = [["AREA_X", "ID_X1", "ID_X2" ...], ["AREA_Y", "ID_Y1", "ID_Y2" ...] ...]
ISIS_L1_L2 = [["AREA_K", "ID_K1", "ID_K2" ...], ["AREA_L", "ID_L1", "ID_L2" ...] ...]
ISIS_L1 = [["AREA_W", "ID_W1", "ID_W2" ...], ["AREA_V", "ID_V1", "ID_V2" ...] ...]

IBGP = ["65001", "Loopback13", ["1", "2", "3", "4", "5", "6"]]
The networks configured with BGP are described by a List having the following format:
IBGP = ["ASN", "LOOPBACK_INTERFACE", ["ID_X1", "ID_X2" ...]]

MPLS = ["Loopback13", ["1", "2", "3", "4", "5", "6"]]
The networks configured with MPLS are described by a List having the following format:
MPLS = ["LOOPBACK_INTERFACE", ["ID_X1", "ID_X2" ...]]
"""



"""
INTERSITE = ["101.0.0.0/8", "102.0.0.0/8", "Loopback103-103.0.0.0/8", ["1#65001", "7#65007"], ["1#65001", "8#65008", "9#65009"]]
The intersite configuration is described by a List having the following format:
INTERSITE = ["P2P_INTERSITE_NETWORK_X/8", "P2MP_INTERSITE_NETWORK_Y/8", "LoopbackZ-LOOPBACK_INTERSITE_NETWORK_Z/8", ["ID_W1#ASN_W1", "ID_W2#ASN_W2"], ["ID_W3#ASN_W3", "ID_W4#ASN_W4", "ID_W5#ASN_W5"] ...]
CONSTRAINTS
Any p2p link (specific pair of devices) CANNOT have more than 1 instances (LINK_INSTANCE)!!!
Any p2mp link (specific set of devices) CANNOT have more than 1 instance (LINK_INSTANCE)!!!
Any p2mp link CANNOT have the same MAX_ID AND the same MIN_ID with any other p2mp link!!!

DOT1Qs
p2p and MAX_ID < 10:                            ->                  str(MAX_ID) + str(MIN_ID)
p2p and MAX_ID >= 10 and MIN_ID < 10:           ->                  str(1) + str(MAX_ID)[-1] + str(MIN_ID)
p2p and MIN_ID >= 10:                           ->                  str(2) + str(MAX_ID)[-1] + str(MIN_ID)[-1]
p2mp and MAX_ID < 10:                           ->                  str(6) + str(MAX_ID) + str(MIN_ID)
p2mp and MAX_ID >= 10 and MIN_ID < 10:          ->                  str(7) + str(MAX_ID) + str(MIN_ID)
p2mp and MIN_ID >= 10:                          ->                  str(8) + str(MAX_ID) + str(MIN_ID)
loopbacks                                       ->                  DO NOT NEEDED

IPs
p2p and MAX_ID < 10:                            ->                  P2P_INTERSITE_NETWORK.str(100).dot1q.str(ID)/24
p2p and MAX_ID >= 10 and MIN_ID < 10:           ->                  P2P_INTERSITE_NETWORK.str(100).dot1q.str(ID)/24
p2p and MIN_ID >= 10:                           ->                  P2P_INTERSITE_NETWORK.str(100).dot1q.str(ID)/24
p2mp and MAX_ID < 10:                           ->                  P2MP_INTERSITE_NETWORK.str(100).str(MAX_ID) + str(MIN_ID).str(ID)/24
p2mp and MAX_ID >= 10 and MIN_ID < 10:          ->                  P2MP_INTERSITE_NETWORK.str(100).str(1) + str(MAX_ID)[-1] + str(MIN_ID).str(ID)/24
p2mp and MIN_ID >= 10:                          ->                  P2MP_INTERSITE_NETWORK.str(100).str(2) + str(MAX_ID)[-1] + str(MIN_ID)[-1].str(ID)/24
loopbacks                                       ->                  LOOPBACK_INTERSITE_NETWORK_Z.str(ID).str(ID).str(ID)/24
"""



def intrasite(INPUT_DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Finds host ID.
    HOST_HOSTNAME = net_connect.find_prompt()[:-1]
    ID = ""
    for character in HOST_HOSTNAME:
        if character.isdigit():
            ID = ID + character
            ID = str(ID)
        else:
            pass

    # Finds hosts participating in intrasite topology.
    TRACK_HOSTS = []
    for element in INTRASITE[3]:
        for item in element.split("-")[:-1]:
            TRACK_HOSTS.append(item)

    #Sends configuration.
    if str(ID) in TRACK_HOSTS:
        COMMANDS = []
        X = INTRASITE[2]
        C1 = "interface " + X.split("-")[0]
        C2 = "ip address " + X.split("-")[1].split(".")[0] + "." + str(ID) + "." + str(ID) + "." + str(ID) + " 255.255.255.0"
        COMMANDS.append(C1)
        COMMANDS.append(C2)
        for element in INTRASITE[3]:
            X = element.split("-")
            LINK_INSTANCE = int(X[-1].strip("#"))
            X.pop()
            X = [int(i) for i in X]
            MIN_ID = min(X)
            MAX_ID = max(X)
            if int(ID) in X and len(X) == 2:
                C3 = "interface " + TOPOLOGY_INTERFACE[0]
                C4 = "no shutdown"
                COMMANDS.append(C3)
                COMMANDS.append(C4)
                if MAX_ID < 10 and LINK_INSTANCE == 1:
                    C5 = "interface " + TOPOLOGY_INTERFACE[0] + "." + str(MAX_ID) + str(MIN_ID)
                    C6 = "encapsulation dot1Q " + str(MAX_ID) + str(MIN_ID)
                    C7 = "ip address " + INTRASITE[0].split(".")[0] + "." + str(100) + "." + str(MAX_ID) + str(MIN_ID) + "." + str(ID) + " 255.255.255.0"
                    COMMANDS.append(C5)
                    COMMANDS.append(C6)
                    COMMANDS.append(C7)
                elif MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 1:
                    C5 = "interface " + TOPOLOGY_INTERFACE[0] + "." + "1" + str(MAX_ID)[1] + str(MIN_ID)
                    C6 = "encapsulation dot1Q " + "1" + str(MAX_ID)[1] + str(MIN_ID)
                    C7 = "ip address " + INTRASITE[0].split(".")[0] + "." + str(100) + "." + "1" + str(MAX_ID)[1] + str(MIN_ID) + "." + str(ID) + " 255.255.255.0"
                    COMMANDS.append(C5)
                    COMMANDS.append(C6)
                    COMMANDS.append(C7)
                elif MIN_ID >= 10 and LINK_INSTANCE == 1:
                    C5 = "interface " + TOPOLOGY_INTERFACE[0] + "." + "2" + str(MAX_ID)[1] + str(MIN_ID)[1]
                    C6 = "encapsulation dot1Q " + "2" + str(MAX_ID)[1] + str(MIN_ID)[1]
                    C7 = "ip address " + INTRASITE[0].split(".")[0] + "." + str(100) + "." + "2" + str(MAX_ID)[1] + str(MIN_ID)[1] + "." + str(ID) + " 255.255.255.0"
                    COMMANDS.append(C5)
                    COMMANDS.append(C6)
                    COMMANDS.append(C7)
                elif MAX_ID < 10 and LINK_INSTANCE == 2:
                    C5 = "interface " + TOPOLOGY_INTERFACE[0] + "." + "3" + str(MAX_ID) + str(MIN_ID)
                    C6 = "encapsulation dot1Q " + "3" + str(MAX_ID) + str(MIN_ID)
                    C7 = "ip address " + INTRASITE[0].split(".")[0] + "." + str(200) + "." + str(MAX_ID) + str(MIN_ID) + "." + str(ID) + " 255.255.255.0"
                    COMMANDS.append(C5)
                    COMMANDS.append(C6)
                    COMMANDS.append(C7)
                elif MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 2:
                    C5 = "interface " + TOPOLOGY_INTERFACE[0] + "." + "4" + str(MAX_ID)[1] + str(MIN_ID)
                    C6 = "encapsulation dot1Q " + "4" + str(MAX_ID)[1] + str(MIN_ID)
                    C7 = "ip address " + INTRASITE[0].split(".")[0] + "." + str(200) + "." + "1" + str(MAX_ID)[1] + str(MIN_ID) + "." + str(ID) + " 255.255.255.0"
                    COMMANDS.append(C5)
                    COMMANDS.append(C6)
                    COMMANDS.append(C7)
                elif MIN_ID >= 10 and LINK_INSTANCE == 2:
                    C5 = "interface " + TOPOLOGY_INTERFACE[0] + "." + "5" + str(MAX_ID)[1] + str(MIN_ID)[1]
                    C6 = "encapsulation dot1Q " + "5" + str(MAX_ID)[1] + str(MIN_ID)[1]
                    C7 = "ip address " + INTRASITE[0].split(".")[0] + "." + str(200) + "." + "2" + str(MAX_ID)[1] + str(MIN_ID)[1] + "." + str(ID) + " 255.255.255.0"
                    COMMANDS.append(C5)
                    COMMANDS.append(C6)
                    COMMANDS.append(C7)
                else:
                    pass
            elif int(ID) in X and len(X) != 2:
                C3 = "interface " + TOPOLOGY_INTERFACE[0]
                C4 = "no shutdown"
                COMMANDS.append(C3)
                COMMANDS.append(C4)
                if MAX_ID < 10:
                    C5 = "interface " + TOPOLOGY_INTERFACE[0] + "." + "6" + str(MAX_ID) + str(MIN_ID)
                    C6 = "encapsulation dot1Q " + "6" + str(MAX_ID) + str(MIN_ID)
                    C7 = "ip address " + INTRASITE[1].split(".")[0] + "." + str(100) + "." + str(MAX_ID) + str(MIN_ID) + "." + str(ID) + " 255.255.255.0"
                    COMMANDS.append(C5)
                    COMMANDS.append(C6)
                    COMMANDS.append(C7)
                elif MAX_ID >= 10 and MIN_ID < 10:
                    C5 = "interface " + TOPOLOGY_INTERFACE[0] + "." + "7" + str(MAX_ID)[1] + str(MIN_ID)
                    C6 = "encapsulation dot1Q " + "7" + str(MAX_ID)[1] + str(MIN_ID)
                    C7 = "ip address " + INTRASITE[1].split(".")[0] + "." + str(100) + "." + "1" + str(MAX_ID)[1] + str(MIN_ID) + "." + str(ID) + " 255.255.255.0"
                    COMMANDS.append(C5)
                    COMMANDS.append(C6)
                    COMMANDS.append(C7)
                elif MIN_ID >= 10:
                    C5 = "interface " + TOPOLOGY_INTERFACE[0] + "." + "8" + str(MAX_ID)[1] + str(MIN_ID)[1]
                    C6 = "encapsulation dot1Q " + "8" + str(MAX_ID)[1] + str(MIN_ID)[1]
                    C7 = "ip address " + INTRASITE[1].split(".")[0] + "." + str(100) + "." + "2" + str(MAX_ID)[1] + str(MIN_ID)[1] + "." + str(ID) + " 255.255.255.0"
                    COMMANDS.append(C5)
                    COMMANDS.append(C6)
                    COMMANDS.append(C7)
                else:
                    pass
            else:
                pass
    else:
        pass

    try:
        # Print configuration commands.
        print(COMMANDS)

        # Sends configuration commands.
        net_connect.send_config_set(COMMANDS)
    except:
        pass

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Disconnects from host.
    net_connect.disconnect()



def rip(INPUT_DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Finds host ID.
    HOST_HOSTNAME = net_connect.find_prompt()[:-1]
    ID = ""
    for character in HOST_HOSTNAME:
        if character.isdigit():
            ID = ID + character
            ID = str(ID)
        else:
            pass

    # Finds hosts participating in intrasite topology.
    TRACK_HOSTS = RIP

    # Sends execution commands.
    exec_output = net_connect.send_command("show ip interface | include Internet address | line protocol")

    # Creates a temporary file (if the specified file does not exist) and overwrites any existing content (if there is).
    random_string = ''.join(random.choices(string.ascii_letters, k=10))
    with open("interfaces_temporary" + random_string, "w") as f:
        # Print the output of execution commands sent to host via Telnet/SSH.
        print(exec_output, file=f)

    # Finds interface address pairs configured on host.
    INTERFACE_ADDRESS_PAIRS_LIST = []
    with open("interfaces_temporary" + random_string, "r") as f:
        previous_line = ""
        for line in f:
            if "Internet address" in line:
                INTERFACE_ADDRESS_PAIRS_LIST.append([previous_line.split()[0], line.split()[3]])
            else:
                pass
            previous_line = line

    # Deletes the temporary file.
    if os.path.exists("interfaces_temporary" + random_string):
        os.remove("interfaces_temporary" + random_string)
    else:
        pass

    # Finds MAJOR NETWORKS configured on host (other than the MANAGEMENT INTERFACE).
    MAJOR_NETWORKS = []
    for element in INTERFACE_ADDRESS_PAIRS_LIST:
        if element[0] == "Ethernet0/0":
            pass
        else:
            X = ipaddress.ip_network(element[1], strict = False)
            N1 = ipaddress.ip_network(INTRASITE[0], strict = False)
            N2 = ipaddress.ip_network(INTRASITE[1], strict = False)
            N3 = ipaddress.ip_network(INTRASITE[2].split("-")[1], strict = False)
            if X.subnet_of(N1) and INTRASITE[0] not in MAJOR_NETWORKS:
                MAJOR_NETWORKS.append(INTRASITE[0])
            elif X.subnet_of(N2) and INTRASITE[1] not in MAJOR_NETWORKS:
                MAJOR_NETWORKS.append(INTRASITE[1])
            elif X.subnet_of(N3) and INTRASITE[2].split("-")[1] not in MAJOR_NETWORKS:
                MAJOR_NETWORKS.append(INTRASITE[2].split("-")[1])
            else:
                pass

    # RIP commands.
    if str(ID) in TRACK_HOSTS and len(MAJOR_NETWORKS) > 0:
        RIP_COMMANDS = []
        C1 = "router rip"
        C2 = "version 2"
        C3 = "no auto-summary"
        RIP_COMMANDS.append(C1)
        RIP_COMMANDS.append(C2)
        RIP_COMMANDS.append(C3)
        for element in MAJOR_NETWORKS:
            Cn = "network " + element.split("/")[0]
            RIP_COMMANDS.append(Cn)
    else:
        pass

    try:
        # Print configuration commands.
        print(RIP_COMMANDS)

        # Sends configuration commands.
        net_connect.send_config_set(RIP_COMMANDS)
    except:
        pass

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Disconnects from host.
    net_connect.disconnect()



def eigrp(INPUT_DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Finds host ID.
    HOST_HOSTNAME = net_connect.find_prompt()[:-1]
    ID = ""
    for character in HOST_HOSTNAME:
        if character.isdigit():
            ID = ID + character
            ID = str(ID)
        else:
            pass

    # Finds hosts participating in intrasite topology.
    TRACK_HOSTS = EIGRP[1]

    # Sends execution commands.
    exec_output = net_connect.send_command("show ip interface | include Internet address | line protocol")

    # Creates a temporary file (if the specified file does not exist) and overwrites any existing content (if there is).
    random_string = ''.join(random.choices(string.ascii_letters, k=10))
    with open("interfaces_temporary" + random_string, "w") as f:
        # Print the output of execution commands sent to host via Telnet/SSH.
        print(exec_output, file=f)

    # Finds interface address pairs configured on host.
    INTERFACE_ADDRESS_PAIRS_LIST = []
    with open("interfaces_temporary" + random_string, "r") as f:
        previous_line = ""
        for line in f:
            if "Internet address" in line:
                INTERFACE_ADDRESS_PAIRS_LIST.append([previous_line.split()[0], line.split()[3]])
            else:
                pass
            previous_line = line

    # Deletes the temporary file.
    if os.path.exists("interfaces_temporary" + random_string):
        os.remove("interfaces_temporary" + random_string)
    else:
        pass

    # Finds NETWORKS configured on host (other than the MANAGEMENT INTERFACE).
    NETWORKS = []
    for element in INTERFACE_ADDRESS_PAIRS_LIST:
        if element[0] == "Ethernet0/0":
            pass
        else:
            X = ipaddress.ip_network(element[1], strict = False)
            N1 = ipaddress.ip_network(INTRASITE[0], strict = False)
            N2 = ipaddress.ip_network(INTRASITE[1], strict = False)
            N3 = ipaddress.ip_network(INTRASITE[2].split("-")[1], strict = False)
            if X.subnet_of(N1) and INTRASITE[0] not in NETWORKS:
                NETWORKS.append(INTRASITE[0])
            elif X.subnet_of(N2) and INTRASITE[1] not in NETWORKS:
                NETWORKS.append(INTRASITE[1])
            elif X.subnet_of(N3) and INTRASITE[2].split("-")[1] not in NETWORKS:
                NETWORKS.append(INTRASITE[2].split("-")[1])
            else:
                pass

    # EIGRP commands.
    if str(ID) in TRACK_HOSTS and len(NETWORKS) > 0:
        EIGRP_COMMANDS = []
        C1 = "router eigrp " + EIGRP[0]
        C2 = "eigrp router-id " + str(ID) + "." + str(ID) + "." + str(ID) + "." + str(ID)
        C3 = "no auto-summary"
        EIGRP_COMMANDS.append(C1)
        EIGRP_COMMANDS.append(C2)
        EIGRP_COMMANDS.append(C3)
        for element in NETWORKS:
            Cn = "network " + element.split("/")[0]
            EIGRP_COMMANDS.append(Cn)
    else:
        pass

    try:
        # Print configuration commands.
        print(EIGRP_COMMANDS)

        # Sends configuration commands.
        net_connect.send_config_set(EIGRP_COMMANDS)
    except:
        pass

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Disconnects from host.
    net_connect.disconnect()



def ospf(INPUT_DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Finds host ID.
    HOST_HOSTNAME = net_connect.find_prompt()[:-1]
    ID = ""
    for character in HOST_HOSTNAME:
        if character.isdigit():
            ID = ID + character
            ID = str(ID)
        else:
            pass

    # Finds hosts participating in intrasite topology.
    TRACK_HOSTS = []
    for element in OSPF[1:]:
        for item in element[1:]:
            if item not in TRACK_HOSTS:
                TRACK_HOSTS.append(item)
            else:
                pass

    # Sends execution commands.
    exec_output = net_connect.send_command("show ip interface | include Internet address | line protocol")

    # Creates a temporary file (if the specified file does not exist) and overwrites any existing content (if there is).
    random_string = ''.join(random.choices(string.ascii_letters, k=10))
    with open("interfaces_temporary" + random_string, "w") as f:
        # Print the output of execution commands sent to host via Telnet/SSH.
        print(exec_output, file=f)

    # Finds interface address pairs configured on host.
    INTERFACE_ADDRESS_PAIRS_LIST = []
    with open("interfaces_temporary" + random_string, "r") as f:
        previous_line = ""
        for line in f:
            if "Internet address" in line:
                INTERFACE_ADDRESS_PAIRS_LIST.append([previous_line.split()[0], line.split()[3]])
            else:
                pass
            previous_line = line

    # Deletes the temporary file.
    if os.path.exists("interfaces_temporary" + random_string):
        os.remove("interfaces_temporary" + random_string)
    else:
        pass

    #Finds Backbone - NonBackbone networks.
    BB_NONBB_NETWORKS = []
    P2P_NET = INTRASITE[0].split(".")[0]
    P2MP_NET = INTRASITE[1].split(".")[0]
    for element in INTERAREA_LINKS:
        X = element.split("-")
        LINK_INSTANCE = int(X[-1].strip("#"))
        X.pop()
        X = [int(i) for i in X]
        MIN_ID = min(X)
        MAX_ID = max(X)
        NETWORKS = ""
        if int(ID) in X and len(X) == 2:
            if MAX_ID < 10 and LINK_INSTANCE == 1:
                NETWORKS = P2P_NET + "." + str(100) + "." + str(MAX_ID) + str(MIN_ID) + "." + str(ID) + "/24"
                BB_NONBB_NETWORKS.append(NETWORKS)
            elif MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 1:
                NETWORKS = P2P_NET + "." + str(100) + "." + "1" + str(MAX_ID)[1] + str(MIN_ID) + "." + str(ID) + "/24"
                BB_NONBB_NETWORKS.append(NETWORKS)
            elif MIN_ID >= 10 and LINK_INSTANCE == 1:
                NETWORKS = P2P_NET + "." + str(100) + "." + "2" + str(MAX_ID)[1] + str(MIN_ID)[1] + "." + str(ID) + "/24"
                BB_NONBB_NETWORKS.append(NETWORKS)
            elif MAX_ID < 10 and LINK_INSTANCE == 2:
                NETWORKS = P2P_NET + "." + str(200) + "." + str(MAX_ID) + str(MIN_ID) + "." + str(ID) + "/24"
                BB_NONBB_NETWORKS.append(NETWORKS)
            elif MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 2:
                NETWORKS = P2P_NET + "." + str(200) + "." + "1" + str(MAX_ID)[1] + str(MIN_ID) + "." + str(ID) + "/24"
                BB_NONBB_NETWORKS.append(NETWORKS)
            elif MIN_ID >= 10 and LINK_INSTANCE == 2:
                NETWORKS = P2P_NET + "." + str(200) + "." + "2" + str(MAX_ID)[1] + str(MIN_ID)[1] + "." + str(ID) + "/24"
                BB_NONBB_NETWORKS.append(NETWORKS)
            else:
                pass
        elif int(ID) in X and len(X) != 2:
            if MAX_ID < 10:
                NETWORKS = P2MP_NET + "." + str(100) + "." + str(MAX_ID) + str(MIN_ID) + "." + str(ID) + "/24"
                BB_NONBB_NETWORKS.append(NETWORKS)
            elif MAX_ID >= 10 and MIN_ID < 10:
                NETWORKS = P2MP_NET + "." + str(100) + "." + "1" + str(MAX_ID)[1] + str(MIN_ID) + "." + str(ID) + "/24"
                BB_NONBB_NETWORKS.append(NETWORKS)
            elif MIN_ID >= 10:
                NETWORKS = P2MP_NET + "." + str(100) + "." + "2" + str(MAX_ID)[1] + str(MIN_ID)[1] + "." + str(ID) + "/24"
                BB_NONBB_NETWORKS.append(NETWORKS)
            else:
                pass
        else:
            pass

    # OSPF commands.
    if str(ID) in TRACK_HOSTS:
        OSPF_COMMANDS = []
        C1 = "router ospf " + OSPF[0]
        C2 = "router-id " + str(ID) + "." + str(ID) + "." + str(ID) + "." + str(ID)
        OSPF_COMMANDS.append(C1)
        OSPF_COMMANDS.append(C2)
        for element in OSPF[1:]:
            if str(ID) in element[1:]:
                for item in INTERFACE_ADDRESS_PAIRS_LIST:
                    if item[0] != MANAGEMENT_INTERFACE[0] and item[1] not in BB_NONBB_NETWORKS:
                        Cn = "interface " + item[0]
                        Cm = "ip ospf " + OSPF[0] + " area " + element[0]
                        OSPF_COMMANDS.append(Cn)
                        OSPF_COMMANDS.append(Cm)
                    elif item[0] != MANAGEMENT_INTERFACE[0] and item[1] in BB_NONBB_NETWORKS:
                        Cn = "interface " + item[0]
                        Cm = "ip ospf " + OSPF[0] + " area " + "0"
                        OSPF_COMMANDS.append(Cn)
                        OSPF_COMMANDS.append(Cm)
                    else:
                        pass
            else:
                pass
    else:
        pass

    try:
        # Print configuration commands.
        print(OSPF_COMMANDS)

        # Sends configuration commands.
        net_connect.send_config_set(OSPF_COMMANDS)
    except:
        pass

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Disconnects from host.
    net_connect.disconnect()



def isis(INPUT_DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Finds host ID.
    HOST_HOSTNAME = net_connect.find_prompt()[:-1]
    ID = ""
    for character in HOST_HOSTNAME:
        if character.isdigit():
            ID = ID + character
            ID = str(ID)
        else:
            pass

    # Finds hosts participating in intrasite topology.
    TRACK_HOSTS = []
    for element in ISIS_L2:
        TRACK_HOSTS = TRACK_HOSTS + element[1:]
    for element in ISIS_L1_L2:
        TRACK_HOSTS = TRACK_HOSTS + element[1:]
    for element in ISIS_L1:
        TRACK_HOSTS = TRACK_HOSTS + element[1:]

    # Sends execution commands.
    exec_output = net_connect.send_command("show ip interface | include Internet address | line protocol")

    # Creates a temporary file (if the specified file does not exist) and overwrites any existing content (if there is).
    random_string = ''.join(random.choices(string.ascii_letters, k=10))
    with open("interfaces_temporary" + random_string, "w") as f:
        # Print the output of execution commands sent to host via Telnet/SSH.
        print(exec_output, file=f)

    # Finds interface address pairs configured on host.
    INTERFACE_ADDRESS_PAIRS_LIST = []
    with open("interfaces_temporary" + random_string, "r") as f:
        previous_line = ""
        for line in f:
            if "Internet address" in line:
                INTERFACE_ADDRESS_PAIRS_LIST.append([previous_line.split()[0], line.split()[3]])
            else:
                pass
            previous_line = line

    # Deletes the temporary file.
    if os.path.exists("interfaces_temporary" + random_string):
        os.remove("interfaces_temporary" + random_string)
    else:
        pass

    # ISIS commands.
    if str(ID) in TRACK_HOSTS:
        ISIS_COMMANDS = []
        C1 = "router isis"
        C2 = "router-id " + INTRASITE[2].split("-")[0]
        ISIS_COMMANDS.append(C1)
        ISIS_COMMANDS.append(C2)
        for element in ISIS_L2:
            if str(ID) in element[1:]:
                AREA = element[0]
                AREA_4_DIGIT =AREA.zfill(4)
                ID_4_DIGIT = str(ID).zfill(4)
                Cu = "net " + "49." + AREA_4_DIGIT + ".0000.0000." + ID_4_DIGIT + ".00"
                Cv = "is-type level-2-only"
                ISIS_COMMANDS.append(Cu)
                ISIS_COMMANDS.append(Cv)
            else:
                pass
        for element in ISIS_L1_L2:
            if str(ID) in element[1:]:
                AREA = element[0]
                AREA_4_DIGIT =AREA.zfill(4)
                ID_4_DIGIT = str(ID).zfill(4)
                Cw = "net " + "49." + AREA_4_DIGIT + ".0000.0000." + ID_4_DIGIT + ".00"
                Cx = "is-type level-1-2"
                ISIS_COMMANDS.append(Cw)
                ISIS_COMMANDS.append(Cx)
            else:
                pass
        for element in ISIS_L1:
            if str(ID) in element[1:]:
                AREA = element[0]
                AREA_4_DIGIT =AREA.zfill(4)
                ID_4_DIGIT = str(ID).zfill(4)
                Cy = "net " + "49." + AREA_4_DIGIT + ".0000.0000." + ID_4_DIGIT + ".00"
                Cz = "is-type level-1"
                ISIS_COMMANDS.append(Cy)
                ISIS_COMMANDS.append(Cz)
            else:
                pass
        for element in INTERFACE_ADDRESS_PAIRS_LIST:
            if element[0] != MANAGEMENT_INTERFACE[0]:
                Cn = "interface " + element[0]
                Cm = "ip router isis"
                ISIS_COMMANDS.append(Cn)
                ISIS_COMMANDS.append(Cm)
            else:
                pass
    else:
        pass

    try:
        # Print configuration commands.
        print(ISIS_COMMANDS)

        # Sends configuration commands.
        net_connect.send_config_set(ISIS_COMMANDS)
    except:
        pass

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Disconnects from host.
    net_connect.disconnect()



def ibgp(INPUT_DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Finds host ID.
    HOST_HOSTNAME = net_connect.find_prompt()[:-1]
    ID = ""
    for character in HOST_HOSTNAME:
        if character.isdigit():
            ID = ID + character
            ID = str(ID)
        else:
            pass

    # Finds hosts participating in intrasite topology.
    TRACK_HOSTS = IBGP[2]

    # Sends execution commands.
    exec_output = net_connect.send_command("show ip interface | include Internet address | line protocol")

    # Creates a temporary file (if the specified file does not exist) and overwrites any existing content (if there is).
    random_string = ''.join(random.choices(string.ascii_letters, k=10))
    with open("interfaces_temporary" + random_string, "w") as f:
        # Print the output of execution commands sent to host via Telnet/SSH.
        print(exec_output, file=f)

    # Finds interface address pairs configured on host.
    INTERFACE_ADDRESS_PAIRS_LIST = []
    with open("interfaces_temporary" + random_string, "r") as f:
        previous_line = ""
        for line in f:
            if "Internet address" in line:
                INTERFACE_ADDRESS_PAIRS_LIST.append([previous_line.split()[0], line.split()[3]])
            else:
                pass
            previous_line = line

    # Deletes the temporary file.
    if os.path.exists("interfaces_temporary" + random_string):
        os.remove("interfaces_temporary" + random_string)
    else:
        pass

    # Finds loopback interface ip.
    for element in INTERFACE_ADDRESS_PAIRS_LIST:
        if element[0] == IBGP[1]:
            LOOPBACK_IP = element[1]
        else:
            pass

    # IBGP commands.
    if str(ID) in TRACK_HOSTS:
        IBGP_COMMANDS = []
        C1 = "router bgp " + IBGP[0]
        C2 = "bgp router-id " + str(ID) + "." + str(ID) + "." + str(ID) + "." + str(ID)
        IBGP_COMMANDS.append(C1)
        IBGP_COMMANDS.append(C2)
        for element in TRACK_HOSTS:
            if element != str(ID):
                Cv = "neighbor " + LOOPBACK_IP.split(".")[0] + "." + element + "." + element + "." + element + " remote-as " + IBGP[0]
                Cw = "neighbor " + LOOPBACK_IP.split(".")[0] + "." + element + "." + element + "." + element + " update-source " + IBGP[1]
                Cx = "address-family ipv4"
                Cy = "neighbor " + LOOPBACK_IP.split(".")[0] + "." + element + "." + element + "." + element + " activate"
                Cz = "exit-address-family"
                IBGP_COMMANDS.append(Cv)
                IBGP_COMMANDS.append(Cw)
                IBGP_COMMANDS.append(Cx)
                IBGP_COMMANDS.append(Cy)
                IBGP_COMMANDS.append(Cz)
            else:
                pass
    else:
        pass

    try:
        # Print configuration commands.
        print(IBGP_COMMANDS)

        # Sends configuration commands.
        net_connect.send_config_set(IBGP_COMMANDS)
    except:
        pass

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Disconnects from host.
    net_connect.disconnect()



def mpls(INPUT_DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Finds host ID.
    HOST_HOSTNAME = net_connect.find_prompt()[:-1]
    ID = ""
    for character in HOST_HOSTNAME:
        if character.isdigit():
            ID = ID + character
            ID = str(ID)
        else:
            pass

    # Finds hosts participating in intrasite topology.
    TRACK_HOSTS = MPLS[1]

    # Sends execution commands.
    exec_output = net_connect.send_command("show ip interface | include Internet address | line protocol")

    # Creates a temporary file (if the specified file does not exist) and overwrites any existing content (if there is).
    random_string = ''.join(random.choices(string.ascii_letters, k=10))
    with open("interfaces_temporary" + random_string, "w") as f:
        # Print the output of execution commands sent to host via Telnet/SSH.
        print(exec_output, file=f)

    # Finds interface address pairs configured on host.
    INTERFACE_ADDRESS_PAIRS_LIST = []
    with open("interfaces_temporary" + random_string, "r") as f:
        previous_line = ""
        for line in f:
            if "Internet address" in line:
                INTERFACE_ADDRESS_PAIRS_LIST.append([previous_line.split()[0], line.split()[3]])
            else:
                pass
            previous_line = line

    # Deletes the temporary file.
    if os.path.exists("interfaces_temporary" + random_string):
        os.remove("interfaces_temporary" + random_string)
    else:
        pass

    # MPLS commands.
    if str(ID) in TRACK_HOSTS:
        MPLS_COMMANDS = []
        C1 = "mpls ip"
        C2 = "mpls ldp router-id " + MPLS[0]
        MPLS_COMMANDS.append(C1)
        MPLS_COMMANDS.append(C2)
        for element in INTERFACE_ADDRESS_PAIRS_LIST:
            if element[0].startswith("Loopback"):
                pass
            elif element[0] == MANAGEMENT_INTERFACE[0]:
                pass
            else:
                Cx = "interface " + element[0]
                Cy = "mpls ip"
                MPLS_COMMANDS.append(Cx)
                MPLS_COMMANDS.append(Cy)
    else:
        pass

    try:
        # Print configuration commands.
        print(MPLS_COMMANDS)

        # Sends configuration commands.
        net_connect.send_config_set(MPLS_COMMANDS)
    except:
        pass

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Disconnects from host.
    net_connect.disconnect()



def intersite(INPUT_DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Finds host ID.
    HOST_HOSTNAME = net_connect.find_prompt()[:-1]
    ID = ""
    for character in HOST_HOSTNAME:
        if character.isdigit():
            ID = ID + character
            ID = str(ID)
        else:
            pass

    # Finds hosts participating in intersite configuration AND in topology configuration.
    TRACK_HOSTS = []
    INTRASITE_HOSTS = []
    for element in INTRASITE[3]:
        INTRASITE_HOSTS = INTRASITE_HOSTS + element.split("-")[:-1]
    INTERSITE_HOSTS = []
    for element in INTERSITE[3:]:
        for item in element:
            INTERSITE_HOSTS.append(item.split("#")[0])
    for element in INTERSITE_HOSTS:
        if element in INTRASITE_HOSTS and element not in TRACK_HOSTS:
            TRACK_HOSTS.append(element)
        else:
            pass

    #Sends configuration.
    if str(ID) in TRACK_HOSTS:
        INTERFACE_STATIC_COMMANDS = []
        C1 = "interface " + INTERSITE[2].split("-")[0]
        C2 = "ip address " + INTERSITE[2].split("-")[1].split(".")[0] + "." + str(ID) + "." + str(ID) + "." + str(ID) + " 255.255.255.0"
        INTERFACE_STATIC_COMMANDS.append(C1)
        INTERFACE_STATIC_COMMANDS.append(C2)
        for element in INTERSITE[3:]:
            INTERSITE_LINK = []
            for item in element:
                X = item.split("#")[0]
                INTERSITE_LINK.append(X)
            INTERSITE_LINK = [int(i) for i in INTERSITE_LINK]
            MIN_ID = min(INTERSITE_LINK)
            MAX_ID = max(INTERSITE_LINK)
            if int(ID) in INTERSITE_LINK and len(INTERSITE_LINK) == 2:
                C3 = "interface " + TOPOLOGY_INTERFACE[0]
                C4 = "no shutdown"
                INTERFACE_STATIC_COMMANDS.append(C3)
                INTERFACE_STATIC_COMMANDS.append(C4)
                INTERSITE_LINK.remove(int(ID))
                if MAX_ID < 10:
                    C5 = "interface " + TOPOLOGY_INTERFACE[0] + "." + str(MAX_ID) + str(MIN_ID)
                    C6 = "encapsulation dot1Q " + str(MAX_ID) + str(MIN_ID)
                    C7 = "ip address " + INTERSITE[0].split(".")[0] + "." + str(100) + "." + str(MAX_ID) + str(MIN_ID) + "." + str(ID) + " 255.255.255.0"
                    C8 = "ip route " + INTERSITE[2].split("-")[1].split(".")[0] + "." + str(INTERSITE_LINK[0]) + "." + str(INTERSITE_LINK[0]) + "." + str(INTERSITE_LINK[0]) + " 255.255.255.255 " + INTERSITE[0].split(".")[0] + "." + str(100) + "." + str(MAX_ID) + str(MIN_ID) + "." + str(INTERSITE_LINK[0])
                    INTERFACE_STATIC_COMMANDS.append(C5)
                    INTERFACE_STATIC_COMMANDS.append(C6)
                    INTERFACE_STATIC_COMMANDS.append(C7)
                    INTERFACE_STATIC_COMMANDS.append(C8)
                elif MAX_ID >= 10 and MIN_ID < 10:
                    C5 = "interface " + TOPOLOGY_INTERFACE[0] + "." + "1" + str(MAX_ID)[1] + str(MIN_ID)
                    C6 = "encapsulation dot1Q " + "1" + str(MAX_ID)[1] + str(MIN_ID)
                    C7 = "ip address " + INTERSITE[0].split(".")[0] + "." + str(100) + "." + "1" + str(MAX_ID)[1] + str(MIN_ID) + "." + str(ID) + " 255.255.255.0"
                    C8 = "ip route " + INTERSITE[2].split("-")[1].split(".")[0] + "." + str(INTERSITE_LINK[0]) + "." + str(INTERSITE_LINK[0]) + "." + str(INTERSITE_LINK[0]) + " 255.255.255.255 " + INTERSITE[0].split(".")[0] + "." + str(100) + "." + "1" + str(MAX_ID)[1] + str(MIN_ID) + "." + str(INTERSITE_LINK[0])
                    INTERFACE_STATIC_COMMANDS.append(C5)
                    INTERFACE_STATIC_COMMANDS.append(C6)
                    INTERFACE_STATIC_COMMANDS.append(C7)
                    INTERFACE_STATIC_COMMANDS.append(C8)
                elif MIN_ID >= 10:
                    C5 = "interface " + TOPOLOGY_INTERFACE[0] + "." + "2" + str(MAX_ID)[1] + str(MIN_ID)[1]
                    C6 = "encapsulation dot1Q " + "2" + str(MAX_ID)[1] + str(MIN_ID)[1]
                    C7 = "ip address " + INTERSITE[0].split(".")[0] + "." + str(100) + "." + "2" + str(MAX_ID)[1] + str(MIN_ID)[1] + "." + str(ID) + " 255.255.255.0"
                    C8 = "ip route " + INTERSITE[2].split("-")[1].split(".")[0] + "." + str(INTERSITE_LINK[0]) + "." + str(INTERSITE_LINK[0]) + "." + str(INTERSITE_LINK[0]) + " 255.255.255.255 " + INTERSITE[0].split(".")[0] + "." + str(100) + "." + "2" + str(MAX_ID)[1] + str(MIN_ID)[1] + "." + str(INTERSITE_LINK[0])
                    INTERFACE_STATIC_COMMANDS.append(C5)
                    INTERFACE_STATIC_COMMANDS.append(C6)
                    INTERFACE_STATIC_COMMANDS.append(C7)
                    INTERFACE_STATIC_COMMANDS.append(C8)
                else:
                    pass
            elif int(ID) in INTERSITE_LINK and len(INTERSITE_LINK) != 2:
                C3 = "interface " + TOPOLOGY_INTERFACE[0]
                C4 = "no shutdown"
                INTERFACE_STATIC_COMMANDS.append(C3)
                INTERFACE_STATIC_COMMANDS.append(C4)
                INTERSITE_LINK.remove(int(ID))
                if MAX_ID < 10:
                    C5 = "interface " + TOPOLOGY_INTERFACE[0] + "." + "6" + str(MAX_ID) + str(MIN_ID)
                    C6 = "encapsulation dot1Q " + "6" + str(MAX_ID) + str(MIN_ID)
                    C7 = "ip address " + INTERSITE[1].split(".")[0] + "." + str(100) + "." + str(MAX_ID) + str(MIN_ID) + "." + str(ID) + " 255.255.255.0"
                    INTERFACE_STATIC_COMMANDS.append(C5)
                    INTERFACE_STATIC_COMMANDS.append(C6)
                    INTERFACE_STATIC_COMMANDS.append(C7)
                    for member in INTERSITE_LINK:
                        Cz = "ip route " + INTERSITE[2].split("-")[1].split(".")[0] + "." + str(member) + "." + str(member) + "." + str(member) + " 255.255.255.255 " + INTERSITE[1].split(".")[0] + "." + str(100) + "." + str(MAX_ID) + str(MIN_ID) + "." + str(member)
                        INTERFACE_STATIC_COMMANDS.append(Cz)
                elif MAX_ID >= 10 and MIN_ID < 10:
                    C5 = "interface " + TOPOLOGY_INTERFACE[0] + "." + "7" + str(MAX_ID)[1] + str(MIN_ID)
                    C6 = "encapsulation dot1Q " + "7" + str(MAX_ID)[1] + str(MIN_ID)
                    C7 = "ip address " + INTERSITE[1].split(".")[0] + "." + str(100) + "." + "1" + str(MAX_ID)[1] + str(MIN_ID) + "." + str(ID) + " 255.255.255.0"
                    INTERFACE_STATIC_COMMANDS.append(C5)
                    INTERFACE_STATIC_COMMANDS.append(C6)
                    INTERFACE_STATIC_COMMANDS.append(C7)
                    for member in INTERSITE_LINK:
                        Cz = "ip route " + INTERSITE[2].split("-")[1].split(".")[0] + "." + str(member) + "." + str(member) + "." + str(member) + " 255.255.255.255 " + INTERSITE[1].split(".")[0] + "." + str(100) + "." + "1" + str(MAX_ID)[1] + str(MIN_ID) + "." + str(member)
                        INTERFACE_STATIC_COMMANDS.append(Cz)
                elif MIN_ID >= 10:
                    C5 = "interface " + TOPOLOGY_INTERFACE[0] + "." + "8" + str(MAX_ID)[1] + str(MIN_ID)[1]
                    C6 = "encapsulation dot1Q " + "8" + str(MAX_ID)[1] + str(MIN_ID)[1]
                    C7 = "ip address " + INTERSITE[1].split(".")[0] + "." + str(100) + "." + "2" + str(MAX_ID)[1] + str(MIN_ID)[1] + "." + str(ID) + " 255.255.255.0"
                    INTERFACE_STATIC_COMMANDS.append(C5)
                    INTERFACE_STATIC_COMMANDS.append(C6)
                    INTERFACE_STATIC_COMMANDS.append(C7)
                    for member in INTERSITE_LINK:
                        Cz = "ip route " + INTERSITE[2].split("-")[1].split(".")[0] + "." + str(member) + "." + str(member) + "." + str(member) + " 255.255.255.255 " + INTERSITE[1].split(".")[0] + "." + str(100) + "." + "2" + str(MAX_ID)[1] + str(MIN_ID)[1] + "." + str(member)
                        INTERFACE_STATIC_COMMANDS.append(Cz)
                else:
                    pass
            else:
                pass
    else:
        pass

    # EBGP commands.
    if str(ID) in TRACK_HOSTS:
        EBGP_COMMANDS = []
        for element in INTERSITE[3:]:
            HOST_ASN = ""
            for item in element:
                if str(ID) == item.split("#")[0]:
                    HOST_ASN = item.split("#")[1]
                else:
                    pass
            if HOST_ASN == "":
                pass
            else:
                for item in element:
                    if str(ID) == item.split("#")[0]:
                        pass
                    else:
                        C1 = "router bgp " + HOST_ASN
                        C2 = "neighbor " + INTERSITE[2].split("-")[1].split(".")[0] + "." + item.split("#")[0] + "." + item.split("#")[0] + "." + item.split("#")[0] + " remote-as " + item.split("#")[1]
                        C3 = "neighbor " + INTERSITE[2].split("-")[1].split(".")[0] + "." + item.split("#")[0] + "." + item.split("#")[0] + "." + item.split("#")[0] + " update-source " + INTERSITE[2].split("-")[0]
                        C4 = "neighbor " + INTERSITE[2].split("-")[1].split(".")[0] + "." + item.split("#")[0] + "." + item.split("#")[0] + "." + item.split("#")[0] + " disable-connected-check"
                        C5 = "address-family ipv4"
                        C6 = "neighbor " + INTERSITE[2].split("-")[1].split(".")[0] + "." + item.split("#")[0] + "." + item.split("#")[0] + "." + item.split("#")[0] + " activate"
                        C7 = "exit-address-family"
                        EBGP_COMMANDS.append(C1)
                        EBGP_COMMANDS.append(C2)
                        EBGP_COMMANDS.append(C3)
                        EBGP_COMMANDS.append(C4)
                        EBGP_COMMANDS.append(C5)
                        EBGP_COMMANDS.append(C6)
                        EBGP_COMMANDS.append(C7)
    else:
        pass

    try:
        # Concatenate commands.
        COMMANDS = INTERFACE_STATIC_COMMANDS + EBGP_COMMANDS

        # Print configuration commands.
        print(COMMANDS)

        # Sends configuration commands.
        net_connect.send_config_set(COMMANDS)
    except:
        pass

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Disconnects from host.
    net_connect.disconnect()



# CODE!!!



# The asynchronous execution can be performed with threads (ThreadPoolExecutor), or processes (ProcessPoolExecutor).
# If the program spends more time waiting on network requests (or any type of I/O task) there is an I/O bottleneck and you should use ThreadPoolExecutor.
# If the program spends more time processing large datasets there is a CPU bottleneck and you should use ProcessPoolExecutor.
# ThreadPoolExecutor cannot be used for parallel CPU computations.
# ThreadPoolExecutor is perfect for scripts related to network/data I/O because the processor is sitting idle waiting for data.

try:
    LENGTH = len(INTRASITE)
    if LENGTH > 0:
        print("\033[1;91m")
        print()
        print()
        print()
        print("The INTRASITE configuration is the following:")
        print()
        print()
        print()
        print("\033[0m")
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            future = [executor.submit(intrasite, element) for element in HOSTS]
    else:
        pass
except:
    pass

try:
    if "RIP" in PROTOCOLS:
        print("\033[1;91m")
        print()
        print()
        print()
        print("The RIP configuration is the following:")
        print()
        print()
        print()
        print("\033[0m")
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            future = [executor.submit(rip, element) for element in HOSTS]
    else:
        pass
    if "EIGRP" in PROTOCOLS:
        print("\033[1;91m")
        print()
        print()
        print()
        print("The EIGRP configuration is the following:")
        print()
        print()
        print()
        print("\033[0m")
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            future = [executor.submit(eigrp, element) for element in HOSTS]
    else:
        pass
    if "OSPF" in PROTOCOLS:
        print("\033[1;91m")
        print()
        print()
        print()
        print("The OSPF configuration is the following:")
        print()
        print()
        print()
        print("\033[0m")
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            future = [executor.submit(ospf, element) for element in HOSTS]
    else:
        pass
    if "ISIS" in PROTOCOLS:
        print("\033[1;91m")
        print()
        print()
        print()
        print("The ISIS configuration is the following:")
        print()
        print()
        print()
        print("\033[0m")
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            future = [executor.submit(isis, element) for element in HOSTS]
    else:
        pass
    if "IBGP" in PROTOCOLS:
        print("\033[1;91m")
        print()
        print()
        print()
        print("The IBGP configuration is the following:")
        print()
        print()
        print()
        print("\033[0m")
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            future = [executor.submit(ibgp, element) for element in HOSTS]
    else:
        pass
    if "MPLS" in PROTOCOLS:
        print("\033[1;91m")
        print()
        print()
        print()
        print("The MPLS configuration is the following:")
        print()
        print()
        print()
        print("\033[0m")
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            future = [executor.submit(mpls, element) for element in HOSTS]
    else:
        pass
except:
    pass

try:
    LENGTH = len(INTERSITE)
    if LENGTH > 0:
        print("\033[1;91m")
        print()
        print()
        print()
        print("The INTERSITE configuration is the following:")
        print()
        print()
        print()
        print("\033[0m")
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            future = [executor.submit(intersite, element) for element in HOSTS]
    else:
        pass
except:
    pass

print("\033[1;91m")
print()
print()
print()
print("End of script!!!")
print()
print()
print()
print("\033[0m")
