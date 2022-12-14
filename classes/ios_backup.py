# This line imports the needed Functions from netmiko
from netmiko import ConnectHandler
# This line imports the os, sys, random, string, shutil, datetime, subprocess Modules
import os, sys, random, string, shutil, datetime, subprocess


# A class to export backup from IOS devices and manage them with git.
# The git repository directory need to be in the working directory (cd /path/to/parent/directory/of/git/repository/directory/).
# eg netmiko_device_dictionary = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.1", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}.


class IosBackUp():
    def __init__(self, netmiko_device_dictionary):
        self.netmiko_device_dictionary = netmiko_device_dictionary
    def export(self):
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
        os.rename("config" + random_string_1, hostname + "_startup-config.cfg")
        return hostname
    def git(self):
        working_directory = os.getcwd()
        for fname in os.listdir("."):
            if os.path.isfile(fname) and os.path.isfile(working_directory + "/" + "GIT/" + fname):
                os.remove(working_directory + "/" + "GIT/" + fname)
                shutil.move(working_directory + "/" + fname, working_directory + "/" + "GIT/" + fname)
            elif os.path.isfile(fname) and fname.endswith("_startup-config.cfg"):
                shutil.move(working_directory + "/" + fname, working_directory + "/" + "GIT/" + fname)
            else:
                pass
        ymd = datetime.date.today()
        date = ymd.strftime("%Y%m%d")
        hms = datetime.datetime.now()
        time = hms.strftime("%H%M%S")
        user_comment = input("\033[1;93m Enter a comment about the changes \n: \033[0m")
        git_path = working_directory + "/" + "GIT/"
        commit_name = date + "-" + time + "-" + user_comment
        git_add = subprocess.run(["git", "add", "."], cwd = git_path, capture_output=True, text=True)
        print(git_add.stdout)
        print(git_add.stderr)
        git_commit = subprocess.run(["git", "commit", "-m " + commit_name], cwd = git_path, capture_output=True, text=True)
        print(git_commit.stdout)
        print(git_commit.stderr)


"""
#######################################################################################################################################################################################################

R1 = {"device_type" : "cisco_ios_telnet", "host" : "10.0.0.1", "username" : "AUTO", "password" : "PASS", "secret" : "SECRET"}

IosBackUp(R1).export()
IosBackUp(R1).git()

#######################################################################################################################################################################################################
"""
