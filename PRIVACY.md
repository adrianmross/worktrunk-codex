# Privacy

This plugin runs local Codex hook scripts on your machine.

- It reads Codex hook payloads from stdin.
- It may call local commands such as `git` and `wt`.
- It writes lightweight local state files under the user's state directory.
- It does not send plugin-specific telemetry or upload hook payloads anywhere.

Any network activity comes from Codex, WorkTrunk, or commands you explicitly run, not from this plugin itself.
