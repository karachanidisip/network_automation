import datetime
import time
import asyncio
from scrapli.driver.core import AsyncIOSXEDriver, AsyncIOSXRDriver
from inventory import ScrapliDeviceDB, SCRAPLI_DB_PATH
#from scrapli.logging import enable_basic_logging
#enable_basic_logging(file=True, level="debug")


# Devices to be configured
DEVICES = ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5", "10.0.0.6", "10.0.0.7", "10.0.0.8", "10.0.0.9", "10.0.0.10",
           "10.0.0.11", "10.0.0.12", "10.0.0.13", "10.0.0.14"]


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

    # Copies startup-config.
    events = [
    (f"copy tftp://10.0.0.100/{host_hostname}_startup-config.cfg unix:", "Destination", False),
    ("", "Accessing", False),
    ("", "", True)
    ]
    # The sending "" just sends ENTER (no content), so "" alone means "press Enter, nothing else."
    # The receiving "#" matches literally if a "#" character appears ANYWHERE in the reply, this usually lands on a normal device prompt (eg R1#, R1(config)#), not a real prompt check.
    # The receiving "" does NOT mean "match anything", it only matches a properly-formatted device prompt line (eg R1#, R1(config)#).
    # The True value in the final tuple means "End of Interaction", signals to scrapli that this is the final step of the interactive channel session.
    response = await conn.send_interactive(events)
    message_1 = host_hostname + ": TFTP copy step - unexpected output, check manually."
    if "Loading" in response.result:
        message_1 = host_hostname + " has copied a startup-config.cfg from TFTP server!!!"
    else:
        pass

    # Replaces startup-config.
    events = [
    (f"configure replace unix:{host_hostname}_startup-config.cfg", "This", False),
    ("Y", "", True),
    ]
    # The sending "" just sends ENTER (no content), so "" alone means "press Enter, nothing else."
    # The receiving "#" matches literally if a "#" character appears ANYWHERE in the reply, this usually lands on a normal device prompt (eg R1#, R1(config)#), not a real prompt check.
    # The receiving "" does NOT mean "match anything", it only matches a properly-formatted device prompt line (eg R1#, R1(config)#).
    # The True value in the final tuple means "End of Interaction", signals to scrapli that this is the final step of the interactive channel session.
    response = await conn.send_interactive(events)
    message_2 = host_hostname + ": configure replace step - unexpected output, check manually."
    if "Rollback Done" in response.result:
        message_2 = host_hostname + " has performed a Rollback!!!"
    else:
        pass

    # Deletes startup-config.
    try:
        await conn.close()
    except Exception:
        pass
    await asyncio.sleep(10)
    conn_new = AsyncIOSXEDriver(transport="asynctelnet", **INPUT_DICT_PER_HOST)
    await conn_new.open()
    await conn_new.send_command("")

    events = [(f"delete unix:{host_hostname}_startup-config.cfg", "Delete", False),
    ("", "Delete", False),
    ("", "", True)
    ]
    # The sending "" just sends ENTER (no content), so "" alone means "press Enter, nothing else."
    # The receiving "#" matches literally if a "#" character appears ANYWHERE in the reply, this usually lands on a normal device prompt (eg R1#, R1(config)#), not a real prompt check.
    # The receiving "" does NOT mean "match anything", it only matches a properly-formatted device prompt line (eg R1#, R1(config)#).
    # The True value in the final tuple means "End of Interaction", signals to scrapli that this is the final step of the interactive channel session.
    response = await conn_new.send_interactive(events)
    if True:
        message_3 = host_hostname + " has deleted the downloaded startup-config.cfg from TFTP server!!!"
    else:
        pass

    # Saves the running-config to the startup-config.
    await conn_new.send_command("write memory")

    # Disconnects from host.
    await conn_new.close()

    return message_1, message_2, message_3


async def xr(INPUT_DICT_PER_HOST):
    # Connects to the host using Scrapli (Telnet/SSH).
    # timeout_ops=120, max wait for a single command/interaction to complete
    # timeout_transport=120, max wait at the connection/channel level (socket open, no data)
    conn = AsyncIOSXRDriver(transport="asynctelnet", timeout_ops=120, timeout_transport=120, **INPUT_DICT_PER_HOST)
    await conn.open()

    # Finds host hostname.
    prompt = await conn.get_prompt()
    host_hostname = prompt.split(":")[-1].rstrip("#>")

    # Copies startup-config.
    events = [
    (f"copy tftp://10.0.0.100/{host_hostname}_startup-config.cfg nvram:", "Destination", False),
    ("", "", False),
    ("", "", True)
    ]
    # The sending "" just sends ENTER (no content), so "" alone means "press Enter, nothing else."
    # The receiving "#" matches literally if a "#" character appears ANYWHERE in the reply, this usually lands on a normal device prompt (eg R1#, R1(config)#), not a real prompt check.
    # The receiving "" does NOT mean "match anything", it only matches a properly-formatted device prompt line (eg R1#, R1(config)#).
    # The True value in the final tuple means "End of Interaction", signals to scrapli that this is the final step of the interactive channel session.
    response = await conn.send_interactive(events)
    message_1 = host_hostname + ": TFTP copy step - unexpected output, check manually."
    if "Accessing" in response.result:
        message_1 = host_hostname + " has copied a startup-config.cfg from TFTP server!!!"
    else:
        pass

    # Replaces startup-config.
    await conn.acquire_priv("configuration")
    await conn.send_configs([f"load nvram:/{host_hostname}_startup-config.cfg"])
    events = [
    ("commit replace", "Do", False),
    ("yes", "", True),
    ]
    # The sending "" just sends ENTER (no content), so "" alone means "press Enter, nothing else."
    # The receiving "#" matches literally if a "#" character appears ANYWHERE in the reply, this usually lands on a normal device prompt (eg R1#, R1(config)#), not a real prompt check.
    # The receiving "" does NOT mean "match anything", it only matches a properly-formatted device prompt line (eg R1#, R1(config)#).
    # The True value in the final tuple means "End of Interaction", signals to scrapli that this is the final step of the interactive channel session.
    response = await conn.send_interactive(events, privilege_level="configuration")
    message_2 = host_hostname + ": configure replace step - unexpected output, check manually."
    if "Do" in response.result:
        message_2 = host_hostname + " has performed a Rollback!!!"
    else:
        pass

    # Deletes startup-config.

    await conn.acquire_priv("privilege_exec")
    events = [
    (f"delete nvram:{host_hostname}_startup-config.cfg", "Delete", False),
    ("", "", True)
    ]
    # The sending "" just sends ENTER (no content), so "" alone means "press Enter, nothing else."
    # The receiving "#" matches literally if a "#" character appears ANYWHERE in the reply, this usually lands on a normal device prompt (eg R1#, R1(config)#), not a real prompt check.
    # The receiving "" does NOT mean "match anything", it only matches a properly-formatted device prompt line (eg R1#, R1(config)#).
    # The True value in the final tuple means "End of Interaction", signals to scrapli that this is the final step of the interactive channel session.
    response = await conn.send_interactive(events)
    if True:
        message_3 = host_hostname + " has deleted the downloaded startup-config.cfg from TFTP server!!!"
    else:
        pass

    # Saves the running-config to the startup-config.
    await conn.send_configs(["commit"])

    # Disconnects from host.
    await conn.close()

    return message_1, message_2, message_3


async def xe_xr(host):
    async with sem:
        if host.get("platform") == "cisco_iosxe":
            host.pop("platform")
            returned_by_xe = await xe(host)
            print(returned_by_xe[0])
            print(returned_by_xe[1])
            print(returned_by_xe[2])
        elif host.get("platform") == "cisco_iosxr":
            host.pop("platform")
            returned_by_xr = await xr(host)
            print(returned_by_xr[0])
            print(returned_by_xr[1])
            print(returned_by_xr[2])
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
