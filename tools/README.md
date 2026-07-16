# Simplee DevKit

The Simplee DevKit creates a safe, upload-ready development context package for ChatGPT without changing repository state.

## Primary command

From the repository root:

```bash
python tools/export_chatgpt_context.py --keep-directory
```

The default export is written outside Git under:

```text
/content/simplee_context_exports/
```

The command prints the exact ZIP path to upload.

## Modes

Focused mode is the default. It includes recent work, runtime candidates, related tests, DevKit source, and recent integration checkpoints.

```bash
python tools/export_chatgpt_context.py --mode focused
```

Full mode includes all safe tracked text files subject to size limits.

```bash
python tools/export_chatgpt_context.py --mode full
```

## Useful options

```bash
python tools/export_chatgpt_context.py \
  --mode focused \
  --checkpoint-limit 3 \
  --recent-commit-limit 25 \
  --max-file-bytes 524288 \
  --max-total-bytes 41943040 \
  --keep-directory
```

## Export contents

Each package contains:

- `AI_HANDOFF.md`
- `export_summary.json`
- `git_context.json`
- `repository_tree.txt`
- `tracked_files.txt`
- `repository_summary.json`
- `runtime_candidates.json`
- `environment_variable_names.json`
- `source_manifest.json`
- `source/` with selected real repository files

## Safety boundaries

The exporter:

- performs no checkout, reset, merge, commit, push, or provider action;
- excludes `.git`, caches, virtual environments, and common secret/key files;
- excludes runtime data directories such as `data/`, `data_v2/`, and `tower/data/`;
- exports environment variable names only, never environment values;
- sanitizes remote URLs to remove embedded credentials;
- writes exports outside the repository by default.

The DevKit is designed to be reusable across Tower, Observatory, Vault, Clouds, Grounds, Teller, and future Simplee repositories.
