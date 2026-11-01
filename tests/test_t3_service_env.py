"""Offline setup checks using fake credentials, isolated Git config, and temp files."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")
GIT = shutil.which("git")


@unittest.skipUnless(NODE and GIT, "T3 setup checks require Node 22.16+ and Git")
class T3ServiceEnvTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.env = {
            "HOME": str(self.home), "PATH": os.defpath,
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0", "LC_ALL": "C",
        }
        # Exercise shell quoting in an absolute helper path. This never contacts GitHub.
        self.gh = self.root / "gh's test CLI"
        self.gh.write_text(
            '#!/bin/sh\n[ "$1 $2 $3" = "auth git-credential get" ] || exit 9\n'
            "cat >/dev/null\nprintf 'username=fixture-user\\npassword=fixture-password\\n'\n"
        )
        self.gh.chmod(0o700)
        self.output = self.root / "candidate"

    def cli(self, *args, env=None, success=True):
        result = subprocess.run(
            [NODE, str(REPO / "t3-service-env.mjs"), *map(str, args)],
            env=self.env if env is None else env, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def generate(self, source=None, env=None, output=None, success=True):
        args = ["--gh", self.gh, "--output", output or self.output]
        if source is not None:
            args += ["--input", source]
        return self.cli(*args, env=env, success=success)

    def parse(self, path):
        result = subprocess.run(
            [NODE, "--input-type=module", "-e",
             'import {parseEnv} from "node:util"; import {readFileSync} from "node:fs";'
             'console.log(JSON.stringify(parseEnv(readFileSync(process.argv[1], "utf8"))));',
             str(path)], env=self.env, capture_output=True, text=True, check=True,
        )
        return json.loads(result.stdout)

    def git(self, *args, config=None, input=None):
        return subprocess.run(
            [GIT, *args], cwd=self.root, env={**self.env, **(config or {})},
            input=input, capture_output=True, text=True, check=True,
        ).stdout.strip()

    def test_scoped_rewrites_helper_reset_and_child_append_without_network(self):
        self.generate()
        config = self.parse(self.output)
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o600)
        self.assertEqual(config["GIT_CONFIG_COUNT"], "4")
        # Without the empty reset, this helper would satisfy Git before gh runs.
        bad_helper = self.root / "wrong-helper"
        bad_helper.write_text("#!/bin/sh\nprintf 'username=wrong\\npassword=wrong\\n'\n")
        bad_helper.chmod(0o700)
        global_config = self.home / "gitconfig"
        global_config.write_text(f'[credential]\n\thelper = "!{bad_helper}"\n')
        self.env["GIT_CONFIG_GLOBAL"] = str(global_config)
        self.git("init", "--quiet")
        self.git("remote", "add", "origin", "git@github.com:example/project.git")
        for url in ("git@github.com:example/project.git", "ssh://git@github.com/example/project.git"):
            self.assertEqual(self.git("ls-remote", "--get-url", url, config=config),
                             "https://github.com/example/project.git")
            self.assertEqual(self.git("ls-remote", "--get-url", url), url)
        self.assertEqual(self.git("ls-remote", "--get-url", "git@gitlab.com:example/project.git", config=config),
                         "git@gitlab.com:example/project.git")
        self.assertEqual(self.git("config", "--get", "remote.origin.url"),
                         "git@github.com:example/project.git")
        credential = self.git("credential", "fill", config=config,
                              input="protocol=https\nhost=github.com\n\n")
        self.assertIn("username=fixture-user", credential)
        self.assertIn("password=fixture-password", credential)
        child = {**config, "GIT_CONFIG_COUNT": "5",
                 "GIT_CONFIG_KEY_4": "core.quotepath", "GIT_CONFIG_VALUE_4": "false"}
        self.assertEqual(self.git("config", "--get", "core.quotepath", config=child), "false")
        self.assertEqual(self.git("ls-remote", "--get-url", "git@github.com:example/project.git", config=child),
                         "https://github.com/example/project.git")

    def test_preserves_literal_multiline_settings_file_pairs_and_inherited_pairs(self):
        source = self.root / "existing-copy"
        original = ('# Keep comments and literal expansion\nexport LABEL="$HOME # untouched"\n'
                    "MULTILINE='one\ntwo'\nGIT_CONFIG_COUNT=1\n"
                    "GIT_CONFIG_KEY_0=demo.setting\nGIT_CONFIG_VALUE_0=file\n")
        source.write_text(original)
        inherited = {**self.env, "GIT_CONFIG_COUNT": "1",
                     "GIT_CONFIG_KEY_0": "demo.setting", "GIT_CONFIG_VALUE_0": "shell"}
        self.generate(source, env=inherited)
        config = self.parse(self.output)
        self.assertTrue(self.output.read_text().startswith(original))
        self.assertEqual(source.read_text(), original)
        self.assertEqual(config["LABEL"], "$HOME # untouched")
        self.assertEqual(config["MULTILINE"], "one\ntwo")
        self.assertEqual(config["GIT_CONFIG_COUNT"], "6")
        self.assertEqual(self.git("config", "--get-all", "demo.setting", config=config), "shell\nfile")
        again = self.root / "candidate-again"
        self.generate(self.output, env=inherited, output=again)
        self.assertEqual(again.read_bytes(), self.output.read_bytes())

    def test_rejects_bad_git_config_without_writing_or_printing_values(self):
        cases = (
            "GIT_CONFIG_COUNT=-1\n", "GIT_CONFIG_COUNT=10001\n",
            "GIT_CONFIG_COUNT=1\nGIT_CONFIG_KEY_0=demo.setting\n",
            "GIT_CONFIG_VALUE_0=private-fixture\n",
            "GIT_CONFIG_COUNT=0\nGIT_CONFIG_KEY_0=demo.setting\n",
            "GIT_CONFIG_COUNT=1\nGIT_CONFIG_KEY_0=demo.setting\nGIT_CONFIG_VALUE_0='one\ntwo'\n",
            'UNRELATED="unterminated\n',
        )
        source = self.root / "existing-copy"
        for content in cases:
            with self.subTest(content=content):
                source.write_text(content + "SENSITIVE=private-fixture\n")
                result = self.generate(source, success=False)
                self.assertFalse(self.output.exists())
                self.assertNotIn("private-fixture", result.stdout + result.stderr)
        result = self.generate(env={**self.env, "GIT_CONFIG_COUNT": "1"}, success=False)
        self.assertIn("Shell environment", result.stderr)
        self.assertFalse(self.output.exists())
        source.write_bytes(b"LABEL=\xff\n")
        self.generate(source, success=False)
        self.assertFalse(self.output.exists())
        self.assertEqual(source.read_bytes(), b"LABEL=\xff\n")

    def test_never_overwrites_files_or_symlinks_and_requires_explicit_paths(self):
        self.cli("--help")
        for args in ((), ("--gh", "gh", "--output", self.output),
                     ("--output", self.output), ("--bogus", "value")):
            self.cli(*args, success=False)
        self.assertFalse(self.output.exists())
        self.output.write_text("preserve")
        self.generate(success=False)
        self.generate(self.output, success=False)
        self.assertEqual(self.output.read_text(), "preserve")
        self.output.unlink()
        target = self.root / "untouched"
        self.output.symlink_to(target)
        self.generate(success=False)
        self.assertFalse(target.exists())
        self.assertTrue(self.output.is_symlink())
        source = self.root / "symlink-input"
        source.symlink_to(self.gh)
        self.generate(source, output=self.root / "other-candidate", success=False)


if __name__ == "__main__":
    unittest.main()
