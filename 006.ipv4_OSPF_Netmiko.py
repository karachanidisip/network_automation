from netmiko import ConnectHandler
import ipaddress
import concurrent.futures
from inventory import NetmikoDeviceDB, NETMIKO_DB_PATH
from topology import Topology
from variables import DEVICES, TOPOLOGY, NETWORKS, EBGP
#import logging
#logging.basicConfig(filename="netmiko_debug.log", level=logging.DEBUG)
#logger = logging.getLogger("netmiko")


# Networks participating in OSPF process (intrasite links only — see 004 for
# why EBGP-declared boundary links are excluded here)
topology = Topology(TOPOLOGY, NETWORKS, EBGP).intrasite_topology()
OSPF_NETWORKS_AND_AREAS = topology.topology_networks_with_ospf_areas()


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

    # Finds OSPF networks.
    ospf_networks_areas = []
    for element in interface_and_ipv4:
        ip_address = ipaddress.IPv4Address(element[1])
        for item in OSPF_NETWORKS_AND_AREAS:
            ip_network = ipaddress.IPv4Network(item[0])
            if ip_address in ip_network and item not in ospf_networks_areas:
                ospf_networks_areas.append([item[0], item[1]])
            else:
                pass

    # Convert OSPF networks to NETWORK WILDCARD statements.
    ospf_networks_wildcards_areas = []
    for element in ospf_networks_areas:
        network_mask = ipaddress.IPv4Network(element[0], strict=True)
        network = network_mask.network_address
        mask = network_mask.netmask
        wildcard_split_list = []
        for x in str(mask).split("."):
            y = str(255 - int(x))
            wildcard_split_list.append(y)
        wildcard = ".".join(wildcard_split_list)
        ospf_statement = str(network) + " " + wildcard + " area " + element[1]
        ospf_networks_wildcards_areas.append(ospf_statement)

    # Finds ID.
    device_id_digits = ""
    for character in host_hostname:
        if character.isdigit():
            device_id_digits += character
    device_id = int(device_id_digits)
    ospf_process = topology.routing_process_tag(device_id)

    # OSPF commands.
    ospf_commands = []
    if len(ospf_networks_wildcards_areas) != 0:
        ospf_commands.append("router ospf " + ospf_process)
        for element in ospf_networks_wildcards_areas:
            ospf_commands.append("network " + element)
    else:
        pass

    # Sends configuration commands.
    net_connect.send_config_set(ospf_commands)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Disconnects from host.
    net_connect.disconnect()

    # Return.
    return ospf_commands


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

    # Finds OSPF interfaces.
    ospf_interfaces_areas = []
    for element in interface_and_ipv4:
        ip_address = ipaddress.IPv4Address(element[1].split("/")[0])
        for item in OSPF_NETWORKS_AND_AREAS:
            ip_network = ipaddress.IPv4Network(item[0])
            if ip_address in ip_network:
                ospf_interfaces_areas.append([element[0], item[1]])
            else:
                pass

    # Finds ID.
    device_id_digits = ""
    for character in host_hostname:
        if character.isdigit():
            device_id_digits += character
    device_id = int(device_id_digits)
    ospf_process = topology.routing_process_tag(device_id)

    # OSPF commands.
    ospf_commands = []
    if len(ospf_interfaces_areas) != 0:
        ospf_commands.append("router ospf " + ospf_process)
        for element in ospf_interfaces_areas:
            ospf_commands.append("area " + element[1])
            ospf_commands.append("interface " + element[0])
    else:
        pass

    # Sends configuration commands.
    net_connect.send_config_set(ospf_commands)

    # Saves the running-config to the startup-config.
    net_connect.commit()

    # Disconnects from host.
    net_connect.disconnect()

    # Return.
    return ospf_commands


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
