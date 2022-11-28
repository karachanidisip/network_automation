# This line imports the needed Functions from netmiko
from netmiko import ConnectHandler
# This line imports the os, sys, datetime, random, string, subprocess, concurrent.futures Modules
import os, sys, datetime, random, string, subprocess, concurrent.futures
# This line imports the variables file (it should be placed in the same directory with the python script)
from var_file import *


def targets():
    # A function to get input from user.
    # As TARGETS are defined the devices that we want to interact.

    print("\033[1;93m")
    print("This loop assisting you to define the targets (ipv4 management addresses)!")
    print("To define all devices as targets enter 'ALL' (case sensitive)!")
    print("To quit this loop enter 'EXIT' (case sensitive)!")
    print("\033[0m")

    track_input = 0

    while track_input == 0:
        user_input = input("\033[1;93m Enter the ipv4 address (management address) of the target \n: \033[0m")
        if user_input == "EXIT":
            track_input = 1
            print("\033[1;93m Exit the target loop! \033[0m")
        else:
            EXPORT_TARGETS_LIST.append(user_input)

    print("\033[1;92m")
    print("The targets are in the following LIST")
    print(EXPORT_TARGETS_LIST)
    print("\033[0m")


def hosts(INPUT_LIST):
    # A function to extract HOSTS from DEVICES based on TARGETS.
    # HOSTS are subset of DEVICES.

    if "ALL" in INPUT_LIST:
        for element_1 in DEVICES_LIST:
            EXPORT_HOSTS_LIST.append(element_1)
    else:
        for element_2 in INPUT_LIST:
            for element_3 in DEVICES_LIST:
                if ("host", element_2) in element_3.items():
                    EXPORT_HOSTS_LIST.append(element_3)

    print("\033[1;92m")
    print("The hosts information are in the following LIST")
    print(EXPORT_HOSTS_LIST)
    print("\033[0m")


def backup(INPUT_DICT_PER_HOST):
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

    # Finds host hostname.
    with open("startup_config_temporary" + random_string, "r") as f:
        for line in f:
            if line.startswith("hostname"):
                host_hostname = line.strip("hostname")
                host_hostname = host_hostname.lstrip()
                host_hostname = host_hostname.rstrip("\n")

    # Deletes the temporary file.
    if os.path.exists("startup_config_temporary" + random_string):
        os.remove("startup_config_temporary" + random_string)

    # Creates a "hostname_startup-config.cfg" file (if the specified file does not exist) and overwrites any existing content (if there is).
    save_path = GIT_PATH
    file_name = str(host_hostname) + "_startup-config.cfg"
    complete_name = os.path.join(save_path, file_name)
    with open(f"{complete_name}", "w") as f:
        # Print the output of execution commands sent to host via Telnet/SSH.
        print(exec_output, file=f)

    # Closes the connection.
    net_connect.disconnect()

    print("\033[1;91m")
    print("There is a new startup-config file for the " + str(host_hostname) + " host!!!")
    print("\033[0m")


def git():
    # $cd /home/pantelis/Downloads/CONFIGURATION_MANAGEMENT/000_GIT/
    # Change the working directory to the GIT repository.
    # $git init
    # $git config --global user.email "no_email@no_email.com"
    # $ git config --global user.name "pantelis"
    # Initializing a repository (needed only once).
    # $git log
    # Viewing the history.
    # $git show HEAD
    # Shows the last commit.
    # $git show HEAD~2
    # Shows two steps before the last commit.
    # $git checkout <COMMIT_ID> .
    # Restoring an old version. NOTICE that the trailing "." is needed!

    # YearMonthDate.
    ymd = datetime.date.today()
    date = ymd.strftime("%Y%m%d")

    # HourMinuteSecond.
    hms = datetime.datetime.now()
    time = hms.strftime("%H%M%S")

    user_comment = input("\033[1;93m Enter a comment about the changes \n: \033[0m")

    commit_name = date + "-" + time + "-" + user_comment

    commit_path = GIT_PATH + "/*"

    # GIT add command.
    command_git_add = ["git", "add", commit_path]
    git_add = subprocess.run(command_git_add, cwd=GIT_PATH, stdout=subprocess.PIPE)

    # GIT commit command.
    command_git_commit = ["git", "commit", "-m " + commit_name]
    git_commit = subprocess.run(command_git_commit, cwd=GIT_PATH, stdout=subprocess.PIPE)

    print("\033[1;91m")
    print("There is a new GIT COMMIT!!!")
    print("\033[0m")


# CODE!!!
targets()
hosts(EXPORT_TARGETS_LIST)

# The asynchronous execution can be performed with threads (ThreadPoolExecutor), or processes (ProcessPoolExecutor).
# If the program spends more time waiting on network requests (or any type of I/O task) there is an I/O bottleneck and you should use ThreadPoolExecutor.
# If the program spends more time processing large datasets there is a CPU bottleneck and you should use ProcessPoolExecutor.
# ThreadPoolExecutor cannot be used for parallel CPU computations.
# ThreadPoolExecutor is perfect for scripts related to network/data I/O because the processor is sitting idle waiting for data.
with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
    future = [executor.submit(backup, element) for element in EXPORT_HOSTS_LIST]

git()
