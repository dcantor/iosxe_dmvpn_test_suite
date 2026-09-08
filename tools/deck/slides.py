"""The fifteen slides. Every figure here came from the running lab."""
from content import *

S = []

def add(*items):
    flat = []
    for i in items:
        flat.extend(i) if isinstance(i, list) else flat.append(i)
    S.append(flat)

# ---------------------------------------------------------------- 1. title
add(
    R(0, 0, W, H, fill=INK),
    R(0, 0, W, 4.10, fill=INK2),
    T(0.85, 1.28, 10, 0.3, "NETWORK TEST INFRASTRUCTURE", size=12.5, bold=True,
      color=TEAL, font=BODY),
    T(0.85, 1.72, 11.4, 1.05, "The DMVPN Lab Testbed", size=54, bold=True,
      color=WHITE, font=HEAD),
    T(0.85, 2.92, 10.6, 0.72,
      "A three-router Cisco DMVPN network, its hosts and its management server, "
      "running as virtual machines on a single Linux box — rebuilt from nothing "
      "and re-verified on demand.",
      size=15.5, color="B9C7CE", lh=1.38),
    C(0.85, 4.42, 0.30, TEAL),
    T(1.32, 4.40, 10.6, 0.34, "215 automated tests across 23 suites, in 24 minutes",
      size=14, bold=True, color=WHITE),
    L(0.85, 5.15, 12.5, 5.15, color="33454F", w=1),
    T(0.85, 5.45, 3.0, 0.3, "PLATFORM", size=10.5, bold=True, color=TEAL),
    T(0.85, 5.78, 3.0, 0.3, "Cisco Catalyst 8000V", size=13.5, color=WHITE),
    T(0.85, 6.06, 3.6, 0.3, "IOS-XE 17.15.06", size=12, color=MUTED),
    T(4.55, 5.45, 3.0, 0.3, "HYPERVISOR", size=10.5, bold=True, color=TEAL),
    T(4.55, 5.78, 3.2, 0.3, "QEMU 10.2 / KVM", size=13.5, color=WHITE),
    T(4.55, 6.06, 3.6, 0.3, "7 VMs, one host", size=12, color=MUTED),
    T(8.25, 5.45, 3.0, 0.3, "HARNESS", size=10.5, bold=True, color=TEAL),
    T(8.25, 5.78, 3.4, 0.3, "Robot Framework 7.3", size=13.5, color=WHITE),
    T(8.25, 6.06, 3.6, 0.3, "Python 3.14 · pyATS · Genie", size=12, color=MUTED),
)

# ------------------------------------------------------- 2. executive summary
add(
    R(0, 0, W, H, fill=MIST),
    title_block("What the lab is, in one slide",
                "A production-shaped network that can be destroyed and rebuilt without touching production"),
    R(0.75, 1.72, 11.83, 1.42, fill=WHITE, radius=0.09, line=LINE, shadow=True),
    stat(1.15, 1.86, 2.4, "7", "virtual machines"),
    stat(4.05, 1.86, 2.4, "23", "test suites"),
    stat(6.95, 1.86, 2.4, "215", "automated tests"),
    stat(9.85, 1.86, 2.6, "24 min", "full regression", color=TEAL_D),
    card(0.75, 3.42, 3.78, 1.94, "Real software, not a simulator",
         "The routers run the same IOS-XE image as the physical fleet. Behaviour that "
         "depends on the operating system — timers, refusals, silent failures — shows up here."),
    card(4.78, 3.42, 3.78, 1.94, "Rebuilt from source config",
         "Ten provisioning phases take a factory-fresh image to a fully configured "
         "network. Nothing is hand-typed, so nothing is unrepeatable."),
    card(8.81, 3.42, 3.77, 1.94, "Evidence, not assertions",
         "Every run archives device state, logs and a numbered PDF report. A claim "
         "that something passed is backed by the command output that proved it."),
    R(0.75, 5.58, 11.83, 1.30, fill=WHITE, radius=0.09, line=LINE, shadow=True),
    C(1.05, 5.86, 0.13, AMBER),
    T(1.38, 5.76, 11.0, 0.32, "Why it matters commercially", size=14.5, bold=True, font=HEAD),
    T(1.38, 6.10, 10.9, 0.66,
      "Changes to encryption, routing policy, NAT or authentication can be proven safe "
      "before they reach a customer site — and a failure found here costs a 24-minute "
      "re-run rather than a change window and a truck roll.",
      size=12.5, color=MUTED, lh=1.32),
)

# --------------------------------------------------------------- 3. the host
rows = [
    ("R1  hub router",        "Catalyst 8000V", "4 vCPU", "8,192 MB"),
    ("R2  spoke router",      "Catalyst 8000V", "4 vCPU", "8,192 MB"),
    ("R3  spoke router",      "Catalyst 8000V", "4 vCPU", "8,192 MB"),
    ("NMS  management server","Ubuntu 24.04",   "1 vCPU", "1,024 MB"),
    ("H1 / H2 / H3  end hosts","CirrOS 0.6.2",  "1 vCPU", "256 MB each"),
]
items = [R(0, 0, W, H, fill=MIST)]
items += title_block("One Linux host carries the whole lab",
                     "No dedicated hardware, no cloud spend, no lab booking")
items += [R(0.75, 1.78, 4.25, 4.55, fill=INK, radius=0.09, shadow=True),
          T(1.10, 2.06, 3.6, 0.3, "THE HOST", size=11, bold=True, color=TEAL)]
host_rows = [("CPU", "12 cores, KVM accelerated"), ("Memory", "57 GB total"),
             ("Storage", "732 GB (36 GB used)"), ("Hypervisor", "QEMU 10.2.1, -cpu host"),
             ("Guest access", "/dev/kvm, no root needed")]
yy = 2.52
for k, v in host_rows:
    items += [T(1.10, yy, 3.6, 0.26, k.upper(), size=9.5, bold=True, color=MUTED),
              T(1.10, yy + 0.26, 3.6, 0.30, v, size=13, color=WHITE)]
    yy += 0.80
items += [R(5.28, 1.78, 7.30, 3.62, fill=WHITE, radius=0.09, line=LINE, shadow=True),
          T(5.60, 2.02, 6.7, 0.32, "How the 57 GB is spent", size=15, bold=True, font=HEAD),
          R(5.60, 2.48, 6.68, 0.30, fill=MIST, radius=0.05),
          T(5.72, 2.48, 2.9, 0.30, "VIRTUAL MACHINE", size=9.5, bold=True, color=MUTED, va="c"),
          T(8.65, 2.48, 1.8, 0.30, "IMAGE", size=9.5, bold=True, color=MUTED, va="c"),
          T(10.30, 2.48, 0.85, 0.30, "CPU", size=9.5, bold=True, color=MUTED, va="c"),
          T(11.15, 2.48, 1.15, 0.30, "RAM", size=9.5, bold=True, color=MUTED, va="c", align="r")]
yy = 2.86
for name, img, cpu, ram in rows:
    items += [T(5.72, yy, 2.9, 0.30, name, size=11.5, va="c", bold=name.startswith(("R1", "R2", "R3"))),
              T(8.65, yy, 1.8, 0.30, img, size=11, color=MUTED, va="c"),
              T(10.30, yy, 0.85, 0.30, cpu, size=11, color=MUTED, va="c"),
              T(11.15, yy, 1.15, 0.30, ram, size=11, va="c", align="r"),
              L(5.60, yy + 0.38, 12.28, yy + 0.38, color=LINE, w=0.75)]
    yy += 0.42
items += [T(5.72, yy + 0.04, 4.0, 0.30, "Total committed", size=11.5, bold=True, va="c"),
          T(11.15, yy + 0.04, 1.15, 0.30, "25.8 GB", size=11.5, bold=True, color=TEAL, va="c", align="r")]
items += [R(5.28, 5.58, 7.30, 1.05, fill=WHITE, radius=0.09, line=LINE, shadow=True),
          C(5.60, 5.86, 0.13, AMBER),
          T(5.92, 5.76, 6.4, 0.28, "The one real constraint", size=13, bold=True, font=HEAD),
          T(5.92, 6.06, 6.4, 0.48,
            "Two labs of this size cannot run at once — 25.8 GB each against 57 GB. "
            "The DMVPN and VTI labs alternate.", size=11.5, color=MUTED, lh=1.28)]
add(*items)

# ------------------------------------------------------------- 4. topology
it = [R(0, 0, W, H, fill=MIST)]
it += title_block("The network under test",
                  "Hub-and-spoke DMVPN over a shared WAN, with an out-of-band management plane")

# WAN segment
it += [R(0.75, 1.80, 11.83, 1.36, fill=WHITE, radius=0.09, line=LINE),
       T(1.02, 1.94, 3.2, 0.26, "WAN  100.64.0.0/24", size=10.5, bold=True, color=MUTED),
       L(1.05, 2.72, 12.28, 2.72, color=MUTED, w=1.5)]
routers = [("R1", "hub", 2.55, "100.64.0.1", "AS 65001", TEAL),
           ("R2", "spoke", 6.35, "100.64.0.2", "AS 65002", TEAL_D),
           ("R3", "spoke", 10.15, "100.64.0.3", "AS 65003", TEAL_D)]
for name, role, x, wan, asn, col in routers:
    it += [L(x + 0.85, 2.72, x + 0.85, 3.30, color=MUTED, w=1.25),
           R(x, 3.30, 1.70, 0.92, fill=INK, radius=0.08, shadow=True),
           T(x, 3.40, 1.70, 0.34, name, size=19, bold=True, color=WHITE, align="c", font=HEAD),
           T(x, 3.74, 1.70, 0.26, role, size=10, color=TEAL, align="c"),
           T(x, 4.00, 1.70, 0.22, asn, size=9, color=MUTED, align="c"),
           T(x - 0.30, 2.42, 2.30, 0.24, wan, size=9.5, color=MUTED, align="c")]

# DMVPN overlay
it += [R(2.55, 4.42, 9.30, 0.60, fill=WHITE, radius=0.08, line=TEAL, lw=1.5),
       T(2.75, 4.42, 4.4, 0.60, "DMVPN overlay  Tunnel0  172.20.0.0/24",
         size=11.5, bold=True, color=TEAL_D, va="c"),
       T(7.20, 4.42, 4.5, 0.60, "mGRE + IPsec + NHRP  ·  eBGP over the tunnel",
         size=10.5, color=MUTED, va="c", align="r")]
it += [T(2.55, 5.06, 9.30, 0.26,
         "Spokes register with the hub, then build direct spoke-to-spoke tunnels on demand",
         size=10, color=MUTED, align="c", italic=True)]

# LANs and hosts
lans = [("H1", "192.168.10.0/24", 2.55), ("H2", "192.168.20.0/24", 6.35), ("H3", "192.168.30.0/24", 10.15)]
for hn, net, x in lans:
    it += [L(x + 0.85, 5.38, x + 0.85, 5.72, color=MUTED, w=1.25),
           R(x, 5.72, 1.70, 0.62, fill=WHITE, radius=0.08, line=LINE),
           T(x, 5.78, 1.70, 0.28, hn, size=12.5, bold=True, align="c"),
           T(x, 6.04, 1.70, 0.24, net, size=8.5, color=MUTED, align="c")]

# OOB management plane
it += [R(0.75, 6.52, 11.83, 0.72, fill=INK, radius=0.09),
       T(1.05, 6.52, 3.6, 0.72, "OOB management  192.168.99.0/24",
         size=11, bold=True, color=TEAL, va="c"),
       T(4.85, 6.52, 4.2, 0.72, "VRF MGMT on every router", size=11, color=WHITE, va="c"),
       R(9.30, 6.66, 3.0, 0.44, fill=TEAL, radius=0.06),
       T(9.30, 6.66, 3.0, 0.44, "NMS  ·  192.168.99.10", size=10.5, bold=True,
         color=WHITE, align="c", va="c")]
add(*it)

# ---------------------------------------------------- 5. how a VM is spun up
it = [R(0, 0, W, H, fill=MIST)]
it += title_block("How a router VM is started",
                  "One shell script, one QEMU process, no hypervisor GUI and no orchestration layer")
steps = [
    ("1", "Copy-on-write disk",
     "qemu-img creates a thin overlay backed by the shared 1.9 GB c8000v image. "
     "Each router gets a private disk; the golden image is never written to."),
    ("2", "Day-0 configuration ISO",
     "Hostname, credentials and management addressing are burned to a small ISO and "
     "attached as a CD-ROM. IOS-XE reads it only when NVRAM is empty — a genuinely fresh boot."),
    ("3", "Network interfaces",
     "Four virtio NICs: a user-mode NAT link for the harness, plus WAN, LAN and OOB "
     "attached to shared multicast segments."),
    ("4", "Launch under KVM",
     "-machine pc,accel=kvm -cpu host -smp 4 -m 8192, daemonized with a PID file. "
     "Serial console is exposed over telnet for boot-time diagnosis."),
    ("5", "Wait for readiness",
     "The harness polls the forwarded SSH port until the device answers and settles, "
     "rather than sleeping a fixed interval."),
]
y = 1.72
for n, head, body in steps:
    it += [C(0.78, y + 0.04, 0.40, TEAL, text=n, size=14),
           T(1.42, y, 5.6, 0.30, head, size=14.5, bold=True, font=HEAD),
           T(1.42, y + 0.32, 5.55, 0.62, body, size=11.5, color=MUTED, lh=1.30)]
    y += 1.02
it += [R(7.45, 1.72, 5.13, 4.62, fill=INK, radius=0.09, shadow=True),
       T(7.75, 1.96, 4.6, 0.28, "start-vm.sh  — the essential flags", size=11.5,
         bold=True, color=TEAL)]
code = [
    ("qemu-system-x86_64 \\", WHITE),
    ("  -machine pc,accel=kvm \\", "9FB6C0"),
    ("  -cpu host -smp 4 -m 8192 \\", "9FB6C0"),
    ("  -drive if=virtio,file=run/R1.qcow2 \\", "9FB6C0"),
    ("  -drive if=ide,media=cdrom,\\", "9FB6C0"),
    ("         file=run/R1-day0.iso \\", "9FB6C0"),
    ("", WHITE),
    ("  # harness reaches the device here", MUTED),
    ("  -netdev user,id=mgmt,\\", TEAL),
    ("     hostfwd=tcp:127.0.0.1:2221-:22 \\", TEAL),
    ("", WHITE),
    ("  # shared L2 segments between VMs", MUTED),
    ("  -netdev socket,id=wan,\\", TEAL),
    ("     mcast=230.10.64.1:10064 \\", TEAL),
    ("  -netdev socket,id=lan,... \\", "9FB6C0"),
    ("  -netdev socket,id=oob,... \\", "9FB6C0"),
    ("", WHITE),
    ("  -serial telnet:127.0.0.1:5001 \\", "9FB6C0"),
    ("  -display none -daemonize", "9FB6C0"),
]
yy = 2.42
for ln, col in code:
    if ln:
        it.append(T(7.75, yy, 4.65, 0.21, ln, size=9.5, color=col, font=MONO))
    yy += 0.205
add(*it)

# ------------------------------------------------------- 6. virtual wiring
it = [R(0, 0, W, H, fill=MIST)]
it += title_block("How the virtual machines are wired together",
                  "There is no virtual switch — QEMU multicast sockets act as shared network segments")
it += [R(0.75, 1.74, 6.05, 2.30, fill=WHITE, radius=0.09, line=LINE, shadow=True),
       T(1.05, 1.98, 5.5, 0.30, "The problem", size=15, bold=True, font=HEAD),
       T(1.05, 2.32, 5.45, 1.55,
         "A point-to-point socket connects exactly two VMs, which is fine for a "
         "back-to-back link but wrong for a shared segment. Three routers on one WAN, "
         "or a router and its host on a LAN, need every frame to reach every member — "
         "including broadcast and multicast, which NHRP and routing protocols rely on.",
         size=12, color=MUTED, lh=1.34)]
it += [R(7.03, 1.74, 5.55, 2.30, fill=INK, radius=0.09, shadow=True),
       T(7.33, 1.98, 5.0, 0.30, "The mechanism", size=15, bold=True, color=WHITE, font=HEAD),
       T(7.33, 2.32, 4.95, 1.55,
         "Each segment is a multicast group on the loopback interface. Every VM "
         "attached to that group sees every frame, exactly like a hub. Pinning to "
         "127.0.0.1 keeps all lab traffic inside the host — nothing reaches the "
         "physical network.",
         size=12, color="A9BCC5", lh=1.34)]
it += [R(0.75, 4.14, 11.83, 2.72, fill=WHITE, radius=0.09, line=LINE, shadow=True),
       R(1.05, 4.40, 11.23, 0.32, fill=MIST, radius=0.05),
       T(1.20, 4.40, 2.5, 0.32, "SEGMENT", size=9.5, bold=True, color=MUTED, va="c"),
       T(3.85, 4.40, 2.4, 0.32, "SUBNET", size=9.5, bold=True, color=MUTED, va="c"),
       T(6.40, 4.40, 2.5, 0.32, "TRANSPORT", size=9.5, bold=True, color=MUTED, va="c"),
       T(9.10, 4.40, 3.1, 0.32, "MEMBERS", size=9.5, bold=True, color=MUTED, va="c")]
segs = [("WAN", "100.64.0.0/24", "mcast 230.10.64.1", "R1, R2, R3"),
        ("LAN per site", "192.168.10/20/30.0/24", "mcast 230.10.x0.1", "one router + its host"),
        ("OOB management", "192.168.99.0/24", "mcast 230.10.99.1", "R1, R2, R3, NMS"),
        ("Harness access", "10.0.2.0/24", "user-mode NAT, hostfwd", "each VM, individually")]
yy = 4.82
for a, b, c, d in segs:
    it += [T(1.20, yy, 2.6, 0.30, a, size=11.5, bold=True, va="c"),
           T(3.85, yy, 2.5, 0.30, b, size=11, color=MUTED, va="c", font=MONO),
           T(6.40, yy, 2.6, 0.30, c, size=11, color=MUTED, va="c", font=MONO),
           T(9.10, yy, 3.1, 0.30, d, size=11, color=MUTED, va="c"),
           L(1.05, yy + 0.36, 12.28, yy + 0.36, color=LINE, w=0.75)]
    yy += 0.40
it += [T(1.20, yy + 0.02, 11.0, 0.28,
         "SSH on 2221-2223 reaches the routers, 2231-2233 the hosts, 2241 the NMS — every device addressable from the harness.",
         size=10.5, color=MUTED, italic=True, va="c")]
add(*it)

# --------------------------------------------------- 7. provisioning phases
it = [R(0, 0, W, H, fill=MIST)]
it += title_block("From factory image to configured network",
                  "Ten ordered phases, each idempotent and independently re-runnable")
phases = [("license", "Boot level + reload"), ("dmvpn", "mGRE, IPsec, NHRP"),
          ("bgp", "eBGP, MD5, BFD, policy"), ("nat", "Static + dynamic pools"),
          ("ntp", "Time sync via OOB"), ("syslog", "Export to NMS"),
          ("snmp", "v3 authPriv + traps"), ("aaa", "TACACS+ authentication"),
          ("vty", "Line access control"), ("banner", "Pre-login notice")]
x, y = 0.75, 1.80
for i, (name, desc) in enumerate(phases):
    col = i % 5
    cx = 0.75 + col * 2.42
    cy = 1.80 if i < 5 else 3.30
    it += [R(cx, cy, 2.18, 1.22, fill=WHITE, radius=0.09, line=LINE, shadow=True),
           C(cx + 0.24, cy + 0.22, 0.34, TEAL if i < 5 else TEAL_D, text=str(i + 1), size=12),
           T(cx + 0.66, cy + 0.24, 1.40, 0.30, name, size=13.5, bold=True, font=MONO),
           T(cx + 0.22, cy + 0.66, 1.80, 0.44, desc, size=10, color=MUTED, lh=1.24)]
    if col < 4:
        it.append(L(cx + 2.18, cy + 0.61, cx + 2.42, cy + 0.61, color=MUTED, w=1.25))
it += [R(0.75, 4.86, 11.83, 0.92, fill=INK, radius=0.09),
       C(1.05, 5.10, 0.13, TEAL),
       T(1.38, 5.02, 10.9, 0.28, "Why the licence phase comes first", size=13, bold=True, color=WHITE, font=HEAD),
       T(1.38, 5.32, 10.9, 0.28,
         "The cryptographic CLI does not exist until the boot level is active, and the boot level only takes effect on reload.",
         size=11.5, color="A9BCC5")]
it += [R(0.75, 6.00, 11.83, 0.92, fill=WHITE, radius=0.09, line=LINE, shadow=True),
       C(1.05, 6.24, 0.13, AMBER),
       T(1.38, 6.16, 10.9, 0.28, "Teardown and configuration are applied separately", size=13, bold=True, font=HEAD),
       T(1.38, 6.46, 10.9, 0.28,
         "Removing an object that is not there is a harmless no-op; a rejected configuration line is a fault worth stopping for.",
         size=11.5, color=MUTED)]
add(*it)

# ------------------------------------------------- 8. feature stack tested
it = [R(0, 0, W, H, fill=MIST)]
it += title_block("What the network actually does",
                  "Every feature below is configured by the harness and verified by it")
feats = [
    ("Overlay & encryption", TEAL,
     "Multipoint GRE with IPsec protection, IKEv2 with a wildcard keyring, NHRP "
     "registration and Phase 3 shortcut switching between spokes."),
    ("Routing & policy", TEAL,
     "eBGP across the tunnel with MD5 authentication and BFD. Outbound prefix-lists, "
     "community tagging, inbound community and AS-path filtering, maximum-prefix limits."),
    ("Address translation", TEAL,
     "Static one-to-one mappings and a dynamic pool with overload, including pool "
     "exhaustion behaviour under deliberate pressure."),
    ("Management plane", TEAL_D,
     "A dedicated out-of-band network in VRF MGMT carrying NTP, syslog and SNMPv3 "
     "authPriv polling and traps to the NMS."),
    ("Identity & access", TEAL_D,
     "TACACS+ authentication against a real server, per-line access control, and a "
     "pre-login banner verified on every device."),
    ("Failure behaviour", CORAL,
     "Hub loss, underlay partition, key mismatches, MTU blackholes and cache expiry — "
     "what the design does when something breaks."),
]
for i, (head, col, body) in enumerate(feats):
    cx = 0.75 + (i % 3) * 4.03
    cy = 1.78 + (i // 3) * 2.42
    it += card(cx, cy, 3.78, 2.20, head, body, accent=col, hsize=14.5, bsize=11.5)
it += [T(0.75, 6.72, 11.83, 0.30,
         "The management, identity and failure work is what turns a connectivity demo into something an operations team can rely on.",
         size=11.5, color=MUTED, italic=True)]
add(*it)

# ----------------------------------------------------- 9. how tests are run
it = [R(0, 0, W, H, fill=MIST)]
it += title_block("How a test run works",
                  "One command, driven entirely over SSH — the same interface an engineer would use")
flow = [("./run-tests.sh", "Loads lab.env and passes every address, port and\ncredential to the test runner as a variable."),
        ("Robot Framework", "Executes 23 suites in order. Shared keywords live in a\nresource file; Python libraries handle SNMP, NETCONF and NAT."),
        ("SSH driver", "A reload-safe client opens a session per device, detects the\nprompt, and distinguishes a real refusal from a benign notice."),
        ("Devices & NMS", "Commands run on the live routers, hosts and management\nserver. Nothing is mocked or replayed."),
        ("Archive & report", "State captures, logs, a numbered evidence PDF and the\ntopology diagram are written to a timestamped folder.")]
y = 1.80
for i, (head, body) in enumerate(flow):
    it += [R(0.75, y, 7.55, 0.88, fill=WHITE if i else INK, radius=0.09, line=LINE if i else None, shadow=True),
           C(1.05, y + 0.25, 0.38, TEAL if i else WHITE, text=str(i + 1),
             size=13, color=WHITE if i else INK),
           T(1.60, y + 0.13, 2.5, 0.30, head, size=13.5, bold=True,
             color=INK if i else WHITE, font=MONO if i == 0 else HEAD),
           T(4.15, y + 0.11, 3.95, 0.68, body.replace("\n", " "), size=10.5,
             color=MUTED if i else "A9BCC5", lh=1.26)]
    if i < 4:
        it.append(L(1.24, y + 0.88, 1.24, y + 1.02, color=MUTED, w=1.25))
    y += 1.02
it += [R(8.62, 1.80, 3.96, 4.36, fill=WHITE, radius=0.09, line=LINE, shadow=True),
       T(8.92, 2.04, 3.4, 0.30, "Design rules", size=15, bold=True, font=HEAD)]
rules = ["Wait for a condition, never sleep a fixed interval",
         "Assert on behaviour, not on configuration text",
         "Every destructive test restores what it broke",
         "Restoration ends when traffic moves again, not when config returns",
         "Probe the device before writing the assertion"]
it += [B(8.92, 2.42, 3.42, 3.6, rules, size=11.5, color=MUTED, gap=0.48)]
add(*it)

# ------------------------------------------------------ 10. suite inventory
it = [R(0, 0, W, H, fill=MIST)]
it += title_block("The 23 suites",
                  "215 tests, every one passing on the reference run of 8 September 2026")
suites = [("01", "Platform", 5), ("02", "Configuration", 5), ("03", "WAN", 6),
          ("04", "DMVPN", 13), ("05", "Capture state", 12), ("06", "Wire encryption", 3),
          ("07", "IPsec negative", 3), ("08", "Management API", 6), ("09", "BGP", 26),
          ("10", "Host to host", 10), ("11", "Throughput", 3), ("12", "NAT", 10),
          ("13", "NAT pool", 13), ("14", "NTP", 12), ("15", "Syslog", 10),
          ("16", "SNMPv3", 13), ("17", "SNMP polling", 14), ("18", "MTU", 8),
          ("19", "Out of band", 9), ("20", "TACACS+", 12), ("21", "VTY ACL", 9),
          ("22", "Banner", 6), ("23", "Destructive", 7)]
for i, (num, name, n) in enumerate(suites):
    col, row = i // 8, i % 8
    if i >= 16:
        col, row = 2, i - 16
    cx = 0.75 + col * 4.03
    cy = 1.76 + row * 0.505
    hot = num in ("23",)
    it += [R(cx, cy, 3.78, 0.44, fill=WHITE, radius=0.06, line=LINE),
           T(cx + 0.16, cy, 0.42, 0.44, num, size=11, bold=True,
             color=CORAL if hot else TEAL, va="c", font=MONO),
           T(cx + 0.62, cy, 2.35, 0.44, name, size=11.5, va="c",
             bold=hot),
           R(cx + 3.06, cy + 0.10, 0.54, 0.24, fill=MIST, radius=0.12),
           T(cx + 3.06, cy + 0.10, 0.54, 0.24, str(n), size=10, bold=True,
             color=MUTED, align="c", va="c")]
it += [R(8.81, 5.80, 3.77, 1.04, fill=INK, radius=0.09, shadow=True),
       T(9.11, 5.96, 3.2, 0.30, "215 / 215", size=22, bold=True, color=TEAL, font=HEAD),
       T(9.11, 6.32, 3.2, 0.26, "24.2 minutes, end to end", size=11, color="A9BCC5")]
it += [T(0.75, 6.00, 7.6, 0.72,
         "BGP is the largest suite at 26 tests, because routing policy has the most ways "
         "to be quietly wrong: a community that is not stripped, an AS-path filter that "
         "permits what it should drop, a prefix-list that never matches.",
         size=11.5, color=MUTED, lh=1.32)]
add(*it)

# ---------------------------------------------------------- 11. tech stack
it = [R(0, 0, W, H, fill=MIST)]
it += title_block("The technology stack", "Open source throughout, except the router image itself")
groups = [
    ("Virtualisation", TEAL, [("QEMU", "10.2.1"), ("KVM", "hardware accel"),
                              ("virtio-net", "guest NICs"), ("cloud-init", "NMS + host seed")]),
    ("Network operating system", TEAL, [("Catalyst 8000V", "IOS-XE 17.15.06"),
                                        ("CirrOS", "0.6.2 end hosts"),
                                        ("Ubuntu", "24.04 minimal, NMS")]),
    ("Test harness", TEAL_D, [("Robot Framework", "7.3.2"), ("Python", "3.14.4"),
                              ("Paramiko / SSHLibrary", "device sessions"),
                              ("pyATS + Genie", "26.8, parsers")]),
    ("Protocol tooling", TEAL_D, [("pysnmp", "7.1.22"), ("ncclient", "0.7.1, NETCONF"),
                                  ("requests", "2.34, RESTCONF"), ("reportlab", "5.0.1, reports")]),
    ("Management services", AMBER, [("rsyslog", "log collection"), ("snmptrapd", "trap receiver"),
                                    ("chrony", "NTP server"), ("tac_plus", "TACACS+ server")]),
    ("Reporting", AMBER, [("Robot log + report", "HTML"), ("Evidence PDF", "numbered, per test"),
                          ("Topology PDF", "generated diagram"), ("Headless Chrome", "HTML to PDF")]),
]
for i, (head, col, rows_) in enumerate(groups):
    cx = 0.75 + (i % 3) * 4.03
    cy = 1.78 + (i // 3) * 2.42
    it += [R(cx, cy, 3.78, 2.22, fill=WHITE, radius=0.09, line=LINE, shadow=True),
           R(cx + 0.28, cy + 0.30, 0.11, 0.11, fill=col, radius=0.055),
           T(cx + 0.50, cy + 0.20, 3.1, 0.30, head, size=14, bold=True, font=HEAD)]
    yy = cy + 0.68
    for a, b in rows_:
        it += [T(cx + 0.30, yy, 2.0, 0.28, a, size=11, bold=True, va="c"),
               T(cx + 2.20, yy, 1.36, 0.28, b, size=10, color=MUTED, va="c", align="r")]
        yy += 0.36
add(*it)

# ------------------------------------------------------------ 12. evidence
it = [R(0, 0, W, H, fill=MIST)]
it += title_block("What every run leaves behind",
                  "A timestamped archive, so any past result can be re-examined rather than recalled")
arts = [("Numbered evidence PDF",
         "Each of the 215 tests appears as a numbered entry — 23.01, 23.02 and so on — "
         "with its setup, acceptance criteria, the commands that checked it, and its teardown."),
        ("Device state captures",
         "Running configuration, routing and BGP tables, crypto sessions, NAT translations, "
         "NTP and SNMP state, taken from every router at the same point in the run."),
        ("Management server evidence",
         "Syslog received, SNMP polling output and trap records, collected from the NMS "
         "rather than from the device that claims to have sent them."),
        ("Robot log and report",
         "Every command and its output, keyword by keyword, for any test that needs "
         "to be understood after the fact.")]
for i, (h, b) in enumerate(arts):
    cx = 0.75 + (i % 2) * 6.05
    cy = 1.78 + (i // 2) * 1.72
    it += card(cx, cy, 5.78, 1.52, h, b, accent=TEAL, hsize=14.5, bsize=11.5)
it += [R(0.75, 5.32, 11.83, 1.42, fill=INK, radius=0.09, shadow=True),
       T(1.10, 5.56, 4.4, 0.32, "Evidence over recollection", size=15, bold=True,
         color=WHITE, font=HEAD),
       T(1.10, 5.94, 5.2, 0.66,
         "The archive is what lets a result be challenged. Twice this month a suite was "
         "found to be passing for the wrong reason — both times by reading the evidence, "
         "not by watching a test fail.",
         size=11.5, color="A9BCC5", lh=1.30),
       T(7.05, 5.56, 5.3, 0.32, "One run kept in version control", size=15, bold=True,
         color=WHITE, font=HEAD),
       T(7.05, 5.94, 5.3, 0.66,
         "The repository carries the latest full run as its reference. When the code "
         "changes, that archive is regenerated — so the published evidence always "
         "matches the tests that produced it.",
         size=11.5, color="A9BCC5", lh=1.30)]
add(*it)

# --------------------------------------------------------- 13. destructive
it = [R(0, 0, W, H, fill=INK)]
it += [T(0.75, 0.52, 11.9, 0.62, "Breaking it on purpose", size=32, bold=True,
         color=WHITE, font=HEAD),
       T(0.75, 1.14, 11.9, 0.34,
         "Seven tests that take the fabric apart while traffic is running, and assert what is still standing",
         size=14, color="8FA6B1")]
dest = [("Hub loss", "The direct spoke-to-spoke tunnel survives — but the routing that used it does not."),
        ("Hub recovery", "Registration, BGP and the shortcut all return with no operator action."),
        ("Underlay partition", "Spokes that cannot reach each other fall back through the hub."),
        ("NHRP key mismatch", "Registration is refused outright."),
        ("Tunnel key mismatch", "Silently discarded — the interface still reports itself up."),
        ("MTU blackhole", "Suppress the too-big message and large traffic fails with no diagnostic."),
        ("Cache expiry", "Shortcuts are soft state and age out when traffic stops justifying them.")]
for i, (h, b) in enumerate(dest):
    cx = 0.75 + (i % 2) * 6.05
    cy = 1.80 + (i // 2) * 0.92
    w = 5.78 if i < 6 else 11.83
    it += [R(cx, cy, w, 0.84, fill=INK2, radius=0.08),
           C(cx + 0.26, cy + 0.34, 0.13, CORAL),
           T(cx + 0.52, cy + 0.10, w - 0.80, 0.28, h, size=13, bold=True, color=WHITE, font=HEAD),
           T(cx + 0.52, cy + 0.40, w - 0.80, 0.34, b, size=11, color="8FA6B1")]
it += [R(0.75, 5.62, 11.83, 1.34, fill=TEAL_D, radius=0.09),
       T(1.10, 5.82, 11.2, 0.30, "The finding that changed a test", size=13.5, bold=True, color=WHITE, font=HEAD),
       T(1.10, 6.14, 11.2, 0.70,
         "Losing the hub was expected to prove resilience. Probing showed the opposite half is also true: "
         "the tunnel survives, but both spokes learn routes only from the hub, so the prefixes withdraw and "
         "the healthy tunnel carries nothing. Written as a resilience claim, the test would have passed while saying something false.",
         size=11, color="D5EEEA", lh=1.26)]
add(*it)

# ---------------------------------------------------- 14. what it caught
it = [R(0, 0, W, H, fill=MIST)]
it += title_block("What the work has caught so far",
                  "The defects that matter most were in the tests, not in the network")
finds = [
    ("An assertion that could not fail", CORAL,
     "Two shared keywords proving a ping was lossless checked for the text "
     "\"0% packet loss\" — which is contained in \"100% packet loss\", and in \"20% packet loss\". "
     "They accepted any loss ending in a zero, across 16 call sites in three suites. Now anchored and fixed in both labs."),
    ("A teardown that finished too early", AMBER,
     "Destructive tests restored the configuration and waited for the tunnel to register — "
     "but BGP rides that tunnel and needs about a minute more. Later tests began against a "
     "network that looked healthy and carried nothing. Teardowns now wait for traffic to move."),
    ("A control that never applied", AMBER,
     "An outbound access list was meant to block the router's \"fragmentation needed\" message. "
     "Outbound lists do not filter traffic the router originates, so it did nothing. "
     "The message is now suppressed at its source, which is also the more realistic fault."),
]
y = 1.78
for h, col, b in finds:
    it += [R(0.75, y, 11.83, 1.38, fill=WHITE, radius=0.09, line=LINE, shadow=True),
           C(1.05, y + 0.32, 0.13, col),
           T(1.38, y + 0.22, 10.9, 0.30, h, size=15, bold=True, font=HEAD),
           T(1.38, y + 0.58, 10.85, 0.68, b, size=11.5, color=MUTED, lh=1.30)]
    y += 1.54
it += [R(0.75, 6.42, 11.83, 0.62, fill=INK, radius=0.09),
       T(1.10, 6.42, 11.2, 0.62,
         "A test suite is itself software, and it needs the same scepticism as the network it measures.",
         size=13, bold=True, color=WHITE, va="c", font=HEAD)]
add(*it)

# ------------------------------------------------------------- 15. closing
it = [R(0, 0, W, H, fill=INK)]
it += [R(0, 0, W, 3.30, fill=INK2),
       T(0.85, 0.92, 11.4, 0.34, "WHERE IT STANDS", size=12.5, bold=True, color=TEAL),
       T(0.85, 1.34, 11.4, 0.72, "Ready to use, and honest about its limits",
         size=38, bold=True, color=WHITE, font=HEAD),
       T(0.85, 2.24, 10.8, 0.66,
         "Both labs are in version control with their reference runs. The DMVPN lab is "
         "current and fully green; the VTI lab carries one fix that has not yet been "
         "exercised against hardware.",
         size=14, color="B9C7CE", lh=1.34)]
cols = [("Complete", TEAL, ["DMVPN lab: 215 / 215 passing",
                            "Destructive coverage: 7 scenarios",
                            "Evidence PDF numbered and structured",
                            "Both repositories pushed"]),
        ("Open", AMBER, ["VTI lab fix committed but not re-run",
                         "Two labs cannot run at once — 25.8 GB each",
                         "Reference archive is ~86 MB per swap"]),
        ("Next", WHITE, ["Bring the VTI lab up and re-verify",
                         "Decide whether raw run data stays in git",
                         "Extend destructive coverage to the VTI design"])]
for i, (h, col, items) in enumerate(cols):
    cx = 0.85 + i * 3.95
    it += [T(cx, 3.72, 3.5, 0.30, h.upper(), size=11.5, bold=True, color=col),
           L(cx, 4.06, cx + 3.55, 4.06, color="33454F", w=1)]
    yy = 4.26
    for s in items:
        it += [C(cx + 0.04, yy + 0.06, 0.13, col),
               T(cx + 0.34, yy - 0.02, 3.2, 0.56, s, size=11.5, color="B9C7CE", lh=1.26)]
        yy += 0.62
it += [L(0.85, 6.66, 12.5, 6.66, color="33454F", w=1),
       T(0.85, 6.82, 8.0, 0.30, "Cisco Catalyst 8000V DMVPN testbed  ·  8 September 2026",
         size=11, color=MUTED),
       T(8.5, 6.82, 4.0, 0.30, "215 tests  ·  23 suites  ·  24 minutes",
         size=11, color=TEAL, align="r", bold=True)]
add(*it)
