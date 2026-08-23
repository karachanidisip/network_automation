import asyncio
from scrapli.driver.core import AsyncIOSXEDriver, AsyncIOSXRDriver
from inventory import ScrapliDeviceDB, SCRAPLI_DB_PATH
from topology import Topology, TOPOLOGY, NETWORKS
from variables import DEVICES, EBGP, TOPOLOGY_INTERFACE_XE, TOPOLOGY_INTERFACE_XR
#from scrapli.logging import enable_basic_logging
#enable_basic_logging(file=True, level="debug")


topology = Topology(TOPOLOGY, NETWORKS, EBGP)


# Caps concurrent device connections at 4 (attacks TFTP server and QEMU limitations)
sem = asyncio.Semaphore(4)


async def xe(INPUT_DICT_PER_HOST):
    # Connects to the host using Scrapli (Telnet/SSH).
    # timeout_ops=120, max wait for a single command/interaction to complete
    # timeout_transport=120, max wait at the connection/channel level (socket open, no data)
    conn = AsyncIOSXEDriver(transport="asynctelnet", timeout_ops=120, timeout_transport=120, **INPUT_DICT_PER_HOST)
    await conn.open()

    # Finds host hostname.
    prompt = await conn.get_prompt()
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
    await conn.acquire_priv("configuration")
    await conn.send_configs(bgp_commands)

    # Saves the running-config to the startup-config.
    await conn.send_command("write memory")

    # Disconnects from host.
    await conn.close()

    # Return.
    return bgp_commands


async def xr(INPUT_DICT_PER_HOST):
    # Connects to the host using Scrapli (Telnet/SSH).
    # timeout_ops=120, max wait for a single command/interaction to complete
    # timeout_transport=120, max wait at the connection/channel level (socket open, no data)
    conn = AsyncIOSXRDriver(transport="asynctelnet", timeout_ops=120, timeout_transport=120, **INPUT_DICT_PER_HOST)
    await conn.open()
    await asyncio.sleep(60)

    # Finds host hostname.
    prompt = await conn.get_prompt()
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
    await conn.acquire_priv("configuration")
    await conn.send_configs(bgp_commands)

    # Saves the running-config to the startup-config.
    await conn.send_configs(["commit"])

    # Disconnects from host.
    await conn.close()

    # Return.
    return bgp_commands


async def xe_xr(host):
    async with sem:
        if host.get("platform") == "cisco_iosxe":
            host.pop("platform")
            returned_by_xe = await xe(host)
            print(returned_by_xe)
        elif host.get("platform") == "cisco_iosxr":
            host.pop("platform")
            returned_by_xr = await xr(host)
            print(returned_by_xr)
        else:
            pass


async def main():
    devices = ScrapliDeviceDB(SCRAPLI_DB_PATH).get_multiple_devices(DEVICES)
    results = await asyncio.gather(*(xe_xr(d) for d in devices), return_exceptions=True)
    for device, result in zip(devices, results):
        if isinstance(result, Exception):
            print(f"[ERROR] {device.get('host')}: {result!r}")


if __name__ == "__main__":
    asyncio.run(main())
