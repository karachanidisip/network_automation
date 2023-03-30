# This line imports the needed Functions from netmiko
from netmiko import ConnectHandler
# This line imports the os, sys, datetime, random, string, subprocess, concurrent.futures Modules
import os, sys, datetime, random, string, subprocess, concurrent.futures
# This line imports the ipaddress Modules
import ipaddress
# This line imports the variables file (it should be placed in the same directory with the python script)
from var_file import *


def interconnections():
    # A function to get interconnections (physical interface and network configured on this) for the topology.

    print("\033[1;93m")
    print("This function assisting you to define the physical interface used to interconnect the devices and the network configured on this physical interface.")
    print("\033[0m")

    USER_INPUT = input("\033[1;93m Enter the physical interface used to interconnect the devices and the network configured on this physical interface (eg 'Ethernet0/1,11.0.0.0/8', RESPECT THE FORMAT, (only /8 are valid inputs)), then press 'ENTER' \n: \033[0m")
    INTERCONNECTIONS_LIST_STRING.append(USER_INPUT)

    for element in INTERCONNECTIONS_LIST_STRING:
        X1 = element.split(',')[0]
        X2 = element.split(',')[1]
        X = [X1, X2]
        INTERCONNECTIONS_LIST_LIST.append(X)


def loopbacks():
    # A function to get loopbacks (interface and network configured on this) for the topology.

    print("\033[1;93m")
    print("This loop assisting you to define the loopback interfaces on the devices and the network configured on these loopback interfaces.")
    print("To quit this loop enter 'EXIT' (case sensitive)!")
    print("\033[0m")

    TRACK_INPUT = 0

    while TRACK_INPUT == 0:
        USER_INPUT = input("\033[1;93m Enter the loopback interface and network configured on this (eg 'Loopback0,12.0.0.0/8', RESPECT THE FORMAT, (only /8 are valid inputs)), then press 'ENTER' \n: \033[0m")
        if USER_INPUT == "EXIT" and LOOPBACKS_LIST_STRING != []:
            TRACK_INPUT = 1
            print("\033[1;93m Exit the loopbacks loop. \033[0m")
        elif USER_INPUT == "EXIT" and LOOPBACKS_LIST_STRING == []:
            print("\033[1;93m You have not provided any input. \033[0m")
        else:
            LOOPBACKS_LIST_STRING.append(USER_INPUT)

    for element in LOOPBACKS_LIST_STRING:
        X1 = element.split(',')[0]
        X2 = element.split(',')[1]
        X = [X1, X2]
        LOOPBACKS_LIST_LIST.append(X)


def segments():
    # A function to get the devices per segment in the topology.

    print("\033[1;93m")
    print("This loop assisting you to define the devices per segment in the topology.")
    print("The IDs of the devices (for Rn is n) are used for the addressing scheme on segment (eg (NET).(MIN_ID).(MAX_ID).(ID)/24).")
    print("Segments can have more than two devices!")
    print("Segments with more than two devices using the addressing scheme (NET).(100 + MIN_ID).(100 + MAX_ID).(ID)/24.")
    print("Segments (with two devices) having the same MIN_ID and MAX_ID are not supported.")
    print("Segments (with MORE THAN two devices) having the same MIN_ID and MAX_ID are not supported.")
    print("To quit this loop enter 'EXIT' (case sensitive)!")
    print("\033[0m")

    TRACK_INPUT = 0

    while TRACK_INPUT == 0:
        USER_INPUT = input("\033[1;93m Enter the IDs of the devices on a given segmant (eg '1,2' or '1,2,3,4', RESPECT THE FORMAT), then press 'ENTER' \n: \033[0m")
        if USER_INPUT == "EXIT" and SEGMENTS_LIST_STRING != []:
            TRACK_INPUT = 1
            print("\033[1;93m Exit the segments loop. \033[0m")
        elif USER_INPUT == "EXIT" and SEGMENTS_LIST_STRING == []:
            print("\033[1;93m You have not provided any input. \033[0m")
        else:
            SEGMENTS_LIST_STRING.append(USER_INPUT)

    for element in SEGMENTS_LIST_STRING:
        X = element.split(',')
        SEGMENTS_LIST_LIST.append(X)


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

    #Sends configuration.
    COMMANDS = []
    for element_1 in SEGMENTS_LIST_LIST:
        element_1 = [int(i) for i in element_1]
        MIN_ID = min(element_1)
        MAX_ID = max(element_1)
        if int(ID) in element_1 and len(element_1) == 2:
            C1 = "interface " + INTERCONNECTIONS_LIST_LIST[0][0]
            C2 = "no shutdown"
            C3 = "interface " + INTERCONNECTIONS_LIST_LIST[0][0] + "." + str(MIN_ID) + str(MAX_ID)
            C4 = "encapsulation dot1Q " + str(MIN_ID) + str(MAX_ID)
            C5 = "ip address " + INTERCONNECTIONS_LIST_LIST[0][1].split('.')[0] + "." + str(MIN_ID) + "." + str(MAX_ID) + "." + ID + " 255.255.255.0"
            COMMANDS.append(C1)
            COMMANDS.append(C2)
            COMMANDS.append(C3)
            COMMANDS.append(C4)
            COMMANDS.append(C5)
        elif int(ID) in element_1 and len(element_1) != 2:
            C1 = "interface " + INTERCONNECTIONS_LIST_LIST[0][0]
            C2 = "no shutdown"
            C3 = "interface " + INTERCONNECTIONS_LIST_LIST[0][0] + "." + str(MIN_ID) + str(MAX_ID)
            C4 = "encapsulation dot1Q " + str(MIN_ID) + str(MAX_ID)
            C5 = "ip address " + INTERCONNECTIONS_LIST_LIST[0][1].split('.')[0] + "." + str(100 + MIN_ID) + "." + str(100 + MAX_ID) + "." + ID + " 255.255.255.0"
            COMMANDS.append(C1)
            COMMANDS.append(C2)
            COMMANDS.append(C3)
            COMMANDS.append(C4)
            COMMANDS.append(C5)
        else:
            pass
    for element_2 in LOOPBACKS_LIST_LIST:
        C6 = "interface " + element_2[0]
        C7 = "ip address " + element_2[1].split('.')[0] + "." + ID + "." + ID + "." + ID + " 255.255.255.0"
        COMMANDS.append(C6)
        COMMANDS.append(C7)

    # Print configuration commands.
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
