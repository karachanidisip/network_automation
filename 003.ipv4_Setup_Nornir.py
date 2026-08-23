from topology import Topology
from variables import (DEVICES, MANAGEMENT_INTERFACE_XE, MANAGEMENT_INTERFACE_XR,
                        TOPOLOGY_INTERFACE_XE, TOPOLOGY_INTERFACE_XR, LOOPBACK_INTERFACE,
                        TOPOLOGY, NETWORKS)
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


topology = Topology(TOPOLOGY, NETWORKS)


def xe(task):
    net_connect = task.host.get_connection("netmiko", task.nornir.config)
    net_connect.enable()
    host_hostname = net_connect.find_prompt().rstrip("#>")

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
    netmiko_send_config(task, config_commands=commands)
    netmiko_save_config(task)

    return commands


def xr(task):
    net_connect = task.host.get_connection("netmiko", task.nornir.config)
    net_connect.enable()
    host_hostname = net_connect.find_prompt().split(":")[-1].rstrip("#>")

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
    netmiko_send_config(task, config_commands=commands)
    netmiko_commit(task)

    return commands


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
