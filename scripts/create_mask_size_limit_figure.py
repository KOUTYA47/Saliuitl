#!/usr/bin/env python3
"""
マスクサイズ上限（5.5%）の説明図を作成
Slide 12: 原因分析（2）技術的制約用
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle
import numpy as np
import os

OUTPUT_DIR = "/mnt/d/csprog/ooki/Saliuitl/docs/slides_material"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日本語フォント設定
plt.rcParams['font.family'] = ['Noto Sans JP', 'Yu Gothic', 'Meiryo', 'sans-serif']
plt.rcParams['font.size'] = 11
plt.rcParams['figure.facecolor'] = 'white'


def create_mask_size_limit_figure():
    """5.5%マスクサイズ上限を説明する図"""

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle('マスクサイズ上限: 5.5% の制約', fontsize=16, fontweight='bold', y=0.98)

    # === 左パネル: 計算式の説明 ===
    ax1 = axes[0]
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    ax1.set_title('制約の計算', fontsize=14, fontweight='bold')

    # 背景ボックス
    bg1 = FancyBboxPatch((0.5, 1), 9, 8,
                          boxstyle="round,pad=0.05,rounding_size=0.2",
                          facecolor='#F5F5F5', alpha=0.5,
                          edgecolor='#333333', linewidth=2)
    ax1.add_patch(bg1)

    # 計算式
    ax1.text(5, 8, 'スキップ条件:', ha='center', va='center',
             fontsize=12, fontweight='bold')
    ax1.text(5, 6.8, 'masking > neulim × size / 9', ha='center', va='center',
             fontsize=14, family='monospace',
             bbox=dict(boxstyle='round', facecolor='#FFECB3', alpha=0.8))

    ax1.text(5, 5.5, '↓', ha='center', va='center', fontsize=16)

    ax1.text(5, 4.5, 'neulim = 0.5 (デフォルト)', ha='center', va='center',
             fontsize=11)
    ax1.text(5, 3.8, 'size = 画像ピクセル数', ha='center', va='center',
             fontsize=11)

    ax1.text(5, 2.5, '上限 = 0.5 × size / 9', ha='center', va='center',
             fontsize=13, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='#C8E6C9', alpha=0.8))

    ax1.text(5, 1.5, '≈ 5.56% of image', ha='center', va='center',
             fontsize=14, color='#D32F2F', fontweight='bold')

    # === 中央パネル: 画像サイズの例 ===
    ax2 = axes[1]
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')
    ax2.set_title('具体例: 416×416画像', fontsize=14, fontweight='bold')

    # 背景ボックス
    bg2 = FancyBboxPatch((0.5, 1), 9, 8,
                          boxstyle="round,pad=0.05,rounding_size=0.2",
                          facecolor='#E3F2FD', alpha=0.5,
                          edgecolor='#1976D2', linewidth=2)
    ax2.add_patch(bg2)

    # 計算
    ax2.text(5, 8, '416 × 416 = 173,056 px', ha='center', va='center',
             fontsize=12)
    ax2.text(5, 7, '↓', ha='center', va='center', fontsize=14)
    ax2.text(5, 6, 'マスク上限 = 173,056 × 5.56%', ha='center', va='center',
             fontsize=11)
    ax2.text(5, 5, '≈ 9,614 px', ha='center', va='center',
             fontsize=14, fontweight='bold', color='#1976D2')
    ax2.text(5, 4, '↓', ha='center', va='center', fontsize=14)
    ax2.text(5, 3, '√9,614 ≈ 98 px', ha='center', va='center',
             fontsize=12)

    # 結論ボックス
    result_box = FancyBboxPatch((1, 1.2), 8, 1.3,
                                 boxstyle="round,pad=0.05,rounding_size=0.2",
                                 facecolor='#FFCDD2', alpha=0.8,
                                 edgecolor='#D32F2F', linewidth=2)
    ax2.add_patch(result_box)
    ax2.text(5, 1.85, '約 98×98 px 以上のマスクは\n処理をスキップ',
             ha='center', va='center', fontsize=11, fontweight='bold', color='#C62828')

    # === 右パネル: 視覚的な比較 ===
    ax3 = axes[2]
    ax3.set_xlim(0, 416)
    ax3.set_ylim(0, 416)
    ax3.set_aspect('equal')
    ax3.set_title('画像に対するマスク上限', fontsize=14, fontweight='bold')

    # 背景（画像を表す）
    bg_img = Rectangle((0, 0), 416, 416, fill=True,
                        facecolor='#E0E0E0', edgecolor='black', linewidth=2)
    ax3.add_patch(bg_img)

    # 5.5%の正方形マスク（約98x98）
    mask_size = 98
    mask_x = (416 - mask_size) / 2
    mask_y = (416 - mask_size) / 2

    # 上限サイズのマスク（緑）
    ok_mask = Rectangle((mask_x, mask_y), mask_size, mask_size, fill=True,
                         facecolor='#4CAF50', alpha=0.6, edgecolor='#2E7D32', linewidth=3)
    ax3.add_patch(ok_mask)
    ax3.text(208, 208, '上限\n98×98', ha='center', va='center',
             fontsize=12, fontweight='bold', color='white')

    # 大きなパッチの例（赤い破線）
    large_patch_size = 150
    large_x = (416 - large_patch_size) / 2
    large_y = (416 - large_patch_size) / 2
    large_patch = Rectangle((large_x, large_y), large_patch_size, large_patch_size, fill=False,
                             edgecolor='#D32F2F', linewidth=3, linestyle='--')
    ax3.add_patch(large_patch)
    ax3.text(208, large_y - 20, '大きいパッチ\n(150×150) → スキップ',
             ha='center', va='top', fontsize=10, color='#D32F2F', fontweight='bold')

    # ラベル
    ax3.text(208, 400, '416×416 画像', ha='center', va='bottom',
             fontsize=11, color='#333333')

    ax3.set_xticks([0, 98, 208, 318, 416])
    ax3.set_yticks([0, 98, 208, 318, 416])
    ax3.invert_yaxis()

    # 凡例
    legend_elements = [
        mpatches.Patch(facecolor='#4CAF50', alpha=0.6, edgecolor='#2E7D32', label='処理可能 (≤5.5%)'),
        mpatches.Patch(facecolor='none', edgecolor='#D32F2F', linestyle='--', linewidth=2, label='スキップ (>5.5%)')
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=2,
               fontsize=11, frameon=True, bbox_to_anchor=(0.5, 0.02))

    # 下部の結論
    fig.text(0.5, 0.08,
             '結論: パッチが画像の5.5%を超えると、そのβ閾値での回復処理はスキップされる',
             ha='center', va='bottom', fontsize=12,
             bbox=dict(boxstyle='round', facecolor='#FFF9C4', alpha=0.9, edgecolor='#F9A825'))

    plt.tight_layout(rect=[0, 0.12, 1, 0.95])

    output_path = os.path.join(OUTPUT_DIR, 'mask_size_limit.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"Created: {output_path}")


def create_skip_flow_figure():
    """スキップ条件のフロー図"""

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')

    fig.suptitle('マスクサイズによる処理フロー', fontsize=16, fontweight='bold', y=0.95)

    # ステップ1: マスク生成
    box1 = FancyBboxPatch((0.5, 5), 2.5, 1.5,
                          boxstyle="round,pad=0.05,rounding_size=0.2",
                          facecolor='#E3F2FD', alpha=0.8,
                          edgecolor='#1976D2', linewidth=2)
    ax.add_patch(box1)
    ax.text(1.75, 5.75, 'β閾値で\nマスク生成', ha='center', va='center', fontsize=10)

    # 矢印
    ax.annotate('', xy=(3.5, 5.75), xytext=(3.1, 5.75),
               arrowprops=dict(arrowstyle='->', color='black', lw=2))

    # ステップ2: サイズチェック（ひし形）
    diamond_x = [4.5, 5.5, 6.5, 5.5]
    diamond_y = [5.75, 6.75, 5.75, 4.75]
    diamond = plt.Polygon(list(zip(diamond_x, diamond_y)), fill=True,
                          facecolor='#FFF9C4', edgecolor='#F9A825', linewidth=2)
    ax.add_patch(diamond)
    ax.text(5.5, 5.75, 'size >\n5.5%?', ha='center', va='center', fontsize=9, fontweight='bold')

    # Yes分岐（上）→ スキップ
    ax.annotate('', xy=(5.5, 7.5), xytext=(5.5, 6.8),
               arrowprops=dict(arrowstyle='->', color='#D32F2F', lw=2))
    ax.text(5.8, 7.1, 'Yes', ha='left', va='center', fontsize=10, color='#D32F2F')

    skip_box = FancyBboxPatch((4, 7.5), 3, 1,
                              boxstyle="round,pad=0.05,rounding_size=0.2",
                              facecolor='#FFCDD2', alpha=0.8,
                              edgecolor='#D32F2F', linewidth=2)
    ax.add_patch(skip_box)
    ax.text(5.5, 8, 'この閾値をスキップ\n(continue)', ha='center', va='center',
            fontsize=10, color='#C62828', fontweight='bold')

    # No分岐（右）→ インペインティング
    ax.annotate('', xy=(7.5, 5.75), xytext=(6.6, 5.75),
               arrowprops=dict(arrowstyle='->', color='#2E7D32', lw=2))
    ax.text(7, 6, 'No', ha='center', va='bottom', fontsize=10, color='#2E7D32')

    inpaint_box = FancyBboxPatch((7.5, 5), 2.5, 1.5,
                                 boxstyle="round,pad=0.05,rounding_size=0.2",
                                 facecolor='#C8E6C9', alpha=0.8,
                                 edgecolor='#2E7D32', linewidth=2)
    ax.add_patch(inpaint_box)
    ax.text(8.75, 5.75, 'Biharmonic\nインペインティング', ha='center', va='center',
            fontsize=10, color='#1B5E20', fontweight='bold')

    # 矢印 → 検出
    ax.annotate('', xy=(10.5, 5.75), xytext=(10.1, 5.75),
               arrowprops=dict(arrowstyle='->', color='black', lw=2))

    detect_box = FancyBboxPatch((10.5, 5), 2, 1.5,
                                boxstyle="round,pad=0.05,rounding_size=0.2",
                                facecolor='#E1BEE7', alpha=0.8,
                                edgecolor='#7B1FA2', linewidth=2)
    ax.add_patch(detect_box)
    ax.text(11.5, 5.75, '物体検出\n実行', ha='center', va='center',
            fontsize=10, color='#4A148C', fontweight='bold')

    # 下部: 繰り返しの矢印
    ax.annotate('', xy=(1.75, 4.2), xytext=(11.5, 4.2),
               arrowprops=dict(arrowstyle='<-', color='gray', lw=1.5,
                              connectionstyle='arc3,rad=0.3'))
    ax.text(6.5, 3.5, '次のβ閾値へ (β=0.99 → 0.95 → ... → 0.05)',
            ha='center', va='center', fontsize=10, color='gray')

    # 注記
    ax.text(6, 1.5, '※ 大きなパッチ (>5.5%) は全てのβ閾値でスキップされる可能性\n'
                    '   → 回復処理が一度も実行されない場合がある',
            ha='center', va='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='#FFECB3', alpha=0.9, edgecolor='#FF8F00'))

    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, 'mask_size_skip_flow.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"Created: {output_path}")


if __name__ == '__main__':
    create_mask_size_limit_figure()
    create_skip_flow_figure()
    print("\n=== All mask size limit figures generated ===")
