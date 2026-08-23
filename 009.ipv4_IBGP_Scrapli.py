import asyncio
from scrapli.driver.core import AsyncIOSXEDriver, AsyncIOSXRDriver
from inventory import ScrapliDeviceDB, SCRAPLI_DB_PATH
from topology import Topology, TOPOLOGY, NETWORKS
from variables import DEVICES, IBGP
#from scrapli.logging import enable_basic_logging
#enable_basic_logging(file=True, level="debug")


topology = Topology(TOPOLOGY, NETWORKS)


# Caps concurrent device connections at 4 (attacks TFTP server and QEMU limitations)
sem = asyncio.Semaphore(4)


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
