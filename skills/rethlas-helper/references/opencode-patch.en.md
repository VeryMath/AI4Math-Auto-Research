# Install the OpenCode Compatibility Files

Use this phase to connect the Rethlas generation and verification agents to
OpenCode.

## 1. Patch contents

The bundled Git patch adds:

- OpenCode usage guides;
- generation and verification `opencode.json` files;
- OpenCode-specific `AGENTS` instructions;
- an OpenCode generation runner;
- an OpenCode verification API;
- an OpenCode recursive-proving skill.

Provider, model, variant, and API credentials come from the user's OpenCode
configuration.

## 2. Check applicability

`TARGET` is already resolved from user configuration. Run:

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" patch-status
git -C "$TARGET" status --short
git -C "$TARGET" branch --show-current
git -C "$TARGET" rev-parse HEAD
```

Report the branch, worktree entries, and `patch_state`. Apply the patch on a
feature branch approved by the user. When the state is partial or conflicting,
show the relevant paths and ask how the user wants to handle them.

## 3. Apply the patch

After the user confirms the branch and repository edit, run:

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" patch-apply
```

The helper runs `git apply --check` and then applies the bundled patch. Inspect
the state again:

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" patch-status
```

Expected output:

```text
patch_state: installed
```

## 4. Inspect OpenCode entry points

Run from each agent directory:

```bash
cd "$TARGET/agents/generation"
opencode agent list
opencode mcp list
```

```bash
cd "$TARGET/agents/verification"
opencode agent list
opencode mcp list
```

Confirm that the generation directory exposes proof agents and the reasoning
MCP, and that the verification directory exposes its agent and verification
MCP. State the provider/model and expected quota use before a real model call,
then ask for approval.

## 5. Restore the pre-patch state

When the user explicitly requests restoration and the patch state is complete,
run:

```bash
python3 "$SKILL_DIR/scripts/rethlas_helper.py" patch-remove
```

The helper checks reverse applicability before applying the patch in reverse.
Report affected paths and Git output when local changes cause a conflict.

## 6. Report

Report:

- Rethlas installation path;
- branch and `HEAD`;
- patch state;
- OpenCode agent and MCP listings;
- provider/model selected by the user;
- the next real problem-solving command.
