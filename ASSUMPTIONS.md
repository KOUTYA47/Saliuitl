# ASSUMPTIONS.md
本研究で暗黙に採用している前提条件を明文化する。

**参照元**: 論文 Section 4.1, saliuitl.py, helper.py

---

## データセットに関する前提

### 使用データセット

| データセット | タスク | 被害者モデル | 画像サイズ |
|-------------|--------|-------------|-----------|
| INRIA | 物体検出 | YOLOv2 | 416x416 |
| Pascal VOC | 物体検出 | YOLOv2 | 416x416 |
| ImageNet | 画像分類 | ResNet-50 | 224x224 |
| CIFAR-10 | 画像分類 | ResNet-50 | 192x192 |

### train / val / test の扱い

- **Attack Detector (AD)の学習**: 各データセットの訓練データを使用
- **評価**: effective_files で指定された攻撃成功画像のみを対象

### クリーン画像の定義

- 敵対的パッチが適用されていない、元の画像
- `--imgdir` で指定されるディレクトリの画像
- Ground truth = クリーン画像に対するモデル予測 `h(xi)`（ラベルではない）

---

## 攻撃設定に関する前提

### patch 数の定義

| 攻撃タイプ | パッチ数 | 形状 |
|-----------|---------|------|
| 1p (single) | 1 | 正方形 |
| 2p (double) | 2 | 正方形×2 |
| 4p (quadruple) | 4 | 正方形×4 |
| trig (triangular) | 1 | 三角形 |
| mo (multi-object) | 各オブジェクトに1つ | 正方形 |

### effective / uneffective の基準

**論文 Section 4.1 より:**

#### 物体検出の場合
攻撃 `pi` が入力 `xi` に対して **effective** である条件:
```
∃ object in h(xi) such that:
  IoU(object, all objects in h(A(xi, pi))) < 0.5
```
すなわち、クリーン予測の少なくとも1つのオブジェクトが、攻撃後の予測のすべてのオブジェクトと IoU < 0.5 であること。

#### 画像分類の場合
攻撃 `pi` が入力 `xi` に対して **effective** である条件:
```
h(A(xi, pi)) ≠ h(xi)
```
すなわち、攻撃後の予測がクリーン予測と異なること。

**コード実装** (`saliuitl.py:257`):
```python
if (eff_files != None and nameee not in eff_files and not args.uneffective):
    continue
```

### 攻撃成功の定義

- **evasion attack** (物体検出): 検出を回避すること
- **misclassification attack** (画像分類): 誤分類を引き起こすこと

---

## 評価指標に関する前提

### RR（Recovery Rate）の定義

**論文 Section 4.1:**
> "the recovery rate is the fraction of effectively attacked inputs (i.e., images in X'_1) recovered by Rφ"

- **分子**: 復元に成功した effectively attacked 画像数
- **分母**: effectively attacked 画像の総数 (|X'_1|)

**コード実装** (`saliuitl.py:789`):
```python
line1="Unsuccesful Attacks:"+str(clean_corr/max(1,kount))
# clean_corr = 復元成功数, kount = 処理画像数
# Unsuccessful Attacks = RR
```

#### 復元成功の判定（物体検出）
```python
for cb in cbb:  # クリーン検出ボックス
    bestest = best_iou(sdb, cb, match_class=args.eval_class)
    best_arr.append(bestest)
suc_atk = False
for b in best_arr:
    if b < iou_thresh:  # デフォルト: 0.5
        suc_atk = True
        break
```
すべてのクリーン検出が復元後の検出と IoU ≥ 0.5 でマッチすれば成功。

### LPR（Lost Prediction Rate）の定義

**論文 Section 4.1:**
> "the lost prediction rate is the fraction of clean inputs (i.e., images in X_1) for which applying Rφ results in an incorrect output"

- **分子**: Rφ適用後に誤った出力となるクリーン画像数
- **分母**: クリーン画像の総数 (|X_1|)

**注意**: 現在の実装では `--clean` オプションで計測可能。

### nmAP（normalized mean Average Precision）の定義

**論文 Section 4.1:**

| 指標 | 定義 |
|------|------|
| adversarial nmAP | mAP(X'_1 after Rφ) / mAP(X_1, no defense) |
| clean nmAP | mAP(X_1 after Rφ) / mAP(X_1, no defense) |

- Ground truth: クリーン画像に対するモデル予測 `h(xi)`
- IoU閾値: 0.5

---

## 実験条件に関する前提

### 乱数 seed

- **明示的なseed設定なし**: コード内でseed固定されていない
- DBSCANクラスタリングは決定的
- ニューラルネットワーク推論は決定的（eval mode）

### 画像前処理（resize / normalize）

| データセット | 前処理 |
|-------------|--------|
| INRIA/VOC | ToTensor() のみ（0-1正規化） |
| ImageNet | Resize(256) → CenterCrop(224) → Normalize([0.485,0.456,0.406], [0.229,0.224,0.225]) |
| CIFAR-10 | Resize(192) → Normalize((0.4914,0.4822,0.4465), (0.2023,0.1994,0.2010)) |

### 閾値（α*, beta など）の扱い

| パラメータ | デフォルト値 | 説明 |
|-----------|-------------|------|
| `nn_det_threshold` (α*) | 0.5 | AD検出閾値 |
| `ensemble_step` | 5 | β閾値セットサイズ (100/5=20閾値) |
| `inpainting_step` | 5 | 復元用β閾値セットサイズ |
| `iou_thresh` | 0.5 | effective判定・評価用IoU閾値 |
| `dbscan_eps` | 1.0 | DBSCANクラスタリング半径 |
| `dbscan_min_pts` | 4 | 最小クラスタサイズ |
| `neulim` | 0.5 | インペインティング上限（画像の50%まで） |

### β閾値セット

```python
BD = {x * max(mi) / 20}  for x in 0..19
# mi: 特徴マップ、各入力で範囲が異なる
```

---

## 比較に関する前提

### 比較は同一分母で行う

- RR比較: 同一の effective_files を使用
- nmAP比較: 同一のGround truth（クリーン予測）を使用

### clean / attacked を混在させない

- `X_1`: effectively attackedな画像に対応するクリーン画像
- `X'_1`: effectively attacked画像
- `X'_2`: ineffectively attacked画像

### 実行時間比較の測定方法

- `--performance`: 復元処理時間を測定
- `--performance_det`: 検出処理時間を測定
- 測定: `time.process_time()` (CPU時間)

---

## 未検証・仮定（Assumptions under Risk）

### 現時点で未検証の前提

1. **effective_filesの網羅性**
   - 提供されたeffective_filesがすべての攻撃成功ケースを含むか未確認
   - 論文のサンプル数と異なる可能性あり

2. **Attack Detectorの汎化性能**
   - 訓練データと異なる攻撃パターンへの汎化は未評価

3. **ResNet50チェックポイント** ✅ 解決済み（2026-02-04）
   - CIFAR/ImageNet用のADチェックポイントは `checkpoints/final_classification/` に存在
   - CIFAR用: `2dcnn_raw_cifar_{2,5,10,25}_atk_det.pth`
   - ImageNet用: `2dcnn_raw_imagenet_{2,5,10,25}_atk_det.pth`
   - 被害者モデル: `checkpoints/resnet50_192_cifar.pth`

### 将来崩れる可能性がある前提

1. **YOLOv2アーキテクチャ**
   - 特徴マップサイズ (13x13 or 26x26) はYOLOv2に依存
   - 他のモデルでは異なる可能性

2. **インペインティング手法**
   - biharmonic inpaintingの性能は画像内容に依存
   - パッチサイズが大きいと品質低下の可能性

3. **攻撃手法の進化**
   - 適応的攻撃（adaptive attack）への耐性は限定的

---

---

## Oracle Testから判明した事実（2026-02-05追加）

### マスク精度のボトルネック

Oracle Test（`--inpaint oracle`）の結果から、以下が判明:

| タスク | 平均Biharmonic RR | 平均Oracle RR | 差分（マスク損失）|
|--------|------------------|--------------|------------------|
| 物体検出 | 0.5045 | 0.9235 | **41.9%** |
| 画像分類 | 0.8977 | 0.9674 | 7.0% |

**解釈**:
- Oracle RR = マスクが完璧な場合の上限性能
- 差分 = マスク不正確性による損失
- **物体検出ではマスク精度が主要なボトルネック**

### タスク間差異の原因

| 要因 | 物体検出 | 画像分類 |
|------|---------|---------|
| 入力サイズ | 416×416 | 192×192 (CIFAR), 224×224 (ImageNet) |
| 特徴マップ | 26×26 | 12×12 (推定) |
| スケール比 | 16倍 | 16-19倍 |
| パッチ/画像比 | 小さい | 大きい |

**仮説**: 画像分類ではパッチが相対的に大きいため、マスクの位置誤差が許容されやすい。

### 三角形パッチの特殊性

VOC trigular: Biharmonic 15.0% → Oracle 93.2%（+78.2%の改善）

**原因**: DBSCANクラスタリングは矩形パッチを想定しており、三角形の境界がうまく捕捉できない。

---

## 更新履歴

- 2026-02-02: 初版作成（論文Section 4.1、saliuitl.pyから抽出）
- 2026-02-04: CIFAR/ImageNet用ADチェックポイントの存在を確認、誤記載を修正
- 2026-02-05: Oracle Test結果から判明した事実を追加
