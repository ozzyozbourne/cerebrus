#!/usr/bin/env bash
# Idempotent setup of the Cerebras SDK 2.10.1 in a Claude Code cloud container (Ubuntu 24.04, root).
# Usage: bash setup.sh [install_dir]   (default: /home/user/cerebras-sdk)
set -euo pipefail

SDK_DIR="${1:-/home/user/cerebras-sdk}"
DRIVE_ID="14XW4OU6w8qW4YpvmqCElGbabQ-2VsZKu"
ARCHIVE="$SDK_DIR/sdk.tar.gz"
EXPECTED_SIZE=3429958480

log() { printf '\033[34m[setup]\033[0m %s\n' "$*"; }
die() { printf '\033[31m[setup] ERROR:\033[0m %s\n' "$*" >&2; exit 1; }

mkdir -p "$SDK_DIR"

# 1. Download the SDK archive from Google Drive (needs network access to drive.usercontent.google.com).
if ls "$SDK_DIR"/*.sif >/dev/null 2>&1 && [ -x "$SDK_DIR/cslc" ]; then
  log "SDK already extracted in $SDK_DIR, skipping download/extract"
else
  size=$(stat -c %s "$ARCHIVE" 2>/dev/null || echo 0)
  if [ "$size" != "$EXPECTED_SIZE" ]; then
    log "Downloading SDK archive (~3.4 GB) ..."
    curl -fSL --retry 5 -C - -o "$ARCHIVE" \
      "https://drive.usercontent.google.com/download?id=${DRIVE_ID}&export=download&confirm=t" \
      || die "Download failed. If curl reports 'CONNECT tunnel failed, response 403', the environment's network policy blocks Google Drive: ask the user to allow drive.google.com and drive.usercontent.google.com (or full access) in the environment settings."
    size=$(stat -c %s "$ARCHIVE")
    [ "$size" = "$EXPECTED_SIZE" ] || die "Archive size $size != expected $EXPECTED_SIZE"
  fi
  log "Verifying gzip integrity ..."
  gzip -t "$ARCHIVE"
  log "Extracting (archive has no top-level folder; files land directly in $SDK_DIR) ..."
  tar -xzf "$ARCHIVE" -C "$SDK_DIR"
  (cd "$SDK_DIR" && sha256sum -c sha256sum.txt) || die "Checksum mismatch"
  rm -f "$ARCHIVE"   # frees 3.4 GB; the .sif is what matters
fi

# 2. Unpack the examples (tutorials + benchmarks).
if [ ! -d "$SDK_DIR/extras" ]; then
  mkdir -p "$SDK_DIR/extras"
  tar -xzf "$SDK_DIR"/csl-extras-*.tar.gz -C "$SDK_DIR/extras"
fi

# 3. Install Singularity from Ubuntu's own repos (third-party Apptainer PPA is blocked by the permission classifier).
if ! command -v singularity >/dev/null 2>&1; then
  log "Installing singularity-container from Ubuntu universe ..."
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq singularity-container
fi
singularity --version

# 4. Environment file.
cat > "$SDK_DIR/env.sh" <<ENVEOF
# source this file before using the SDK
export PATH=$SDK_DIR:\$PATH
export TMPDIR=$SDK_DIR/tmp
mkdir -p "\$TMPDIR"
# The cloud container lacks CAP_SYS_RESOURCE; Singularity-as-root fails unless it is dropped.
export SINGULARITY_DROP_CAPS=CAP_SYS_RESOURCE
ENVEOF

# 5. Smoke test: compile + simulate a tutorial.
# shellcheck disable=SC1091
source "$SDK_DIR/env.sh"
cd "$SDK_DIR"/extras/csl-extras-*/examples/tutorials/gemv-01-complete-program
if bash commands_wse3.sh 2>&1 | tail -1 | grep -q 'SUCCESS!'; then
  log "Smoke test passed (gemv-01-complete-program on WSE-3 simulator)."
else
  die "Smoke test failed; rerun 'bash commands_wse3.sh' in $(pwd) to see the output."
fi
log "Done. Run: source $SDK_DIR/env.sh"
