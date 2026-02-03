#!/bin/bash

# Visual Recovery Improvement Experiments
# 2026-02-02

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_ROOT"

echo "========================================"
echo "Visual Recovery Improvement Experiments"
echo "========================================"
echo "Project root: $PROJECT_ROOT"
echo ""

# VOC data paths
VOC_CLEAN="data/voc/clean"
VOC_ATTACKED="data/voc/1p"

# INRIA data paths
INRIA_CLEAN="data/inria/clean"
INRIA_ATTACKED="data/inria/1p"

# Output directory
OUTPUT_DIR="experiments/exp_20260202_visual_recovery"

# ========================================
# Experiment 1: Oracle Inpainting Test
# ========================================
echo "[1/3] Oracle Inpainting Test (VOC)"
echo "=================================="

python analysis/oracle_inpaint_test.py \
    --clean_dir "$VOC_CLEAN" \
    --attacked_dir "$VOC_ATTACKED" \
    --output_dir "$OUTPUT_DIR/oracle_test/voc" \
    --diff_threshold 30 \
    --num_images 10

echo ""
echo "[1/3] Oracle Inpainting Test (INRIA)"
echo "===================================="

python analysis/oracle_inpaint_test.py \
    --clean_dir "$INRIA_CLEAN" \
    --attacked_dir "$INRIA_ATTACKED" \
    --output_dir "$OUTPUT_DIR/oracle_test/inria" \
    --diff_threshold 30 \
    --num_images 10

# ========================================
# Experiment 2: Grad-CAM Visualization
# ========================================
echo ""
echo "[2/3] Grad-CAM Visualization (VOC)"
echo "=================================="

python analysis/gradcam_visualize.py \
    --clean_dir "$VOC_CLEAN" \
    --attacked_dir "$VOC_ATTACKED" \
    --output_dir "$OUTPUT_DIR/gradcam/voc" \
    --target_layer 13 \
    --num_images 5

# ========================================
# Experiment 3: Dilation Parameter Sweep
# ========================================
echo ""
echo "[3/3] Dilation Parameter Sweep"
echo "=============================="
echo "TODO: Implement dilation sweep experiment"

# ========================================
# Summary
# ========================================
echo ""
echo "========================================"
echo "Experiments Complete"
echo "========================================"
echo "Results saved to: $OUTPUT_DIR"
echo ""
echo "Generated files:"
find "$OUTPUT_DIR" -type f -name "*.png" | head -20
