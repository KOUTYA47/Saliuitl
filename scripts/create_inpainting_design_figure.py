#!/usr/bin/env python3
"""
インペインティング設計の説明図を作成
Slide 11: 原因分析（1）設計上の理由
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch
import numpy as np
import os

OUTPUT_DIR = "/mnt/d/csprog/ooki/Saliuitl/docs/slides_material"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日本語フォント設定
plt.rcParams['font.family'] = ['Noto Sans JP', 'Yu Gothic', 'Meiryo', 'sans-serif']
plt.rcParams['font.size'] = 11
plt.rcParams['figure.facecolor'] = 'white'


def create_inpainting_design_figure():
    """可視化マスク vs 実際のインペインティングの違いを説明する図"""

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    fig.suptitle('可視化マスク vs 実際のインペインティング', fontsize=16, fontweight='bold', y=0.98)

    # === 左パネル: 可視化マスク（蓄積） ===
    ax1 = axes[0]
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    ax1.set_title('可視化（Mask Overlay）\n全βの結果を蓄積', fontsize=13, fontweight='bold', color='green')

    # 背景ボックス
    bg1 = FancyBboxPatch((0.5, 1), 9, 8,
                          boxstyle="round,pad=0.05,rounding_size=0.2",
                          facecolor='#E8F5E9', alpha=0.5,
                          edgecolor='green', linewidth=2)
    ax1.add_patch(bg1)

    # β値ごとのマスクを重ねて表示
    masks = [
        (3, 5, 1.5, 1.5, '#FF6B6B', 'β=0.99'),
        (3.3, 4.7, 2, 2, '#FFA94D', 'β=0.95'),
        (3.5, 4.5, 2.5, 2.5, '#FFD43B', 'β=0.90'),
        (3.7, 4.3, 3, 3, '#69DB7C', 'β=0.50'),
        (4, 4, 3.5, 3.5, '#4DABF7', 'β=0.05'),
    ]

    for x, y, w, h, color, label in masks:
        rect = Rectangle((x, y), w, h, fill=True,
                          facecolor=color, alpha=0.4, edgecolor=color, linewidth=1)
        ax1.add_patch(rect)

    # パッチの実際位置
    patch = Rectangle((3.5, 4.2), 3.2, 3.2, fill=False,
                       edgecolor='red', linewidth=3, linestyle='--')
    ax1.add_patch(patch)
    ax1.text(5.1, 7.8, '実際のパッチ', ha='center', va='bottom', fontsize=10, color='red')

    # 説明
    ax1.text(5, 2.5, '全βのマスクを重ね合わせ\n→ パッチ全体をカバー',
             ha='center', va='center', fontsize=11,
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    ax1.text(5, 0.5, '✓ 見た目上はパッチをカバー',
             ha='center', va='center', fontsize=11, color='green', fontweight='bold')

    # === 右パネル: 実際のインペインティング（各β単独） ===
    ax2 = axes[1]
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')
    ax2.set_title('実際のインペインティング\n各β単独で実行', fontsize=13, fontweight='bold', color='red')

    # 背景ボックス
    bg2 = FancyBboxPatch((0.5, 1), 9, 8,
                          boxstyle="round,pad=0.05,rounding_size=0.2",
                          facecolor='#FFEBEE', alpha=0.5,
                          edgecolor='red', linewidth=2)
    ax2.add_patch(bg2)

    # 各反復を縦に並べて表示
    iterations = [
        (1.5, 7.5, 'β=0.99', '#FF6B6B', 0.8, 0.8),
        (1.5, 5.5, 'β=0.95', '#FFA94D', 1.0, 1.0),
        (1.5, 3.5, 'β=0.05', '#4DABF7', 1.5, 1.5),
    ]

    for x, y, label, color, w, h in iterations:
        # オリジナル画像ボックス
        img_box = Rectangle((x, y), 2, 1.5, fill=True,
                             facecolor='lightgray', alpha=0.5, edgecolor='black', linewidth=1)
        ax2.add_patch(img_box)
        ax2.text(x+1, y+1.7, 'オリジナル', ha='center', va='bottom', fontsize=8)

        # 矢印
        ax2.annotate('', xy=(x+3, y+0.75), xytext=(x+2.2, y+0.75),
                    arrowprops=dict(arrowstyle='->', color='black', lw=1.5))

        # マスク（小さい）
        mask_box = Rectangle((x+3.2, y+0.3), w, h, fill=True,
                              facecolor=color, alpha=0.6, edgecolor=color, linewidth=2)
        ax2.add_patch(mask_box)
        ax2.text(x+3.2+w/2, y+0.1, label, ha='center', va='top', fontsize=8)

        # 矢印
        ax2.annotate('', xy=(x+5.5, y+0.75), xytext=(x+4.8, y+0.75),
                    arrowprops=dict(arrowstyle='->', color='black', lw=1.5))

        # 結果（部分的にインペイント）
        result_box = Rectangle((x+5.7, y), 2, 1.5, fill=True,
                                facecolor='lightgray', alpha=0.5, edgecolor='black', linewidth=1)
        ax2.add_patch(result_box)
        # 部分的にぼやける部分
        blur_box = Rectangle((x+6.1, y+0.3), w*0.8, h*0.8, fill=True,
                              facecolor='white', alpha=0.7, edgecolor='gray', linewidth=1)
        ax2.add_patch(blur_box)
        ax2.text(x+6.7, y+1.7, '部分的', ha='center', va='bottom', fontsize=8)

    # 毎回リセットの説明
    ax2.annotate('', xy=(1.2, 5.5), xytext=(1.2, 7),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1, linestyle='--'))
    ax2.text(0.8, 6.2, 'リセット', ha='center', va='center', fontsize=8, color='gray', rotation=90)

    ax2.annotate('', xy=(1.2, 3.5), xytext=(1.2, 5),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1, linestyle='--'))

    # 説明
    ax2.text(5, 2, '各βで独立に実行\n毎回オリジナル画像に戻る\n→ 部分的なマスクのみ適用',
             ha='center', va='center', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    ax2.text(5, 0.5, '✗ パッチは部分的にしか処理されない',
             ha='center', va='center', fontsize=11, color='red', fontweight='bold')

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])

    output_path = os.path.join(OUTPUT_DIR, 'inpainting_design.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print(f"Created: {output_path}")


def create_design_intention_figure():
    """設計意図を説明する図"""

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')

    fig.suptitle('Saliuitl の設計意図: 検出回復の最大化', fontsize=16, fontweight='bold', y=0.95)

    # 左側: 設計の流れ
    ax.text(3, 9, '【設計の流れ】', ha='center', va='center', fontsize=13, fontweight='bold')

    steps = [
        (3, 7.5, 'β=0.99 で試す', '検出0個'),
        (3, 6, 'β=0.95 で試す', '検出1個 ✓'),
        (3, 4.5, 'β=0.90 で試す', '検出2個 ✓'),
        (3, 3, '...', '...'),
        (3, 1.5, 'β=0.05 で試す', '検出1個 ✓'),
    ]

    for x, y, left_text, right_text in steps:
        # 左のボックス
        box = FancyBboxPatch((x-2, y-0.4), 2.5, 0.8,
                             boxstyle="round,pad=0.05,rounding_size=0.1",
                             facecolor='#E3F2FD', alpha=0.8,
                             edgecolor='#1976D2', linewidth=1)
        ax.add_patch(box)
        ax.text(x-0.75, y, left_text, ha='center', va='center', fontsize=10)

        # 矢印
        ax.annotate('', xy=(x+1.5, y), xytext=(x+0.7, y),
                   arrowprops=dict(arrowstyle='->', color='black', lw=1))

        # 右のテキスト
        color = 'green' if '✓' in right_text else 'gray'
        ax.text(x+2.2, y, right_text, ha='left', va='center', fontsize=10, color=color)

    # 右側: 蓄積と結果
    ax.text(9, 9, '【検出ボックスの蓄積】', ha='center', va='center', fontsize=13, fontweight='bold')

    # 蓄積ボックス
    accum_box = FancyBboxPatch((7, 4), 4, 4,
                                boxstyle="round,pad=0.05,rounding_size=0.2",
                                facecolor='#FFF9C4', alpha=0.8,
                                edgecolor='#F9A825', linewidth=2)
    ax.add_patch(accum_box)

    ax.text(9, 7.5, '全βからの検出を蓄積', ha='center', va='center', fontsize=11)
    ax.text(9, 6.5, '↓', ha='center', va='center', fontsize=14)
    ax.text(9, 5.5, 'NMSで重複除去', ha='center', va='center', fontsize=11)
    ax.text(9, 4.5, '↓', ha='center', va='center', fontsize=14)

    # 結果
    result_box = FancyBboxPatch((7.5, 1.5), 3, 1.5,
                                 boxstyle="round,pad=0.05,rounding_size=0.2",
                                 facecolor='#C8E6C9', alpha=0.8,
                                 edgecolor='#388E3C', linewidth=2)
    ax.add_patch(result_box)
    ax.text(9, 2.25, '1つでも検出できれば\n「回復成功」', ha='center', va='center',
            fontsize=11, fontweight='bold', color='#2E7D32')

    # 矢印（蓄積へ）
    ax.annotate('', xy=(6.8, 6), xytext=(5.5, 6),
               arrowprops=dict(arrowstyle='->', color='#F9A825', lw=2))

    # 下部の結論
    ax.text(6, 0.3,
            '目標: 検出の回復（Recovery Rate）  |  視覚的なパッチ除去は目標外',
            ha='center', va='center', fontsize=12,
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9, edgecolor='orange'))

    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, 'design_intention.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print(f"Created: {output_path}")


if __name__ == '__main__':
    create_inpainting_design_figure()
    create_design_intention_figure()
    print("\n=== All design figures generated ===")
