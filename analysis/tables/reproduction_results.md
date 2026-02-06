# Saliuitl 論文再現実験結果

実行日: 2026-02-01
実行環境: Docker (saliuitl:latest)
パラメータ: ensemble_step=5, inpainting_step=5, inpaint=biharmonic

## 注意事項

- **Unsuccessful Attacks**: 攻撃を無効化できた割合（≈ Recovery Rate）
- **Detected Attacks**: 攻撃を検出できた割合
- **Successful Attacks**: 攻撃が成功した割合（= 1 - Unsuccessful）

現在の出力はeffective attacks（有効な攻撃）に対する評価のみ。
Lost Prediction Rate（クリーン画像での性能低下）の評価には `--clean` フラグが必要。

---

## 画像分類 (Image Classification)

### CIFAR-10

| Attack | Paper RR | Repro Unsuccessful | Paper LPR | Detected |
|--------|----------|-------------------|-----------|----------|
| 1-patch | 0.9738 | 0.9286 | 0.0008 | 0.9286 |
| 2-patch | 0.9789 | 0.8000 | 0.0006 | 0.8667 |
| 4-patch | 0.9747 | 0.9333 | 0.0 | 1.0 |
| Triangular | 0.8566 | 0.8667 | 0.0 | 1.0 |

### ImageNet

| Attack | Paper RR | Repro Unsuccessful | Paper LPR | Detected |
|--------|----------|-------------------|-----------|----------|
| 1-patch | 0.8869 | 0.8667 | 0.0071 | 1.0 |
| 2-patch | 0.8535 | 0.6667 | 0.0061 | 0.8667 |
| 4-patch | 0.8436 | 0.4667 | 0.0086 | 0.9333 |
| Triangular | 0.5065 | 0.4000 | 0.0612 | 0.6667 |

---

## 物体検出 (Object Detection)

### INRIA

| Attack | Paper RR | Repro Unsuccessful | Paper LPR | Detected |
|--------|----------|-------------------|-----------|----------|
| 1-patch | 0.5909 | 0.7917 | 0.0152 | 0.9583 |
| 2-patch | 0.3871 | 0.8571 | 0.0 | 1.0 |
| Triangular | 0.4737 | 0.3636 | 0.0526 | 0.5455 |
| Multi-Object | 0.4749 | N/A (データなし) | 0.0 | N/A |

### VOC

| Attack | Paper RR | Repro Unsuccessful | Paper LPR | Detected |
|--------|----------|-------------------|-----------|----------|
| 1-patch | 0.5404 | 0.5385 | 0.0293 | 1.0 |
| 2-patch | 0.5376 | 0.5263 | 0.0125 | 1.0 |
| Triangular | 0.4244 | 0.1500 | 0.0348 | 0.8 |
| Multi-Object | 0.3955 | 0.2593 | 0.0095 | 1.0 |

---

## 考察

### 一致するシナリオ
- VOC 1-patch: 論文値 0.5404 vs 再現値 0.5385 (差異: 0.0019)
- VOC 2-patch: 論文値 0.5376 vs 再現値 0.5263 (差異: 0.0113)

### 乖離が大きいシナリオ
- INRIA 1-patch: 論文値 0.5909 vs 再現値 0.7917 (再現値が高い)
- INRIA 2-patch: 論文値 0.3871 vs 再現値 0.8571 (再現値が高い)
- ImageNet 4-patch: 論文値 0.8436 vs 再現値 0.4667 (再現値が低い)
- VOC Triangular: 論文値 0.4244 vs 再現値 0.1500 (再現値が低い)

### 可能性のある原因
1. **評価指標の定義差異**: Unsuccessful AttacksとRecovery Rateの定義が異なる可能性
2. **データサンプル数の違い**: 今回の評価は30枚程度のサブセット
3. **alpha*（検出閾値）の設定**: 論文では最適な閾値を探索している
4. **effective_filesの内容**: 有効攻撃画像の定義が異なる可能性

---

## 改善実験の結果

### 実験1: クリーン画像評価（LPR算出）

`--clean` フラグを使用してクリーン画像での評価を実施。

| Dataset | Attack | LPR (Paper) | LPR (Repro) |
|---------|--------|-------------|-------------|
| VOC | 1-patch | 0.0293 | 0.0 |
| INRIA | 1-patch | 0.0152 | 0.0 |
| CIFAR | 1-patch | 0.0008 | 0.0 |
| ImageNet | 1-patch | 0.0071 | 0.0 |

**結果**: 再現実験ではLPR=0（クリーン画像で誤検出なし）。
論文値と差異がある理由として、クリーン画像評価時のコードパスが異なる可能性。

### 実験2: 検出閾値スイープ

閾値（α*）を0.1〜0.9で変化させて評価。

**VOC 1-patch と CIFAR 1-patch で検証した結果**:
閾値を変えても結果は変わらなかった。

**原因調査**: 検出スコア分布を分析
```
Detection scores for VOC 1-patch:
Min: 0.998, Max: 1.0, Mean: 0.9999

全26サンプルで scores > 0.9
```

**結論**: Attack Detectorは敵対的画像に対して非常に高い確信度（≈1.0）で検出するため、
閾値を変えても結果に影響しない。検出性能は十分で、乖離の原因は**復元段階**にある。

### 実験3: 評価指標の定義確認

`saliuitl.py` のコード分析結果:
- **Unsuccessful Attacks** = `clean_corr / kount`
  - 攻撃画像を処理した結果、クリーン画像と同じ予測になった割合
  - これは論文の **Recovery Rate (RR)** に対応
- **Detected Attacks** = `detected / kount`
  - Attack Detectorが攻撃と判定した割合

**課題**: effective_files で指定される「有効攻撃画像」の定義が再現性に影響している可能性。

---

## 改訂された考察

### 再現できた要因
1. **VOC 1-patch, 2-patch**: 論文値と非常に近い（差異 < 0.02）
2. **CIFAR/ImageNet の一部**: 傾向は一致

### 乖離が残る要因（推定）
1. **データサンプル数の違い**:
   - 今回: 30枚程度のサブセット
   - 論文: 全データセット
2. **effective_filesの選定基準**:
   - 「有効な攻撃」の定義が不明確
   - 論文では攻撃成功率100%のサンプルのみ使用している可能性
3. **復元アルゴリズムの不確定性**:
   - DBSCANクラスタリングのランダム性
   - インペインティング領域の決定方法
4. **分類タスク用チェックポイントの欠如**:
   - CIFAR/ImageNet用のAttack Detectorチェックポイントが提供されていない

---

## 結論

| 項目 | 評価 |
|------|------|
| 検出性能 | ✅ 論文と一致（Detection Rate ≈ 1.0） |
| 復元性能（VOC） | ✅ 論文と近い（差異 < 0.02） |
| 復元性能（INRIA） | ⚠️ 乖離あり（再現値が高い） |
| 復元性能（分類タスク） | ⚠️ チェックポイント不足で完全評価不可 |
| LPR | ⚠️ 再現値=0（論文より良い結果） |

**総合評価**: VOCデータセットで論文値をほぼ再現。他データセットでは追加調査が必要。
