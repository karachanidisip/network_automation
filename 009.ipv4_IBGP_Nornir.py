from topology import Topology, TOPOLOGY, NETWORKS
from variables import DEVICES, IBGP
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


def ibgp_neighbors(device_id):
    """Returns this device's asn and the full-mesh list of neighbor device_ids
    (every other device_id sharing an IBGP entry with device_id)."""
    asn = ""
    neighbor_ids = []
    for entry in IBGP:
        device_ids = []
        for d in entry["device_ids"].split("-"):
            device_ids.append(int(d))

        if device_id in device_ids:
            asn = entry["asn"]
            for neighbor_id in device_ids:
                if neighbor_id != device_id and neighbor_id not in neighbor_ids:
                    neighbor_ids.append(neighbor_id)

    return asn, neighbor_ids


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

    # Finds IBGP asn and neighbors.
    asn, neighbor_ids = ibgp_neighbors(device_id)

    # BGP commands.
    bgp_commands = []
    if len(neighbor_ids) != 0:
        bgp_commands.append("router bgp " + asn)
        for neighbor_id in neighbor_ids:
            neighbor_loopback = topology.loopback_address(neighbor_id).split("/")[0]
            bgp_commands.append("neighbor " + neighbor_loopback + " remote-as " + asn)
            bgp_commands.append("neighbor " + neighbor_loopback + " update-source Loopback0")
    else:
        pass

    # Sends configuration commands.
    if len(bgp_commands) == 0:
        pass
    else:
        netmiko_send_config(task, config_commands=bgp_commands)
        netmiko_save_config(task)

    return bgp_commands


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

    # Finds IBGP asn and neighbors.
    asn, neighbor_ids = ibgp_neighbors(device_id)

    # BGP commands.
    bgp_commands = []
    if len(neighbor_ids) != 0:
        bgp_commands.append("router bgp " + asn)
        bgp_commands.append("address-family ipv4 unicast")
        bgp_commands.append("ibgp policy out enforce-modifications")
        for neighbor_id in neighbor_ids:
            neighbor_loopback = topology.loopback_address(neighbor_id).split("/")[0]
            bgp_commands.append("neighbor " + neighbor_loopback)
            bgp_commands.append("remote-as " + asn)
            bgp_commands.append("update-source Loopback0")
            bgp_commands.append("address-family ipv4 unicast")
    else:
        pass

    # Sends configuration commands.
    if len(bgp_commands) == 0:
        pass
    else:
        netmiko_send_config(task, config_commands=bgp_commands)
        netmiko_commit(task)

    return bgp_commands


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
