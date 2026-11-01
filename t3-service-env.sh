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
GIT_CONFIG_COUNT=4
GIT_CONFIG_KEY_0=url.https://github.com/.insteadOf
GIT_CONFIG_VALUE_0=git@github.com:
GIT_CONFIG_KEY_1=url.https://github.com/.insteadOf
GIT_CONFIG_VALUE_1=ssh://git@github.com/
GIT_CONFIG_KEY_2=credential.https://github.com.helper
GIT_CONFIG_VALUE_2=
GIT_CONFIG_KEY_3=credential.https://github.com.helper
GIT_CONFIG_VALUE_3='!$gh_bin auth git-credential'
EOF
chmod 600 "$temporary"
mv -f "$temporary" "$destination"
echo "Installed $destination. T3 has not been started or restarted."
