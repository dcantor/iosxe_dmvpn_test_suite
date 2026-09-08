#!/usr/bin/env bash
# Boots one C8000V.  usage: ./start-vm.sh R1|R2|R3
#
# NIC order fixes interface naming, so it is role-dependent:
#   every router: Gi1 mgmt | Gi2 WAN (mcast) | Gi3 LAN (mcast) | Gi4 OOB (mcast)
# All four are multicast segments or user-mode NAT, so nothing listens for
# anything and the routers may be started in any order -- unlike the VTI lab,
# where the hub owned the listening end of a link per spoke and had to be first.
set -euo pipefail
cd "$(dirname "$0")"
source ./lab.env
source ./lib.sh
router_vars "${1:?usage: $0 R1|R2|R3}"

missing=""
command -v qemu-system-x86_64 >/dev/null || missing="$missing qemu-system-x86"
command -v qemu-img          >/dev/null || missing="$missing qemu-utils"
command -v genisoimage >/dev/null || command -v xorrisofs >/dev/null || missing="$missing genisoimage"
[[ -z "$missing" ]] || { echo "ERROR: missing host packages:$missing -- run ./setup.sh" >&2; exit 1; }
[[ -r /dev/kvm && -w /dev/kvm ]] || { echo "ERROR: no access to /dev/kvm as $(whoami)." >&2; exit 1; }

IMG=$(ls images/c8000v*.qcow2 2>/dev/null | head -1 || true)
[[ -n "$IMG" ]] || { echo "ERROR: no c8000v .qcow2 in images/ (see README.md)" >&2; exit 1; }

mkdir -p run
DISK="run/${ROUTER}.qcow2"
[[ -f "$DISK" ]] || qemu-img create -q -f qcow2 -F qcow2 -b "$(realpath "$IMG")" "$DISK"
[[ -f "run/${ROUTER}-day0.iso" ]] || ./make-day0.sh "$ROUTER"

pidf="run/${ROUTER}.pid"
if [[ -f "$pidf" ]] && kill -0 "$(cat "$pidf")" 2>/dev/null; then
  echo "${ROUTER} (${NAME}) already running, pid $(cat "$pidf")"; exit 0
fi

case "$ROUTER" in R1) IDX=1 ;; R2) IDX=2 ;; R3) IDX=3 ;; esac
M=$(printf "%02d" "$IDX")

NICS=()
# Identical on every router: mgmt, WAN, LAN, OOB. The hub no longer needs a
# link per spoke, because all three attach to one shared WAN segment -- which
# is also why nothing here listens for anything, so start order no longer
# matters at all. In the VTI lab the hub had to come up first.
NICS+=( -netdev "socket,id=wan,mcast=${WAN_MCAST}:${WAN_PORT},localaddr=${MCAST_LOCALADDR}" -device "virtio-net-pci,netdev=wan,mac=52:54:00:c8:${M}:02" )
NICS+=( -netdev "socket,id=lan,mcast=${LAN_MCAST}:${LAN_PORT},localaddr=${MCAST_LOCALADDR}" -device "virtio-net-pci,netdev=lan,mac=52:54:00:c8:${M}:03" )
NICS+=( -netdev "socket,id=oob,mcast=${OOB_MCAST}:${OOB_PORT},localaddr=${MCAST_LOCALADDR}" -device "virtio-net-pci,netdev=oob,mac=52:54:00:c8:${M}:04" )

qemu-system-x86_64 \
  -name "${NAME}" \
  -machine pc,accel=kvm \
  -cpu host \
  -smp "${VM_CPUS}" \
  -m "${VM_RAM_MB}" \
  -drive if=virtio,file="${DISK}",format=qcow2,cache=writeback \
  -drive if=ide,media=cdrom,file="run/${ROUTER}-day0.iso",readonly=on \
  -netdev user,id=mgmt,hostfwd=tcp:127.0.0.1:${SSH}-:22,hostfwd=tcp:127.0.0.1:${NETCONF}-:830,hostfwd=tcp:127.0.0.1:${RESTCONF}-:443 \
  -device virtio-net-pci,netdev=mgmt,mac=52:54:00:c8:${M}:01 \
  "${NICS[@]}" \
  -serial telnet:127.0.0.1:${CONSOLE},server,nowait \
  -display none -daemonize -pidfile "$pidf"

echo "${ROUTER} (${NAME}, ${ROLE}) started, pid $(cat "$pidf")"
echo "   ssh     : ssh -p ${SSH} ${VM_USER}@127.0.0.1"
echo "   console : telnet 127.0.0.1 ${CONSOLE}"
