# Moduleur community patch workspace

This repository contains reproducible Shmoergh Moduleur patches, a Codex skill
for creating them, and small tools for keeping local copies of official resources.

## Included patch

[Alien Thunder](patches/alien-thunder/patch.pdf) has a one-page description
followed by the annotated official patch sheet. Its directory contains the
editable JSON definition, vector overlay, PDF overlay, and finished two-page PDF.

## Patch-authoring skill

The repository-scoped [Moduleur patch skill](.agents/skills/moduleur-patches/SKILL.md)
contains the authoring workflow, format reference, panel map, renderer, and Python
requirements. Codex discovers it automatically under `.agents/skills/` when
working inside this repository.

The skill records every active cable and internal normal, every critical control
position, and the Brain firmware and mode. It generates a compact vector overlay
and a two-page PDF using the minimal style by default. Additional presentation
styles are available through the renderer's `--style` option.

## Repository layout

```text
moduleur/
├── .agents/skills/moduleur-patches/   # Shared patch-authoring skill
├── patches/                           # Definitions, overlays, and finished PDFs
├── downloads/                         # Local firmware and patch sheets
└── upstream/                          # Local official source clones
```

## Local Shmoergh resources

Download the currently linked firmware and patch sheets, or verify the existing
collection:

```sh
./downloads/refresh.sh
./downloads/refresh.sh --verify
```

See [downloads/README.md](downloads/README.md) for supported platforms, source
URLs, preservation behavior, and recovery details. Existing files are retained
when the Shmoergh site is unavailable.

Official source repositories can be refreshed with:

```sh
./upstream/refresh.sh
```

See [upstream/README.md](upstream/README.md) for the repository list and refresh
behavior. The `hog` repository is intentionally excluded.

## What belongs in Git

Patch definitions, generated overlays and PDFs, the patch skill, and maintenance
documentation belong in Git. Downloaded firmware, patch-sheet source files,
history, generated metadata, private notes, and upstream clones stay local and
are covered by `.gitignore`.

Do not force-add ignored material. Review `git status` before committing because
publishing a repository exposes its history as well as its current files.
