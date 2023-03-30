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


def ospf_process():
    # A function to get process number for ospf.

    print("\033[1;93m")
    print("This function assisting you to define the process number for ospf.")
    print("\033[0m")

    X = []
    USER_INPUT = input("\033[1;93m Enter the process number for ospf (eg '101', RESPECT THE FORMAT), then press 'ENTER' \n: \033[0m")
    X.append(USER_INPUT)
    OSPF_LIST.append(X)


def ospf_areas_and_networks():
    # A function to get areas and networks (for these areas) enabled for ospf.

    print("\033[1;93m")
    print("This function assisting you to define areas and networks (for these areas) enabled for ospf.")
    print("To quit this loop enter 'EXIT' (case sensitive)!")
    print("\033[0m")

    TRACK_INPUT = 0

    while TRACK_INPUT == 0:
        USER_INPUT = input("\033[1;93m Enter an area number and the networks for this area enabled for ospf (eg '0,11.1.3.0/24,11.3.4.0/24', RESPECT THE FORMAT), then press 'ENTER' \n: \033[0m")
        if USER_INPUT == "EXIT" and len(OSPF_LIST) >= 2:
            TRACK_INPUT = 1
            print("\033[1;93m Exit the ospf areas and networks loop. \033[0m")
        elif USER_INPUT == "EXIT" and len(OSPF_LIST) == 1:
            print("\033[1;93m You have not provided any area number (and the networks for this area) enabled for ospf. \033[0m")
        else:
            OSPF_LIST.append(USER_INPUT.split(','))


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

    # OSPF commands.
    OSPF_COMMANDS = []
    C1 = "router ospf " + OSPF_LIST[0][0]
    OSPF_COMMANDS.append(C1)
    for element_1 in OSPF_LIST[1:]:
        for element_2 in element_1[1:]:
            for element_3 in INTERFACE_ADDRESS_PAIRS_LIST:
                if CompareAddresses(element_2, element_3[1]).check_for_subnet():
                    Cn = "network " + element_2.split("/")[0] + " " + str(Address(element_2).extrack_mask_wildcard_form()) + " area " + element_1[0]
                    OSPF_COMMANDS.append(Cn)
                else:
                    pass

    # Remove duplicates.
    EMPTY_LIST = []
    for element in OSPF_COMMANDS:
        if element not in EMPTY_LIST:
            EMPTY_LIST.append(element)
    OSPF_COMMANDS = EMPTY_LIST

    # Check if there is any network configuration.
    if len(OSPF_COMMANDS) == 1:
        OSPF_COMMANDS = []
    else:
        pass

    # Print configuration commands.
    print(OSPF_COMMANDS)

    # Sends configuration commands.
    net_connect.send_config_set(OSPF_COMMANDS)

    # Saves the running-config to the startup-config.
    net_connect.save_config()


# CODE!!!
ospf_process()
ospf_areas_and_networks()


# The asynchronous execution can be performed with threads (ThreadPoolExecutor), or processes (ProcessPoolExecutor).
# If the program spends more time waiting on network requests (or any type of I/O task) there is an I/O bottleneck and you should use ThreadPoolExecutor.
# If the program spends more time processing large datasets there is a CPU bottleneck and you should use ProcessPoolExecutor.
# ThreadPoolExecutor cannot be used for parallel CPU computations.
# ThreadPoolExecutor is perfect for scripts related to network/data I/O because the processor is sitting idle waiting for data.
with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
    future = [executor.submit(setup, element) for element in HOSTS_LIST]
