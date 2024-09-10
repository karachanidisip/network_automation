The script give you the ability to IMPORT the configuration for a set of devices (or for all the devices) in the topology.
The scripts requires a directory named "TFTP" in the working directory. This is the directory where the configuration files from every device are stored.
You need to configure a TFTP SERVER tracking the TFTP directory (do not forget to turn off the firewall/iptables or to allow the tftp traffic).
An easy solution for TFTP SERVER is the tftpy python library.
                                                                                  
The LEVEL 2 topology consist of 14 Routers connected via TRUNK to a BREAKOUT switch. Moreover the 14 Routers are connected to an AccessSwitch using their Management interfaces. Finally a PC (management workstation) is connected to the AccessSwitch.
The LEVEL 3 topology configured over the abovementioned LEVEL 2 topology using DOT1Q encapsulation.
