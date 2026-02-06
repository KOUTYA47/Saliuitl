# Session Log: 2026-02-05

**セッション開始**: 2026-02-05
**主担当**: Lead Agent
**セッション終了**: 2026-02-05

---

## エグゼクティブサマリー

本日のセッションでは、Saliuitl論文再現実験の深掘り分析を行い、**4つの重要な課題**を発見した：

1. **Oracle Test結果**: マスク精度改善は物体検出でのみ有効（+22.8%）、画像分類では限定的（+0.8%）
2. **effective_filesの不整合**: フルデータセット用のファイルをサブセットに適用 → 評価対象が減少
3. **ADの汎化性能**: データセット固有・攻撃パターン固有の学習 → 未知攻撃への汎化が困難
4. **データセット規模**: 手元30枚では統計的信頼性が低い → 拡張が必要

---

## 本日の完了タスク

### 1. Oracle Inpainting Test 詳細考察
- **ステータス**: 完了
- **出力**: `docs/notes/oracle_test_analysis.md`（310行）
- **主要発見**:
  - 物体検出: Oracle効果 +22.8%（マスク精度改善の余地大）
  - 画像分類: Oracle効果 +0.8%（Biharmonicで十分）
  - ボトルネック階層: 検出率 > マスク精度 > インペインティング品質

### 2. effective_files調査
- **ステータス**: 完了
- **発見**:
  | Dataset | effective_files | 手元データ | 処理数 |
  |---------|----------------|-----------|--------|
  | INRIA 1p | 234 | 30 | 24 |
  | CIFAR 1p | 14 | 30 | 14 |
  | VOC mo | 27 | 29 | 27 |
- **問題**: フルデータセット用のeffective_filesを30枚のサブセットに適用
- **対策**: 手元データ用に再生成が必要（TASK-20260205-EFFGEN）

### 3. Attack Detector（AD）汎化性能調査
- **ステータス**: 完了
- **発見**:
  - ADはデータセット固有で学習（被害者モデル、特徴マップサイズ、画像特性が異なる）
  - 未知のデータセット・攻撃パターンへの汎化は未検証
  - INRIA trigの低検出率（54.5%）がその証拠
- **関連研究**:
  - NutNet: クリーン画像のみで学習（OOD検出）→ 攻撃パターン非依存
  - DIFFender: Diffusionモデルで再生成 → 学習不要
  - PATCHOUT: セマンティック一貫性で検出 → 学習不要

### 4. データセット拡張方法の調査
- **ステータス**: 完了
- **発見**:
  - APDE (ICCV 2025): 94,000枚の大規模データセット（公開待ち）
  - ImageNet-Patch: 50,000枚（公開済み）
  - パッチ変換による拡張: 回転・移動・スケールで10倍以上に拡張可能

### 5. ドキュメント更新
- **TASKS.md**: 4つの新タスク追加（EFFGEN, ADGEN, RELATED, DATAUG）
- **RESULT_LOG.md**: Oracle考察サマリー追加
- **ASSUMPTIONS.md**: ボトルネック階層、AD汎化性能の懸念を追加
- **DECISIONS.md**: D-2026-02-05-B/C/D追加

---

## 主要な発見

### Oracle Test結果

| タスク | Biharmonic RR | Oracle RR | 改善幅 |
|--------|--------------|-----------|--------|
| 物体検出 | 49.8% | 72.6% | **+22.8%** |
| 画像分類 | 74.1% | 75.0% | +0.8% |

**結論**: マスク精度改善は物体検出でのみ効果的

### ボトルネック階層構造

```
Recovery Rate（復元率）
      ↑ 制約
Level 3: インペインティング品質（改善余地: 5-15%）
      ↑ 制約
Level 2: マスク精度（物体検出: +22.8% / 画像分類: +0.8%）
      ↑ 制約
Level 1: 検出率 ← 最重要（trig攻撃で45%の改善余地）
```

### Saliuitlの限界

| 限界 | 説明 | 影響 |
|------|------|------|
| データセット固有のAD | 新ドメインには再学習が必要 | 汎用性が低い |
| 攻撃パターン固有の学習 | 未知の攻撃形状で性能低下 | trig: 54.5%検出 |
| effective_filesの依存 | フルデータセットが必要 | 評価の正確性 |
| 小規模データセット | 30枚では統計的信頼性が低い | 結果のばらつき |

---

## 新規作成タスク

| タスクID | タイトル | 優先度 | 内容 |
|---------|---------|--------|------|
| TASK-20260205-EFFGEN | effective_files再生成 | **高** | 手元30枚に対して--geteffで再生成 |
| TASK-20260205-ADGEN | AD汎化性能検証 | 中 | クロスデータセット・クロス攻撃評価 |
| TASK-20260205-RELATED | 関連研究調査 | 低 | NutNet, DIFFender等との比較 |
| TASK-20260205-DATAUG | データセット拡張 | 低 | ImageNet-Patch活用、パッチ変換 |

---

## 新規判断事項

| 判断ID | タイトル | 内容 |
|--------|---------|------|
| D-2026-02-05-B | 改善優先順位 | 検出率 > マスク精度 > インペインティング |
| D-2026-02-05-C | effective_files再生成 | 手元サブセット用に再生成が必要 |
| D-2026-02-05-D | AD汎化性能検証 | クロス評価で限界を明確化 |

---

## 更新ファイル一覧

| ファイル | 更新内容 |
|---------|---------|
| `TASKS.md` | 4タスク追加、次のアクション更新 |
| `RESULT_LOG.md` | Oracle考察サマリー・ボトルネック表追加 |
| `ASSUMPTIONS.md` | ボトルネック階層、AD汎化性能、関連研究を追加 |
| `DECISIONS.md` | D-2026-02-05-B/C/D追加 |
| `docs/notes/oracle_test_analysis.md` | 新規作成（310行） |
| `docs/notes/session_latest.md` | 本ファイル |

---

## 次のアクション

### 優先度: 高
- [ ] **effective_filesの再生成**（TASK-20260205-EFFGEN）
- [ ] スライドPPTX最終確認（ユーザー側作業）
- [ ] スライドへのOracle考察反映

### 優先度: 中
- [ ] Table 2 (nmAP) 再現実験の実行
- [ ] 検出率向上の検討（INRIA trig: Detected=54.5%）
- [ ] **AD汎化性能の検証**（TASK-20260205-ADGEN）

### 優先度: 低
- [ ] 異なるインペインティング手法との比較実験
- [ ] 高解像度特徴マップでの実験
- [ ] **関連研究の詳細調査**（TASK-20260205-RELATED）
- [ ] **データセット拡張**（TASK-20260205-DATAUG）

---

## 参考リンク

### Saliuitl関連
- [Saliuitl Paper (CVPR 2025)](https://openaccess.thecvf.com/content/CVPR2025/papers/Victorica_Saliuitl_Ensemble_Salience_Guided_Recovery_of_Adversarial_Patches_against_CNNs_CVPR_2025_paper.pdf)

### 汎化性能改善手法
- [NutNet (2024)](https://arxiv.org/html/2406.10285v1) - クリーン画像のみで学習
- [DIFFender (2025)](https://pubmed.ncbi.nlm.nih.gov/40768456/) - Diffusionモデルベース
- [PATCHOUT (2025)](https://link.springer.com/article/10.1007/s11063-025-11775-5) - セマンティック一貫性
- [PAD (CVPR 2024)](https://openaccess.thecvf.com/content/CVPR2024/papers/Jing_PAD_Patch-Agnostic_Defense_against_Adversarial_Patch_Attacks_CVPR_2024_paper.pdf) - Patch-Agnostic Defense

### データセット
- [ImageNet-Patch](https://github.com/pralab/ImageNet-Patch) - 50,000枚
- [APDE Dataset (ICCV 2025)](https://github.com/Gandolfczjh/APDE) - 94,000枚（公開待ち）
- [Adversarial Patch Paper List](https://github.com/inspire-group/adv-patch-paper-list)

---

**セッション終了**: 2026-02-05
