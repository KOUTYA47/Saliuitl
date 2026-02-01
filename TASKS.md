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
```
