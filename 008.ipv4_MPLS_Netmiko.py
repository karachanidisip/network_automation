from netmiko import ConnectHandler
import ipaddress
import concurrent.futures
from inventory import NetmikoDeviceDB, NETMIKO_DB_PATH
from topology import Topology
from variables import DEVICES, MANAGEMENT_INTERFACE_XE, MANAGEMENT_INTERFACE_XR, NETWORKS, MPLS, TOPOLOGY, EBGP
#import logging
#logging.basicConfig(filename="netmiko_debug.log", level=logging.DEBUG)
#logger = logging.getLogger("netmiko")


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
    net_connect.send_config_set(mpls_commands)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Disconnects from host.
    net_connect.disconnect()

    # Return.
    return mpls_commands


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
    net_connect.send_config_set(mpls_commands)

    # Saves the running-config to the startup-config.
    net_connect.commit()

    # Disconnects from host.
    net_connect.disconnect()

    # Return.
    return mpls_commands


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
