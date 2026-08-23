import asyncio
from scrapli.driver.core import AsyncIOSXEDriver, AsyncIOSXRDriver
from inventory import ScrapliDeviceDB, SCRAPLI_DB_PATH
import ipaddress
from topology import Topology
from variables import DEVICES, TOPOLOGY, NETWORKS, EBGP
#from scrapli.logging import enable_basic_logging
#enable_basic_logging(file=True, level="debug")


# Networks participating in RIP process (intrasite links only — EBGP-declared
# boundary links are excluded so an AS-boundary link, whether or not it's
# been provisioned yet, is never picked up by this IGP scan)
topology = Topology(TOPOLOGY, NETWORKS, EBGP).intrasite_topology()
RIP_NETWORKS = topology.topology_networks()


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

    # Finds ipv4 interfaces.
    response = await conn.send_command("show interfaces")
    structured_data = response.textfsm_parse_output()
    interface_and_ipv4 =[]
    for element in structured_data:
        if element.get("interface") != "Ethernet0/0" and element.get("ip_address") != "":
            interface_and_ipv4.append([element.get("interface"), element.get("ip_address"), element.get("prefix_length")])
        else:
            pass

    # Finds RIP networks.
    rip_networks = []
    for element in interface_and_ipv4:
        ip_address = ipaddress.IPv4Address(element[1])
        for item in RIP_NETWORKS:
            ip_network = ipaddress.IPv4Network(item)
            if ip_address in ip_network:
                rip_networks.append(element[1])
            else:
                pass

    # Convert RIP networks to CASSFUL networks.
    rip_networks_classful = []
    for element in rip_networks:
        first_octet = int(element.split(".")[0])
        if first_octet < 128:
            item = element.split(".")[0] + ".0.0.0"
            if item not in rip_networks_classful:
                rip_networks_classful.append(item)
            else:
                pass
        elif first_octet < 192:
            item = element.split(".")[0] + "." + element.split(".")[1] + ".0.0"
            if item not in rip_networks_classful:
                rip_networks_classful.append(item)
            else:
                pass
        elif first_octet < 224:
            item = element.split(".")[0] + "." + element.split(".")[1] + "." + element.split(".")[2] + ".0"
            if item not in rip_networks_classful:
                rip_networks_classful.append(item)
            else:
                pass
        else:
            pass

    # RIP commands.
    rip_commands = []
    if len(rip_networks_classful) != 0:
        rip_commands.append("router rip")
        rip_commands.append("no auto-summary")
        rip_commands.append("version 2")
        for element in rip_networks_classful:
            rip_commands.append("network " + element)
    else:
        pass

    # Sends configuration commands.
    await conn.acquire_priv("configuration")
    await conn.send_configs(rip_commands)

    # Saves the running-config to the startup-config.
    await conn.send_command("write memory")

    # Disconnects from host.
    await conn.close()

    # Return.
    return rip_commands


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

    # Finds ipv4 interfaces.
    response = await conn.send_command("show interfaces")
    structured_data = response.textfsm_parse_output()
    interface_and_ipv4 =[]
    for element in structured_data:
        if element.get("interface") != "MgmtEth0/0/CPU0/0" and element.get("ip_address") != "Unknown":
            interface_and_ipv4.append([element.get("interface"), element.get("ip_address")])
        else:
            pass

    # Finds RIP interfaces.
    rip_interfaces = []
    for element in interface_and_ipv4:
        ip_address = ipaddress.IPv4Address(element[1].split("/")[0])
        for item in RIP_NETWORKS:
            ip_network = ipaddress.IPv4Network(item)
            if ip_address in ip_network:
                rip_interfaces.append(element[0])
            else:
                pass

    # RIP commands.
    rip_commands = []
    if len(rip_interfaces) != 0:
        rip_commands.append("router rip")
        rip_commands.append("no auto-summary")
        for element in rip_interfaces:
            rip_commands.append("interface " + element)
            rip_commands.append("send version 2")
            rip_commands.append("receive version 2")
    else:
        pass

    # Sends configuration commands.
    await conn.acquire_priv("configuration")
    await conn.send_configs(rip_commands)

    # Saves the running-config to the startup-config.
    await conn.send_configs(["commit"])

    # Disconnects from host.
    await conn.close()

    # Return.
    return rip_commands


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
