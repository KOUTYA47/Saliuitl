#!/bin/bash
# Oracle Inpainting Test - All Datasets
# 2026-02-05
# 目的: 全データセットでOracle Testを実施し、biharmonic再現実験との差分を比較

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "========================================"
echo "Oracle Inpainting Test - All Datasets"
echo "========================================"
echo "Date: $(date)"
echo ""

LOG_DIR="$SCRIPT_DIR/logs"
RESULTS_DIR="$SCRIPT_DIR/results"
mkdir -p "$LOG_DIR" "$RESULTS_DIR"

# Common parameters
ENSEMBLE_STEP=5
INPAINTING_STEP=5

# ========================================
# Object Detection: VOC
# ========================================
echo "[1/8] VOC 1-patch (Oracle)"
docker compose run --rm saliuitl python saliuitl.py \
  --inpaint oracle \
  --imgdir data/voc/clean \
  --patch_imgdir data/voc/1p \
  --dataset voc \
  --det_net_path checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step $ENSEMBLE_STEP \
  --inpainting_step $INPAINTING_STEP \
  --effective_files data/voc/1p/effective_1p.npy \
  --n_patches 1 2>&1 | tee "$LOG_DIR/voc_1p_oracle.log"

echo "[2/8] VOC 2-patch (Oracle)"
docker compose run --rm saliuitl python saliuitl.py \
  --inpaint oracle \
  --imgdir data/voc/clean \
  --patch_imgdir data/voc/2p \
  --dataset voc \
  --det_net_path checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step $ENSEMBLE_STEP \
  --inpainting_step $INPAINTING_STEP \
  --effective_files data/voc/2p/effective_2p.npy \
  --n_patches 2 2>&1 | tee "$LOG_DIR/voc_2p_oracle.log"

echo "[3/8] VOC trig (Oracle)"
docker compose run --rm saliuitl python saliuitl.py \
  --inpaint oracle \
  --imgdir data/voc/clean \
  --patch_imgdir data/voc/trig \
  --dataset voc \
  --det_net_path checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step $ENSEMBLE_STEP \
  --inpainting_step $INPAINTING_STEP \
  --effective_files data/voc/trig/effective_1p.npy \
  --n_patches 1 2>&1 | tee "$LOG_DIR/voc_trig_oracle.log"

# ========================================
# Object Detection: INRIA
# ========================================
echo "[4/8] INRIA 1-patch (Oracle)"
docker compose run --rm saliuitl python saliuitl.py \
  --inpaint oracle \
  --imgdir data/inria/clean \
  --patch_imgdir data/inria/1p \
  --dataset inria \
  --det_net_path checkpoints/final_detection/2dcnn_raw_inria_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step $ENSEMBLE_STEP \
  --inpainting_step $INPAINTING_STEP \
  --effective_files data/inria/1p/effective_1p.npy \
  --n_patches 1 2>&1 | tee "$LOG_DIR/inria_1p_oracle.log"

echo "[5/8] INRIA 2-patch (Oracle)"
docker compose run --rm saliuitl python saliuitl.py \
  --inpaint oracle \
  --imgdir data/inria/clean \
  --patch_imgdir data/inria/2p \
  --dataset inria \
  --det_net_path checkpoints/final_detection/2dcnn_raw_inria_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step $ENSEMBLE_STEP \
  --inpainting_step $INPAINTING_STEP \
  --effective_files data/inria/2p/effective_2p.npy \
  --n_patches 2 2>&1 | tee "$LOG_DIR/inria_2p_oracle.log"

echo "[6/8] INRIA trig (Oracle)"
docker compose run --rm saliuitl python saliuitl.py \
  --inpaint oracle \
  --imgdir data/inria/clean \
  --patch_imgdir data/inria/trig \
  --dataset inria \
  --det_net_path checkpoints/final_detection/2dcnn_raw_inria_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step $ENSEMBLE_STEP \
  --inpainting_step $INPAINTING_STEP \
  --effective_files data/inria/trig/effective_1p.npy \
  --n_patches 1 2>&1 | tee "$LOG_DIR/inria_trig_oracle.log"

# ========================================
# Image Classification: CIFAR-10
# ========================================
echo "[7/8] CIFAR 1-patch (Oracle)"
docker compose run --rm saliuitl python saliuitl.py \
  --inpaint oracle \
  --imgdir data/cifar/clean \
  --patch_imgdir data/cifar/1p \
  --dataset cifar \
  --det_net_path checkpoints/final_classification/2dcnn_raw_cifar_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step $ENSEMBLE_STEP \
  --inpainting_step $INPAINTING_STEP \
  --effective_files data/cifar/1p/effective_1p.npy \
  --n_patches 1 2>&1 | tee "$LOG_DIR/cifar_1p_oracle.log"

# ========================================
# Image Classification: ImageNet
# ========================================
echo "[8/8] ImageNet 1-patch (Oracle)"
docker compose run --rm saliuitl python saliuitl.py \
  --inpaint oracle \
  --imgdir data/imagenet/clean \
  --patch_imgdir data/imagenet/1p \
  --dataset imagenet \
  --det_net_path checkpoints/final_classification/2dcnn_raw_imagenet_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step $ENSEMBLE_STEP \
  --inpainting_step $INPAINTING_STEP \
  --effective_files data/imagenet/1p/effective_1p.npy \
  --n_patches 1 2>&1 | tee "$LOG_DIR/imagenet_1p_oracle.log"

echo ""
echo "========================================"
echo "Oracle Test Complete"
echo "========================================"
echo "Logs saved to: $LOG_DIR"
