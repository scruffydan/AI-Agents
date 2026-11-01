# T3 Code background service for remote work

This setup targets the official **T3 Code 0.1.6** app on Dan's Mac. The background
service owns the backend; the normal Dock app connects as a client with its
**Local environment disabled**. Remote devices connect to that same service
through T3 Connect. No custom app or patched installation is needed.

The separate [`t3-service-env.mjs`](../t3-service-env.mjs) script prepares a new
candidate file. It never installs, starts, stops, or restarts T3, changes app
settings, or chooses a T3 home. `install.sh` does not run it. **Activation below
is a separate, deliberate step that interrupts active work.**

## Authentication choice and scope

The service receives indexed `GIT_CONFIG_*` environment variables that:

1. Rewrite `git@github.com:owner/repo` and `ssh://git@github.com/owner/repo` to
   `https://github.com/owner/repo` in memory.
2. Reset GitHub's credential-helper list in that process scope, then use the
   existing `gh auth git-credential` helper through an absolute executable path.

Repository SSH remote URLs stay unchanged. Ordinary terminals launched separately
keep their current Git/SSH behavior. T3 and processes that inherit the backend's
environment, including agents and integrated terminals, receive these settings.
An explicitly overridden/cleared child environment can change that behavior.
The installed 0.1.6 Git driver was statically checked to append its indexed
settings after inherited entries.

This avoids SSH transport's 1Password authorization prompts for GitHub operations
without exporting a key. It relies on the existing GitHub CLI account and its
access to the necessary repositories. `gh` must authenticate as the **same OS
user that owns the service**, with credentials accessible noninteractively in
that user's login session. A successful interactive check alone does not prove
that a locked or remote service session can access its credential store. Test
from the running service after activation. Never put tokens in this repo or the
generated configuration. The helper's absolute path must remain valid after
Homebrew or CLI changes; regenerate if it moves.

SSH **commit signing is separate**. Existing `commit.gpgsign`, `gpg.format=ssh`,
or an SSH signing program can still invoke 1Password when committing. This setup
does not change signing settings. Investigate signing separately if transport
works but commits prompt. Other SSH hosts, submodules on other hosts, aliases,
custom ports, Git LFS, and tools that bypass Git need separate verification.
More-specific existing URL rewrites win Git's longest-prefix match; explicit
`git -c` settings can also override environment config.

A dedicated SSH key retrieved through a 1Password service account into a separate
OpenSSH agent remains an option for a future VM. It needs credential provisioning,
key/agent lifecycle management, and service-account access controls. This simpler
`gh` approach reuses the existing account and requires none of that provisioning.
It does not create service accounts, retrieve/export keys, or alter 1Password.

## Prepare a candidate (no activation)

Requirements: Node **22.16+** with `node:util.parseEnv`, Git, and an existing
executable `gh`. No npm packages are needed. On this Mac, `gh` is currently
`/opt/homebrew/bin/gh`; neither `t3` nor `t3code` was on the harness shell's PATH
when this setup was prepared. Check the paths on another host.

Run from this repository. Keep the staging directory outside the checkout; an
existing env file may contain secrets. The script prints neither its contents
nor config values, and creates its output exclusively with mode `600`.

```sh
umask 077
mkdir -p "$HOME/.ai-agents-backups"
stage_dir="$(mktemp -d "$HOME/.ai-agents-backups/t3-service-XXXXXX")"
```

Choose **one** preparation command. If `~/.t3/service.env` already exists as a
regular file, make a private copy and include it. If it is a symlink or another
file type, resolve that intentionally before proceeding.

```sh
cp -p "$HOME/.t3/service.env" "$stage_dir/service.env.before"
chmod 600 "$stage_dir/service.env.before"
node t3-service-env.mjs --gh /opt/homebrew/bin/gh \
  --input "$stage_dir/service.env.before" --output "$stage_dir/service.env.next"
```

If **no** env file exists, omit `--input`:

```sh
node t3-service-env.mjs --gh /opt/homebrew/bin/gh \
  --output "$stage_dir/service.env.next"
```

The script does not look for `~/.t3/service.env` itself. Supplying a missing input
is an error. It refuses existing output paths, including symlinks, and validates
that `gh` is executable without executing it. Review the candidate locally in an
editor; do not paste, log, or commit copied secrets. Retain this private staging
directory for rollback.

Existing input bytes, including comments, quotes, multiline values, and unrelated
settings, are preserved. T3 uses Node's dotenv parser: values are literal, with
no shell expansion; the last occurrence of a variable wins. The script appends
new indexed Git definitions using that same parser and validates a round trip.
An empty input normally produces four config pairs.

Current-shell indexed Git pairs are included first, existing file pairs follow,
and the four new pairs are last. An already matching shell prefix and managed
suffix are reused, so rerunning against a candidate does not keep adding them.
Malformed counts, gaps, orphaned variables, or Git values the generator cannot
safely quote fail before output is created. Inherited Git values must be
single-line; other multiline env settings remain intact.

**The preparation shell is not launchd.** Its environment is not automatically
persisted by service installation. This script freezes only indexed Git settings
visible in that shell and the supplied copy. If launchd has additional indexed
Git configuration, include that configuration in the preparation context too;
do not assume it will merge at runtime. T3 overlays `service.env` onto its
inherited environment, so its `GIT_CONFIG_COUNT` would otherwise hide those
entries. Regenerate when that base configuration changes.

## Activate manually during an interruption window

Do not run this section while preparing or reviewing the PR.

1. Open the official Dock app. If needed, use **Settings → About → Install** next
   to the `t3` command, then ensure `t3` resolves in your activation shell. Keep
   the official app and CLI on the intended compatible version.
2. Check `gh auth status --hostname github.com` as the service's OS user. If
   login is needed, complete it locally through `gh auth login`, declining any
   offer to reconfigure Git's existing transport/authentication settings. Do not use
   `gh auth setup-git` here: its normal persistent configuration is unnecessary
   for this process-scoped design. Do not export a token into the env file.
3. Finish active work, then turn **Settings → Environments → Local** off. The
   desktop restarts without its embedded server. Confirm no existing background
   backend is running (`t3 service status`). Never run two backends against the
   same home; if one is already installed/running, reconcile it before continuing.
4. With all backends stopped, take a private backup of the existing **whole T3
   home**, including database companions, settings, and attachments. The default
   is `~/.t3`, with history in `userdata/statev2.sqlite`. `runtime/service-state.json`
   is launcher metadata, not the history database. A plain copy of a running
   SQLite database alone is not a consistent backup. If the desktop uses a
   nondefault home, resolve that before continuing; do not silently select a new
   home, set `T3CODE_HOME`, or add `--base-dir` to work around a conflict.
5. Prepare/review the candidate above if not already done. Confirm the live env
   file has not changed since the copy. For an existing file, this guarded
   command installs only if it still matches:

   ```sh
   cmp -s "$HOME/.t3/service.env" "$stage_dir/service.env.before" && \
     install -m 600 "$stage_dir/service.env.next" "$HOME/.t3/service.env"
   ```

   For a fresh file, first confirm the default home already exists and contains
   the expected history/settings. Install only while no env file or symlink exists:

   ```sh
   test -d "$HOME/.t3" && test ! -e "$HOME/.t3/service.env" && \
     test ! -L "$HOME/.t3/service.env" && \
     install -m 600 "$stage_dir/service.env.next" "$HOME/.t3/service.env"
   ```

   If a guard fails, stop and prepare a new candidate from the current file.
   T3 ignores attempts to set `PATH`, `T3CODE_HOME`, `T3_BOOT_SERVICE_UNIT`, or
   `T3_SERVICE_LAUNCHER_CONTEXT` in this file, including case variants. The
   candidate deliberately needs none of those settings.
6. Run the supported transition and complete the T3 Connect sign-in:

   ```sh
   t3 up --connect
   t3 service status
   ```

7. Open the same official Dock app and sign in to/select the service environment.
   Keep Local off. Connect the remote device to that environment with the same
   T3 Connect account. Confirm existing history and settings are present before
   doing new work. If history is missing, stop and investigate the home/version;
   do not initialize or copy databases over it.

On macOS this is a per-user **launchd LaunchAgent**: it starts at login and stops
at logout. Keep this Mac logged in and awake; T3 Connect does not wake a sleeping
host. Later env changes take effect only after `t3 service restart`, which also
interrupts active work. The embedded desktop backend does not read `service.env`.

## Verify after activation

In a terminal launched **inside the service environment**, check the rewrite
without network access:

```sh
git ls-remote --get-url git@github.com:owner/repo.git
git ls-remote --get-url ssh://git@github.com/owner/repo.git
```

Both should report `https://github.com/owner/repo.git`. For a real repository,
`git config --get remote.origin.url` should still show its original SSH value.
In a separately launched ordinary terminal, the same `--get-url` checks should
retain their prior behavior.

Then use `git ls-remote origin HEAD` inside the service on a private repository
you already have access to. This checks actual read authentication without a
push. Exercise the normal T3 fetch/PR workflow too; successful reads do not prove
write permissions or SSH signing works. Check remotely for an unexpected
1Password prompt. Do not dump the environment or run commands that print tokens
or credential-helper responses.

## Rollback

To undo authentication configuration while keeping the service, restore
`service.env.before` with mode `600`, then run `t3 service restart`. For a fresh
setup with no prior file, remove only the env file installed above, then restart.
First check for subsequent changes; do not overwrite unrelated edits added after
activation. Schedule this interruption just like activation. Keep the home and
history intact.

To return ownership to the desktop, finish active work, run `t3 service stop`,
and use `t3 service uninstall` to prevent a later login from starting a second
backend. Only then enable the desktop's Local environment again. Restore/remove
the scoped env file as above; do not delete `~/.t3`. The ordinary SSH setup and
repo remotes require no restoration because this workflow never changes them.

## Future Linux VM and evidence

The same Git environment preparation can be used with an authenticated VM user
and that VM's absolute `gh` path. T3 uses a systemd **user** service on Linux;
session persistence and credential availability need deliberate setup there.
VM provisioning, moving history, 1Password service accounts, and SSH-agent setup
are outside this change.

Automated checks use temporary files, isolated Git configs, and a fake `gh`:
URL rewriting, helper reset/selection, preserved settings and inherited pairs,
child config appending, private output, repeatability, and failure safety. They
perform no network authentication. The installed app was inspected statically;
no service transition, live service authentication, remote-device connection,
or locked-session test was performed while preparing this PR.

Primary references for the targeted behavior:

- [T3 v0.1.6 background service](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/background-service.md)
- [T3 v0.1.6 remote access](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/remote-access.md)
- [T3 v0.1.6 installation](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/install.md)
- [v0.1.6 service launcher and dotenv overlay](https://github.com/pingdotgg/t3code/blob/v0.1.6/apps/server/src/serviceLauncher.ts)
- [v0.1.6 state paths](https://github.com/pingdotgg/t3code/blob/v0.1.6/apps/server/src/config.ts)
- [Git runtime config and URL rewriting](https://git-scm.com/docs/git-config)
- [Git credential-helper reset](https://git-scm.com/docs/gitcredentials)
- [GitHub CLI setup-git](https://cli.github.com/manual/gh_auth_setup-git)
