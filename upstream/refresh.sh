#!/bin/sh
# Refresh existing clones beside this script, preserving local work.
set -eu

if [ "$#" -gt 0 ]; then
    if [ "$#" -eq 1 ] && [ "$1" = '--help' ]; then
        printf 'Usage: refresh.sh\nRefresh existing Git clones beside this script.\n'
        exit 0
    fi
    printf 'Usage: refresh.sh\n' >&2
    exit 2
fi

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
result=0

for repo in "$SCRIPT_DIR"/*/; do
    [ -e "$repo/.git" ] || continue
    name=$(basename "$repo")
    if ! changes=$(git -C "$repo" status --porcelain); then
        printf 'Cannot inspect %s; skipping\n' "$name" >&2
        result=1
        continue
    fi
    if [ -n "$changes" ]; then
        printf 'Skipping %s: local changes\n' "$name"
        continue
    fi
    if ! git -C "$repo" symbolic-ref -q HEAD >/dev/null ||
       ! git -C "$repo" rev-parse --verify '@{upstream}' >/dev/null 2>&1; then
        printf 'Skipping %s: no active tracking branch\n' "$name"
        continue
    fi
    printf 'Refreshing %s\n' "$name"
    if ! git -C "$repo" fetch origin --prune --tags; then
        printf 'Fetch failed for %s; inspect before retrying\n' "$name" >&2
        result=1
        continue
    fi
    if ! git -C "$repo" pull --ff-only; then
        printf 'Pull failed for %s; inspect before retrying\n' "$name" >&2
        result=1
    fi
done

exit "$result"
