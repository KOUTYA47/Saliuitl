# RESULT_LOG.md
実験結果の記録。各エントリは実験ID、日付、主要メトリクスを含む。

---

## R-2026-02-01: 論文再現実験（Table 1）

### 実験ID
`exp_20260201_reproduction`

### パラメータ
- ensemble_step: 5
- inpainting_step: 5
- inpaint: biharmonic
- nn_det_threshold: 0.5

### 結果

| Dataset | Attack | Paper RR | Repro RR | Paper LPR | Detected |
|---------|--------|----------|----------|-----------|----------|
| CIFAR | 1-patch | 0.9738 | 0.9286 | 0.0008 | 0.9286 |
| CIFAR | 2-patch | 0.9789 | 0.8000 | 0.0006 | 0.8667 |
| CIFAR | 4-patch | 0.9747 | 0.9333 | 0.0 | 1.0 |
| CIFAR | trig | 0.8566 | 0.8667 | 0.0 | 1.0 |
| ImageNet | 1-patch | 0.8869 | 0.8667 | 0.0071 | 1.0 |
| ImageNet | 2-patch | 0.8535 | 0.6667 | 0.0061 | 0.8667 |
| ImageNet | 4-patch | 0.8436 | 0.4667 | 0.0086 | 0.9333 |
| ImageNet | trig | 0.5065 | 0.4000 | 0.0612 | 0.6667 |
| INRIA | 1-patch | 0.5909 | 0.7917 | 0.0152 | 0.9583 |
| INRIA | 2-patch | 0.3871 | 0.8571 | 0.0 | 1.0 |
| INRIA | trig | 0.4737 | 0.3636 | 0.0526 | 0.5455 |
| VOC | 1-patch | 0.5404 | 0.5385 | 0.0293 | 1.0 |
| VOC | 2-patch | 0.5376 | 0.5263 | 0.0125 | 1.0 |
| VOC | trig | 0.4244 | 0.1500 | 0.0348 | 0.8 |
| VOC | mo | 0.3955 | 0.2593 | 0.0095 | 1.0 |

### 備考
- CIFAR/ImageNet用チェックポイントが提供されていない（torchvision pretrained使用）
- INRIA-MO データなし
- VOC 1-patch, 2-patch は論文値に近い

---

## R-2026-02-02-A: 検出スコア分布調査

### 実験内容
VOC 1-patch の検出スコア分布を `--save_scores` で取得

### 結果
```
Detection scores (26 samples):
Min: 0.9981
Max: 1.0
Mean: 0.9999
```

### 結論
- 全サンプルでスコア > 0.9
- 閾値スイープ（0.1〜0.9）が結果に影響しない理由が判明

---

## R-2026-02-02-B: 復元画像可視化実験

### 実験ID
`exp_20260202_recovery_viz`

### 実行内容
- VOC 1-patch: 10枚の復元画像を生成
- INRIA 1-patch: 10枚の復元画像を生成

### 結果

| Dataset | Unsuccessful Attacks | Detected Attacks |
|---------|---------------------|------------------|
| VOC 1-patch | 0.5385 (53.85%) | 1.0 (100%) |
| INRIA 1-patch | 0.7917 (79.17%) | 0.9583 (95.83%) |

### 生成ファイル
- `experiments/exp_20260202_recovery_viz/figures/voc_1p_*.png` (10枚)
- `experiments/exp_20260202_recovery_viz/figures/inria_1p_*.png` (10枚)

### 観察
- 復元後に検出数が増加するケースあり
- Detection Maskが黒く表示される（特徴マップサイズが小さいため）

---

## R-2026-02-02-C: nmAP再現実験（Table 2）

### 実験ID
`exp_20260202_nmap`

### 目的
論文Table 2のnmAP（normalized mean Average Precision）を再現

### nmAPの定義（論文Section 4.1）
- **adversarial nmAP** = mAP(復元後攻撃画像) / mAP(クリーン画像ベースライン)
- **clean nmAP** = mAP(復元後クリーン画像) / mAP(クリーン画像ベースライン)
- Ground truth = クリーン画像に対するモデル予測 h(xi)

### パラメータ
- ensemble_step: 5
- inpainting_step: 5
- inpaint: biharmonic
- iou_threshold: 0.5

### 結果

| Dataset | Metric | Paper | Repro | Diff |
|---------|--------|-------|-------|------|
| VOC 1-patch | Adv. nmAP | 0.5094 | 0.6938 | +0.18 |
| VOC 1-patch | Clean nmAP | 0.9950 | 1.0000 | +0.005 |
| INRIA 1-patch | Adv. nmAP | 0.6897 | 0.7886 | +0.10 |
| INRIA 1-patch | Clean nmAP | 0.9998 | 1.0000 | +0.0002 |

### 生成ファイル
- `compute_nmap.py`: nmAP計算スクリプト
- `experiments/exp_20260202_nmap/outcomes/`: outcomes保存先

### 考察
- 再現値のAdv. nmAPが論文値より高い
- サンプル数の違い（VOC: 26 vs 論文のフルデータ）が原因の可能性
- Clean nmAPはほぼ完全に一致（1.0）

---

## R-2026-02-02-D: Detection Mask可視化改善

### 実験ID
`exp_20260202_viz_improved`

### 問題
- 以前の可視化で `my_mask` が黒く表示されていた
- 原因: `my_mask` が初期化後に更新されていなかった

### 解決策
1. `my_mask` を `imgneer`（インペインティングマスク）で累積更新
2. `scipy.ndimage.zoom` で特徴マップを画像サイズにアップサンプリング
3. 6パネルレイアウト（2x3）に拡張

### 新しい可視化パネル
- **Feature Map Heatmap**: 特徴マップをアップサンプリングしてオーバーレイ
- **Inpainting Mask Overlay**: マスクを画像にオーバーレイ（alpha=0.6）
- **Inpainting Mask**: マスクのみ表示 + ピクセル比率

### 生成ファイル
`experiments/exp_20260202_viz_improved/figures/voc_1p_*.png` (5枚)

---

## R-2026-02-02-E: 回復画像品質問題の分析

### 実験ID
`exp_20260202_failure_analysis`

### 目的
回復画像が「ぼやける」「パッチが除去されていない」問題の原因を特定

### 核心的発見

**パッチは完全に除去されていない** - 全ての「Success」画像でも敵対的パッチがそのまま可視状態で残っている。

| 画像 | 状態 | パッチ除去 | 検出回復 |
|------|------|-----------|---------|
| VOC 000001 | Failed | ❌ 残存 | 2→3→6 |
| VOC 000006 | Success | ❌ 残存 | 3→3→8 |
| VOC 000010 | Success | ❌ 残存 | 1→2→4 |

### 原因分析

#### 1. 解像度のミスマッチ（最重要）
- 特徴マップ: 13×13、入力画像: 416×416
- スケール比: 1:1024（32×32ブロック単位）
- 1ピクセル誤差 → 32ピクセル誤差

#### 2. Biharmonicインペインティングの限界
- 曲率最小化アルゴリズム → 滑らか＝ぼやける
- 小さな傷向け設計 → 大きなパッチには不適

#### 3. マスク生成パイプラインの問題
- マスクが断片的で連続していない
- パッチ全体をカバーできていない

#### 4. 最適化目標のずれ
- 現在: 検出回復（IoU ≥ 0.5）
- 期待: 視覚的なパッチ除去

### 結論
1. 「成功」の定義が視覚的品質と乖離している
2. パッチ除去は行われていない - 検出回復のみ達成
3. 13×13→416×416のスケーリングが根本的なボトルネック
4. これは論文手法自体の限界であり、コードのバグではない

### 詳細レポート
`experiments/exp_20260202_failure_analysis/analysis_report.md`

---

## R-2026-02-02-F: 視覚的回復品質改善実験

### 実験ID
`exp_20260202_visual_recovery`

### 目的
視覚的にパッチを除去できるようにするための仮説検証

### 実施内容

#### 1. Oracle Inpainting Test
Ground-truthマスク（差分ベース）でbiharmonicインペインティングの上限性能を確認。

| Dataset | 画像数 | 平均マスク% | 平均エラー |
|---------|--------|------------|-----------|
| VOC | 5 | 1.6% | 0.63 |
| INRIA | 5 | 0.6% | 0.23 |

**発見**: 正確なマスクがあればパッチを視覚的に除去可能。ただしbiharmonicは結果がぼやける。

#### 2. Grad-CAM Attention可視化
YOLOv2 Layer 13でGrad-CAMを生成し、Clean/Attackedのattention比較。

| 画像 | Clean Score | Attacked Score | Attention変化 |
|------|-------------|----------------|---------------|
| 000001 | 0.884 | 0.670 | 人物→パッチに移動 |
| 000002 | 0.777 | 0.700 | 電車→パッチに移動 |
| 000004 | 0.833 | 0.834 | 変化小 |

**発見**: 敵対的パッチはモデルのAttentionを対象物体からパッチ自体にハイジャックする。

### 核心的発見

1. **マスク精度が主要ボトルネック** - 現システムのマスクが不正確なためパッチが除去されない
2. **Biharmonicは機能する** - 正確なマスクがあれば視覚的除去可能（ただしぼやける）
3. **Attention Hijacking** - パッチは検出器の注意を対象物体から奪う

### 解像度の訂正
以前の分析で13×13としていた特徴マップ解像度は**26×26**が正しい（Layer 13）。
- 実際のスケール比: 16倍（26×26→416×416）
- 1ピクセル誤差 → 16ピクセル誤差

### 生成ファイル
- `experiments/exp_20260202_visual_recovery/oracle_test/`
- `experiments/exp_20260202_visual_recovery/gradcam/`
- `experiments/exp_20260202_visual_recovery/results_summary.md`
- `analysis/oracle_inpaint_test.py`
- `analysis/gradcam_visualize.py`

---

## R-2026-02-03: 計算時間比較実験

### 実験ID
`exp_20260203_perf`

### 目的
論文Figure 4(a)の計算時間を実測値と比較

### パラメータ
- ensemble_step: 5, 10, 25 (|B|=20, 10, 4)
- inpainting_step: 同上
- inpaint: biharmonic
- performance mode: enabled

### 結果

| Dataset | |B| | Paper(s) | Measured(s) | Std(s) | n | Ratio |
|---------|-----|----------|-------------|--------|---|-------|
| VOC | 4 | 0.30 | 0.068 | 0.012 | 26 | 0.23 |
| VOC | 10 | 0.75 | 0.200 | 0.036 | 26 | 0.27 |
| VOC | 20 | 1.50 | 0.455 | 0.071 | 26 | 0.30 |
| INRIA | 4 | 0.30 | 0.071 | 0.023 | 24 | 0.24 |
| INRIA | 10 | 0.75 | 0.202 | 0.039 | 23 | 0.27 |
| INRIA | 20 | 1.50 | 0.409 | 0.048 | 23 | 0.27 |

### 考察
- 実測値は論文値の約23-30%
- ハードウェア環境の違い（論文: NVIDIA T4）が主因と推測
- |B|に対して線形スケーリングを確認

### 生成ファイル
- `analysis/tables/measured_computational_cost.csv`
- `docs/slides_material/timing_paper_vs_measured.pdf/png`
- `docs/slides_material/timing_scaling.pdf/png`
