# Moduleur community patch workspace

This repository contains reproducible Shmoergh Moduleur patches and scripts for
maintaining local copies of official source code, firmware, and patch sheets.

## Contents

- `patches/` — editable patch definitions, vector overlays, and finished PDFs.
- `downloads/` — shared instructions and refresh script; downloaded files stay local.
- `upstream/` — shared instructions and refresh script; official Git clones stay local.

```text
moduleur/
├── README.md
├── .gitignore
├── patches/
├── downloads/
│   ├── README.md                 # Shared
│   ├── refresh.sh                # Shared
│   ├── firmware/                 # Local, ignored
│   ├── patchsheets/              # Local, ignored
│   ├── history/                  # Local, ignored; created on changes
│   └── …                        # Local manifests, checksums, change log
└── upstream/
    ├── README.md                 # Shared
    ├── refresh.sh                # Shared
    └── <official-repository>/    # Local, ignored independent Git clones
```

## Set up and refresh local resources

From this repository's root, download the currently linked official firmware
and patch sheets:

```sh
./downloads/refresh.sh
./downloads/refresh.sh --verify
```

Current files live directly under `downloads/firmware/` and
`downloads/patchsheets/`. Unchanged refreshes create no snapshots. Replaced file
contents are archived by content hash, and actual changes are logged. Files no longer linked upstream remain in place; refresh never prunes them.
See [downloads instructions](downloads/README.md) for sources and details.

Clone the desired official [Shmoergh repositories](https://github.com/shmoergh)
into `upstream/`, following the [upstream instructions](upstream/README.md).
This workspace uses all the listed official repositories except `hog`.
These are independent clones, not submodules or copies tracked in this repository.
For example:

```sh
git clone https://github.com/shmoergh/brain-sdk.git upstream/brain-sdk
./upstream/refresh.sh
```

The upstream refresh script updates existing clones only; it does not create
missing clones. It skips local changes and uses fast-forward-only pulls.
The scripts locate their data folders relative to their own paths, so they can
also be invoked from another working directory. They require Git for upstream
updates, and standard shell utilities, curl, unzip, and a SHA-256 tool for downloads,
plus network access. Python is not required. Use a POSIX shell on macOS/Linux,
or Git Bash/WSL on Windows; see [platform requirements](downloads/README.md#platform-requirements).

## What belongs in Git

Share patch definitions and generated patch PDFs/overlays, plus resource-management
scripts and documentation. Within `downloads/`
and `upstream/`, `.gitignore` allows only each folder's `README.md` and
`refresh.sh`. Downloaded firmware, generated metadata, history, temporary files,
and upstream repositories remain local. Common firmware and archive extensions
are also ignored throughout this repository.

Do not force-add ignored material. Git ignore rules prevent ordinary additions,
but cannot prevent `git add -f` or untrack files already committed. Review
`git status` before committing.

Keep private account information and credentials outside this repository.
Publishing a repository exposes its history as well as current files. The local
resource folders require their own backup; pushing this repository does not
back up their contents. Downloading firmware does not install it on an instrument.

## Included patch

[Alien Thunder](patches/alien-thunder/patch.pdf) has a one-page description
followed by the annotated official patch sheet. Its directory contains the
editable JSON definition, vector overlay, PDF overlay, and finished two-page PDF.
