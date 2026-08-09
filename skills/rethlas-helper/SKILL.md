---
name: rethlas-helper
description: Install and configure Rethlas for OpenCode, remember its user-level installation path, locate it from any OpenCode Desktop project or conversation, and run natural-language mathematics proof generation and verification. Use whenever the user asks to install or configure Rethlas, solve a mathematics problem with Rethlas, continue a Rethlas run, inspect Rethlas results, or repair a Rethlas setup. 用于在 OpenCode 中安装和配置 Rethlas、记住本机安装路径、从任意项目或新对话定位 Rethlas，以及运行自然语言数学证明的生成、验证和修复流程。
---

# Rethlas Helper for OpenCode

Use this skill as the global OpenCode entry point for Rethlas. Resolve the
remembered installation before every task, then route the request to setup,
proof generation, continuation, or result inspection.

## Select language and scope

Use the `.en.md` reference for English requests and the `.zh-CN.md` reference
for Chinese requests. Read both versions for bilingual or translation work.
Load the reference for the current phase together with its named prerequisites.

## Resolve the installation first

Set `SKILL_DIR` to the base directory reported when OpenCode loads this skill.
Inspect the user-level installation record:

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" installation-show --json
```

Interpret the result:

- `configured: true` and `valid: true`: set `TARGET` to `rethlas_home` and
  continue without asking the user for a repository path.
- an `error` field: report the configuration problem and ask for the intended
  Rethlas location before updating the record.
- `configured: false`: enter the install flow and ask where Rethlas should be
  installed when the user has not supplied a destination.
- `configured: true` and `valid: false`: report the recorded path and error,
  then ask for the moved installation or a new destination.

OpenCode may request `external_directory` approval when `TARGET` is outside the
active project. Explain that the saved Rethlas installation is being accessed
and let the user approve the trusted directory. Keep the permission scope on
the exact Rethlas directory.

## Route the request

- **Install or repair:** follow all setup phases in order.
- **Solve a mathematics problem:** resolve `TARGET`, read the usage reference,
  and start the OpenCode generation and verification workflow.
- **Continue a run:** resolve `TARGET`, inspect the active runner and matching
  logs, memory, and results. Monitor an active process; after a completed run,
  report its state and ask before starting another model-backed run.
- **Inspect results:** resolve `TARGET` and report the exact blueprint, verified
  blueprint, logs, and verification state.
- **Check or change the saved path:** use `installation-show` or
  `installation-set` directly.

## Phase 1 — Install, locate, and remember Rethlas

Read:

- English: [install-clone.en.md](references/install-clone.en.md)
- 中文：[install-clone.zh-CN.md](references/install-clone.zh-CN.md)

Locate a recognized Rethlas repository or clone the upstream requested by the
user. After the repository root is recognized, remember its absolute path:

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" installation-set "$TARGET" --json
```

The command writes `rethlas_home` to the user-level OpenCode configuration
file shown in its output. Treat that file as local machine configuration.

## Phase 2 — Configure the OpenCode environment

Read:

- English: [environment.en.md](references/environment.en.md)
- 中文：[environment.zh-CN.md](references/environment.zh-CN.md)

Prepare the two Python environments, confirm the OpenCode CLI and the user's
existing provider connection, and inspect optional reference and website tools.
Let the user select the provider and model. Ask before network installation,
provider login, or a model-backed run.

## Phase 3 — Install the OpenCode compatibility files

Read:

- English: [opencode-patch.en.md](references/opencode-patch.en.md)
- 中文：[opencode-patch.zh-CN.md](references/opencode-patch.zh-CN.md)

Inspect patch applicability and the repository worktree. Apply the compatibility
patch after the user approves the repository edit and branch. Keep provider,
model, and credentials in the user's OpenCode configuration.

After setup, run the doctor without a target to confirm that the remembered
installation resolves from any working directory:

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" doctor --json
```

## Phase 4 — Solve problems and guide usage

Read:

- English: [usage.en.md](references/usage.en.md)
- 中文：[usage.zh-CN.md](references/usage.zh-CN.md)

For a plain-language problem request:

1. Resolve the remembered `TARGET`.
2. Save the mathematical problem as Markdown under
   `agents/generation/data/` using a clear problem identifier.
3. Place user-provided references in the matching `.refs/` directory.
4. Start the OpenCode verification service on port 8091.
5. Run the OpenCode generation runner with the selected problem file.
6. Follow iteration logs and report the final blueprint, verification verdict,
   and exact result paths in the current OpenCode Desktop conversation.

Ask once before the first model-backed operation in the task and state the
selected provider/model. Continue monitoring from the same conversation while
the run is active.

## Shared rules

- Install this skill globally when it should work across OpenCode projects:
  `~/.config/opencode/skills/rethlas-helper/`.
- Use the remembered path for new projects and new conversations.
- Preserve unrelated tracked and untracked files in the Rethlas repository.
- Keep credentials in user-level OpenCode storage.
- Retain logs and exact paths when reporting failures.
- Ask before staging, committing, pushing, network installation, provider
  login, or a model-backed run.

Bundled resources:

- `scripts/rethlas_helper.py`: installation path, doctor, patch status,
  installation, and removal commands.
- `assets/rethlas-opencode-compat.patch`: OpenCode compatibility files.
