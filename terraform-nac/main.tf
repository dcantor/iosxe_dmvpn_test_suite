# Network as Code: the configuration is data, not resources. This file only
# points the module at the model; everything that reaches the devices is
# described in iosxe.nac.yaml.
module "iosxe" {
  source  = "netascode/nac-iosxe/iosxe"
  version = ">= 1.0.0"

  yaml_files = ["iosxe.nac.yaml"]

  # Leave startup-config alone. The lab's own provisioning decides what is
  # saved; a test that quietly writes to startup-config would survive a reload
  # and outlive the run that created it.
  save_config = false
}
