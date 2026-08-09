---
name: archon-helper
description: Install and configure Archon for OpenCode, remember its user-level installation path, locate its CLI from any OpenCode Desktop project or conversation, and run Lean formalization workflows in the current project. Use whenever the user asks to install Archon, formalize mathematics with Archon, initialize an Archon project, run or resume Archon, inspect results, or use init/dag/loop/discuss/dashboard/extract/merge/refactor/peers/scope/subagents. 用于在 OpenCode 中安装和配置 Archon、记住本机安装路径、从任意项目或新对话定位 Archon CLI，以及在当前项目运行 Lean 形式化流程。
---

# Archon Helper for OpenCode

Use this skill as the global OpenCode entry point for Archon. Keep two paths
explicit throughout the task:

- `ARCHON_HOME`: remembered Archon source and CLI installation;
- `PROJECT`: current Lean/Archon project selected by the user.

## Resolve the installation first

Set `SKILL_DIR` to the base directory reported when OpenCode loads this skill.
Read the user-level installation record:

```bash
python3 "$SKILL_DIR/scripts/archon_helper.py" installation-show --json
```

Interpret the result:

- `configured: true` and `valid: true`: set `ARCHON_HOME` and `ARCHON_BIN` from
  `archon_home` and `archon_bin`.
- an `error` field: report the saved path and configuration error, then ask for
  the intended Archon installation.
- `configured: false`: enter the install flow and ask for an installation
  destination when the user has not supplied one.

OpenCode may request `external_directory` approval for `ARCHON_HOME` in a new
project. Explain the saved Archon installation path and keep the approved scope
on that directory.

## Resolve the target project

Use the path named by the user. Otherwise set `PROJECT` to the current OpenCode
workspace. Inspect installation and project state together:

```bash
python3 "$SKILL_DIR/scripts/archon_helper.py" doctor "$PROJECT" --json
```

Use these fields to route the next action:

- `project_initialized`: whether `.archon/config.json` exists;
- `project_harness`: expected value `opencode` after initialization;
- `project_multilane_enabled`: expected value `false` for this compatibility
  patch;
- `project_opencode_skill` and `project_opencode_subagent`: project support
  files installed by `init --harness opencode`.

## Route the request

- **Install or repair Archon:** follow the installation, environment, and patch
  phases.
- **Initialize the current project:** run `init --harness opencode` with
  `ARCHON_BIN` after explaining the files Archon will create.
- **Formalize mathematics:** inspect the project, prepare its statement or
  source materials, then run `dag`, `loop`, or the user-selected command.
- **Continue work:** inspect current logs and run `loop --resume` with the
  requested phase.
- **Discuss or inspect:** use `discuss`, `dashboard`, `log`, or project files.
- **Manage several projects:** use `extract`, `merge`, `peers`, or `scope` after
  confirming all paths involved.

## Phase 1 — Install and remember Archon

Read [install-zh.md](references/install-zh.md).

Locate a recognized Archon source checkout or clone the supported upstream
revision. Create `<archon-home>/.venv` and install Archon in editable mode.
After the repository root is recognized, save its absolute path:

```bash
python3 "$SKILL_DIR/scripts/archon_helper.py" \
  installation-set "$ARCHON_HOME" --json
```

The command writes machine-local configuration to the `config_file` shown in
its output. Derive `ARCHON_BIN` from the saved installation on every task.

## Phase 2 — Configure OpenCode and Lean

Read [environment-zh.md](references/environment-zh.md).

Inspect Python, Git, Elan, Lean, Lake, uv, and OpenCode. Use the user's existing
OpenCode provider configuration and model selection. Keep login information in
the user-level OpenCode store. Explain network installations and real provider
requests before asking for approval.

## Phase 3 — Install the OpenCode compatibility patch

Read [patch-zh.md](references/patch-zh.md).

Inspect patch state from the remembered installation:

```bash
python3 "$SKILL_DIR/scripts/archon_helper.py" patch-status --json
```

Apply the patch after the user approves the Archon source change:

```bash
python3 "$SKILL_DIR/scripts/archon_helper.py" patch-apply
```

The patch targets Archon 0.3.3. It registers the OpenCode harness for init,
plan, prover, review, resume, subagents, and other agent-backed commands.

## Phase 4 — Initialize and run the current project

Read [usage-zh.md](references/usage-zh.md).

For a new project:

```bash
"$ARCHON_BIN" init "$PROJECT" --harness opencode
```

Inspect the project again, then choose the command that matches the request.
Typical examples:

```bash
"$ARCHON_BIN" dag "$PROJECT" --max-iterations 4
"$ARCHON_BIN" loop "$PROJECT" --max-iterations 3
"$ARCHON_BIN" loop "$PROJECT" --resume
"$ARCHON_BIN" discuss "$PROJECT" --harness opencode
```

State the selected provider/model and expected quota use before the first
model-backed operation. Follow logs and report Lean files, build state, Archon
phase, and exact result paths in the current OpenCode Desktop conversation.

## Shared rules

- Install this skill globally for cross-project use:
  `~/.config/opencode/skills/archon-helper/`.
- Resolve `ARCHON_HOME` from user configuration in every new conversation.
- Resolve `PROJECT` from the current workspace or the user's explicit path.
- Preserve user source, Lean files, and Git work in both directories.
- Use `ARCHON_BIN` from the remembered editable installation.
- Keep OpenCode credentials in user-level storage.
- Ask before repository edits, network installation, provider login, real
  model calls, staging, commits, pushes, and cross-project writes.
- Keep `multilane.enabled = false` for the Archon 0.3.3 OpenCode patch.

Bundled resources:

- `scripts/archon_helper.py`: installation path, project doctor, patch status,
  and patch installation commands.
- `assets/patches/archon-v0.3.3-opencode.patch`: OpenCode harness patch.
