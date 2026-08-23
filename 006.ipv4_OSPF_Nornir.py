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


# Networks participating in OSPF process (intrasite links only — see 004 for
# why EBGP-declared boundary links are excluded here)
topology = Topology(TOPOLOGY, NETWORKS, EBGP).intrasite_topology()
OSPF_NETWORKS_AND_AREAS = topology.topology_networks_with_ospf_areas()


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
    netmiko_send_config(task, config_commands=ospf_commands)
    netmiko_save_config(task)

    return ospf_commands


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
    netmiko_send_config(task, config_commands=ospf_commands)
    netmiko_commit(task)

    return ospf_commands


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
