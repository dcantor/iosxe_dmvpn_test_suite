output "loopbacks" {
  description = "What Terraform believes it pushed, for the test suite to check against the devices."
  value = {
    for name, r in var.routers : name => {
      interface = "Loopback${var.loopback_id}"
      address   = r.loopback_ip
    }
  }
}

output "acl_name" {
  value = var.managed_acl_name
}
