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

## 1. タスク基本情報（必須）

```yaml
task:
  id: TASK-YYYYMMDD-XX
  title: "Short descriptive title"
  owner: Lead
  assigned_agents:
    - Experiment-Runner
    - Result-Analyst
  status: todo | running | blocked | done
  priority: high | medium | low
```

---

## 2. 背景・目的（Why）

```text
[背景]
- なぜこのタスクが必要か
- どの論文 / 実験 / 仮説に基づくか

[目的]
- このタスクで「何が分かれば成功か」
```

---

## 3. 入力（Inputs）

```text
- 使用するデータセット：
- 参照論文・資料：
- 使用するコード・スクリプト：
- 前提条件（seed, model, dataset split 等）：
```

---

## 4. 実施内容（What to do）

```text
1. 実施する手順を箇条書きで明示
2. 条件・パラメータは明示的に書く
3. 「試してみる」「良さそうなら」は禁止
```

---

## 5. 出力（Deliverables）

```text
- 生成されるファイル：
  - path/to/file.ext
- 表・図・ログの形式：
- Lead が確認すべき要点：
```

---

## 6. 成功条件（Acceptance Criteria）

```text
- 数値・条件で YES/NO 判定できる形で記述
- 「妥当そう」「問題なさそう」は不可
```

---

## 7. 制約・禁止事項（Constraints）

```text
- 変更禁止項目（dataset, metric 定義など）
- 使用禁止手法・近道
```

---

## 8. 検証・確認方法（Verification）

```text
- 再実行方法：
- 再現確認のチェックポイント：
```

---

## 9. リスク・失敗時対応（Risk & Rollback）

```text
- 想定される失敗：
- 切り分け方法：
- ロールバック手順：
```

---

## 10. 関連タスク・次の一手（Next Steps）

```text
- 依存しているタスク：
- このタスク完了後にやるべきこと：
```

---

## 11. 履歴（History）

```text
- YYYY-MM-DD: 作成
- YYYY-MM-DD: 更新内容
```

---

## 12. タスク作成時のチェックリスト（必須）

- [ ] 目的が1文で説明できる
- [ ] 成功条件が数値または明確な条件で定義されている
- [ ] 分母・評価条件が明示されている
- [ ] 出力ファイルの保存場所が決まっている
- [ ] 再実行方法が記載されている

---

## Golden Rule

> **「この TASKS.md を読んだ別の人（または1週間後の自分）が、
> 追加質問なしで同じ作業を再現できるか？」**

---
---

# TASK ENTRIES

---

## TASK-20260201-01: Reproduce Saliuitl on INRIA with 2-patch attack

### 1. タスク基本情報

```yaml
task:
  id: TASK-20260201-01
  title: "Reproduce Saliuitl on INRIA 2-patch attack"
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
- Saliuitl論文の再現実験として、INRIA dataset上での2-patch攻撃に対する検出・復元性能を検証する
- 既存の1-patch実験（data/inria/1p）は完了済み。2-patch（data/inria/2p）の再現が未完了
- 2-patch攻撃はパッチ数が増えることで検出難易度が変化する可能性がある

[目的]
- 2-patch攻撃画像に対してSaliuitlパイプライン（検出→復元）が正常に動作することを確認する
- 論文記載の評価指標（Detection Rate, Recovery Rate）を算出し、再現性を検証する
```

### 3. 入力（Inputs）

```text
- 使用するデータセット：
  - data/inria/clean/         : クリーン画像（正解）
  - data/inria/2p/            : 2-patch攻撃画像（評価対象）

- 参照論文・資料：
  - Victorica_Saliuitl_Ensemble_Salience_Guided_Recovery_of_Adversarial_Patches_against_CNNs_CVPR_2025_paper.pdf

- 使用するコード・スクリプト：
  - saliuitl.py               : メイン評価スクリプト
  - train_attack_detector.py  : AD学習スクリプト
  - helper.py                 : 特徴抽出・クラスタリング

- 前提条件：
  - seed: 未指定（デフォルト）
  - model: YOLOv2 (cfg/yolo.cfg, weights/yolo.weights)
  - ensemble_step: 5
  - inpainting_step: 5
  - dbscan_eps: 1.0
  - dbscan_min_pts: 4
  - inpaint: biharmonic
```

### 4. 実施内容（What to do）

**サブタスク一覧:**

| Sub-ID | タイトル | 担当 | 依存 |
|--------|---------|------|------|
| 01-A | 2-patch特徴マップ抽出 | Experiment-Runner | - |
| 01-B | Attack Detector学習（2-patch） | Experiment-Runner | 01-A |
| 01-C | effective_2p.npy生成 | Experiment-Runner | - |
| 01-D | 検出・復元評価実行 | Experiment-Runner | 01-B, 01-C |
| 01-E | 結果解析・レポート作成 | Result-Analyst | 01-D |

---

#### Sub-Task 01-A: 2-patch特徴マップ抽出

```text
目的: Attack Detector学習用の特徴マップを生成する

手順:
1. data/inria/clean/ から特徴マップを抽出 → 2p_train_fms.npy
2. data/inria/2p/ から特徴マップを抽出 → 2p_train_pfms.npy
3. 対応するタグファイル生成 → 2p_train_tags.npy

出力ファイル:
  - net_train_data/inria/2p_train_fms.npy
  - net_train_data/inria/2p_train_pfms.npy
  - net_train_data/inria/2p_train_tags.npy

成功条件:
  - 3ファイルが生成される
  - 2p_train_fms.npy と 2p_train_pfms.npy の shape[0] が一致する
```

---

#### Sub-Task 01-B: Attack Detector学習（2-patch）

```text
目的: 2-patch攻撃検出用のADモデルを学習する

コマンド:
python train_attack_detector.py \
  --feature_maps net_train_data/inria/2p_train_fms.npy \
  --adv_feature_maps net_train_data/inria/2p_train_pfms.npy \
  --dataset inria \
  --ensemble_step 5

出力ファイル:
  - checkpoints/final_detection/2dcnn_raw_inria_5_2p_atk_det.pth

成功条件:
  - モデルファイルが生成される
  - 学習ログにloss収束が確認できる
```

---

#### Sub-Task 01-C: effective_2p.npy生成

```text
目的: 2-patch攻撃が「有効」な画像リストを特定する

定義: 攻撃が有効 = クリーン画像では検出成功、攻撃画像では検出失敗

手順:
1. data/inria/clean/ の全画像に対してYOLOv2で検出実行
2. data/inria/2p/ の全画像に対してYOLOv2で検出実行
3. clean で検出成功 かつ 2p で検出失敗 の画像をリスト化

出力ファイル:
  - effective_2p.npy (画像ファイル名のリスト)

成功条件:
  - effective_2p.npy が生成される
  - リストが空でない（有効攻撃画像が存在する）
```

---

#### Sub-Task 01-D: 検出・復元評価実行

```text
目的: Saliuitlパイプラインで2-patch攻撃の検出・復元を評価する

コマンド:
python saliuitl.py \
  --inpaint biharmonic \
  --imgdir data/inria/clean \
  --patch_imgdir data/inria/2p \
  --dataset inria \
  --det_net_path checkpoints/final_detection/2dcnn_raw_inria_5_2p_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step 5 \
  --inpainting_step 5 \
  --effective_files effective_2p.npy \
  --n_patches 2

出力ファイル:
  - experiments/exp_20260201_inria_2p/config.yaml
  - experiments/exp_20260201_inria_2p/logs/stdout.log
  - experiments/exp_20260201_inria_2p/results/metrics.json

成功条件:
  - スクリプトがエラーなく完了する
  - Detection Rate, Recovery Rate が出力される
```

---

#### Sub-Task 01-E: 結果解析・レポート作成

```text
目的: 評価結果を論文形式で整理し、1-patchとの比較を行う

手順:
1. metrics.json から主要指標を抽出
2. 1-patch結果との比較表を作成
3. 論文Table形式で整形

出力ファイル:
  - analysis/tables/inria_2p_results.csv
  - analysis/figures/inria_1p_vs_2p.png (optional)

成功条件:
  - Detection Rate, Recovery Rate が数値で報告される
  - 1-patch結果との差異が明示される
```

### 5. 出力（Deliverables）

```text
- 生成されるファイル：
  - net_train_data/inria/2p_train_fms.npy
  - net_train_data/inria/2p_train_pfms.npy
  - checkpoints/final_detection/2dcnn_raw_inria_5_2p_atk_det.pth
  - effective_2p.npy
  - experiments/exp_20260201_inria_2p/
  - analysis/tables/inria_2p_results.csv

- 表・図・ログの形式：
  - metrics.json: {"detection_rate": float, "recovery_rate": float, ...}
  - CSV: dataset, n_patches, detection_rate, recovery_rate

- Lead が確認すべき要点：
  - 2-patchでのDetection Rateが1-patchと比較して妥当か
  - Recovery Rateの低下幅が許容範囲か
```

### 6. 成功条件（Acceptance Criteria）

```text
- [AC-1] 全サブタスク(01-A〜01-E)がエラーなく完了する
- [AC-2] Detection Rate ≥ 0.0（数値として算出される）
- [AC-3] Recovery Rate ≥ 0.0（数値として算出される）
- [AC-4] effective_2p.npy に最低1枚以上の有効攻撃画像が含まれる
- [AC-5] 実験ディレクトリにconfig.yaml, logs/, results/が存在する
```

### 7. 制約・禁止事項（Constraints）

```text
- 変更禁止項目:
  - YOLOv2モデル構成（cfg/yolo.cfg）
  - データセット分割（既存のclean/2pディレクトリ構成）
  - 評価指標の定義（Detection Rate = 検出成功数 / 有効攻撃画像数）

- 使用禁止:
  - 手動でのパラメータチューニング（ensemble_step=5固定）
  - 他データセットからの転移学習
  - 既存の1-patch用モデルでの評価（必ず2-patch用を学習する）
```

### 8. 検証・確認方法（Verification）

```text
- 再実行方法:
  1. experiments/exp_20260201_inria_2p/config.yaml を確認
  2. 同ディレクトリの run.sh を実行
  3. results/metrics.json が同一値を出力することを確認

- 再現確認のチェックポイント:
  - [ ] 特徴マップのshapeが一致するか
  - [ ] ADモデルの学習曲線が収束しているか
  - [ ] effective_2p.npy の画像数が変わらないか
  - [ ] 最終metricsが±1%以内で再現されるか
```

### 9. リスク・失敗時対応（Risk & Rollback）

```text
- 想定される失敗:
  1. 2-patch画像が少なすぎてAD学習が不安定
  2. effective_2p.npy が空（有効攻撃画像がない）
  3. メモリ不足で特徴抽出が失敗

- 切り分け方法:
  1. → 学習ログでloss/accuracyの推移を確認
  2. → cleanでの検出率を確認（検出器自体の問題か切り分け）
  3. → バッチサイズ縮小、GPU利用可否を確認

- ロールバック手順:
  - experiments/exp_20260201_inria_2p/ を削除して再実行
  - checkpoints配下は既存1-patchモデルを保持しているため影響なし
```

### 10. 関連タスク・次の一手（Next Steps）

```text
- 依存しているタスク:
  - なし（独立タスク）

- このタスク完了後にやるべきこと:
  - VOCデータセットでの2-patch再現実験
  - 3-patch以上のスケーラビリティ検証
  - inpaint手法比較（diffusion vs biharmonic）
```

### 11. 履歴（History）

```text
- 2026-02-01: Lead agent により作成
```

### 12. タスク作成時のチェックリスト

- [x] 目的が1文で説明できる
- [x] 成功条件が数値または明確な条件で定義されている
- [x] 分母・評価条件が明示されている
- [x] 出力ファイルの保存場所が決まっている
- [x] 再実行方法が記載されている
