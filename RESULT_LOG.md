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
