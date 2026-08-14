---
name: danus-helper-dsh
description: Install, locate, configure, operate, diagnose, or remove the supported Danus v0.1.0-codex adaptation for DeepSeek Harness 0.1.0-rc.5 and rc.6. Use for Danus mathematics research, autonomous workers, proof verification, scheduled follow-ups, recovery, paper writing, or human-readable summaries in DeepSeek Harness.
---

# Danus Helper for DeepSeek Harness

Deploy the supported Danus release with DeepSeek Harness as its agent runtime. Keep the user's provider credentials in the existing DeepSeek Harness configuration.

## Resolve the installation

Set `SKILL_DIR` to this skill directory. Begin every operation with:

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" installation-show --json
```

Use the returned `danus_home` when `configured` and `valid` are true. A missing or invalid record starts the installation workflow in [references/install-zh.md](references/install-zh.md).

The installation record lives at `$DSH_HOME/danus-helper-dsh.toml`, with `~/.dsh` as the default DSH home. This makes the same Danus installation discoverable from later DeepSeek Harness sessions and other project directories.

## Choose the workflow

- Install or redeploy Danus: read [references/install-zh.md](references/install-zh.md).
- Inspect, apply, or remove the adaptation: read [references/patch-zh.md](references/patch-zh.md).
- Start research, inspect progress, recover work, create a paper, or create a human summary: read [references/usage-zh.md](references/usage-zh.md).

Run this diagnosis after resolving the installation:

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" doctor --json
```

Report the registered path, supported source commit, patch state, DeepSeek Harness version, deployment state, and live processes before making changes.

## Operating rules

1. Preserve user changes. Inspect `git status --short` before applying or reversing the patch.
2. Apply the bundled patch only to commit `7a51336e53cd1d558d0e766a61eb0fed46ebb05b` from tag `v0.1.0-codex`.
3. Reuse a registered DeepSeek Harness rc.5 or rc.6 runtime. When one is unavailable, install the pinned `@deepseek-ai/dsh@0.1.0-rc.6` through Danus `scripts/bootstrap.sh`.
4. Install this helper into the global DSH skill directory with the helper's `skill-install` command.
5. Use `bin/danus-web` for the human-facing main agent. It starts DeepSeek Harness in the Danus root, where `AGENTS.md` and the project skills load.
6. Use the official DeepSeek Harness schedule tools for session wakeups. Preserve Danus worker processes and project state through the supplied service and recovery scripts.
7. Before the first model-backed research operation, report the selected provider and model and request confirmation.
8. Ask for confirmation before dependency downloads, source patching, service changes, worker termination, paper finalization, publication, or pushes.
9. Report absolute paths for generated research artifacts, summaries, TeX sources, PDFs, and logs.

## Supported capabilities

The adaptation covers the DeepSeek Harness Web main agent, headless research workers, verifier sessions, strategy consultation, fact storage, revision rounds, scheduled project checks, process recovery, `write-paper`, and `human-summary`.
