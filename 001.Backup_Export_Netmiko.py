from pathlib import Path
from netmiko import ConnectHandler
import datetime
import subprocess
import concurrent.futures
from inventory import NetmikoDeviceDB, NETMIKO_DB_PATH
#import logging
#logging.basicConfig(filename="netmiko_debug.log", level=logging.DEBUG)
#logger = logging.getLogger("netmiko")


# Paths
REPOSITORY_PATH = Path(__file__).resolve().parent / "001.REPOSITORY/"


# Devices to be configured
DEVICES = ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5", "10.0.0.6", "10.0.0.7", "10.0.0.8", "10.0.0.9", "10.0.0.10",
           "10.0.0.11", "10.0.0.12", "10.0.0.13", "10.0.0.14"]


def xe(INPUT_DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Finds host hostname.
    prompt = net_connect.find_prompt()
    host_hostname = prompt.rstrip("#>")

    # Sends execution commands.
    exec_output = net_connect.send_command("show running-config")

    # Creates a "hostname_startup-config.cfg" file (if the specified file does not exist) and overwrites any existing content (if there is).
    file_name = host_hostname + "_startup-config.cfg"
    complete_name = REPOSITORY_PATH / file_name
    with open(f"{complete_name}", "w") as f:
        # Removes initial non configuration lines and exclamation marks in order to comply with IOS/IOS-XE/IOS-XR startup-config format.

        exclamation_mark_counter = 0
        clear_config = ""

        for line in exec_output.splitlines():
            if line.startswith("!"):
                exclamation_mark_counter += 1
            elif exclamation_mark_counter >= 1:
                clear_config += line + "\n"

        f.write(clear_config)

    # Disconnects from host.
    net_connect.disconnect()

    message = "There is a new startup-config file for the " + host_hostname + " host!!!"
    return message


def xr(INPUT_DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Finds host hostname.
    prompt = net_connect.find_prompt()
    host_hostname = prompt.split(":")[-1].rstrip("#>")

    # Sends execution commands.
    exec_output = net_connect.send_command(
        "show running-config",
        read_timeout=120
        )

    # Creates a "hostname_startup-config.cfg" file (if the specified file does not exist) and overwrites any existing content (if there is).
    file_name = host_hostname + "_startup-config.cfg"
    complete_name = REPOSITORY_PATH / file_name
    with open(f"{complete_name}", "w") as f:
        # Removes initial non configuration lines and exclamation marks in order to comply with IOS/IOS-XE/IOS-XR startup-config format.

        exclamation_mark_counter = 0
        clear_config = ""

        for line in exec_output.splitlines():
            if line.startswith("!"):
                exclamation_mark_counter += 1
            elif exclamation_mark_counter >= 1:
                clear_config += line + "\n"

        f.write(clear_config)

    # Disconnects from host.
    net_connect.disconnect()

    message = "There is a new startup-config file for the " + host_hostname + " host!!!"
    return message


def git():
    # YearMonthDate.
    ymd = datetime.date.today()
    date = ymd.strftime("%Y%m%d")

    # HourMinuteSecond.
    hms = datetime.datetime.now()
    time = hms.strftime("%H%M%S")

    user_comment = input("\033[1;93m Enter a comment about the changes \n: \033[0m")

    commit_name = date + "-" + time + "-" + user_comment

    # GIT add command.
    git_add = subprocess.run(["git", "add", "."], cwd = REPOSITORY_PATH, capture_output=True, text=True)
    print(git_add.stdout)
    print(git_add.stderr)

    # GIT commit command.
    git_commit = subprocess.run(["git", "commit", "-m", commit_name], cwd = REPOSITORY_PATH, capture_output=True, text=True)
    print(git_commit.stdout)
    print(git_commit.stderr)


def xe_xr(host):
    if host.get("device_type") == "cisco_ios_telnet":
        returned_by_xe = xe(host)
        print(returned_by_xe)
    elif host.get("device_type") == "cisco_xr_telnet":
        returned_by_xr = xr(host)
        print(returned_by_xr)
    else:
        pass


if __name__ == "__main__":
    output = NetmikoDeviceDB(NETMIKO_DB_PATH).get_multiple_devices(DEVICES)

    with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
        future_to_host = {executor.submit(xe_xr, host): host for host in output}

        for future in concurrent.futures.as_completed(future_to_host):
            host = future_to_host[future]
            try:
                result = future.result()
                print(result)
            except Exception as e:
                print(f"[ERROR] {host.get('host')}: {e}")

    git()
