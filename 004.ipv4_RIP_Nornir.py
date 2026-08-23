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


# Networks participating in RIP process (intrasite links only — EBGP-declared
# boundary links are excluded so an AS-boundary link, whether or not it's
# been provisioned yet, is never picked up by this IGP scan)
topology = Topology(TOPOLOGY, NETWORKS, EBGP).intrasite_topology()
RIP_NETWORKS = topology.topology_networks()


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
    netmiko_send_config(task, config_commands=rip_commands)
    netmiko_save_config(task)

    return rip_commands



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
    netmiko_send_config(task, config_commands=rip_commands)
    netmiko_commit(task)

    return rip_commands


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
