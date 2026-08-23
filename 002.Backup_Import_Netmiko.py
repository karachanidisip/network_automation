from netmiko import ConnectHandler
import time
import concurrent.futures
from inventory import NetmikoDeviceDB, NETMIKO_DB_PATH
#import logging
#logging.basicConfig(filename="netmiko_debug.log", level=logging.DEBUG)
#logger = logging.getLogger("netmiko")


# Devices to be configured
DEVICES = ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5", "10.0.0.6", "10.0.0.7", "10.0.0.8", "10.0.0.9", "10.0.0.10",
           "10.0.0.11", "10.0.0.12", "10.0.0.13", "10.0.0.14"]


def xe(INPUT_DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Finds host hostname.
    prompt = net_connect.find_prompt()
    host_hostname = prompt.rstrip("#>")

    # Copies startup-config.
    exec_output = net_connect.send_command_timing("copy tftp://10.0.0.100/" + host_hostname + "_startup-config.cfg unix:", read_timeout=10)
    exec_output += net_connect.send_command_timing("\n")
    exec_output += net_connect.send_command_timing("\n")
    message_1 = host_hostname + ": TFTP copy step - unexpected output, check manually."
    if "OK" in exec_output:
        message_1 = host_hostname + " has copied a startup-config.cfg from TFTP server!!!"
    else:
        pass

    # Replaces startup-config.
    exec_output = net_connect.send_command_timing("configure replace unix:" + host_hostname + "_startup-config.cfg", read_timeout=30)
    exec_output += net_connect.send_command_timing("Y")
    message_2 = host_hostname + ": configure replace step - unexpected output, check manually."
    if "Rollback Done" in exec_output:
        message_2 = host_hostname + " has performed a Rollback!!!"
    else:
        pass

    # Deletes startup-config.
    exec_output = net_connect.send_command_timing("delete unix:" + host_hostname + "_startup-config.cfg", read_timeout=10)
    exec_output += net_connect.send_command_timing("\n")
    exec_output += net_connect.send_command_timing("\n")
    if True:
        message_3 = host_hostname + " has deleted the downloaded startup-config.cfg from TFTP server!!!"
    else:
        pass

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Disconnects from host.
    net_connect.disconnect()

    return message_1, message_2, message_3


def xr(INPUT_DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Finds host hostname.
    prompt = net_connect.find_prompt()
    host_hostname = prompt.split(":")[-1].rstrip("#>")

    # Copies startup-config.
    exec_output = net_connect.send_command_timing("copy tftp://10.0.0.100/" + host_hostname + "_startup-config.cfg nvram:", read_timeout=10)
    exec_output += net_connect.send_command_timing("\n")
    exec_output += net_connect.send_command_timing("\n")
    message_1 = host_hostname + ": TFTP copy step - unexpected output, check manually."
    if "bytes" in exec_output:
        message_1 = host_hostname + " has copied a startup-config.cfg from TFTP server!!!"
    else:
        pass

    # Replaces startup-config.
    net_connect.config_mode()
    exec_output = net_connect.send_command_timing("load nvram:/" + host_hostname + "_startup-config.cfg", read_timeout=30)
    exec_output += net_connect.send_command_timing("commit replace", read_timeout=30)
    net_connect.write_channel("yes")
    # Wait for commit to finish
    time.sleep(30)
    message_2 = host_hostname + ": configure replace step - unexpected output, check manually."
    if "Loading" in exec_output:
        message_2 = host_hostname + " has performed a Rollback!!!"
    else:
        pass

    # Deletes startup-config.
    net_connect.exit_config_mode()
    exec_output = net_connect.send_command_timing("delete nvram:" + host_hostname + "_startup-config.cfg", read_timeout=10)
    exec_output += net_connect.send_command_timing("\n")
    exec_output += net_connect.send_command_timing("\n")
    if True:
        message_3 = host_hostname + " has deleted the downloaded startup-config.cfg from TFTP server!!!"
    else:
        pass

    # Saves the running-config to the startup-config.
    net_connect.commit()

    # Disconnects from host.
    net_connect.disconnect()

    return message_1, message_2, message_3


def xe_xr(host):
    if host.get("device_type") == "cisco_ios_telnet":
        returned_by_xe = xe(host)
        print(returned_by_xe[0])
        print(returned_by_xe[1])
        print(returned_by_xe[2])
    elif host.get("device_type") == "cisco_xr_telnet":
        returned_by_xr = xr(host)
        print(returned_by_xr[0])
        print(returned_by_xr[1])
        print(returned_by_xr[2])
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
