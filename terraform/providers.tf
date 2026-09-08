# One provider, several devices. The provider addresses each by the name given
# here, which is why every resource carries a `device` argument -- there is no
# implicit "current device" to fall back on.
provider "iosxe" {
  username = var.username
  password = var.password
  insecure = true

  # The provider speaks NETCONF by default. These devices are addressed on
  # their forwarded RESTCONF port, so the protocol has to be stated -- the
  # default silently attempts an SSH handshake against an HTTPS listener.
  protocol = "restconf"

  devices = [
    for name, r in var.routers : {
      name    = name
      host    = r.host
      managed = true
    }
  ]
}
