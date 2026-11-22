---
name: cerebras-sdk
description: Download, install and run the Cerebras SDK 2.10.1 (cslc compiler, cs_python, simulator) in a Claude Code cloud container. Use when asked to set up, run, compile or simulate CSL programs / Cerebras SDK examples, or when `cslc`/`cs_python`/`singularity` is missing.
---

# Cerebras SDK 2.10.1: setup and run

The SDK ships as a Google Drive file owned by the user:
`Cerebras-SDK-2.10.1-sdk-202606181328-8faf87a26e.tar.gz` (Drive ID `14XW4OU6w8qW4YpvmqCElGbabQ-2VsZKu`, 3,429,958,480 bytes).
It contains host wrapper scripts (`cslc`, `cs_python`, `csdb`, `cs_readelf`, `sdk_debug_shell`) that run tools inside a
Singularity image (`sdk-cbcore-*.sif`, 3,455,725,568 bytes, about 3.5 GB), plus `csl-extras-*.tar.gz` (tutorials and benchmarks).
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
4. **Container runtime.** The wrappers call a `singularity` command and exit with `singularity not in $PATH` without one.
   Either runtime works; the script installs the first only if no `singularity` command exists yet.
   - SingularityCE: `apt-get install -y singularity-container` from Ubuntu universe (4.1.1 on Ubuntu 24.04). This is what
     `setup.sh` installs.
   - Apptainer 1.5.5 from the official PPA (`ppa:apptainer/ppa`) also works: it installs `/usr/bin/singularity` as a
     symlink to `apptainer`, and `cslc`, `cs_python`, `cs_readelf` and all seven course programs ran with it
     (both `--arch=wse3` and `--arch=wse2`). In the session that wrote this skill the PPA could not be added
     (`add-apt-repository` failed with `No module named 'apt_pkg'`, the GitHub API returned 403, and adding the PPA by
     hand was denied by the permission classifier), which is why the script uses the Ubuntu package. If Apptainer is
     already installed, leave it.
5. **Capabilities.** The cloud container runs as root without CAP_SYS_RESOURCE (`grep CapPrm /proc/self/status` shows
   `000001fffeffffff`). A root container that asks for the full capability set then fails, in every tool, with
   `Requesting capability set 0x000001ffffffffff while permitted capability set is 0x000001fffeffffff`. Two fixes, either is enough:
   - `export SINGULARITY_DROP_CAPS=CAP_SYS_RESOURCE` (what `setup.sh` writes to `env.sh`). Apptainer accepts it too and
     prints `INFO: Environment variable SINGULARITY_DROP_CAPS is set, but APPTAINER_DROP_CAPS is preferred` on each call.
   - With Apptainer, set `root default capabilities = no` in `/etc/apptainer/apptainer.conf`; then no environment
     variable is needed. (`singularity exec --keep-privs <sif> true` reproduces the error on such a machine, and adding
     `--drop-caps CAP_SYS_RESOURCE` clears it.)
   - With SingularityCE 4.1.1, `SINGULARITY_USERNS=1` did not work: there is no fusermount and extraction fails.
     (Apptainer 1.5.5 ran `singularity exec --userns <sif> true` without error, but the SDK tools were not tested that way.)
6. **Environment file** (`<sdk>/env.sh`):
   - SDK directory on `PATH`.
   - `TMPDIR=<sdk>/tmp`. The wrappers mount `$TMPDIR` over the container's `/tmp` (so the host's `/tmp` is hidden,
     except for the current directory, which is mounted on top). `/home/user/cerebras-sdk` may be a symlink; the
     wrappers bind the current directory by its real path but `$TMPDIR` as written.
   - The `SINGULARITY_DROP_CAPS` line from step 5.

## Running programs

Most example directories have `commands_wse3.sh` and `commands_wse2.sh` (one per target architecture) and a `run.py`.
The CSL files are often `layout.csl` and `pe_program.csl`, but many examples use other names or a `src/` directory.
Exceptions among the 56 directories: `gemv-00-basic-syntax` and `benchmark-libs` have no scripts; `topic-14-color-swap`,
`25-pt-stencil`, `histogram-torus` and `spmv-hypersparse` have only `commands_wse2.sh`; `topic-15-wse3-microthreads`
and `fft-3d` have only `commands_wse3.sh`. Run an example from inside its directory (or a copy of it):

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

`--memcpy --channels 1` (or more) is required in practice: without `--channels`, `cslc` 2.10.1 stops with
`RuntimeError: n_channels=0 corresponds to the deprecated runtime CSELFRunner`. `--arch` defaults to `wse2`.

- Tutorials live in `examples/tutorials/` (gemv-00..09, pipeline-*, sdklayout-*, topic-01..16); benchmarks are in `examples/benchmarks/`.
- The wrappers bind-mount only the current directory and `$TMPDIR`. If a program imports CSL files from elsewhere
  (five benchmarks import `../benchmark-libs`), set `CSL_IMPORT_PATH=$(realpath dir1):$(realpath dir2)` before `cslc`.
  `cs_python` does not read `CSL_IMPORT_PATH`: everything `run.py` opens must be under the current directory.
- Each run leaves `out/`, `sim.log`, `sim_stats.json`, `simconfig.json` and `simfab_traces/` in the current directory,
  and empty mount-point directories under `$TMPDIR`. Work in a copy if the directory is under version control.
- The whole-run `cycle_count` in `sim_stats.json` grows when the machine is loaded (the simulated wafer keeps
  counting while it waits for the host). Run one simulation at a time when comparing totals.
- `cs_python` is the SDK's Python 3.11 with `cerebras.sdk` available. Use it, not the host Python, for `run.py` scripts.
- Verified working: `gemv-01-complete-program` and `gemv-05-multiple-pes` on WSE-3 both print `SUCCESS!`
  (gemv-01 takes about 15 s), and `ARCH=wse3 bash course/programs/run_all.sh` reports 7 of 7 PASS (also with `ARCH=wse2`).

## Notes

- The container is ephemeral, so the install is lost when the session ends. Re-run `setup.sh` in a new session.
  If `<sdk>/*.sif` and `<sdk>/cslc` already exist the script skips the download, and if a `singularity` command exists
  it skips the package install; it always rewrites `env.sh` and runs the smoke test.
- Never commit the SDK files to the repo; they are licensed (see `cerebras-software-eula.pdf`) and huge.
