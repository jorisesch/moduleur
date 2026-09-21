# Moduleur downloads

This folder stores official firmware archives and printable patch sheets for the
Shmoergh Moduleur. Only this README and `refresh.sh` are shared in this
repository. All downloaded files, manifests, checksums, change logs, and history
are ignored by Git; pushing the repository does not back them up.

## Sources

- [Moduleur user guide — Downloads](https://www.shmoergh.com/guides/moduleur-user-guide/#downloads)
- [Brain firmwares](https://www.shmoergh.com/brain-firmwares/), which links to firmware release ZIPs on GitHub
- [Printable patch sheet](https://www.shmoergh.com/content/files/2026/02/moduleur-patch-sheet.pdf), as linked when the initial snapshot was downloaded

`manifest.tsv` is the canonical inventory of saved files: source URLs, download
dates, byte sizes, and locally calculated SHA-256 checksums. `manifest.json` is
also generated for convenient use by other tools.

## Layout

```text
downloads/
├── README.md
├── refresh.sh                  # Refresh current files or verify them
├── firmware/                   # Saved firmware ZIPs, including older releases
├── patchsheets/                 # Saved printable PDFs
├── manifest.tsv                # Canonical inventory, read by the shell script
├── manifest.json               # JSON export of the inventory
├── SHA256SUMS                  # Checksums for current files
├── changes.jsonl               # Created when changes are detected
└── history/                    # Created only for replaced file contents
    └── <sha256>/               # Previous content, deduplicated by hash and path
        └── <category>/<filename>
```

Original filenames are retained. Refreshing does not create dated snapshots.

## Files initially downloaded on 2026-09-20

| Artifact | Saved file |
| --- | --- |
| Le Controlleur v1.4 | [le-controlleur-v1.4.zip](firmware/le-controlleur-v1.4.zip) |
| Lo-Fi Delay v1.4 | [lo-fi-delay-v1.4.zip](firmware/lo-fi-delay-v1.4.zip) |
| CV Utilities v1.3 | [brain-cv-utils-v1.3.zip](firmware/brain-cv-utils-v1.3.zip) |
| CV Tuner v1.3 | [brain-cv-tuner-v1.3.zip](firmware/brain-cv-tuner-v1.3.zip) |
| Brain Diagnostics v1.2 | [brain-diagnostics-v1.2.zip](firmware/brain-diagnostics-v1.2.zip) |
| Printable patch sheet | [moduleur-patch-sheet.pdf](patchsheets/moduleur-patch-sheet.pdf) |

These are the versions linked by the official pages at download time. They are
not a claim about the latest available releases on a later date.

## Refresh downloads

Run [refresh.sh](refresh.sh) from this `downloads/` directory:

```sh
./refresh.sh
```

The POSIX shell script requires no Python or `jq`. It discovers the current
firmware ZIPs and patch-sheet PDFs from the official pages and stages downloads
in a temporary directory. All downloads are checked before current files change.

SHA-256 comparison determines what changed:

- Unchanged files retain their contents, modification times, and download dates.
  An unchanged run creates no history or log entries and leaves metadata alone.
- New files are added to the current collection.
- Replaced files are copied to `history/<sha256>/<category>/<filename>` before
  replacement; the archived copy is checksum-verified before replacing the
  working file. Existing history copies are reused.
- Files no longer linked remain in place and in the manifests/checksums. A missing
  link is never interpreted as a deletion request. New release filenames are
  added alongside older releases.
- Source URL changes are logged even when file contents are identical.

`changes.jsonl` records additions, replacements, and source URL changes,
including timestamps and before/after metadata. The manifests and checksum file
track the current collection. Temporary downloads are removed after each run.

The script downloads files to compare their contents on each run; it avoids
storing duplicate snapshots, rather than avoiding network transfers. If links
cannot be discovered or validation fails during staging, current files remain
unchanged. Publication uses individual file replacements, not a transaction
across the whole directory; an interruption during publication may require
inspection. Concurrent runs are blocked by `.refresh.lock`. After an uncatchable
termination, remove that empty lock directory only after confirming no refresh
is still running.

Link discovery supports quoted HTML links and the official pages' current URL
formats. It deliberately rejects unsupported filenames (including spaces and
percent-encoded names) and fails if either category has no matching links. If the
pages change, inspect them and update the parser rather than treating missing
links as a request to remove everything.

Invoke the script from any working directory; files are always stored beside it.

Updating the Git clones in `../upstream/` does not refresh these downloads or
retrieve GitHub release attachments. Downloading a firmware archive also does
not install it on the instrument; consult the official firmware instructions
when ready to install.

## If Shmoergh or GitHub becomes unavailable

This folder is a preservation collection, not a mirror that prunes missing files.
DNS failures, connection errors, timeouts, HTTP errors, missing download categories,
or invalid ZIP/PDF responses stop the refresh with a nonzero exit status. Both
index pages and every discovered artifact must be downloaded and validated in a
temporary directory before any saved artifact or metadata is updated. Cleanup
removes only that run's temporary directory and lock, never saved downloads.

If the website still loads but omits some old links, those saved files stay in
`firmware/` or `patchsheets/`, with their original source URL, date, and checksum.
If nothing else changed, even the manifests and change log remain untouched.
The script has no automatic deletion or pruning operation for saved artifacts.

A valid changed file at the same path replaces the working copy only after the
previous bytes have been archived and checked. This preserves the earlier
version even if the upstream publisher changes or repurposes a download URL.
The existing per-file publication caveat above still applies to interrupted
writes; a refresh is not a transactional backup system.

`./refresh.sh --verify` works offline. Local files and previously generated patch
PDFs remain usable without the website. New patch rendering also works offline
when its matching background and Python dependencies are already installed.

**Back up the entire `downloads/` directory separately**, including both manifests,
`SHA256SUMS`, `changes.jsonl`, and `history/`. These files are intentionally ignored
by Git: publishing this repository does not preserve them for you. Keep another
copy on a separate disk or backup service if the upstream site may disappear.

## Verify current downloads

Run from this `downloads/` directory:

```sh
./refresh.sh --verify
```

Checksums detect changes relative to the files originally saved. These checksums
were calculated locally, not supplied or signed by the publisher. Keep the
manifest, change log, history, and checksum file with the artifacts, and back up this folder separately.

## Platform requirements

- **macOS:** run with `sh ./refresh.sh` or `./refresh.sh`. It uses the standard
  shell utilities, `curl`, `unzip`, and an available SHA-256 tool.
- **Linux:** use the same command. Install `curl` and `unzip` if missing; most
  distributions provide `sha256sum` through coreutils.
- **Windows:** run from **Git Bash** or **WSL**, with `curl`, `unzip`, and the
  utilities below available. Native PowerShell and Command Prompt do not execute
  POSIX shell scripts directly. WSL uses the Linux setup; Git Bash installations
  can vary, so missing commands must be installed in that environment.

SHA-256 selection is automatic: `sha256sum`, then `shasum`, then `openssl`.
Other required utilities are `awk`, `sed`, `sort`, `cmp`, `cp`, `mv`, `mkdir`,
`rm`, `rmdir`, `mktemp`, `date`, `wc`, `head`, `cat`, and `dirname`. Missing
requirements are reported before downloads begin. Shell files are kept with LF
line endings through the repository's `.gitattributes`.

The implementation is tested on macOS with `sh`, Bash, and dash. Linux and
Windows execution still need verification on those platforms.

## Local metadata format

`manifest.tsv` has no header and contains five tab-separated fields per line:
relative path, HTTPS source URL, byte size, SHA-256 digest, and download date
(`YYYY-MM-DD`). Artifact paths are limited to `firmware/` and `patchsheets/`
with simple ASCII filenames. Do not edit the inventory to hide a checksum failure.

Existing local metadata has been migrated from the earlier JSON-only format.
The script deliberately refuses to overwrite a JSON-only collection lacking
`manifest.tsv`; such a collection needs its existing records converted into
these five columns before refreshing. A fresh checkout needs no migration.
`--verify` checks the canonical TSV inventory, `SHA256SUMS`, file sizes, hashes,
ZIP integrity, and PDF headers; it does not use the JSON export as its authority.

## Preservation regression tests

From the repository root, run:

```sh
python -m unittest discover -s src/tests -p test_downloads.py -v
```

These optional tests use Python's standard library and simulated curl responses;
they do not contact upstream or modify your real downloads. They cover network
errors at every download stage, invalid responses, missing links, retained old
releases, replacements, history integrity, and unchanged-file metadata. Python
is not required to run `refresh.sh` itself.
