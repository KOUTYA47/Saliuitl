#!/bin/bash
# Oracle Test - All Patterns (15 scenarios)
# 2026-02-05

set -e

WORKSPACE="/mnt/d/csprog/ooki/Saliuitl"
LOGDIR="${WORKSPACE}/experiments/exp_20260205_oracle_full/logs"
mkdir -p "$LOGDIR"

run_oracle() {
    local dataset=$1
    local attack=$2
    local imgdir=$3
    local patchdir=$4
    local checkpoint=$5
    local effective=$6
    local n_patches=$7
    local logfile="${LOGDIR}/${dataset}_${attack}_oracle.log"

    echo "Running: ${dataset} ${attack}..."
    docker run --rm --gpus all --network host \
        -v ${WORKSPACE}:/workspace -w /workspace \
        saliuitl:latest python saliuitl.py \
        --inpaint oracle \
        --imgdir "$imgdir" \
        --patch_imgdir "$patchdir" \
        --dataset "$dataset" \
        --det_net_path "$checkpoint" \
        --det_net 2dcnn_raw \
        --ensemble_step 5 \
        --inpainting_step 5 \
        --effective_files "$effective" \
        --n_patches "$n_patches" 2>&1 | tee "$logfile"

    echo "Done: ${dataset} ${attack}"
    echo ""
}

echo "========================================"
echo "Oracle Test - All 15 Patterns"
echo "========================================"
echo ""

# INRIA (3 patterns - no mo data)
run_oracle inria 1p data/inria/clean data/inria/1p \
    checkpoints/final_detection/2dcnn_raw_inria_5_atk_det.pth effective_1p.npy 1

run_oracle inria 2p data/inria/clean data/inria/2p \
    checkpoints/final_detection/2dcnn_raw_inria_5_atk_det.pth effective_2p.npy 2

run_oracle inria trig data/inria/clean data/inria/trig \
    checkpoints/final_detection/2dcnn_raw_inria_5_atk_det.pth effective_1p.npy 1

# VOC (4 patterns)
run_oracle voc 1p data/voc/clean data/voc/1p \
    checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth effective_1p.npy 1

run_oracle voc 2p data/voc/clean data/voc/2p \
    checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth effective_2p.npy 2

run_oracle voc trig data/voc/clean data/voc/trig \
    checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth effective_1p.npy 1

run_oracle voc mo data/voc/clean data/voc/mo \
    checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth effective_mop.npy 1

# CIFAR (4 patterns)
run_oracle cifar 1p data/cifar/clean data/cifar/1p \
    checkpoints/final_classification/2dcnn_raw_cifar_5_atk_det.pth effective_1p.npy 1

run_oracle cifar 2p data/cifar/clean data/cifar/2p \
    checkpoints/final_classification/2dcnn_raw_cifar_5_atk_det.pth effective_2p.npy 2

run_oracle cifar 4p data/cifar/clean data/cifar/4p \
    checkpoints/final_classification/2dcnn_raw_cifar_5_atk_det.pth effective_4p.npy 4

run_oracle cifar trig data/cifar/clean data/cifar/trig \
    checkpoints/final_classification/2dcnn_raw_cifar_5_atk_det.pth effective_1p.npy 1

# ImageNet (4 patterns)
run_oracle imagenet 1p data/imagenet/clean data/imagenet/1p \
    checkpoints/final_classification/2dcnn_raw_imagenet_5_atk_det.pth effective_1p.npy 1

run_oracle imagenet 2p data/imagenet/clean data/imagenet/2p \
    checkpoints/final_classification/2dcnn_raw_imagenet_5_atk_det.pth effective_2p.npy 2

run_oracle imagenet 4p data/imagenet/clean data/imagenet/4p \
    checkpoints/final_classification/2dcnn_raw_imagenet_5_atk_det.pth effective_4p.npy 4

run_oracle imagenet trig data/imagenet/clean data/imagenet/trig \
    checkpoints/final_classification/2dcnn_raw_imagenet_5_atk_det.pth effective_1p.npy 1

echo "========================================"
echo "All 15 Oracle Tests Complete"
echo "========================================"
