import time
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


# Devices to be configured
DEVICES = ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5", "10.0.0.6", "10.0.0.7", "10.0.0.8", "10.0.0.9", "10.0.0.10",
           "10.0.0.11", "10.0.0.12", "10.0.0.13", "10.0.0.14"]


def xe(task):
    net_connect = task.host.get_connection("netmiko", task.nornir.config)
    net_connect.enable()
    host_hostname = net_connect.find_prompt().rstrip("#>")
    output = ""
    output += net_connect.send_command_timing(f"copy tftp://10.0.0.100/{host_hostname}_startup-config.cfg unix:", read_timeout=10)
    output += net_connect.send_command_timing("\n")
    output += net_connect.send_command_timing("\n")
    output += net_connect.send_command_timing(f"configure replace unix:{host_hostname}_startup-config.cfg", read_timeout=30)
    output += net_connect.send_command_timing("Y")
    output += net_connect.send_command_timing(f"delete unix:{host_hostname}_startup-config.cfg", read_timeout=10)
    output += net_connect.send_command_timing("\n")
    output += net_connect.send_command_timing("\n")
    net_connect.save_config()
    print(output)


def xr(task):
    net_connect = task.host.get_connection("netmiko", task.nornir.config)
    net_connect.enable()
    host_hostname = net_connect.find_prompt().split(":")[-1].rstrip("#>")
    output = ""
    output += net_connect.send_command_timing(f"copy tftp://10.0.0.100/{host_hostname}_startup-config.cfg nvram:", read_timeout=10)
    output += net_connect.send_command_timing("\n")
    output += net_connect.send_command_timing("\n")
    net_connect.config_mode()
    output += net_connect.send_command_timing(f"load nvram:/{host_hostname}_startup-config.cfg", read_timeout=30)
    output += net_connect.send_command_timing("commit replace", read_timeout=30)
    net_connect.write_channel("yes")
    time.sleep(30)
    net_connect.exit_config_mode()
    output += net_connect.send_command_timing(f"delete nvram:{host_hostname}_startup-config.cfg", read_timeout=10)
    output += net_connect.send_command_timing("\n")
    output += net_connect.send_command_timing("\n")
    net_connect.commit()
    print(output)


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


if __name__ == "__main__":
    main()
