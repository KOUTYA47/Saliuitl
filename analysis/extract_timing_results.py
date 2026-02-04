#!/usr/bin/env python3
"""
時間計測結果を抽出・集計するスクリプト
"""

import numpy as np
import os
import glob

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'experiments', 'exp_20260203_perf', 'results')
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def extract_timing():
    """npyファイルから時間データを抽出"""
    results = []

    # パターンで検索
    perf_files = glob.glob(os.path.join(RESULTS_DIR, '*_perfs.npy'))

    for f in perf_files:
        filename = os.path.basename(f)
        # ファイル名から情報を抽出
        # 例: voc_step5_voc_2dcnn_raw_npatches_1_inp_5_perfs.npy
        parts = filename.split('_')

        # データセットとステップを抽出
        if 'voc' in filename:
            dataset = 'VOC'
        elif 'inria' in filename:
            dataset = 'INRIA'
        elif 'cifar' in filename:
            dataset = 'CIFAR'
        elif 'imagenet' in filename:
            dataset = 'ImageNet'
        else:
            dataset = 'Unknown'

        # inpainting_step を抽出
        for i, p in enumerate(parts):
            if p == 'inp':
                step = int(parts[i+1])
                break
        else:
            step = 0

        ensemble_size = 100 // step if step > 0 else 0

        # npyファイルを読み込み
        try:
            data = np.load(f)
            mean_time = np.mean(data)
            std_time = np.std(data)
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            n_samples = len(data)

            results.append({
                'dataset': dataset,
                'ensemble_step': step,
                'ensemble_size': ensemble_size,
                'mean': mean_time,
                'std': std_time,
                'q1': q1,
                'q3': q3,
                'n_samples': n_samples,
                'file': filename
            })

            print(f"{dataset} step={step} (|B|={ensemble_size}): mean={mean_time:.4f}s, std={std_time:.4f}s, n={n_samples}")
        except Exception as e:
            print(f"Error loading {f}: {e}")

    return results

def save_results(results):
    """結果をCSVに保存"""
    import csv

    output_file = os.path.join(OUTPUT_DIR, 'tables', 'measured_computational_cost.csv')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['dataset', 'ensemble_step', 'ensemble_size',
                                               'mean', 'std', 'q1', 'q3', 'n_samples'])
        writer.writeheader()
        for r in sorted(results, key=lambda x: (x['dataset'], x['ensemble_step'])):
            writer.writerow({
                'dataset': r['dataset'],
                'ensemble_step': r['ensemble_step'],
                'ensemble_size': r['ensemble_size'],
                'mean': f"{r['mean']:.4f}",
                'std': f"{r['std']:.4f}",
                'q1': f"{r['q1']:.4f}",
                'q3': f"{r['q3']:.4f}",
                'n_samples': r['n_samples']
            })

    print(f"\nSaved: {output_file}")

def print_summary(results):
    """サマリーを表示"""
    print("\n=== 時間計測結果サマリー ===\n")
    print(f"{'Dataset':<10} {'Step':<6} {'|B|':<4} {'Mean(s)':<10} {'Std(s)':<10} {'Q1(s)':<10} {'Q3(s)':<10}")
    print("-" * 70)

    for r in sorted(results, key=lambda x: (x['dataset'], x['ensemble_step'])):
        print(f"{r['dataset']:<10} {r['ensemble_step']:<6} {r['ensemble_size']:<4} "
              f"{r['mean']:<10.4f} {r['std']:<10.4f} {r['q1']:<10.4f} {r['q3']:<10.4f}")

if __name__ == '__main__':
    print(f"Results directory: {RESULTS_DIR}")
    print()

    results = extract_timing()

    if results:
        save_results(results)
        print_summary(results)
    else:
        print("No results found.")
