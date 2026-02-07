#!/usr/bin/env python3
"""
スライドv2用の図表作成スクリプト（日本語版）
1. Oracle Test結果の棒グラフ
2. ボトルネック階層図
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path

# 出力ディレクトリ
OUTPUT_DIR = Path("/mnt/d/csprog/ooki/Saliuitl/docs/slides_material")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 日本語フォントを設定
JP_FONT_PATHS = [
    '/mnt/c/Windows/Fonts/NotoSansJP-VF.ttf',
    '/mnt/c/Windows/Fonts/meiryo.ttc',
    '/mnt/c/Windows/Fonts/YuGothR.ttc',
    '/mnt/c/Windows/Fonts/msgothic.ttc',
]

JP_FONT = None
for font_path in JP_FONT_PATHS:
    if Path(font_path).exists():
        JP_FONT = fm.FontProperties(fname=font_path)
        print(f"Using font: {font_path}")
        break

if JP_FONT is None:
    print("Warning: No Japanese font found. Using default font.")
    JP_FONT = fm.FontProperties()

# スタイル設定
plt.rcParams.update({
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
    'axes.unicode_minus': False,
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
    detection_data = {
        'INRIA 1p': (0.7917, 0.8750),
        'INRIA 2p': (0.8571, 1.0000),
        'INRIA trig': (0.3636, 0.5455),
        'VOC 1p': (0.5385, 0.7692),
        'VOC 2p': (0.5263, 0.7368),
        'VOC trig': (0.1500, 0.4500),
        'VOC mo': (0.2593, 0.7037),
    }

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

    ax1.set_ylabel('復元率 (Recovery Rate)', fontproperties=JP_FONT)
    ax1.set_title('物体検出 (平均 +22.8%)', fontproperties=JP_FONT, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=45, ha='right')
    ax1.set_ylim(0, 1.1)
    ax1.legend()
    ax1.axhline(y=1.0, color='gray', linestyle='--', alpha=0.3)

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

    ax2.set_ylabel('復元率 (Recovery Rate)', fontproperties=JP_FONT)
    ax2.set_title('画像分類 (平均 +0.8%)', fontproperties=JP_FONT, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, rotation=45, ha='right')
    ax2.set_ylim(0, 1.1)
    ax2.legend()
    ax2.axhline(y=1.0, color='gray', linestyle='--', alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "oracle_test_comparison.png")
    plt.savefig(OUTPUT_DIR / "oracle_test_comparison.pdf")
    print(f"Created: oracle_test_comparison.png")
    plt.close()


def create_oracle_test_summary():
    """Oracle Test結果のサマリー棒グラフ（タスク別平均）"""

    fig, ax = plt.subplots(figsize=(8, 5))

    tasks = ['物体検出', '画像分類']
    biharmonic = [0.498, 0.741]
    oracle = [0.726, 0.750]
    improvements = [0.228, 0.008]

    x = np.arange(len(tasks))
    width = 0.35

    bars1 = ax.bar(x - width/2, biharmonic, width, label='Biharmonic', color=COLORS['biharmonic'])
    bars2 = ax.bar(x + width/2, oracle, width, label='Oracle', color=COLORS['oracle'])

    ax.set_ylabel('平均復元率', fontproperties=JP_FONT)
    ax.set_title('Oracle Test: タスク別比較', fontproperties=JP_FONT, fontweight='bold', fontsize=16)
    ax.set_xticks(x)
    ax.set_xticklabels(tasks, fontproperties=JP_FONT)
    ax.set_ylim(0, 1.0)
    ax.legend(loc='upper right')

    for i, (b, o, imp) in enumerate(zip(biharmonic, oracle, improvements)):
        ax.annotate(f'+{imp:.1%}',
                   xy=(i + width/2, o + 0.03),
                   ha='center', fontsize=14, fontweight='bold',
                   color=COLORS['oracle'] if imp > 0.1 else 'gray')

    for bar, val in zip(bars1, biharmonic):
        ax.annotate(f'{val:.1%}', xy=(bar.get_x() + bar.get_width()/2, val + 0.01),
                   ha='center', fontsize=10)
    for bar, val in zip(bars2, oracle):
        ax.annotate(f'{val:.1%}', xy=(bar.get_x() + bar.get_width()/2, val + 0.01),
                   ha='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "oracle_test_summary.png")
    plt.savefig(OUTPUT_DIR / "oracle_test_summary.pdf")
    print(f"Created: oracle_test_summary.png")
    plt.close()


def create_bottleneck_hierarchy():
    """ボトルネック階層図"""

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    levels = [
        {
            'y': 8.5, 'label': '復元率 (Recovery Rate)',
            'color': '#e0e0e0', 'text_color': 'black',
            'detail': '出力'
        },
        {
            'y': 6.5, 'label': 'Level 3: インペインティング品質',
            'color': '#c8e6c9', 'text_color': 'black',
            'detail': '改善余地: 5-15%'
        },
        {
            'y': 4.5, 'label': 'Level 2: マスク精度',
            'color': '#fff9c4', 'text_color': 'black',
            'detail': '物体検出: +22.8% | 画像分類: +0.8%'
        },
        {
            'y': 2.5, 'label': 'Level 1: 検出率',
            'color': '#ffcdd2', 'text_color': 'black',
            'detail': '最重要ボトルネック (trig攻撃: 54-67%)'
        },
    ]

    box_width = 8
    box_height = 1.2

    for level in levels:
        rect = mpatches.FancyBboxPatch(
            (1, level['y'] - box_height/2), box_width, box_height,
            boxstyle="round,pad=0.05,rounding_size=0.2",
            facecolor=level['color'],
            edgecolor='gray',
            linewidth=2
        )
        ax.add_patch(rect)

        ax.text(5, level['y'] + 0.15, level['label'],
               ha='center', va='center', fontsize=13, fontweight='bold',
               color=level['text_color'], fontproperties=JP_FONT)

        if level['detail']:
            ax.text(5, level['y'] - 0.3, level['detail'],
                   ha='center', va='center', fontsize=10,
                   color='#555555', fontproperties=JP_FONT)

    arrow_props = dict(arrowstyle='->', color='#666666', lw=2)
    for i in range(len(levels) - 1):
        y_start = levels[i+1]['y'] + box_height/2 + 0.1
        y_end = levels[i]['y'] - box_height/2 - 0.1
        ax.annotate('', xy=(5, y_end), xytext=(5, y_start),
                   arrowprops=arrow_props)
        ax.text(5.5, (y_start + y_end)/2, '制約',
               ha='left', va='center', fontsize=9, color='#666666',
               style='italic', fontproperties=JP_FONT)

    ax.text(5, 9.5, 'ボトルネック階層構造',
           ha='center', va='center', fontsize=18, fontweight='bold',
           fontproperties=JP_FONT)

    ax.text(1, 0.8, '改善優先順位: Level 1 > Level 2 > Level 3',
           ha='left', va='center', fontsize=11, fontweight='bold',
           color=COLORS['highlight'], fontproperties=JP_FONT)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "bottleneck_hierarchy.png")
    plt.savefig(OUTPUT_DIR / "bottleneck_hierarchy.pdf")
    print(f"Created: bottleneck_hierarchy.png")
    plt.close()


def create_bottleneck_table():
    """ボトルネック改善余地の表形式図"""

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis('off')

    columns = ['レベル', 'ボトルネック', '物体検出', '画像分類']
    data = [
        ['Level 1', '検出率', '15-45% (攻撃依存)', '3-7%'],
        ['Level 2', 'マスク精度', '+22.8% (高優先)', '+0.8% (低優先)'],
        ['Level 3', 'インペインティング品質', '5-15%', '0-10%'],
    ]

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

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(fontweight='bold', fontproperties=JP_FONT)
        else:
            cell.set_text_props(fontproperties=JP_FONT)
        cell.set_edgecolor('white')
        cell.set_linewidth(2)

    ax.set_title('ボトルネック別の改善余地',
                fontsize=14, fontweight='bold', pad=20, fontproperties=JP_FONT)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "bottleneck_table.png")
    plt.savefig(OUTPUT_DIR / "bottleneck_table.pdf")
    print(f"Created: bottleneck_table.png")
    plt.close()


def create_success_definition():
    """成功の定義と乖離の図"""

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # 左側: 論文の定義
    rect1 = mpatches.FancyBboxPatch(
        (0.5, 2), 4, 3,
        boxstyle="round,pad=0.1,rounding_size=0.2",
        facecolor='#e3f2fd',
        edgecolor='#1976d2',
        linewidth=2
    )
    ax.add_patch(rect1)
    ax.text(2.5, 4.5, '論文の「成功」定義', ha='center', va='center',
           fontsize=12, fontweight='bold', color='#1976d2', fontproperties=JP_FONT)
    ax.text(2.5, 3.5, 'IoU ≥ 0.5 で\n検出がマッチ', ha='center', va='center',
           fontsize=11, fontproperties=JP_FONT)
    ax.text(2.5, 2.5, '→ 検出回復が目標', ha='center', va='center',
           fontsize=10, color='#555555', fontproperties=JP_FONT)

    # 右側: 視覚的期待
    rect2 = mpatches.FancyBboxPatch(
        (5.5, 2), 4, 3,
        boxstyle="round,pad=0.1,rounding_size=0.2",
        facecolor='#fff3e0',
        edgecolor='#e65100',
        linewidth=2
    )
    ax.add_patch(rect2)
    ax.text(7.5, 4.5, '視覚的な期待', ha='center', va='center',
           fontsize=12, fontweight='bold', color='#e65100', fontproperties=JP_FONT)
    ax.text(7.5, 3.5, 'パッチが除去され\n元画像に近づく', ha='center', va='center',
           fontsize=11, fontproperties=JP_FONT)
    ax.text(7.5, 2.5, '→ 画像復元が目標', ha='center', va='center',
           fontsize=10, color='#555555', fontproperties=JP_FONT)

    ax.text(5, 3.5, '≠', ha='center', va='center',
           fontsize=30, fontweight='bold', color=COLORS['highlight'])

    ax.text(5, 1, '検出回復 ≠ パッチ除去（評価指標と視覚的品質は別物）',
           ha='center', va='center', fontsize=12, fontweight='bold',
           color=COLORS['highlight'], fontproperties=JP_FONT)

    ax.text(5, 5.7, '「成功」の定義と視覚的期待の乖離',
           ha='center', va='center', fontsize=16, fontweight='bold',
           fontproperties=JP_FONT)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "success_definition.png")
    plt.savefig(OUTPUT_DIR / "success_definition.pdf")
    print(f"Created: success_definition.png")
    plt.close()


def create_oracle_definition():
    """Oracle Inpaintingの定義図"""

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')

    # ボックス1: マスク領域
    rect1 = mpatches.FancyBboxPatch(
        (0.5, 1.5), 2.5, 2,
        boxstyle="round,pad=0.1",
        facecolor='#ffcdd2',
        edgecolor='#d32f2f',
        linewidth=2
    )
    ax.add_patch(rect1)
    ax.text(1.75, 2.5, 'マスク領域\n(攻撃パッチ)', ha='center', va='center',
           fontsize=10, fontproperties=JP_FONT)

    ax.annotate('', xy=(4, 2.5), xytext=(3.2, 2.5),
               arrowprops=dict(arrowstyle='->', lw=2, color='#666666'))

    # ボックス2: クリーン画像
    rect2 = mpatches.FancyBboxPatch(
        (4.2, 1.5), 2.5, 2,
        boxstyle="round,pad=0.1",
        facecolor='#c8e6c9',
        edgecolor='#388e3c',
        linewidth=2
    )
    ax.add_patch(rect2)
    ax.text(5.45, 2.5, 'クリーン画像の\nピクセルを貼付', ha='center', va='center',
           fontsize=10, fontproperties=JP_FONT)

    ax.annotate('', xy=(7.8, 2.5), xytext=(7, 2.5),
               arrowprops=dict(arrowstyle='->', lw=2, color='#666666'))

    # ボックス3: 結果
    rect3 = mpatches.FancyBboxPatch(
        (8, 1.5), 1.8, 2,
        boxstyle="round,pad=0.1",
        facecolor='#e3f2fd',
        edgecolor='#1976d2',
        linewidth=2
    )
    ax.add_patch(rect3)
    ax.text(8.9, 2.5, '理論上の\n上限性能', ha='center', va='center',
           fontsize=10, fontproperties=JP_FONT)

    ax.text(5, 4.3, 'Oracle Inpainting の定義',
           ha='center', va='center', fontsize=16, fontweight='bold',
           fontproperties=JP_FONT)

    ax.text(5, 0.7, '→ インペインティング品質の理論上の上限を示す（マスク精度の問題は残る）',
           ha='center', va='center', fontsize=11, color='#555555',
           fontproperties=JP_FONT)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "oracle_definition.png")
    plt.savefig(OUTPUT_DIR / "oracle_definition.pdf")
    print(f"Created: oracle_definition.png")
    plt.close()


def main():
    print("Creating slide figures v2 (Japanese)...")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    print("1. Creating Oracle Test comparison chart...")
    create_oracle_test_comparison()

    print("2. Creating Oracle Test summary chart...")
    create_oracle_test_summary()

    print("3. Creating bottleneck hierarchy diagram...")
    create_bottleneck_hierarchy()

    print("4. Creating bottleneck table...")
    create_bottleneck_table()

    print("5. Creating success definition diagram...")
    create_success_definition()

    print("6. Creating Oracle definition diagram...")
    create_oracle_definition()

    print()
    print("All figures created successfully!")
    print()
    print("Generated files:")
    for f in sorted(OUTPUT_DIR.glob("*.png")):
        if any(x in f.name for x in ["oracle", "bottleneck", "success"]):
            print(f"  - {f.name}")


if __name__ == "__main__":
    main()
