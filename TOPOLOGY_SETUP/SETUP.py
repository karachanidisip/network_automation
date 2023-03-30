# This line imports the os, subprocess
import os, subprocess


def igp():
    # A function to get igp preference.

    print("\033[1;93m")
    print("This function assisting you to define the igp preference.")
    print("\033[0m")

    USER_INPUT = input("\033[1;93m Enter the igp preference (eg 'ISIS', valid values RIP, ISIS, OSPF, EIGRP (case sensitive)), then press 'ENTER' \n: \033[0m")

    if USER_INPUT == "RIP":
        subprocess.call(["python3", "rip_setup.py"])
    elif USER_INPUT == "ISIS":
        subprocess.call(["python3", "isis_setup.py"])
    elif USER_INPUT == "OSPF":
        subprocess.call(["python3", "ospf_setup.py"])
    elif USER_INPUT == "EIGRP":
        subprocess.call(["python3", "eigrp_setup.py"])
    else:
        print("\033[1;93m You have provided an input NOT VALID. \033[0m")


# CODE!!!

# Change directory to the directory of a Python script
os.chdir(os.path.dirname(__file__) or '.')

subprocess.call(["python3", "topology_and_ipv4_setup.py"])
igp()
