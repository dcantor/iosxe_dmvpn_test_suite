terraform {
  # The Network-as-Code module needs a newer core and a 1.x provider than the
  # hand-written configuration in ../terraform, which is one reason the two live
  # in separate working directories.
  required_version = ">= 1.9.0"
}
