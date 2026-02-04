#!/usr/bin/env python3
"""
IoUと回復成功判定の説明図を作成
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


def create_iou_explanation_figure():
    """IoUの説明図を作成"""

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle('IoU (Intersection over Union) の計算', fontsize=16, fontweight='bold', y=0.98)

    # === 左パネル: 2つのボックス ===
    ax1 = axes[0]
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, 100)
    ax1.set_aspect('equal')
    ax1.set_title('2つのボックス', fontsize=14, fontweight='bold')

    # 正解ボックス（緑）
    gt_box = Rectangle((20, 30), 40, 40, fill=True,
                        facecolor='green', alpha=0.5, edgecolor='darkgreen', linewidth=3)
    ax1.add_patch(gt_box)

    # 予測ボックス（青）
    pred_box = Rectangle((35, 40), 40, 40, fill=True,
                          facecolor='blue', alpha=0.5, edgecolor='darkblue', linewidth=3)
    ax1.add_patch(pred_box)

    ax1.text(40, 20, '正解ボックス', ha='center', va='top', fontsize=11, color='darkgreen', fontweight='bold')
    ax1.text(55, 90, '予測ボックス', ha='center', va='bottom', fontsize=11, color='darkblue', fontweight='bold')
    ax1.axis('off')

    # === 中央パネル: 重なり部分 ===
    ax2 = axes[1]
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 100)
    ax2.set_aspect('equal')
    ax2.set_title('重なり部分 (A ∩ B)', fontsize=14, fontweight='bold')

    # 重なり部分のみ表示（赤）
    intersection = Rectangle((35, 40), 25, 30, fill=True,
                              facecolor='red', alpha=0.7, edgecolor='darkred', linewidth=3)
    ax2.add_patch(intersection)

    # 元のボックスの輪郭
    gt_outline = Rectangle((20, 30), 40, 40, fill=False, edgecolor='darkgreen', linewidth=2, linestyle='--')
    pred_outline = Rectangle((35, 40), 40, 40, fill=False, edgecolor='darkblue', linewidth=2, linestyle='--')
    ax2.add_patch(gt_outline)
    ax2.add_patch(pred_outline)

    ax2.text(47, 55, '重なり\n(Intersection)', ha='center', va='center', fontsize=10, color='white', fontweight='bold')
    ax2.axis('off')

    # === 右パネル: 合計面積 ===
    ax3 = axes[2]
    ax3.set_xlim(0, 100)
    ax3.set_ylim(0, 100)
    ax3.set_aspect('equal')
    ax3.set_title('合計面積 (A ∪ B)', fontsize=14, fontweight='bold')

    # 合計面積（両方のボックスを合わせた領域）
    gt_box2 = Rectangle((20, 30), 40, 40, fill=True,
                         facecolor='orange', alpha=0.6, edgecolor='darkorange', linewidth=3)
    pred_box2 = Rectangle((35, 40), 40, 40, fill=True,
                           facecolor='orange', alpha=0.6, edgecolor='darkorange', linewidth=3)
    ax3.add_patch(gt_box2)
    ax3.add_patch(pred_box2)

    ax3.text(50, 55, '合計\n(Union)', ha='center', va='center', fontsize=10, color='black', fontweight='bold')
    ax3.axis('off')

    # 下部に計算式
    fig.text(0.5, 0.08,
             'IoU = 重なり面積 / 合計面積 = (A ∩ B) / (A ∪ B)    |    IoU ≥ 0.5 → 正しい検出',
             ha='center', va='bottom', fontsize=13, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))

    plt.tight_layout(rect=[0, 0.12, 1, 0.95])

    output_path = os.path.join(OUTPUT_DIR, 'iou_explanation.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print(f"Created: {output_path}")


def create_recovery_evaluation_figure():
    """回復成功判定の説明図を作成"""

    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    fig.suptitle('Recovery Rate の評価方法', fontsize=16, fontweight='bold', y=0.98)

    # === 左パネル: Clean画像の検出 ===
    ax1 = axes[0]
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, 100)
    ax1.set_aspect('equal')
    ax1.set_title('① Clean画像の検出\n（正解）', fontsize=12, fontweight='bold')

    # 背景
    bg1 = Rectangle((0, 0), 100, 100, fill=True, facecolor='#f5f5f5', edgecolor='black', linewidth=2)
    ax1.add_patch(bg1)

    # 人物（正解ボックス）
    person_gt = Rectangle((30, 20), 30, 60, fill=True,
                           facecolor='green', alpha=0.3, edgecolor='green', linewidth=3)
    ax1.add_patch(person_gt)
    ax1.text(45, 50, '人物', ha='center', va='center', fontsize=12, fontweight='bold')

    ax1.text(50, 5, '検出数: 1', ha='center', va='bottom', fontsize=11,
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    ax1.axis('off')

    # === 中央パネル: Attacked画像 ===
    ax2 = axes[1]
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 100)
    ax2.set_aspect('equal')
    ax2.set_title('② Attacked画像の検出\n（攻撃成功）', fontsize=12, fontweight='bold')

    # 背景
    bg2 = Rectangle((0, 0), 100, 100, fill=True, facecolor='#f5f5f5', edgecolor='black', linewidth=2)
    ax2.add_patch(bg2)

    # パッチ
    patch = Rectangle((35, 35), 20, 20, fill=True,
                       facecolor='red', alpha=0.8, edgecolor='darkred', linewidth=2)
    ax2.add_patch(patch)
    ax2.text(45, 45, 'パッチ', ha='center', va='center', fontsize=10, color='white', fontweight='bold')

    # 人物は検出されない（点線で表示）
    person_miss = Rectangle((30, 20), 30, 60, fill=False,
                             edgecolor='gray', linewidth=2, linestyle='--')
    ax2.add_patch(person_miss)
    ax2.text(45, 50, '検出\nされない', ha='center', va='center', fontsize=10, color='gray')

    ax2.text(50, 5, '検出数: 0', ha='center', va='bottom', fontsize=11,
             bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))
    ax2.axis('off')

    # === 右パネル: Recovered画像 ===
    ax3 = axes[2]
    ax3.set_xlim(0, 100)
    ax3.set_ylim(0, 100)
    ax3.set_aspect('equal')
    ax3.set_title('③ Recovered画像の検出\n（回復判定）', fontsize=12, fontweight='bold')

    # 背景
    bg3 = Rectangle((0, 0), 100, 100, fill=True, facecolor='#f5f5f5', edgecolor='black', linewidth=2)
    ax3.add_patch(bg3)

    # ぼやけたパッチ領域
    patch_blur = Rectangle((35, 35), 20, 20, fill=True,
                            facecolor='#cccccc', alpha=0.5, edgecolor='gray', linewidth=1)
    ax3.add_patch(patch_blur)

    # 正解ボックス（緑の点線）
    person_gt2 = Rectangle((30, 20), 30, 60, fill=False,
                            edgecolor='green', linewidth=3, linestyle='--')
    ax3.add_patch(person_gt2)

    # 検出されたボックス（人物 - IoU高い）
    person_det = Rectangle((32, 22), 28, 56, fill=True,
                            facecolor='blue', alpha=0.3, edgecolor='blue', linewidth=3)
    ax3.add_patch(person_det)
    ax3.text(46, 50, '人物\nIoU=0.8', ha='center', va='center', fontsize=10, color='darkblue', fontweight='bold')

    # 余分な検出ボックス1（車）
    extra1 = Rectangle((5, 60), 20, 15, fill=True,
                        facecolor='orange', alpha=0.4, edgecolor='orange', linewidth=2)
    ax3.add_patch(extra1)
    ax3.text(15, 67, '車?', ha='center', va='center', fontsize=9, color='darkorange')

    # 余分な検出ボックス2（犬）
    extra2 = Rectangle((70, 10), 25, 20, fill=True,
                        facecolor='orange', alpha=0.4, edgecolor='orange', linewidth=2)
    ax3.add_patch(extra2)
    ax3.text(82, 20, '犬?', ha='center', va='center', fontsize=9, color='darkorange')

    ax3.text(50, 5, '検出数: 3（人物+余分2）', ha='center', va='bottom', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    ax3.axis('off')

    # 凡例
    legend_elements = [
        mpatches.Patch(facecolor='green', alpha=0.3, edgecolor='green', linewidth=2, label='正解ボックス'),
        mpatches.Patch(facecolor='blue', alpha=0.3, edgecolor='blue', linewidth=2, label='検出ボックス（人物）'),
        mpatches.Patch(facecolor='orange', alpha=0.4, edgecolor='orange', linewidth=2, label='余分な検出（無視される）'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=3,
               fontsize=10, frameon=True, bbox_to_anchor=(0.5, 0.02))

    # 判定結果のテキスト
    fig.text(0.5, 0.12,
             '判定: 正解（人物）のIoU ≥ 0.5 → 回復成功 ✓    ※余分な検出は評価に影響しない',
             ha='center', va='bottom', fontsize=12, fontweight='bold',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.9))

    plt.tight_layout(rect=[0, 0.18, 1, 0.95])

    output_path = os.path.join(OUTPUT_DIR, 'recovery_evaluation.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print(f"Created: {output_path}")


def create_evaluation_logic_figure():
    """評価ロジックのフロー図を作成"""

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')

    fig.suptitle('Recovery Rate 評価ロジック', fontsize=16, fontweight='bold', y=0.95)

    # ノード定義
    nodes = [
        ('各正解ボックスに\nついてループ', 6, 9, '#AED6F1', 2.2),
        ('対応する検出ボックスを\n探す（IoU計算）', 6, 7, '#F9E79F', 2.4),
        ('最大IoU ≥ 0.5?', 6, 5, '#F5B7B1', 2.0),
    ]

    # メインノードを描画
    for label, x, y, color, width in nodes:
        box = FancyBboxPatch((x-width, y-0.5), width*2, 1.0,
                             boxstyle="round,pad=0.05,rounding_size=0.2",
                             facecolor=color, alpha=0.8,
                             edgecolor='#333333', linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', fontsize=11, fontweight='bold')

    # 矢印（メインフロー）
    ax.annotate('', xy=(6, 7.5), xytext=(6, 8.5),
                arrowprops=dict(arrowstyle='->', color='#333333', lw=2))
    ax.annotate('', xy=(6, 5.5), xytext=(6, 6.5),
                arrowprops=dict(arrowstyle='->', color='#333333', lw=2))

    # Yes分岐（右へ）
    ax.annotate('', xy=(9.5, 5), xytext=(8, 5),
                arrowprops=dict(arrowstyle='->', color='green', lw=2))
    ax.text(8.7, 5.3, 'Yes', fontsize=10, color='green', fontweight='bold')

    # Yes の先（次のボックスへ）
    next_box = FancyBboxPatch((9.5, 4.5), 2.0, 1.0,
                               boxstyle="round,pad=0.05,rounding_size=0.2",
                               facecolor='#D5F5E3', alpha=0.8,
                               edgecolor='#333333', linewidth=2)
    ax.add_patch(next_box)
    ax.text(10.5, 5, '次の正解\nボックスへ', ha='center', va='center', fontsize=10, fontweight='bold')

    # 次へのループ矢印
    ax.annotate('', xy=(10.5, 8.5), xytext=(10.5, 5.5),
                arrowprops=dict(arrowstyle='->', color='#333333', lw=1.5,
                               connectionstyle='arc3,rad=-0.3'))

    # No分岐（下へ）
    ax.annotate('', xy=(6, 3.5), xytext=(6, 4.5),
                arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax.text(6.3, 4.0, 'No', fontsize=10, color='red', fontweight='bold')

    # 失敗ノード
    fail_box = FancyBboxPatch((4.5, 2.5), 3.0, 1.0,
                               boxstyle="round,pad=0.05,rounding_size=0.2",
                               facecolor='#F1948A', alpha=0.8,
                               edgecolor='darkred', linewidth=3)
    ax.add_patch(fail_box)
    ax.text(6, 3, '回復失敗 ✗', ha='center', va='center', fontsize=12, fontweight='bold', color='darkred')

    # 全てYesの場合（成功）
    success_box = FancyBboxPatch((9, 1.5), 2.5, 1.0,
                                  boxstyle="round,pad=0.05,rounding_size=0.2",
                                  facecolor='#82E0AA', alpha=0.8,
                                  edgecolor='darkgreen', linewidth=3)
    ax.add_patch(success_box)
    ax.text(10.25, 2, '回復成功 ✓', ha='center', va='center', fontsize=12, fontweight='bold', color='darkgreen')

    ax.annotate('', xy=(10.25, 2.5), xytext=(10.5, 4.5),
                arrowprops=dict(arrowstyle='->', color='green', lw=1.5))
    ax.text(11, 3.5, '全て\n完了', fontsize=9, color='green')

    # 左側に注釈
    ax.text(1, 7, '評価対象:\n正解ボックスのみ', ha='left', va='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray'))

    ax.text(1, 4, '余分な検出:\n評価に含まれない\n（無視される）', ha='left', va='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='#FADBD8', alpha=0.9, edgecolor='gray'))

    # 下部の結論
    ax.text(6, 0.8,
            'Recovery Rate = 回復成功した画像数 / 攻撃が検出された画像数',
            ha='center', va='center', fontsize=12, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))

    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, 'evaluation_logic.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print(f"Created: {output_path}")


if __name__ == '__main__':
    create_iou_explanation_figure()
    create_recovery_evaluation_figure()
    create_evaluation_logic_figure()
    print("\n=== All evaluation figures generated ===")
