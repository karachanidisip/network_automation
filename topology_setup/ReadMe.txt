This a python script automates the boring stuff with GNS3.
But, what is the boring stuff?
As far as it concerns GNS3 the boring stuff includes the setup of a topopology AND basic connectivity (basic rip/eigrp/ospf/isis/bgp/mpls setup).
The fundamental concept for this script is the decouple of LEVEL 2 (PHYSICAL) from LEVEL 3 (LOGICAL) topologies.
The LEVEL 2 topology consist of 14 Routers connected via TRUNK to a BREAKOUT switch. Moreover the 14 Routers are connected to an AccessSwitch using their Management interfaces. Finally a PC (management workstation) is connected to the AccessSwitch.
The LEVEL 3 topology configured over the abovementioned LEVEL 2 topology using DOT1Q encapsulation.

The script give you the ability to define the topology (LEVEL 3) and the IPs that will be used in two variables (INTRASITE, INTERSITE).
The script give you the ability to define the protocols (rip/eigrp/ospf/isis/bgp/mpls) that will be used to achieve basic connectivity.
Running the script more than one time (with different set of Routers) you can achieve multisite configuration (INTERSITE).

DEVICE_ID == DEVICE_NUMBER

INTRASITE CONSTRAINTS
Any p2p link (specific pair of devices) CANNOT have more than 2 instances (LINK_INSTANCE)!!!
Any p2mp link (specific set of devices) CANNOT have more than 1 instance (LINK_INSTANCE)!!!
Any p2mp link CANNOT have the same MAX_ID AND the same MIN_ID with any other p2mp link!!!

INTRASITE DOT1Qs RULES
p2p and MAX_ID < 10 and LINK_INSTANCE == 1:                             for 1st ->                  str(MAX_ID) + str(MIN_ID)
p2p and MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 1:            for 1st ->                  str(1) + str(MAX_ID)[-1] + str(MIN_ID)
p2p and MIN_ID >= 10 and LINK_INSTANCE == 1:                            for 1st ->                  str(2) + str(MAX_ID)[-1] + str(MIN_ID)[-1]
p2p and MAX_ID < 10 and LINK_INSTANCE == 2:                             for 2nd ->                  str(3) + str(MAX_ID) + str(MIN_ID)
p2p and MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 2:            for 2nd ->                  str(4) + str(MAX_ID)[-1] + str(MIN_ID)
p2p and MIN_ID >= 10 and LINK_INSTANCE == 2:                            for 2nd ->                  str(5) + str(MAX_ID)[-1] + str(MIN_ID)[-1]
p2mp and MAX_ID < 10 and LINK_INSTANCE == 1:                                    ->                  str(6) + str(MAX_ID) + str(MIN_ID)
p2mp and MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 1:                   ->                  str(7) + str(MAX_ID) + str(MIN_ID)
p2mp and MIN_ID >= 10 and LINK_INSTANCE == 1:                                   ->                  str(8) + str(MAX_ID) + str(MIN_ID)
loopbacks                                                                       ->                  DO NOT NEEDED

INTRASITE IPs RULES
p2p and MAX_ID < 10 and LINK_INSTANCE == 1:                             for 1st ->                  P2P_INTRASITE_NETWORK_X.str(100).dot1q.str(ID)/24
p2p and MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 1:            for 1st ->                  P2P_INTRASITE_NETWORK_X.str(100).dot1q.str(ID)/24
p2p and MIN_ID >= 10 and LINK_INSTANCE == 1:                            for 1st ->                  P2P_INTRASITE_NETWORK_X.str(100).dot1q.str(ID)/24
p2p and MAX_ID < 10 and LINK_INSTANCE == 2:                             for 2nd ->                  P2P_INTRASITE_NETWORK_X.str(200).str(MAX_ID) + str(MIN_ID).str(ID)/24
p2p and MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 2:            for 2nd ->                  P2P_INTRASITE_NETWORK_X.str(200).str(1) + str(MAX_ID)[-1] + str(MIN_ID).str(ID)/24
p2p and MIN_ID >= 10 and LINK_INSTANCE == 2:                            for 2nd ->                  P2P_INTRASITE_NETWORK_X.str(200).str(2) + str(MAX_ID)[-1] + str(MIN_ID)[-1].str(ID)/24
p2mp and MAX_ID < 10 and LINK_INSTANCE == 1:                                    ->                  P2MP_INTRASITE_NETWORK_Y.str(100).str(MAX_ID) + str(MIN_ID).str(ID)/24
p2mp and MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 1:                   ->                  P2MP_INTRASITE_NETWORK_Y.str(100).str(1) + str(MAX_ID)[-1] + str(MIN_ID).str(ID)/24
p2mp and MIN_ID >= 10 and LINK_INSTANCE == 1:                                   ->                  P2MP_INTRASITE_NETWORK_Y.str(100).str(2) + str(MAX_ID)[-1] + str(MIN_ID)[-1].str(ID)/24
loopbacks  

INTERSITE CONSTRAINTS
Any p2p link (specific pair of devices) CANNOT have more than 1 instances (LINK_INSTANCE)!!!
Any p2mp link (specific set of devices) CANNOT have more than 1 instance (LINK_INSTANCE)!!!
Any p2mp link CANNOT have the same MAX_ID AND the same MIN_ID with any other p2mp link!!!

INTERSITE DOT1Qs RULES
p2p and MAX_ID < 10:                            ->                  str(MAX_ID) + str(MIN_ID)
p2p and MAX_ID >= 10 and MIN_ID < 10:           ->                  str(1) + str(MAX_ID)[-1] + str(MIN_ID)
p2p and MIN_ID >= 10:                           ->                  str(2) + str(MAX_ID)[-1] + str(MIN_ID)[-1]
p2mp and MAX_ID < 10:                           ->                  str(6) + str(MAX_ID) + str(MIN_ID)
p2mp and MAX_ID >= 10 and MIN_ID < 10:          ->                  str(7) + str(MAX_ID) + str(MIN_ID)
p2mp and MIN_ID >= 10:                          ->                  str(8) + str(MAX_ID) + str(MIN_ID)
loopbacks                                       ->                  DO NOT NEEDED

INTERSITE IPs RULES
p2p and MAX_ID < 10:                            ->                  P2P_INTERSITE_NETWORK.str(100).dot1q.str(ID)/24
p2p and MAX_ID >= 10 and MIN_ID < 10:           ->                  P2P_INTERSITE_NETWORK.str(100).dot1q.str(ID)/24
p2p and MIN_ID >= 10:                           ->                  P2P_INTERSITE_NETWORK.str(100).dot1q.str(ID)/24
p2mp and MAX_ID < 10:                           ->                  P2MP_INTERSITE_NETWORK.str(100).str(MAX_ID) + str(MIN_ID).str(ID)/24
p2mp and MAX_ID >= 10 and MIN_ID < 10:          ->                  P2MP_INTERSITE_NETWORK.str(100).str(1) + str(MAX_ID)[-1] + str(MIN_ID).str(ID)/24
p2mp and MIN_ID >= 10:                          ->                  P2MP_INTERSITE_NETWORK.str(100).str(2) + str(MAX_ID)[-1] + str(MIN_ID)[-1].str(ID)/24
loopbacks                                       ->                  LOOPBACK_INTERSITE_NETWORK_Z.str(ID).str(ID).str(ID)/24

