#!/usr/bin/env python3
"""Generate Terraform variables from lab.env.

lab.env is the single source of truth for addressing and credentials, so the
Terraform side reads from it rather than repeating it. The generated file holds
the device password and is git-ignored for that reason.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from provision import load_env, routers  # noqa: E402

LAB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(LAB_DIR, "terraform", "terraform.auto.tfvars.json")


def build(env):
    return {
        "username": env["VM_USER"],
        "password": env["VM_PASS"],
        "routers": {
            r: {
                # RESTCONF is reached through the hypervisor's forwarded port,
                # the same way the harness reaches SSH.
                "host": f"127.0.0.1:{env[f'{r}_RESTCONF']}",
                # A /32 per router in a range nothing else in the lab uses.
                "loopback_ip": f"10.99.{i}.1",
            }
            for i, r in enumerate(routers(env), start=1)
        },
    }


def main():
    env = load_env()
    with open(OUT, "w") as fh:
        json.dump(build(env), fh, indent=2)
        fh.write("\n")
    os.chmod(OUT, 0o600)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
