#!/bin/bash
# Sync README.md files into docs/, renaming them as <parent-dir>.md in the corresponding docs subfolder

set -e

SRC_ROOT="$(dirname "$0")/.."
DOCS_ROOT="$(dirname "$0")"

find "$SRC_ROOT" -type f -name 'README.md' | grep -v "$DOCS_ROOT" | while read src_readme; do
    # Get relative path from project root
    rel_path="${src_readme#$SRC_ROOT/}"
    # Get parent directory name
    parent_dir="$(basename $(dirname "$src_readme"))"
    # Get docs destination subfolder (mirror the structure, but skip README.md filename)
    rel_dir="$(dirname "$rel_path")"
    dest_dir="$DOCS_ROOT/$rel_dir"
    mkdir -p "$dest_dir"
    # Destination filename: <parent-dir>.md
    dest_file="$dest_dir/$parent_dir.md"
    cp "$src_readme" "$dest_file"
    echo "Copied $src_readme to $dest_file"
done

echo "All README.md files synced and renamed in docs/"
