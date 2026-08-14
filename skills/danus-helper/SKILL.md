---
name: danus-helper
description: Install Danus at its supported upstream commit, apply and inspect the bundled OpenCode adaptation, remember its user-level installation path, diagnose or recover the deployment, and run Danus mathematics research, scheduled monitoring, human summaries, and paper writing in OpenCode Desktop. Use when the user asks to install, configure, locate, repair, recover, or use Danus with OpenCode, asks Danus to research a mathematics problem, requests a progress report or paper from a Danus project, or mentions Danus workers or scheduled checks. 用于安装和定位 Danus、应用 OpenCode 适配、检查与恢复部署，以及在 OpenCode Desktop 中运行数学研究、定时检查、进展总结和论文生成流程。
---

# Danus Helper for OpenCode

Use this skill as the global OpenCode entry point for Danus. Resolve the saved
installation before every task, then route the request to installation,
adaptation, deployment inspection, or Danus usage.

## Resolve the installation first

Set `SKILL_DIR` to the directory reported when OpenCode loads this skill. Run:

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" installation-show --json
```

Interpret the result:

- `configured: true` and `valid: true`: set `DANUS_HOME` to `danus_home`.
- `configured: false`: enter the installation flow and ask for a destination
  when the user supplied none.
- an `error` field: report the saved path and error, then ask for the intended
  Danus location.

OpenCode may request `external_directory` approval when `DANUS_HOME` is outside
the active workspace. Explain the saved installation and keep approval scoped
to that directory.

## Route the request

- **Install Danus:** follow all three setup phases in order.
- **Apply or inspect the adaptation:** resolve `DANUS_HOME`, then follow the
  patch reference.
- **Repair or recover the deployment:** run the helper doctor, inspect Danus
  services and worker status, then follow the recovery reference.
- **Research mathematics with Danus:** resolve `DANUS_HOME`, read the usage
  reference, and guide the user into the saved Danus project in OpenCode
  Desktop.
- **Monitor, summarize, or write a paper:** resolve `DANUS_HOME`, identify the
  Danus project, then follow the corresponding workflow in the usage reference.
- **Locate Danus:** return the saved absolute path and current deployment state.

## Phase 1 — Install and remember Danus

Read [install-zh.md](references/install-zh.md). Clone the supported upstream
commit, create the deployment branch, recognize the repository, and save its
absolute path:

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" \
  installation-set "$DANUS_HOME" --json
```

The supported upstream release and commit are:

```text
v0.1.0-codex
7a51336e53cd1d558d0e766a61eb0fed46ebb05b
```

## Phase 2 — Apply the OpenCode adaptation

Read [patch-zh.md](references/patch-zh.md). Inspect the registered checkout:

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" patch-status --json
```

Apply the bundled patch after the user approves the source-tree edit:

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" patch-apply --json
```

The helper requires the supported commit and a clean worktree before applying
the patch.

## Phase 3 — Provision and inspect the deployment

Follow the provisioning section in [install-zh.md](references/install-zh.md).
Use Danus's own bootstrap and service commands from `DANUS_HOME`. Treat provider
credentials as OpenCode-owned. Installation finishes without a model-backed
request.

Run the helper doctor from any working directory:

```bash
python3 "$SKILL_DIR/scripts/danus_helper.py" doctor --json
```

Then run Danus's health check from the registered installation. Treat the
installation as complete after the helper reports `deployment_state: ready`,
Danus bootstrap succeeds, and `scripts/doctor.sh` recognizes OpenCode and the
runtime.

## Phase 4 — Use Danus in OpenCode Desktop

Read [usage-zh.md](references/usage-zh.md). Use `DANUS_HOME` as the OpenCode
Desktop project for the full main-agent workflow. OpenCode loads Danus's agent
contract, skills, MCP services, scheduling plugin, and project memory from that
directory.

When the user gives a mathematics problem, preserve the original statement and
let the Danus main agent perform its initialization, strategy, worker dispatch,
verification, monitoring, and reporting flow. Report the selected provider and
model and request confirmation before the first model-backed Danus operation.

After workers start, arrange the next project review with
`danus_schedule_wakeup`. During another conversation, run `bin/danus list`,
adopt every live project the user wants monitored, and bind its next review to
the current conversation.

For progress summaries and papers, read the corresponding Danus-owned skill at
`$DANUS_HOME/.claude/skills/` in full before invoking its MCP tools. Verify the
returned artifact, validation result, and absolute output path before reporting
completion.

## Shared rules

- Install this skill globally at
  `~/.config/opencode/skills/danus-helper/` for cross-project discovery.
- Resolve `DANUS_HOME` from user-level configuration in every conversation.
- Keep provider credentials in OpenCode's user-level storage.
- Preserve unrelated files in the Danus checkout.
- Treat an explicit request to install or configure Danus for OpenCode as
  authorization for the clone, bundled patch, and bootstrap steps in this
  workflow. Request confirmation for provider login, model-backed work, staging,
  commits, pushes, publication, and changes outside the registered installation.
- Report exact commands, exit states, service status, logs, and result paths.

Bundled resources:

- `scripts/danus_helper.py`: installation record, baseline inspection, patch
  state, patch application, and deployment doctor.
- `assets/danus-v0.1.0-codex-opencode.patch`: OpenCode adaptation for the
  supported Danus commit.
- `references/install-zh.md`, `references/patch-zh.md`, and
  `references/usage-zh.md`: phase-specific operating instructions.
