---
name: cerebras-sdk
description: Download, install and run the Cerebras SDK 2.10.1 (cslc compiler, cs_python, simulator) in a Claude Code cloud container. Use when asked to set up, run, compile or simulate CSL programs / Cerebras SDK examples, or when `cslc`/`cs_python`/`singularity` is missing.
---

# Cerebras SDK 2.10.1: setup and run

The SDK ships as a Google Drive file owned by the user:
`Cerebras-SDK-2.10.1-sdk-202606181328-8faf87a26e.tar.gz` (Drive ID `14XW4OU6w8qW4YpvmqCElGbabQ-2VsZKu`, 3,429,958,480 bytes).
It contains host wrapper scripts (`cslc`, `cs_python`, `csdb`, `cs_readelf`, `sdk_debug_shell`) that run tools inside a
Singularity image (`sdk-cbcore-*.sif`, 3.4 GB), plus `csl-extras-*.tar.gz` (tutorials and benchmarks).
Programs run on the SDK's bundled simulator; no Cerebras hardware is needed.

## Quick path

```bash
bash .claude/skills/cerebras-sdk/scripts/setup.sh            # installs into /home/user/cerebras-sdk
source /home/user/cerebras-sdk/env.sh
```

The script is idempotent and does every step below, ending with a smoke test that must print
`Smoke test passed`. Run it with `run_in_background` (the download plus extraction takes several minutes).
Peak disk use is about 7 GB; the script deletes the archive after it verifies and extracts it.

## What the script does, and the pitfalls behind each step

1. **Download.** `curl` from `https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t`.
   - `confirm=t` skips Drive's "can't scan for viruses" page on large files.
   - If curl fails with `CONNECT tunnel failed, response 403`, the environment's network policy blocks Google.
     The user must allow `drive.google.com` and `drive.usercontent.google.com` (or full access) under the
     environment's Network access settings, then possibly start a new session.
   - Do **not** use the Google Drive MCP connector: it returns file content inline as base64 and cannot carry a 3.4 GB file.
2. **Verify and extract.** `gzip -t`, then `tar -xzf`. The archive has **no top-level folder**, so extract it into a
   dedicated directory. Then `sha256sum -c sha256sum.txt`.
3. **Examples.** Unpack `csl-extras-*.tar.gz` into `<sdk>/extras/`.
4. **Container runtime.** The wrappers require `singularity` on PATH.
   - Install `singularity-container` from Ubuntu universe (`apt-get install -y singularity-container`, which gives singularity-ce 4.1.1).
   - Don't bother with Apptainer: the GitHub API is gated in this session (403), `add-apt-repository` is broken
     (`No module named 'apt_pkg'`), and adding the Apptainer PPA by hand was denied by the auto-mode permission classifier.
5. **Required environment** (written to `<sdk>/env.sh`):
   - `SINGULARITY_DROP_CAPS=CAP_SYS_RESOURCE`. Without it every tool fails with
     `Requesting capability set 0x000001ffffffffff while permitted capability set is 0x000001fffeffffff`,
     because the cloud container lacks CAP_SYS_RESOURCE. (`SINGULARITY_USERNS=1` does not work either: there is no fusermount and extraction fails.)
   - `TMPDIR=<sdk>/tmp`, because the wrappers bind-mount `$TMPDIR`.
   - SDK directory on `PATH`.

## Running programs

Every example directory has `commands_wse3.sh` and `commands_wse2.sh` (the target architecture), along with `layout.csl`,
`pe_program.csl` and `run.py`. Run one from inside its directory:

```bash
source /home/user/cerebras-sdk/env.sh
cd /home/user/cerebras-sdk/extras/csl-extras-*/examples/tutorials/gemv-01-complete-program
bash commands_wse3.sh          # ends with "SUCCESS!"
```

What that script runs:

```bash
cslc --arch=wse3 ./layout.csl --fabric-dims=8,3 --fabric-offsets=4,1 -o out --memcpy --channels 1
cs_python run.py --name out
```

- Tutorials live in `examples/tutorials/` (gemv-00..09, pipeline-*, sdklayout-*, topic-01..16); benchmarks are in `examples/benchmarks/`.
- The wrappers only bind-mount the current directory. If a program imports CSL files from elsewhere, set
  `CSL_IMPORT_PATH=$(realpath dir1):$(realpath dir2)`.
- `cs_python` is the SDK's Python 3.11 with `cerebras.sdk` available. Use it, not the host Python, for `run.py` scripts.
- Verified working: `gemv-01-complete-program` and `gemv-05-multiple-pes` on WSE-3 both print `SUCCESS!`.

## Notes

- The container is ephemeral, so the install is lost when the session ends. Re-run `setup.sh` in a new session.
- Never commit the SDK files to the repo; they are licensed (see `cerebras-software-eula.pdf`) and huge.
