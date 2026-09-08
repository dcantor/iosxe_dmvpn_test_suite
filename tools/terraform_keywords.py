"""Robot keywords for driving Terraform against the lab.

The suite's job is not to test Terraform. It is to prove that configuration
written as Terraform reaches the devices, that Terraform agrees with them
afterwards, and that it can take back what it put there. Every assertion about
what landed is made over the CLI, deliberately not through the same RESTCONF
API that performed the write -- an API confirming its own success proves only
that the API is self-consistent.
"""
import json
import os
import shutil
import subprocess
import sys

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
LAB_DIR = os.path.dirname(TOOLS_DIR)
TF_DIR = os.path.join(LAB_DIR, "terraform")


def _tf_vars():
    """Import the sibling module that renders lab.env into Terraform variables.

    The path has to be added here rather than at module scope. Robot imports a
    library given by file path with a saved copy of sys.path, and restores that
    copy once the import returns -- which silently undoes anything the module
    added to it on the way in. Doing it at call time is outside that window.
    """
    if TOOLS_DIR not in sys.path:
        sys.path.insert(0, TOOLS_DIR)
    import tf_vars
    return tf_vars

# plan --detailed-exitcode: 0 = no changes, 1 = error, 2 = changes proposed.
PLAN_CLEAN, PLAN_ERROR, PLAN_CHANGES = 0, 1, 2


def _binary():
    for candidate in (os.environ.get("TERRAFORM_BIN"),
                      shutil.which("terraform"),
                      os.path.expanduser("~/bin/terraform")):
        if candidate and os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    raise AssertionError(
        "terraform not found; set TERRAFORM_BIN or put it on PATH")


class terraform_keywords:
    ROBOT_LIBRARY_SCOPE = "SUITE"

    def _run(self, *args, timeout=600):
        proc = subprocess.run(
            [_binary(), *args, "-no-color"],
            cwd=TF_DIR, capture_output=True, text=True, timeout=timeout,
            env={**os.environ, "TF_IN_AUTOMATION": "1", "TF_INPUT": "0"},
        )
        return proc.returncode, proc.stdout + proc.stderr

    # ---- lifecycle -----------------------------------------------------
    def terraform_init(self):
        """Idempotent. Needed on a fresh clone, harmless afterwards."""
        rc, out = self._run("init", "-upgrade")
        assert rc == 0, f"terraform init failed:\n{out}"
        return out

    def terraform_validate(self):
        rc, out = self._run("validate")
        assert rc == 0, f"terraform validate failed:\n{out}"
        return out

    def terraform_formatting_is_canonical(self):
        """`fmt -check` reports files that are not in canonical form."""
        rc, out = self._run("fmt", "-check", "-recursive")
        assert rc == 0, f"terraform files are not canonically formatted:\n{out}"

    def terraform_plan(self):
        """Return (exitcode, output) using the detailed exit code."""
        return self._run("plan", "-detailed-exitcode")

    def terraform_apply(self):
        rc, out = self._run("apply", "-auto-approve")
        assert rc == 0, f"terraform apply failed:\n{out}"
        return out

    def terraform_destroy(self):
        rc, out = self._run("destroy", "-auto-approve")
        assert rc == 0, f"terraform destroy failed:\n{out}"
        return out

    # ---- introspection -------------------------------------------------
    def terraform_output(self, name):
        rc, out = self._run("output", "-json", name)
        assert rc == 0, f"terraform output {name} failed:\n{out}"
        return json.loads(out)

    def terraform_state_resource_count(self):
        rc, out = self._run("state", "list")
        if rc != 0 and "No state file" in out:
            return 0
        assert rc == 0, f"terraform state list failed:\n{out}"
        return len([ln for ln in out.splitlines() if ln.strip()])

    def plan_should_be_clean(self):
        rc, out = self.terraform_plan()
        assert rc != PLAN_ERROR, f"terraform plan errored:\n{out}"
        assert rc == PLAN_CLEAN, (
            "Terraform still proposes changes after applying its own "
            f"configuration, so the provider and the device disagree:\n{out}")
        return out

    def plan_should_propose_changes(self):
        rc, out = self.terraform_plan()
        assert rc != PLAN_ERROR, f"terraform plan errored:\n{out}"
        assert rc == PLAN_CHANGES, (
            f"Terraform saw no drift when drift was introduced:\n{out}")
        return out

    def generate_terraform_variables(self):
        """Rebuild terraform.auto.tfvars.json from lab.env."""
        _tf_vars().main()
