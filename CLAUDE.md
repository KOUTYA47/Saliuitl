# CLAUDE.md

このファイルは、このリポジトリで作業する際のClaude Code (claude.ai/code) へのガイダンスを提供します。

## プロジェクト概要

SaliuitlはPyTorchベースの敵対的パッチ検出・復元システムです。名前はナワトル語で「思想的転換」を意味し、敵対的パッチ検出に使用するアンサンブル間の属性シフトを指しています。

システムは2段階のパイプラインを実装:
1. **検出**: 特徴マップに対するDBSCANベースのクラスタリングで敵対的パッチを識別
2. **復元**: インペインティング技術を適用して改ざんされた画像を復元

## コマンド

### 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 検出・復元の実行
```bash
# INRIAデータセットの例
python saliuitl.py \
  --inpaint biharmonic \
  --imgdir data/inria/clean \
  --patch_imgdir data/inria/1p \
  --dataset inria \
  --det_net_path checkpoints/final_detection/2dcnn_raw_inria_5_atk_det.pth \
  --det_net 2dcnn_raw \
  --ensemble_step 5 \
  --inpainting_step 5 \
  --effective_files effective_1p.npy \
  --n_patches 1
```

### Attack Detectorの学習
```bash
python train_attack_detector.py \
  --feature_maps net_train_data/inria/1p_train_fms.npy \
  --adv_feature_maps net_train_data/inria/1p_train_pfms.npy \
  --dataset inria
```

## アーキテクチャ

### コアパイプライン (saliuitl.py)
- 被害者モデル（YOLOv2またはResNet50）から特徴マップを抽出
- 各顕著性閾値beta（0.0-1.0）について: 特徴を二値化し、DBSCANクラスタリングを適用、4つの属性（クラスタ数、平均クラスタ内距離、標準偏差、重要度スコア）を抽出
- 属性をL∞ノルムで正規化し、Attack Detector（AD）ニューラルネットワークに入力
- 攻撃検出時は、疑わしい領域を特定してインペインティングを適用

### 主要コンポーネント
- **`saliuitl.py`**: 検出・復元評価のメイン実行スクリプト
- **`train_attack_detector.py`**: ADモデルの学習スクリプト
- **`helper.py`**: コアユーティリティ（bbox_iou, nms, do_detect, inpainting, clustering_data_preprocessing）
- **`darknet.py`**: 特徴抽出を修正したYOLOv2実装
- **`nets/attack_detector.py`**: Attack Detectorモデル（AtkDetCNNRawがデフォルト）
- **`nets/resnet.py`**: 特徴マップ抽出用に修正したResNet50

### 被害者モデル
- **YOLOv2**: INRIA/Pascal VOC用の物体検出（設定: `cfg/yolo.cfg`）
- **ResNet50**: CIFAR-10/ImageNet用の画像分類

### 対応データセット
- CIFAR-10, ImageNet（分類）
- INRIA, Pascal VOC（物体検出）

## 主要CLIオプション

| オプション | 説明 | デフォルト |
|--------|-------------|---------|
| `--ensemble_step` | 検出用の閾値セットサイズ（100/step = 閾値数） | 5 |
| `--inpainting_step` | 復元用の閾値セットサイズ | 5 |
| `--inpaint` | インペインティング手法: zero, mean, biharmonic, diffusion, oracle | biharmonic |
| `--dataset` | 対象データセット: inria, voc, imagenet, cifar | - |
| `--dbscan_eps` | DBSCANクラスタリング半径 | 1.0 |
| `--dbscan_min_pts` | 最小クラスタサイズ | 4 |
| `--nn_det_threshold` | 攻撃検出閾値 | 0.5 |
| `--clean` | パッチなし画像のみで評価 | false |

## 外部依存関係

- YOLOv2重み: [adversarial_yolo2](https://github.com/Zhang-Jack/adversarial_yolo2)からダウンロード → `weights/`に配置
- ResNet50 CIFARチェックポイント: [PatchGuard](https://github.com/inspire-group/PatchGuard)からダウンロード → `checkpoints/`に配置
