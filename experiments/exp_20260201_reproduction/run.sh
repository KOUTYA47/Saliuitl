#!/bin/bash
# Saliuitl 論文再現実験
# 実行日: 2026-02-01

set -e
EXP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$(dirname "$0")/../.."

echo "=== Saliuitl Paper Reproduction ===" | tee "$EXP_DIR/logs/stdout.txt"
echo "Start: $(date)" | tee -a "$EXP_DIR/logs/stdout.txt"

# 共通パラメータ
ENSEMBLE_STEP=5
INPAINTING_STEP=5
INPAINT=biharmonic
THRESHOLD=0.5

# ============================================================
# VOC (Object Detection)
# ============================================================
echo "=== VOC Dataset ===" | tee -a "$EXP_DIR/logs/stdout.txt"

# VOC 1-patch
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
  2>&1 | tee -a "$EXP_DIR/logs/stdout.txt"

# VOC 2-patch
docker compose run --rm saliuitl python saliuitl.py \
  --dataset voc \
  --imgdir data/voc/clean \
  --patch_imgdir data/voc/2p \
  --n_patches 2 \
  --ensemble_step $ENSEMBLE_STEP \
  --inpainting_step $INPAINTING_STEP \
  --inpaint $INPAINT \
  --det_net 2dcnn_raw \
  --det_net_path checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth \
  --nn_det_threshold $THRESHOLD \
  --effective_files effective_2p.npy \
  2>&1 | tee -a "$EXP_DIR/logs/stdout.txt"

# VOC triangular
docker compose run --rm saliuitl python saliuitl.py \
  --dataset voc \
  --imgdir data/voc/clean \
  --patch_imgdir data/voc/trig \
  --n_patches 1 \
  --ensemble_step $ENSEMBLE_STEP \
  --inpainting_step $INPAINTING_STEP \
  --inpaint $INPAINT \
  --det_net 2dcnn_raw \
  --det_net_path checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth \
  --nn_det_threshold $THRESHOLD \
  --effective_files effective_trig.npy \
  2>&1 | tee -a "$EXP_DIR/logs/stdout.txt"

# VOC multi-object
docker compose run --rm saliuitl python saliuitl.py \
  --dataset voc \
  --imgdir data/voc/clean \
  --patch_imgdir data/voc/mo \
  --n_patches 1 \
  --ensemble_step $ENSEMBLE_STEP \
  --inpainting_step $INPAINTING_STEP \
  --inpaint $INPAINT \
  --det_net 2dcnn_raw \
  --det_net_path checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth \
  --nn_det_threshold $THRESHOLD \
  --effective_files effective_mo.npy \
  2>&1 | tee -a "$EXP_DIR/logs/stdout.txt"

# ============================================================
# INRIA (Object Detection)
# ============================================================
echo "=== INRIA Dataset ===" | tee -a "$EXP_DIR/logs/stdout.txt"

# INRIA 1-patch
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
  2>&1 | tee -a "$EXP_DIR/logs/stdout.txt"

# INRIA 2-patch
docker compose run --rm saliuitl python saliuitl.py \
  --dataset inria \
  --imgdir data/inria/clean \
  --patch_imgdir data/inria/2p \
  --n_patches 2 \
  --ensemble_step $ENSEMBLE_STEP \
  --inpainting_step $INPAINTING_STEP \
  --inpaint $INPAINT \
  --det_net 2dcnn_raw \
  --det_net_path checkpoints/final_detection/2dcnn_raw_inria_5_atk_det.pth \
  --nn_det_threshold $THRESHOLD \
  --effective_files effective_2p.npy \
  2>&1 | tee -a "$EXP_DIR/logs/stdout.txt"

# INRIA triangular
docker compose run --rm saliuitl python saliuitl.py \
  --dataset inria \
  --imgdir data/inria/clean \
  --patch_imgdir data/inria/trig \
  --n_patches 1 \
  --ensemble_step $ENSEMBLE_STEP \
  --inpainting_step $INPAINTING_STEP \
  --inpaint $INPAINT \
  --det_net 2dcnn_raw \
  --det_net_path checkpoints/final_detection/2dcnn_raw_inria_5_atk_det.pth \
  --nn_det_threshold $THRESHOLD \
  --effective_files effective_trig.npy \
  2>&1 | tee -a "$EXP_DIR/logs/stdout.txt"

echo "=== Completed: $(date) ===" | tee -a "$EXP_DIR/logs/stdout.txt"
