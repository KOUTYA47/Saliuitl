# MIGRATION.md
*Directory structure optimization + migration steps for a Saliuitl-style repo (saliuitl.py at repo root)*

This guide optimizes **structure management** for research (reproducible experiments + multi-agent workflow)
**without breaking** the existing `saliuitl.py` assumptions.

`Saliuitl`-style code commonly assumes paths relative to the **repo root**, e.g.
- `./checkpoints`
- `cfg/yolo.cfg`
- `weights/yolo.weights`

So in this plan we **keep those legacy paths at the repo root**, and introduce a clean, reproducible
experiment/analysis layer around them.

---

## 1) Target directory layout (keep legacy, add research scaffolding)

```text
repo/
├─ saliuitl.py                 # keep (legacy entrypoint)
├─ nets/                       # keep (legacy imports)
├─ helper.py / darknet.py      # keep
├─ cfg/                        # keep (default args expect this)
├─ weights/                    # keep
├─ checkpoints/                # keep
├─ data/                       # keep (your current data placement)
│
├─ .claude/
│  └─ agents/
│     ├─ lead.md
│     ├─ experiment-runner.md
│     └─ result-analyst.md
│
├─ CONVENTIONS.md
├─ TASKS.md
│
├─ experiments/                # NEW: “truth” of all runs
│  └─ exp_YYYYMMDD_slug/
│     ├─ config.yaml           # conditions (SSOT)
│     ├─ run.sh                # exact command
│     ├─ logs/
│     │  ├─ stdout.txt
│     │  └─ stderr.txt
│     ├─ artifacts/            # optional (patch masks, etc.)
│     └─ results/              # machine-readable outputs (csv/json/npy)
│
├─ analysis/                   # NEW: cross-experiment aggregation
│  ├─ scripts/
│  ├─ tables/
│  ├─ figures/
│  └─ reports/
│
└─ scripts/                    # NEW: helpers (create/run/validate)
   ├─ env_check.sh
   └─ new_experiment.sh
```

### Why “keep legacy at root”?
Because `saliuitl.py` uses relative paths in defaults and runtime assertions like:
- `assert os.path.isdir('./checkpoints')`

Moving those directories breaks runs unless you refactor code.
This migration avoids that disruption and still gives you reproducible structure.

---

## 2) Migration steps (safe, minimal disruption)

### Step A — Add new scaffolding (no moves)
From repo root:

```bash
mkdir -p .claude/agents docs/notes docs/decisions \
  experiments analysis/scripts analysis/tables analysis/figures analysis/reports \
  scripts
```

Copy in the files we already prepared:
- `CONVENTIONS.md`
- `TASKS.md`
- `.claude/agents/*.md`

### Step B — Standardize experiment creation
Each experiment gets its own directory:

```bash
mkdir -p experiments/exp_20260201_inria_2p/{logs,results,artifacts}
```

Inside that directory you always have:
- `config.yaml` (conditions)
- `run.sh` (single source of truth for the command)

### Step C — Run from experiment dir but **cd to repo root**
Because `saliuitl.py` expects relative paths from repo root, your `run.sh` should do:

```bash
#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

EXP_DIR="$(cd "$(dirname "$0")" && pwd)"

python saliuitl.py \
  --dataset inria \
  --imgdir data/inria/clean \
  --patch_imgdir data/inria/2p \
  --n_patches 2 \
  --ensemble_step 2 \
  --inpainting_step 5 \
  --det_net_path checkpoints/final_detection/2dcnn_raw_inria_2_atk_det.pth \
  --det_net 2dcnn_raw \
  --performance_det --performance \
  --savedir "$EXP_DIR/results/" \
  2> "$EXP_DIR/logs/stderr.txt" | tee "$EXP_DIR/logs/stdout.txt"
```

This keeps legacy relative paths working and still stores outputs under the experiment folder.

---

## 3) What to commit vs ignore (research-friendly)

### Commit (recommended)
- `CONVENTIONS.md`, `TASKS.md`
- `.claude/agents/`
- `experiments/**/config.yaml`, `experiments/**/run.sh`
- `analysis/scripts/` (parsers, table generators)
- `analysis/tables/` (small CSVs)

### Ignore (recommended)
- raw datasets
- heavyweight checkpoints
- large logs/artifacts/results (optionally keep results if small)

See `.gitignore.research` template in this bundle.

---

## 4) Optional: “clean refactor” later (when ready)
If you later want to move legacy code into `src/` and make it a package, do it as a separate phase:
- add `src/saliuitl/` and turn `nets/` into a module
- convert imports to package-relative
- remove hard-coded `./checkpoints` assumptions (make them args with defaults)

This is a bigger change; don’t mix it with paper deadlines.

---

## 5) Quick validation checklist
- [ ] From repo root, `python saliuitl.py --help` works
- [ ] `./checkpoints` exists where `saliuitl.py` expects it
- [ ] Every experiment has `config.yaml` + `run.sh`
- [ ] `run.sh` stores logs/results under its own experiment directory
- [ ] analysis scripts never read from `data/raw` directly (only `experiments/**/results`)
