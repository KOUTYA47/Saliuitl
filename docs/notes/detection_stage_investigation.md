# 検知ステージ徹底調査

調査日: 2026-02-09
調査者: Lead Agent（直接コード確認による修正版）

---

## 1. 全体フロー

```
画像 → YOLOv2推論 → 第1maxpool FM取得 → チャネル合計(208×208)
  → per-beta二値化 → DBSCAN → 4属性抽出
  → 全beta集約 → L∞正規化 → 2x-1スケール → AD(1D-CNN) → sigmoid → 判定
```

---

## 2. 特徴マップ取得

### YOLOv2（INRIA/VOC）

- `do_detect()` → `darknet.forward()` で**第1 maxpool層の出力**を取得
  - 根拠: `darknet.py:89` (`fm_out=False`) → `darknet.py:130-135`（最初のmaxpoolで`fm`をキャプチャ、`fm_out=True`に設定）
- cfg/yolo.cfg: Conv(32, 3×3) → **Maxpool(2×2, stride=2)** → 出力 `(batch, 32, 208, 208)`
- `saliuitl.py:303-304`:
  ```python
  fm_np = feature_map[0].detach().cpu().numpy()  # (32, 208, 208)
  fm = np.sum(fm_np, axis=0)                      # (208, 208)
  ```
- **チャネル方向に合計**して1枚の空間マップにする

### 重要な注意

- MEMORY.md等で「26×26」「13×13」と言及されていたFM解像度は**復元ステージで使われるYOLO検出グリッド**の話であり、検知ステージのFMとは別物
- 検知ステージは**208×208**の高解像度空間マップ上で動作する

---

## 3. per-beta 二値化 + DBSCAN

### 3a. 閾値リスト生成（`saliuitl.py:307`）

```python
betas = [0.0 + x * 0.01 for x in range(0, 100, ensemble_step)]
```
- `ensemble_step=5` → 20個: `[0.00, 0.05, 0.10, ..., 0.95]`

### 3b. beta_iteration（`saliuitl.py:203-249`）

**二値化**（`saliuitl.py:205`）:
```python
binarized_fm = np.array(fm >= np.max(fm) * beta, dtype='float32')
```
- 閾値 = **FMの最大値 × beta**
- CLAUDE.mdの「mean + beta × std」という記述は**コード実装と異なる**

**座標取得 + StandardScaler**（`saliuitl.py:207-209`）:
```python
x, y = np.where(binarized_fm > 0)
thing = np.hstack((x.reshape(-1,1), y.reshape(-1,1)))
thing = StandardScaler(with_mean=mn, with_std=std).fit_transform(thing)
```
- `mn`, `std` は `--scale_mean`, `--scale_var`（デフォルト両方`False`=スケーリングOFF）

**DBSCAN**（`saliuitl.py:210`）:
```python
cluster = DBSCAN(eps=args.dbscan_eps, min_samples=args.dbscan_min_pts).fit(thing)
```
- デフォルト: `eps=1.0`, `min_samples=4`

---

## 4. 4属性の定義（`saliuitl.py:213-248`）

### 属性1: クラスタ数（n_clusters）

```python
clusters = np.unique(cluster.labels_)
# saliuitl.py:240
feat_stack.append(len([x!=-1 for x in clusters]))
```
- **注意**: `len([x!=-1 for x in clusters])` はブーリアンリストの長さ = **unique labelsの総数（ノイズ-1を含む）**
- 実質的にはクラスタ数+1（ノイズがある場合）またはクラスタ数（ノイズがない場合）

### 属性2: 平均クラスタ内距離（avg_intra_dist）

```python
# saliuitl.py:219-230
for cluster_label in clusters:
    if cluster_label == -1: continue
    data_c = thing[np.where(cluster.labels_ == cluster_label)]
    data_samp = data_c[np.random.choice(..., size=min(1000, len(data_c)), replace=False)]
    dmx = distance_matrix(data_samp, data_samp)
    dmx = dmx[np.tril_indices(dmx.shape[0], k=-1)]  # 下三角のみ（対角除外）
    avg_ic_d.append(np.mean(dmx))
avg_intracluster_d = np.mean(avg_ic_d)
```
- 各クラスタ内から最大1000点をサンプリング
- ペアワイズ距離行列の下三角（自分自身を除外）の平均
- 全クラスタのクラスタ内平均距離のさらに平均

### 属性3: 距離のクラスタ間標準偏差（std_intra_dist）

```python
avg_intracluster_std = np.std(avg_ic_d)  # saliuitl.py:231
```
- 各クラスタの「クラスタ内平均距離」のクラスタ間std

### 属性4: 活性ニューロン数（importance）

```python
feat_stack.append(binarized_fm.sum())  # saliuitl.py:246
```
- 二値化FM（0 or 1）の合計 = **閾値を超えた画素の個数**
- CLAUDE.mdの「重要度スコア」は誤解を招く名称。値の重み付けはなく、単純なカウント

### 属性の選択的除外

```python
if not 'nclus' in args.remove:   feat_stack.append(...)  # 属性1
if not 'avg' in args.remove:     feat_stack.append(...)  # 属性2
if not 'std' in args.remove:     feat_stack.append(...)  # 属性3
if not 'impneu' in args.remove:  feat_stack.append(...)  # 属性4
```
- `--remove` オプションで個別属性を除外可能（アブレーション用）

---

## 5. 集約・正規化・AD入力

### 集約（`saliuitl.py:306-314`）

```python
vector_s = []
for beta in betas:
    biggie, clus_feats = beta_iteration(beta, fm, raw=False)
    vector_s.append(clus_feats)
vector_s = np.array(vector_s).reshape((1, len(vector_s), len(clus_feats)))
# → shape: (1, num_betas, 4)
```

### 前処理: clustering_data_preprocessing（`helper.py:644-693`）

```python
clustering_data_preprocessing(vector_s, skip=True)
```
- `skip=True`: アライメント処理をスキップし、`transpose(0, 2, 1)` のみ実行
- 出力: `(1, 4, num_betas)` — 4チャネル × betaシーケンス

### L∞正規化（`saliuitl.py:315`）

```python
detector_input = 2 * nn.functional.normalize(
    torch.Tensor(...), dim=2, p=float('inf')
) - 1
```
- `nn.functional.normalize(dim=2, p=inf)`: **各属性チャネル内で、全beta値中の最大絶対値で割る**
- `2*x - 1`: [0,1] → [-1,1] にスケール
- 最終形状: `(1, 4, num_betas)` — 3Dテンソル（Conv1d入力に適合）

---

## 6. ADモデル: AtkDetCNNRaw（`nets/attack_detector.py:39-75`）

**実態は1D-CNN**（名称の"CNN Raw"は2D-CNNを想起させるが、Conv1dを使用）

```
入力:  (batch=1, channels=4, seq=num_betas)
  → Conv1d(4→12, k=2) → AdaptiveAvgPool1d(12) → BN(12) → ReLU
  → Conv1d(12→12, k=2) → AdaptiveAvgPool1d(12) → BN(12) → ReLU
  → flatten → (144,)
  → Linear(144→576) → ReLU
  → Linear(576→576) → ReLU
  → Linear(576→1) → Sigmoid
出力: [0, 1] のスカラー（sigmoid適用済み）
```

- `in_feats` パラメータでチャネル数（属性数）を可変にできる（`saliuitl.py:160`）
- デフォルト `in_feats=4`（全属性使用時）

### 判定（`saliuitl.py:317-320`）

```python
with torch.no_grad():
    detector_output = net(detector_input.to(device))
detection_score = detector_output.detach().cpu().numpy()
condition = detection_score >= args.nn_det_threshold  # default: 0.5
```
- **sigmoidはモデル内で適用済み**なので、外部で追加のsigmoidは不要

---

## 7. 実験結果（2026-02-09）

VOC 1-patch、26画像で4属性を抽出:

| 指標 | Attacked平均 | Clean平均 | 分離度 |
|------|------------|---------|-------|
| AD Score | 0.9999 | 0.0245 | 完全分離 |

### 属性別の乖離パターン

- **全4属性でβ=0.05〜0.30に乖離が集中**
- 高beta（≥0.5）では clean/attacked の差はほぼゼロ
- **n_clusters**: 相対的判別力が最強（個別画像で最大9.9%相対乖離）
- **importance**: 絶対差が最大（β=0.05で Attacked≈40,000 vs Clean≈15,000）

### 生成ファイル

- `experiments/exp_20260209_detection_features/detection_features.csv`（1,040レコード）
- `experiments/exp_20260209_detection_features/figures/mean_raw_attributes.png`
- `experiments/exp_20260209_detection_features/figures/mean_normalized_ad_input.png`
- `experiments/exp_20260209_detection_features/figures/single_*.png`（3枚）

---

## 8. CLAUDE.md / MEMORY.md の記述との相違点

| 項目 | CLAUDE.md / MEMORY.md | コード実装（事実） |
|------|----------------------|------------------|
| 二値化 | 「mean + beta × std」 | `max(fm) * beta` (`saliuitl.py:205`) |
| 処理単位 | 暗黙にチャネルごと | チャネル合計後の1枚の空間マップ |
| 重要度スコア | 「重要度スコア」 | `binarized_fm.sum()` = 活性ピクセル数 |
| FM解像度 | 「26×26」 | 検知ステージは**208×208**（第1 maxpool出力） |
| ADモデル | — | **1D-CNN**（Conv1d）、2D-CNNではない |
| AD出力 | — | モデル内sigmoid適用済み |
| L∞正規化 | 「各属性のbeta全体最大値」 | `nn.functional.normalize(dim=2, p=inf)` → 事実上同義だが `2*x-1` スケーリングが追加 |
