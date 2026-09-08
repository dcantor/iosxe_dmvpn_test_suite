# A loopback is the honest minimum for proving a push: it is real configuration
# with an address that either appears in the routing table or does not, it is
# unambiguous to verify from the CLI, and it touches nothing the rest of the
# suite depends on.
resource "iosxe_interface_loopback" "managed" {
  for_each = var.routers

  device            = each.key
  name              = var.loopback_id
  description       = "Managed by Terraform"
  ipv4_address      = each.value.loopback_ip
  ipv4_address_mask = "255.255.255.255"
  shutdown          = false
}

# A second resource of a different shape. The loopback is a flat object; this is
# a list of ordered entries, which is where a provider is most likely to disagree
# with the device about what the configuration currently says.
resource "iosxe_access_list_standard" "managed" {
  for_each = var.routers

  device = each.key
  name   = var.managed_acl_name

  entries = [
    {
      sequence = 10
      remark   = "Managed by Terraform"
    },
    {
      sequence           = 20
      permit_prefix      = "10.99.0.0"
      permit_prefix_mask = "0.0.255.255"
    },
    {
      sequence = 30
      deny_any = true
    },
  ]
}
