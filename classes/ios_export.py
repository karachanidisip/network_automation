# This line imports the needed Functions from netmiko
from netmiko import ConnectHandler
# This line imports the os, sys, random, string Modules
import os, sys, random, string


# A class to export configuration from IOS devices.
# The hostname of the device is exported as string.
# The pairs of interface and configured network are exported as a list with lists eg [["ethernet0/0", "10.1.0.1/24"], ["ethernet0/1", "10.1.1.1/24"], ["ethernet0/2", "10.1.2.1/24"]].
# eg netmiko_device_dictionary = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.1", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}.


class IosExport():
    def __init__(self, netmiko_device_dictionary):
        self.netmiko_device_dictionary = netmiko_device_dictionary
    def hostname(self):
        y = self.netmiko_device_dictionary
        net_connect = ConnectHandler(**y)
        net_connect.send_command("show running-config")
        exec_output_1 = net_connect.send_command("show running-config")
        random_string_1 = ''.join(random.choices(string.ascii_letters, k=10))
        with open("config" + random_string_1, "w") as f:
            print(exec_output_1, file=f)
        with open("config" + random_string_1, "r") as f:
            for line in f:
                if line.startswith("hostname"):
                    hostname = line.strip("hostname")
                    hostname = hostname.strip("\n")
        return hostname
    def interfaces(self):
        y = self.netmiko_device_dictionary
        net_connect = ConnectHandler(**y)
        net_connect.send_command("show ip interface")
        exec_output_2 = net_connect.send_command("show ip interface")
        random_string_2 = ''.join(random.choices(string.ascii_letters, k=10))
        with open("interface" + random_string_2, "w") as f:
            print(exec_output_2, file=f)
        interface_address_pairs = []
        with open("interface" + random_string_2, "r") as f:
            previous_line_first_word = ""
            for line in f:
                if line.startswith("  Internet address is "):
                    pair = []
                    z1 = previous_line_first_word
                    z2 = line.split()[3]
                    pair.append(z1)
                    pair.append(z2)
                    interface_address_pairs.append(pair)
                    try:
                        previous_line_first_word = line.split()[0]
                    except:
                        pass
                else:
                    try:
                        previous_line_first_word = line.split()[0]
                    except:
                        pass
        return interface_address_pairs
    def del_files(self):
        for fname in os.listdir("."):
            if os.path.isfile(fname) and fname.startswith("config"):
                os.remove(fname)
            elif os.path.isfile(fname) and fname.startswith("interface"):
                os.remove(fname)
            else:
                pass


"""
#######################################################################################################################################################################################################

R1 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.1", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}

print(IosExport(R1).hostname())
print(IosExport(R1).interfaces())
IosExport(R1).del_files()
#######################################################################################################################################################################################################
"""
