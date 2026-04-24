#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
plugin_root="$repo_root/plugins/worktrunk"
cache_root="${CODEX_HOME:-$HOME/.codex}/plugins/cache/worktrunk-codex/worktrunk/local"

codex plugin marketplace add "$repo_root" >/dev/null 2>&1 || true
mkdir -p "$(dirname "$cache_root")"
rsync -a --delete "$plugin_root/" "$cache_root/"

cat <<'EOF'
WorkTrunk for Codex was synced into the local plugin cache.

Ensure your ~/.codex/config.toml includes:

[features]
plugins = true
codex_hooks = true

[plugins."worktrunk@worktrunk-codex"]
enabled = true
EOF
