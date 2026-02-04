#!/usr/bin/env python3
"""
Oracle Test結果抽出・比較スクリプト

Oracle TestのログからRRを抽出し、biharmonic再現実験と比較する。
"""

import os
import re
import sys
from pathlib import Path

# 再現実験結果（RESULT_LOG.mdより）
BIHARMONIC_RESULTS = {
    # Dataset, Attack: (RR, Detected)
    ('CIFAR', '1p'): (0.9286, 0.9286),
    ('CIFAR', '2p'): (0.8000, 0.8667),
    ('CIFAR', '4p'): (0.9333, 1.0),
    ('CIFAR', 'trig'): (0.8667, 1.0),
    ('ImageNet', '1p'): (0.8667, 1.0),
    ('ImageNet', '2p'): (0.6667, 0.8667),
    ('ImageNet', '4p'): (0.4667, 0.9333),
    ('ImageNet', 'trig'): (0.4000, 0.6667),
    ('INRIA', '1p'): (0.7917, 0.9583),
    ('INRIA', '2p'): (0.8571, 1.0),
    ('INRIA', 'trig'): (0.3636, 0.5455),
    ('VOC', '1p'): (0.5385, 1.0),
    ('VOC', '2p'): (0.5263, 1.0),
    ('VOC', 'trig'): (0.1500, 0.8),
    ('VOC', 'mo'): (0.2593, 1.0),
}

# 論文値（Table 1）
PAPER_RESULTS = {
    ('CIFAR', '1p'): 0.9738,
    ('CIFAR', '2p'): 0.9789,
    ('CIFAR', '4p'): 0.9747,
    ('CIFAR', 'trig'): 0.8566,
    ('ImageNet', '1p'): 0.8869,
    ('ImageNet', '2p'): 0.8535,
    ('ImageNet', '4p'): 0.8436,
    ('ImageNet', 'trig'): 0.5065,
    ('INRIA', '1p'): 0.5909,
    ('INRIA', '2p'): 0.3871,
    ('INRIA', 'trig'): 0.4737,
    ('VOC', '1p'): 0.5404,
    ('VOC', '2p'): 0.5376,
    ('VOC', 'trig'): 0.4244,
    ('VOC', 'mo'): 0.3955,
}


def parse_log_file(log_path):
    """ログファイルからRRとDetectedを抽出"""
    if not os.path.exists(log_path):
        return None, None

    with open(log_path, 'r') as f:
        content = f.read()

    # "Unsuccesful Attacks:X.XXXX" パターンを検索（RR）
    rr_match = re.search(r'Unsuccesful Attacks[:\s]*([\d.]+)', content)
    rr = float(rr_match.group(1)) if rr_match else None

    # "Detected Attacks:X.XXXX" パターンを検索
    det_match = re.search(r'Detected Attacks[:\s]*([\d.]+)', content)
    detected = float(det_match.group(1)) if det_match else None

    return rr, detected


def main():
    script_dir = Path(__file__).parent
    log_dir = script_dir / 'logs'
    results_dir = script_dir / 'results'
    results_dir.mkdir(exist_ok=True)

    # ログファイルマッピング
    log_files = {
        ('VOC', '1p'): 'voc_1p_oracle.log',
        ('VOC', '2p'): 'voc_2p_oracle.log',
        ('VOC', 'trig'): 'voc_trig_oracle.log',
        ('INRIA', '1p'): 'inria_1p_oracle.log',
        ('INRIA', '2p'): 'inria_2p_oracle.log',
        ('INRIA', 'trig'): 'inria_trig_oracle.log',
        ('CIFAR', '1p'): 'cifar_1p_oracle.log',
        ('ImageNet', '1p'): 'imagenet_1p_oracle.log',
    }

    # 結果抽出
    oracle_results = {}
    for key, log_name in log_files.items():
        log_path = log_dir / log_name
        rr, detected = parse_log_file(log_path)
        if rr is not None:
            oracle_results[key] = (rr, detected)

    # 結果表示・保存
    print("=" * 90)
    print("Oracle Test Results vs Biharmonic Reproduction")
    print("=" * 90)
    print(f"{'Dataset':<12} {'Attack':<8} {'Paper RR':>10} {'Biharmonic':>12} {'Oracle':>10} {'Δ(O-B)':>10} {'Δ(O-P)':>10}")
    print("-" * 90)

    results_lines = []
    results_lines.append("Dataset,Attack,Paper_RR,Biharmonic_RR,Oracle_RR,Diff_Oracle_Biharmonic,Diff_Oracle_Paper")

    # 物体検出
    for dataset in ['INRIA', 'VOC']:
        for attack in ['1p', '2p', 'trig', 'mo']:
            key = (dataset, attack)
            if key not in PAPER_RESULTS:
                continue

            paper_rr = PAPER_RESULTS.get(key, None)
            biharmonic_rr = BIHARMONIC_RESULTS.get(key, (None, None))[0]
            oracle_rr = oracle_results.get(key, (None, None))[0]

            diff_ob = (oracle_rr - biharmonic_rr) if (oracle_rr and biharmonic_rr) else None
            diff_op = (oracle_rr - paper_rr) if (oracle_rr and paper_rr) else None

            paper_str = f"{paper_rr:.4f}" if paper_rr else "-"
            bio_str = f"{biharmonic_rr:.4f}" if biharmonic_rr else "-"
            oracle_str = f"{oracle_rr:.4f}" if oracle_rr else "-"
            diff_ob_str = f"{diff_ob:+.4f}" if diff_ob is not None else "-"
            diff_op_str = f"{diff_op:+.4f}" if diff_op is not None else "-"

            print(f"{dataset:<12} {attack:<8} {paper_str:>10} {bio_str:>12} {oracle_str:>10} {diff_ob_str:>10} {diff_op_str:>10}")

            results_lines.append(f"{dataset},{attack},{paper_rr or ''},{biharmonic_rr or ''},{oracle_rr or ''},{diff_ob or ''},{diff_op or ''}")

    print("-" * 90)

    # 画像分類
    for dataset in ['CIFAR', 'ImageNet']:
        for attack in ['1p', '2p', '4p', 'trig']:
            key = (dataset, attack)
            if key not in PAPER_RESULTS:
                continue

            paper_rr = PAPER_RESULTS.get(key, None)
            biharmonic_rr = BIHARMONIC_RESULTS.get(key, (None, None))[0]
            oracle_rr = oracle_results.get(key, (None, None))[0]

            diff_ob = (oracle_rr - biharmonic_rr) if (oracle_rr and biharmonic_rr) else None
            diff_op = (oracle_rr - paper_rr) if (oracle_rr and paper_rr) else None

            paper_str = f"{paper_rr:.4f}" if paper_rr else "-"
            bio_str = f"{biharmonic_rr:.4f}" if biharmonic_rr else "-"
            oracle_str = f"{oracle_rr:.4f}" if oracle_rr else "-"
            diff_ob_str = f"{diff_ob:+.4f}" if diff_ob is not None else "-"
            diff_op_str = f"{diff_op:+.4f}" if diff_op is not None else "-"

            print(f"{dataset:<12} {attack:<8} {paper_str:>10} {bio_str:>12} {oracle_str:>10} {diff_ob_str:>10} {diff_op_str:>10}")

            results_lines.append(f"{dataset},{attack},{paper_rr or ''},{biharmonic_rr or ''},{oracle_rr or ''},{diff_ob or ''},{diff_op or ''}")

    print("=" * 90)

    # CSV保存
    csv_path = results_dir / 'oracle_comparison.csv'
    with open(csv_path, 'w') as f:
        f.write('\n'.join(results_lines))
    print(f"\nResults saved to: {csv_path}")

    # サマリー
    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)

    oracle_count = len(oracle_results)
    total_count = len(log_files)
    print(f"Completed: {oracle_count}/{total_count} experiments")

    if oracle_results:
        diffs = []
        for key, (oracle_rr, _) in oracle_results.items():
            bio_rr = BIHARMONIC_RESULTS.get(key, (None, None))[0]
            if oracle_rr and bio_rr:
                diffs.append(oracle_rr - bio_rr)

        if diffs:
            avg_diff = sum(diffs) / len(diffs)
            print(f"Average Δ(Oracle - Biharmonic): {avg_diff:+.4f}")
            print(f"Max improvement: {max(diffs):+.4f}")
            print(f"Min improvement: {min(diffs):+.4f}")


if __name__ == '__main__':
    main()
