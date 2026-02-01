#!/bin/bash
# 復元画像可視化実験
# 実行日: 2026-02-02

set -e
EXP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$(dirname "$0")/../.."

echo "=== Recovery Visualization Experiment ===" | tee "$EXP_DIR/logs/stdout.txt"
echo "Start: $(date)" | tee -a "$EXP_DIR/logs/stdout.txt"
echo "" | tee -a "$EXP_DIR/logs/stdout.txt"

# 共通パラメータ
ENSEMBLE_STEP=5
INPAINTING_STEP=5
INPAINT=biharmonic
THRESHOLD=0.5
SAVE_LIMIT=10

# ============================================================
# VOC 1-patch
# ============================================================
echo "=== VOC 1-patch ===" | tee -a "$EXP_DIR/logs/stdout.txt"

docker compose run --rm saliuitl python saliuitl.py \
  --dataset voc \
  --imgdir data/voc/clean \
  --patch_imgdir data/voc/1p \
  --n_patches 1 \
  --ensemble_step $ENSEMBLE_STEP \
  --inpainting_step $INPAINTING_STEP \
  --inpaint $INPAINT \
  --det_net 2dcnn_raw \
  --det_net_path checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth \
  --nn_det_threshold $THRESHOLD \
  --effective_files effective_1p.npy \
  --save_images \
  --save_images_dir "$EXP_DIR/figures" \
  --save_images_limit $SAVE_LIMIT \
  2>&1 | tee -a "$EXP_DIR/logs/stdout.txt"

echo "" | tee -a "$EXP_DIR/logs/stdout.txt"

# ============================================================
# INRIA 1-patch
# ============================================================
echo "=== INRIA 1-patch ===" | tee -a "$EXP_DIR/logs/stdout.txt"

docker compose run --rm saliuitl python saliuitl.py \
  --dataset inria \
  --imgdir data/inria/clean \
  --patch_imgdir data/inria/1p \
  --n_patches 1 \
  --ensemble_step $ENSEMBLE_STEP \
  --inpainting_step $INPAINTING_STEP \
  --inpaint $INPAINT \
  --det_net 2dcnn_raw \
  --det_net_path checkpoints/final_detection/2dcnn_raw_inria_5_atk_det.pth \
  --nn_det_threshold $THRESHOLD \
  --effective_files effective_1p.npy \
  --save_images \
  --save_images_dir "$EXP_DIR/figures" \
  --save_images_limit $SAVE_LIMIT \
  2>&1 | tee -a "$EXP_DIR/logs/stdout.txt"

echo "" | tee -a "$EXP_DIR/logs/stdout.txt"
echo "=== Completed: $(date) ===" | tee -a "$EXP_DIR/logs/stdout.txt"
