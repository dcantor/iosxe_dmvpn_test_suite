terraform {
  required_version = ">= 1.6"
  required_providers {
    iosxe = {
      source  = "CiscoDevNet/iosxe"
      version = "~> 0.5"
    }
  }
}
