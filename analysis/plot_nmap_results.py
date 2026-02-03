"""
nmAP再現結果のグラフ作成スクリプト

参考: https://qiita.com/Hosi121/items/2196be987d8f47824c76
- PDF出力（ベクタ形式）
- 論文品質のフォント設定
- カラーマップによる配色
"""

import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import os

# フォント設定（論文向け）
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['xtick.major.width'] = 1.0
plt.rcParams['ytick.major.width'] = 1.0

# 出力ディレクトリ
OUTPUT_DIR = 'analysis/figures'
os.makedirs(OUTPUT_DIR, exist_ok=True)


def plot_nmap_comparison():
    """
    nmAP再現結果と論文値の比較グラフ
    """
    # データ
    datasets = ['VOC\n1-patch', 'INRIA\n1-patch']

    # Adversarial nmAP
    paper_adv = [0.5094, 0.6897]
    repro_adv = [0.6938, 0.7886]

    # Clean nmAP
    paper_clean = [0.9950, 0.9998]
    repro_clean = [1.0000, 1.0000]

    # カラーマップから色を取得
    cmap = plt.cm.get_cmap('GnBu')
    colors = [cmap(x) for x in np.linspace(0.4, 0.8, 4)]

    x = np.arange(len(datasets))
    width = 0.2

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # --- Adversarial nmAP ---
    ax1 = axes[0]
    bars1 = ax1.bar(x - width/2, paper_adv, width, label='Paper', color=colors[0], edgecolor='black', linewidth=0.8)
    bars2 = ax1.bar(x + width/2, repro_adv, width, label='Reproduction', color=colors[2], edgecolor='black', linewidth=0.8)

    ax1.set_ylabel('Adversarial nmAP', fontsize=14)
    ax1.set_xticks(x)
    ax1.set_xticklabels(datasets, fontsize=12)
    ax1.set_ylim(0, 1.0)
    ax1.legend(fontsize=10, loc='upper left')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    ax1.tick_params(axis='both', which='major', labelsize=12)
    ax1.set_title('(a) Adversarial nmAP', fontsize=14, fontweight='bold')

    # 値をバーの上に表示
    for bar, val in zip(bars1, paper_adv):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.3f}', ha='center', va='bottom', fontsize=9)
    for bar, val in zip(bars2, repro_adv):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.3f}', ha='center', va='bottom', fontsize=9)

    # --- Clean nmAP ---
    ax2 = axes[1]
    bars3 = ax2.bar(x - width/2, paper_clean, width, label='Paper', color=colors[0], edgecolor='black', linewidth=0.8)
    bars4 = ax2.bar(x + width/2, repro_clean, width, label='Reproduction', color=colors[2], edgecolor='black', linewidth=0.8)

    ax2.set_ylabel('Clean nmAP', fontsize=14)
    ax2.set_xticks(x)
    ax2.set_xticklabels(datasets, fontsize=12)
    ax2.set_ylim(0.9, 1.01)
    ax2.legend(fontsize=10, loc='lower left')
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    ax2.tick_params(axis='both', which='major', labelsize=12)
    ax2.set_title('(b) Clean nmAP', fontsize=14, fontweight='bold')

    # 値をバーの上に表示
    for bar, val in zip(bars3, paper_clean):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
                f'{val:.4f}', ha='center', va='bottom', fontsize=9)
    for bar, val in zip(bars4, repro_clean):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
                f'{val:.4f}', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()

    # PDF出力
    pdf_path = os.path.join(OUTPUT_DIR, 'nmap_comparison.pdf')
    with PdfPages(pdf_path) as pdf:
        pdf.savefig(fig, bbox_inches='tight')
    print(f'Saved: {pdf_path}')

    # PNG出力（プレビュー用）
    png_path = os.path.join(OUTPUT_DIR, 'nmap_comparison.png')
    plt.savefig(png_path, dpi=300, bbox_inches='tight')
    print(f'Saved: {png_path}')

    plt.close()


def plot_rr_lpr_comparison():
    """
    Recovery Rate / Lost Prediction Rate の比較グラフ（Table 1）
    """
    # RESULT_LOG.mdからのデータ
    datasets = ['CIFAR\n1p', 'CIFAR\n2p', 'CIFAR\n4p', 'CIFAR\ntrig',
                'ImageNet\n1p', 'ImageNet\n2p', 'ImageNet\n4p', 'ImageNet\ntrig',
                'INRIA\n1p', 'INRIA\n2p', 'INRIA\ntrig',
                'VOC\n1p', 'VOC\n2p', 'VOC\ntrig', 'VOC\nmo']

    paper_rr = [0.9738, 0.9789, 0.9747, 0.8566,
                0.8869, 0.8535, 0.8436, 0.5065,
                0.5909, 0.3871, 0.4737,
                0.5404, 0.5376, 0.4244, 0.3955]

    repro_rr = [0.9286, 0.8000, 0.9333, 0.8667,
                0.8667, 0.6667, 0.4667, 0.4000,
                0.7917, 0.8571, 0.3636,
                0.5385, 0.5263, 0.1500, 0.2593]

    # カラーマップ
    cmap = plt.cm.get_cmap('RdYlBu')

    fig, ax = plt.subplots(figsize=(14, 5))

    x = np.arange(len(datasets))
    width = 0.35

    bars1 = ax.bar(x - width/2, paper_rr, width, label='Paper',
                   color=cmap(0.7), edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x + width/2, repro_rr, width, label='Reproduction',
                   color=cmap(0.3), edgecolor='black', linewidth=0.5)

    ax.set_ylabel('Recovery Rate', fontsize=14)
    ax.set_xlabel('Dataset / Attack', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(datasets, fontsize=9, rotation=45, ha='right')
    ax.set_ylim(0, 1.1)
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.tick_params(axis='y', which='major', labelsize=12)

    # データセット区切り線
    for pos in [3.5, 7.5, 10.5]:
        ax.axvline(x=pos, color='gray', linestyle=':', alpha=0.7)

    plt.tight_layout()

    # PDF出力
    pdf_path = os.path.join(OUTPUT_DIR, 'rr_comparison.pdf')
    with PdfPages(pdf_path) as pdf:
        pdf.savefig(fig, bbox_inches='tight')
    print(f'Saved: {pdf_path}')

    # PNG出力
    png_path = os.path.join(OUTPUT_DIR, 'rr_comparison.png')
    plt.savefig(png_path, dpi=300, bbox_inches='tight')
    print(f'Saved: {png_path}')

    plt.close()


def plot_table2_full():
    """
    Table 2 (nmAP) の全シナリオ比較グラフ
    論文値のみ（再現は一部のみ）
    """
    # 論文 Table 2 データ
    scenarios = ['INRIA-1', 'INRIA-2', 'INRIA-T', 'INRIA-MO',
                 'VOC-1', 'VOC-2', 'VOC-T', 'VOC-MO']

    adv_nmap = [0.6897, 0.5998, 0.7034, 0.4737,
                0.5094, 0.5088, 0.5043, 0.3563]

    clean_nmap = [0.9998, 1.0, 0.9987, 0.9999,
                  0.9950, 0.9940, 0.9942, 0.9877]

    # 再現値（実施分のみ）
    repro_adv = [0.7886, None, None, None,
                 0.6938, None, None, None]

    fig, ax = plt.subplots(figsize=(10, 5))

    x = np.arange(len(scenarios))
    width = 0.25

    # カラーマップ
    cmap = plt.cm.get_cmap('GnBu')

    # Adversarial nmAP (Paper)
    bars1 = ax.bar(x - width, adv_nmap, width, label='Adv. nmAP (Paper)',
                   color=cmap(0.5), edgecolor='black', linewidth=0.8)

    # Clean nmAP (Paper)
    bars2 = ax.bar(x, clean_nmap, width, label='Clean nmAP (Paper)',
                   color=cmap(0.8), edgecolor='black', linewidth=0.8)

    # Adversarial nmAP (Reproduction) - 実施分のみ
    repro_vals = [v if v is not None else 0 for v in repro_adv]
    bars3 = ax.bar(x + width, repro_vals, width, label='Adv. nmAP (Repro)',
                   color='coral', edgecolor='black', linewidth=0.8, alpha=0.8)

    # 未実施分は透明化
    for i, v in enumerate(repro_adv):
        if v is None:
            bars3[i].set_alpha(0.1)

    ax.set_ylabel('nmAP', fontsize=14)
    ax.set_xlabel('Attack Scenario', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, fontsize=11, rotation=45, ha='right')
    ax.set_ylim(0, 1.15)
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.tick_params(axis='both', which='major', labelsize=12)

    # INRIA/VOC区切り線
    ax.axvline(x=3.5, color='gray', linestyle=':', alpha=0.7)
    ax.text(1.5, 1.08, 'INRIA', ha='center', fontsize=12, fontweight='bold')
    ax.text(5.5, 1.08, 'VOC', ha='center', fontsize=12, fontweight='bold')

    plt.tight_layout()

    # PDF出力
    pdf_path = os.path.join(OUTPUT_DIR, 'table2_nmap.pdf')
    with PdfPages(pdf_path) as pdf:
        pdf.savefig(fig, bbox_inches='tight')
    print(f'Saved: {pdf_path}')

    # PNG出力
    png_path = os.path.join(OUTPUT_DIR, 'table2_nmap.png')
    plt.savefig(png_path, dpi=300, bbox_inches='tight')
    print(f'Saved: {png_path}')

    plt.close()


if __name__ == '__main__':
    print("=" * 50)
    print("Generating publication-quality figures")
    print("=" * 50)

    print("\n[1/3] nmAP Comparison (VOC/INRIA 1-patch)")
    plot_nmap_comparison()

    print("\n[2/3] Recovery Rate Comparison (Table 1)")
    plot_rr_lpr_comparison()

    print("\n[3/3] Table 2 Full nmAP")
    plot_table2_full()

    print("\n" + "=" * 50)
    print("Done! Figures saved to:", OUTPUT_DIR)
    print("=" * 50)
