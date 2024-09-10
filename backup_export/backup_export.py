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



# Paths
GIT_PATH = "/home/pantelis/GNS3/projects/AUTOMATION/001_backup_export/GIT/"



def backup_export(INPUT_DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Finds host hostname.
    HOST_HOSTNAME = net_connect.find_prompt()[:-1]

    # Sends execution commands.
    exec_output = net_connect.send_command("show startup-config")

    # Creates a "hostname_startup-config.cfg" file (if the specified file does not exist) and overwrites any existing content (if there is).
    save_path = GIT_PATH
    file_name = HOST_HOSTNAME + "_startup-config.cfg"
    complete_name = os.path.join(save_path, file_name)
    with open(f"{complete_name}", "w") as f:
        # Print the output of execution commands sent to host via Telnet/SSH.
        # The partition method used to remove the first line "Using YYY out of XXX bytes" in order to comply with IOS/IOS-XE/IOS-XR startup-config format.
        print(exec_output.partition("!")[2], file=f)
    print("\033[1;91m")
    print("There is a new startup-config file for the " + HOST_HOSTNAME + " host!!!")
    print("\033[0m")

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Disconnects from host.
    net_connect.disconnect()



def git():
    # $cd "/home/pantelis/GNS3/projects/AUTOMATION/001_backup_export/GIT/"
    # Change the working directory to the GIT repository.
    # $git init
    # $git config --global user.email "no_email@no_email.com"
    # $git config --global user.name "pantelis"
    # Initializing a repository (needed only once).
    # $git log
    # Viewing the history.
    # $git show HEAD
    # Shows the last commit.
    # $git show HEAD~2
    # Shows two steps before the last commit.
    # $git checkout <COMMIT_ID> .
    # Restoring an old version. NOTICE that the trailing "." is NEEDED! Then you have to issue the "git commit -m MESSAGE" command in order to version the "new" state.
    # $git checkout <COMMIT_ID>
    # Switch to an old version. NOTICE that the trailing "." is MISSING! All the subsequent versions are deleted. To undo this operation issue the "git switch -" command.

    # YearMonthDate.
    ymd = datetime.date.today()
    date = ymd.strftime("%Y%m%d")

    # HourMinuteSecond.
    hms = datetime.datetime.now()
    time = hms.strftime("%H%M%S")

    user_comment = input("\033[1;93m Enter a comment about the changes \n: \033[0m")

    commit_name = date + "-" + time + "-" + user_comment

    # GIT add command.
    git_add = subprocess.run(["git", "add", "."], cwd = GIT_PATH, capture_output=True, text=True)
    print(git_add.stdout)
    print(git_add.stderr)

    # GIT commit command.
    git_commit = subprocess.run(["git", "commit", "-m " + commit_name], cwd = GIT_PATH, capture_output=True, text=True)
    print(git_commit.stdout)
    print(git_commit.stderr)


# CODE!!!



# The asynchronous execution can be performed with threads (ThreadPoolExecutor), or processes (ProcessPoolExecutor).
# If the program spends more time waiting on network requests (or any type of I/O task) there is an I/O bottleneck and you should use ThreadPoolExecutor.
# If the program spends more time processing large datasets there is a CPU bottleneck and you should use ProcessPoolExecutor.
# ThreadPoolExecutor cannot be used for parallel CPU computations.
# ThreadPoolExecutor is perfect for scripts related to network/data I/O because the processor is sitting idle waiting for data.
with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
    future = [executor.submit(backup_export, element) for element in HOSTS]

git()
