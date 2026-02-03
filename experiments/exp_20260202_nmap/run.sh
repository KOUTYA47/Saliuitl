#!/bin/bash
# nmAP計算実験スクリプト
# 実行方法: ./experiments/exp_20260202_nmap/run.sh

set -e

EXP_DIR="experiments/exp_20260202_nmap"
mkdir -p ${EXP_DIR}/logs ${EXP_DIR}/outcomes

echo "========================================"
echo "nmAP Calculation Experiment"
echo "Date: $(date)"
echo "========================================"

# ===============================================
# VOC Dataset
# ===============================================

echo ""
echo "[1/4] VOC 1-patch: Attacked images with recovery"
docker compose run --rm saliuitl python saliuitl.py \
  --inpaint biharmonic \
  --imgdir data/voc/clean \
  --patch_imgdir data/voc/1p \
  --dataset voc \
  --det_net_path checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step 5 \
  --inpainting_step 5 \
  --effective_files data/voc/1p/effective_1p.npy \
  --n_patches 1 \
  --save_outcomes \
  --savedir ${EXP_DIR}/outcomes/voc_1p_attacked 2>&1 | tee ${EXP_DIR}/logs/voc_1p_attacked.log

echo ""
echo "[2/4] VOC 1-patch: Clean images (baseline)"
docker compose run --rm saliuitl python saliuitl.py \
  --inpaint biharmonic \
  --imgdir data/voc/clean \
  --patch_imgdir data/voc/clean \
  --dataset voc \
  --det_net_path checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step 5 \
  --inpainting_step 5 \
  --n_patches 1 \
  --clean \
  --save_outcomes \
  --savedir ${EXP_DIR}/outcomes/voc_1p_clean 2>&1 | tee ${EXP_DIR}/logs/voc_1p_clean.log

# ===============================================
# INRIA Dataset
# ===============================================

echo ""
echo "[3/4] INRIA 1-patch: Attacked images with recovery"
docker compose run --rm saliuitl python saliuitl.py \
  --inpaint biharmonic \
  --imgdir data/inria/clean \
  --patch_imgdir data/inria/1p \
  --dataset inria \
  --det_net_path checkpoints/final_detection/2dcnn_raw_inria_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step 5 \
  --inpainting_step 5 \
  --effective_files data/inria/1p/effective_1p.npy \
  --n_patches 1 \
  --save_outcomes \
  --savedir ${EXP_DIR}/outcomes/inria_1p_attacked 2>&1 | tee ${EXP_DIR}/logs/inria_1p_attacked.log

echo ""
echo "[4/4] INRIA 1-patch: Clean images (baseline)"
docker compose run --rm saliuitl python saliuitl.py \
  --inpaint biharmonic \
  --imgdir data/inria/clean \
  --patch_imgdir data/inria/clean \
  --dataset inria \
  --det_net_path checkpoints/final_detection/2dcnn_raw_inria_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step 5 \
  --inpainting_step 5 \
  --n_patches 1 \
  --clean \
  --save_outcomes \
  --savedir ${EXP_DIR}/outcomes/inria_1p_clean 2>&1 | tee ${EXP_DIR}/logs/inria_1p_clean.log

echo ""
echo "========================================"
echo "Computing nmAP"
echo "========================================"

# nmAP計算
echo ""
echo "[VOC 1-patch nmAP]"
docker compose run --rm saliuitl python compute_nmap.py \
  --attacked_outcomes ${EXP_DIR}/outcomes/voc_1p_attacked_voc_2dcnn_raw_npatches_1_inp_5_scores.npy \
  --clean_outcomes ${EXP_DIR}/outcomes/voc_1p_clean_voc_2dcnn_raw_npatches_1_inp_5_scores_clean.npy \
  --iou_threshold 0.5

echo ""
echo "[INRIA 1-patch nmAP]"
docker compose run --rm saliuitl python compute_nmap.py \
  --attacked_outcomes ${EXP_DIR}/outcomes/inria_1p_attacked_inria_2dcnn_raw_npatches_1_inp_5_scores.npy \
  --clean_outcomes ${EXP_DIR}/outcomes/inria_1p_clean_inria_2dcnn_raw_npatches_1_inp_5_scores_clean.npy \
  --iou_threshold 0.5

echo ""
echo "========================================"
echo "Experiment completed: $(date)"
echo "========================================"
