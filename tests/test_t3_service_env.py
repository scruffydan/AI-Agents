"""Shell installer checks in isolated homes; no T3 or real credentials are used."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]


class T3ServiceEnvTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        gh = self.bin / "gh"
        gh.write_text(
            '#!/bin/sh\n[ "$1 $2 $3" = "auth git-credential get" ] || exit 9\n'
            "cat >/dev/null\nprintf 'username=fixture\\npassword=fixture\\n'\n"
        )
        gh.chmod(0o700)
        launchctl = self.bin / "launchctl"
        launchctl.write_text(
            '#!/bin/sh\ncase "$1" in\n'
            'managername) printf "%s\\n" "${TEST_MANAGER_NAME:-Aqua}" ;;\n'
            'manageruid) printf "%s\\n" "${TEST_MANAGER_UID:-$(id -u)}" ;;\n'
            'getenv) [ "$2" = GIT_CONFIG_COUNT ] || exit 9\n'
            '  [ "${TEST_LAUNCHCTL_FAIL:-0}" = 0 ] || exit 8\n'
            '  printf "%s" "${TEST_LAUNCHD_COUNT:-}" ;;\n'
            '*) exit 9 ;;\nesac\n'
        )
        launchctl.chmod(0o700)
        self.env = {
            "HOME": str(self.home), "PATH": f"{self.bin}:{os.defpath}",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
        }
        self.destination = self.home / ".t3/service.env"

    def service_environment(self, inherited=None):
        environment = {**self.env, **(inherited or {})}
        for line in self.destination.read_text().splitlines():
            key, value = line.split("=", 1)
            environment[key] = value.strip("'")
        return environment

    def install(self, *args, answer=None):
        return subprocess.run(
            ["bash", str(REPO / "t3-service-env.sh"), *args],
            env=self.env, input=answer or "", capture_output=True, text=True,
        )

    def test_installs_scoped_git_settings_without_network_or_service_commands(self):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.destination.stat().st_mode & 0o777, 0o600)
        git_env = self.service_environment()
        git = shutil.which("git")
        for url in ("git@github.com:example/repo.git", "ssh://git@github.com/example/repo.git"):
            scoped = subprocess.check_output([git, "ls-remote", "--get-url", url], env=git_env, text=True)
            self.assertEqual(scoped.strip(), "https://github.com/example/repo.git")
            ordinary = subprocess.check_output([git, "ls-remote", "--get-url", url], env=self.env, text=True)
            self.assertEqual(ordinary.strip(), url)
        # A file-scoped helper would satisfy Git first if the empty reset were missing.
        wrong_helper = self.bin / "wrong-helper"
        wrong_helper.write_text("#!/bin/sh\nprintf 'username=wrong\\npassword=wrong\\n'\n")
        wrong_helper.chmod(0o700)
        global_config = self.home / "gitconfig"
        global_config.write_text(f'[credential]\n\thelper = "!{wrong_helper}"\n')
        git_env["GIT_CONFIG_GLOBAL"] = str(global_config)
        credential = subprocess.run(
            [git, "credential", "fill"], env=git_env,
            input="protocol=https\nhost=github.com\n\n", capture_output=True, text=True,
        )
        self.assertEqual(credential.returncode, 0, credential.stderr)
        self.assertIn("username=fixture", credential.stdout)
        self.assertIn("password=fixture", credential.stdout)

    def test_appends_after_launchd_config_even_when_installer_shell_differs(self):
        self.env["TEST_LAUNCHD_COUNT"] = "2"
        # The installer shell does not necessarily inherit launchd's Git config.
        self.env["GIT_CONFIG_COUNT"] = "0"
        inherited = {
            "GIT_CONFIG_COUNT": "2",
            "GIT_CONFIG_KEY_0": "demo.inherited", "GIT_CONFIG_VALUE_0": "launcher",
            "GIT_CONFIG_KEY_1": "core.quotepath", "GIT_CONFIG_VALUE_1": "false",
        }
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        config = self.service_environment(inherited)
        self.assertEqual(config["GIT_CONFIG_COUNT"], "6")
        git = shutil.which("git")
        for key, value in (("demo.inherited", "launcher"), ("core.quotepath", "false")):
            actual = subprocess.check_output([git, "config", "--get", key], env=config, text=True)
            self.assertEqual(actual.strip(), value)
        rewritten = subprocess.check_output(
            [git, "ls-remote", "--get-url", "git@github.com:example/repo.git"], env=config, text=True,
        )
        self.assertEqual(rewritten.strip(), "https://github.com/example/repo.git")
        self.assertNotIn("GIT_CONFIG_KEY_0=", self.destination.read_text())

    def test_launchd_failures_leave_existing_file_unchanged(self):
        self.destination.parent.mkdir()
        self.destination.write_text("KEEP=private-fixture\n")
        for name, value in (
            ("TEST_MANAGER_NAME", "Background"), ("TEST_MANAGER_UID", "other-user"),
            ("TEST_LAUNCHCTL_FAIL", "1"), ("TEST_LAUNCHD_COUNT", "-1"),
            ("TEST_LAUNCHD_COUNT", "invalid-private-fixture"),
            ("TEST_LAUNCHD_COUNT", "10001"),
        ):
            with self.subTest(variable=name, value=value):
                self.env[name] = value
                result = self.install(answer="yes\n")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.destination.read_text(), "KEEP=private-fixture\n")
                self.assertNotIn("private-fixture", result.stdout + result.stderr)
                del self.env[name]

    def test_leading_zero_launchd_count_is_decimal_and_rerun_does_not_grow(self):
        self.env["TEST_LAUNCHD_COUNT"] = "00008"
        self.assertEqual(self.install().returncode, 0)
        contents = self.destination.read_bytes()
        self.assertTrue(contents.startswith(b"GIT_CONFIG_COUNT=12\nGIT_CONFIG_KEY_8="))
        self.assertEqual(self.install(answer="yes\n").returncode, 0)
        self.assertEqual(self.destination.read_bytes(), contents)

    def test_replacement_requires_confirmation_and_creates_no_backup(self):
        self.destination.parent.mkdir()
        self.destination.write_text("KEEP=private-fixture\n")
        history = self.destination.parent / "userdata/statev2.sqlite"
        history.parent.mkdir()
        history.write_bytes(b"history-fixture")
        for answer in ("n\n", "\n", ""):
            result = self.install(answer=answer)
            self.assertEqual(self.destination.read_text(), "KEEP=private-fixture\n")
            self.assertNotIn("private-fixture", result.stdout + result.stderr)
        result = self.install(answer="yes\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.destination.read_text().startswith("GIT_CONFIG_COUNT=4\n"))
        self.assertEqual(history.read_bytes(), b"history-fixture")
        self.assertEqual(set(self.destination.parent.iterdir()), {self.destination, history.parent})
        self.assertEqual(list(self.home.iterdir()), [self.destination.parent])

    def test_confirmed_symlink_replacement_leaves_target_untouched(self):
        self.destination.parent.mkdir()
        target = self.root / "original"
        target.write_text("preserve\n")
        self.destination.symlink_to(target)
        result = self.install(answer="y\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.destination.is_symlink())
        self.assertEqual(target.read_text(), "preserve\n")

    def test_help_and_invalid_options_do_not_write(self):
        self.assertEqual(self.install("--help").returncode, 0)
        self.assertNotEqual(self.install("--unknown").returncode, 0)
        self.assertFalse(self.destination.parent.exists())


if __name__ == "__main__":
    unittest.main()
