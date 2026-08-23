import ipaddress
from topology import Topology
from variables import DEVICES, MANAGEMENT_INTERFACE_XE, MANAGEMENT_INTERFACE_XR, NETWORKS, MPLS, TOPOLOGY, EBGP
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


# Any interface with an IP inside this network is treated as the management
# interface and is never enabled for MPLS forwarding.
MANAGEMENT_NETWORK = ipaddress.IPv4Network(MANAGEMENT_INTERFACE_XE[1])
# OR
MANAGEMENT_NETWORK = ipaddress.IPv4Network(MANAGEMENT_INTERFACE_XR[1])
LOOPBACK_NETWORK = ipaddress.IPv4Network(NETWORKS["LOOPBACK"])

# Intersite (eBGP boundary) link subnets. Unlike 004-007, this script doesn't
# build its interface list from TOPOLOGY at all — it scans "show interfaces"
# directly — so it has no other way to recognize an AS-boundary link.
# Excluded the same way MANAGEMENT_NETWORK/LOOPBACK_NETWORK are, so MPLS is
# never enabled on a boundary link regardless of whether 010_ipv4_ebgp.py
# has run yet.
topology = Topology(TOPOLOGY, NETWORKS, EBGP)
INTERSITE_NETWORKS = [ipaddress.IPv4Network(n) for n in topology.intersite_networks()]


def is_intersite_address(ip_address):
    """True if ip_address falls inside any INTERSITE_NETWORKS subnet."""
    for network in INTERSITE_NETWORKS:
        if ip_address in network:
            return True
    return False


MPLS_DEVICE_IDS = []
for d in MPLS["devices_ids"].split("-"):
    MPLS_DEVICE_IDS.append(int(d))


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

    # MPLS commands.
    mpls_commands = []
    if device_id in MPLS_DEVICE_IDS:
        # Finds ip enabled interfaces.
        cli_output = net_connect.send_command("show interfaces", use_textfsm=True)
        mpls_interfaces = []
        for element in cli_output:
            ip_address = element.get("ip_address")
            if ip_address != "":
                address = ipaddress.IPv4Address(ip_address)
                if address not in MANAGEMENT_NETWORK and not is_intersite_address(address):
                    mpls_interfaces.append(element.get("interface"))
            else:
                pass

        if len(mpls_interfaces) != 0:
            mpls_commands.append("mpls ip")
            for interface in mpls_interfaces:
                mpls_commands.append("interface " + interface)
                mpls_commands.append("mpls ip")
        else:
            pass
    else:
        pass

    # Sends configuration commands.
    if len(mpls_commands) == 0:
        pass
    else:
        netmiko_send_config(task, config_commands=mpls_commands)
        netmiko_save_config(task)

    return mpls_commands


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

    # MPLS commands.
    mpls_commands = []
    if device_id in MPLS_DEVICE_IDS:
        # Finds ip enabled interfaces.
        cli_output = net_connect.send_command("show interfaces", use_textfsm=True)
        mpls_interfaces = []
        for element in cli_output:
            ip_address = element.get("ip_address")
            if ip_address != "Unknown":
                address = ipaddress.IPv4Address(ip_address.split("/")[0])
                # Removes Management, Loopback, and intersite interfaces from the list of
                # MPLS enabled interfaces (Loopback exclusion works around an IOS XRv bug:
                # a Loopback interface entered in mpls ldp configuration mode makes it hang).
                if address not in MANAGEMENT_NETWORK and address not in LOOPBACK_NETWORK and not is_intersite_address(address):
                    mpls_interfaces.append(element.get("interface"))
            else:
                pass

        if len(mpls_interfaces) != 0:
            mpls_commands.append("mpls oam")
            mpls_commands.append("mpls ldp")
            for interface in mpls_interfaces:
                mpls_commands.append("interface " + interface)
            mpls_commands.append("exit")
            # This is needed to be entered after all the mpls enabled interfaces entered (IOS XRv BUG).
            # This is needed to enable label assignment for 32/ routes in routing table.
            # IOS XR do NOT show interface Loopback (with /32) in configuration.
            mpls_commands.append("address-family ipv4")
            mpls_commands.append("label local allocate for host-routes")
        else:
            pass
    else:
        pass

    # Sends configuration commands.
    if len(mpls_commands) == 0:
        pass
    else:
        netmiko_send_config(task, config_commands=mpls_commands)
        netmiko_commit(task)

    return mpls_commands


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
