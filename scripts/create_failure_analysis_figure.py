#!/usr/bin/env python3
"""
失敗分析サマリー図の作成スクリプト
TASK-20260204-B: S-06 スライド用
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os

# 出力ディレクトリ
OUTPUT_DIR = "/mnt/d/csprog/ooki/Saliuitl/docs/slides_material"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# フォント設定
plt.rcParams['font.size'] = 11
plt.rcParams['axes.unicode_minus'] = False

def create_failure_analysis_figure():
    """失敗分析サマリー図を作成"""

    fig, axes = plt.subplots(1, 3, figsize=(16, 8))
    fig.suptitle('Failure Analysis Summary: Patch Removal Pipeline',
                 fontsize=16, fontweight='bold', y=0.98)

    # === 左パネル: 失敗ケース分類 ===
    ax1 = axes[0]
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    ax1.set_title('Failure Categories', fontsize=14, fontweight='bold', pad=10)

    # カテゴリボックス
    categories = [
        ('1. Mask Localization\n    Failure', 'red', 8.5,
         '- Mask does not cover patch\n- Overlap ratio: 1.4%-2.5%\n- mIoU: 0.00-0.08'),
        ('2. Resolution\n    Mismatch', 'orange', 5.5,
         '- Feature map: 26x26\n- Input image: 416x416\n- Scale factor: 16x'),
        ('3. Attention\n    Hijacking', 'gold', 2.5,
         '- Patch diverts detector\n- Detection "succeeds" but\n  patch remains visible')
    ]

    for title, color, y_pos, details in categories:
        # メインボックス
        box = FancyBboxPatch((0.5, y_pos-1), 4, 2.2,
                             boxstyle="round,pad=0.1,rounding_size=0.3",
                             facecolor=color, alpha=0.3,
                             edgecolor=color, linewidth=2)
        ax1.add_patch(box)
        ax1.text(2.5, y_pos+0.5, title, ha='center', va='center',
                fontsize=11, fontweight='bold')

        # 詳細テキスト
        ax1.text(5, y_pos, details, ha='left', va='center',
                fontsize=9, family='monospace')

    # === 中央パネル: 因果関係図 ===
    ax2 = axes[1]
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')
    ax2.set_title('Causal Chain', fontsize=14, fontweight='bold', pad=10)

    # ノード定義
    nodes = [
        ('Low Resolution\nFeature Maps\n(26x26)', 5, 9, '#ff6b6b'),
        ('Coarse Mask\nGeneration', 5, 6.5, '#ffa94d'),
        ('Mask-Patch\nMisalignment', 5, 4, '#ffd43b'),
        ('Patch Remains\nVisible', 5, 1.5, '#69db7c'),
    ]

    for label, x, y, color in nodes:
        box = FancyBboxPatch((x-2, y-0.8), 4, 1.6,
                             boxstyle="round,pad=0.05,rounding_size=0.2",
                             facecolor=color, alpha=0.5,
                             edgecolor='black', linewidth=1.5)
        ax2.add_patch(box)
        ax2.text(x, y, label, ha='center', va='center',
                fontsize=10, fontweight='bold')

    # 矢印
    arrow_style = dict(arrowstyle='->', connectionstyle='arc3,rad=0',
                       color='#495057', lw=2, mutation_scale=15)
    for i in range(len(nodes)-1):
        y1 = nodes[i][2] - 0.8
        y2 = nodes[i+1][2] + 0.8
        ax2.annotate('', xy=(5, y2), xytext=(5, y1),
                    arrowprops=arrow_style)

    # 補足テキスト
    ax2.text(5, -0.3, 'Root Cause: Architectural Limitation',
            ha='center', va='top', fontsize=10, style='italic',
            color='#495057')

    # === 右パネル: 数値統計 ===
    ax3 = axes[2]
    ax3.set_title('Quantitative Results', fontsize=14, fontweight='bold', pad=10)

    # 棒グラフデータ
    methods = ['Naive\n(>0)', 'Liberal\n(>0.1)', 'Conservative\n(>0.5)', 'Oracle\n(GT)']
    miou_values = [0.00, 0.08, 0.03, 1.00]
    colors = ['#e03131', '#f08c00', '#fab005', '#2f9e44']

    bars = ax3.bar(methods, miou_values, color=colors, edgecolor='black', linewidth=1.5)
    ax3.set_ylabel('Mask IoU with Patch', fontsize=12)
    ax3.set_ylim(0, 1.1)
    ax3.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='Acceptable threshold')

    # 値ラベル
    for bar, val in zip(bars, miou_values):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.03,
                f'{val:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax3.legend(loc='upper right', fontsize=9)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)

    # 下部にサマリーテキスト
    fig.text(0.5, 0.02,
             'Key Finding: Current system cannot accurately locate adversarial patches due to resolution limitations.\n'
             'Detection "success" does not imply visual patch removal.',
             ha='center', va='bottom', fontsize=11, style='italic',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.3))

    plt.tight_layout(rect=[0, 0.08, 1, 0.95])

    # 保存
    output_path = os.path.join(OUTPUT_DIR, 'failure_analysis_summary.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"Saved: {output_path}")

    plt.close()

if __name__ == '__main__':
    create_failure_analysis_figure()
