#!/usr/bin/env python3
"""
スライド用図表作成スクリプト
- S-01: Table 1 (RR) 再現比較グラフ
- S-02: Table 2 (nmAP) 再現比較グラフ
- S-03: 計算時間比較グラフ
"""

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd
import os

# 出力ディレクトリ（絶対パス）
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
    'xtick.labelsize': 9,
    'ytick.labelsize': 10,
    'legend.fontsize': 9,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1
})

# カラーパレット
COLORS = {
    'paper': '#1f77b4',      # 青
    'repro': '#2ca02c',      # 緑
    'saliuitl_4': '#ff7f0e', # オレンジ
    'saliuitl_20': '#d62728', # 赤
    'certifiable': '#9467bd', # 紫
    'themis': '#8c564b',      # 茶
    'jedi': '#e377c2',        # ピンク
}


def plot_table1_comparison():
    """S-01: Table 1 (Recovery Rate) 比較グラフ"""

    # RESULT_LOG.mdからのデータ
    data = {
        'Attack': [
            'CIFAR-1', 'CIFAR-2', 'CIFAR-4', 'CIFAR-T',
            'ImageNet-1', 'ImageNet-2', 'ImageNet-4', 'ImageNet-T',
            'INRIA-1', 'INRIA-2', 'INRIA-T',
            'VOC-1', 'VOC-2', 'VOC-T', 'VOC-MO'
        ],
        'Paper_RR': [
            0.9738, 0.9789, 0.9747, 0.8566,
            0.8869, 0.8535, 0.8436, 0.5065,
            0.5909, 0.3871, 0.4737,
            0.5404, 0.5376, 0.4244, 0.3955
        ],
        'Repro_RR': [
            0.9286, 0.8000, 0.9333, 0.8667,
            0.8667, 0.6667, 0.4667, 0.4000,
            0.7917, 0.8571, 0.3636,
            0.5385, 0.5263, 0.1500, 0.2593
        ]
    }

    df = pd.DataFrame(data)

    # グラフ作成
    fig, ax = plt.subplots(figsize=(14, 5))

    x = np.arange(len(df))
    width = 0.35

    bars1 = ax.bar(x - width/2, df['Paper_RR'], width,
                   label='Paper', color=COLORS['paper'], alpha=0.8)
    bars2 = ax.bar(x + width/2, df['Repro_RR'], width,
                   label='Reproduction', color=COLORS['repro'], alpha=0.8)

    # 装飾
    ax.set_ylabel('Recovery Rate')
    ax.set_title('Table 1: Recovery Rate Comparison (Paper vs Reproduction)')
    ax.set_xticks(x)
    ax.set_xticklabels(df['Attack'], rotation=45, ha='right')
    ax.legend(loc='upper right')
    ax.set_ylim(0, 1.1)
    ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.3)

    # グリッド
    ax.yaxis.grid(True, alpha=0.3)
    ax.set_axisbelow(True)

    # データセット区切り線
    for i in [4, 8, 11]:
        ax.axvline(x=i-0.5, color='gray', linestyle=':', alpha=0.5)

    # データセットラベル
    ax.text(1.5, 1.05, 'CIFAR', ha='center', fontsize=10, fontweight='bold')
    ax.text(5.5, 1.05, 'ImageNet', ha='center', fontsize=10, fontweight='bold')
    ax.text(9.5, 1.05, 'INRIA', ha='center', fontsize=10, fontweight='bold')
    ax.text(13, 1.05, 'VOC', ha='center', fontsize=10, fontweight='bold')

    plt.tight_layout()

    # 保存
    plt.savefig(f'{OUTPUT_DIR}/table1_comparison.pdf')
    plt.savefig(f'{OUTPUT_DIR}/table1_comparison.png')
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/table1_comparison.pdf/png")


def plot_table2_comparison():
    """S-02: Table 2 (nmAP) 比較グラフ"""

    # RESULT_LOG.mdからのデータ（物体検出のみ）
    data = {
        'Attack': [
            'VOC-1p', 'INRIA-1p'
        ],
        'Paper_Adv': [0.5094, 0.6897],
        'Repro_Adv': [0.6938, 0.7886],
        'Paper_Clean': [0.9950, 0.9998],
        'Repro_Clean': [1.0000, 1.0000]
    }

    df = pd.DataFrame(data)

    # 2つのサブプロット
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    x = np.arange(len(df))
    width = 0.35

    # Adversarial nmAP
    ax1 = axes[0]
    bars1 = ax1.bar(x - width/2, df['Paper_Adv'], width,
                    label='Paper', color=COLORS['paper'], alpha=0.8)
    bars2 = ax1.bar(x + width/2, df['Repro_Adv'], width,
                    label='Reproduction', color=COLORS['repro'], alpha=0.8)

    ax1.set_ylabel('Adversarial nmAP')
    ax1.set_title('Adversarial nmAP Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df['Attack'])
    ax1.legend(loc='upper left')
    ax1.set_ylim(0, 1.1)
    ax1.yaxis.grid(True, alpha=0.3)

    # バーの上に値を表示
    for bar, val in zip(bars1, df['Paper_Adv']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.3f}', ha='center', va='bottom', fontsize=9)
    for bar, val in zip(bars2, df['Repro_Adv']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.3f}', ha='center', va='bottom', fontsize=9)

    # Clean nmAP
    ax2 = axes[1]
    bars3 = ax2.bar(x - width/2, df['Paper_Clean'], width,
                    label='Paper', color=COLORS['paper'], alpha=0.8)
    bars4 = ax2.bar(x + width/2, df['Repro_Clean'], width,
                    label='Reproduction', color=COLORS['repro'], alpha=0.8)

    ax2.set_ylabel('Clean nmAP')
    ax2.set_title('Clean nmAP Comparison')
    ax2.set_xticks(x)
    ax2.set_xticklabels(df['Attack'])
    ax2.legend(loc='lower right')
    ax2.set_ylim(0.95, 1.02)
    ax2.yaxis.grid(True, alpha=0.3)

    # バーの上に値を表示
    for bar, val in zip(bars3, df['Paper_Clean']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.003,
                f'{val:.4f}', ha='center', va='bottom', fontsize=9)
    for bar, val in zip(bars4, df['Repro_Clean']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.003,
                f'{val:.4f}', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()

    # 保存
    plt.savefig(f'{OUTPUT_DIR}/table2_comparison.pdf')
    plt.savefig(f'{OUTPUT_DIR}/table2_comparison.png')
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/table2_comparison.pdf/png")


def plot_computational_cost():
    """S-03: 計算時間比較グラフ（論文Figure 4(a)再現）"""

    # 論文からの読み取りデータ
    # 代表的なシナリオのみ表示
    scenarios = ['INRIA', 'VOC', 'ImageNet', 'CIFAR']

    # 各手法の計算時間（秒）
    data = {
        'Saliuitl |B|=4': [0.30, 0.30, 0.10, 0.05],
        'Saliuitl |B|=20': [1.50, 1.50, 0.50, 0.25],
        'Themis': [0.20, 0.20, 0.10, 0.05],
        'Certifiable': [3.50, 2.00, 1.00, 0.50],
        'Jedi': [2.00, 1.00, 0.50, 0.20],
    }

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(scenarios))
    width = 0.15
    multiplier = 0

    colors = [COLORS['saliuitl_4'], COLORS['saliuitl_20'],
              COLORS['themis'], COLORS['certifiable'], COLORS['jedi']]

    for i, (method, times) in enumerate(data.items()):
        offset = width * multiplier
        bars = ax.bar(x + offset, times, width, label=method,
                     color=colors[i], alpha=0.8)
        multiplier += 1

    ax.set_ylabel('Time (seconds)')
    ax.set_title('Computational Cost Comparison (Paper Figure 4(a))')
    ax.set_xticks(x + width * 2)
    ax.set_xticklabels(scenarios)
    ax.legend(loc='upper right', ncol=2)
    ax.set_ylim(0, 4.5)
    ax.yaxis.grid(True, alpha=0.3)
    ax.set_axisbelow(True)

    plt.tight_layout()

    # 保存
    plt.savefig(f'{OUTPUT_DIR}/computational_cost.pdf')
    plt.savefig(f'{OUTPUT_DIR}/computational_cost.png')
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/computational_cost.pdf/png")


def plot_recovery_rate_by_dataset():
    """データセット別Recovery Rate詳細グラフ"""

    # 物体検出のみ
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # INRIA
    inria_data = {
        'Attack': ['1-patch', '2-patch', 'Triangular'],
        'Paper': [0.5909, 0.3871, 0.4737],
        'Repro': [0.7917, 0.8571, 0.3636]
    }

    ax1 = axes[0]
    x = np.arange(len(inria_data['Attack']))
    width = 0.35
    ax1.bar(x - width/2, inria_data['Paper'], width, label='Paper', color=COLORS['paper'])
    ax1.bar(x + width/2, inria_data['Repro'], width, label='Reproduction', color=COLORS['repro'])
    ax1.set_title('INRIA Dataset')
    ax1.set_ylabel('Recovery Rate')
    ax1.set_xticks(x)
    ax1.set_xticklabels(inria_data['Attack'])
    ax1.legend()
    ax1.set_ylim(0, 1.0)
    ax1.yaxis.grid(True, alpha=0.3)

    # VOC
    voc_data = {
        'Attack': ['1-patch', '2-patch', 'Triangular', 'Multi-Obj'],
        'Paper': [0.5404, 0.5376, 0.4244, 0.3955],
        'Repro': [0.5385, 0.5263, 0.1500, 0.2593]
    }

    ax2 = axes[1]
    x = np.arange(len(voc_data['Attack']))
    ax2.bar(x - width/2, voc_data['Paper'], width, label='Paper', color=COLORS['paper'])
    ax2.bar(x + width/2, voc_data['Repro'], width, label='Reproduction', color=COLORS['repro'])
    ax2.set_title('Pascal VOC Dataset')
    ax2.set_ylabel('Recovery Rate')
    ax2.set_xticks(x)
    ax2.set_xticklabels(voc_data['Attack'])
    ax2.legend()
    ax2.set_ylim(0, 1.0)
    ax2.yaxis.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/rr_by_dataset_detection.pdf')
    plt.savefig(f'{OUTPUT_DIR}/rr_by_dataset_detection.png')
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/rr_by_dataset_detection.pdf/png")


def create_summary_table():
    """サマリーテーブルをCSV出力"""

    data = {
        'Dataset': ['CIFAR', 'CIFAR', 'CIFAR', 'CIFAR',
                   'ImageNet', 'ImageNet', 'ImageNet', 'ImageNet',
                   'INRIA', 'INRIA', 'INRIA',
                   'VOC', 'VOC', 'VOC', 'VOC'],
        'Attack': ['1p', '2p', '4p', 'T',
                  '1p', '2p', '4p', 'T',
                  '1p', '2p', 'T',
                  '1p', '2p', 'T', 'MO'],
        'Paper_RR': [0.9738, 0.9789, 0.9747, 0.8566,
                    0.8869, 0.8535, 0.8436, 0.5065,
                    0.5909, 0.3871, 0.4737,
                    0.5404, 0.5376, 0.4244, 0.3955],
        'Repro_RR': [0.9286, 0.8000, 0.9333, 0.8667,
                    0.8667, 0.6667, 0.4667, 0.4000,
                    0.7917, 0.8571, 0.3636,
                    0.5385, 0.5263, 0.1500, 0.2593],
        'Paper_LPR': [0.0008, 0.0006, 0.0, 0.0,
                     0.0071, 0.0061, 0.0086, 0.0612,
                     0.0152, 0.0, 0.0526,
                     0.0293, 0.0125, 0.0348, 0.0095],
        'Detected': [0.9286, 0.8667, 1.0, 1.0,
                    1.0, 0.8667, 0.9333, 0.6667,
                    0.9583, 1.0, 0.5455,
                    1.0, 1.0, 0.8, 1.0]
    }

    df = pd.DataFrame(data)
    df['Diff_RR'] = df['Repro_RR'] - df['Paper_RR']

    df.to_csv(f'{OUTPUT_DIR}/reproduction_summary.csv', index=False)
    print(f"Saved: {OUTPUT_DIR}/reproduction_summary.csv")


if __name__ == '__main__':
    print("Generating slide figures...")

    # S-01: Table 1比較
    plot_table1_comparison()

    # S-02: Table 2比較
    plot_table2_comparison()

    # S-03: 計算時間比較
    plot_computational_cost()

    # 追加: データセット別詳細
    plot_recovery_rate_by_dataset()

    # サマリーテーブル
    create_summary_table()

    print("\nAll figures generated successfully!")
