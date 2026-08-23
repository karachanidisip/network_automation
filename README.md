# Network Automation Demo

## What is it / How it works

An automation tool that automates the boring stuff in network labbing:
setting IP addresses on interfaces and enabling basic IGP/BGP/MPLS on a GNS3
lab. **No advanced features** — this is a foundation, not a full NMS.

Implemented three times over, once each with Netmiko, Nornir, and Scrapli
— same devices, same result, different connection model each time.

## Core idea

A **dynamic Layer 3 topology** is generated over a **static Layer 2
topology**, using dot1Q sub-interfaces to carry each logical link. The
physical wiring never changes; what changes is which dot1Q sub-interfaces
exist and what's configured on them.

## Algorithm

Given a static topology description (which devices share a link, and what
that link is), the tool derives:

- **Subinterface numbering** — a sub-interface per logical link on the
  physical trunk each device is wired to.
- **VLAN assignment per link** — a dot1Q tag identifying that link.
- **IP assignment per link** — an address for each device on that link,
  drawn from the link's assigned subnet.

The same link description also drives which IGP/area/level a device
belongs to, and which links are MPLS- or BGP-relevant.

## Constraints

- Two multipoint links sharing the same max-id/min-id pair are not
  distinguished by the current algorithm — link identity relies on that
  pair being unique.
- An inter-site (eBGP) boundary is only modeled as a two-device
  point-to-point link. A multipoint segment spanning a site boundary is
  out of scope.
- The static topology data is not the source of truth for the eBGP
  boundary link — the eBGP peer list is, since the boundary link isn't
  reliably present in the per-site topology data.
- A device with no declared IS-IS area for its site raises an error by
  design — there's no silent fallback.
- IOS XR + MPLS: a Loopback interface must never be entered under
  `mpls ldp`, and `label local allocate for host-routes` must be issued
  only after all real interfaces are entered — reversing either causes
  IOS XR to hang.
- The Scrapli (async) execution path is less stable against this
  QEMU-based lab than the Netmiko/Nornir (sync) path, independent of the
  automation logic itself.

## Lab topology

- **Access Switch** — management network, `10.0.0.0/24`. The workstation
  running these scripts reaches all 14 devices through here.
- **Breakout Switch** — carries the dot1Q data-plane links the tool
  configures; kept separate from management on purpose.
- Devices `1`–`10` are IOS XE, devices `11`–`14` are IOS XR.

## How to run

1. **Populate the inventory** — run the `000_Inventory_Management_*`
   script matching the toolchain you want (Netmiko, Nornir, or Scrapli)
   to register the 14 devices.
2. **Set up the topology** — run the `003_ipv4_Setup_*` script to push
   loopbacks and dot1Q sub-interfaces to every device.
3. **Bring up an IGP** — run whichever of `004`–`007` matches the IGP
   the scenario needs per site (RIP/EIGRP/OSPF/IS-IS).
4. **Enable MPLS** — `008_ipv4_mpls`, for label switching.
5. **Peer BGP** — `009_ipv4_ibgp` for the full-mesh within a site, then
   `010_ipv4_ebgp` to connect sites together once each site is
   independently up.
6. **Backup/restore** — `001_Backup_Export_*` and `002_Backup_Import_*`
   are standalone and safe to run at any point.

Each numbered script has a `_Netmiko`, `_Nornir`, or `_Scrapli` variant
where available — pick one toolchain per run.

Whether a run ends up as a **single-site** or **multi-site** deployment
depends entirely on the data supplied in `variables.py`, not on which
scripts you run: an empty eBGP peer list means everything stays within
one site, while populating it declares the boundary links between sites
and brings `010_ipv4_ebgp` into play to connect them.
