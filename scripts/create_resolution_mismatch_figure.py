#!/usr/bin/env python3
"""
解像度ミスマッチ図の作成スクリプト
Slide 11: 原因分析用
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyArrowPatch, FancyBboxPatch
import numpy as np
import os

OUTPUT_DIR = "/mnt/d/csprog/ooki/Saliuitl/docs/slides_material"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日本語フォント設定
plt.rcParams['font.family'] = ['Noto Sans JP', 'Yu Gothic', 'Meiryo', 'sans-serif']
plt.rcParams['font.size'] = 11
plt.rcParams['figure.facecolor'] = 'white'

def create_resolution_mismatch_figure():
    """解像度ミスマッチを説明する図を作成"""

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle('解像度ミスマッチ: 特徴マップから入力画像へ',
                 fontsize=16, fontweight='bold', y=0.98)

    # === 左パネル: 特徴マップ (26x26) ===
    ax1 = axes[0]
    ax1.set_xlim(0, 26)
    ax1.set_ylim(0, 26)
    ax1.set_aspect('equal')
    ax1.set_title('特徴マップ (26×26)', fontsize=14, fontweight='bold')

    # グリッドを描画
    for i in range(27):
        ax1.axhline(y=i, color='lightgray', linewidth=0.5)
        ax1.axvline(x=i, color='lightgray', linewidth=0.5)

    # パッチ位置（特徴マップ上で2-3セル程度）
    patch_fm = Rectangle((10, 10), 3, 3, fill=True,
                          facecolor='red', alpha=0.6, edgecolor='darkred', linewidth=2)
    ax1.add_patch(patch_fm)

    # マスク（検出されたセル - 少しずれている）
    mask_fm = Rectangle((11, 11), 2, 2, fill=True,
                         facecolor='blue', alpha=0.4, edgecolor='darkblue', linewidth=2)
    ax1.add_patch(mask_fm)

    ax1.text(13, 7, 'パッチ\n(実際)', ha='center', va='top', fontsize=10, color='darkred')
    ax1.text(13, 15, 'マスク\n(検出)', ha='center', va='bottom', fontsize=10, color='darkblue')
    ax1.set_xlabel('1セル = 1単位', fontsize=10)
    ax1.invert_yaxis()

    # 軸の目盛り
    ax1.set_xticks([0, 13, 26])
    ax1.set_yticks([0, 13, 26])

    # === 中央パネル: スケーリング説明 ===
    ax2 = axes[1]
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')
    ax2.set_title('スケーリング係数', fontsize=14, fontweight='bold')

    # 大きな矢印
    arrow = FancyArrowPatch((2, 5), (8, 5),
                            arrowstyle='->', mutation_scale=30,
                            color='#333333', linewidth=4)
    ax2.add_patch(arrow)

    # スケール倍率
    ax2.text(5, 6.5, '×16', ha='center', va='center',
             fontsize=36, fontweight='bold', color='#E74C3C')

    # 説明テキスト
    ax2.text(5, 3.5, '416 ÷ 26 = 16', ha='center', va='center',
             fontsize=14, family='monospace')
    ax2.text(5, 2, '1セル → 16×16ピクセル', ha='center', va='center',
             fontsize=12)

    # === 右パネル: 入力画像 (416x416) ===
    ax3 = axes[2]
    ax3.set_xlim(0, 416)
    ax3.set_ylim(0, 416)
    ax3.set_aspect('equal')
    ax3.set_title('入力画像 (416×416)', fontsize=14, fontweight='bold')

    # 背景をグレーに
    bg = Rectangle((0, 0), 416, 416, fill=True, facecolor='#f0f0f0', edgecolor='black')
    ax3.add_patch(bg)

    # 16x16グリッドの一部を描画（セル境界を示す）
    for i in range(0, 417, 16):
        ax3.axhline(y=i, color='lightgray', linewidth=0.3, alpha=0.5)
        ax3.axvline(x=i, color='lightgray', linewidth=0.3, alpha=0.5)

    # パッチの実際位置 (10*16=160, サイズ3*16=48)
    patch_img = Rectangle((160, 160), 48, 48, fill=True,
                           facecolor='red', alpha=0.6, edgecolor='darkred', linewidth=2)
    ax3.add_patch(patch_img)

    # マスクの位置 (11*16=176, サイズ2*16=32) - ずれている
    mask_img = Rectangle((176, 176), 32, 32, fill=True,
                          facecolor='blue', alpha=0.4, edgecolor='darkblue', linewidth=2)
    ax3.add_patch(mask_img)

    # ずれを強調する矢印
    ax3.annotate('', xy=(192, 240), xytext=(184, 208),
                arrowprops=dict(arrowstyle='->', color='orange', lw=2))
    ax3.text(200, 250, 'ずれ発生！\n(16px誤差)', ha='left', va='top',
             fontsize=10, color='#E67E22', fontweight='bold')

    ax3.text(184, 145, 'パッチ (48×48px)', ha='center', va='bottom',
             fontsize=10, color='darkred')
    ax3.text(192, 220, 'マスク (32×32px)', ha='center', va='top',
             fontsize=10, color='darkblue')

    ax3.set_xlabel('ピクセル', fontsize=10)
    ax3.invert_yaxis()

    # 軸の目盛り
    ax3.set_xticks([0, 160, 208, 416])
    ax3.set_yticks([0, 160, 208, 416])

    # 凡例
    legend_elements = [
        mpatches.Patch(facecolor='red', alpha=0.6, edgecolor='darkred', label='実際のパッチ'),
        mpatches.Patch(facecolor='blue', alpha=0.4, edgecolor='darkblue', label='検出されたマスク')
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=2,
               fontsize=11, frameon=True, bbox_to_anchor=(0.5, 0.02))

    # 下部に結論テキスト
    fig.text(0.5, 0.08,
             '問題: 低解像度の特徴マップではパッチ境界を正確に特定できない',
             ha='center', va='bottom', fontsize=12,
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    plt.tight_layout(rect=[0, 0.12, 1, 0.95])

    output_path = os.path.join(OUTPUT_DIR, 'resolution_mismatch.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"Created: {output_path}")

def create_cause_chain_figure():
    """因果連鎖図を作成"""

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    fig.suptitle('因果連鎖: なぜパッチが残存するのか',
                 fontsize=16, fontweight='bold', y=0.95)

    # ノード定義（上から下へ）
    nodes = [
        ('低解像度\n特徴マップ\n(26×26)', 5, 9, '#FF6B6B', '原因1'),
        ('粗いマスク\n生成', 5, 7, '#FFA94D', None),
        ('マスクとパッチの\nずれ', 5, 5, '#FFD43B', '原因2'),
        ('部分的な\nインペインティング', 5, 3, '#69DB7C', None),
        ('パッチテクスチャ\nが残存', 5, 1, '#4DABF7', '結果'),
    ]

    # ノードを描画
    for label, x, y, color, annotation in nodes:
        box = FancyBboxPatch((x-1.8, y-0.6), 3.6, 1.2,
                             boxstyle="round,pad=0.05,rounding_size=0.2",
                             facecolor=color, alpha=0.7,
                             edgecolor='#333333', linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center',
                fontsize=11, fontweight='bold')

        if annotation:
            ax.text(x+2.2, y, annotation, ha='left', va='center',
                    fontsize=10, color='#666666')

    # 矢印を描画
    for i in range(len(nodes)-1):
        y1 = nodes[i][2] - 0.6
        y2 = nodes[i+1][2] + 0.6
        ax.annotate('', xy=(5, y2), xytext=(5, y1),
                   arrowprops=dict(arrowstyle='->', color='#333333', lw=2))

    # 右側に原因3を追加（別枠）
    box3 = FancyBboxPatch((7, 2.4), 2.5, 1.2,
                          boxstyle="round,pad=0.05,rounding_size=0.2",
                          facecolor='#E599F7', alpha=0.7,
                          edgecolor='#333333', linewidth=2)
    ax.add_patch(box3)
    ax.text(8.25, 3, 'Biharmonic\nの限界', ha='center', va='center',
            fontsize=10, fontweight='bold')
    ax.text(8.25, 1.8, '原因3', ha='center', va='top',
            fontsize=10, color='#666666')

    # 原因3への矢印
    ax.annotate('', xy=(6.8, 3), xytext=(5.5, 3),
               arrowprops=dict(arrowstyle='->', color='#333333', lw=1.5,
                              connectionstyle='arc3,rad=0.3'))

    # 下部の結論
    ax.text(5, -0.3, '根本原因: 検出パイプラインのアーキテクチャ的制約',
            ha='center', va='top', fontsize=11, color='#495057')

    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, 'cause_chain.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"Created: {output_path}")

if __name__ == '__main__':
    create_resolution_mismatch_figure()
    create_cause_chain_figure()
    print("\n=== All figures generated ===")
