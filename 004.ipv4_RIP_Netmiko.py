from netmiko import ConnectHandler
import ipaddress
import concurrent.futures
from inventory import NetmikoDeviceDB, NETMIKO_DB_PATH
from topology import Topology
from variables import DEVICES, TOPOLOGY, NETWORKS, EBGP
#import logging
#logging.basicConfig(filename="netmiko_debug.log", level=logging.DEBUG)
#logger = logging.getLogger("netmiko")


# Networks participating in RIP process (intrasite links only — EBGP-declared
# boundary links are excluded so an AS-boundary link, whether or not it's
# been provisioned yet, is never picked up by this IGP scan)
topology = Topology(TOPOLOGY, NETWORKS, EBGP).intrasite_topology()
RIP_NETWORKS = topology.topology_networks()


def xe(INPUT_DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Finds host hostname.
    prompt = net_connect.find_prompt()
    host_hostname = prompt.rstrip("#>")

    # Finds ipv4 interfaces.
    cli_output = net_connect.send_command("show interfaces", use_textfsm=True)
    interface_and_ipv4 =[]
    for element in cli_output:
        if element.get("interface") != "Ethernet0/0" and element.get("ip_address") != "":
            interface_and_ipv4.append([element.get("interface"), element.get("ip_address"), element.get("prefix_length")])
        else:
            pass

    # Finds RIP networks.
    rip_networks = []
    for element in interface_and_ipv4:
        ip_address = ipaddress.IPv4Address(element[1])
        for item in RIP_NETWORKS:
            ip_network = ipaddress.IPv4Network(item)
            if ip_address in ip_network:
                rip_networks.append(element[1])
            else:
                pass

    # Convert RIP networks to CASSFUL networks.
    rip_networks_classful = []
    for element in rip_networks:
        first_octet = int(element.split(".")[0])
        if first_octet < 128:
            item = element.split(".")[0] + ".0.0.0"
            if item not in rip_networks_classful:
                rip_networks_classful.append(item)
            else:
                pass
        elif first_octet < 192:
            item = element.split(".")[0] + "." + element.split(".")[1] + ".0.0"
            if item not in rip_networks_classful:
                rip_networks_classful.append(item)
            else:
                pass
        elif first_octet < 224:
            item = element.split(".")[0] + "." + element.split(".")[1] + "." + element.split(".")[2] + ".0"
            if item not in rip_networks_classful:
                rip_networks_classful.append(item)
            else:
                pass
        else:
            pass

    # RIP commands.
    rip_commands = []
    if len(rip_networks_classful) != 0:
        rip_commands.append("router rip")
        rip_commands.append("no auto-summary")
        rip_commands.append("version 2")
        for element in rip_networks_classful:
            rip_commands.append("network " + element)
    else:
        pass

    # Sends configuration commands.
    net_connect.send_config_set(rip_commands)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Disconnects from host.
    net_connect.disconnect()

    # Return.
    return rip_commands


def xr(INPUT_DICT_PER_HOST):
    # Connects to the host using Netmiko (Telnet/SSH).
    net_connect = ConnectHandler(**INPUT_DICT_PER_HOST)

    # Finds host hostname.
    prompt = net_connect.find_prompt()
    host_hostname = prompt.split(":")[-1].rstrip("#>")

    # Finds ipv4 interfaces.
    cli_output = net_connect.send_command("show interfaces", use_textfsm=True)
    interface_and_ipv4 =[]
    for element in cli_output:
        if element.get("interface") != "MgmtEth0/0/CPU0/0" and element.get("ip_address") != "Unknown":
            interface_and_ipv4.append([element.get("interface"), element.get("ip_address")])
        else:
            pass

    # Finds RIP interfaces.
    rip_interfaces = []
    for element in interface_and_ipv4:
        ip_address = ipaddress.IPv4Address(element[1].split("/")[0])
        for item in RIP_NETWORKS:
            ip_network = ipaddress.IPv4Network(item)
            if ip_address in ip_network:
                rip_interfaces.append(element[0])
            else:
                pass

    # RIP commands.
    rip_commands = []
    if len(rip_interfaces) != 0:
        rip_commands.append("router rip")
        rip_commands.append("no auto-summary")
        for element in rip_interfaces:
            rip_commands.append("interface " + element)
            rip_commands.append("send version 2")
            rip_commands.append("receive version 2")
    else:
        pass

    # Sends configuration commands.
    net_connect.send_config_set(rip_commands)

    # Saves the running-config to the startup-config.
    net_connect.commit()

    # Disconnects from host.
    net_connect.disconnect()

    # Return.
    return rip_commands


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
