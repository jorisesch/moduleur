#!/bin/sh
# POSIX shell; no Python, jq, or platform-specific stat/date options.
set -eu
LC_ALL=C
export LC_ALL
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
GUIDE=https://www.shmoergh.com/guides/moduleur-user-guide/
INDEX=https://www.shmoergh.com/brain-firmwares/
fail() { printf 'Refresh failed: %s\n' "$*" >&2; exit 1; }
usage() {
    printf '%s\n' 'Usage: refresh.sh [--verify [DIRECTORY]]' \
        'Refresh current downloads, retaining unlisted files and archiving replaced content.' \
        '--verify checks existing files without network access.'
}
MODE=refresh
case $# in
    0) ;;
    1) case $1 in --help|-h) usage; exit 0;; --verify) MODE=verify;; *) usage >&2; exit 2;; esac ;;
    2) [ "$1" = --verify ] || { usage >&2; exit 2; }
       MODE=verify; ROOT=$(CDPATH= cd -- "$2" && pwd) ;;
    *) usage >&2; exit 2 ;;
esac
for tool in awk sed sort cmp cp mv mkdir rm rmdir mktemp date wc head unzip cat dirname; do
    command -v "$tool" >/dev/null 2>&1 || fail "Missing command: $tool"
done
if command -v sha256sum >/dev/null 2>&1; then
    HASH=sha256sum
elif command -v shasum >/dev/null 2>&1; then
    HASH=shasum
elif command -v openssl >/dev/null 2>&1; then
    HASH=openssl
else
    fail 'Install sha256sum, shasum, or openssl for SHA-256 checks.'
fi
hash() {
    case $HASH in
        sha256sum) sha256sum < "$1" ;;
        shasum) shasum -a 256 < "$1" ;;
        openssl) openssl dgst -sha256 < "$1" ;;
    esac | awk '{print ($NF == "-" ? $1 : $NF)}'
}
validate() {
    case $1 in
        *.zip) unzip -t "$1" >/dev/null || fail "Invalid ZIP: $1" ;;
        *.pdf) [ "$(head -c 5 "$1")" = '%PDF-' ] || fail "Invalid PDF header: $1" ;;
        *) fail "Unsupported artifact: $1" ;;
    esac
}
# Narrow filenames make tab-separated metadata and checksum files portable.
check_rows() {
    awk -F '\t' '
        NF != 5 || $1 !~ /^(firmware|patchsheets)\/[A-Za-z0-9][A-Za-z0-9._-]*\.(zip|pdf)$/ ||
        $2 !~ /^https:\/\/[^[:space:]]+$/ || $3 !~ /^[0-9]+$/ ||
        length($4) != 64 || $4 ~ /[^0-9a-f]/ || $5 !~ /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$/ || seen[$1]++ {exit 1}
    ' "$1" || fail "Invalid or duplicate manifest rows: $1"
}
checksums() { awk -F '\t' '{print $4 "  " $1}' "$1"; }
TAB=$(printf '\t')
verify() {
    [ -f "$ROOT/manifest.tsv" ] || fail 'Missing manifest.tsv; see README for metadata format.'
    check_rows "$ROOT/manifest.tsv"
    checksums "$ROOT/manifest.tsv" > "$STAGE/checksums"
    cmp -s "$STAGE/checksums" "$ROOT/SHA256SUMS" || fail 'SHA256SUMS does not match manifest.tsv'
    while IFS="$TAB" read -r file url bytes digest downloaded; do
        [ ! -L "$ROOT/${file%%/*}" ] && [ ! -L "$ROOT/$file" ] || fail "Symlink in artifact path: $file"
        [ -f "$ROOT/$file" ] || fail "Missing file: $file"
        [ "$(wc -c < "$ROOT/$file" | awk '{print $1}')" = "$bytes" ] || fail "Size mismatch: $file"
        [ "$(hash "$ROOT/$file")" = "$digest" ] || fail "Checksum mismatch: $file"
        validate "$ROOT/$file"
        printf 'Verified %s\n' "$file"
    done < "$ROOT/manifest.tsv"
}
# Lock prevents overlapping refreshes. A killed process may leave a stale lock.
LOCK="$ROOT/.refresh.lock"
mkdir "$LOCK" 2>/dev/null || fail "Lock exists: $LOCK (another refresh may be running)"
STAGE=
cleanup() { [ -z "$STAGE" ] || rm -rf "$STAGE"; rmdir "$LOCK"; }
trap cleanup 0
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP
STAGE=$(mktemp -d "$ROOT/.refresh-XXXXXX")
if [ "$MODE" = verify ]; then verify; exit 0; fi
command -v curl >/dev/null 2>&1 || fail 'Missing command: curl'
if [ -f "$ROOT/manifest.tsv" ]; then
    verify
    cp "$ROOT/manifest.tsv" "$STAGE/old.tsv"
else
    [ ! -e "$ROOT/manifest.json" ] && [ ! -e "$ROOT/SHA256SUMS" ] ||
        fail 'Legacy metadata found without manifest.tsv; migrate it before refreshing (see README).'
    : > "$STAGE/old.tsv"
fi
fetch() {
    curl --fail --location --silent --show-error --retry 3 \
        --connect-timeout 20 --max-time 180 --proto '=https' --proto-redir '=https' \
        "$1" --output "$2" ||
        fail "Unable to download $1; existing downloads and metadata have not been changed."
}
# Extract quoted hrefs from the official pages. Fail closed if expected links disappear.
links() {
    awk '
    BEGIN {RS="<"}
    /^[aA][[:space:]]/ {
        text=$0
        while (match(tolower(text), /href[[:space:]]*=[[:space:]]*/)) {
            text=substr(text,RSTART+RLENGTH); q=substr(text,1,1)
            if (q == "\"" || q == sprintf("%c",39)) {
                text=substr(text,2); end=index(text,q)
                if (end) {u=substr(text,1,end-1); gsub(/&amp;/,"\\&",u); print u}
            }
            break
        }
    }' "$1"
}
fetch "$INDEX" "$STAGE/index.html"
fetch "$GUIDE" "$STAGE/guide.html"
links "$STAGE/index.html" | awk '
 /^https:\/\/github.com\/shmoergh\/[^\/]+\/releases\/download\/[^\/]+\/[^?]+\.zip([?].*)?$/ {print "firmware\t" $0}
' | sort -u > "$STAGE/urls"
[ -s "$STAGE/urls" ] || fail 'No firmware links found; inspect the official page.'
links "$STAGE/guide.html" | awk '
 {
    if ($0 ~ /^\/\//) $0="https:" $0
    else if ($0 ~ /^\//) $0="https://www.shmoergh.com" $0
    if ($0 ~ /^https:\/\/[^[:space:]]*patch[^[:space:]]*\.pdf([?].*)?$/) print "patchsheets\t" $0
 }' | sort -u > "$STAGE/sheets"
[ -s "$STAGE/sheets" ] || fail 'No patch sheet links found; inspect the official page.'
cat "$STAGE/sheets" >> "$STAGE/urls"
TODAY=$(date -u +%Y-%m-%d)
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
mkdir "$STAGE/firmware" "$STAGE/patchsheets"
: > "$STAGE/new.tsv"
while IFS="$TAB" read -r category url; do
    clean=${url%%\?*}; name=${clean##*/}
    case $name in ''|*[!A-Za-z0-9._-]*|[!A-Za-z0-9]*) fail "Unsupported filename: $name";; esac
    file="$category/$name"
    [ ! -e "$STAGE/$file" ] || fail "Duplicate filename: $file"
    printf 'Downloading %s\n' "$name"
    fetch "$url" "$STAGE/$file"
    validate "$STAGE/$file"
    digest=$(hash "$STAGE/$file")
    bytes=$(wc -c < "$STAGE/$file" | awk '{print $1}')
    downloaded=$(awk -F '\t' -v f="$file" -v h="$digest" '$1==f && $4==h {print $5}' "$STAGE/old.tsv")
    [ -n "$downloaded" ] || downloaded=$TODAY
    printf '%s\t%s\t%s\t%s\t%s\n' "$file" "$url" "$bytes" "$digest" "$downloaded" >> "$STAGE/new.tsv"
done < "$STAGE/urls"
check_rows "$STAGE/new.tsv"
# This is a preservation collection, not a mirror: disappearance upstream must
# never remove a saved file, even when the rest of the page still parses.
awk -F '\t' 'FILENAME==ARGV[1] {seen[$1]=1; next}
 !($1 in seen) {print}
' "$STAGE/new.tsv" "$STAGE/old.tsv" > "$STAGE/retained.tsv"
if [ -s "$STAGE/retained.tsv" ]; then
    while IFS="$TAB" read -r file url bytes digest downloaded; do
        printf 'Retaining previously downloaded file no longer listed: %s\n' "$file"
    done < "$STAGE/retained.tsv"
    cat "$STAGE/retained.tsv" >> "$STAGE/new.tsv"
fi
check_rows "$STAGE/new.tsv"
# Plan additions/replacements only, before modifying any managed file.
awk -F '\t' 'FILENAME==ARGV[1] {old[$1]=$0; hash[$1]=$4; url[$1]=$2; next}
 {seen[$1]=1; if (!($1 in old)) print "added\t" $1;
  else if ($4!=hash[$1]) print "changed\t" $1;
  else if ($2!=url[$1]) print "source_changed\t" $1}
' "$STAGE/old.tsv" "$STAGE/new.tsv" | sort > "$STAGE/plan"
if [ ! -s "$STAGE/plan" ]; then
    printf 'No changes; existing files and metadata retained.\n'
    exit 0
fi
# Check destinations and existing history before publication.
[ ! -L "$ROOT/history" ] || fail 'history must not be a symlink'
while IFS="$TAB" read -r action file; do
    [ ! -L "$ROOT/${file%%/*}" ] || fail "Symlink directory: $file"
    if [ "$action" = added ]; then
        [ ! -e "$ROOT/$file" ] && [ ! -L "$ROOT/$file" ] || fail "Unmanaged file would be overwritten: $file"
    fi
    case $action in changed)
        digest=$(awk -F '\t' -v f="$file" '$1==f {print $4}' "$STAGE/old.tsv")
        archive="$ROOT/history/$digest/$file"
        for path in "$ROOT/history/$digest" "$ROOT/history/$digest/${file%%/*}" "$archive"; do
            [ ! -L "$path" ] || fail "Symlink in history: $path"
        done
        if [ -e "$archive" ]; then
            [ "$(hash "$archive")" = "$digest" ] || fail "History checksum mismatch: $archive"
        fi ;;
    esac
done < "$STAGE/plan"
# Generate JSON from the canonical TSV without requiring a JSON interpreter.
cat > "$STAGE/json.awk" <<'AWK'
function quote(s,    out,i,c) {
    out="\""
    for(i=1;i<=length(s);i++) {
        c=substr(s,i,1)
        if(c=="\\" || c=="\"") out=out "\\"
        out=out c
    }
    return out "\""
}
function record(row,    v) {
    if(row=="") return "null"
    split(row,v,"\t")
    return "{\"file\":" quote(v[1]) ",\"source_url\":" quote(v[2]) ",\"bytes\":" v[3] ",\"sha256\":" quote(v[4]) ",\"downloaded_on\":" quote(v[5]) "}"
}
FILENAME==ARGV[1] {old[$1]=$0; next}
FILENAME==ARGV[2] {new[$1]=$0; rows[++count]=$0; next}
{
    event="{\"at\":" quote(now) ",\"action\":" quote($1) ",\"before\":" record(old[$2]) ",\"after\":" record(new[$2])
    if($1=="changed") {
        split(old[$2],v,"\t")
        event=event ",\"archived_file\":" quote("history/" v[4] "/" $2)
    }
    print event "}" > eventfile
}
END {
    printf "{\"updated_at\":%s,\"guide_url\":%s,\"firmware_index_url\":%s,\"files\":[",quote(now),quote(guide "#downloads"),quote(indexurl) > manifest
    for(i=1;i<=count;i++) printf "%s%s",(i>1 ? "," : ""),record(rows[i]) > manifest
    print "]}" > manifest
}
AWK
awk -F '\t' -v now="$NOW" -v guide="$GUIDE" -v indexurl="$INDEX" \
    -v eventfile="$STAGE/events" -v manifest="$STAGE/manifest.json" -f "$STAGE/json.awk" \
    "$STAGE/old.tsv" "$STAGE/new.tsv" "$STAGE/plan"
checksums "$STAGE/new.tsv" > "$STAGE/SHA256SUMS"
while IFS="$TAB" read -r action file; do
    case $action in changed)
        digest=$(awk -F '\t' -v f="$file" '$1==f {print $4}' "$STAGE/old.tsv")
        archive="$ROOT/history/$digest/$file"
        mkdir -p "$(dirname "$archive")"
        [ -f "$archive" ] || cp -p "$ROOT/$file" "$archive"
        [ "$(hash "$archive")" = "$digest" ] || fail "Archived copy failed verification: $archive" ;;
    esac
    case $action in
        added|changed) mkdir -p "$ROOT/${file%%/*}"; mv "$STAGE/$file" "$ROOT/$file" ;;
    esac
done < "$STAGE/plan"
mv "$STAGE/new.tsv" "$ROOT/manifest.tsv"
mv "$STAGE/manifest.json" "$ROOT/manifest.json"
mv "$STAGE/SHA256SUMS" "$ROOT/SHA256SUMS"
cat "$STAGE/events" >> "$ROOT/changes.jsonl"
printf 'Applied %s changes.\n' "$(wc -l < "$STAGE/plan" | awk '{print $1}')"
