"""Robot keywords for the Network-as-Code Terraform module.

The sibling suite drives hand-written Terraform resources over RESTCONF. This
one drives the netascode/nac-iosxe module, where the configuration is a YAML
data model rather than a set of resources, and the transport is NETCONF.

The transport difference is not a preference. The module requires the iosxe
provider at 1.0.0 or newer, and 1.0.0 removed RESTCONF: the protocol and url
attributes are gone and the default port is 830. Anything built on this module
speaks NETCONF whether it meant to or not.

Credentials go in as environment variables. The module declares its own provider
block and feeds it only the device list rendered from the YAML, so there is no
Terraform variable to pass them through.
"""
import os
import shutil
import subprocess
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LAB_DIR = os.path.dirname(TOOLS_DIR)
NAC_DIR = os.path.join(LAB_DIR, "terraform-nac")

PLAN_CLEAN, PLAN_ERROR, PLAN_CHANGES = 0, 1, 2


def _sibling(name):
    """Import a module from tools/ at call time.

    Robot restores a saved sys.path after importing a library by file path, so
    anything added at module scope is undone before a keyword ever runs.
    """
    if TOOLS_DIR not in sys.path:
        sys.path.insert(0, TOOLS_DIR)
    return __import__(name)


def _binary():
    for candidate in (os.environ.get("TERRAFORM_BIN"),
                      shutil.which("terraform"),
                      os.path.expanduser("~/bin/terraform")):
        if candidate and os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    raise AssertionError("terraform not found; set TERRAFORM_BIN or put it on PATH")


class nac_keywords:
    ROBOT_LIBRARY_SCOPE = "SUITE"

    def _env(self):
        provision = _sibling("provision")
        lab = provision.load_env()
        return {
            **os.environ,
            "TF_IN_AUTOMATION": "1",
            "TF_INPUT": "0",
            "IOSXE_USERNAME": lab["VM_USER"],
            "IOSXE_PASSWORD": lab["VM_PASS"],
        }

    def _run(self, *args, timeout=600):
        proc = subprocess.run([_binary(), *args, "-no-color"], cwd=NAC_DIR,
                              capture_output=True, text=True, timeout=timeout,
                              env=self._env())
        return proc.returncode, proc.stdout + proc.stderr

    def render_nac_model(self):
        """Rebuild iosxe.nac.yaml from lab.env."""
        _sibling("nac_yaml").main()

    def nac_init(self):
        rc, out = self._run("init", "-upgrade")
        assert rc == 0, f"terraform init failed:\n{out}"
        return out

    def nac_validate(self):
        rc, out = self._run("validate")
        assert rc == 0, f"terraform validate failed:\n{out}"
        return out

    def nac_apply(self):
        rc, out = self._run("apply", "-auto-approve")
        assert rc == 0, f"terraform apply failed:\n{out}"
        return out

    def nac_destroy(self):
        rc, out = self._run("destroy", "-auto-approve")
        assert rc == 0, f"terraform destroy failed:\n{out}"
        return out

    def nac_plan(self):
        return self._run("plan", "-detailed-exitcode")

    def nac_plan_should_be_clean(self):
        rc, out = self.nac_plan()
        assert rc != PLAN_ERROR, f"terraform plan errored:\n{out}"
        assert rc == PLAN_CLEAN, (
            "the module still proposes changes after applying its own model, so "
            f"it cannot read back what it wrote:\n{out}")
        return out

    def nac_plan_should_propose_changes(self):
        rc, out = self.nac_plan()
        assert rc != PLAN_ERROR, f"terraform plan errored:\n{out}"
        assert rc == PLAN_CHANGES, f"no drift seen when drift was introduced:\n{out}"
        return out

    def nac_state_resource_count(self):
        rc, out = self._run("state", "list")
        if rc != 0 and "No state file" in out:
            return 0
        assert rc == 0, f"terraform state list failed:\n{out}"
        return len([ln for ln in out.splitlines() if ln.strip()])

    def nac_provider_version(self):
        """The version actually locked in this working directory."""
        lock = os.path.join(NAC_DIR, ".terraform.lock.hcl")
        assert os.path.isfile(lock), "no provider lock file; run nac init first"
        with open(lock) as fh:
            text = fh.read()
        marker = 'provider "registry.terraform.io/ciscodevnet/iosxe"'
        assert marker in text, f"iosxe provider not locked in {lock}"
        after = text.split(marker, 1)[1]
        for line in after.splitlines():
            if "version" in line and "=" in line:
                return line.split("=", 1)[1].strip().strip('"')
        raise AssertionError("could not read the locked provider version")

    def read_nac_model(self):
        """The generated YAML, as a dictionary, for asserting against."""
        import yaml
        with open(os.path.join(NAC_DIR, "iosxe.nac.yaml")) as fh:
            return yaml.safe_load(fh)
