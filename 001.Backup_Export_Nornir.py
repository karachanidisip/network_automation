from pathlib import Path
import datetime
import subprocess
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


REPOSITORY_PATH = Path(__file__).resolve().parent / "001.REPOSITORY/"


def xe(task):
    net_connect = task.host.get_connection("netmiko", task.nornir.config)
    net_connect.enable()
    host_hostname = net_connect.find_prompt().rstrip("#>")
    output = task.run(task=netmiko_send_command, command_string="show running-config")
    text = output.result
    file_name = host_hostname + "_startup-config.cfg"
    complete_name = REPOSITORY_PATH / file_name
    with open(f"{complete_name}", "w") as f:
        exclamation_mark_counter = 0
        clear_config = ""
        for line in text.splitlines():
            if line.startswith("!"):
                exclamation_mark_counter += 1
            elif exclamation_mark_counter >= 1:
                clear_config += line + "\n"
        f.write(clear_config)
    print(f"{host_hostname} backup is extracted!!!")


def xr(task):
    net_connect = task.host.get_connection("netmiko", task.nornir.config)
    net_connect.enable()
    host_hostname = net_connect.find_prompt().split(":")[-1].rstrip("#>")
    output = task.run(task=netmiko_send_command, command_string="show running-config")
    text = output.result
    file_name = host_hostname + "_startup-config.cfg"
    complete_name = REPOSITORY_PATH / file_name
    with open(f"{complete_name}", "w") as f:
        exclamation_mark_counter = 0
        clear_config = ""
        for line in text.splitlines():
            if line.startswith("!"):
                exclamation_mark_counter += 1
            elif exclamation_mark_counter >= 1:
                clear_config += line + "\n"
        f.write(clear_config)
    print(f"{host_hostname} backup is extracted!!!")


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

if __name__ == "__main__":
    main()
    git()
