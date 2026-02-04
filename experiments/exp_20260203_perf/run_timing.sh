#!/bin/bash
# 時間計測実験スクリプト
# TASK-20260203-PERF: 証明可能防御と提案手法の計算時間比較

set -e

COMPOSE_FILE="/mnt/d/csprog/ooki/Saliuitl/docker-compose.yml"
OUTPUT_DIR="/mnt/d/csprog/ooki/Saliuitl/experiments/exp_20260203_perf/results"
mkdir -p "$OUTPUT_DIR"

echo "=== 時間計測実験 $(date) ===" | tee "$OUTPUT_DIR/timing_log.txt"

# VOC 1-patch
echo "--- VOC 1-patch ---" | tee -a "$OUTPUT_DIR/timing_log.txt"
for STEP in 25 10 5 2; do
    echo "ensemble_step=$STEP (|B|=$((100/STEP)))" | tee -a "$OUTPUT_DIR/timing_log.txt"
    docker compose -f "$COMPOSE_FILE" run --rm saliuitl python saliuitl.py \
        --dataset voc \
        --imgdir data/voc/clean \
        --patch_imgdir data/voc/1p \
        --det_net_path checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth \
        --det_net 2dcnn_raw \
        --effective_files effective_1p.npy \
        --ensemble_step $STEP \
        --inpainting_step $STEP \
        --inpaint biharmonic \
        --n_patches 1 \
        --performance 2>&1 | tee -a "$OUTPUT_DIR/voc_1p_step${STEP}.log"
    echo "" | tee -a "$OUTPUT_DIR/timing_log.txt"
done

# INRIA 1-patch
echo "--- INRIA 1-patch ---" | tee -a "$OUTPUT_DIR/timing_log.txt"
for STEP in 25 10 5; do
    echo "ensemble_step=$STEP (|B|=$((100/STEP)))" | tee -a "$OUTPUT_DIR/timing_log.txt"
    docker compose -f "$COMPOSE_FILE" run --rm saliuitl python saliuitl.py \
        --dataset inria \
        --imgdir data/inria/clean \
        --patch_imgdir data/inria/1p \
        --det_net_path checkpoints/final_detection/2dcnn_raw_inria_5_atk_det.pth \
        --det_net 2dcnn_raw \
        --effective_files effective_1p.npy \
        --ensemble_step $STEP \
        --inpainting_step $STEP \
        --inpaint biharmonic \
        --n_patches 1 \
        --performance 2>&1 | tee -a "$OUTPUT_DIR/inria_1p_step${STEP}.log"
    echo "" | tee -a "$OUTPUT_DIR/timing_log.txt"
done

echo "=== 完了 $(date) ===" | tee -a "$OUTPUT_DIR/timing_log.txt"
