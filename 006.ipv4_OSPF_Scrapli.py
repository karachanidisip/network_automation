import asyncio
from scrapli.driver.core import AsyncIOSXEDriver, AsyncIOSXRDriver
from inventory import ScrapliDeviceDB, SCRAPLI_DB_PATH
import ipaddress
from topology import Topology
from variables import DEVICES, TOPOLOGY, NETWORKS, EBGP
#from scrapli.logging import enable_basic_logging
#enable_basic_logging(file=True, level="debug")


# Networks participating in OSPF process (intrasite links only — see 004 for
# why EBGP-declared boundary links are excluded here)
topology = Topology(TOPOLOGY, NETWORKS, EBGP).intrasite_topology()
OSPF_NETWORKS_AND_AREAS = topology.topology_networks_with_ospf_areas()


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

    # Finds OSPF networks.
    ospf_networks_areas = []
    for element in interface_and_ipv4:
        ip_address = ipaddress.IPv4Address(element[1])
        for item in OSPF_NETWORKS_AND_AREAS:
            ip_network = ipaddress.IPv4Network(item[0])
            if ip_address in ip_network and item not in ospf_networks_areas:
                ospf_networks_areas.append([item[0], item[1]])
            else:
                pass

    # Convert OSPF networks to NETWORK WILDCARD statements.
    ospf_networks_wildcards_areas = []
    for element in ospf_networks_areas:
        network_mask = ipaddress.IPv4Network(element[0], strict=True)
        network = network_mask.network_address
        mask = network_mask.netmask
        wildcard_split_list = []
        for x in str(mask).split("."):
            y = str(255 - int(x))
            wildcard_split_list.append(y)
        wildcard = ".".join(wildcard_split_list)
        ospf_statement = str(network) + " " + wildcard + " area " + element[1]
        ospf_networks_wildcards_areas.append(ospf_statement)

    # Finds ID.
    device_id_digits = ""
    for character in host_hostname:
        if character.isdigit():
            device_id_digits += character
    device_id = int(device_id_digits)
    ospf_process = topology.routing_process_tag(device_id)

    # OSPF commands.
    ospf_commands = []
    if len(ospf_networks_wildcards_areas) != 0:
        ospf_commands.append("router ospf " + ospf_process)
        for element in ospf_networks_wildcards_areas:
            ospf_commands.append("network " + element)
    else:
        pass

    # Sends configuration commands.
    await conn.acquire_priv("configuration")
    await conn.send_configs(ospf_commands)

    # Saves the running-config to the startup-config.
    await conn.send_command("write memory")

    # Disconnects from host.
    await conn.close()

    # Return.
    return ospf_commands


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

    # Finds OSPF interfaces.
    ospf_interfaces_areas = []
    for element in interface_and_ipv4:
        ip_address = ipaddress.IPv4Address(element[1].split("/")[0])
        for item in OSPF_NETWORKS_AND_AREAS:
            ip_network = ipaddress.IPv4Network(item[0])
            if ip_address in ip_network:
                ospf_interfaces_areas.append([element[0], item[1]])
            else:
                pass

    # Finds ID.
    device_id_digits = ""
    for character in host_hostname:
        if character.isdigit():
            device_id_digits += character
    device_id = int(device_id_digits)
    ospf_process = topology.routing_process_tag(device_id)

    # OSPF commands.
    ospf_commands = []
    if len(ospf_interfaces_areas) != 0:
        ospf_commands.append("router ospf " + ospf_process)
        for element in ospf_interfaces_areas:
            ospf_commands.append("area " + element[1])
            ospf_commands.append("interface " + element[0])
    else:
        pass

    # Sends configuration commands.
    await conn.acquire_priv("configuration")
    await conn.send_configs(ospf_commands)

    # Saves the running-config to the startup-config.
    await conn.send_configs(["commit"])

    # Disconnects from host.
    await conn.close()

    # Return.
    return ospf_commands


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
