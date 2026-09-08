# Sourced by the lab scripts. Flattens R<n>_* settings into bare names.
# Fields absent for a role (a hub has no LINK_LOCAL) resolve to empty.
router_vars() {
  local r="${1:?usage: router_vars R1|R2|R3}"
  case " $ROUTERS " in *" $r "*) ;; *) echo "ERROR: unknown router '$r'" >&2; return 1 ;; esac
  local f v
  for f in NAME ROLE ASN SSH NETCONF RESTCONF CONSOLE LOOPBACK BGP_PREFIX \
           LAN_IP LAN_NET LAN_PORT LAN_MCAST OOB_IP OOB_INTF WAN_IP DMVPN_IP; do
    v="${r}_${f}"
    printf -v "$f" '%s' "${!v-}"
  done
  ROUTER="$r"
}
