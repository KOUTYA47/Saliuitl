#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 exp_YYYYMMDD_slug"
  exit 1
fi

EXP_ID="$1"
EXP_DIR="experiments/${EXP_ID}"

mkdir -p "${EXP_DIR}/"{logs,results,artifacts}

if [ ! -f "${EXP_DIR}/config.yaml" ]; then
cat > "${EXP_DIR}/config.yaml" <<'YAML'
experiment:
  id: REPLACE_ME
  purpose: "Describe purpose"

environment:
  seed: 42
  git_commit: "REPLACE_ME"

dataset:
  name: inria
  imgdir: "data/inria/clean"
  patch_imgdir: "data/inria/2p"
  n_patches: "2"

method:
  ensemble_step: 2
  inpainting_step: 5
  det_net: "2dcnn_raw"
  det_net_path: "checkpoints/final_detection/2dcnn_raw_inria_2_atk_det.pth"
  nn_det_threshold: 0.5

run:
  extra_args: ""
YAML
fi

if [ ! -f "${EXP_DIR}/run.sh" ]; then
cat > "${EXP_DIR}/run.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

EXP_DIR="$(cd "$(dirname "$0")" && pwd)"

# TODO: edit args or generate from config.yaml
python saliuitl.py   --dataset inria   --imgdir data/inria/clean   --patch_imgdir data/inria/2p   --n_patches 2   --ensemble_step 2   --inpainting_step 5   --det_net 2dcnn_raw   --det_net_path checkpoints/final_detection/2dcnn_raw_inria_2_atk_det.pth   --nn_det_threshold 0.5   --performance_det --performance   --savedir "$EXP_DIR/results/"   2> "$EXP_DIR/logs/stderr.txt" | tee "$EXP_DIR/logs/stdout.txt"
SH
chmod +x "${EXP_DIR}/run.sh"
fi

echo "[new_experiment] created: ${EXP_DIR}"
echo "Next: edit ${EXP_DIR}/config.yaml and ${EXP_DIR}/run.sh"
