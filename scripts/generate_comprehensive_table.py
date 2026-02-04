#!/usr/bin/env python3
"""
全実験結果を含む包括的な表を生成するスクリプト
RESULT_LOG.md の R-2026-02-01 から15クラスの結果を表示
順番: INRIA → VOC → ImageNet → CIFAR
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

# 出力ディレクトリ
OUTPUT_DIR = "/mnt/d/csprog/ooki/Saliuitl/docs/slides_material/tables"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# フォント設定
plt.rcParams['font.size'] = 10
plt.rcParams['figure.facecolor'] = 'white'

def create_comprehensive_table(data, col_labels, filename, title=None,
                                figsize=(12, 8), group_colors=None):
    """包括的な表を生成"""
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
    table.set_fontsize(9)
    table.scale(1.2, 1.6)

    # ヘッダー行のスタイル
    for j in range(len(col_labels)):
        cell = table[(0, j)]
        cell.set_facecolor('#4472C4')
        cell.set_text_props(color='white', weight='bold')

    # データ行の背景色（データセットごとにグループ化）
    if group_colors:
        for i, (row, color) in enumerate(zip(data, group_colors), start=1):
            for j in range(len(col_labels)):
                cell = table[(i, j)]
                cell.set_facecolor(color)
    else:
        for i in range(1, len(data) + 1):
            for j in range(len(col_labels)):
                cell = table[(i, j)]
                if i % 2 == 0:
                    cell.set_facecolor('#D6DCE5')
                else:
                    cell.set_facecolor('#FFFFFF')

    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)

    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(filepath, dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none', pad_inches=0.15)
    plt.close()
    print(f"Created: {filepath}")
    return filepath

def diff_percent(paper, repro):
    """差分を%形式で計算"""
    diff = repro - paper
    if diff >= 0:
        return f"+{diff*100:.1f}%"
    else:
        return f"{diff*100:.1f}%"

# ============================================================
# データ定義（RESULT_LOG.md R-2026-02-01より）
# 順番: INRIA → VOC → ImageNet → CIFAR
# ============================================================

# 生データ: [Dataset, Attack, Paper RR, Repro RR]
raw_data = [
    # INRIA (3 classes)
    ['INRIA', '1-patch', 0.5909, 0.7917],
    ['INRIA', '2-patch', 0.3871, 0.8571],
    ['INRIA', 'trig', 0.4737, 0.3636],
    # VOC (4 classes)
    ['VOC', '1-patch', 0.5404, 0.5385],
    ['VOC', '2-patch', 0.5376, 0.5263],
    ['VOC', 'trig', 0.4244, 0.1500],
    ['VOC', 'mo', 0.3955, 0.2593],
    # ImageNet (4 classes)
    ['ImageNet', '1-patch', 0.8869, 0.8667],
    ['ImageNet', '2-patch', 0.8535, 0.6667],
    ['ImageNet', '4-patch', 0.8436, 0.4667],
    ['ImageNet', 'trig', 0.5065, 0.4000],
    # CIFAR (4 classes)
    ['CIFAR', '1-patch', 0.9738, 0.9286],
    ['CIFAR', '2-patch', 0.9789, 0.8000],
    ['CIFAR', '4-patch', 0.9747, 0.9333],
    ['CIFAR', 'trig', 0.8566, 0.8667],
]

# 表示用データに変換
recovery_data = []
for row in raw_data:
    dataset, attack, paper, repro = row
    recovery_data.append([
        dataset,
        attack,
        f"{paper:.4f}",
        f"{repro:.4f}",
        diff_percent(paper, repro)
    ])

# データセットごとの色分け
colors = (
    ['#E8F5E9'] * 3 +  # INRIA: 薄い緑
    ['#FCE4EC'] * 4 +  # VOC: 薄いピンク
    ['#FFF3E0'] * 4 +  # ImageNet: 薄いオレンジ
    ['#E8F4FD'] * 4    # CIFAR: 薄い青
)

col_labels_rr = ['Dataset', 'Attack', 'Paper RR', 'Repro RR', 'Diff']

create_comprehensive_table(
    recovery_data,
    col_labels_rr,
    'comprehensive_recovery_rate_full.png',
    title='Table 1: Recovery Rate Results (All 15 Experiment Classes)',
    figsize=(10, 7),
    group_colors=colors
)

# ============================================================
# タスク別に分離した表
# ============================================================

# Detection (INRIA + VOC = 7 classes)
detection_data = []
for row in raw_data[:7]:  # INRIA (3) + VOC (4)
    dataset, attack, paper, repro = row
    detection_data.append([
        dataset,
        attack,
        f"{paper:.4f}",
        f"{repro:.4f}",
        diff_percent(paper, repro)
    ])

colors_det = ['#E8F5E9'] * 3 + ['#FCE4EC'] * 4

create_comprehensive_table(
    detection_data,
    ['Dataset', 'Attack', 'Paper RR', 'Repro RR', 'Diff'],
    'comprehensive_rr_detection.png',
    title='Table 1a: Recovery Rate - Object Detection (7 Classes)',
    figsize=(9, 4),
    group_colors=colors_det
)

# Classification (ImageNet + CIFAR = 8 classes)
classification_data = []
for row in raw_data[7:]:  # ImageNet (4) + CIFAR (4)
    dataset, attack, paper, repro = row
    classification_data.append([
        dataset,
        attack,
        f"{paper:.4f}",
        f"{repro:.4f}",
        diff_percent(paper, repro)
    ])

colors_cls = ['#FFF3E0'] * 4 + ['#E8F4FD'] * 4

create_comprehensive_table(
    classification_data,
    ['Dataset', 'Attack', 'Paper RR', 'Repro RR', 'Diff'],
    'comprehensive_rr_classification.png',
    title='Table 1b: Recovery Rate - Classification (8 Classes)',
    figsize=(9, 4.5),
    group_colors=colors_cls
)

# ============================================================
# Table 2: nmAP (Object Detection only)
# ============================================================

nmap_data = [
    ['INRIA', '1-patch', 'Adv. nmAP', '0.6897', '0.7886', '+9.9%'],
    ['INRIA', '1-patch', 'Clean nmAP', '0.9998', '1.0000', '+0.0%'],
    ['VOC', '1-patch', 'Adv. nmAP', '0.5094', '0.6938', '+18.4%'],
    ['VOC', '1-patch', 'Clean nmAP', '0.9950', '1.0000', '+0.5%'],
]

colors_nmap = ['#E8F5E9', '#E8F5E9', '#FCE4EC', '#FCE4EC']

create_comprehensive_table(
    nmap_data,
    ['Dataset', 'Attack', 'Metric', 'Paper', 'Repro', 'Diff'],
    'comprehensive_nmap.png',
    title='Table 2: nmAP Results (Object Detection)',
    figsize=(10, 3),
    group_colors=colors_nmap
)

# ============================================================
# LaTeX形式の表を出力
# ============================================================

latex_output = r"""% ============================================================
% Table 1: Recovery Rate (All 15 Classes)
% 順番: INRIA → VOC → ImageNet → CIFAR
% ============================================================

\begin{table}[htbp]
\centering
\caption{Recovery Rate Results (All 15 Experiment Classes)}
\label{tab:recovery_rate_full}
\begin{tabular}{llrrr}
\toprule
Dataset & Attack & Paper RR & Repro RR & Diff \\
\midrule
\multicolumn{5}{l}{\textit{Object Detection}} \\
\midrule
INRIA & 1-patch & 0.5909 & 0.7917 & +20.1\% \\
INRIA & 2-patch & 0.3871 & 0.8571 & +47.0\% \\
INRIA & trig & 0.4737 & 0.3636 & -11.0\% \\
\midrule
VOC & 1-patch & 0.5404 & 0.5385 & -0.2\% \\
VOC & 2-patch & 0.5376 & 0.5263 & -1.1\% \\
VOC & trig & 0.4244 & 0.1500 & -27.4\% \\
VOC & mo & 0.3955 & 0.2593 & -13.6\% \\
\midrule
\multicolumn{5}{l}{\textit{Image Classification}} \\
\midrule
ImageNet & 1-patch & 0.8869 & 0.8667 & -2.0\% \\
ImageNet & 2-patch & 0.8535 & 0.6667 & -18.7\% \\
ImageNet & 4-patch & 0.8436 & 0.4667 & -37.7\% \\
ImageNet & trig & 0.5065 & 0.4000 & -10.7\% \\
\midrule
CIFAR & 1-patch & 0.9738 & 0.9286 & -4.5\% \\
CIFAR & 2-patch & 0.9789 & 0.8000 & -17.9\% \\
CIFAR & 4-patch & 0.9747 & 0.9333 & -4.1\% \\
CIFAR & trig & 0.8566 & 0.8667 & +1.0\% \\
\bottomrule
\end{tabular}
\end{table}

% ============================================================
% Table 1a: Recovery Rate - Object Detection (7 Classes)
% ============================================================

\begin{table}[htbp]
\centering
\caption{Recovery Rate - Object Detection (7 Classes)}
\label{tab:recovery_rate_detection}
\begin{tabular}{llrrr}
\toprule
Dataset & Attack & Paper RR & Repro RR & Diff \\
\midrule
INRIA & 1-patch & 0.5909 & 0.7917 & +20.1\% \\
INRIA & 2-patch & 0.3871 & 0.8571 & +47.0\% \\
INRIA & trig & 0.4737 & 0.3636 & -11.0\% \\
\midrule
VOC & 1-patch & 0.5404 & 0.5385 & -0.2\% \\
VOC & 2-patch & 0.5376 & 0.5263 & -1.1\% \\
VOC & trig & 0.4244 & 0.1500 & -27.4\% \\
VOC & mo & 0.3955 & 0.2593 & -13.6\% \\
\bottomrule
\end{tabular}
\end{table}

% ============================================================
% Table 1b: Recovery Rate - Classification (8 Classes)
% ============================================================

\begin{table}[htbp]
\centering
\caption{Recovery Rate - Image Classification (8 Classes)}
\label{tab:recovery_rate_classification}
\begin{tabular}{llrrr}
\toprule
Dataset & Attack & Paper RR & Repro RR & Diff \\
\midrule
ImageNet & 1-patch & 0.8869 & 0.8667 & -2.0\% \\
ImageNet & 2-patch & 0.8535 & 0.6667 & -18.7\% \\
ImageNet & 4-patch & 0.8436 & 0.4667 & -37.7\% \\
ImageNet & trig & 0.5065 & 0.4000 & -10.7\% \\
\midrule
CIFAR & 1-patch & 0.9738 & 0.9286 & -4.5\% \\
CIFAR & 2-patch & 0.9789 & 0.8000 & -17.9\% \\
CIFAR & 4-patch & 0.9747 & 0.9333 & -4.1\% \\
CIFAR & trig & 0.8566 & 0.8667 & +1.0\% \\
\bottomrule
\end{tabular}
\end{table}

% ============================================================
% Table 2: nmAP Results (Object Detection)
% ============================================================

\begin{table}[htbp]
\centering
\caption{nmAP Results (Object Detection)}
\label{tab:nmap}
\begin{tabular}{lllrrr}
\toprule
Dataset & Attack & Metric & Paper & Repro & Diff \\
\midrule
INRIA & 1-patch & Adv. nmAP & 0.6897 & 0.7886 & +9.9\% \\
INRIA & 1-patch & Clean nmAP & 0.9998 & 1.0000 & +0.0\% \\
\midrule
VOC & 1-patch & Adv. nmAP & 0.5094 & 0.6938 & +18.4\% \\
VOC & 1-patch & Clean nmAP & 0.9950 & 1.0000 & +0.5\% \\
\bottomrule
\end{tabular}
\end{table}
"""

latex_path = os.path.join(OUTPUT_DIR, 'comprehensive_tables.tex')
with open(latex_path, 'w', encoding='utf-8') as f:
    f.write(latex_output)
print(f"Created: {latex_path}")

print("\n=== All comprehensive tables generated ===")
print(f"Output directory: {OUTPUT_DIR}")
print("\nGenerated files:")
print("  - comprehensive_recovery_rate_full.png (15 classes)")
print("  - comprehensive_rr_detection.png (7 classes)")
print("  - comprehensive_rr_classification.png (8 classes)")
print("  - comprehensive_nmap.png")
print("  - comprehensive_tables.tex (LaTeX)")
