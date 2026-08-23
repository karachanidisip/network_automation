import asyncio
from scrapli.driver.core import AsyncIOSXEDriver, AsyncIOSXRDriver
from inventory import ScrapliDeviceDB, SCRAPLI_DB_PATH
from topology import Topology
from variables import (DEVICES, MANAGEMENT_INTERFACE_XE, MANAGEMENT_INTERFACE_XR,
                        TOPOLOGY_INTERFACE_XE, TOPOLOGY_INTERFACE_XR, LOOPBACK_INTERFACE,
                        TOPOLOGY, NETWORKS)
#from scrapli.logging import enable_basic_logging
#enable_basic_logging(file=True, level="debug")


topology = Topology(TOPOLOGY, NETWORKS)


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
    await conn.acquire_priv("configuration")
    await conn.send_configs(commands)

    # Saves the running-config to the startup-config.
    await conn.send_command("write memory")

    # Disconnects from host.
    await conn.close()

    return commands


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
    await conn.acquire_priv("configuration")
    await conn.send_configs(commands)

    # Saves the running-config to the startup-config.
    await conn.send_configs(["commit"])

    # Disconnects from host.
    await conn.close()

    return commands


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
