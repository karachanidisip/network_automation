# A class to create configuration for RIP.
# The class require an rip_input_list formatted as [network, ...].
# The network need to be any ipv4 address (eg "10.12.1.2").
# eg rip_input_list = ["10.1.1.0", "11.1.0.0", "12.0.0.0"]


class Rip():
    def __init__(self, rip_input_list):
        self.rip_input_list = rip_input_list
    def process(self):
        y = self.rip_input_list
        rip_process_list = []
        x = f"configure terminal"
        rip_process_list.append(x)
        x = f"router rip"
        rip_process_list.append(x)
        for item in y:
            x = f"network {item}"
            rip_process_list.append(x)
        return rip_process_list


# A class to create configuration for EIGRP.
# The class require an eigrp_input_list formatted as [AS, [[network, wildcard], ...]].
# The AS need to be from 1 to 65535 (eg "12").
# The network need to be any ipv4 address (eg "10.12.1.2").
# The wildcard need to be formatted as X.X.X.X (eg "0.0.0.255").
# eg eigrp_input_list = ["123", [["10.1.1.0", "0.0.0.255"], ["10.1.2.0", "0.0.0.255"], ["10.1.3.0", "0.0.0.255"]]]


class Eigrp():
    def __init__(self, eigrp_input_list):
        self.eigrp_input_list = eigrp_input_list
    def process(self):
        y = self.eigrp_input_list
        eigrp_process_list = []
        z0 = y[0]
        x = f"configure terminal"
        eigrp_process_list.append(x)
        x = f"router eigrp {z0}"
        eigrp_process_list.append(x)
        return eigrp_process_list
    def networks(self):
        y = self.eigrp_input_list
        eigrp_networks_list = []
        z0 = y[0]
        z1 = y[1]
        x = f"configure terminal"
        eigrp_networks_list.append(x)
        x = f"router eigrp {z0}"
        eigrp_networks_list.append(x)
        for item in z1:
            x = f"network {item[0]} {item[1]}"
            eigrp_networks_list.append(x)
        return eigrp_networks_list


# A class to create configuration for ISIS.
# The class require an isis_input_list formatted as [area_id, system_id, process_level, [[interface_active, interface_level], ...]].
# The area_id need to be formatted as XXXX (eg "0012").
# The system_id need to be formatted as XXXX.XXXX (eg "0000.0001").
# The process_level need to be either "level-1" or "level-1-2" or "level-2-only".
# The interface_active need to be any of the interfaces (eg "ethernet0/0").
# The interface_level need to be either "level-1" or "level-1-2" or "level-2-only".
# eg isis_input_list = ["0020", "0000.0001", "level-1-2", [["ethernet0/0", "level-1-2"], ["ethernet0/1", "level-1"], ["ethernet0/2", "level-2-only"]]]


class Isis():
    def __init__(self, isis_input_list):
        self.isis_input_list = isis_input_list
    def process(self):
        y = self.isis_input_list
        isis_process_list = []
        z0 = y[0]
        z1 = y[1]
        z2 = y[2]
        x = f"configure terminal"
        isis_process_list.append(x)
        x = f"router isis"
        isis_process_list.append(x)
        x = f"net 49.{z0}.{z1}.00"
        isis_process_list.append(x)
        x = f"is-type {z2}"
        isis_process_list.append(x)
        return isis_process_list
    def interfaces(self):
        y = self.isis_input_list
        isis_interfaces_list = []
        z3 = y[3]
        x = f"configure terminal"
        isis_interfaces_list.append(x)
        for item in z3:
            x = f"interface {item[0]}"
            isis_interfaces_list.append(x)
            x = f"ip router isis"
            isis_interfaces_list.append(x)
            x = f"isis circuit-type {item[1]}"
            isis_interfaces_list.append(x)
        return isis_interfaces_list


# A class to create configuration for OSPF.
# The class require an ospf_input_list formatted as [process_id, [[interface_active, area_id], ...], [[network, wildcard ,area_id], ...]].
# The process_id need to be from 1 to 65535 (eg "12").
# The interface_active need to be any of the interfaces (eg "ethernet0/0").
# The area_id need to be from 1 to 4294967295 (eg "2").
# The network need to be any ipv4 address (eg "10.12.1.2").
# The wildcard need to be formatted as X.X.X.X (eg "0.0.0.255").
# eg ospf_input_list = ["123", [["ethernet0/1", "1"], ["ethernet0/2", "2"], ["ethernet0/3", "3"]], [["10.1.1.0", "0.0.0.255", "1"], ["10.1.2.0", "0.0.0.255", "2"], ["10.1.3.0", "0.0.0.255", "3"]]]


class Ospf():
    def __init__(self, ospf_input_list):
        self.ospf_input_list = ospf_input_list
    def process(self):
        y = self.ospf_input_list
        ospf_process_list = []
        z0 = y[0]
        x = f"configure terminal"
        ospf_process_list.append(x)
        x = f"router ospf {z0}"
        ospf_process_list.append(x)
        return ospf_process_list
    def interfaces(self):
        y = self.ospf_input_list
        ospf_interfaces_list = []
        z0 = y[0]
        z1 = y[1]
        x = f"configure terminal"
        ospf_interfaces_list.append(x)
        for item in z1:
            x = f"interface {item[0]}"
            ospf_interfaces_list.append(x)
            x = f"ip ospf {z0} area {item[1]}"
            ospf_interfaces_list.append(x)
        return ospf_interfaces_list
    def networks(self):
        y = self.ospf_input_list
        ospf_networks_list = []
        z0 = y[0]
        z2 = y[2]
        x = f"configure terminal"
        ospf_networks_list.append(x)
        x = f"router ospf {z0}"
        ospf_networks_list.append(x)
        for item in z2:
            x = f"network {item[0]} {item[1]} area {item[2]}"
            ospf_networks_list.append(x)
        return ospf_networks_list


"""
#######################################################################################################################################################################################################

rip_input_list = ["10.1.1.0", "11.1.0.0", "12.0.0.0"]
print(Rip(rip_input_list).process())


eigrp_input_list = ["123", [["10.1.1.0", "0.0.0.255"], ["10.1.2.0", "0.0.0.255"], ["10.1.3.0", "0.0.0.255"]]]
print(Eigrp(eigrp_input_list).process())
print(Eigrp(eigrp_input_list).networks())


isis_input_list = ["0020", "0000.0001", "level-1-2", [["ethernet0/0", "level-1-2"], ["ethernet0/1", "level-1"], ["ethernet0/2", "level-2-only"]]]
print(Isis(isis_input_list).process())
print(Isis(isis_input_list).interfaces())


ospf_input_list = ["123", [["ethernet0/1", "1"], ["ethernet0/2", "2"], ["ethernet0/3", "3"]], [["10.1.1.0", "0.0.0.255", "1"], ["10.1.2.0", "0.0.0.255", "2"], ["10.1.3.0", "0.0.0.255", "3"]]]
print(Ospf(ospf_input_list).process())
print(Ospf(ospf_input_list).interfaces())
print(Ospf(ospf_input_list).networks())

#######################################################################################################################################################################################################
"""
