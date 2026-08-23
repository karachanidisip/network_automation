from pathlib import Path
import asyncio
from scrapli.driver.core import AsyncIOSXEDriver, AsyncIOSXRDriver
import datetime
import subprocess
from inventory import ScrapliDeviceDB, SCRAPLI_DB_PATH
#from scrapli.logging import enable_basic_logging
#enable_basic_logging(file=True, level="debug")


# Paths
REPOSITORY_PATH = Path(__file__).resolve().parent / "001.REPOSITORY/"


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

    # Sends execution commands.
    exec_output = await conn.send_command("show running-config")

    # Creates a "hostname_startup-config.cfg" file (if the specified file does not exist) and overwrites any existing content (if there is).
    file_name = host_hostname + "_startup-config.cfg"
    complete_name = REPOSITORY_PATH / file_name
    with open(f"{complete_name}", "w") as f:
        # Removes initial non configuration lines and exclamation marks in order to comply with IOS/IOS-XE/IOS-XR startup-config format.

        exclamation_mark_counter = 0
        clear_config = ""

        for line in exec_output.result.splitlines():
            if line.startswith("!"):
                exclamation_mark_counter += 1
            elif exclamation_mark_counter >= 1:
                clear_config += line + "\n"

        f.write(clear_config)

    # Disconnects from host.
    await conn.close()

    message = "There is a new startup-config file for the " + host_hostname + " host!!!"
    return message


async def xr(INPUT_DICT_PER_HOST):
    # Connects to the host using Scrapli (Telnet/SSH).
    # timeout_ops=120, max wait for a single command/interaction to complete
    # timeout_transport=120, max wait at the connection/channel level (socket open, no data)
    conn = AsyncIOSXRDriver(transport="asynctelnet", timeout_ops=120, timeout_transport=120, **INPUT_DICT_PER_HOST)
    await conn.open()

    # Finds host hostname.
    prompt = await conn.get_prompt()
    host_hostname = prompt.split(":")[-1].rstrip("#>")

    # Sends execution commands.
    exec_output = await conn.send_command("show running-config")

    # Creates a "hostname_startup-config.cfg" file (if the specified file does not exist) and overwrites any existing content (if there is).
    file_name = host_hostname + "_startup-config.cfg"
    complete_name = REPOSITORY_PATH / file_name
    with open(f"{complete_name}", "w") as f:
        # Removes initial non configuration lines and exclamation marks in order to comply with IOS/IOS-XE/IOS-XR startup-config format.

        exclamation_mark_counter = 0
        clear_config = ""

        for line in exec_output.result.splitlines():
            if line.startswith("!"):
                exclamation_mark_counter += 1
            elif exclamation_mark_counter >= 1:
                clear_config += line + "\n"

        f.write(clear_config)

    # Disconnects from host.
    await conn.close()

    message = "There is a new startup-config file for the " + host_hostname + " host!!!"
    return message


def git():
    # YearMonthDate.
    ymd = datetime.date.today()
    date = ymd.strftime("%Y%m%d")

    # HourMinuteSecond.
    hms = datetime.datetime.now()
    time = hms.strftime("%H%M%S")

    user_comment = input("\033[1;93m Enter a comment about the changes \n: \033[0m")

    commit_name = date + "-" + time + "-" + user_comment

    # GIT add command.
    git_add = subprocess.run(["git", "add", "."], cwd = REPOSITORY_PATH, capture_output=True, text=True)
    print(git_add.stdout)
    print(git_add.stderr)

    # GIT commit command.
    git_commit = subprocess.run(["git", "commit", "-m", commit_name], cwd = REPOSITORY_PATH, capture_output=True, text=True)
    print(git_commit.stdout)
    print(git_commit.stderr)


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
    git()
