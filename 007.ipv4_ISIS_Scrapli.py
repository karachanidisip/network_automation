import asyncio
from scrapli.driver.core import AsyncIOSXEDriver, AsyncIOSXRDriver
from inventory import ScrapliDeviceDB, SCRAPLI_DB_PATH
import ipaddress
from topology import Topology
from variables import DEVICES, TOPOLOGY, NETWORKS, EBGP
#from scrapli.logging import enable_basic_logging
#enable_basic_logging(file=True, level="debug")


# Networks participating in ISIS process (intrasite links only — see 004 for
# why EBGP-declared boundary links are excluded here)
topology = Topology(TOPOLOGY, NETWORKS, EBGP).intrasite_topology()
ISIS_NETWORKS_AND_LEVELS = topology.topology_networks_with_isis_levels()


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

    # Finds ISIS SYSTEM_ID.
    router_id = ""
    for element in host_hostname:
        if element.isdigit():
            router_id = router_id + element
        else:
            pass
    device_id = int(router_id)
    system_id = "0000.0000." + ((4 - len(router_id))*"0" + router_id)

    # Finds ISIS AREA and TAG.
    raw_area = topology.isis_area(device_id)
    area = (4 - len(raw_area)) * "0" + raw_area
    isis_tag = topology.routing_process_tag(device_id)

    # Finds ISIS NET.
    net = "49." + area + "." + system_id + ".00"

    # Finds ISIS interfaces.
    isis_interfaces_levels = []
    for element in interface_and_ipv4:
        ip_address = ipaddress.IPv4Address(element[1])
        for item in ISIS_NETWORKS_AND_LEVELS:
            ip_network = ipaddress.IPv4Network(item[0])
            if ip_address in ip_network:
                isis_interfaces_levels.append([element[0], item[1]])
            else:
                pass

    # ISIS commands.
    isis_commands = []
    if len(isis_interfaces_levels) != 0:
        isis_commands.append("router isis " + isis_tag)
        isis_commands.append("net " + net)
        for element in isis_interfaces_levels:
            isis_commands.append("interface " + element[0])
            isis_commands.append("ip router isis " + isis_tag)
            if element[1] == "1":
                isis_commands.append("isis circuit-type level-1")
            elif element[1] == "2":
                isis_commands.append("isis circuit-type level-2-only")
            else:
                pass
    else:
        pass

    # Sends configuration commands.
    await conn.acquire_priv("configuration")
    await conn.send_configs(isis_commands)

    # Saves the running-config to the startup-config.
    await conn.send_command("write memory")

    # Disconnects from host.
    await conn.close()

    # Return.
    return isis_commands


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

    # Finds ISIS SYSTEM_ID.
    router_id = ""
    for element in host_hostname:
        if element.isdigit():
            router_id = router_id + element
        else:
            pass
    device_id = int(router_id)
    system_id = "0000.0000." + ((4 - len(router_id))*"0" + router_id)

    # Finds ISIS AREA and TAG.
    raw_area = topology.isis_area(device_id)
    area = (4 - len(raw_area)) * "0" + raw_area
    isis_tag = topology.routing_process_tag(device_id)

    # Finds ISIS NET.
    net = "49." + area + "." + system_id + ".00"

    # Finds ISIS interfaces.
    isis_interfaces_levels = []
    for element in interface_and_ipv4:
        ip_address = ipaddress.IPv4Address(element[1].split("/")[0])
        for item in ISIS_NETWORKS_AND_LEVELS:
            ip_network = ipaddress.IPv4Network(item[0])
            if ip_address in ip_network:
                isis_interfaces_levels.append([element[0], item[1]])
            else:
                pass

    # ISIS commands.
    isis_commands = []
    if len(isis_interfaces_levels) != 0:
        isis_commands.append("router isis " + isis_tag)
        isis_commands.append("net " + net)
        isis_commands.append("address-family ipv4 unicast")
        for element in isis_interfaces_levels:
            isis_commands.append("interface " + element[0])
            isis_commands.append("address-family ipv4 unicast")
            if element[1] == "1":
                isis_commands.append("circuit-type level-1")
            elif element[1] == "2":
                isis_commands.append("circuit-type level-2-only")
            else:
                pass
    else:
        pass

    # Sends configuration commands.
    await conn.acquire_priv("configuration")
    await conn.send_configs(isis_commands)

    # Saves the running-config to the startup-config.
    await conn.send_configs(["commit"])

    # Disconnects from host.
    await conn.close()

    # Return.
    return isis_commands


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
