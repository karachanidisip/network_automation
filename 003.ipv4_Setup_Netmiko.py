from netmiko import ConnectHandler
import concurrent.futures
from inventory import NetmikoDeviceDB, NETMIKO_DB_PATH
from topology import Topology
from variables import (DEVICES, MANAGEMENT_INTERFACE_XE, MANAGEMENT_INTERFACE_XR,
                        TOPOLOGY_INTERFACE_XE, TOPOLOGY_INTERFACE_XR, LOOPBACK_INTERFACE,
                        TOPOLOGY, NETWORKS)
#import logging
#logging.basicConfig(filename="netmiko_debug.log", level=logging.DEBUG)
#logger = logging.getLogger("netmiko")


topology = Topology(TOPOLOGY, NETWORKS)


def xe(INPUT_DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Finds host hostname.
    prompt = net_connect.find_prompt()
    host_hostname = prompt.rstrip("#>")

    # Finds ID.
    device_id_digits = ""
    for character in host_hostname:
        if character.isdigit():
            device_id_digits += character
    device_id = int(device_id_digits)

    # Finds links this device participates in.
    links = topology.links_for_device(device_id)

    # Creates configuration.
    commands = []
    if len(links) != 0:
        loopback_address = topology.loopback_address(device_id)
        loopback_ip = loopback_address.split("/")[0]
        commands.append("interface " + LOOPBACK_INTERFACE)
        commands.append("ip address " + loopback_ip + " 255.255.255.255")
        commands.append("interface " + TOPOLOGY_INTERFACE_XE[0])
        commands.append("no shutdown")

        for link in links:
            tag = topology.dot1q_tag(device_id, link)
            address = topology.ip_address(device_id, link)
            ip_only = address.split("/")[0]
            commands.append("interface " + TOPOLOGY_INTERFACE_XE[0] + "." + tag)
            commands.append("encapsulation dot1Q " + tag)
            commands.append("ip address " + ip_only + " 255.255.255.0")

    # Sends configuration commands.
    net_connect.send_config_set(commands)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Disconnects from host.
    net_connect.disconnect()

    return commands


def xr(INPUT_DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Finds host hostname.
    prompt = net_connect.find_prompt()
    host_hostname = prompt.split(":")[-1].rstrip("#>")

    # Finds ID.
    device_id_digits = ""
    for character in host_hostname:
        if character.isdigit():
            device_id_digits += character
    device_id = int(device_id_digits)

    # Finds links this device participates in.
    links = topology.links_for_device(device_id)

    # Creates configuration.
    commands = []
    if len(links) != 0:
        loopback_address = topology.loopback_address(device_id)
        commands.append("interface " + LOOPBACK_INTERFACE)
        commands.append("ipv4 address " + loopback_address)
        commands.append("interface " + TOPOLOGY_INTERFACE_XR[0])
        commands.append("no shutdown")

        for link in links:
            tag = topology.dot1q_tag(device_id, link)
            address = topology.ip_address(device_id, link)
            commands.append("interface " + TOPOLOGY_INTERFACE_XR[0] + "." + tag)
            commands.append("encapsulation dot1Q " + tag)
            commands.append("ipv4 address " + address)

    # Sends configuration commands.
    net_connect.send_config_set(commands)

    # Saves the running-config to the startup-config.
    net_connect.commit()

    # Disconnects from host.
    net_connect.disconnect()

    return commands


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
