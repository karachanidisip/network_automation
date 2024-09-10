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



def backup_import(INPUT_DICT_PER_HOST):
    # $sudo systemctl status firewalld.service
    # Checks the status of firewalld on TFTP server.
    # $sudo systemctl stop firewalld.service
    # Stops the firewalld on TFTP server (allows access to the TFTP server).
    # $ sudo systemctl start firewalld.service
    # Starts the firewalld on TFTP server (prevents access to the TFTP server).
    # $sudo /home/pantelis/.VENV/bin/python3 "/home/pantelis/GNS3/projects/AUTOMATION/002_backup_import/TFTP/tftp.py"
    # Enables the TFTP server.

    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Finds host hostname.
    HOST_HOSTNAME = net_connect.find_prompt()[:-1]

    # Sends execution commands.
    exec_output = net_connect.send_command(
    command_string = "copy tftp://10.0.0.15/" + HOST_HOSTNAME + "_startup-config.cfg unix:",
    expect_string=r"Destination filename",
    strip_prompt=False,
    strip_command=False
    )
    exec_output += net_connect.send_command(
        command_string="\n",
        expect_string=r"#",
        strip_prompt=False,
        strip_command=False
    )
    print()
    print(exec_output)
    print()
    print("\033[1;91m")
    print(HOST_HOSTNAME + " has copied a startup-config.cfg from TFTP server!!!")
    print("\033[0m")

    # Sends execution commands.
    exec_output = net_connect.send_command(
    command_string = "configure replace unix:" + HOST_HOSTNAME + "_startup-config.cfg",
    expect_string=r"no",
    strip_prompt=False,
    strip_command=False
    )
    exec_output += net_connect.send_command(
        command_string="Y",
        expect_string=r"#",
        strip_prompt=False,
        strip_command=False
    )
    print()
    print(exec_output)
    print()
    print("\033[1;91m")
    print(HOST_HOSTNAME + " has performed a Rollback!!!")
    print("\033[0m")

    # Sends execution commands.
    exec_output = net_connect.send_command(
    command_string = "delete unix:" + HOST_HOSTNAME + "_startup-config.cfg",
    expect_string=r"Delete filename",
    strip_prompt=False,
    strip_command=False
    )
    exec_output += net_connect.send_command(
        command_string="\n",
        expect_string=r"confirm",
        strip_prompt=False,
        strip_command=False
    )
    exec_output += net_connect.send_command(
        command_string="\n",
        expect_string=r"#",
        strip_prompt=False,
        strip_command=False
    )
    print()
    print(exec_output)
    print()
    print("\033[1;91m")
    print(HOST_HOSTNAME + " has deleted the downloaded startup-config.cfg from TFTP server!!!")
    print("\033[0m")

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
with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
    future = [executor.submit(backup_import, element) for element in HOSTS]
