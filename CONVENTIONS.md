# CONVENTIONS.md
*Research Conventions for Claude Code + Sub-agents*

## 0. 目的（Why this exists）
本プロジェクトでは、Claude Code の **複数サブエージェント** を用いて  
論文調査・再現実験・解析・執筆を並行して行う。

その際に起きがちな以下を防ぐことを目的とする。

- 実験条件・指標定義のズレ
- サブエージェントごとの暗黙の前提の不一致
- 後から再現できないログ・図表・結果
- 論文記述と実験コードの乖離

本ファイルは **すべてのエージェントが必ず従う共通規約** である。

---

## 1. 共通原則（Global Principles）

### 1.1 再現性最優先
- 実験結果は **必ず再実行可能** でなければならない
- 「その場限りの試行」「手動実行のみ」は禁止

### 1.2 暗黙の変更禁止
- パラメータ・データ・評価条件を **黙って変更しない**
- 変更は必ず **明示的に記録** する

### 1.3 ロール分離
- 各サブエージェントは **自分の責務以外に踏み込まない**
- 判断が必要な場合は **Lead（主エージェント）にエスカレーション**

---

## 2. ディレクトリ構成規約

```text
project-root/
├─ data/
│  ├─ raw/              # 生データ（不変）
│  ├─ processed/        # 前処理済み
│  └─ splits/           # train/val/test 分割
│
├─ experiments/
│  ├─ exp_YYYYMMDD_xxx/
│  │  ├─ config.yaml    # 実験条件（最重要）
│  │  ├─ run.sh         # 実行コマンド
│  │  ├─ logs/          # stdout / stderr
│  │  └─ results/       # npy / csv / json
│
├─ analysis/
│  ├─ scripts/
│  ├─ tables/
│  └─ figures/
│
├─ paper/
│  ├─ figures/
│  ├─ tables/
│  └─ draft.md
│
├─ .claude/
│  └─ agents/
│
├─ CONVENTIONS.md
└─ TASKS.md
```

---

## 3. 実験命名規則（Experiment Naming）

### 3.1 実験ID
```
exp_<YYYYMMDD>_<short-description>
```

### 3.2 実験は「1条件1ディレクトリ」
- 異なる条件を **同じ実験IDに混在させない**
- 条件比較は analysis 側で行う

---

## 4. 実験条件の記録（config.yaml）

```yaml
experiment:
  id: exp_YYYYMMDD_example
  purpose: "Describe experiment purpose"

environment:
  framework: pytorch
  cuda: "12.1"
  seed: 42
  git_commit: "<commit-hash>"
```

---

## 5. ログ規約（Logging）

### 5.1 必須ログ項目
- 実行開始・終了時刻
- 実行コマンド全文
- seed
- 実験ID
- 各評価指標の **分子・分母**

---

## 6. 評価指標の定義（Metrics）

- 指標は必ず **式で定義**
- 分母が異なる場合は別指標として扱う

---

## 7. サブエージェント共通ルール

- 推測禁止
- 出力フォーマット厳守
- 変更は差分で提示

---

## 8. 最終原則（Golden Rule）

> **未来の自分が1日で再現できるか？**
