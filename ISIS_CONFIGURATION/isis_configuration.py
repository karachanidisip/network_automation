# This line imports the needed Classes from jinja2
from jinja2 import FileSystemLoader, Environment
# This line imports the needed Functions from netmiko
from netmiko import ConnectHandler
# This line imports the os, sys, datetime, random, string, subprocess, concurrent.futures, ipaddress Modules
import os, sys, datetime, random, string, subprocess, concurrent.futures, ipaddress
# This line imports the variables file (it should be placed in the same directory with the python script)
from var_file import *


def targets():
    # A function to get LISTS with ipv4 management addresses of DEVICES per ISIS LEVEL.

    print("\033[1;93m")
    print("These loops assisting you to define the devices (ipv4 management addresses, eg 10.0.0.1) for ISIS configuration!")
    print("To quit each loop enter 'EXIT' (case sensitive) and press ENTER!")
    print("\033[0m")

    track_input = 1

    while track_input == 1:
        user_input = input("\033[1;93m Enter the ipv4 address (management address) of the L1_ONLY devices and press ENTER \n: \033[0m")
        if user_input == "EXIT":
            track_input = 2
            print("\033[1;93m Exit the L1_ONLY devices loop! \033[0m")
        else:
            L1_ONLY_TARGETS_LIST.append(user_input)

    while track_input == 2:
        user_input = input("\033[1;93m Enter the ipv4 address (management address) of the L2_ONLY devices and press ENTER \n: \033[0m")
        if user_input == "EXIT":
            track_input = 12
            print("\033[1;93m Exit the L2_ONLY devices loop! \033[0m")
        else:
            L2_ONLY_TARGETS_LIST.append(user_input)

    while track_input == 12:
        user_input = input("\033[1;93m Enter the ipv4 address (management address) of the L1L2 devices and press ENTER \n: \033[0m")
        if user_input == "EXIT":
            track_input = 0
            print("\033[1;93m Exit the L1L2 devices loop! \033[0m")
        else:
            L1L2_TARGETS_LIST.append(user_input)

    print("\033[1;92m")
    print("The devices are in the following LISTS per LEVEL!")
    print("L1_ONLY devices!")
    print(L1_ONLY_TARGETS_LIST)
    print("L2_ONLY devices!")
    print(L2_ONLY_TARGETS_LIST)
    print("L1L2 devices!")
    print(L1L2_TARGETS_LIST)
    print("\033[0m")


def hosts(LIST_1, LIST_2, LIST_3):
    # A function to get LISTS with dictionaries of DEVICES per ISIS LEVEL.

    for element_1 in LIST_1:
        for element_2 in HOSTS_LIST:
            if ("host", element_1) in element_2.items():
                L1_ONLY_HOSTS_LIST.append(element_2)

    for element_3 in LIST_2:
        for element_4 in HOSTS_LIST:
            if ("host", element_3) in element_4.items():
                L2_ONLY_HOSTS_LIST.append(element_4)

    for element_5 in LIST_3:
        for element_6 in HOSTS_LIST:
            if ("host", element_5) in element_6.items():
                L1L2_HOSTS_LIST.append(element_6)

    print("\033[1;92m")
    print("The L1_ONLY hosts information are in the following LIST")
    print(L1_ONLY_HOSTS_LIST)
    print("The L2_ONLY hosts information are in the following LIST")
    print(L2_ONLY_HOSTS_LIST)
    print("The L1L2 hosts information are in the following LIST")
    print(L1L2_HOSTS_LIST)
    print("\033[0m")


def target_area_pairs():
    # A function to get LIST with pairs of ipv4 management address and 4-digits area.

    print("\033[1;93m")
    print("This loop assisting you to define the pairs of target (ipv4 management address) and 4-digits area for ISIS configuration (eg 10.0.0.1/0034)!")
    print("To quit the loop enter 'EXIT' (case sensitive) and press ENTER!")
    print("\033[0m")

    track_input = 1

    while track_input == 1:
        user_input = input("\033[1;93m Enter a pair of target (ipv4 management addresses) and 4-digits area for ISIS configuration (eg 10.0.0.1/0034) and press ENTER \n: \033[0m")
        if user_input == "EXIT":
            track_input = 2
            print("\033[1;93m Exit the L1_ONLY targets loop! \033[0m")
        else:
            TARGET_AREA_PAIRS_LIST.append(user_input)

    print("\033[1;92m")
    print("The pairs of target (ipv4 management address) and 4-digits area for ISIS configuration are in the following LIST")
    print(TARGET_AREA_PAIRS_LIST)
    print("\033[0m")


def isis_networks():
    # A function to get LISTS with networks per ISIS LEVEL.

    print("\033[1;93m")
    print("These loops assisting you to define the ISIS enabled networks (eg 10.0.3.4/23) per LEVEL!")
    print("To quit each loop enter 'EXIT' (case sensitive) and press ENTER!")
    print("\033[0m")

    track_input = 1

    while track_input == 1:
        user_input = input("\033[1;93m Enter the ISIS enabled networks for L1 (eg 10.0.3.4/23) and press ENTER \n: \033[0m")
        if user_input == "EXIT":
            track_input = 2
            print("\033[1;93m Exit the loop for L1 ISIS enabled networks! \033[0m")
        else:
            L1_NETWORKS_LIST.append(user_input)

    while track_input == 2:
        user_input = input("\033[1;93m Enter the ISIS enabled networks for L2 (eg 10.0.3.4/23) and press ENTER \n: \033[0m")
        if user_input == "EXIT":
            track_input = 12
            print("\033[1;93m Exit the loop for L2 ISIS enabled networks! \033[0m")
        else:
            L2_NETWORKS_LIST.append(user_input)

    while track_input == 12:
        user_input = input("\033[1;93m Enter the ISIS enabled networks for L1L2 (eg 10.0.3.4/23) and press ENTER \n: \033[0m")
        if user_input == "EXIT":
            track_input = 0
            print("\033[1;93m Exit the loop for L1L2 ISIS enabled networks! \033[0m")
        else:
            L1L2_NETWORKS_LIST.append(user_input)

    print("\033[1;92m")
    print("The ISIS enabled networks are in the following LISTS")
    print("L1 ISIS enabled networks!")
    print(L1_NETWORKS_LIST)
    print("L2 ISIS enabled networks!")
    print(L2_NETWORKS_LIST)
    print("L1L2 ISIS enabled networks!")
    print(L1L2_NETWORKS_LIST)
    print("\033[0m")


def isis_config(DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**DICT_PER_HOST)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Sends execution commands.
    net_connect.send_command("show startup-config")
    exec_output_1 = net_connect.send_command("show startup-config")

    # Creates a temporary file (if the specified file does not exist) and overwrites any existing content (if there is).
    random_string_1 = ''.join(random.choices(string.ascii_letters, k=10))
    with open("startup_config_temporary" + random_string_1, "w") as f:
        # Print the output of execution commands sent to host via Telnet/SSH.
        print(exec_output_1, file=f)

    # Finds host hostname.
    with open("startup_config_temporary" + random_string_1, "r") as f:
        for line in f:
            if line.startswith("hostname"):
                host_hostname = line.strip("hostname")
                host_hostname = host_hostname.lstrip()
                host_hostname = host_hostname.rstrip("\n")

    # Finds host host_id.
    host_id = ""
    for char in host_hostname:
        if char.isdigit():
            host_id = host_id + char
    host_id = host_id.zfill(4)

    # Deletes the temporary file.
    if os.path.exists("startup_config_temporary" + random_string_1):
        os.remove("startup_config_temporary" + random_string_1)

    # Finds host AREA.
    mgmnt_address = DICT_PER_HOST["host"]
    for element in TARGET_AREA_PAIRS_LIST:
        address_area = element.partition('/')
        address = address_area[0]
        area = address_area[2]
        if address == mgmnt_address:
            host_area = area

    # Finds host LEVEL.
    mgmnt_address = DICT_PER_HOST["host"]
    if mgmnt_address in L1_ONLY_TARGETS_LIST:
        host_level = "level-1"
    elif mgmnt_address in L2_ONLY_TARGETS_LIST:
        host_level = "level-2-only"
    elif mgmnt_address in L1L2_TARGETS_LIST:
        host_level = "level-1-2"
    else:
        pass

    # This line defines as working directory the directory of the script (all files should be placed in this directory). Used from jinja2.
    file_loader = FileSystemLoader(os.path.dirname(sys.argv[0]))

    # Load the enviroment. Used from jinja2.
    env = Environment(loader=file_loader)

    # Add the template.
    template_task = env.get_template("template_isis_process.j2")

    # Render the template.
    output_task = template_task.render(VAR_1=host_area, VAR_2=host_id, VAR_3=host_level)
    print("\033[1;92m")
    print("The ISIS process configuration for the " + str(host_hostname) + " host is as following!!!")
    print(output_task)
    print("\033[0m")

    # Creates a temporary file (if the specified file does not exist) and overwrites any existing content (if there is).
    random_string_2 = ''.join(random.choices(string.ascii_letters, k=10))
    with open("config_file_temporary" + random_string_2, "w") as f:
        # Print the output of execution commands sent to device via Telnet/SSH.
        print(output_task, file=f)

    # Sends execution commands.
    net_connect.send_config_from_file("config_file_temporary" + random_string_2)

    # Deletes the temporary file.
    if os.path.exists("config_file_temporary" + random_string_2):
        os.remove("config_file_temporary" + random_string_2)

    # Sends execution commands.
    net_connect.send_command("show ip interface | include Internet address | line protocol")
    exec_output_3 = net_connect.send_command("show ip interface | include Internet address | line protocol")

    # Creates a temporary file (if the specified file does not exist) and overwrites any existing content (if there is).
    random_string_3 = ''.join(random.choices(string.ascii_letters, k=10))
    with open("interfaces_temporary" + random_string_3, "w") as f:
        # Print the output of execution commands sent to host via Telnet/SSH.
        print(exec_output_3, file=f)

    # List with lists of interface and address pairs.
    INTERFACE_ADDRESS_PAIRS_LIST = []

    # Finds interfaces addresses.
    with open("interfaces_temporary" + random_string_3, "r") as f:
        previous_line = ""
        for line in f:
            if "Internet address" in line:
                INTERFACE_ADDRESS_PAIRS_LIST.append([previous_line.split()[0], line.split()[3]])
            previous_line = line

    # List with lists of interface and network pairs.
    INTERFACE_NETWORK_PAIRS_LIST = []

    # Finds interfaces networks.
    for element in INTERFACE_ADDRESS_PAIRS_LIST:
        a = element[0]
        b = ipaddress.ip_network(element[1], strict=False).with_prefixlen
        INTERFACE_NETWORK_PAIRS_LIST.append([a, b])

    # Deletes the temporary file.
    if os.path.exists("interfaces_temporary" + random_string_3):
        os.remove("interfaces_temporary" + random_string_3)

    # List with configuration commands for interfaces of ISIS.
    CONFIG_ISIS_INTERFACES_LIST = []

    # Add the ISIS interface configuration commands in a LIST.
    for element in INTERFACE_NETWORK_PAIRS_LIST:
        if element[1] in L1_NETWORKS_LIST:
            CONFIG_ISIS_INTERFACES_LIST.append("interface " + str(element[0]))
            CONFIG_ISIS_INTERFACES_LIST.append("ip router isis")
            CONFIG_ISIS_INTERFACES_LIST.append("isis circuit-type level-1")
        elif element[1] in L2_NETWORKS_LIST:
            CONFIG_ISIS_INTERFACES_LIST.append("interface " + str(element[0]))
            CONFIG_ISIS_INTERFACES_LIST.append("ip router isis")
            CONFIG_ISIS_INTERFACES_LIST.append("isis circuit-type level-2-only")
        elif element[1] in L1L2_NETWORKS_LIST:
            CONFIG_ISIS_INTERFACES_LIST.append("interface " + str(element[0]))
            CONFIG_ISIS_INTERFACES_LIST.append("ip router isis")
            CONFIG_ISIS_INTERFACES_LIST.append("isis circuit-type level-1-2")

    print("\033[1;92m")
    print("The ISIS interface configuration commands for the " + str(host_hostname) + " host are in the following LIST!!!")
    print(CONFIG_ISIS_INTERFACES_LIST)
    print("\033[0m")


    # Sends execution commands.
    net_connect.send_config_set(CONFIG_ISIS_INTERFACES_LIST)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Closes the connection.
    net_connect.disconnect()

    print("\033[1;91m")
    print("There is a new ISIS configuration for the " + host_hostname + " device!!!")
    print("\033[0m")

# CODE!!!
targets()
hosts(L1_ONLY_TARGETS_LIST, L2_ONLY_TARGETS_LIST, L1L2_TARGETS_LIST)
target_area_pairs()
isis_networks()

ALL_ISIS_HOSTS_LIST = L1_ONLY_HOSTS_LIST + L2_ONLY_HOSTS_LIST + L1L2_HOSTS_LIST

# The asynchronous execution can be performed with threads (ThreadPoolExecutor), or processes (ProcessPoolExecutor).
# If the program spends more time waiting on network requests (or any type of I/O task) there is an I/O bottleneck and you should use ThreadPoolExecutor.
# If the program spends more time processing large datasets there is a CPU bottleneck and you should use ProcessPoolExecutor.
# ThreadPoolExecutor cannot be used for parallel CPU computations.
# ThreadPoolExecutor is perfect for scripts related to network/data I/O because the processor is sitting idle waiting for data.
with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
    future = [executor.submit(isis_config, element) for element in ALL_ISIS_HOSTS_LIST]
