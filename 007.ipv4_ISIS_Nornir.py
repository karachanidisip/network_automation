import ipaddress
from topology import Topology
from variables import DEVICES, TOPOLOGY, NETWORKS, EBGP
from nornir import InitNornir
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command
from nornir_netmiko.tasks import netmiko_send_config
from nornir_netmiko.tasks import netmiko_save_config
from nornir_netmiko.tasks import netmiko_commit
from nornir_jinja2.plugins.tasks import template_file
#import logging
#logging.basicConfig(
#    filename="nornir_debug.log",
#    level=logging.DEBUG,
#    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")


# Networks participating in ISIS process (intrasite links only — see 004 for
# why EBGP-declared boundary links are excluded here)
topology = Topology(TOPOLOGY, NETWORKS, EBGP).intrasite_topology()
ISIS_NETWORKS_AND_LEVELS = topology.topology_networks_with_isis_levels()


def xe(task):
    net_connect = task.host.get_connection("netmiko", task.nornir.config)
    net_connect.enable()
    host_hostname = net_connect.find_prompt().rstrip("#>")

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
    netmiko_send_config(task, config_commands=isis_commands)
    netmiko_save_config(task)

    return isis_commands


def xr(task):
    net_connect = task.host.get_connection("netmiko", task.nornir.config)
    net_connect.enable()
    host_hostname = net_connect.find_prompt().split(":")[-1].rstrip("#>")

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
    netmiko_send_config(task, config_commands=isis_commands)
    netmiko_commit(task)

    return isis_commands


def main():

    nr = InitNornir(
        runner={
            "plugin": "threaded",
            "options": {"num_workers": 20}
        },
        inventory={
            "plugin": "SimpleInventory",
            "options": {
                "host_file": "/home/pantelis/GNS3/projects/AUTOMATION_DEMO_PROJECT/hosts.yaml",
                "group_file": "/home/pantelis/GNS3/projects/AUTOMATION_DEMO_PROJECT/groups.yaml",
                "defaults_file": "/home/pantelis/GNS3/projects/AUTOMATION_DEMO_PROJECT/defaults.yaml"
            }
        }
    )

    result = nr.filter(platform="cisco_ios_telnet").run(task=xe)
    print_result(result)
    result = nr.filter(platform="cisco_xr_telnet").run(task=xr)
    print_result(result)


if __name__ == "__main__":
    main()
