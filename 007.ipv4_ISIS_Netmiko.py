from netmiko import ConnectHandler
import ipaddress
import concurrent.futures
from inventory import NetmikoDeviceDB, NETMIKO_DB_PATH
from topology import Topology
from variables import DEVICES, TOPOLOGY, NETWORKS, EBGP
#import logging
#logging.basicConfig(filename="netmiko_debug.log", level=logging.DEBUG)
#logger = logging.getLogger("netmiko")


# Networks participating in ISIS process (intrasite links only — see 004 for
# why EBGP-declared boundary links are excluded here)
topology = Topology(TOPOLOGY, NETWORKS, EBGP).intrasite_topology()
ISIS_NETWORKS_AND_LEVELS = topology.topology_networks_with_isis_levels()


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

    # Finds ISIS SYSTEM_ID.
    router_id = ""
    for element in host_hostname:
        if element.isdigit():
            router_id = router_id + element
        else:
            pass
    device_id = int(router_id)
    system_id = "0000.0000." + ((4 - len(router_id))*"0" + router_id)

    # Finds ISIS AREA and TAG.
    raw_area = topology.isis_area(device_id)
    area = (4 - len(raw_area)) * "0" + raw_area
    isis_tag = topology.routing_process_tag(device_id)

    # Finds ISIS NET.
    net = "49." + area + "." + system_id + ".00"

    # Finds ISIS interfaces.
    isis_interfaces_levels = []
    for element in interface_and_ipv4:
        ip_address = ipaddress.IPv4Address(element[1])
        for item in ISIS_NETWORKS_AND_LEVELS:
            ip_network = ipaddress.IPv4Network(item[0])
            if ip_address in ip_network:
                isis_interfaces_levels.append([element[0], item[1]])
            else:
                pass

    # ISIS commands.
    isis_commands = []
    if len(isis_interfaces_levels) != 0:
        isis_commands.append("router isis " + isis_tag)
        isis_commands.append("net " + net)
        for element in isis_interfaces_levels:
            isis_commands.append("interface " + element[0])
            isis_commands.append("ip router isis " + isis_tag)
            if element[1] == "1":
                isis_commands.append("isis circuit-type level-1")
            elif element[1] == "2":
                isis_commands.append("isis circuit-type level-2-only")
            else:
                pass
    else:
        pass

    # Sends configuration commands.
    net_connect.send_config_set(isis_commands)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Disconnects from host.
    net_connect.disconnect()

    # Return.
    return isis_commands


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

    # Finds ISIS SYSTEM_ID.
    router_id = ""
    for element in host_hostname:
        if element.isdigit():
            router_id = router_id + element
        else:
            pass
    device_id = int(router_id)
    system_id = "0000.0000." + ((4 - len(router_id))*"0" + router_id)

    # Finds ISIS AREA and TAG.
    raw_area = topology.isis_area(device_id)
    area = (4 - len(raw_area)) * "0" + raw_area
    isis_tag = topology.routing_process_tag(device_id)

    # Finds ISIS NET.
    net = "49." + area + "." + system_id + ".00"

    # Finds ISIS interfaces.
    isis_interfaces_levels = []
    for element in interface_and_ipv4:
        ip_address = ipaddress.IPv4Address(element[1].split("/")[0])
        for item in ISIS_NETWORKS_AND_LEVELS:
            ip_network = ipaddress.IPv4Network(item[0])
            if ip_address in ip_network:
                isis_interfaces_levels.append([element[0], item[1]])
            else:
                pass

    # ISIS commands.
    isis_commands = []
    if len(isis_interfaces_levels) != 0:
        isis_commands.append("router isis " + isis_tag)
        isis_commands.append("net " + net)
        isis_commands.append("address-family ipv4 unicast")
        for element in isis_interfaces_levels:
            isis_commands.append("interface " + element[0])
            isis_commands.append("address-family ipv4 unicast")
            if element[1] == "1":
                isis_commands.append("circuit-type level-1")
            elif element[1] == "2":
                isis_commands.append("circuit-type level-2-only")
            else:
                pass
    else:
        pass

    # Sends configuration commands.
    net_connect.send_config_set(isis_commands)

    # Saves the running-config to the startup-config.
    net_connect.commit()

    # Disconnects from host.
    net_connect.disconnect()

    # Return.
    return isis_commands


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
