variable "username" {
  description = "Device login, supplied from lab.env -- never committed."
  type        = string
  sensitive   = true
}

variable "password" {
  description = "Device password, supplied from lab.env -- never committed."
  type        = string
  sensitive   = true
}

variable "routers" {
  description = <<-EOT
    The devices Terraform manages, keyed by the name the lab uses for them.
    host carries the forwarded RESTCONF port, because every device is reached
    through the hypervisor's NAT rather than directly.
  EOT
  type = map(object({
    host        = string
    loopback_ip = string
  }))
}

variable "loopback_id" {
  description = <<-EOT
    Deliberately high, and outside the range the provisioning phases use.
    Loopback0 and Loopback1 carry lab identity and BGP-advertised prefixes; a
    collision there would have Terraform and the harness fighting over the same
    interface, and the loser would look like a flapping test.
  EOT
  type        = number
  default     = 99
}

variable "managed_acl_name" {
  description = "Name of the standard ACL Terraform owns. Not referenced by any interface."
  type        = string
  default     = "TF-MANAGED"
}
