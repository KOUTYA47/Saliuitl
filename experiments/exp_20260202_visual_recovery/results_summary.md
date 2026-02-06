# 視覚的回復品質改善実験 - 結果サマリー

実験ID: `exp_20260202_visual_recovery`
実施日: 2026-02-02

---

## 核心的発見

### 1. マスク精度が主要なボトルネック

**Oracle Inpainting Test結果**:
| Dataset | 平均エラー | 結論 |
|---------|-----------|------|
| VOC | 0.63 | 正確なマスクがあれば視覚的にパッチ除去可能 |
| INRIA | 0.23 | 同上 |

**発見**: Ground-truthマスクを使用すれば、biharmonicインペインティングで**パッチを視覚的に除去できる**。現在のシステムの問題は**マスク生成の精度**にある。

### 2. Biharmonicインペインティングの限界

Oracleテストでも復元領域は**ぼやけた仕上がり**になる。これはbiharmonic手法の本質的な特性：
- 曲率最小化アルゴリズムのため滑らかな結果
- テクスチャやエッジの再構成は不可能
- 大きな領域では品質低下

### 3. 敵対的パッチはモデルのAttentionをハイジャックする

**Grad-CAM分析結果**:
| 画像 | Clean Score | Attacked Score | Attention変化 |
|------|-------------|----------------|---------------|
| 000001 | 0.884 | 0.670 | 人物→パッチに移動 |
| 000002 | 0.777 | 0.700 | 電車→パッチに移動 |
| 000004 | 0.833 | 0.834 | 変化小（攻撃失敗ケース） |

**発見**: 敵対的パッチは検出器のAttentionを**対象物体からパッチ自体**に誘導する。これが検出失敗のメカニズム。

---

## 実験詳細

### Experiment 1: Oracle Inpainting Test

**目的**: マスク精度 vs インペインティング手法の問題切り分け

**手法**:
1. Clean画像とAttacked画像の差分でパッチ位置を特定
2. 差分マスクを膨張して完全なカバレッジを確保
3. biharmonicインペインティングを適用

**結果**:
```
VOC (5 images):
  Mask coverage: 0.2% - 5.3%
  Average residual error: 0.63

INRIA (5 images):
  Mask coverage: 0.1% - 1.3%
  Average residual error: 0.23
```

**可視化**: `oracle_test/voc/`, `oracle_test/inria/`

### Experiment 2: Grad-CAM Attention可視化

**目的**: パッチが検出を妨害するメカニズムの理解

**手法**:
1. YOLOv2のLayer 13（26×26）でGrad-CAM生成
2. Clean/Attacked画像のAttentionマップを比較

**結果**:
- Clean画像: Attentionは検出対象（人物、電車など）に集中
- Attacked画像: Attentionがパッチ領域に強く引き寄せられる
- Detection scoreが0.884→0.670に低下（000001の例）

**可視化**: `gradcam/voc/`

---

## 仮説検証状況

| 仮説 | 状態 | 結果 |
|------|------|------|
| H1: 高解像度特徴マップ | 📋 未実施 | - |
| H2: 膨張パラメータ最適化 | 📋 未実施 | - |
| H3: 閾値選択改善 | 📋 未実施 | - |
| H4: Oracle インペインティング | ✅ 完了 | **有効** - マスクが正確なら除去可能 |
| H5: Attention可視化 | ✅ 完了 | **パッチがAttentionをハイジャック** |

---

## 推奨される次のステップ

### 優先度1: マスク精度の改善

現在のシステムのマスクが不正確なため：
1. **高解像度特徴マップ使用** (Layer 10: 52×52)
2. **膨張パラメータの最適化** (n_dilation=5 or 7)
3. **閾値選択の改善** (平均ではなく最大カバレッジ閾値)

### 優先度2: インペインティング手法の改善

biharmonicの限界を克服するため：
1. **GAN-based インペインティング** (LaMa, DeepFill)
2. **Diffusion-based インペインティング** (Stable Diffusion Inpaint)

### 優先度3: 検出手法の改善

Attention hijackingへの対策：
1. **Adversarial training**
2. **Attention regularization**

---

## 生成ファイル一覧

| ディレクトリ | 内容 |
|-------------|------|
| `oracle_test/voc/` | VOC Oracle inpainting結果 (5画像) |
| `oracle_test/inria/` | INRIA Oracle inpainting結果 (5画像) |
| `gradcam/voc/` | VOC Grad-CAM可視化 (3画像) |
| `hypotheses.md` | 仮説リストと検証計画 |

---

## 結論

1. **現在のシステムの主要なボトルネックはマスク精度**
2. **Biharmonicインペインティングは正確なマスクがあれば機能する**が、ぼやけた結果になる
3. **敵対的パッチはモデルのAttentionを対象物体からパッチに誘導**することで攻撃が成功
4. **視覚的品質改善のためにはマスク精度向上とより高度なインペインティング手法が必要**
