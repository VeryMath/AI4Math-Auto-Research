---
name: rethlas-helper
description: Install or clone Rethlas, detect whether its original Codex runtime is available, guide users through their own provider/API configuration, explain its proof-generation and verification features, and conditionally offer the additive OpenCode patch. Also safely inspect, apply, validate, or remove that patch. 用于安装或克隆 Rethlas、检测原版 Codex 运行环境、引导用户配置自己的 provider/API、介绍并使用证明生成和验证功能，以及按 Codex 状态询问并安全管理 OpenCode 增量补丁。
---

# Rethlas Helper

Guide the user through Rethlas in four distinct phases. Keep the original
Codex workflow available, and install OpenCode support only after an explicit
user decision.

## Select language and scope

Use the `.en.md` reference for English requests and the `.zh-CN.md` reference
for Chinese requests. Read both versions only for bilingual or translation
work.

For a full setup, follow all four phases in order. For a request limited to
one phase, read that phase's reference plus only the prerequisites it names.
Do not load every reference by default.

## Phase 1 — Install or clone

Read:

- English: [install-clone.en.md](references/install-clone.en.md)
- 中文：[install-clone.zh-CN.md](references/install-clone.zh-CN.md)

Locate an existing Rethlas repository or clone the requested upstream/fork.
Run the bundled doctor and establish `SKILL_DIR` and `TARGET`. End this phase
with a valid repository root; do not mix environment setup into the clone
step.

## Runtime selection gate

Before environment configuration, inspect the doctor output, patch state, and
whether `codex` is actually usable:

```bash
command -v codex
codex --version
```

If the OpenCode patch is already installed, report that state and ask which
installed runtime the user wants to use. Do not offer to install it again.

If the patch is not installed and Codex is unavailable, explain that upstream
Rethlas is built on Codex and no usable Codex CLI was detected. Unless the
user already chose a path, ask:

> Original Rethlas requires Codex, but Codex is not installed or usable.
> Would you like to install the OpenCode compatibility patch?

For a Chinese request, ask:

> 原版 Rethlas 基于 Codex，但当前没有检测到可用的 Codex。是否安装
> OpenCode 版兼容补丁？

If the patch is not installed and Codex is available, ask:

> Codex is available. Would you like to use original Rethlas directly, or
> also install the OpenCode compatibility patch?

For a Chinese request, ask:

> 已检测到可用的 Codex。你希望直接使用原版 Rethlas，还是安装 OpenCode
> 版兼容补丁？

Do not repeat the question when the user already made an explicit choice.
If Codex is unavailable and the user declines the patch, explain that Rethlas
cannot run yet and offer to guide a Codex installation. Record the selected
runtime before configuring provider access.

## Phase 2 — Guide environment configuration

Read:

- English: [environment.en.md](references/environment.en.md)
- 中文：[environment.zh-CN.md](references/environment.zh-CN.md)

Guide the user interactively through required CLIs, the two Python
environments, optional system tools, authentication, provider/model choice,
and non-paid validation. Explain each decision and report what is ready,
missing, or awaiting user login.

For OpenCode, never choose a provider or model for the user. Guide them to
connect their own coding plan or API provider and select an available model.
The patch contains no default provider, model, or API credential.

Do not request or expose credentials. Ask before network-backed installation,
provider login, or any paid model call.

## Phase 3 — Apply the OpenCode patch when selected

If the user selected direct original Codex use, skip this phase. If the user
selected OpenCode and the patch is not already installed, read:

- English: [opencode-patch.en.md](references/opencode-patch.en.md)
- 中文：[opencode-patch.zh-CN.md](references/opencode-patch.zh-CN.md)

Apply the patch only on a user-approved non-default branch. Never force a
conflict, overwrite an existing path, or remove a patched file changed by the
user. Installing the patch must not silently select a provider or model.

## Phase 4 — Introduce features and guide usage

Read:

- English: [usage.en.md](references/usage.en.md)
- 中文：[usage.zh-CN.md](references/usage.zh-CN.md)

Introduce the generation agent, verification service, proof-and-repair loop,
optional references and retrieval, output artifacts, and result website.
Then guide the user's selected workflow through its first useful run. Give
commands for Codex unless the OpenCode patch is installed and selected.

## Shared completion rules

- Preserve unrelated tracked and untracked work.
- Keep credentials in user-level stores, outside the repository.
- Use `scripts/rethlas_helper.py doctor TARGET` for diagnosis.
- Retain logs and exact paths when reporting failures.
- Do not stage, commit, push, or run a paid smoke test unless the user asked
  for that action.

Bundled resources:

- `scripts/rethlas_helper.py`: doctor, patch status, safe install, and removal.
- `assets/rethlas-opencode-compat.patch`: additive Git patch.
- `assets/rethlas-opencode-compat.json`: baseline, checksum, and file manifest.
