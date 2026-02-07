#!/usr/bin/env python3
"""
スライドv2用の図表作成スクリプト
1. Oracle Test結果の棒グラフ
2. ボトルネック階層図
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# 出力ディレクトリ
OUTPUT_DIR = Path("docs/slides_material")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# スタイル設定
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1
})

# カラーパレット
COLORS = {
    'biharmonic': '#1f77b4',  # 青
    'oracle': '#2ca02c',       # 緑
    'detection': '#ff7f0e',    # オレンジ
    'highlight': '#d62728',    # 赤
}


def create_oracle_test_comparison():
    """Oracle Test結果の棒グラフ（物体検出 vs 画像分類）"""

    # データ（RESULT_LOG.mdより）
    # 物体検出
    detection_data = {
        'INRIA 1p': (0.7917, 0.8750),
        'INRIA 2p': (0.8571, 1.0000),
        'INRIA trig': (0.3636, 0.5455),
        'VOC 1p': (0.5385, 0.7692),
        'VOC 2p': (0.5263, 0.7368),
        'VOC trig': (0.1500, 0.4500),
        'VOC mo': (0.2593, 0.7037),
    }

    # 画像分類
    classification_data = {
        'CIFAR 1p': (0.9286, 0.9286),
        'CIFAR 2p': (0.8000, 0.8000),
        'CIFAR 4p': (0.9333, 0.8667),
        'CIFAR trig': (0.8667, 0.8000),
        'ImageNet 1p': (0.8667, 0.7333),
        'ImageNet 2p': (0.6667, 0.8000),
        'ImageNet 4p': (0.4667, 0.6667),
        'ImageNet trig': (0.4000, 0.4000),
    }

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 物体検出
    ax1 = axes[0]
    labels = list(detection_data.keys())
    bio_vals = [v[0] for v in detection_data.values()]
    oracle_vals = [v[1] for v in detection_data.values()]

    x = np.arange(len(labels))
    width = 0.35

    bars1 = ax1.bar(x - width/2, bio_vals, width, label='Biharmonic', color=COLORS['biharmonic'])
    bars2 = ax1.bar(x + width/2, oracle_vals, width, label='Oracle', color=COLORS['oracle'])

    ax1.set_ylabel('Recovery Rate')
    ax1.set_title('Object Detection (Avg. +22.8%)', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=45, ha='right')
    ax1.set_ylim(0, 1.1)
    ax1.legend()
    ax1.axhline(y=1.0, color='gray', linestyle='--', alpha=0.3)

    # 改善幅を表示
    for i, (b, o) in enumerate(zip(bio_vals, oracle_vals)):
        diff = o - b
        if diff > 0:
            ax1.annotate(f'+{diff:.1%}', xy=(i, o + 0.02), ha='center', fontsize=9, color=COLORS['oracle'])

    # 画像分類
    ax2 = axes[1]
    labels = list(classification_data.keys())
    bio_vals = [v[0] for v in classification_data.values()]
    oracle_vals = [v[1] for v in classification_data.values()]

    x = np.arange(len(labels))

    bars1 = ax2.bar(x - width/2, bio_vals, width, label='Biharmonic', color=COLORS['biharmonic'])
    bars2 = ax2.bar(x + width/2, oracle_vals, width, label='Oracle', color=COLORS['oracle'])

    ax2.set_ylabel('Recovery Rate')
    ax2.set_title('Image Classification (Avg. +0.8%)', fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, rotation=45, ha='right')
    ax2.set_ylim(0, 1.1)
    ax2.legend()
    ax2.axhline(y=1.0, color='gray', linestyle='--', alpha=0.3)

    plt.tight_layout()

    # 保存
    plt.savefig(OUTPUT_DIR / "oracle_test_comparison.png")
    plt.savefig(OUTPUT_DIR / "oracle_test_comparison.pdf")
    print(f"Created: {OUTPUT_DIR}/oracle_test_comparison.png")
    plt.close()


def create_oracle_test_summary():
    """Oracle Test結果のサマリー棒グラフ（タスク別平均）"""

    fig, ax = plt.subplots(figsize=(8, 5))

    tasks = ['Object Detection', 'Image Classification']
    biharmonic = [0.498, 0.741]
    oracle = [0.726, 0.750]
    improvements = [0.228, 0.008]

    x = np.arange(len(tasks))
    width = 0.35

    bars1 = ax.bar(x - width/2, biharmonic, width, label='Biharmonic', color=COLORS['biharmonic'])
    bars2 = ax.bar(x + width/2, oracle, width, label='Oracle', color=COLORS['oracle'])

    ax.set_ylabel('Average Recovery Rate')
    ax.set_title('Oracle Test: Task Comparison', fontweight='bold', fontsize=16)
    ax.set_xticks(x)
    ax.set_xticklabels(tasks)
    ax.set_ylim(0, 1.0)
    ax.legend(loc='upper right')

    # 改善幅を表示
    for i, (b, o, imp) in enumerate(zip(biharmonic, oracle, improvements)):
        ax.annotate(f'+{imp:.1%}',
                   xy=(i + width/2, o + 0.03),
                   ha='center', fontsize=14, fontweight='bold',
                   color=COLORS['oracle'] if imp > 0.1 else 'gray')

    # 値を棒の上に表示
    for bar, val in zip(bars1, biharmonic):
        ax.annotate(f'{val:.1%}', xy=(bar.get_x() + bar.get_width()/2, val + 0.01),
                   ha='center', fontsize=10)
    for bar, val in zip(bars2, oracle):
        ax.annotate(f'{val:.1%}', xy=(bar.get_x() + bar.get_width()/2, val + 0.01),
                   ha='center', fontsize=10)

    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / "oracle_test_summary.png")
    plt.savefig(OUTPUT_DIR / "oracle_test_summary.pdf")
    print(f"Created: {OUTPUT_DIR}/oracle_test_summary.png")
    plt.close()


def create_bottleneck_hierarchy():
    """ボトルネック階層図"""

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # 階層ボックスの設定
    levels = [
        {
            'y': 8.5, 'label': 'Recovery Rate (Output)',
            'color': '#e0e0e0', 'text_color': 'black',
            'detail': ''
        },
        {
            'y': 6.5, 'label': 'Level 3: Inpainting Quality',
            'color': '#c8e6c9', 'text_color': 'black',
            'detail': 'Improvement: 5-15%'
        },
        {
            'y': 4.5, 'label': 'Level 2: Mask Accuracy',
            'color': '#fff9c4', 'text_color': 'black',
            'detail': 'Detection: +22.8% | Classification: +0.8%'
        },
        {
            'y': 2.5, 'label': 'Level 1: Detection Rate',
            'color': '#ffcdd2', 'text_color': 'black',
            'detail': 'Most Critical (trig: 54-67%)'
        },
    ]

    box_width = 8
    box_height = 1.2

    for level in levels:
        # ボックス
        rect = mpatches.FancyBboxPatch(
            (1, level['y'] - box_height/2), box_width, box_height,
            boxstyle="round,pad=0.05,rounding_size=0.2",
            facecolor=level['color'],
            edgecolor='gray',
            linewidth=2
        )
        ax.add_patch(rect)

        # ラベル
        ax.text(5, level['y'] + 0.15, level['label'],
               ha='center', va='center', fontsize=13, fontweight='bold',
               color=level['text_color'])

        # 詳細
        if level['detail']:
            ax.text(5, level['y'] - 0.3, level['detail'],
                   ha='center', va='center', fontsize=10,
                   color='#555555')

    # 矢印（制約の方向）
    arrow_props = dict(arrowstyle='->', color='#666666', lw=2)
    for i in range(len(levels) - 1):
        y_start = levels[i+1]['y'] + box_height/2 + 0.1
        y_end = levels[i]['y'] - box_height/2 - 0.1
        ax.annotate('', xy=(5, y_end), xytext=(5, y_start),
                   arrowprops=arrow_props)
        ax.text(5.5, (y_start + y_end)/2, 'constrains',
               ha='left', va='center', fontsize=9, color='#666666', style='italic')

    # タイトル
    ax.text(5, 9.5, 'Bottleneck Hierarchy',
           ha='center', va='center', fontsize=18, fontweight='bold')

    # 凡例
    ax.text(1, 0.8, 'Priority: Level 1 > Level 2 > Level 3',
           ha='left', va='center', fontsize=11, fontweight='bold',
           color=COLORS['highlight'])

    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / "bottleneck_hierarchy.png")
    plt.savefig(OUTPUT_DIR / "bottleneck_hierarchy.pdf")
    print(f"Created: {OUTPUT_DIR}/bottleneck_hierarchy.png")
    plt.close()


def create_bottleneck_table():
    """ボトルネック改善余地の表形式図"""

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis('off')

    # テーブルデータ
    columns = ['Level', 'Bottleneck', 'Object Detection', 'Image Classification']
    data = [
        ['Level 1', 'Detection Rate', '15-45% (attack dependent)', '3-7%'],
        ['Level 2', 'Mask Accuracy', '+22.8% (High Priority)', '+0.8% (Low Priority)'],
        ['Level 3', 'Inpainting Quality', '5-15%', '0-10%'],
    ]

    # カラー設定
    cell_colors = [
        ['#ffcdd2', '#ffcdd2', '#ffcdd2', '#e8f5e9'],
        ['#fff9c4', '#fff9c4', '#ffcc80', '#e8f5e9'],
        ['#c8e6c9', '#c8e6c9', '#c8e6c9', '#c8e6c9'],
    ]

    table = ax.table(
        cellText=data,
        colLabels=columns,
        cellLoc='center',
        loc='center',
        cellColours=cell_colors,
        colColours=['#b0bec5'] * 4
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 2)

    # ヘッダーを太字に
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(fontweight='bold')
        cell.set_edgecolor('white')
        cell.set_linewidth(2)

    ax.set_title('Improvement Potential by Bottleneck Level',
                fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / "bottleneck_table.png")
    plt.savefig(OUTPUT_DIR / "bottleneck_table.pdf")
    print(f"Created: {OUTPUT_DIR}/bottleneck_table.png")
    plt.close()


def create_attack_comparison():
    """攻撃前後の比較用プレースホルダー図（実際の画像がない場合）"""

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    titles = ['Clean Image', 'Attacked Image', 'Detection Result']
    colors = ['#4CAF50', '#f44336', '#2196F3']

    for ax, title, color in zip(axes, titles, colors):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)

        # 画像プレースホルダー
        rect = mpatches.Rectangle((0.5, 0.5), 9, 9,
                                   facecolor='#f5f5f5', edgecolor=color, linewidth=3)
        ax.add_patch(rect)

        ax.text(5, 5, f'[{title}]', ha='center', va='center',
               fontsize=14, color='#888888')
        ax.set_title(title, fontsize=12, fontweight='bold', color=color)
        ax.axis('off')

    plt.suptitle('Adversarial Patch Attack Example', fontsize=14, fontweight='bold')
    plt.tight_layout()

    plt.savefig(OUTPUT_DIR / "attack_comparison_placeholder.png")
    print(f"Created: {OUTPUT_DIR}/attack_comparison_placeholder.png")
    plt.close()


def main():
    print("Creating slide figures v2...")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    # 1. Oracle Test結果の棒グラフ（詳細版）
    print("1. Creating Oracle Test comparison chart...")
    create_oracle_test_comparison()

    # 2. Oracle Test結果のサマリー
    print("2. Creating Oracle Test summary chart...")
    create_oracle_test_summary()

    # 3. ボトルネック階層図
    print("3. Creating bottleneck hierarchy diagram...")
    create_bottleneck_hierarchy()

    # 4. ボトルネック表
    print("4. Creating bottleneck table...")
    create_bottleneck_table()

    # 5. 攻撃比較プレースホルダー
    print("5. Creating attack comparison placeholder...")
    create_attack_comparison()

    print()
    print("All figures created successfully!")
    print()
    print("Generated files:")
    for f in sorted(OUTPUT_DIR.glob("*.png")):
        if f.name.startswith(("oracle_", "bottleneck_", "attack_comparison")):
            print(f"  - {f}")


if __name__ == "__main__":
    main()
