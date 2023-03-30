# This line imports the needed Functions from netmiko
from netmiko import ConnectHandler
# This line imports the os, sys, datetime, random, string, subprocess, concurrent.futures Modules
import os, sys, datetime, random, string, subprocess, concurrent.futures
# This line imports the ipaddress Modules
import ipaddress
# This line imports the variables file (it should be placed in the same directory with the python script)
from var_file import *


class Address():
    def __init__(self, address):
    # Accepts either ipv4_short_form or ipv4_long_form or ipv4_wilcard_form
        self.address = address
    def extrack_network_short_form(self):
        VAR = self.address
        ipv4_network_short_form = ipaddress.ip_network(VAR, strict=False).with_prefixlen
        return ipv4_network_short_form
    def extrack_network_long_form(self):
        VAR = self.address
        ipv4_network_long_form = ipaddress.ip_network(VAR, strict=False).with_netmask
        return ipv4_network_long_form
    def extrack_network_wildcard_form(self):
        VAR = self.address
        ipv4_network_wildcard_form = ipaddress.ip_network(VAR, strict=False).with_hostmask
        return ipv4_network_wildcard_form
    def extrack_mask_short_form(self):
        VAR = self.address
        ipv4_mask_short_form = ipaddress.ip_network(VAR, strict=False).prefixlen
        return ipv4_mask_short_form
    def extrack_mask_long_form(self):
        VAR = self.address
        ipv4_mask_long_form = ipaddress.ip_network(VAR, strict=False).netmask
        return ipv4_mask_long_form
    def extrack_mask_wildcard_form(self):
        VAR = self.address
        ipv4_mask_wildcard_form = ipaddress.ip_network(VAR, strict=False).hostmask
        return ipv4_mask_wildcard_form


class CompareAddresses():
    def __init__(self, address_1, address_2):
    # Accepts either ipv4_short_form or ipv4_long_form or ipv4_wilcard_form
        self.address_1 = address_1
        self.address_2 = address_2
    def check_for_subnet(self):
        VAR_1 = self.address_1
        VAR_2 = self.address_2
        a = ipaddress.ip_network(VAR_1, strict=False)
        b = ipaddress.ip_network(VAR_2, strict=False)
        output = b.subnet_of(a)
        return output
    def check_for_supernet(self):
        VAR_1 = self.address_1
        VAR_2 = self.address_2
        a = ipaddress.ip_network(VAR_1, strict=False)
        b = ipaddress.ip_network(VAR_2, strict=False)
        output = b.supernet_of(a)
        return output


def isis_areas():
    # A function to get areas for isis.

    print("\033[1;93m")
    print("This function assisting you to define areas for isis.")
    print("To quit this loop enter 'EXIT' (case sensitive)!")
    print("\033[0m")

    TRACK_INPUT = 0

    while TRACK_INPUT == 0:
        USER_INPUT = input("\033[1;93m Enter an area for isis (NO more than 4 digits length) and the IDs of the devices (ID(Rn) = n) in this area (eg '12,1,2,3', RESPECT THE FORMAT (AREA,ID_1,ID_2,...)), then press 'ENTER' \n: \033[0m")
        if USER_INPUT == "EXIT" and len(ISIS_AREAS_LIST) >= 1:
            TRACK_INPUT = 1
            print("\033[1;93m Exit the areas for isis loop. \033[0m")
        elif USER_INPUT == "EXIT" and len(ISIS_AREAS_LIST) == 0:
            print("\033[1;93m You have not provided any areas for isis. \033[0m")
        else:
            ISIS_AREAS_LIST.append(USER_INPUT.split(','))


def isis_levels():
    # A function to get levels for isis.

    print("\033[1;93m")
    print("This function assisting you to define levels for isis.")
    print("To quit this loop enter 'EXIT' (case sensitive)!")
    print("\033[0m")

    TRACK_INPUT = 0

    while TRACK_INPUT == 0:
        USER_INPUT = input("\033[1;93m Enter the level for isis (EITHER level-1 OR level-1-2 OR level-2-only) and the IDs of the devices (ID(Rn) = n) in this level (eg 'level-1,1,2,3', RESPECT THE FORMAT (LEVEL,ID_1,ID_2,...)), then press 'ENTER' \n: \033[0m")
        if USER_INPUT == "EXIT" and len(ISIS_LEVELS_LIST) >= 1:
            TRACK_INPUT = 1
            print("\033[1;93m Exit the levels for isis loop. \033[0m")
        elif USER_INPUT == "EXIT" and len(ISIS_LEVELS_LIST) == 0:
            print("\033[1;93m You have not provided any levels for isis. \033[0m")
        else:
            ISIS_LEVELS_LIST.append(USER_INPUT.split(','))


def isis_networks():
    # A function to get networks for isis.

    print("\033[1;93m")
    print("This function assisting you to define networks for isis.")
    print("To quit this loop enter 'EXIT' (case sensitive)!")
    print("\033[0m")

    TRACK_INPUT = 0

    while TRACK_INPUT == 0:
        USER_INPUT = input("\033[1;93m Enter the level for isis (EITHER level-1 OR level-1-2 OR level-2-only) and the networks enabled for this level (eg 'level-1,11.1.3.0/24,11.3.4.0/24', RESPECT THE FORMAT (LEVEL,NETWORK_1,NETWORK_2,...)), then press 'ENTER' \n: \033[0m")
        if USER_INPUT == "EXIT" and len(ISIS_NETWORKS_LIST) >= 1:
            TRACK_INPUT = 1
            print("\033[1;93m Exit the networks for isis loop. \033[0m")
        elif USER_INPUT == "EXIT" and len(ISIS_NETWORKS_LIST) == 0:
            print("\033[1;93m You have not provided any networks for isis. \033[0m")
        else:
            ISIS_NETWORKS_LIST.append(USER_INPUT.split(','))


def setup(INPUT_DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Sends execution commands.
    net_connect.send_command("show ip interface | include Internet address | line protocolf")
    exec_output = net_connect.send_command("show ip interface | include Internet address | line protocol")

    # Creates a temporary file (if the specified file does not exist) and overwrites any existing content (if there is).
    random_string = ''.join(random.choices(string.ascii_letters, k=10))
    with open("interfaces_temporary" + random_string, "w") as f:
        # Print the output of execution commands sent to host via Telnet/SSH.
        print(exec_output, file=f)

    # Finds interfaces addresses.
    INTERFACE_ADDRESS_PAIRS_LIST = []
    with open("interfaces_temporary" + random_string, "r") as f:
        previous_line = ""
        for line in f:
            if "Internet address" in line:
                INTERFACE_ADDRESS_PAIRS_LIST.append([previous_line.split()[0], line.split()[3]])
            previous_line = line

    # Deletes the temporary file.
    if os.path.exists("interfaces_temporary" + random_string):
        os.remove("interfaces_temporary" + random_string)

    # Sends execution commands.
    net_connect.send_command("show startup-config")
    exec_output = net_connect.send_command("show startup-config")

    # Creates a temporary file (if the specified file does not exist) and overwrites any existing content (if there is).
    random_string = ''.join(random.choices(string.ascii_letters, k=10))
    with open("startup_config_temporary" + random_string, "w") as f:
        # Print the output of execution commands sent to host via Telnet/SSH.
        print(exec_output, file=f)

    # Finds host ID.
    HOST_HOSTNAME = ""
    ID = ""
    with open("startup_config_temporary" + random_string, "r") as f:
        for line in f:
            if line.startswith("hostname"):
                HOST_HOSTNAME = line.strip("hostname")
                HOST_HOSTNAME = HOST_HOSTNAME.lstrip()
                HOST_HOSTNAME = HOST_HOSTNAME.rstrip("\n")
                for character in HOST_HOSTNAME:
                    if character.isdigit():
                        ID = ID + character

    # Deletes the temporary file.
    if os.path.exists("startup_config_temporary" + random_string):
        os.remove("startup_config_temporary" + random_string)

    # ISIS commands.
    ISIS_COMMANDS = []
    C1 = "router isis"
    ISIS_COMMANDS.append(C1)
    for element_1 in ISIS_AREAS_LIST:
        for element_2 in element_1[1:]:
            if element_2 == ID:
                ID_4_DIGIT = ID.zfill(4)
                AREA = element_1[0]
                AREA = AREA.zfill(4)
                Cn = "49." + AREA + ".0000.0000." + ID_4_DIGIT + ".00"
                ISIS_COMMANDS.append(Cn)
            else:
                pass
    for element_1 in ISIS_LEVELS_LIST:
        for element_2 in element_1[1:]:
            if element_2 == ID:
                LEVEL = element_1[0]
                Cn = "is-type " + LEVEL
                ISIS_COMMANDS.append(Cn)
            else:
                pass
    for element_1 in ISIS_NETWORKS_LIST:
        for element_2 in element_1[1:]:
            for element_3 in INTERFACE_ADDRESS_PAIRS_LIST:
                if CompareAddresses(element_2, element_3[1]).check_for_subnet():
                    Cn1 = "interface " + element_3[0]
                    Cn2 = "ip router isis"
                    Cn3 = "isis circuit-type " + element_1[0]
                    ISIS_COMMANDS.append(Cn1)
                    ISIS_COMMANDS.append(Cn2)
                    ISIS_COMMANDS.append(Cn3)
                else:
                    pass

    # Print configuration commands.
    print(ISIS_COMMANDS)

    # Sends configuration commands.
    net_connect.send_config_set(ISIS_COMMANDS)

    # Saves the running-config to the startup-config.
    net_connect.save_config()


# CODE!!!
isis_areas()
isis_levels()
isis_networks()


# The asynchronous execution can be performed with threads (ThreadPoolExecutor), or processes (ProcessPoolExecutor).
# If the program spends more time waiting on network requests (or any type of I/O task) there is an I/O bottleneck and you should use ThreadPoolExecutor.
# If the program spends more time processing large datasets there is a CPU bottleneck and you should use ProcessPoolExecutor.
# ThreadPoolExecutor cannot be used for parallel CPU computations.
# ThreadPoolExecutor is perfect for scripts related to network/data I/O because the processor is sitting idle waiting for data.
with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
    future = [executor.submit(setup, element) for element in HOSTS_LIST]
