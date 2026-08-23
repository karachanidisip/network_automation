# Devices to be configured
DEVICES = ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5", "10.0.0.6", "10.0.0.7", "10.0.0.8", "10.0.0.9", "10.0.0.10",
           "10.0.0.11", "10.0.0.12", "10.0.0.13", "10.0.0.14"]


# GNS3 Interfaces
MANAGEMENT_INTERFACE_XE = ["Ethernet0/0", "10.0.0.0/24"]
MANAGEMENT_INTERFACE_XR = ["MgmtEth0/0/CPU0/0", "10.0.0.0/24"]
TOPOLOGY_INTERFACE_XE = ["Ethernet0/1"]
TOPOLOGY_INTERFACE_XR = ["GigabitEthernet0/0/0/1"]
LOOPBACK_INTERFACE = "Loopback0"


# Networks
NETWORKS = {"P2P":"20.0.0.0/8",
            "P2MP":"30.0.0.0/8",
            "LOOPBACK":"40.0.0.0/8"
            }


# Topology
TOPOLOGY = [{"devices_ids":"1-2-3-4-5", "link_instance":"1", "tag":"1", "ospf_area":"0", "isis_level":"2", "isis_area":"NULL"},
            {"devices_ids":"1-3", "link_instance":"1", "tag":"1", "ospf_area":"4", "isis_level":"2", "isis_area":"NULL"},
            {"devices_ids":"2-3", "link_instance":"1", "tag":"1", "ospf_area":"5", "isis_level":"1", "isis_area":"2"},
            {"devices_ids":"4-5", "link_instance":"1", "tag":"1", "ospf_area":"0", "isis_level":"2", "isis_area":"NULL"},
            {"devices_ids":"1-4-6", "link_instance":"1", "tag":"1", "ospf_area":"1", "isis_level":"1", "isis_area":"1"},
            {"devices_ids":"3-7", "link_instance":"1", "tag":"1", "ospf_area":"2", "isis_level":"1", "isis_area":"2"},
            {"devices_ids":"6-7", "link_instance":"1", "tag":"1", "ospf_area":"2", "isis_level":"1", "isis_area":"NULL"},
            {"devices_ids":"7-9", "link_instance":"1", "tag":"1", "ospf_area":"2", "isis_level":"1", "isis_area":"2"},
            {"devices_ids":"5-8", "link_instance":"1", "tag":"1", "ospf_area":"3", "isis_level":"1", "isis_area":"3"},
            {"devices_ids":"8-10", "link_instance":"1", "tag":"1", "ospf_area":"3", "isis_level":"1", "isis_area":"3"},
            {"devices_ids":"9-11", "link_instance":"1", "tag":"NULL", "ospf_area":"NULL", "isis_level":"NULL", "isis_area":"NULL"},
            {"devices_ids":"10-14", "link_instance":"1", "tag":"NULL", "ospf_area":"NULL", "isis_level":"NULL", "isis_area":"NULL"},
            {"devices_ids":"11-14", "link_instance":"1", "tag":"1", "ospf_area":"0", "isis_level":"2", "isis_area":"14"},
            {"devices_ids":"11-12", "link_instance":"1", "tag":"1", "ospf_area":"1", "isis_level":"2", "isis_area":"14"},
            {"devices_ids":"13-14", "link_instance":"1", "tag":"1", "ospf_area":"2", "isis_level":"2", "isis_area":"14"},
            {"devices_ids":"12-14", "link_instance":"1", "tag":"1", "ospf_area":"1", "isis_level":"2", "isis_area":"14"},
            {"devices_ids":"11-13", "link_instance":"1", "tag":"1", "ospf_area":"2", "isis_level":"2", "isis_area":"14"}
            ]


# Devices to enable MPLS forwarding on
MPLS = {"devices_ids":"1-2-3-4-5-6-7-8-9-10-11-12-13-14"}


# Full-mesh iBGP groups (every device_id inside one "device_ids" entry peers with every other device_id in that same entry, under that entry's asn)
IBGP = [{"asn":"109", "device_ids":"3-9"},
        {"asn":"109", "device_ids":"5-10"},
        {"asn":"109", "device_ids":"1-3-5"},
        {"asn":"1411", "device_ids":"11-14"}
        ]


# USEFUL ONLY IN MULTI-SITE CONFIGURATIONS
# Point-to-point eBGP sessions (entries are grouped two-by-two, each pair forming one eBGP peering)
EBGP = [{"asn":"109", "device_id":"10"}, {"asn":"1411", "device_id":"14"},
        {"asn":"109", "device_id":"9"}, {"asn":"1411", "device_id":"11"}
        ]
