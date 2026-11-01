# T3 Code background service on Dan's Mac

Use the official T3 Code **0.1.6** app from its normal Dock icon. The background
service owns the backend, and the desktop connects as a client with Local off.

## Install the configuration

From this checkout, in a terminal in this Mac user's logged-in desktop session,
with `gh` on PATH:

```sh
./t3-service-env.sh
```

This writes `~/.t3/service.env` with mode `600`, using the absolute path to `gh`.
If a file already exists, the script asks before replacing **the entire file**.
Answering no leaves it unchanged. There are no backups and no automatic merges;
confirming discards any previous env settings. It also replaces symlinks rather
than writing through them. The script does not read credentials or run T3.

The file contains four process-scoped Git settings: two GitHub SSH-to-HTTPS URL
rewrites, a credential-helper reset, and `gh auth git-credential`. Repository
remote URLs and global Git/SSH configuration are unchanged. These settings reach
the service and children that inherit its environment; separately launched
terminals keep their existing SSH behavior.

The script reads only `GIT_CONFIG_COUNT` from the user's GUI launchd context.
It leaves existing inherited key/value entries untouched, adds the four settings
at the next available indices, and increases the count by four. It checks the
bootstrap manager name and user first, requiring the current user's Aqua GUI
context used by T3's LaunchAgent. Query failures or invalid
counts stop installation rather than silently resetting the count. It does not
read inherited values, which may contain credentials. The official app's Git
driver appends its own settings too. If launchd's base configuration changes,
rerun the script before restarting T3; the env file records the count at setup time.

## Activate separately

The script does **not** install, start, stop, or restart the backend. During an
interruption window:

1. In the official app, use **Settings → About → Install** next to `t3` if needed.
2. Ensure `gh auth status --hostname github.com` succeeds as the same macOS user
   that will run the service. Keep credentials out of `service.env`; do not run
   `gh auth setup-git`, which changes persistent Git configuration.
3. Finish active work and turn **Settings → Environments → Local** off. The app
   restarts without its embedded server. Confirm `t3 service status` does not
   show another running backend before continuing.
4. Run `./t3-service-env.sh`, then:

   ```sh
   t3 up --connect
   t3 service status
   ```

5. Complete T3 Connect sign-in. Open the normal Dock app and select the service
   environment, keeping Local off. Connect the remote device to that environment.

Keep the existing T3 home: normally `~/.t3`, with history in
`userdata/statev2.sqlite`. Do not set another `T3CODE_HOME` or run two backends
against the same home. Confirm existing history/settings are visible after the
transition. The macOS LaunchAgent runs while the user is logged in; keep the Mac
logged in and awake. Later env changes require `t3 service restart` and interrupt
active work. The embedded desktop backend does not read `service.env`.

## Check and undo

Inside the service environment, `git ls-remote --get-url git@github.com:owner/repo.git`
should show HTTPS; `git config --get remote.origin.url` still shows the stored SSH
remote. Use `git ls-remote origin HEAD` on a private repo to check real read
authentication, then check the normal T3 fetch/PR workflow. Separately launched
terminals should keep their previous behavior.

`gh` needs access to its authenticated account from the service's login session;
interactive success alone does not prove access while locked or remote. SSH
**commit signing** can still prompt through 1Password even when HTTPS transport
works. Other hosts, custom SSH aliases, and tools that bypass Git need their own
checks. A dedicated SSH key/agent using a 1Password service account remains a
future VM option; this setup provisions neither keys nor service accounts.

To remove this configuration, remove only the `service.env` installed here (check
for later edits first), then restart the service. Prior file contents are not
recoverable through this script. To return backend ownership to the desktop,
finish work, run `t3 service stop` and `t3 service uninstall`, then enable Local.
Keep `~/.t3` and its history. A future Linux VM would use a systemd user service;
VM provisioning and history migration are separate work.

Offline tests use isolated homes and fake credentials. No live service transition,
authentication, or remote/locked-session test has been performed for this PR.

References: [background service](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/background-service.md),
[remote access](https://github.com/pingdotgg/t3code/blob/v0.1.6/docs/user/remote-access.md),
[service env loading](https://github.com/pingdotgg/t3code/blob/v0.1.6/apps/server/src/serviceLauncher.ts),
[state paths](https://github.com/pingdotgg/t3code/blob/v0.1.6/apps/server/src/config.ts),
[launchctl commands](https://github.com/apple-oss-distributions/launchd/blob/main/man/launchctl.1),
[Git config](https://git-scm.com/docs/git-config),
[credential helpers](https://git-scm.com/docs/gitcredentials).
