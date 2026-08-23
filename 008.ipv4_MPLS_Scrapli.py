import asyncio
from scrapli.driver.core import AsyncIOSXEDriver, AsyncIOSXRDriver
from inventory import ScrapliDeviceDB, SCRAPLI_DB_PATH
import ipaddress
from topology import Topology
from variables import DEVICES, MANAGEMENT_INTERFACE_XE, MANAGEMENT_INTERFACE_XR, NETWORKS, MPLS, TOPOLOGY, EBGP
#from scrapli.logging import enable_basic_logging
#enable_basic_logging(file=True, level="debug")


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


# Caps concurrent device connections at 4 (attacks TFTP server and QEMU limitations)
sem = asyncio.Semaphore(4)


def is_intersite_address(ip_address):
    """True if ip_address falls inside any INTERSITE_NETWORKS subnet."""
    for network in INTERSITE_NETWORKS:
        if ip_address in network:
            return True
    return False


MPLS_DEVICE_IDS = []
for d in MPLS["devices_ids"].split("-"):
    MPLS_DEVICE_IDS.append(int(d))


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

    # MPLS commands.
    mpls_commands = []
    if device_id in MPLS_DEVICE_IDS:
        # Finds ip enabled interfaces.
        response = await conn.send_command("show interfaces")
        structured_data = response.textfsm_parse_output()
        mpls_interfaces = []
        for element in structured_data:
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
    await conn.acquire_priv("configuration")
    await conn.send_configs(mpls_commands)

    # Saves the running-config to the startup-config.
    await conn.send_command("write memory")

    # Disconnects from host.
    await conn.close()

    # Return.
    return mpls_commands


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

    # MPLS commands.
    mpls_commands = []
    if device_id in MPLS_DEVICE_IDS:
        # Finds ip enabled interfaces.
        response = await conn.send_command("show interfaces")
        structured_data = response.textfsm_parse_output()
        mpls_interfaces = []
        for element in structured_data:
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
    await conn.acquire_priv("configuration")
    await conn.send_configs(mpls_commands)

    # Saves the running-config to the startup-config.
    await conn.send_configs(["commit"])

    # Disconnects from host.
    await conn.close()

    # Return.
    return mpls_commands


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
