#!/usr/bin/env python3
"""
LaTeX表をPNG画像に変換するスクリプト
docs/latex_tables.tex の内容をmatplotlibで描画
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

# 出力ディレクトリ
OUTPUT_DIR = "docs/slides_material/tables"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# フォント設定
plt.rcParams['font.size'] = 11
plt.rcParams['figure.facecolor'] = 'white'

def create_table_image(data, col_labels, filename, title=None, figsize=(8, 2.5)):
    """表データから画像を生成"""
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')

    # 表を作成
    table = ax.table(
        cellText=data,
        colLabels=col_labels,
        loc='center',
        cellLoc='center'
    )

    # スタイル設定
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)

    # ヘッダー行のスタイル
    for j in range(len(col_labels)):
        cell = table[(0, j)]
        cell.set_facecolor('#4472C4')
        cell.set_text_props(color='white', weight='bold')

    # データ行の背景色（交互）
    for i in range(1, len(data) + 1):
        for j in range(len(col_labels)):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor('#D6DCE5')
            else:
                cell.set_facecolor('#FFFFFF')

    if title:
        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)

    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(filepath, dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none', pad_inches=0.1)
    plt.close()
    print(f"Created: {filepath}")

# === Slide 5: データセット・モデル ===
data1 = [
    ['Object Detection', 'INRIA, VOC', 'YOLOv2'],
    ['Classification', 'ImageNet, CIFAR-10', 'ResNet-50'],
]
col_labels1 = ['Task', 'Dataset', 'Model']
create_table_image(data1, col_labels1, 'table_slide5_dataset.png', figsize=(7, 1.5))

# === Slide 5: パラメータ ===
data2 = [
    ['Ensemble size |B|', '20'],
    ['Inpainting', 'biharmonic'],
    ['Detection threshold α*', '0.5'],
]
col_labels2 = ['Parameter', 'Value']
create_table_image(data2, col_labels2, 'table_slide5_params.png', figsize=(5, 1.8))

# === Slide 6: Recovery Rate ===
data3 = [
    ['VOC', '1-patch', '0.540', '0.538', '-0.002'],
    ['VOC', '2-patch', '0.538', '0.526', '-0.012'],
    ['INRIA', '1-patch', '0.591', '0.792', '+0.201'],
    ['CIFAR', '1-patch', '0.974', '0.929', '-0.045'],
    ['ImageNet', '1-patch', '0.887', '0.867', '-0.020'],
]
col_labels3 = ['Dataset', 'Attack', 'Paper', 'Repro', 'Diff']
create_table_image(data3, col_labels3, 'table_slide6_rr.png', figsize=(8, 3))

# === Slide 7: nmAP ===
data4 = [
    ['VOC 1p', 'Adv. nmAP', '0.509', '0.694'],
    ['VOC 1p', 'Clean nmAP', '0.995', '1.000'],
    ['INRIA 1p', 'Adv. nmAP', '0.690', '0.789'],
    ['INRIA 1p', 'Clean nmAP', '1.000', '1.000'],
]
col_labels4 = ['Dataset', 'Metric', 'Paper', 'Repro']
create_table_image(data4, col_labels4, 'table_slide7_nmap.png', figsize=(7, 2.5))

# === Slide 8: 計算時間比較 ===
data5 = [
    ['VOC', '4', '0.30s', '0.07s', '23%'],
    ['VOC', '20', '1.50s', '0.46s', '30%'],
    ['INRIA', '20', '1.50s', '0.41s', '27%'],
]
col_labels5 = ['Dataset', '|B|', 'Paper', 'Measured', 'Ratio']
create_table_image(data5, col_labels5, 'table_slide8_timing.png', figsize=(8, 2))

# === Slide 12: 結論 ===
data6 = [
    ['Recovery Rate', 'Reproduced (VOC ±2%)'],
    ['nmAP', 'Reproduced (higher values)'],
    ['Computation Time', '23-30% of paper'],
]
col_labels6 = ['Metric', 'Result']
create_table_image(data6, col_labels6, 'table_slide12_conclusion.png', figsize=(6, 1.8))

print("\n=== All table images generated ===")
