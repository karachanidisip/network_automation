# This line imports the ipaddress Modules
import ipaddress


# The term SHORT_FORM refers to mask expressed as /<VALUE> (eg 10.1.1.1/24)
# The term LONG_FORM refers to mask expressed as /<VALUE>.<VALUE>.<VALUE>.<VALUE> (eg 10.1.2.1/255.255.255.0)
# The term WILDCARD_FORM refers to mask expressed as the logical inverse of a LONG_FORM mask (eg 10.1.2.1/0.0.0.255)
# The option "strict=False" allows VAR with host bits set


class Address():
    def __init__(self, address):
    # Accepts either ipv4_short_form or ipv4_long_form or ipv4_wilcard_form
        self.address = address
    def extrack_network_short_form(self):
        VAR = self.address
        ipv4_network_short_form = ipaddress.ip_network(VAR, strict=False).with_prefixlen
        return ipv4_network_short_form
    def extrack_network_long_form(self):
        VAR = self.address
        ipv4_network_long_form = ipaddress.ip_network(VAR, strict=False).with_netmask
        return ipv4_network_long_form
    def extrack_network_wildcard_form(self):
        VAR = self.address
        ipv4_network_wildcard_form = ipaddress.ip_network(VAR, strict=False).with_hostmask
        return ipv4_network_wildcard_form
    def extrack_mask_short_form(self):
        VAR = self.address
        ipv4_mask_short_form = ipaddress.ip_network(VAR, strict=False).prefixlen
        return ipv4_mask_short_form
    def extrack_mask_long_form(self):
        VAR = self.address
        ipv4_mask_long_form = ipaddress.ip_network(VAR, strict=False).netmask
        return ipv4_mask_long_form
    def extrack_mask_wildcard_form(self):
        VAR = self.address
        ipv4_mask_wildcard_form = ipaddress.ip_network(VAR, strict=False).hostmask
        return ipv4_mask_wildcard_form


class CompareAddresses():
    def __init__(self, address_1, address_2):
    # Accepts either ipv4_short_form or ipv4_long_form or ipv4_wilcard_form
        self.address_1 = address_1
        self.address_2 = address_2
    def check_for_subnet(self):
        VAR_1 = self.address_1
        VAR_2 = self.address_2
        a = ipaddress.ip_network(VAR_1, strict=False)
        b = ipaddress.ip_network(VAR_2, strict=False)
        output = b.subnet_of(a)
        return output
    def check_for_supernet(self):
        VAR_1 = self.address_1
        VAR_2 = self.address_2
        a = ipaddress.ip_network(VAR_1, strict=False)
        b = ipaddress.ip_network(VAR_2, strict=False)
        output = b.supernet_of(a)
        return output


"""
#######################################################################################################################################################################################################

x = "10.1.2.3/23"

print(Address(x).extrack_network_short_form())
print(Address(x).extrack_network_long_form())
print(Address(x).extrack_network_wildcard_form())
print(Address(x).extrack_mask_short_form())
print(Address(x).extrack_mask_long_form())
print(Address(x).extrack_mask_wildcard_form())

y = "10.1.2.3/23"
z = "10.1.2.3/22"

print(CompareAddresses(y, z).check_for_subnet())
print(CompareAddresses(y, z).check_for_supernet())

#######################################################################################################################################################################################################
"""
