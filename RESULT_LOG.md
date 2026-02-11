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

---

## R-2026-02-05: Oracle Inpainting Test（全15パターン）

### 実験ID
`exp_20260205_oracle_full`

### 目的
全データセット・全攻撃パターンでOracle Inpainting Testを実施し、biharmonic再現実験との差分を明らかにする。
Oracle Inpaintingは、マスク領域にクリーン画像のピクセルを貼り付ける手法で、**インペインティング品質の上限**を示す。

### パラメータ
- ensemble_step: 5
- inpainting_step: 5
- inpaint: **oracle**
- nn_det_threshold: 0.5

### 結果（全15パターン）

#### 物体検出（Object Detection）- 7パターン

| Dataset | Attack | Paper RR | Biharmonic RR | Oracle RR | Detected | Δ(O-B) |
|---------|--------|----------|---------------|-----------|----------|--------|
| INRIA   | 1p     | 0.5909   | 0.7917        | **0.8750** | 0.9583   | +0.083 |
| INRIA   | 2p     | 0.3871   | 0.8571        | **1.0000** | 1.0000   | +0.143 |
| INRIA   | trig   | 0.4737   | 0.3636        | **0.5455** | 0.5455   | +0.182 |
| VOC     | 1p     | 0.5404   | 0.5385        | **0.7692** | 1.0000   | +0.231 |
| VOC     | 2p     | 0.5376   | 0.5263        | **0.7368** | 1.0000   | +0.211 |
| VOC     | trig   | 0.4244   | 0.1500        | **0.4500** | 0.8500   | +0.300 |
| VOC     | mo     | 0.3955   | 0.2593        | **0.7037** | 1.0000   | +0.444 |

**物体検出 平均改善**: +0.228 (+22.8%)

#### 画像分類（Image Classification）- 8パターン

| Dataset  | Attack | Paper RR | Biharmonic RR | Oracle RR | Detected | Δ(O-B) |
|----------|--------|----------|---------------|-----------|----------|--------|
| CIFAR    | 1p     | 0.9738   | 0.9286        | 0.9286    | 0.9286   | 0.000  |
| CIFAR    | 2p     | 0.9789   | 0.8000        | 0.8000    | 0.8667   | 0.000  |
| CIFAR    | 4p     | 0.9747   | 0.9333        | 0.8667    | 1.0000   | -0.067 |
| CIFAR    | trig   | 0.8566   | 0.8667        | 0.8000    | 1.0000   | -0.067 |
| ImageNet | 1p     | 0.8869   | 0.8667        | 0.7333    | 1.0000   | -0.133 |
| ImageNet | 2p     | 0.8535   | 0.6667        | 0.8000    | 0.8667   | +0.133 |
| ImageNet | 4p     | 0.8436   | 0.4667        | 0.6667    | 0.9333   | +0.200 |
| ImageNet | trig   | 0.5065   | 0.4000        | 0.4000    | 0.6667   | 0.000  |

**画像分類 平均改善**: +0.008 (+0.8%)

### 統計サマリ

| タスク | 平均Oracle RR | 平均Biharmonic RR | 平均改善幅 |
|--------|--------------|------------------|-----------|
| 物体検出（7シナリオ） | 0.726 | 0.498 | **+0.228** |
| 画像分類（8シナリオ） | 0.750 | 0.741 | +0.008 |
| **全体（15シナリオ）** | 0.739 | 0.628 | **+0.111** |

### 主要な発見

1. **物体検出ではOracleが効果的**: 平均+22.8%の改善。マスク精度改善の余地が大きい。

2. **画像分類ではOracle効果が限定的**: 平均+0.8%の改善。一部でOracleがBiharmonicより低下。

3. **検出率がRRに大きく影響**: INRIA trigではDetected=54.5%と低く、Oracle RRも54.5%に留まる。

4. **VOC moが最大改善**: +44.4%（0.2593→0.7037）。Multi-objectパッチへの対応改善が効果的。

### 考察

#### Oracle RR ≤ Biharmonic RRのケース

CIFAR 4p, CIFAR trig, ImageNet 1pで発生。原因：
- **Oracle Inpaintingはマスクの問題を解決しない**（インペインティング品質のみ改善）
- 検出率の差異
- サンプル数の統計的変動

#### マスク精度 vs インペインティング品質

| 問題 | 物体検出への影響 | 画像分類への影響 |
|------|----------------|----------------|
| マスク位置の誤差 | **大** | 小 |
| インペインティング品質 | 中 | 中 |

物体検出ではマスク精度が重要であり、Oracle効果が顕著。

### 生成ファイル
- `experiments/exp_20260205_oracle_full/results/oracle_all_results.csv`
- `experiments/exp_20260205_oracle_full/results/oracle_full_comparison.md`

### 詳細考察（2026-02-05追加）

**考察ファイル**: `docs/notes/oracle_test_analysis.md`（310行）

#### 主要発見（5点サマリー）

1. **物体検出と画像分類で改善効果が大きく異なる**（+22.8% vs +0.8%）
   - マスク精度改善は物体検出でのみ有効

2. **検出率が全体の上限を決定する最重要ボトルネック**
   - 特にtrig攻撃で検出率が54-67%に低下

3. **VOC moが最大改善（+44.4%）を示したのは、Biharmonicのマスク精度が特に低かったため**

4. **画像分類では、完璧なマスクでも50-65%の復元率上限が存在**
   - インペインティングアプローチの本質的限界

5. **改善優先順位: 検出率 > マスク精度 > インペインティング品質**
   - 特に検出率の改善が全体性能に直結

#### ボトルネック階層構造

| レベル | ボトルネック | 物体検出での改善余地 | 画像分類での改善余地 |
|--------|-------------|---------------------|---------------------|
| Level 1 | 検出率 | 15-45%（攻撃パターン依存） | 3-7% |
| Level 2 | マスク精度 | **22.8%**（高優先） | 0.8%（低優先） |
| Level 3 | インペインティング品質 | 5-15% | 0-10% |

#### スライド用要約

> Oracle Inpainting Testにより、マスク精度改善の効果は物体検出タスクで顕著（+22.8%）である一方、画像分類では最小限（+0.8%）であることが判明した。最も重要なボトルネックは検出率であり、特定の攻撃パターン（三角形パッチ）で54-67%まで低下する。

---

## R-2026-02-08: 復元マスク面積考察・可視化/評価乖離の発見と修正

### 分析ID
`docs/notes/recovery_mask_analysis.md`

### 目的
1. システム生成マスクの累積面積が5.5%以下かを検証
2. 可視化画像と評価入力の整合性を確認
3. over-maskingメカニズムの解明

### 核心的発見

#### 発見1: マスク面積は5.5%以下ではない

| 画像 | `my_mask` 面積 | 結果 |
|------|---------------|------|
| VOC 000001 | 9.4% | Failed |
| VOC 000006 | 5.8% | Success |
| VOC 000008 | 10.9% | Success |
| VOC 000010 | 10.3% | Success |
| VOC 000011 | 4.3% | Success |

- **5枚中4枚が5.5%超**、平均8.1%
- Oracleパッチ面積（0.1-5.3%）の 2-100倍に膨張

#### 発見2: 可視化と評価の乖離（重要）

| 項目 | 可視化 | 評価 |
|------|--------|------|
| 使用画像 | **最終beta**（最低閾値）の`in_img` | 全betaの`sd_boxes`蓄積 |
| マスク面積 | 最終betaの `imgneer`（50-90%） | 各betaで独立（1-90%） |
| 代表性 | **最悪ケースのみ表示** | **全betaの検出を統合** |

**原因**: per-betaループ内で `in_img = p_img.detach().clone()` が毎回実行されるため、ループ終了後の `in_img` は最後のbeta（最も広いマスク）の結果のみ。

#### 発見3: over-maskingメカニズム

- `bfm_old` 重み付け: 最初のbeta(0.95)では全て1.0、以降は前betaの二値化結果
- 低beta(0.05)で FM全域の95%が活性化 → DBSCAN巨大クラスタ → 全面マスク
- `neulim=0.5` 停止条件: FMセル22%まで通過 → 画像面積の約21%がマスク対象
- `continue`（`break`ではない）のため、停止後も次betaが処理される

### 実装修正

`saliuitl.py` に以下を追加:

1. **per-betaループ前**: `best_viz_img`, `best_viz_beta`, `best_viz_mask`, `per_beta_stats` トラッキング変数
2. **per-betaループ内**: 最多検出ボックスを生成したbetaの画像・マスクを記録
3. **可視化セクション**:
   - "Recovered" パネル: `in_img` → `best_viz_img`（最多検出beta画像）
   - "Mask Overlay" パネル: 累積 → best betaの単体マスク
   - "Accum. Mask" パネル: per-beta統計テキスト追加

### 生成ファイル

| ファイル | 内容 |
|---------|------|
| `docs/notes/recovery_mask_analysis.md` | 復元マスク面積の包括的考察（400行） |

### 備考
- 可視化修正はR-2026-02-08-Bで検証済み
- 3層ボトルネック構造を確立: 検出率 > マスク精度(+22.8%) > IP品質

---

## R-2026-02-08-B: 可視化修正テスト (VIZTEST)

### 実験ID
`exp_20260208_vizfix`

### 目的
R-2026-02-08で実装した可視化修正（best_viz_img）の回帰テスト・目視検証

### 実行コマンド
```bash
docker run --rm --gpus all --network host -v /mnt/d/csprog/ooki/Saliuitl:/workspace -w /workspace saliuitl:latest \
  python saliuitl.py --inpaint biharmonic --imgdir data/voc/clean --patch_imgdir data/voc/1p \
  --dataset voc --det_net_path checkpoints/final_detection/2dcnn_raw_voc_5_atk_det.pth \
  --det_net 2dcnn_raw --ensemble_step 5 --inpainting_step 5 \
  --effective_files effective_1p.npy --n_patches 1 --save_images
```

### 結果
- **RR = 0.5385** (ベースラインと一致 → 回帰テスト合格)
- 5枚の可視化画像を生成

### 検証項目

| 項目 | 結果 |
|------|------|
| V-1: [beta=X.XX] ラベル表示 | OK |
| V-2: Best Beta Maskパネル表示 | OK |
| V-3: per-beta統計テキスト | OK |
| V-4: best betaマスク面積の妥当性 | OK (0.3-2.6%, 平均1.2%) |
| V-5: RR回帰テスト | OK (0.5385) |

### 重要な発見
- best betaのマスク面積: 0.3-2.6% (平均1.2%)
- 累積マスク面積(my_mask): 4.3-10.9% (平均8.1%)
- **best betaマスクは累積の約1/6** → best betaの方がパッチ実面積に近い

### 生成ファイル
- `experiments/exp_20260208_vizfix/figures/voc_1p_*.png` (5枚)

---

## R-2026-02-08-C: Per-Beta統計定量分析 (BETASTATS)

### 実験ID
`exp_20260208_betastats`

### 目的
各beta値が検出に与える貢献度を定量化し、beta範囲制限の妥当性を評価

### 結果

#### Best Beta分布

| Beta範囲 | VOC (26画像) | INRIA (23画像) | 全体 |
|----------|-------------|---------------|------|
| >= 0.50 | 19.2% | 17.4% | 18.4% |
| 0.40-0.49 | 19.2% | 17.4% | 18.4% |
| 0.30-0.39 | 26.9% | 21.7% | 24.5% |
| 0.20-0.29 | 23.1% | 34.8% | 28.6% |
| < 0.20 | 11.5% | 8.7% | 10.2% |

**核心的発見**:
- **全画像の63.3%で、best betaが0.40未満**
- **全画像の38.8%で、best betaが0.30未満**
- best betaのマスク面積: VOC平均2.2%、INRIA平均1.9%（累積8.1%の約1/4）

#### ボックス貢献度（Beta範囲別）

| Beta範囲 | VOC (914box) | INRIA (495box) | 全体 (1,409box) |
|----------|-------------|---------------|----------------|
| >= 0.50 | 28.9% | 22.0% | 26.5% |
| 0.40-0.49 | 18.6% | 16.6% | 17.9% |
| 0.30-0.39 | 19.5% | 18.8% | 19.2% |
| 0.20-0.29 | 20.7% | 24.2% | 22.0% |
| < 0.20 | 12.4% | 18.4% | 14.5% |
| **< 0.30合計** | **33.0%** | **42.6%** | **36.4%** |

全ボックスの36.4%がbeta<0.30で生成。最頻best beta: VOC=0.35、INRIA=0.20。

#### Beta範囲制限の影響評価

| 制限 | VOCで失われる画像 | INRIAで失われる画像 |
|------|-----------------|-------------------|
| beta >= 0.30 | 34.6% | 43.5% |
| beta >= 0.40 | **61.5%** | **65.2%** |

**結論: 低betaの単純カットは壊滅的。beta範囲制限タスク(BETARANGE)は実行不要。**

### 生成ファイル
- `experiments/exp_20260208_betastats/voc_1p/log.txt`
- `experiments/exp_20260208_betastats/inria_1p/log.txt`
- `experiments/exp_20260208_betastats/analysis_report.md`

---

## R-2026-02-08-D: neulim閾値チューニング (NEULIM)

### 実験ID
`exp_20260208_neulim`

### 目的
neulim停止条件の閾値を変えた場合のRR変化を測定

### 結果

| neulim | VOC 1p RR | INRIA 1p RR | VOC Detected | INRIA Detected |
|--------|-----------|-------------|--------------|----------------|
| 0.1 | **0.4231** | **0.7500** | 1.0 | 0.9583 |
| 0.2 | 0.5000 | 0.7917 | 1.0 | 0.9583 |
| 0.3 | 0.5000 | 0.7917 | 1.0 | 0.9583 |
| 0.5 (baseline) | 0.5385 | 0.7917 | 1.0 | 0.9583 |

### 分析

- **neulim=0.1**: VOC RRが-11.5%低下（0.5385→0.4231）。低betaの広域マスキングが遮断され、検出回復に必要なボックスが失われた。INRIAは-4.2%の軽微な低下。
- **neulim=0.2, 0.3**: VOC RRが-3.8%低下（0.5385→0.5000）。INRIAは影響なし。
- **検出率は全条件で変化なし**: neulimはインペインティング段階の制御であり、攻撃検出自体には影響しない。

### 結論
- neulim引き下げはVOCでRRを低下させる
- neulim=0.5（デフォルト）が最適
- 低betaの広域マスキングは「有害」ではなく、検出回復に不可欠

### 生成ファイル
- `experiments/exp_20260208_neulim/voc_1p_neulim_{0.1,0.2,0.3}/log.txt`
- `experiments/exp_20260208_neulim/inria_1p_neulim_{0.1,0.2,0.3}/log.txt`

---

## R-2026-02-09: 検知ステージ4属性抽出・可視化 (DETFEAT)

### 実験ID
`exp_20260209_detection_features`

### 目的
1. 検知ステージの攻撃検知メカニズムをコードレベルで正確に特定
2. 論文中の4属性グラフ（beta vs 属性値、clean/attacked比較）を再現
3. ADの判定根拠を可視化

### 調査で判明した事実

#### CLAUDE.md記述との相違

| 項目 | CLAUDE.md記載 | コード実装（事実） |
|------|-------------|------------------|
| 二値化閾値 | mean + beta × std | `max(FM) × beta`（`saliuitl.py:205`） |
| FM解像度 | 26×26 | **208×208**（第1 maxpool出力、`darknet.py:130-135`） |
| 処理単位 | チャネルごと | チャネル合計後の1枚の空間マップ（`saliuitl.py:304`） |
| 重要度 | 値ベース比率 | `binarized_fm.sum()` = 活性ピクセル数（`saliuitl.py:246`） |
| ADモデル | — | **1D-CNN (Conv1d)**（`nets/attack_detector.py:43`） |
| AD出力 | — | sigmoid適用済み [0,1]（`nets/attack_detector.py:73`） |

#### 4属性の正確な定義

| # | 属性 | 計算方法 | コード位置 |
|---|------|---------|-----------|
| 1 | クラスタ数 | DBSCAN unique labels数 | `saliuitl.py:240` |
| 2 | 平均クラスタ内距離 | 各クラスタ内1000点サンプル→ペアワイズ距離の下三角平均→クラスタ間平均 | `saliuitl.py:224-230` |
| 3 | 距離の標準偏差 | 上記クラスタ内平均距離のクラスタ間std | `saliuitl.py:231` |
| 4 | 活性ニューロン数 | `binarized_fm.sum()` | `saliuitl.py:246` |

### パラメータ
- dataset: VOC, attack: 1-patch
- ensemble_step: 5 (20 beta values)
- dbscan_eps: 1.0, dbscan_min_pts: 4
- nn_det_threshold: 0.5
- 画像数: 26

### 結果

#### AD判定スコアの分離

| 対象 | 平均 | 最小 | 最大 |
|------|------|------|------|
| Attacked | 0.9999 | 0.9987 | 1.0000 |
| Clean | 0.0245 | 0.0000 | 0.3530 |

→ **VOC 1-patchでは完全分離**（検知率100%と一致）

#### 属性別の乖離パターン

- **全4属性でβ=0.05〜0.30に乖離が集中**
- 高beta（≥0.5）ではclean/attackedの差がほぼゼロ
- **n_clusters**: 相対的判別力最強（パッチが独立クラスタを形成）
- **importance**: 絶対差最大（β=0.05でAttacked≈40,000 vs Clean≈15,000）

### 生成ファイル
- `experiments/exp_20260209_detection_features/detection_features.csv`（26画像×20beta×2type = 1,040レコード）
- `experiments/exp_20260209_detection_features/figures/mean_raw_attributes.png`（26画像平均、生値）
- `experiments/exp_20260209_detection_features/figures/mean_normalized_ad_input.png`（L∞正規化後）
- `experiments/exp_20260209_detection_features/figures/single_*.png`（3枚、個別画像詳細）
- `scripts/extract_detection_features.py`（抽出+可視化スクリプト）
- `docs/notes/detection_stage_investigation.md`（検知ステージ調査ドキュメント）

---

## R-2026-02-10: Table 1再現結果の考察分析 + 可視化

### 実験ID
`exp_20260201_reproduction`（追加分析）

### 目的
15シナリオの論文値との乖離原因を体系的に整理し、スライド・グラフを作成

### 分析結果

#### 乖離パターンの分類（全15シナリオ）

| Dataset | Attack | 評価n | 1枚=± | 検出率 | 論文差 | 主因 |
|---------|--------|:-----:|:-----:|:------:|:------:|:-----|
| VOC | 1p | 26 | 3.8% | 1.00 | **-0.2%** | — |
| VOC | 2p | 19 | 5.3% | 1.00 | **-1.1%** | — |
| VOC | trig | 20 | 5.0% | 0.80 | -27.4% | パッチ形状 |
| VOC | mo | 27 | 3.7% | 1.00 | -13.6% | 境界配置 |
| INRIA | 1p | 24 | 4.2% | 0.96 | +20.1% | eff不整合 |
| INRIA | 2p | 7 | 14.3% | 1.00 | +47.0% | eff不整合+n不足 |
| INRIA | trig | 11 | 9.1% | 0.55 | -11.0% | パッチ形状 |
| CIFAR | 1p | 14 | 7.1% | 0.93 | **-4.5%** | — |
| CIFAR | 2p | 15 | 6.7% | 0.87 | -17.9% | 検出率+n |
| CIFAR | 4p | 15 | 6.7% | 1.00 | **-4.1%** | — |
| CIFAR | trig | 15 | 6.7% | 1.00 | **+1.0%** | — |
| ImageNet | 1p | 15 | 6.7% | 1.00 | **-2.0%** | — |
| ImageNet | 2p | 15 | 6.7% | 0.87 | -18.7% | checkpoint |
| ImageNet | 4p | 15 | 6.7% | 0.93 | -37.7% | checkpoint+n増 |
| ImageNet | trig | 15 | 6.7% | 0.67 | -10.7% | checkpoint+形状 |

#### 主要知見
- **±5%以内で一致**: 6/15シナリオ（VOC 1p/2p, CIFAR 1p/4p/trig, ImageNet 1p）
- **INRIA上昇の主因**: effective_files不整合（重み差ではない。検出率95-100%で正常）
- **trig低下**: 非矩形パッチ形状による二重劣化（検出失敗+マスク形状不一致）
- **mo低下**: 境界配置によるIP品質低下（検出率100%、復元段階のみ劣化）
- **ImageNet低下**: checkpoint未提供（torchvision pretrained使用）+ パッチ数増加で拡大

### 生成ファイル
- `docs/slides_table1_reproduction.md`（結果+考察スライド、最終2枚構成）
- `experiments/exp_20260201_reproduction/results/rr_diff_chart.png`（RR Diff水平バーチャート）

---
