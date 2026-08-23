from netmiko import ConnectHandler
import concurrent.futures
from inventory import NetmikoDeviceDB, NETMIKO_DB_PATH
from topology import Topology, TOPOLOGY, NETWORKS
from variables import DEVICES, EBGP, TOPOLOGY_INTERFACE_XE, TOPOLOGY_INTERFACE_XR
#import logging
#logging.basicConfig(filename="netmiko_debug.log", level=logging.DEBUG)
#logger = logging.getLogger("netmiko")


topology = Topology(TOPOLOGY, NETWORKS, EBGP)


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

    # Finds eBGP peer.
    peer = topology.ebgp_peer(device_id)

    # BGP commands.
    bgp_commands = []
    if peer is not None:
        own_asn, peer_asn, peer_id = peer
        peer_loopback = topology.loopback_address(peer_id).split("/")[0]

        # The link — and this device's own subinterface on it — were already
        # created by 003_ipv4_setup.py, since it's a normal TOPOLOGY entry
        # now (just one that happens to cross an AS boundary). This script
        # only needs to find which entry it is.
        link = topology.link_for_ebgp_peer(device_id)
        tag = topology.dot1q_tag(device_id, link)
        peer_link_ip = topology.ip_address(peer_id, link).split("/")[0]
        exit_interface = TOPOLOGY_INTERFACE_XE[0] + "." + tag

        # Static route to the peer's loopback, exiting out that subinterface, with
        # an explicit next-hop IP. An interface-only static route works on true p2p media,
        # but this is a dot1Q subinterface on shared Ethernet, so IOS treats it as on-link
        # and ARPs for the destination itself — which only resolves with proxy ARP enabled
        # on the peer, which nothing here sets up. Both ends compute the peer's link IP the
        # same deterministic way, so no lookup/proxy-ARP dependency is needed.
        bgp_commands.append("ip route " + peer_loopback + " 255.255.255.255 " + exit_interface + " " + peer_link_ip)

        bgp_commands.append("router bgp " + own_asn)
        bgp_commands.append("neighbor " + peer_loopback + " remote-as " + peer_asn)
        bgp_commands.append("neighbor " + peer_loopback + " update-source Loopback0")
        bgp_commands.append("neighbor " + peer_loopback + " ebgp-multihop 2")
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

    # Finds eBGP peer.
    peer = topology.ebgp_peer(device_id)

    # BGP commands.
    bgp_commands = []
    if peer is not None:
        own_asn, peer_asn, peer_id = peer
        peer_loopback = topology.loopback_address(peer_id).split("/")[0]

        # The link — and this device's own subinterface on it — were already
        # created by 003_ipv4_setup.py — see the comment in the XE branch above.
        link = topology.link_for_ebgp_peer(device_id)
        tag = topology.dot1q_tag(device_id, link)
        peer_link_ip = topology.ip_address(peer_id, link).split("/")[0]
        exit_interface = TOPOLOGY_INTERFACE_XR[0] + "." + tag

        # Static route to the peer's loopback, exiting out that same subinterface, with
        # an explicit next-hop IP — see the matching comment in the XE branch above.
        bgp_commands.append("router static")
        bgp_commands.append("address-family ipv4 unicast")
        bgp_commands.append(peer_loopback + "/32 " + exit_interface + " " + peer_link_ip)

        bgp_commands.append("router bgp " + own_asn)
        bgp_commands.append("address-family ipv4 unicast")
        bgp_commands.append("neighbor " + peer_loopback)
        bgp_commands.append("remote-as " + peer_asn)
        bgp_commands.append("update-source Loopback0")
        bgp_commands.append("ebgp-multihop 2")
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
