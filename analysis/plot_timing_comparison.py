#!/usr/bin/env python3
"""
時間計測結果と論文値の比較グラフを作成
"""

import matplotlib.pyplot as plt
import numpy as np
import os

# 出力ディレクトリ
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'docs', 'slides_material')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# スタイル設定
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 9,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

# 実測データ
measured = {
    'VOC': {
        4: {'mean': 0.0678, 'std': 0.0116},
        10: {'mean': 0.1999, 'std': 0.0357},
        20: {'mean': 0.4552, 'std': 0.0706},
    },
    'INRIA': {
        4: {'mean': 0.0714, 'std': 0.0229},
        10: {'mean': 0.2021, 'std': 0.0385},
        20: {'mean': 0.4087, 'std': 0.0477},
    }
}

# 論文値（Figure 4(a)から読み取り）
paper = {
    'VOC': {
        4: 0.30,
        10: 0.75,
        20: 1.50,
    },
    'INRIA': {
        4: 0.30,
        10: 0.75,
        20: 1.50,
    }
}

def plot_comparison():
    """実測値と論文値の比較グラフ"""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ensemble_sizes = [4, 10, 20]
    x = np.arange(len(ensemble_sizes))
    width = 0.35

    for idx, dataset in enumerate(['VOC', 'INRIA']):
        ax = axes[idx]

        # 実測値
        measured_means = [measured[dataset][s]['mean'] for s in ensemble_sizes]
        measured_stds = [measured[dataset][s]['std'] for s in ensemble_sizes]

        # 論文値
        paper_values = [paper[dataset][s] for s in ensemble_sizes]

        bars1 = ax.bar(x - width/2, paper_values, width, label='Paper (Figure 4a)',
                      color='#1f77b4', alpha=0.8)
        bars2 = ax.bar(x + width/2, measured_means, width, label='Measured',
                      color='#2ca02c', alpha=0.8, yerr=measured_stds, capsize=3)

        ax.set_xlabel('Ensemble Size |B|')
        ax.set_ylabel('Time (seconds)')
        ax.set_title(f'{dataset} 1-patch: Computational Cost Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels([str(s) for s in ensemble_sizes])
        ax.legend(loc='upper left')
        ax.yaxis.grid(True, alpha=0.3)
        ax.set_axisbelow(True)

        # 値をバーの上に表示
        for bar, val in zip(bars1, paper_values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                   f'{val:.2f}s', ha='center', va='bottom', fontsize=9)
        for bar, val in zip(bars2, measured_means):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                   f'{val:.3f}s', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'timing_paper_vs_measured.pdf'))
    plt.savefig(os.path.join(OUTPUT_DIR, 'timing_paper_vs_measured.png'))
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/timing_paper_vs_measured.pdf/png")


def plot_scaling():
    """ensemble sizeに対するスケーリング"""
    fig, ax = plt.subplots(figsize=(8, 5))

    ensemble_sizes = [4, 10, 20]

    # VOC
    voc_measured = [measured['VOC'][s]['mean'] for s in ensemble_sizes]
    ax.plot(ensemble_sizes, voc_measured, 'o-', label='VOC (Measured)',
           color='#2ca02c', markersize=8)

    # INRIA
    inria_measured = [measured['INRIA'][s]['mean'] for s in ensemble_sizes]
    ax.plot(ensemble_sizes, inria_measured, 's-', label='INRIA (Measured)',
           color='#ff7f0e', markersize=8)

    # 論文値（VOC代表）
    paper_voc = [paper['VOC'][s] for s in ensemble_sizes]
    ax.plot(ensemble_sizes, paper_voc, '^--', label='Paper (Figure 4a)',
           color='#1f77b4', markersize=8, alpha=0.7)

    ax.set_xlabel('Ensemble Size |B|')
    ax.set_ylabel('Time (seconds)')
    ax.set_title('Computational Cost Scaling with Ensemble Size')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(ensemble_sizes)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'timing_scaling.pdf'))
    plt.savefig(os.path.join(OUTPUT_DIR, 'timing_scaling.png'))
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/timing_scaling.pdf/png")


def print_comparison_table():
    """比較表を出力"""
    print("\n=== 論文値 vs 実測値 比較 ===\n")
    print(f"{'Dataset':<8} {'|B|':<4} {'Paper(s)':<10} {'Measured(s)':<12} {'Ratio':<8}")
    print("-" * 50)

    for dataset in ['VOC', 'INRIA']:
        for b in [4, 10, 20]:
            p = paper[dataset][b]
            m = measured[dataset][b]['mean']
            ratio = m / p
            print(f"{dataset:<8} {b:<4} {p:<10.2f} {m:<12.4f} {ratio:<8.2f}")


if __name__ == '__main__':
    plot_comparison()
    plot_scaling()
    print_comparison_table()
