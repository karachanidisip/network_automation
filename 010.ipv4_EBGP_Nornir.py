from topology import Topology, TOPOLOGY, NETWORKS
from variables import DEVICES, EBGP, TOPOLOGY_INTERFACE_XE, TOPOLOGY_INTERFACE_XR
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


topology = Topology(TOPOLOGY, NETWORKS, EBGP)


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
