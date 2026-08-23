"""
CONSTRAINTS
Any p2p link (specific pair of devices) CANNOT have more than 2 instances (LINK_INSTANCE)!!!
Any p2mp link (specific set of devices) CANNOT have more than 1 instance (LINK_INSTANCE)!!!
Any p2mp link CANNOT have the same MAX_ID AND the same MIN_ID with any other p2mp link!!!

DOT1Qs
p2p and MAX_ID < 10 and LINK_INSTANCE == 1:                             for 1st ->                  str(MAX_ID) + str(MIN_ID)
p2p and MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 1:            for 1st ->                  str(1) + str(MAX_ID)[-1] + str(MIN_ID)
p2p and MIN_ID >= 10 and LINK_INSTANCE == 1:                            for 1st ->                  str(2) + str(MAX_ID)[-1] + str(MIN_ID)[-1]
p2p and MAX_ID < 10 and LINK_INSTANCE == 2:                             for 2nd ->                  str(3) + str(MAX_ID) + str(MIN_ID)
p2p and MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 2:            for 2nd ->                  str(4) + str(MAX_ID)[-1] + str(MIN_ID)
p2p and MIN_ID >= 10 and LINK_INSTANCE == 2:                            for 2nd ->                  str(5) + str(MAX_ID)[-1] + str(MIN_ID)[-1]
p2mp and MAX_ID < 10 and LINK_INSTANCE == 1:                                    ->                  str(6) + str(MAX_ID) + str(MIN_ID)
p2mp and MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 1:                   ->                  str(7) + str(MAX_ID)[-1] + str(MIN_ID)
p2mp and MIN_ID >= 10 and LINK_INSTANCE == 1:                                   ->                  str(8) + str(MAX_ID)[-1] + str(MIN_ID)[-1]
loopbacks                                                                       ->                  DO NOT NEEDED

IPv4s
p2p and MAX_ID < 10 and LINK_INSTANCE == 1:                             for 1st ->                  P2P_SITE_NETWORK_X.str(100).str(MAX_ID) + str(MIN_ID).str(ID)/24
p2p and MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 1:            for 1st ->                  P2P_SITE_NETWORK_X.str(100).str(1) + str(MAX_ID)[-1] + str(MIN_ID).str(ID)/24
p2p and MIN_ID >= 10 and LINK_INSTANCE == 1:                            for 1st ->                  P2P_SITE_NETWORK_X.str(100).str(2) + str(MAX_ID)[-1] + str(MIN_ID)[-1].str(ID)/24
p2p and MAX_ID < 10 and LINK_INSTANCE == 2:                             for 2nd ->                  P2P_SITE_NETWORK_X.str(200).str(MAX_ID) + str(MIN_ID).str(ID)/24
p2p and MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 2:            for 2nd ->                  P2P_SITE_NETWORK_X.str(200).str(1) + str(MAX_ID)[-1] + str(MIN_ID).str(ID)/24
p2p and MIN_ID >= 10 and LINK_INSTANCE == 2:                            for 2nd ->                  P2P_SITE_NETWORK_X.str(200).str(2) + str(MAX_ID)[-1] + str(MIN_ID)[-1].str(ID)/24
p2mp and MAX_ID < 10 and LINK_INSTANCE == 1:                                    ->                  P2MP_SITE_NETWORK_Y.str(100).str(MAX_ID) + str(MIN_ID).str(ID)/24
p2mp and MAX_ID >= 10 and MIN_ID < 10 and LINK_INSTANCE == 1:                   ->                  P2MP_SITE_NETWORK_Y.str(100).str(1) + str(MAX_ID)[-1] + str(MIN_ID).str(ID)/24
p2mp and MIN_ID >= 10 and LINK_INSTANCE == 1:                                   ->                  P2MP_SITE_NETWORK_Y.str(100).str(2) + str(MAX_ID)[-1] + str(MIN_ID)[-1].str(ID)/24
loopbacks                                                                       ->                  LOOPBACK_SITE_NETWORK_Z.str(ID).str(ID).str(ID)/24

LOOPBACKS
OSPF loopbacks are placed in the highest-numbered area the router touches, except area 0 (the backbone) always takes priority if present.
ISIS loopbacks are placed in highest (numerically) level available (2>1).
"""


from variables import NETWORKS, TOPOLOGY


class Topology:

    def __init__(self, topology_data, networks_data, ebgp_data=None):
        self.topology_data = topology_data
        self.networks = networks_data
        self.ebgp_data = ebgp_data if ebgp_data is not None else []

    def links_for_device(self, device_id):
        """All TOPOLOGY entries (as dicts) that a given device participates in."""
        matching_links = []
        for entry in self.topology_data:
            device_ids = []
            for d in entry["devices_ids"].split("-"):
                device_ids.append(int(d))
            if device_id in device_ids:
                matching_links.append(entry)
        return matching_links

    def dot1q_tag(self, device_id, link):
        """Returns the DOT1Q subinterface tag for one device on one link."""
        device_ids = []
        for d in link["devices_ids"].split("-"):
            device_ids.append(int(d))

        if device_id not in device_ids:
            raise ValueError(f"Device {device_id} is not part of link {link['devices_ids']}.")

        min_id = min(device_ids)
        max_id = max(device_ids)
        is_p2mp = len(device_ids) > 2

        if is_p2mp:
            if max_id < 10:
                tag = "6" + str(max_id) + str(min_id)
            elif max_id >= 10 and min_id < 10:
                tag = "7" + str(max_id)[-1] + str(min_id)
            else:
                tag = "8" + str(max_id)[-1] + str(min_id)[-1]
        elif link["link_instance"] == "1":
            if max_id < 10:
                tag = str(max_id) + str(min_id)
            elif max_id >= 10 and min_id < 10:
                tag = "1" + str(max_id)[-1] + str(min_id)
            else:
                tag = "2" + str(max_id)[-1] + str(min_id)[-1]
        else:
            if max_id < 10:
                tag = "3" + str(max_id) + str(min_id)
            elif max_id >= 10 and min_id < 10:
                tag = "4" + str(max_id)[-1] + str(min_id)
            else:
                tag = "5" + str(max_id)[-1] + str(min_id)[-1]

        return tag

    def subinterface_id(self, device_id, link):
        """Returns the physical interface's subinterface number (same value as the DOT1Q tag)."""
        return self.dot1q_tag(device_id, link)

    def ip_address(self, device_id, link):
        """Returns this device's IPv4 address + prefix length on this link."""
        device_ids = []
        for d in link["devices_ids"].split("-"):
            device_ids.append(int(d))

        if device_id not in device_ids:
            raise ValueError(f"Device {device_id} is not part of link {link['devices_ids']}.")

        min_id = min(device_ids)
        max_id = max(device_ids)
        is_p2mp = len(device_ids) > 2

        if is_p2mp:
            base_network = self.networks["P2MP"]
            second_octet = "100"
        elif link["link_instance"] == "1":
            base_network = self.networks["P2P"]
            second_octet = "100"
        else:
            base_network = self.networks["P2P"]
            second_octet = "200"

        first_octet = base_network.split(".")[0]

        if max_id < 10:
            third_octet = str(max_id) + str(min_id)
        elif max_id >= 10 and min_id < 10:
            third_octet = "1" + str(max_id)[-1] + str(min_id)
        else:
            third_octet = "2" + str(max_id)[-1] + str(min_id)[-1]

        fourth_octet = str(device_id)

        address = first_octet + "." + second_octet + "." + third_octet + "." + fourth_octet
        return address + "/24"

    def topology_networks(self):
        """Returns the flat list of subnets."""
        networks = []

        # Link subnets.
        for link in self.topology_data:
            device_ids = []
            for d in link["devices_ids"].split("-"):
                device_ids.append(int(d))
            min_id = min(device_ids)
            max_id = max(device_ids)
            is_p2mp = len(device_ids) > 2

            if is_p2mp:
                base_network = self.networks["P2MP"]
                second_octet = "100"
            elif link["link_instance"] == "1":
                base_network = self.networks["P2P"]
                second_octet = "100"
            else:
                base_network = self.networks["P2P"]
                second_octet = "200"

            first_octet = base_network.split(".")[0]

            if max_id < 10:
                third_octet = str(max_id) + str(min_id)
            elif max_id >= 10 and min_id < 10:
                third_octet = "1" + str(max_id)[-1] + str(min_id)
            else:
                third_octet = "2" + str(max_id)[-1] + str(min_id)[-1]

            subnet = first_octet + "." + second_octet + "." + third_octet + ".0/24"
            if subnet not in networks:
                networks.append(subnet)

        # Loopback subnets — one per device that appears anywhere in the topology.
        all_device_ids = []
        for link in self.topology_data:
            for d in link["devices_ids"].split("-"):
                device_id = int(d)
                if device_id not in all_device_ids:
                    all_device_ids.append(device_id)

        loopback_base = self.networks["LOOPBACK"]
        loopback_first_octet = loopback_base.split(".")[0]
        for device_id in all_device_ids:
            loopback_subnet = loopback_first_octet + "." + str(device_id) + ".0.0/16"
            networks.append(loopback_subnet)

        return networks

    def routing_process_tag(self, device_id):
        """Returns the tag (ASN, PROCESS NUMBER, TAG)."""
        links = self.links_for_device(device_id)

        tags = []
        for link in links:
            if link["tag"] not in tags:
                tags.append(link["tag"])

        if len(tags) == 0:
            raise ValueError(f"Device {device_id} has no links in the topology.")

        if len(tags) > 1:
            raise ValueError(f"Device {device_id} has conflicting tags across its links: {tags}")

        return tags[0]

    def ospf_area(self, device_id, for_loopback=False):
        """OSPF loopbacks are placed in the highest-numbered area the router touches, except area 0 (the backbone) always takes priority if present."""
        if not for_loopback:
            raise NotImplementedError("ospf_area() is only defined for for_loopback=True — "
                                       "a link's own area is available directly as link['ospf_area'].")

        links = self.links_for_device(device_id)

        if len(links) == 0:
            raise ValueError(f"Device {device_id} has no links in the topology.")

        areas = []
        for link in links:
            area = int(link["ospf_area"])
            if area not in areas:
                areas.append(area)

        if 0 in areas:
            return 0

        return max(areas)

    def isis_level(self, device_id, for_loopback=False):
        """ISIS loopbacks are placed in highest (numerically) level available (2>1)."""
        if not for_loopback:
            raise NotImplementedError("isis_level() is only defined for for_loopback=True — "
                                       "a link's own level is available directly as link['isis_level'].")

        links = self.links_for_device(device_id)

        if len(links) == 0:
            raise ValueError(f"Device {device_id} has no links in the topology.")

        levels = []
        for link in links:
            level = int(link["isis_level"])
            if level not in levels:
                levels.append(level)

        return max(levels)

    def loopback_address(self, device_id):
        """Returns this device's IPv4 loopback address + prefix length.

        Always a /32: a loopback is a host address, not a subnet. A /24 here
        would advertise 254 unused addresses as "reachable" via that
        interface, which is at best sloppy and at worst a real reachability
        hazard if two loopbacks ever end up looking like they share a
        subnet. MPLS FECs, BGP next-hops, and router-IDs all expect a clean
        host route.
        """
        loopback_base = self.networks["LOOPBACK"]
        first_octet = loopback_base.split(".")[0]
        address = first_octet + "." + str(device_id) + "." + str(device_id) + "." + str(device_id)
        return address + "/32"

    def isis_area(self, device_id):
        """Returns the isis area."""
        links = self.links_for_device(device_id)

        if len(links) == 0:
            raise ValueError(f"Device {device_id} has no links in the topology.")

        areas = []
        for link in links:
            if link["isis_area"] != "NULL" and link["isis_area"] not in areas:
                areas.append(link["isis_area"])

        if len(areas) == 0:
            raise ValueError(f"Device {device_id} has no ISIS area information on any of its links.")

        if len(areas) > 1:
            raise ValueError(f"Device {device_id} has conflicting ISIS areas across its links: {areas}")

        return areas[0]

    def topology_networks_with_ospf_areas(self):
        """Returns [subnet, area] pairs."""
        networks_and_areas = []

        for link in self.topology_data:
            device_ids = []
            for d in link["devices_ids"].split("-"):
                device_ids.append(int(d))
            min_id = min(device_ids)
            max_id = max(device_ids)
            is_p2mp = len(device_ids) > 2

            if is_p2mp:
                base_network = self.networks["P2MP"]
                second_octet = "100"
            elif link["link_instance"] == "1":
                base_network = self.networks["P2P"]
                second_octet = "100"
            else:
                base_network = self.networks["P2P"]
                second_octet = "200"

            first_octet = base_network.split(".")[0]

            if max_id < 10:
                third_octet = str(max_id) + str(min_id)
            elif max_id >= 10 and min_id < 10:
                third_octet = "1" + str(max_id)[-1] + str(min_id)
            else:
                third_octet = "2" + str(max_id)[-1] + str(min_id)[-1]

            subnet = first_octet + "." + second_octet + "." + third_octet + ".0/24"
            pair = [subnet, link["ospf_area"]]
            if pair not in networks_and_areas:
                networks_and_areas.append(pair)

        all_device_ids = []
        for link in self.topology_data:
            for d in link["devices_ids"].split("-"):
                device_id = int(d)
                if device_id not in all_device_ids:
                    all_device_ids.append(device_id)

        loopback_base = self.networks["LOOPBACK"]
        loopback_first_octet = loopback_base.split(".")[0]
        for device_id in all_device_ids:
            loopback_subnet = loopback_first_octet + "." + str(device_id) + ".0.0/16"
            loopback_area = str(self.ospf_area(device_id, for_loopback=True))
            networks_and_areas.append([loopback_subnet, loopback_area])

        return networks_and_areas

    def topology_networks_with_isis_levels(self):
        """Returns [subnet, level] pairs."""
        networks_and_levels = []

        for link in self.topology_data:
            device_ids = []
            for d in link["devices_ids"].split("-"):
                device_ids.append(int(d))
            min_id = min(device_ids)
            max_id = max(device_ids)
            is_p2mp = len(device_ids) > 2

            if is_p2mp:
                base_network = self.networks["P2MP"]
                second_octet = "100"
            elif link["link_instance"] == "1":
                base_network = self.networks["P2P"]
                second_octet = "100"
            else:
                base_network = self.networks["P2P"]
                second_octet = "200"

            first_octet = base_network.split(".")[0]

            if max_id < 10:
                third_octet = str(max_id) + str(min_id)
            elif max_id >= 10 and min_id < 10:
                third_octet = "1" + str(max_id)[-1] + str(min_id)
            else:
                third_octet = "2" + str(max_id)[-1] + str(min_id)[-1]

            subnet = first_octet + "." + second_octet + "." + third_octet + ".0/24"
            pair = [subnet, link["isis_level"]]
            if pair not in networks_and_levels:
                networks_and_levels.append(pair)

        all_device_ids = []
        for link in self.topology_data:
            for d in link["devices_ids"].split("-"):
                device_id = int(d)
                if device_id not in all_device_ids:
                    all_device_ids.append(device_id)

        loopback_base = self.networks["LOOPBACK"]
        loopback_first_octet = loopback_base.split(".")[0]
        for device_id in all_device_ids:
            loopback_subnet = loopback_first_octet + "." + str(device_id) + ".0.0/16"
            loopback_level = str(self.isis_level(device_id, for_loopback=True))
            networks_and_levels.append([loopback_subnet, loopback_level])

        return networks_and_levels

    def ebgp_peer(self, device_id):
        """Returns (own_asn, peer_asn, peer_device_id) for device_id's eBGP
        peer, or None if device_id isn't part of any EBGP pair. EBGP entries
        are grouped two-by-two: index 0-1 is one p2p session, 2-3 the next."""
        for i in range(0, len(self.ebgp_data), 2):
            pair = self.ebgp_data[i:i + 2]
            pair_ids = []
            for element in pair:
                pair_ids.append(int(element["device_id"]))

            if device_id in pair_ids:
                if int(pair[0]["device_id"]) == device_id:
                    own_entry, peer_entry = pair[0], pair[1]
                else:
                    own_entry, peer_entry = pair[1], pair[0]
                return own_entry["asn"], peer_entry["asn"], int(peer_entry["device_id"])

        return None

    def intersite_pairs(self):
        """Returns the list of {device_id_a, device_id_b} sets declared in
        EBGP — these are the device-id sets that mark a TOPOLOGY entry as
        crossing an AS boundary rather than staying inside one site."""
        pairs = []
        for i in range(0, len(self.ebgp_data), 2):
            pair = self.ebgp_data[i:i + 2]
            pair_ids = []
            for element in pair:
                pair_ids.append(int(element["device_id"]))
            pair_set = frozenset(pair_ids)
            if pair_set not in pairs:
                pairs.append(pair_set)
        return pairs

    def is_intersite_entry(self, entry):
        """True if this TOPOLOGY entry's device-id set exactly matches one
        of the EBGP pairs. Only a plain two-device (p2p) link can be
        intersite under this scheme — a p2mp segment spanning a site
        boundary isn't modeled here."""
        device_ids = []
        for d in entry["devices_ids"].split("-"):
            device_ids.append(int(d))

        if len(device_ids) != 2:
            return False

        return frozenset(device_ids) in self.intersite_pairs()

    def split_intersite(self):
        """Partitions topology_data into (intrasite_entries, intersite_entries)."""
        intrasite_entries = []
        intersite_entries = []
        for entry in self.topology_data:
            if self.is_intersite_entry(entry):
                intersite_entries.append(entry)
            else:
                intrasite_entries.append(entry)
        return intrasite_entries, intersite_entries

    def intrasite_topology(self):
        """Returns a Topology built from only the intrasite links — the view
        004-007 should build their IGP-network lists from, so an AS-boundary
        link is never picked up by an IGP scan regardless of run order."""
        intrasite_entries, _ = self.split_intersite()
        return Topology(intrasite_entries, self.networks, self.ebgp_data)

    def link_for_ebgp_peer(self, device_id):
        """Returns the TOPOLOGY entry for device_id's intersite (eBGP
        boundary) link. Used by 010 instead of building/addressing the link
        itself — the link is now a normal TOPOLOGY entry, so 010 only needs
        to find which one it is."""
        peer = self.ebgp_peer(device_id)
        if peer is None:
            raise ValueError(f"Device {device_id} has no EBGP entry.")

        _, _, peer_id = peer
        pair_set = frozenset([device_id, peer_id])

        for entry in self.topology_data:
            device_ids = []
            for d in entry["devices_ids"].split("-"):
                device_ids.append(int(d))
            if frozenset(device_ids) == pair_set:
                return entry

        raise ValueError(f"No TOPOLOGY entry found for the {device_id}-{peer_id} EBGP link.")

    def _link_subnet(self, link):
        """The /24 subnet for one p2p/p2mp link. Factored out of the
        duplicated third-octet math in ip_address()/topology_networks() so
        intersite_networks() below doesn't need its own copy of it."""
        device_ids = []
        for d in link["devices_ids"].split("-"):
            device_ids.append(int(d))
        min_id = min(device_ids)
        max_id = max(device_ids)
        is_p2mp = len(device_ids) > 2

        if is_p2mp:
            base_network = self.networks["P2MP"]
            second_octet = "100"
        elif link["link_instance"] == "1":
            base_network = self.networks["P2P"]
            second_octet = "100"
        else:
            base_network = self.networks["P2P"]
            second_octet = "200"

        first_octet = base_network.split(".")[0]

        if max_id < 10:
            third_octet = str(max_id) + str(min_id)
        elif max_id >= 10 and min_id < 10:
            third_octet = "1" + str(max_id)[-1] + str(min_id)
        else:
            third_octet = "2" + str(max_id)[-1] + str(min_id)[-1]

        return first_octet + "." + second_octet + "." + third_octet + ".0/24"

    def intersite_networks(self):
        """Returns the flat list of /24 subnets for intersite (eBGP
        boundary) links only — this is INTERSITE_NETWORKS for 008, the one
        script that doesn't derive its interface list from TOPOLOGY at all."""
        _, intersite_entries = self.split_intersite()
        networks = []
        for link in intersite_entries:
            subnet = self._link_subnet(link)
            if subnet not in networks:
                networks.append(subnet)
        return networks
