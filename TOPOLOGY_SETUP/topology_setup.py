# This line imports the needed Functions from netmiko
from netmiko import ConnectHandler
# This line imports the os, sys, datetime, random, string, subprocess, concurrent.futures Modules
import os, sys, datetime, random, string, subprocess, concurrent.futures
# This line imports the variables file (it should be placed in the same directory with the python script)
from var_file import *


def interconnections():
    # A function to get interconnections (interface/network pairs) for the topology.

    print("\033[1;93m")
    print("This function assisting you to define the physical interface used to interconnect the devices and the network configured on this physical interface.")
    print("\033[0m")

    user_input = input("\033[1;93m Enter the physical interface and network used to interconnect the devices (eg 'Ethernet0/1,11.0.0.0/8', respect the format (only /8 are valid inputs)) \n: \033[0m")
    INTERCONNECTIONS_LIST_STRING.append(user_input)

    for element in INTERCONNECTIONS_LIST_STRING:
        x1 = element.split(',')[0]
        x2 = element.split(',')[1]
        x = [x1, x2]
        INTERCONNECTIONS_LIST_LIST.append(x)


def loopbacks():
    # A function to get loopbacks (interface/network pairs) for the topology.

    print("\033[1;93m")
    print("This loop assisting you to define the loopback interfaces on the devices and the network configured on these loopback interfaces.")
    print("To quit this loop enter 'EXIT' (case sensitive)!")
    print("\033[0m")

    track_input = 0

    while track_input == 0:
        user_input = input("\033[1;93m Enter the loopback interface and network used on this (eg 'Loopback0,12.0.0.0/8', respect the format (only /8 are valid inputs)) \n: \033[0m")
        if user_input == "EXIT":
            track_input = 1
            print("\033[1;93m Exit the loopbacks loop! \033[0m")
        else:
            LOOPBACKS_LIST_STRING.append(user_input)

    for element in LOOPBACKS_LIST_STRING:
        x1 = element.split(',')[0]
        x2 = element.split(',')[1]
        x = [x1, x2]
        LOOPBACKS_LIST_LIST.append(x)


def segments():
    # A function to get the devices per segment in the topology.

    print("\033[1;93m")
    print("This loop assisting you to define the devices per segment in the topology.")
    print("The IDs (a single digit, for Rn is n) of the devices are used for the addressing scheme (eg (NET).(MIN_ID).(MAX_ID).(ID)).")
    print("You can define segments with more than two devices!")
    print("For segments with more than two devices the addressing scheme is (NET).(10 + MIN_ID).(10 + MAX_ID).(ID).")
    print("You CANNOT define two segments (each one with two devices) having the same MIN_ID and MAX_ID.")
    print("You CANNOT define two segments (each one with MORE THAN two devices) having the same MIN_ID and MAX_ID.")
    print("To quit this loop enter 'EXIT' (case sensitive)!")
    print("\033[0m")

    track_input = 0

    while track_input == 0:
        user_input = input("\033[1;93m Enter the IDs of the devices on a given segmant (eg '1,2' or '1,2,3,4', respect the format) and press 'ENTER' \n: \033[0m")
        if user_input == "EXIT":
            track_input = 1
            print("\033[1;93m Exit the segments loop! \033[0m")
        else:
            SEGMENTS_LIST_STRING.append(user_input)

    for element in SEGMENTS_LIST_STRING:
        x = element.split(',')
        SEGMENTS_LIST_LIST.append(x)



def setup(INPUT_DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Sends execution commands.
    net_connect.send_command("show startup-config")
    exec_output = net_connect.send_command("show startup-config")

    # Creates a temporary file (if the specified file does not exist) and overwrites any existing content (if there is).
    random_string = ''.join(random.choices(string.ascii_letters, k=10))
    with open("startup_config_temporary" + random_string, "w") as f:
        # Print the output of execution commands sent to host via Telnet/SSH.
        print(exec_output, file=f)

    # Finds host ID.
    with open("startup_config_temporary" + random_string, "r") as f:
        for line in f:
            if line.startswith("hostname"):
                host_hostname = line.strip("hostname")
                host_hostname = host_hostname.lstrip()
                host_hostname = host_hostname.rstrip("\n")
                ID = ""
                for c in host_hostname:
                    if c.isdigit():
                        ID = ID + c

    # Deletes the temporary file.
    if os.path.exists("startup_config_temporary" + random_string):
        os.remove("startup_config_temporary" + random_string)

    #Sends configuration.
    COMMANDS = []
    for element_1 in SEGMENTS_LIST_LIST:
        element_1 = [int(i) for i in element_1]
        min_id = min(element_1)
        max_id = max(element_1)
        if int(ID) in element_1 and len(element_1) == 2:
            C1 = "interface " + INTERCONNECTIONS_LIST_LIST[0][0]
            C2 = "no shutdown"
            C3 = "interface " + INTERCONNECTIONS_LIST_LIST[0][0] + "." + str(min_id) + str(max_id)
            C4 = "encapsulation dot1Q " + str(min_id) + str(max_id)
            C5 = "ip address " + INTERCONNECTIONS_LIST_LIST[0][1].split('.')[0] + "." + str(min_id) + "." + str(max_id) + "." + str(ID) + " 255.255.255.0"
            COMMANDS.append(C1)
            COMMANDS.append(C2)
            COMMANDS.append(C3)
            COMMANDS.append(C4)
            COMMANDS.append(C5)
        elif int(ID) in element_1 and len(element_1) != 2:
            C1 = "interface " + INTERCONNECTIONS_LIST_LIST[0][0]
            C2 = "no shutdown"
            C3 = "interface " + INTERCONNECTIONS_LIST_LIST[0][0] + "." + str(min_id) + str(max_id)
            C4 = "encapsulation dot1Q " + str(min_id) + str(max_id)
            C5 = "ip address " + INTERCONNECTIONS_LIST_LIST[0][1].split('.')[0] + "." + str(10 + min_id) + "." + str(10 + max_id) + "." + str(ID) + " 255.255.255.0"
            COMMANDS.append(C1)
            COMMANDS.append(C2)
            COMMANDS.append(C3)
            COMMANDS.append(C4)
            COMMANDS.append(C5)
        else:
            pass
    for element_3 in LOOPBACKS_LIST_LIST:
        C6 = "interface " + element_3[0]
        C7 = "ip address " + element_3[1].split('.')[0] + "." + str(ID) + "." + str(ID) + "." + str(ID) + " 255.255.255.0"
        COMMANDS.append(C6)
        COMMANDS.append(C7)

    print(COMMANDS)

    # Sends configuration commands.
    net_connect.send_config_set(COMMANDS)

    # Saves the running-config to the startup-config.
    net_connect.save_config()


# CODE!!!
interconnections()
loopbacks()
segments()


# The asynchronous execution can be performed with threads (ThreadPoolExecutor), or processes (ProcessPoolExecutor).
# If the program spends more time waiting on network requests (or any type of I/O task) there is an I/O bottleneck and you should use ThreadPoolExecutor.
# If the program spends more time processing large datasets there is a CPU bottleneck and you should use ProcessPoolExecutor.
# ThreadPoolExecutor cannot be used for parallel CPU computations.
# ThreadPoolExecutor is perfect for scripts related to network/data I/O because the processor is sitting idle waiting for data.
with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
    future = [executor.submit(setup, element) for element in HOSTS_LIST]
