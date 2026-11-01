#!/usr/bin/env bash
# Configure the official T3 service; activation remains a separate manual step.
set -eu
umask 077

case "${1:-}" in
    -h|--help)
        echo "Usage: ./t3-service-env.sh"
        echo "Install ~/.t3/service.env using gh from PATH."
        echo "Confirms before replacing an existing file. No backups or service restart."
        exit 0
        ;;
esac
if [ "$#" -ne 0 ]; then
    echo "Usage: ./t3-service-env.sh" >&2
    exit 2
fi

: "${HOME:?HOME must be set}"
gh_bin="$(command -v gh)" || { echo "Install gh and put it on PATH first." >&2; exit 1; }
case "$gh_bin" in
    /*) ;;
    *) echo "gh must resolve to an absolute executable path." >&2; exit 1 ;;
esac
# Keep the literal dotenv value and Git's shell helper safe without an escaping layer.
case "$gh_bin" in
    *[!a-zA-Z0-9_./-]*) echo "Use a gh executable path without spaces or shell characters." >&2; exit 1 ;;
esac

# T3's LaunchAgent inherits the logged-in user's GUI launchd environment.
# Query only its count; keep the existing indexed keys/values inherited at runtime.
if [ "$(launchctl managername)" != Aqua ] || [ "$(launchctl manageruid)" != "$(id -u)" ]; then
    echo "Run this setup from a terminal in this Mac user's logged-in desktop session." >&2
    exit 1
fi
base_count="$(launchctl getenv GIT_CONFIG_COUNT)" || {
    echo "Could not read launchd's Git configuration count; unchanged." >&2; exit 1;
}
base_count="${base_count:-0}"
if ! [[ "$base_count" =~ ^[0-9]{1,5}$ ]] || [ "$((10#$base_count))" -gt 10000 ]; then
    echo "launchd's GIT_CONFIG_COUNT must be an integer between 0 and 10000; unchanged." >&2
    exit 1
fi
base_count=$((10#$base_count))

destination="$HOME/.t3/service.env"
if [ -d "$destination" ]; then
    echo "$destination is a directory; expected a file." >&2
    exit 1
fi
if [ -e "$destination" ] || [ -L "$destination" ]; then
    printf 'Replace %s entirely, without a backup? [y/N]: ' "$destination"
    if ! read -r answer; then
        echo "No confirmation received; unchanged." >&2
        exit 1
    fi
    case "$answer" in
        y|Y|yes|YES) ;;
        *) echo "Unchanged."; exit 0 ;;
    esac
fi

mkdir -p "$HOME/.t3"
temporary="$(mktemp "$HOME/.t3/.service.env.XXXXXX")"
trap 'rm -f "$temporary"' EXIT
cat > "$temporary" <<EOF
GIT_CONFIG_COUNT=$((base_count + 4))
GIT_CONFIG_KEY_$base_count=url.https://github.com/.insteadOf
GIT_CONFIG_VALUE_$base_count=git@github.com:
GIT_CONFIG_KEY_$((base_count + 1))=url.https://github.com/.insteadOf
GIT_CONFIG_VALUE_$((base_count + 1))=ssh://git@github.com/
GIT_CONFIG_KEY_$((base_count + 2))=credential.https://github.com.helper
GIT_CONFIG_VALUE_$((base_count + 2))=
GIT_CONFIG_KEY_$((base_count + 3))=credential.https://github.com.helper
GIT_CONFIG_VALUE_$((base_count + 3))='!$gh_bin auth git-credential'
EOF
chmod 600 "$temporary"
mv -f "$temporary" "$destination"
echo "Installed $destination. T3 has not been started or restarted."
