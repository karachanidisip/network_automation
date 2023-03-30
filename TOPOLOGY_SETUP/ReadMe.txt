AIM
This collection of scripts makes use of a topology with devices interconnected over a switch using the same interface (eg Ethernet0/1).
The topology_and_ipv4_setup.py creates a logical topology, making use of sub-interfaces and dot1q encapsulation, over the physical one. In effect you can create ANY kind of logical topology.
There are other scripts to configure IGPs (RIP, ISIS, OSPF, EIGRP) on the logical topology.
The SETUP.py can be used to call any of the scripts.

LIMITATIONS
The hostmane and the management address of the devices CANNOT be changed!
