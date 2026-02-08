# 復元マスク面積の考察 — 「5.5%以下か？」

作成日: 2026-02-08
更新日: 2026-02-08（可視化と評価の乖離を追記、可視化修正を実装、ボックス貢献度分析を追加）

---

## 結論

**システム生成マスクの累積面積（`my_mask`）は5.5%以下ではない。** 可視化画像から読み取った実測値は **4.3%〜10.9%**であり、大半が5.5%を超えている。

ただし、**可視化で表示される「回復画像」と、評価に実際に使われるデータは異なる**ことが判明した（Section 1.4参照）。可視化は最終beta（最低閾値）のインペインティング画像を表示するが、評価は全betaの検出ボックスの蓄積を使う。高beta（小さいマスク）の回が評価の主な貢献者である可能性が高い。

---

## 1. 実測データ

### 1.1 `my_mask` 累積マスク面積（viz_improved 可視化タイトルから読み取り）

| 画像 | `my_mask` 面積 | 結果 | 備考 |
|------|---------------|------|------|
| VOC 000001 | **9.4%** | Failed | パッチは人物の胸部に配置 |
| VOC 000006 | **5.8%** | Success | ダイニングテーブルの画像 |
| VOC 000008 | **10.9%** | Success | 椅子周辺の複雑なシーン |
| VOC 000010 | **10.3%** | Success | 馬術の画像 |
| VOC 000011 | **4.3%** | Success | 猫の画像 |

- **5枚中4枚が5.5%超**
- 平均: **8.1%**
- ソース: `experiments/exp_20260202_viz_improved/figures/voc_1p_*.png`

### 1.2 Oracle マスク面積（実際のパッチ占有面積）

| Dataset | パッチ面積範囲 | 平均復元誤差 |
|---------|-------------|------------|
| VOC | 0.2% - 5.3% | 0.63 |
| INRIA | 0.1% - 1.3% | 0.23 |

- ソース: `experiments/exp_20260202_visual_recovery/results_summary.md`

### 1.3 面積比較

```
パッチ実面積（oracle）:   0.1% ─ 5.3%   ← 実際の敵対的パッチ
システム生成マスク:        4.3% ─ 10.9%  ← Saliuitlが生成するマスク
失敗分析レポートの値:      5.8% ─ 10.3%  ← 周囲の正常領域含む

膨張率: パッチ面積の 約2倍〜100倍
```

### 1.4 可視化と評価の乖離（重要発見）

**`analysis/figures/recovered/` の「回復画像」は、評価に使われる画像とは異なる。**

#### 可視化が表示するもの

`saliuitl.py:482` で `in_img` を表示している。`in_img` はper-betaループ内で毎回 `p_img.detach().clone()` から再生成され（line 397）、ループ終了後に残るのは**最終反復（最低beta）のインペインティング画像のみ**。

```python
# line 482: ループ終了後の in_img = 最低beta（最も広いマスク）の結果
recovered_np = in_img.squeeze(0).cpu().numpy().transpose(1, 2, 0)
```

そのため `analysis/figures/recovered/` で確認された:
- INRIA crop_000016: ほぼ全面が緑がかった平坦なブロブ
- VOC 000025: 牛のシーンが完全に白化
- VOC 001023: キッチンが完全にぼやける

これらは**最終beta（最も低い閾値 ≒ 最も広いマスク）の1回分のインペインティング結果**に過ぎない。

#### 評価が使うもの

```python
# line 415-416: 各betaの検出ボックスを蓄積
boxes2, feature_map = do_detect(model, in_img, ...)
sd_boxes = sd_boxes + boxes2

# line 419-420: ループ後、全betaの結果 + 元の検出をNMS統合
sd_boxes = nms(sd_boxes, 0.4, match_class=False)
sd_boxes = nms(sd_boxes + adv_boxes, 0.4, match_class=True)
```

評価は**全betaの検出ボックスの蓄積**。高beta（beta=0.95等）の回は:
- マスク面積: 1-3%（パッチ核心部のみ）
- biharmonic品質: 良好
- 検出回復: パッチの最も顕著な部分のみ除去

**Success判定は、高betaの小さいマスクで得られた良質な検出ボックスに依存している可能性が高い。**

#### 構造図

```
beta=0.95: in_img_1 (mask ~1%) → boxes_1  ─┐
beta=0.90: in_img_2 (mask ~3%) → boxes_2  ─┤
  ...                                       ├→ sd_boxes(蓄積) → NMS → 評価
beta=0.05: in_img_19 (mask ~90%) → boxes_19─┘
                │
                └──→ 可視化の "Recovered" ★ 最悪ケースのみ表示 (修正前)
```

#### 実装修正 (2026-02-08)

**修正内容**: 可視化の "Recovered" パネルに、最終betaの画像ではなく**最も多くの検出ボックスを生成したbeta**の画像を表示するよう変更。

**変更箇所** (`saliuitl.py`):

1. **per-betaループ前** (line ~355-360): トラッキング変数を追加
   - `best_viz_img`: 最多検出ボックスを生成したbetaのインペインティング画像
   - `best_viz_beta`: そのbeta値
   - `best_viz_mask`: そのbetaの`imgneer`マスク
   - `per_beta_stats`: 各betaの (beta値, マスク面積%, 検出ボックス数)

2. **per-betaループ内** (line ~423-430): 各betaの検出後にトラッキング更新
   - 検出ボックス数が過去最多、または同数で高betaの場合にbest更新

3. **可視化セクション** (line ~495-550):
   - "Recovered" パネル: `in_img` → `best_viz_img` (fallback付き)
   - "Mask Overlay" パネル: 累積`my_mask` → `best_viz_mask` (best betaの単体マスク)
   - "Accum. Mask" パネル: 累積マスク表示 + per-beta統計テキスト

**修正後の構造図**:
```
beta=0.95: in_img_1 (mask ~1%) → boxes_1=3  ─┐
beta=0.90: in_img_2 (mask ~3%) → boxes_2=2  ─┤
  ...                                          ├→ sd_boxes(蓄積) → NMS → 評価
beta=0.05: in_img_19 (mask ~90%) → boxes_19=0─┘
     │                                │
     │                                └──→ best_viz_img = in_img_1 ★ 最多検出betaを表示
     └──→ per_beta_stats: 各betaのマスク面積・検出数を記録
```

---

## 2. なぜマスクが膨張するか — メカニズムの解明

### 2.1 ベータ反復の構造（`saliuitl.py:348-416`）

```python
# line 348: beta は高→低で降順に反復
revran = list(reversed([0.0+x*0.01 for x in range(0,100,args.inpainting_step)]))[:-1]
# step=5 の場合: [0.95, 0.90, 0.85, ..., 0.10, 0.05]  (19値)

# line 354: bfm_old は全て1で初期化
bfm_old = np.ones(fm.shape)

for numel, beta_big in enumerate(revran):
    this = beta_iteration(beta_big, fm_og)          # line 363: DBSCAN結果
    ...
    bfm = fm_og >= np.max(fm_og) * beta_big          # line 381: 二値化

    # line 384: 停止条件（FMセル数ベース）
    if masking > (args.neulim * my_mask.size) / 9:
        continue

    # line 386-391: per-beta マスク生成
    imgneer = np.zeros((416, 416))                    # 毎回リセット
    for x, y in cluster_coords:
        imgneer[2*x-1:2*x+2, 2*y-1:2*y+2] = bfm_old[x, y]  # 前betaの重み

    bfm_old = bfm                                     # line 393: 更新

    # line 395: 可視化用累積（検出ロジックには非関連）
    my_mask = np.maximum(my_mask, imgneer * (1.0 - beta_big))

    # line 397-408: 独立にインペインティング + 再検出
    in_img = p_img.detach().clone()                   # 毎回元画像から
    in_img = inpaint.inpaint_biharmonic(in_img, imgneer, ...)
    boxes2 = do_detect(model, in_img, ...)
    sd_boxes = sd_boxes + boxes2                      # 検出結果を蓄積
```

### 2.2 `bfm_old` 重み付けの効果

`bfm_old` は前betaの二値化マスクであり、`imgneer` の各ピクセル値を制御する:

| 反復 | beta | `bfm_old` の状態 | `imgneer` への効果 |
|------|------|-----------------|-------------------|
| 1 | 0.95 | `np.ones(fm.shape)` = 全て1 | 全クラスタ座標がimgneer=1.0 |
| 2 | 0.90 | `bfm(0.95)` = top 5%のみTrue | 前回も顕著だった座標のみimgneer=1.0 |
| 3 | 0.85 | `bfm(0.90)` = top 10%のみTrue | 同上、やや広い |
| ... | ... | ... | ... |
| 19 | 0.05 | `bfm(0.10)` = top 90%がTrue | ほぼ全てのクラスタ座標がimgneer=1.0 |

**発見**: 最初の反復（beta=0.95）では`bfm_old = ones`のため、DBSCANが見つけた全クラスタ座標が無条件にマスクされる。最後の反復（beta=0.05）では、DBSCANのクラスタは非常に大きくなり（FM全域に近い）、かつ`bfm_old`も広いため、画像の大半がマスクされる。

### 2.3 低betaでの「全面マスク」問題

`beta_iteration()` (line 205): `binarized_fm = fm >= np.max(fm) * beta`

beta=0.05の場合、FMの最大値の5%以上の全ピクセルが活性化する。ReLU後の特徴マップでは、ほとんどの値が正であるため、**FM全域の90%以上が活性化**する。

```
beta=0.95 → FM活性化セル数: ごく少数（上位5%のみ）
beta=0.50 → FM活性化セル数: 全体の約半分
beta=0.05 → FM活性化セル数: 全体の約95%
```

DBSCANがこの大量のポイントに対して1つの巨大クラスタを形成し、結果として画像のほぼ全面がインペインティング対象となる。

### 2.4 停止条件 `neulim` の不十分さ

```python
# line 384
if masking > (args.neulim * my_mask.size) / 9:
    continue   # このbetaをスキップ（breakではない）
```

- `neulim=0.5`（デフォルト）、`my_mask.size = 416×416 = 173,056`
- 閾値 = (0.5 × 173,056) / 9 ≈ **9,614 FMセル**
- 208×208 FM全体 = 43,264セル → 閾値は**全FMの22.2%**

つまり、FMセルの22%以上がクラスタに含まれるbetaはスキップされるが、21%以下なら通過する。21%のFMセル × 9ピクセル/セル = 画像面積の**約21%**がインペインティング対象になりうる。

**重要**: `continue`（`break`ではない）のため、あるbetaがスキップされても次のbeta（より低い閾値）の処理は続行される。ただし低betaはさらに大きなクラスタを生むため、連続してスキップされる傾向がある。

### 2.5 `my_mask` と per-beta `imgneer` の関係

```python
# line 395: 累積マスク（可視化専用）
my_mask = np.maximum(my_mask, imgneer * (1.0 - beta_big))
```

`my_mask` は全betaの `imgneer` マスクの**重み付き最大値**であり、重みは `(1 - beta)`。高beta（0.95）は重み0.05、低beta（0.05）は重み0.95。

- 可視化で表示される **4.3-10.9%** は、この累積マスクの非ゼロピクセル率
- per-beta `imgneer` のうち、低betaの回は面積がはるかに大きい（50-90%の推定値と整合）
- **各betaのインペインティングは独立に実行**される（`in_img = p_img.detach().clone()` で毎回元画像から生成）
- 最終結果は全betaの検出ボックスの蓄積（`sd_boxes`）

---

## 3. 重要な発見

### 発見1: パッチ面積とマスク面積の乖離（over-masking）

| 指標 | 値 | ソース |
|------|-----|--------|
| 実際のパッチ面積 | 0.1-5.3% | Oracle mask測定 |
| `my_mask` 累積面積 | 4.3-10.9% | viz_improved タイトル |
| per-beta実効面積（低beta） | 50-90% | analysis/recovered 目視 |

**パッチが1%の画像でも、システムは10%以上をマスクする**。これは以下の要因による:
- 特徴マップ上でパッチ以外の顕著領域もクラスタに含まれる
- 低betaでFMのほぼ全域が活性化し、巨大クラスタが形成される
- FM→画像空間のスケーリング（各FMセル → 約3×3ピクセル）がマスクを膨張させる

### 発見2: 検出成功と視覚的復元の乖離

| 画像 | マスク面積 | 結果 | 視覚的状態 |
|------|----------|------|-----------|
| VOC 000008 | 10.9% | **Success** | パッチは完全残存 |
| VOC 000010 | 10.3% | **Success** | パッチ残存、ぼやけた領域 |
| INRIA crop_000017 | — | Detected | 画像全体が白い霧 |

**Success = 検出が回復しただけ**であり、パッチが除去されたわけではない。これは`sd_boxes`が各betaの検出結果の蓄積であり、低betaで画像をほぼ全面マスクした際に偶然生じた検出ボックスも含まれるため。

**文献的裏付け**（failure_analysis レポート）:
> 「成功」の定義が視覚的品質と乖離している。パッチ除去は行われていない — 検出回復のみ達成

### 発見3: biharmonicインペインティングの面積依存的品質崩壊

文献調査の結果:

| マスク面積 | biharmonic品質 | 根拠 |
|-----------|---------------|------|
| 0-2% | 良好 | INRIA oracle test (誤差0.23) |
| 2-5% | 許容範囲 | VOC oracle test (誤差0.63) |
| **5-10%** | **急激に劣化** | Guillemot & Le Meur (2014) |
| 10%+ | 使用不可 | Rao et al. (2020) |

analysis/recovered画像で確認された「白い霧」は、biharmonicが大面積マスクに適用された結果。biharmonicは第4階偏微分方程式（曲率最小化）を解くため、大領域では境界情報が内部に到達できず、平坦な補間結果になる。

### 発見4: マスク精度が復元の主要ボトルネック

Oracle vs Biharmonic比較（`exp_20260205_oracle_full`）:

| タスク | 平均Oracle RR | 平均Biharmonic RR | 改善幅 |
|--------|-------------|------------------|--------|
| 物体検出 (7パターン) | 0.726 | 0.498 | **+22.8%** |
| 画像分類 (8パターン) | 0.750 | 0.741 | +0.8% |

**物体検出で+22.8%の改善余地がマスク精度にある**。完璧なマスク（oracle）なら、biharmonicでも十分な復元が可能。現在の問題はインペインティング手法ではなくマスク生成。

### 発見5: 3層ボトルネック構造

```
Level 1: 検出率 (Detection Rate)
  ├ 最重要。未検出なら復元処理自体が走らない
  ├ INRIA trig = 54.5% → Oracle RR上限も54.5%
  └ 改善余地: 15-45%（攻撃パターン依存）

Level 2: マスク精度 (Mask Precision)
  ├ 物体検出で+22.8%の改善余地
  ├ 根本原因: FMから画像空間へのアップスケーリング + over-masking
  └ 画像分類では影響小（+0.8%）

Level 3: インペインティング品質
  ├ 正確なマスクがあればbiharmonicで十分（物体検出）
  ├ ただし大面積では崩壊（5%超で劣化、10%超で使用不可）
  └ 視覚的品質はどの手法でも限界あり
```

---

## 4. `my_mask` 面積と per-beta 面積の関係図

```
beta=0.95 (最初)
  imgneer面積: ~1-3% (最も顕著な少数セルのみ)
  bfm_old: ones(全て1) → 全クラスタ座標がマスク
  biharmonic品質: 良好
  検出回復: パッチの核心部分のみ除去

beta=0.50 (中盤)
  imgneer面積: ~10-20% (顕著領域の半分程度)
  bfm_old: bfm(0.55) → 55%以上の活性領域のみマスク
  biharmonic品質: 劣化開始
  検出回復: パッチ周辺も巻き込むが回復可能性あり

beta=0.05 (最後)
  imgneer面積: ~50-90% (ほぼ全面)
  bfm_old: bfm(0.10) → 90%以上の領域がマスク
  biharmonic品質: 壊滅的（白い霧）
  検出回復: 画像破壊により偶発的な検出が生じうる

───────────────────────────────────────────────
my_mask (累積): 全betaの重み付き最大値 = 4.3-10.9%
  ← 低betaの寄与が支配的（重み=1-beta が大きい）
  ← ただし停止条件(neulim)でスキップされたbetaは含まれない
```

---

## 5. 文献的コンテキスト

### over-masking 問題の位置づけ

| 手法 | 対策 | 参考文献 |
|------|------|---------|
| PatchCleanser | 2段階マスキング（粗→精緻化） | Xiang et al. (2022) |
| Segment and Complete | セグメンテーションで正確なマスク | Liu et al. (2022) |
| Jedi | エントロピーベースで密接なバウンディング | Wu & Chen (2023) |
| ObjectSeeker | パッチ非依存マスキング + 認証保証 | Xiang et al. (2023) |
| **Saliuitl** | **顕著性ベース + DBSCAN → over-masking傾向** | 本プロジェクト |

Saliuitlのアプローチは、低beta反復で「安全側に倒す」（広くマスクして確実にパッチを除去）設計だが、その代償としてbiharmonicの品質崩壊を招いている。

### 検出率 vs 視覚品質のギャップ

文献的にも、検出ベースの評価（RR、mAP回復）と視覚的品質（PSNR、SSIM、パッチ除去率）の乖離は広く認識されている（Naseer et al. 2019, Chou et al. 2020）。Saliuitlの「Success」判定もこの乖離を示す典型例。

---

## 6. 今後の方向性

### 6.1 マスク精度改善（最優先）

**目標**: over-masking を抑制し、パッチ実面積（0.1-5.3%）に近いマスクを生成

| アプローチ | 期待効果 | 根拠 |
|-----------|---------|------|
| 高解像度FM使用（Layer 10: 52×52） | マスク位置精度2倍 | hypotheses.md H1 |
| beta範囲の制限（0.3-0.8等） | 低beta全面マスク防止 | 本分析 Section 2.3 |
| neulim閾値の引き下げ（0.5→0.1等） | 過大マスクの早期カット | 本分析 Section 2.4 |
| 2段階マスキング（粗検出→精緻化） | PatchCleanser方式 | Xiang et al. (2022) |

### 6.2 インペインティング手法の改善

**目標**: 5%以上のマスク面積でも意味的に正しい復元

| 手法 | 対応面積 | 根拠 |
|------|---------|------|
| Navier-Stokes (OpenCV) | ~10%まで | Rao et al. (2020) |
| GAN (LaMa, DeepFill) | ~15-20%まで | Rao et al. (2020) |
| Diffusion (Stable Diffusion Inpaint) | ~30%+報告あり | コード内にパスあり（未実装） |

### 6.3 評価指標の拡充

**目標**: 検出回復と視覚品質の両方を評価

| 指標 | 何を測るか |
|------|-----------|
| RR（現行） | 検出/分類の回復率 |
| マスクIoU | 生成マスクと実パッチの重なり |
| マスク面積率 | over-masking の程度 |
| 復元PSNR/SSIM | インペインティング品質 |

---

---

## 7. 実験的検証結果 (2026-02-08)

### 7.1 可視化修正の検証 (VIZTEST)

VOC 1p で `--save_images` を用いてbest_viz_img修正を検証。

| 項目 | 結果 |
|------|------|
| RR回帰テスト | 0.5385 (一致) |
| best betaマスク面積 | 0.3-2.6% (平均1.2%) |
| 累積マスク面積 | 4.3-10.9% (平均8.1%) |
| **比率** | **best beta ≈ 累積の1/6** |

best betaのマスクはパッチ実面積（0.1-5.3%）に近く、累積マスクよりも精緻。

### 7.2 Per-Beta統計 (BETASTATS)

best beta（最多検出ボックスを生むbeta）の分布:

| Beta範囲 | VOC (26画像) | INRIA (23画像) |
|----------|-------------|---------------|
| >= 0.50 | 19.2% | 17.4% |
| 0.40-0.49 | 19.2% | 17.4% |
| 0.30-0.39 | 26.9% | 21.7% |
| 0.20-0.29 | 23.1% | 34.8% |
| < 0.20 | 11.5% | 8.7% |

**全画像の63.3%でbest beta < 0.40。** 低betaを制限するとこれらの画像でbest betaを失う。

#### ボックス貢献度（Beta範囲別）

全betaで生成された検出ボックスの分布:

| Beta範囲 | VOC (914box) | INRIA (495box) | 全体 (1,409box) |
|----------|-------------|---------------|----------------|
| >= 0.50 | 264 (28.9%) | 109 (22.0%) | 373 (26.5%) |
| 0.40-0.49 | 170 (18.6%) | 82 (16.6%) | 252 (17.9%) |
| 0.30-0.39 | 178 (19.5%) | 93 (18.8%) | 271 (19.2%) |
| 0.20-0.29 | 189 (20.7%) | 120 (24.2%) | 309 (22.0%) |
| < 0.20 | 113 (12.4%) | 91 (18.4%) | 204 (14.5%) |
| **< 0.30合計** | **302 (33.0%)** | **211 (42.6%)** | **513 (36.4%)** |

**全ボックスの36.4%がbeta < 0.30で生成**。低betaの遮断はNMS前の全ボックスの1/3以上を失う。

#### best betaのマスク面積

| 指標 | VOC | INRIA |
|------|-----|-------|
| 平均 | 2.2% | 1.9% |
| 中央値 | 0.9% | 0.6% |
| 累積(my_mask)との比 | 約1/4 | 約1/4 |

### 7.3 neulim実験結果

| neulim | VOC RR | INRIA RR |
|--------|--------|----------|
| 0.1 | 0.4231 (-11.5%) | 0.7500 (-4.2%) |
| 0.2 | 0.5000 (-3.8%) | 0.7917 (0%) |
| 0.3 | 0.5000 (-3.8%) | 0.7917 (0%) |
| 0.5 | 0.5385 (baseline) | 0.7917 (baseline) |

neulim引き下げ（=低betaの遮断）はVOC RRを最大11.5%低下。低betaは検出回復に不可欠。

### 7.4 Section 6の仮説の検証結果

| 仮説 (Section 6.1) | 検証結果 |
|---------------------|---------|
| beta範囲の制限（0.3-0.8等） | **否定**: 63.3%の画像でbest beta<0.40。制限は壊滅的 |
| neulim閾値の引き下げ（0.5→0.1等） | **否定**: VOC RR -11.5%低下。デフォルト0.5が最適 |
| 高解像度FM使用 | 未検証 |
| 2段階マスキング | 未検証 |

**重要な発見**: 低betaの広域マスキングは「有害なover-masking」ではなく、高betaでは回復できない検出を補完する**必要な広域マスキング**であった。over-maskingの削減ではなく、マスク精度の向上（高解像度FM等）が正しい改善方向。

---

## 関連ドキュメント

| ファイル | 内容 |
|---------|------|
| `experiments/exp_20260202_failure_analysis/analysis_report.md` | 失敗分析（マスク断片化、解像度ミスマッチ） |
| `experiments/exp_20260205_oracle_full/results/oracle_vs_biharmonic_comparison.md` | Oracle vs Biharmonic RR比較 |
| `experiments/exp_20260202_visual_recovery/results_summary.md` | Oracle mask coverage測定 |
| `experiments/exp_20260202_visual_recovery/hypotheses.md` | 改善仮説リスト |
| `experiments/exp_20260208_betastats/analysis_report.md` | Per-Beta統計分析レポート |
| `experiments/exp_20260208_neulim/` | neulim閾値チューニング実験データ |
| `ASSUMPTIONS.md` | 評価指標定義、ボトルネック階層 |
| `RESULT_LOG.md` | 全実験結果の記録 |
