from netmiko import ConnectHandler
import concurrent.futures
from inventory import NetmikoDeviceDB, NETMIKO_DB_PATH
from topology import Topology, TOPOLOGY, NETWORKS
from variables import DEVICES, IBGP
#import logging
#logging.basicConfig(filename="netmiko_debug.log", level=logging.DEBUG)
#logger = logging.getLogger("netmiko")


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
    net_connect.send_config_set(bgp_commands)

    # Saves the running-config to the startup-config.
    net_connect.save_config()

    # Disconnects from host.
    net_connect.disconnect()

    # Return.
    return bgp_commands


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
    net_connect.send_config_set(bgp_commands)

    # Saves the running-config to the startup-config.
    net_connect.commit()

    # Disconnects from host.
    net_connect.disconnect()

    # Return.
    return bgp_commands


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
