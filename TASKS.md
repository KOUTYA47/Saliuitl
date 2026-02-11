# TASKS.md
*Standard Task Template for Research with Claude Code Sub-agents*

## 0. 目的
本ファイルは、Claude Code における **Lead / サブエージェント間の共通タスク定義** を提供する。
すべての研究タスクは、本テンプレートに基づいて記述されなければならない。

目的：
- タスクの意図・範囲・成功条件を明確化する
- サブエージェントの暴走・暗黙補完を防ぐ
- 実験・解析・執筆を一貫した形で管理する

---

# TASK ENTRIES: 論文再現実験

---

## TASK-20260201-REPRO: Saliuitl論文 Table 1 & Table 2 再現

### 1. タスク基本情報

```yaml
task:
  id: TASK-20260201-REPRO
  title: "Saliuitl論文の主要結果（Table 1, Table 2）を再現"
  owner: Lead
  assigned_agents:
    - Experiment-Runner
    - Result-Analyst
  status: todo
  priority: high
```

### 2. 背景・目的（Why）

```text
[背景]
- Saliuitl論文（CVPR 2025）の再現実験を実施
- 論文中のTable 1（Recovery Rate / Lost Prediction Rate）とTable 2（nmAP）を再現
- ユーザーが論文結果の正確性を検証できるようにする

[目的]
- 論文で報告された全シナリオの数値を再現する
- 再現結果と論文値の差異を明確にする
```

### 3. 再現対象の論文結果

#### Table 1: Recovery Rate (RR) / Lost Prediction Rate (LPR)

| Attack | Saliuitl RR/LPR (論文値) |
|--------|-------------------------|
| INRIA-1 | 0.5909/0.0152 |
| INRIA-2 | 0.3871/0.0 |
| INRIA-T | 0.4737/0.0526 |
| INRIA-MO | 0.4749/0.0 |
| VOC-1 | 0.5404/0.0293 |
| VOC-2 | 0.5376/0.0125 |
| VOC-T | 0.4244/0.0348 |
| VOC-MO | 0.3955/0.0095 |
| ImageNet-1 | 0.8869/0.0071 |
| ImageNet-2 | 0.8535/0.0061 |
| ImageNet-4 | 0.8436/0.0086 |
| ImageNet-T | 0.5065/0.0612 |
| CIFAR-1 | 0.9738/0.0008 |
| CIFAR-2 | 0.9789/0.0006 |
| CIFAR-4 | 0.9747/0.0 |
| CIFAR-T | 0.8566/0.0 |

#### Table 2: Adversarial/Clean nmAP（物体検出のみ）

| Attack | Saliuitl Adv./Clean (論文値) |
|--------|------------------------------|
| INRIA-1 | 0.6897/0.9998 |
| INRIA-2 | 0.5998/1.0 |
| INRIA-T | 0.7034/0.9987 |
| INRIA-MO | 0.4737/0.9999 |
| VOC-1 | 0.5094/0.9950 |
| VOC-2 | 0.5088/0.9940 |
| VOC-T | 0.5043/0.9942 |
| VOC-MO | 0.3563/0.9877 |

### 4. 利用可能なリソース

#### データセット
| Dataset | 攻撃シナリオ | effective file |
|---------|-------------|----------------|
| INRIA | 1p, 2p, trig | あり |
| INRIA | mo | **なし（要確認）** |
| VOC | 1p, 2p, trig, mo | あり |
| ImageNet | 1p, 2p, 4p, trig | あり |
| CIFAR-10 | 1p, 2p, 4p, trig | あり |

#### チェックポイント（Attack Detector）
- `checkpoints/final_detection/2dcnn_raw_inria_{2,5,10,25}_atk_det.pth`
- `checkpoints/final_detection/2dcnn_raw_VOC_{2,5,10,25}_atk_det.pth`
- `checkpoints/final_classification/2dcnn_raw_cifar_{2,5,10,25}_atk_det.pth`
- `checkpoints/final_classification/2dcnn_raw_imagenet_{2,5,10,25}_atk_det.pth`

#### 重みファイル
- `weights/yolo.weights` (YOLOv2)

### 5. サブタスク一覧

| Sub-ID | タスク | データセット | 攻撃 | 担当 | 状態 |
|--------|--------|-------------|------|------|------|
| R-01 | INRIA 1-patch 評価 | INRIA | 1p | Runner | todo |
| R-02 | INRIA 2-patch 評価 | INRIA | 2p | Runner | todo |
| R-03 | INRIA Triangular 評価 | INRIA | trig | Runner | todo |
| R-04 | VOC 1-patch 評価 | VOC | 1p | Runner | todo |
| R-05 | VOC 2-patch 評価 | VOC | 2p | Runner | todo |
| R-06 | VOC Triangular 評価 | VOC | trig | Runner | todo |
| R-07 | VOC Multi-Object 評価 | VOC | mo | Runner | todo |
| R-08 | ImageNet 1-patch 評価 | ImageNet | 1p | Runner | todo |
| R-09 | ImageNet 2-patch 評価 | ImageNet | 2p | Runner | todo |
| R-10 | ImageNet 4-patch 評価 | ImageNet | 4p | Runner | todo |
| R-11 | ImageNet Triangular 評価 | ImageNet | trig | Runner | todo |
| R-12 | CIFAR 1-patch 評価 | CIFAR | 1p | Runner | todo |
| R-13 | CIFAR 2-patch 評価 | CIFAR | 2p | Runner | todo |
| R-14 | CIFAR 4-patch 評価 | CIFAR | 4p | Runner | todo |
| R-15 | CIFAR Triangular 評価 | CIFAR | trig | Runner | todo |
| R-16 | 結果集計・論文比較表作成 | - | - | Analyst | todo |

---

## Sub-Task R-01: INRIA 1-patch 評価

### コマンド
```bash
python saliuitl.py \
  --inpaint biharmonic \
  --imgdir data/inria/clean \
  --patch_imgdir data/inria/1p \
  --dataset inria \
  --det_net_path checkpoints/final_detection/2dcnn_raw_inria_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step 5 \
  --inpainting_step 5 \
  --effective_files data/inria/1p/effective_1p.npy \
  --n_patches 1
```

### 期待される出力
- Recovery Rate (RR)
- Lost Prediction Rate (LPR)
- Adversarial nmAP
- Clean nmAP

### 論文値（比較対象）
- RR: 0.5909, LPR: 0.0152
- Adv. nmAP: 0.6897, Clean nmAP: 0.9998

---

## Sub-Task R-02: INRIA 2-patch 評価

### コマンド
```bash
python saliuitl.py \
  --inpaint biharmonic \
  --imgdir data/inria/clean \
  --patch_imgdir data/inria/2p \
  --dataset inria \
  --det_net_path checkpoints/final_detection/2dcnn_raw_inria_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step 5 \
  --inpainting_step 5 \
  --effective_files data/inria/2p/effective_2p.npy \
  --n_patches 2
```

### 論文値
- RR: 0.3871, LPR: 0.0
- Adv. nmAP: 0.5998, Clean nmAP: 1.0

---

## Sub-Task R-03: INRIA Triangular 評価

### コマンド
```bash
python saliuitl.py \
  --inpaint biharmonic \
  --imgdir data/inria/clean \
  --patch_imgdir data/inria/trig \
  --dataset inria \
  --det_net_path checkpoints/final_detection/2dcnn_raw_inria_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step 5 \
  --inpainting_step 5 \
  --effective_files data/inria/trig/effective_1p.npy \
  --n_patches 1
```

### 論文値
- RR: 0.4737, LPR: 0.0526
- Adv. nmAP: 0.7034, Clean nmAP: 0.9987

---

## Sub-Task R-04 ~ R-07: VOC 評価

### R-04: VOC 1-patch
```bash
python saliuitl.py \
  --inpaint biharmonic \
  --imgdir data/voc/clean \
  --patch_imgdir data/voc/1p \
  --dataset voc \
  --det_net_path checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step 5 \
  --inpainting_step 5 \
  --effective_files data/voc/1p/effective_1p.npy \
  --n_patches 1
```
論文値: RR: 0.5404, LPR: 0.0293, Adv: 0.5094, Clean: 0.9950

### R-05: VOC 2-patch
```bash
python saliuitl.py \
  --imgdir data/voc/clean \
  --patch_imgdir data/voc/2p \
  --dataset voc \
  --det_net_path checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth \
  --effective_files data/voc/2p/effective_2p.npy \
  --n_patches 2
```
論文値: RR: 0.5376, LPR: 0.0125, Adv: 0.5088, Clean: 0.9940

### R-06: VOC Triangular
```bash
python saliuitl.py \
  --imgdir data/voc/clean \
  --patch_imgdir data/voc/trig \
  --dataset voc \
  --det_net_path checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth \
  --effective_files data/voc/trig/effective_1p.npy \
  --n_patches 1
```
論文値: RR: 0.4244, LPR: 0.0348, Adv: 0.5043, Clean: 0.9942

### R-07: VOC Multi-Object
```bash
python saliuitl.py \
  --imgdir data/voc/clean \
  --patch_imgdir data/voc/mo \
  --dataset voc \
  --det_net_path checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth \
  --effective_files data/voc/mo/effective_mop.npy \
  --n_patches 1
```
論文値: RR: 0.3955, LPR: 0.0095, Adv: 0.3563, Clean: 0.9877

---

## Sub-Task R-08 ~ R-11: ImageNet 評価

### R-08: ImageNet 1-patch
```bash
python saliuitl.py \
  --imgdir data/imagenet/clean \
  --patch_imgdir data/imagenet/1p \
  --dataset imagenet \
  --det_net_path checkpoints/final_classification/2dcnn_raw_imagenet_5_atk_det.pth \
  --effective_files data/imagenet/1p/effective_1p.npy \
  --n_patches 1
```
論文値: RR: 0.8869, LPR: 0.0071

### R-09: ImageNet 2-patch
論文値: RR: 0.8535, LPR: 0.0061

### R-10: ImageNet 4-patch
論文値: RR: 0.8436, LPR: 0.0086

### R-11: ImageNet Triangular
論文値: RR: 0.5065, LPR: 0.0612

---

## Sub-Task R-12 ~ R-15: CIFAR-10 評価

### R-12: CIFAR 1-patch
```bash
python saliuitl.py \
  --imgdir data/cifar/clean \
  --patch_imgdir data/cifar/1p \
  --dataset cifar \
  --det_net_path checkpoints/final_classification/2dcnn_raw_cifar_5_atk_det.pth \
  --effective_files data/cifar/1p/effective_1p.npy \
  --n_patches 1
```
論文値: RR: 0.9738, LPR: 0.0008

### R-13: CIFAR 2-patch
論文値: RR: 0.9789, LPR: 0.0006

### R-14: CIFAR 4-patch
論文値: RR: 0.9747, LPR: 0.0

### R-15: CIFAR Triangular
論文値: RR: 0.8566, LPR: 0.0

---

## Sub-Task R-16: 結果集計・論文比較表作成

### 担当
Result-Analyst

### 入力
- 各実験の出力ログ（R-01 ~ R-15）

### 出力
- `analysis/tables/reproduction_table1.csv`: Table 1 再現結果
- `analysis/tables/reproduction_table2.csv`: Table 2 再現結果
- `analysis/tables/reproduction_comparison.md`: 論文値との比較

### フォーマット
```csv
dataset,attack,paper_rr,repro_rr,paper_lpr,repro_lpr,diff_rr,diff_lpr
INRIA,1p,0.5909,X.XXXX,0.0152,X.XXXX,X.XXXX,X.XXXX
...
```

---

## 6. 成功条件（Acceptance Criteria）

```text
- [AC-1] 全15シナリオ（R-01〜R-15）がエラーなく実行完了
- [AC-2] 各シナリオで RR, LPR が数値として出力される
- [AC-3] 物体検出シナリオ（INRIA/VOC）で nmAP が出力される
- [AC-4] 再現値と論文値の差異が ±5% 以内（許容誤差）
- [AC-5] 比較表が analysis/tables/ に生成される
```

---

## 7. 制約・禁止事項

```text
- **全実験はDockerコンテナ内で実行すること（必須）**
  - コマンド形式: docker compose run --rm saliuitl python saliuitl.py ...
- ensemble_step = 5 固定（論文のデフォルト設定）
- inpainting = biharmonic 固定
- パラメータチューニング禁止
- effective_files は各データセット付属のものを使用
```

### Docker実行コマンド形式
```bash
# 基本形式
docker compose run --rm saliuitl python saliuitl.py [OPTIONS]

# 例: CIFAR 1-patch
docker compose run --rm saliuitl python saliuitl.py \
  --inpaint biharmonic \
  --imgdir data/cifar/clean \
  --patch_imgdir data/cifar/1p \
  --dataset cifar \
  --det_net_path checkpoints/final_classification/2dcnn_raw_cifar_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step 5 \
  --inpainting_step 5 \
  --effective_files data/cifar/1p/effective_1p.npy \
  --n_patches 1
```

---

## 8. 既知の問題・確認事項

```text
1. INRIA の multi-object (mo) データが見つからない
   → 論文では INRIA-MO の結果があるが、data/inria/mo/ が存在しない
   → 対応: VOC-MO のみ評価するか、データ補完が必要

2. ResNet50 チェックポイントの有無
   → ImageNet/CIFAR 用の ResNet50 重みが必要
   → checkpoints/ にあるのは AD モデルのみ
```

---

## 9. 実行順序（推奨）

1. **Phase 1**: 環境確認（依存関係、GPU、データ整合性）
2. **Phase 2**: CIFAR 1-patch (R-12) で動作確認（軽量）
3. **Phase 3**: 全シナリオ実行（R-01 ~ R-15）
4. **Phase 4**: 結果集計（R-16）

---

## 10. 履歴

```text
- 2026-02-01: Lead agent により作成（論文再現タスク）
- 2026-02-02: 再現実験完了、改善実験（閾値スイープ、クリーン評価）完了、画像保存機能追加
- 2026-02-03: 計算時間比較実験完了、スライド資料生成完了
- 2026-02-04: スライド表画像化、失敗分析図作成、ADチェックポイント確認、nmAP実験環境確認
- 2026-02-04: マスクサイズ上限（5.5%）説明図作成、スライド更新
- 2026-02-05: Oracle Inpainting Test全データセット実施完了
- 2026-02-05: Oracle Test詳細考察完了（docs/notes/oracle_test_analysis.md）
- 2026-02-06: スライド構成改善（12枚、可視化・Oracle Test強調版）
- 2026-02-06: スライド草案v2作成、日本語図表6点作成
- 2026-02-08: 復元マスク面積の考察、可視化/評価乖離の発見・修正実装
- 2026-02-09: 検知ステージ徹底調査、4属性グラフ再現実験完了
```

---

## 11. 次のアクション（2026-02-09更新）

### 完了済み（2026-02-09）
- [x] **検知ステージ徹底調査** ✅
  - ドキュメント: `docs/notes/detection_stage_investigation.md`
  - 4属性の正確な定義をコードから特定
  - CLAUDE.md記述との相違点を6項目発見・記録
  - FM解像度は208×208（第1 maxpool）、二値化は`max(FM)*beta`
- [x] **4属性グラフ再現実験**（TASK-20260209-DETFEAT） ✅
  - VOC 1-patch 26画像で clean/attacked の4属性を抽出
  - AD Score: Attacked平均=0.9999, Clean平均=0.0245（完全分離）
  - 全4属性でβ=0.05〜0.30に乖離集中
  - スクリプト: `scripts/extract_detection_features.py`
  - CSV + 5枚のグラフ → `experiments/exp_20260209_detection_features/`
- [x] **スライド記載方針の策定** ✅
  - 4属性の推奨名称・説明文・グラフとの対応を整理

### 完了済み（2026-02-08）
- [x] **復元マスク面積の考察** ✅
  - ドキュメント: `docs/notes/recovery_mask_analysis.md`
  - 可視化の `my_mask` 面積は 4.3-10.9%（5枚中4枚が5.5%超）
  - over-masking メカニズム解明（bfm_old重み付け、低beta全面マスク）
  - 3層ボトルネック構造の特定（検出率 > マスク精度 > IP品質）
- [x] **可視化/評価乖離の発見** ✅
  - 可視化: 最終beta（最悪ケース）の画像を表示
  - 評価: 全betaの検出ボックスを蓄積・NMS統合
  - 両者が根本的に異なることを発見
- [x] **可視化修正の実装** ✅
  - `saliuitl.py` に `best_viz_img`（最多検出betaの画像）トラッキングを追加
  - "Recovered" パネルを最多検出beta画像に変更
  - per-beta統計表示を追加

### 完了済み（2026-02-06）
- [x] **スライド構成の改善** ✅
  - 13枚構成 → 12枚構成（可視化・Oracle Test強調版）
  - 手法説明を1枚に圧縮
- [x] **スライド草案v2作成** ✅
  - ファイル: `docs/slides_draft_v2.md`
- [x] **スライド用図表作成（日本語版）** ✅
  - `oracle_test_comparison.png`: 全15パターン詳細比較
  - `oracle_test_summary.png`: タスク別平均比較
  - `bottleneck_hierarchy.png`: ボトルネック階層図
  - `bottleneck_table.png`: 改善余地の表
  - `success_definition.png`: 「成功」定義と乖離
  - `oracle_definition.png`: Oracle Inpaintingの定義
  - スクリプト: `scripts/create_slide_figures_v2_ja.py`

### 完了済み（2026-02-05）
- [x] TASK-20260205-ORACLE: Oracle Inpainting Test全データセット ✅
- [x] Oracle Test結果の詳細考察 ✅

### 完了済み（2026-02-04）
- [x] マスクサイズ上限（5.5%）説明図の作成 ✅
- [x] スライド用表のLaTeX画像化（6点生成） ✅

### 優先度: 高（発表準備）
- [ ] **スライドPPTXへの変換**
- [ ] **復元画像サンプルの選定**（スライド7用）
  - `experiments/exp_20260202_viz_improved/figures/` から選定
- [ ] **4属性グラフのスライド組み込み**
  - `experiments/exp_20260209_detection_features/figures/` の図を使用
  - 推奨: `mean_raw_attributes.png`（全体傾向）+ `single_*.png`（個別例）
- [ ] **発表練習**

### 完了済み（2026-02-08 実験実行）
- [x] **可視化修正のテスト実行**（TASK-20260208-VIZTEST） ✅
  - VOC 1p: RR=0.5385（回帰テスト合格）、5枚の可視化生成
  - best betaマスク面積: 0.3-2.6%（累積の約1/6）
- [x] **per-beta統計の定量分析**（TASK-20260208-BETASTATS） ✅
  - VOC 26画像、INRIA 23画像でBETA_STATS収集
  - **核心的発見**: 全画像の63.3%でbest beta < 0.40
  - beta範囲制限は壊滅的（best betaを失う画像が過半数）
- [x] **beta範囲制限の効果検証**（TASK-20260208-BETARANGE） ✅ → **実行不要と判断**
  - BETASTATSの結果から、低betaカットは有害と結論
  - neulim=0.1のVOC RR -11.5%低下がこれを裏付け
- [x] **neulim閾値チューニング**（TASK-20260208-NEULIM） ✅
  - neulim=0.1: VOC -11.5%, INRIA -4.2%
  - neulim=0.2/0.3: VOC -3.8%, INRIA 0%
  - **結論**: デフォルト(0.5)が最適、低betaは検出回復に不可欠

### 優先度: 高（評価精度改善）
- [ ] **effective_filesの再生成**（TASK-20260205-EFFGEN）
  - 現状: フルデータセット用のeffective_filesをサブセット（30枚）に適用
  - 問題: 30枚中14枚しか評価対象にならない（CIFAR 1p）
  - 対策: 手元のサブセットに対してeffective_filesを再生成
  - コマンド: `--geteff` オプションで各データセット・攻撃パターンを実行

### 優先度: 中
- [ ] Table 2 (nmAP) 再現実験の実行（全8シナリオ）
- [ ] **検出率向上の検討**: INRIA trigのDetected=54.5%が低い原因調査
  - DBSCANパラメータ調整（eps, min_pts）
  - 検出閾値調整（nn_det_threshold）
- [ ] **AD汎化性能の検証**（TASK-20260205-ADGEN）
  - クロスデータセット評価（INRIA用ADでVOCを評価）
  - クロス攻撃評価（1p用ADでtrig攻撃を評価）
  - 関連研究との比較検討

### 優先度: 低
- [ ] 異なるインペインティング手法（zero, mean, diffusion）との比較実験
- [ ] **関連研究の詳細調査**（TASK-20260205-RELATED）
  - NutNet, DIFFender, PATCHOUT等の手法比較
  - Saliuitlの位置づけ・限界の明確化
- [ ] **データセット拡張**（TASK-20260205-DATAUG）
  - ImageNet-Patchの活用
  - パッチ変換による拡張（回転・移動・スケール）
  - ADの汎化性能向上のための学習データ多様化
- [ ] 高解像度特徴マップ（Layer 10: 52×52）での実験

---

# TASK ENTRIES: 計算時間比較実験

---

## TASK-20260203-PERF: 証明可能防御と提案手法の計算時間比較

### 1. タスク基本情報

```yaml
task:
  id: TASK-20260203-PERF
  title: "証明可能防御と提案手法の計算時間比較"
  owner: Lead
  assigned_agents:
    - Experiment-Runner
    - Result-Analyst
  status: completed
  priority: high
  created: 2026-02-03
  completed: 2026-02-03
```

### 2. 背景・目的（Why）

```text
[背景]
- 論文 Figure 4(a) で計算コストの比較が示されている
- 証明可能防御（Certifiable Defense）は高い保証を提供するが計算コストが高い
- Saliuitlは ensemble size によって計算コストと性能のトレードオフが可能

[目的]
- Saliuitlの計算時間を ensemble_step 変動で計測
- 論文 Figure 4(a) から既存手法の値を抽出し比較表を作成
- スライド用のグラフを生成
```

### 3. 論文 Figure 4(a) の比較対象

| 手法 | カテゴリ | 計測対象 |
|------|---------|---------|
| Saliuitl (\|B\|=4,10,20,50) | 提案手法 | 実測 |
| Themis | Empirical | 論文値 |
| Certifiable (Object Seeker / Patch Cleanser) | 証明可能防御 | 論文値 |
| Jedi | Empirical | 論文値 |

### 4. 論文から抽出した概算値（Figure 4(a)）

#### 物体検出（INRIA / VOC）

| Dataset | Attack | Saliuitl \|B\|=4 | Saliuitl \|B\|=20 | Themis | Object Seeker | Jedi |
|---------|--------|-----------------|-------------------|--------|---------------|------|
| INRIA | 1p | ~0.3s | ~1.5s | ~0.2s | ~3.5s | ~2.0s |
| INRIA | 2p | ~0.3s | ~1.5s | ~0.2s | ~3.5s | ~2.0s |
| INRIA | T | ~0.3s | ~1.5s | ~0.2s | ~3.5s | ~2.0s |
| INRIA | MO | ~0.3s | ~1.5s | ~0.2s | ~3.5s | ~2.0s |
| VOC | 1p | ~0.3s | ~1.5s | ~0.2s | ~2.0s | ~1.0s |
| VOC | 2p | ~0.3s | ~1.5s | ~0.2s | ~2.0s | ~1.0s |
| VOC | T | ~0.3s | ~1.5s | ~0.2s | ~2.0s | ~1.0s |
| VOC | MO | ~0.3s | ~1.5s | ~0.2s | ~2.0s | ~1.0s |

#### 画像分類（ImageNet / CIFAR-10）

| Dataset | Attack | Saliuitl \|B\|=4 | Saliuitl \|B\|=20 | Themis | Patch Cleanser | Jedi |
|---------|--------|-----------------|-------------------|--------|----------------|------|
| ImageNet | 1p | ~0.1s | ~0.5s | ~0.1s | ~1.0s | ~0.5s |
| ImageNet | 2p | ~0.1s | ~0.5s | ~0.1s | ~1.0s | ~0.5s |
| ImageNet | T | ~0.1s | ~0.5s | ~0.1s | ~1.0s | ~0.5s |
| ImageNet | 4p | ~0.1s | ~0.5s | ~0.1s | ~1.0s | ~0.5s |
| CIFAR | 1p | ~0.05s | ~0.2s | ~0.05s | ~0.5s | ~0.2s |
| CIFAR | 2p | ~0.05s | ~0.2s | ~0.05s | ~0.5s | ~0.2s |
| CIFAR | 4p | ~0.05s | ~0.2s | ~0.05s | ~0.5s | ~0.2s |
| CIFAR | T | ~0.05s | ~0.2s | ~0.05s | ~0.5s | ~0.2s |

**注意**: 上記は論文グラフからの目視読み取り値。正確な数値は論文著者に確認が必要。

### 5. サブタスク一覧

| Sub-ID | タスク | 担当 | 状態 |
|--------|--------|------|------|
| P-01 | Saliuitl時間計測（VOC 1p, ensemble_step=5,10,25） | Runner | ✅ done |
| P-02 | Saliuitl時間計測（INRIA 1p, ensemble_step=5,10,25） | Runner | ✅ done |
| P-03 | Saliuitl時間計測（CIFAR 1p） | Runner | ⏭️ skipped |
| P-04 | 論文Figure 4(a)から既存手法の値を正確に抽出 | Analyst | ✅ done |
| P-05 | 比較表・グラフ作成 | Analyst | ✅ done |

### 5.1. 実測結果（2026-02-03）

| Dataset | \|B\| | Paper(s) | Measured(s) | Ratio |
|---------|-------|----------|-------------|-------|
| VOC | 4 | 0.30 | 0.068 | 0.23 |
| VOC | 10 | 0.75 | 0.200 | 0.27 |
| VOC | 20 | 1.50 | 0.455 | 0.30 |
| INRIA | 4 | 0.30 | 0.071 | 0.24 |
| INRIA | 10 | 0.75 | 0.202 | 0.27 |
| INRIA | 20 | 1.50 | 0.409 | 0.27 |

**備考**: 実測値は論文値の約23-30%。ハードウェア環境の違い（論文: NVIDIA T4）が主因。

---

## Sub-Task P-01: Saliuitl時間計測（VOC 1-patch）

### コマンド

```bash
# ensemble_step=5 (|B|=20)
docker compose run --rm saliuitl python saliuitl.py \
  --dataset voc \
  --imgdir data/voc/clean \
  --patch_imgdir data/voc/1p \
  --det_net_path checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --effective_files data/voc/1p/effective_1p.npy \
  --ensemble_step 5 \
  --inpainting_step 5 \
  --performance

# ensemble_step を 2, 10, 25, 50 に変えて繰り返し
# |B| = 100 / ensemble_step
# ensemble_step=2  -> |B|=50
# ensemble_step=5  -> |B|=20
# ensemble_step=10 -> |B|=10
# ensemble_step=25 -> |B|=4
# ensemble_step=50 -> |B|=2
```

### 出力フォーマット

```csv
dataset,attack,ensemble_step,ensemble_size,time_mean,time_std,time_q1,time_q3
VOC,1p,5,20,X.XXX,X.XXX,X.XXX,X.XXX
VOC,1p,10,10,X.XXX,X.XXX,X.XXX,X.XXX
VOC,1p,25,4,X.XXX,X.XXX,X.XXX,X.XXX
```

---

## Sub-Task P-05: 比較表・グラフ作成

### 入力
- P-01〜P-03 の計測結果
- P-04 の論文値抽出結果

### 出力
- `analysis/tables/computational_cost.csv`: 計算時間比較表
- `analysis/figures/computational_cost.pdf`: 棒グラフ（論文Figure 4(a)再現）
- `docs/slides_material/perf_comparison.png`: スライド用PNG

### グラフ仕様
- X軸: データセット・攻撃シナリオ
- Y軸: 時間（秒）
- 系列: Saliuitl各サイズ, Themis, Certifiable, Jedi
- エラーバー: Q1-Q3

---

## 6. 成功条件（Acceptance Criteria）

```text
- [AC-1] Saliuitlの時間計測が少なくとも3シナリオで完了
- [AC-2] ensemble_step変動による時間変化が記録される
- [AC-3] 論文値との比較表が生成される
- [AC-4] スライド用グラフ（PDF/PNG）が生成される
```

---

## 7. 制約・禁止事項

```text
- 計測は Docker コンテナ内で実行
- --performance オプションを使用（CPU時間計測）
- 各設定で複数回実行して統計値を取得（推奨: 3回以上）
```

---

# TASK ENTRIES: スライド資料作成

---

## TASK-20260203-SLIDES: 発表スライド用資料作成

### 1. タスク基本情報

```yaml
task:
  id: TASK-20260203-SLIDES
  title: "発表スライド用資料作成"
  owner: Lead
  assigned_agents:
    - Result-Analyst
  status: completed
  priority: medium
  created: 2026-02-03
  completed: 2026-02-03
```

### 2. 背景・目的（Why）

```text
[背景]
- 再現実験、分析実験の結果をスライド発表用にまとめる必要がある
- 論文の図表を参考に、再現結果を視覚的に示す

[目的]
- 発表スライドに挿入可能な図表を生成
- 論文との比較を視覚的に示す
- 手法の特徴（検出→復元パイプライン）を図解
```

### 3. 作成する資料一覧

| ID | 資料名 | 内容 | フォーマット |
|----|--------|------|-------------|
| S-01 | Table 1 再現比較 | RR/LPR の論文値 vs 再現値 | PDF/PNG |
| S-02 | Table 2 再現比較 | nmAP の論文値 vs 再現値 | PDF/PNG |
| S-03 | 計算時間比較 | Figure 4(a) 再現 | PDF/PNG |
| S-04 | 復元画像サンプル | Clean/Attacked/Recovered 比較 | PNG |
| S-05 | パイプライン図 | 検出→復元フロー | PDF/PNG |
| S-06 | 失敗分析サマリー | 回復品質問題の要約 | PNG |

### 4. サブタスク一覧

| Sub-ID | タスク | 依存 | 担当 | 状態 |
|--------|--------|------|------|------|
| S-01 | Table 1 再現比較グラフ | RESULT_LOG | Analyst | ✅ done |
| S-02 | Table 2 再現比較グラフ | RESULT_LOG | Analyst | ✅ done |
| S-03 | 計算時間比較グラフ | P-05 | Analyst | ✅ done |
| S-04 | 復元画像サンプル選定・整形 | exp_20260202_viz | Analyst | ✅ done |
| S-05 | パイプライン図作成 | - | Analyst | ✅ done |
| S-06 | 失敗分析サマリー図 | failure_analysis | Analyst | ⏭️ pending |

### 4.1. 生成物一覧（2026-02-03）

| ファイル | 内容 |
|---------|------|
| `table1_comparison.pdf/png` | Table 1 (RR) 論文vs再現 |
| `table2_comparison.pdf/png` | Table 2 (nmAP) 論文vs再現 |
| `computational_cost.pdf/png` | 計算時間比較（論文値） |
| `timing_paper_vs_measured.pdf/png` | 論文値vs実測値 |
| `timing_scaling.pdf/png` | スケーリンググラフ |
| `rr_by_dataset_detection.pdf/png` | データセット別RR |
| `pipeline_diagram.md` | パイプライン図（Mermaid/ASCII） |
| `sample_voc_*.png` | VOC復元画像サンプル |
| `sample_inria_*.png` | INRIA復元画像サンプル |

---

## Sub-Task S-01: Table 1 再現比較グラフ

### 入力データ
- `RESULT_LOG.md` の R-2026-02-01 セクション
- 論文 Table 1 の値

### 出力
- `docs/slides_material/table1_comparison.pdf`
- `docs/slides_material/table1_comparison.png`

### グラフ仕様
- グループ棒グラフ（Paper vs Repro）
- X軸: データセット-攻撃
- Y軸: Recovery Rate (%)
- エラーバー: なし（単一値）
- カラー: 論文=青系, 再現=緑系

### Pythonスクリプト例

```python
import matplotlib.pyplot as plt
import pandas as pd

# データ準備
data = {
    'Attack': ['CIFAR-1', 'CIFAR-2', 'CIFAR-4', 'CIFAR-T',
               'ImageNet-1', 'ImageNet-2', 'ImageNet-4', 'ImageNet-T',
               'INRIA-1', 'INRIA-2', 'INRIA-T',
               'VOC-1', 'VOC-2', 'VOC-T', 'VOC-MO'],
    'Paper_RR': [0.9738, 0.9789, 0.9747, 0.8566,
                 0.8869, 0.8535, 0.8436, 0.5065,
                 0.5909, 0.3871, 0.4737,
                 0.5404, 0.5376, 0.4244, 0.3955],
    'Repro_RR': [0.9286, 0.8000, 0.9333, 0.8667,
                 0.8667, 0.6667, 0.4667, 0.4000,
                 0.7917, 0.8571, 0.3636,
                 0.5385, 0.5263, 0.1500, 0.2593]
}

# プロット
fig, ax = plt.subplots(figsize=(14, 6))
# ... グラフ作成コード
plt.savefig('docs/slides_material/table1_comparison.pdf')
plt.savefig('docs/slides_material/table1_comparison.png', dpi=300)
```

---

## Sub-Task S-04: 復元画像サンプル選定・整形

### 入力
- `experiments/exp_20260202_viz_improved/figures/*.png`
- `experiments/exp_20260202_recovery_viz/figures/*.png`

### 出力
- `docs/slides_material/recovery_samples_voc.png`
- `docs/slides_material/recovery_samples_inria.png`

### 仕様
- 3x3 または 2x3 のグリッドレイアウト
- Success/Failed の両方を含む
- キャプション付き

---

## Sub-Task S-05: パイプライン図作成

### 内容
論文 Figure 2 を参考に、Saliuitlのパイプラインを図解

```
[入力画像 xi]
    ↓
[特徴マップ抽出 h(.)]
    ↓
[二値化 (β閾値セット BD)]
    ↓
[属性抽出 (DBSCAN)]
    ↓
[Attack Detector AD]
    ↓ AD(s) > α*?
    ├─ NO → [クリーン予測を返す h(xi)]
    └─ YES → [復元ステージ]
              ↓
         [マスク生成 (β閾値セット BR)]
              ↓
         [インペインティング]
              ↓
         [復元予測を返す ŷi]
```

### 出力
- `docs/slides_material/pipeline_diagram.pdf`
- `docs/slides_material/pipeline_diagram.png`

---

## 5. 成功条件（Acceptance Criteria）

```text
- [AC-1] 全6種類の資料が生成される
- [AC-2] PDF/PNGの両形式で出力
- [AC-3] 論文品質のスタイル（Times New Roman, 適切な解像度）
- [AC-4] docs/slides_material/ に整理して配置
```

---

## 6. グラフスタイル規約

```python
# 共通スタイル設定
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1
})

# カラーパレット
COLORS = {
    'paper': '#1f77b4',      # 青
    'repro': '#2ca02c',      # 緑
    'saliuitl': '#ff7f0e',   # オレンジ
    'certifiable': '#d62728', # 赤
    'themis': '#9467bd',      # 紫
}
```

---

## 7. 履歴

```text
- 2026-02-03: Lead agent により作成
- 2026-02-03: 図表生成完了、タスク完了
```

---

# TASK ENTRIES: スライド草案作成

---

## TASK-20260203-DRAFT: 発表スライド草案作成

### 1. タスク基本情報

```yaml
task:
  id: TASK-20260203-DRAFT
  title: "発表スライド草案作成"
  owner: Lead
  assigned_agents:
    - Lead
  status: completed
  priority: high
  created: 2026-02-03
  completed: 2026-02-03
```

### 2. 背景・目的（Why）

```text
[背景]
- TASK-20260203-SLIDES で図表は生成済み
- 実際のスライド（草案）を作成する必要がある

[目的]
- 発表用スライドの草案をMarkdown形式で作成
- 各スライドの内容・構成を明確化
- 生成した図表の配置を決定
```

### 3. スライド構成（最終版・12枚）

中間発表（`hoshino_中間発表.pptx`）をベースに簡潔化。

| # | タイトル | 内容 | 使用図表 | 時間 |
|---|---------|------|---------|------|
| 1 | タイトル | 期末発表 | - | 0:30 |
| 2 | 読んだ論文 | 論文情報 | - | 0:30 |
| 3 | 背景・課題 | 敵対的パッチ、既存手法の問題 | - | 1:00 |
| 4 | 提案手法 Saliuitl | 2段階パイプライン概要 | - | 1:30 |
| 5 | 再現実験設定 | データセット、パラメータ | - | 1:00 |
| 6 | 再現結果: Table 1 | Recovery Rate比較 | table1_comparison | 1:30 |
| 7 | 再現結果: Table 2 | nmAP比較 | table2_comparison | 1:00 |
| 8 | 計算時間比較 | 論文値vs実測値 | timing_paper_vs_measured | 1:00 |
| 9 | **問題発見** | パッチ残存の発見 | sample_voc_* | 1:30 |
| 10 | **原因分析** | 解像度ミスマッチ等 | - | 1:30 |
| 11 | **追加実験** | Attention Hijacking | - | 1:30 |
| 12 | 結論 | まとめ、限界、今後の課題 | - | 1:00 |

**合計: 約13分**

### 4. サブタスク一覧

| Sub-ID | タスク | 担当 | 状態 |
|--------|--------|------|------|
| D-01 | スライド草案（Markdown） | Lead | ✅ done |
| D-02 | 図表配置確認 | Lead | ✅ done |
| D-03 | 発表ノート作成 | Lead | ✅ done |

### 5. 出力

- `docs/slides_draft_final.md`: 期末発表スライド草案（最終版） ✅
- `docs/slides_draft.md`: 初期草案（参考用）
- `docs/slides_notes.md`: 発表ノート

### 5.1. 生成物詳細

| ファイル | 内容 |
|---------|------|
| `slides_draft_final.md` | **12スライド構成の最終草案（中間発表ベース）** |
| `slides_draft.md` | 初期草案（13スライド版） |
| `slides_notes.md` | 発表ノート（Q&A想定含む） |

### 6. 成功条件（Acceptance Criteria）

```text
- [AC-1] 全12スライドの草案が作成される ✅
- [AC-2] 各スライドに使用する図表が明記される ✅
- [AC-3] 発表時間の目安が記載される ✅（約13分）
- [AC-4] 中間発表をベースに簡潔化される ✅
```

### 7. 履歴

```text
- 2026-02-03: Lead agent により作成
- 2026-02-03: 初期草案（13スライド版）作成
- 2026-02-03: 中間発表ベースで簡潔化、最終版（12スライド）作成
```

---

# TASK ENTRIES: 2026-02-02 追加実験・分析

---

## TASK-20260202-ANALYSIS: 検出・復元詳細分析

### 1. タスク基本情報

```yaml
task:
  id: TASK-20260202-ANALYSIS
  title: "検出・復元パイプラインの詳細分析"
  owner: Lead
  assigned_agents:
    - Experiment-Runner
    - Result-Analyst
  status: completed
  priority: high
  created: 2026-02-02
  completed: 2026-02-02
```

### 2. サブタスク一覧

| Sub-ID | タスク | 担当 | 状態 | 結果参照 |
|--------|--------|------|------|----------|
| A | 検出スコア分布調査 | Runner | ✅ done | R-2026-02-02-A |
| B | 復元画像可視化実験 | Runner | ✅ done | R-2026-02-02-B |
| C | nmAP再現実験（Table 2） | Runner | ✅ done | R-2026-02-02-C |
| D | Detection Mask可視化改善 | Builder | ✅ done | R-2026-02-02-D |
| E | 回復画像品質問題分析 | Analyst | ✅ done | R-2026-02-02-E |
| F | 視覚的回復品質改善実験 | Runner | ✅ done | R-2026-02-02-F |

### 3. 主要な発見

1. **検出スコア分布**: 全サンプルでスコア > 0.99（閾値変更が影響しない理由）
2. **パッチ残存問題**: 「成功」判定でも敵対的パッチが視覚的に残存
3. **解像度ミスマッチ**: 26×26→416×416のスケーリングが根本的ボトルネック
4. **Attention Hijacking**: パッチが検出器の注意を対象物体から奪う

### 4. 生成物

| ファイル | 内容 |
|---------|------|
| experiments/exp_20260202_recovery_viz/ | 復元画像可視化 |
| experiments/exp_20260202_nmap/ | nmAP再現実験 |
| experiments/exp_20260202_viz_improved/ | 改善版可視化 |
| experiments/exp_20260202_failure_analysis/ | 失敗分析 |
| experiments/exp_20260202_visual_recovery/ | 視覚的回復実験 |

---

# TASK ENTRIES: コード改善・ツール作成

---

## TASK-TOOLS: 分析ツール・スクリプト作成

### 1. タスク基本情報

```yaml
task:
  id: TASK-TOOLS
  title: "分析ツール・スクリプト作成"
  owner: Lead
  status: completed
  created: 2026-02-02
  completed: 2026-02-04
```

### 2. saliuitl.py への機能追加（2026-02-02）

| オプション | 説明 |
|-----------|------|
| `--save_images` | 復元画像を保存（Clean/Attacked/Recovered/Mask） |
| `--save_images_dir` | 保存先ディレクトリ |
| `--save_images_limit` | 保存枚数上限 |
| `--save_scores` | 検出スコアを保存 |
| `--save_outcomes` | 検出結果詳細を保存 |

**関連**: DECISIONS.md D-2026-02-02 参照

### 3. 新規スクリプト一覧

| ファイル | 用途 | 作成日 |
|---------|------|--------|
| `compute_nmap.py` | nmAP計算 | 2026-02-02 |
| `analysis/oracle_inpaint_test.py` | Oracle inpaintingテスト | 2026-02-02 |
| `analysis/gradcam_visualize.py` | Grad-CAM可視化 | 2026-02-02 |
| `analysis/plot_nmap_results.py` | nmAP結果プロット | 2026-02-02 |
| `analysis/plot_slides_figures.py` | スライド図表生成 | 2026-02-03 |
| `analysis/plot_timing_comparison.py` | 計算時間比較 | 2026-02-03 |
| `analysis/extract_timing_results.py` | 計算時間抽出 | 2026-02-03 |
| `scripts/generate_table_images.py` | LaTeX表画像化 | 2026-02-04 |
| `scripts/create_failure_analysis_figure.py` | 失敗分析図生成 | 2026-02-04 |
| `scripts/replace_tables_in_html.py` | HTML表置換 | 2026-02-04 |
| `scripts/create_mask_size_limit_figure.py` | マスクサイズ上限説明図 | 2026-02-04 |

### 4. 履歴

```text
- 2026-02-02: saliuitl.py機能追加、分析スクリプト作成
- 2026-02-03: スライド用図表生成スクリプト作成
- 2026-02-04: 表画像化・失敗分析図生成スクリプト作成
- 2026-02-04: 監査により本エントリ追加
```

---

# TASK ENTRIES: Oracle Inpainting Test

---

## TASK-20260205-ORACLE: Oracle Inpainting Test（全データセット）

### 1. タスク基本情報

```yaml
task:
  id: TASK-20260205-ORACLE
  title: "Oracle Inpainting Test - 全データセット評価"
  owner: Lead
  assigned_agents:
    - Experiment-Runner
  status: completed
  priority: high
  created: 2026-02-05
  completed: 2026-02-05
```

### 2. 背景・目的（Why）

```text
[背景]
- R-2026-02-02-Eで「パッチ残存問題」が発見された
- R-2026-02-02-Fで小規模Oracle Test（VOC/INRIA各5画像）を実施
- 全データセットでの定量的評価が未実施

[目的]
- 全データセット（INRIA, VOC, CIFAR, ImageNet）でOracle Testを実施
- Biharmonic再現実験との差分を定量化
- マスク精度がボトルネックであることを検証
```

### 3. Oracle Inpaintingの定義

**Oracle Inpainting (`--inpaint oracle`)**:
- システムが生成したマスク領域に、クリーン画像のピクセルをそのまま貼り付ける
- **インペインティング品質の上限**を示す
- **注意**: マスクの位置・形状は変わらない（マスク精度の問題は残る）

### 4. 結果サマリ（全15パターン）

#### 物体検出（7パターン）

| Dataset | Attack | Biharmonic RR | Oracle RR | Detected | Δ(O-B) |
|---------|--------|---------------|-----------|----------|--------|
| INRIA   | 1p     | 0.7917        | **0.8750** | 0.9583  | +0.083 |
| INRIA   | 2p     | 0.8571        | **1.0000** | 1.0000  | +0.143 |
| INRIA   | trig   | 0.3636        | **0.5455** | 0.5455  | +0.182 |
| VOC     | 1p     | 0.5385        | **0.7692** | 1.0000  | +0.231 |
| VOC     | 2p     | 0.5263        | **0.7368** | 1.0000  | +0.211 |
| VOC     | trig   | 0.1500        | **0.4500** | 0.8500  | +0.300 |
| VOC     | mo     | 0.2593        | **0.7037** | 1.0000  | +0.444 |

**平均改善**: +22.8%

#### 画像分類（8パターン）

| Dataset  | Attack | Biharmonic RR | Oracle RR | Detected | Δ(O-B) |
|----------|--------|---------------|-----------|----------|--------|
| CIFAR    | 1p     | 0.9286        | 0.9286    | 0.9286   | 0.000  |
| CIFAR    | 2p     | 0.8000        | 0.8000    | 0.8667   | 0.000  |
| CIFAR    | 4p     | 0.9333        | 0.8667    | 1.0000   | -0.067 |
| CIFAR    | trig   | 0.8667        | 0.8000    | 1.0000   | -0.067 |
| ImageNet | 1p     | 0.8667        | 0.7333    | 1.0000   | -0.133 |
| ImageNet | 2p     | 0.6667        | 0.8000    | 0.8667   | +0.133 |
| ImageNet | 4p     | 0.4667        | 0.6667    | 0.9333   | +0.200 |
| ImageNet | trig   | 0.4000        | 0.4000    | 0.6667   | 0.000  |

**平均改善**: +0.8%

### 5. 主要な発見

1. **物体検出ではOracleが効果的**
   - 平均+22.8%の改善
   - マスク精度改善の余地が大きい

2. **画像分類ではOracle効果が限定的**
   - 平均+0.8%（一部でマイナス）
   - Biharmonicでも十分な性能

3. **検出率がRRに大きく影響**
   - INRIA trig: Detected=54.5% → Oracle RR=54.5%
   - 検出されないサンプルは復元できない

4. **VOC moが最大改善**
   - +44.4%（0.2593→0.7037）
   - Multi-objectパッチへの対応改善が効果的

### 6. 成功条件（Acceptance Criteria）

```text
- [AC-1] 全15パターン（INRIA moなし）でOracle Test完了 ✅
- [AC-2] Biharmonic再現実験との比較表作成 ✅
- [AC-3] 統計サマリ（平均改善幅）算出 ✅
- [AC-4] RESULT_LOG.mdに結果記録 ✅
```

### 7. 生成物

| ファイル | 内容 |
|---------|------|
| `experiments/exp_20260205_oracle_full/results/oracle_all_results.csv` | 全15パターンCSV |
| `experiments/exp_20260205_oracle_full/results/oracle_full_comparison.md` | 詳細レポート |

### 8. 履歴

```text
- 2026-02-05: タスク作成、全15パターン実験実行、完了
```

---

# TASK ENTRIES: effective_files再生成

---

## TASK-20260205-EFFGEN: 手元データ用effective_filesの再生成

### 1. タスク基本情報

```yaml
task:
  id: TASK-20260205-EFFGEN
  title: "手元サブセット用effective_filesの再生成"
  owner: Lead
  assigned_agents:
    - Experiment-Runner
  status: todo
  priority: high
  created: 2026-02-05
```

### 2. 背景・目的（Why）

```text
[背景]
- 現在のeffective_filesはフルデータセット（数千枚）に対して生成されたもの
- 手元のデータはサブセット（約30枚/データセット）
- 結果として、30枚中14枚しか評価対象にならないケースがある（CIFAR 1p）

[問題点]
- 16枚が「uneffective」扱いだが、手元データでの攻撃成功/失敗を確認していない
- 評価の分母が不正確になる
- RR/LPRの計算が論文定義と乖離する可能性

[目的]
- 手元のサブセットに対してeffective_filesを再生成
- 全画像を評価対象にする
- 正確なRR/LPR計算を可能にする
```

### 3. 現状の問題

| Dataset | effective_files | 手元データ | 処理数 | 未評価 |
|---------|----------------|-----------|--------|--------|
| INRIA 1p | 234 | 30 | 24 | 6 |
| VOC 1p | 3612 | 29 | 26 | 3 |
| VOC mo | 27 | 29 | 27 | 2 |
| CIFAR 1p | 14 | 30 | 14 | **16** |
| ImageNet 1p | 34112 | 30 | ? | ? |

### 4. サブタスク一覧

| Sub-ID | タスク | データセット | 攻撃 | 状態 |
|--------|--------|-------------|------|------|
| EG-01 | effective再生成 | CIFAR | 1p | todo |
| EG-02 | effective再生成 | CIFAR | 2p | todo |
| EG-03 | effective再生成 | CIFAR | 4p | todo |
| EG-04 | effective再生成 | CIFAR | trig | todo |
| EG-05 | effective再生成 | ImageNet | 1p | todo |
| EG-06 | effective再生成 | ImageNet | 2p | todo |
| EG-07 | effective再生成 | ImageNet | 4p | todo |
| EG-08 | effective再生成 | ImageNet | trig | todo |
| EG-09 | effective再生成 | INRIA | 1p | todo |
| EG-10 | effective再生成 | INRIA | 2p | todo |
| EG-11 | effective再生成 | INRIA | trig | todo |
| EG-12 | effective再生成 | VOC | 1p | todo |
| EG-13 | effective再生成 | VOC | 2p | todo |
| EG-14 | effective再生成 | VOC | trig | todo |
| EG-15 | effective再生成 | VOC | mo | todo |

### 5. 実行コマンド

```bash
# CIFAR
docker compose run --rm saliuitl python saliuitl.py \
  --dataset cifar --imgdir data/cifar/clean --patch_imgdir data/cifar/1p \
  --det_net_path checkpoints/final_classification/2dcnn_raw_cifar_5_atk_det.pth \
  --det_net 2dcnn_raw --geteff

# ImageNet
docker compose run --rm saliuitl python saliuitl.py \
  --dataset imagenet --imgdir data/imagenet/clean --patch_imgdir data/imagenet/1p \
  --det_net_path checkpoints/final_classification/2dcnn_raw_imagenet_5_atk_det.pth \
  --det_net 2dcnn_raw --geteff

# INRIA
docker compose run --rm saliuitl python saliuitl.py \
  --dataset inria --imgdir data/inria/clean --patch_imgdir data/inria/1p \
  --det_net_path checkpoints/final_detection/2dcnn_raw_inria_5_atk_det.pth \
  --det_net 2dcnn_raw --geteff

# VOC
docker compose run --rm saliuitl python saliuitl.py \
  --dataset voc --imgdir data/voc/clean --patch_imgdir data/voc/1p \
  --det_net_path checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth \
  --det_net 2dcnn_raw --geteff
```

### 6. 成功条件（Acceptance Criteria）

```text
- [AC-1] 全15パターンでeffective_filesを再生成
- [AC-2] 再生成後: effective + uneffective = 手元データ数
- [AC-3] 旧effective_filesをバックアップ
- [AC-4] 再生成後のRR/LPRを再計算
```

### 7. 注意事項

```text
- --geteff は復元処理を行わず、攻撃成功/失敗のみを判定
- 判定基準:
  - 物体検出: IoU(clean_pred, attacked_pred) < 0.5 → effective
  - 画像分類: clean_pred ≠ attacked_pred → effective
- 旧ファイルは effective_1p.npy.bak 等にリネームして保存
```

### 8. 履歴

```text
- 2026-02-05: タスク作成（effective_filesの不整合発見による）
```

---

# TASK ENTRIES: AD汎化性能検証

---

## TASK-20260205-ADGEN: Attack Detectorの汎化性能検証

### 1. タスク基本情報

```yaml
task:
  id: TASK-20260205-ADGEN
  title: "Attack Detectorの汎化性能検証"
  owner: Lead
  assigned_agents:
    - Experiment-Runner
    - Research-Critic
  status: todo
  priority: medium
  created: 2026-02-05
```

### 2. 背景・目的（Why）

```text
[背景]
- ADはデータセット固有・攻撃パターン固有で学習されている
- 未知のデータセット・攻撃パターンへの汎化性能は未検証
- INRIA trigの検出率54.5%が低い理由として、ADの学習データに
  三角形パッチが含まれていない可能性がある

[問題点]
- 実運用では未知の攻撃に遭遇する可能性が高い
- データセットごとにADを再学習するコストが高い
- 論文の「汎用性」の主張に対する懸念

[目的]
- クロスデータセット・クロス攻撃評価でADの汎化性能を定量化
- Saliuitlの適用範囲・限界を明確化
```

### 3. サブタスク一覧

| Sub-ID | タスク | 内容 | 状態 |
|--------|--------|------|------|
| AG-01 | クロスデータセット評価 | INRIA用ADでVOCを評価 | todo |
| AG-02 | クロスデータセット評価 | VOC用ADでINRIAを評価 | todo |
| AG-03 | クロスデータセット評価 | CIFAR用ADでImageNetを評価 | todo |
| AG-04 | クロス攻撃評価 | 1p攻撃用ADでtrig攻撃を評価 | todo |
| AG-05 | 結果分析 | 汎化性能の定量化・考察 | todo |

### 4. 実行コマンド例

```bash
# クロスデータセット: INRIA用ADでVOCを評価
docker compose run --rm saliuitl python saliuitl.py \
  --dataset voc \
  --imgdir data/voc/clean \
  --patch_imgdir data/voc/1p \
  --det_net_path checkpoints/final_detection/2dcnn_raw_inria_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step 5

# クロス攻撃: 通常の1p用ADでtrig攻撃を評価（既存実験で実施済み）
```

### 5. 成功条件（Acceptance Criteria）

```text
- [AC-1] クロスデータセット評価で検出率・RRを計測
- [AC-2] 同一データセット評価との比較表作成
- [AC-3] 汎化性能の低下度合いを定量化
- [AC-4] 考察と論文への示唆をまとめる
```

### 6. 関連研究との比較観点

| 手法 | 汎化アプローチ | Saliuitlとの違い |
|------|--------------|-----------------|
| NutNet | クリーン画像のみで学習（OOD検出） | 攻撃パターン非依存 |
| DIFFender | Diffusionモデルで再生成 | 学習不要 |
| PATCHOUT | セマンティック一貫性で検出 | 学習不要 |

### 7. 履歴

```text
- 2026-02-05: タスク作成（AD汎化性能の懸念発見による）
```

---

# TASK ENTRIES: 関連研究調査

---

## TASK-20260205-RELATED: 敵対的パッチ防御の関連研究調査

### 1. タスク基本情報

```yaml
task:
  id: TASK-20260205-RELATED
  title: "敵対的パッチ防御の関連研究調査"
  owner: Lead
  assigned_agents:
    - Paper-Searcher
    - Research-Critic
  status: todo
  priority: low
  created: 2026-02-05
```

### 2. 背景・目的（Why）

```text
[背景]
- Saliuitlはデータセット固有のADを必要とし、汎化性能に課題がある
- 2024-2025年に汎化性能を改善した新しい手法が複数提案されている
- Saliuitlの位置づけ・限界を明確化するために関連研究の調査が必要

[目的]
- 最新の敵対的パッチ防御手法を調査
- Saliuitlとの比較表を作成
- 研究の方向性・改善案を検討
```

### 3. 調査対象論文

| 論文 | 会議/年 | アプローチ | URL |
|------|--------|-----------|-----|
| NutNet | 2024 | OOD検出（クリーンのみ学習） | [arXiv](https://arxiv.org/html/2406.10285v1) |
| DIFFender | 2025 | Diffusionモデル | [PubMed](https://pubmed.ncbi.nlm.nih.gov/40768456/) |
| Unified Detector | CVPR 2025 | 大規模学習 | [CVF](https://openaccess.thecvf.com/content/CVPR2025/papers/Kumar_A_Unified_Resilient_and_Explainable_Adversarial_Patch_Detector_CVPR_2025_paper.pdf) |
| PATCHOUT | 2025 | セマンティック一貫性 | [Springer](https://link.springer.com/article/10.1007/s11063-025-11775-5) |
| Revisiting Defenses | ICCV 2025 | ベンチマーク | [CVF](https://openaccess.thecvf.com/content/ICCV2025/supplemental/Zheng_Revisiting_Adversarial_Patch_ICCV_2025_supplemental.pdf) |

### 4. 比較観点

```text
- 汎化性能（未知データセット、未知攻撃への対応）
- 計算コスト（推論時間、学習コスト）
- 検出精度（検出率、False Positive率）
- 復元精度（RR、画像品質）
- 実用性（学習データの必要性、デプロイの容易さ）
```

### 5. 成功条件（Acceptance Criteria）

```text
- [AC-1] 5本以上の関連論文を調査
- [AC-2] Saliuitlとの比較表を作成
- [AC-3] 各手法の長所・短所をまとめる
- [AC-4] Saliuitlの改善方向性を提案
```

### 6. 出力

- `docs/notes/related_work_survey.md`: 関連研究サーベイ
- `docs/notes/method_comparison.md`: 手法比較表

### 7. 参考リソース

- [inspire-group/adv-patch-paper-list](https://github.com/inspire-group/adv-patch-paper-list)

### 8. 履歴

```text
- 2026-02-05: タスク作成（AD汎化性能調査の派生として）
```

---

# TASK ENTRIES: データセット拡張

---

## TASK-20260205-DATAUG: データセット拡張による評価・学習データの強化

### 1. タスク基本情報

```yaml
task:
  id: TASK-20260205-DATAUG
  title: "データセット拡張による評価・学習データの強化"
  owner: Lead
  assigned_agents:
    - Experiment-Runner
  status: todo
  priority: low
  created: 2026-02-05
```

### 2. 背景・目的（Why）

```text
[背景]
- 手元のデータはサブセット（約30枚/データセット）
- ADの汎化性能が低い（データセット固有・攻撃パターン固有）
- 関連研究では大規模データセット（APDE: 94,000枚）が公開されている

[目的]
- データ拡張により評価データを増やす
- 多様なパッチパターンでADの汎化性能を向上
- 公開データセットを活用して評価の信頼性を向上
```

### 3. データ拡張方法

#### 方法1: パッチ変換による拡張

```python
# 1枚の攻撃画像から複数の変形画像を生成
transformations:
  - rotation: [-22.5°, +22.5°] (5段階)
  - translation: [-68px, +68px] (5段階)
  - scale: [0.8x, 1.2x] (3段階)
  - brightness: [-20%, +20%] (3段階)

# 拡張効果: 30枚 → 30 × 75 = 2,250枚
```

#### 方法2: 公開データセットの活用

| データセット | サイズ | 用途 | URL |
|-------------|--------|------|-----|
| ImageNet-Patch | 50,000枚 | CIFAR/ImageNet評価 | https://github.com/pralab/ImageNet-Patch |
| APDE | 94,000枚 | 物体検出評価 | https://github.com/Gandolfczjh/APDE（公開待ち） |
| MS COCO | 2,693枚 | VOC代替 | 公開済み |

#### 方法3: パッチ自動生成

- DiffPatch: Diffusionモデルによるパッチ生成
- PAD: 動的敵対的学習でパッチを生成

### 4. サブタスク一覧

| Sub-ID | タスク | 内容 | 状態 |
|--------|--------|------|------|
| DA-01 | ImageNet-Patchダウンロード | 公開リポジトリから取得 | todo |
| DA-02 | パッチ変換スクリプト作成 | 回転・移動・スケール適用 | todo |
| DA-03 | 手元データ拡張 | 30枚→300枚以上に拡張 | todo |
| DA-04 | 拡張データでeffective_files再生成 | --geteffで再生成 | todo |
| DA-05 | 拡張データでAD再学習（オプション） | 汎化性能向上 | todo |
| DA-06 | APDEデータセット取得 | 公開後に取得 | blocked |

### 5. 実装例

```python
# scripts/augment_patch_data.py
import torchvision.transforms as T
import random
from PIL import Image

def augment_attacked_image(image_path, output_dir, n_augmentations=10):
    img = Image.open(image_path)

    for i in range(n_augmentations):
        # ランダム変換
        angle = random.uniform(-22.5, 22.5)
        tx = random.randint(-20, 20)
        ty = random.randint(-20, 20)
        scale = random.uniform(0.9, 1.1)

        # 変換適用
        transform = T.Compose([
            T.RandomAffine(degrees=angle, translate=(tx/416, ty/416), scale=(scale, scale)),
        ])

        augmented = transform(img)
        augmented.save(f"{output_dir}/{image_path.stem}_aug{i}.png")
```

### 6. 成功条件（Acceptance Criteria）

```text
- [AC-1] ImageNet-Patchをダウンロードし、評価に使用可能な状態にする
- [AC-2] パッチ変換スクリプトを作成し、手元データを10倍以上に拡張
- [AC-3] 拡張データに対してeffective_filesを再生成
- [AC-4] 拡張データでの評価結果を記録
```

### 7. 参考文献

- [ImageNet-Patch](https://github.com/pralab/ImageNet-Patch)
- [APDE Dataset (ICCV 2025)](https://github.com/Gandolfczjh/APDE)
- [PAD: Patch-Agnostic Defense (CVPR 2024)](https://openaccess.thecvf.com/content/CVPR2024/papers/Jing_PAD_Patch-Agnostic_Defense_against_Adversarial_Patch_Attacks_CVPR_2024_paper.pdf)
- [DiffPatch (2024)](https://arxiv.org/html/2412.01440v1)

### 8. 履歴

```text
- 2026-02-05: タスク作成（データセット拡張方法の調査結果を反映）
```

---

# TASK ENTRIES: 復元マスク改善実験

---

## TASK-20260208-VIZTEST: 可視化修正のテスト実行

### 1. タスク基本情報

```yaml
task:
  id: TASK-20260208-VIZTEST
  title: "可視化修正（best_viz_img）のテスト実行"
  owner: Lead
  assigned_agents:
    - Experiment-Runner
  status: todo
  priority: high
  created: 2026-02-08
```

### 2. 背景・目的（Why）

```text
[背景]
- 可視化が最終beta（最悪ケース）を表示していた問題を修正
- best_viz_img（最多検出betaの画像）を表示するよう saliuitl.py を変更済み
- 修正が正しく動作するか実行確認が必要

[目的]
- 修正後の可視化が正しく生成されることを確認
- best_viz_img, best_viz_mask, per_beta_stats が期待通りに表示されるか検証
- 既存の評価ロジック（RR, LPR）に影響がないことを確認
```

### 3. 実行コマンド

```bash
docker compose run --rm saliuitl python saliuitl.py \
  --inpaint biharmonic \
  --imgdir data/voc/clean \
  --patch_imgdir data/voc/1p \
  --dataset voc \
  --det_net_path checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step 5 \
  --inpainting_step 5 \
  --effective_files data/voc/1p/effective_1p.npy \
  --n_patches 1 \
  --save_images \
  --save_images_limit 5 \
  --save_images_dir experiments/exp_20260208_vizfix/figures
```

### 4. 検証項目

```text
- [V-1] "Recovered" パネルに "[beta=X.XX]" が表示される
- [V-2] "Best Beta Mask" パネルが表示される（累積マスクではなく単体beta）
- [V-3] "Accum. Mask" パネルにper-beta統計テキストが描画される
- [V-4] RR/LPRが exp_20260201_reproduction と同値（回帰テスト）
- [V-5] best_viz_img=Noneのフォールバック（全betaで検出0のケース）
```

### 5. 成功条件

```text
- [AC-1] 5枚の可視化画像がエラーなく生成される
- [AC-2] V-1〜V-3が目視確認できる
- [AC-3] VOC 1p のRR = 0.5385 と一致
```

---

## TASK-20260208-BETASTATS: per-beta統計の定量分析

### 1. タスク基本情報

```yaml
task:
  id: TASK-20260208-BETASTATS
  title: "per-beta統計の定量分析"
  owner: Lead
  assigned_agents:
    - Experiment-Runner
    - Result-Analyst
  status: todo
  priority: high
  created: 2026-02-08
```

### 2. 背景・目的（Why）

```text
[背景]
- recovery_mask_analysis.md で「高betaが評価の主な貢献者」と仮説を立てた
- per_beta_stats トラッキングを実装済みだが、データ収集は未実施
- どのbeta帯が検出回復に最も寄与するか定量的に不明

[目的]
- 全画像で per_beta_stats を収集
- 各betaのマスク面積・検出ボックス数の分布を明らかにする
- 低betaの寄与が実際にあるか検証（ない場合、beta範囲制限の根拠になる）
```

### 3. 必要な実装

per_beta_stats をログ出力またはCSV保存する機能を追加:

```python
# saliuitl.py のper-betaループ後に追加
if per_beta_stats:
    print(f"[BETA_STATS] {nameee}: " +
          ", ".join([f"b={b:.2f}:{a:.1f}%/{n}box" for b,a,n in per_beta_stats]))
```

### 4. 分析計画

| 分析 | 目的 |
|------|------|
| beta別マスク面積ヒストグラム | 各betaでのマスク面積分布 |
| beta別検出ボックス数 | どのbeta帯が検出に最も寄与するか |
| beta別検出精度（IoU≥0.5率） | 高betaの検出品質 vs 低betaの検出品質 |
| beta-cutoff感度分析 | beta_min を 0.05→0.30 に変えた場合のRR変化 |

### 5. 成功条件

```text
- [AC-1] VOC 1p, INRIA 1p の全画像で per_beta_stats を収集
- [AC-2] beta帯ごとの検出寄与度を定量化
- [AC-3] 低beta（<0.30）の削除がRRに影響するか結論を出す
```

---

## TASK-20260208-BETARANGE: beta範囲制限の効果検証

### 1. タスク基本情報

```yaml
task:
  id: TASK-20260208-BETARANGE
  title: "beta範囲制限によるover-masking抑制"
  owner: Lead
  assigned_agents:
    - Experiment-Runner
  status: todo
  priority: high
  created: 2026-02-08
  depends_on: TASK-20260208-BETASTATS
```

### 2. 背景・目的

```text
[背景]
- recovery_mask_analysis.md Section 2.3: 低beta（<0.30）ではFM全域の70%+が活性化
- DBSCANが巨大クラスタを形成し、画像のほぼ全面がインペインティング対象になる
- biharmonicは5%超のマスクで急激に劣化（Section 3.3）

[目的]
- revranの下限を制限（0.05→0.30等）してover-maskingを抑制
- RRへの影響を計測（低betaが不要なら削除でRR維持＋品質改善）
```

### 3. 実験設計

| 条件 | revran範囲 | beta数 |
|------|-----------|--------|
| baseline | [0.95..0.05] step=5 | 19 |
| conservative | [0.95..0.30] step=5 | 14 |
| moderate | [0.95..0.50] step=5 | 10 |
| aggressive | [0.95..0.70] step=5 | 6 |

### 4. 実装方法

`saliuitl.py` の `revran` 生成を `--beta_min` オプションで制御:

```python
# 案: 引数追加
parser.add_argument('--beta_min', type=float, default=0.0)
# revran生成時にフィルタ
revran = [b for b in revran if b >= args.beta_min]
```

### 5. 成功条件

```text
- [AC-1] 4条件でVOC 1p, INRIA 1pを評価
- [AC-2] 各条件のRR, 平均マスク面積, 計算時間を記録
- [AC-3] RRを維持しつつover-maskingを減らせる最適beta_minを特定
```

---

## TASK-20260208-NEULIM: neulim閾値チューニング

### 1. タスク基本情報

```yaml
task:
  id: TASK-20260208-NEULIM
  title: "neulim停止条件閾値の最適化"
  owner: Lead
  assigned_agents:
    - Experiment-Runner
  status: todo
  priority: high
  created: 2026-02-08
```

### 2. 背景・目的

```text
[背景]
- recovery_mask_analysis.md Section 2.4:
  neulim=0.5 → FMセル22%まで通過 → 画像面積の約21%がマスク対象
- `continue`（breakではない）のためスキップ後も次betaが処理される
- より低い閾値でマスク面積を制限すればover-masking抑制可能

[目的]
- neulim = 0.1, 0.2, 0.3, 0.5（デフォルト）での比較
- RRとマスク面積のトレードオフを定量化
```

### 3. 実験設計

| 条件 | neulim | 通過FMセル上限 | 推定マスク面積上限 |
|------|--------|-------------|-----------------|
| tight | 0.1 | ~4.4% | ~4% |
| moderate | 0.2 | ~8.9% | ~9% |
| default_low | 0.3 | ~13.3% | ~13% |
| default | 0.5 | ~22.2% | ~21% |

### 4. 実行コマンド

```bash
for neulim in 0.1 0.2 0.3 0.5; do
  docker compose run --rm saliuitl python saliuitl.py \
    --dataset voc --imgdir data/voc/clean --patch_imgdir data/voc/1p \
    --det_net_path checkpoints/final_detection/2dcnn_raw_VOC_5_atk_det.pth \
    --det_net 2dcnn_raw --ensemble_step 5 --inpainting_step 5 \
    --effective_files data/voc/1p/effective_1p.npy --n_patches 1 \
    --neulim $neulim \
    --save_images --save_images_limit 5 \
    --save_images_dir experiments/exp_20260208_neulim/neulim_${neulim}/figures
done
```

### 5. 成功条件

```text
- [AC-1] 4条件でVOC 1p, INRIA 1pを評価
- [AC-2] 各条件のRR, 平均マスク面積を記録
- [AC-3] 可視化でマスク面積の変化を確認
- [AC-4] 最適neulim値の推奨を出す
```
