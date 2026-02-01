# Saliuitl（研究用フォーク）

このリポジトリは、**Saliuitl: Ensemble Salience Guided Recovery of Adversarial Patches** の
オリジナル実装を**研究目的でフォーク**したものです。

> オリジナルリポジトリ（フォーク元）:
> **https://github.com/Saliuitl/Saliuitl**

本フォークは、オリジナルの実装動作を維持しつつ、
**再現可能な研究**、**Claude Code サブエージェントワークフロー**、
**Git Worktree による並列開発**をサポートするために再構成されています。

---

## オリジナルリポジトリとの違い

本フォークは**研究インフラ**を導入するものであり、アルゴリズムの変更は行っていません（明示的に記載がある場合を除く）。

- **再現可能な実験構造**
  - `experiments/exp_YYYYMMDD_*` を単一の真実源（SSOT）として使用
  - 実験ごとに明示的な `config.yaml` と `run.sh` を配置
- **Claude Code サブエージェントワークフロー**
  - 明確な役割分担: Lead / Runner / Analyst / Reviewer / Critic / Investigator
- **Git Worktree による並列研究**
  - 実装・実験・分析用に別々のワークツリーを使用
- **正式な研究規約**
  - `CONVENTIONS.md`, `TASKS.md`, `WORKTREE.md`

コアとなる Saliuitl のロジックとデフォルトパスは、
再現性を損なわないようオリジナルリポジトリと互換性を維持しています。

---

## リポジトリ構造（研究指向）

```text
.
├─ saliuitl.py                # オリジナルのエントリポイント（変更なし）
├─ cfg/ weights/ checkpoints/ # オリジナルのレイアウト（互換性のため維持）
├─ data/                      # データセット配置（変更なし）
│
├─ experiments/               # 全実験実行（SSOT）
│  └─ exp_YYYYMMDD_slug/
│     ├─ config.yaml
│     ├─ run.sh
│     ├─ logs/
│     └─ results/
│
├─ analysis/                  # 集計と可視化
│  ├─ scripts/
│  ├─ tables/
│  └─ figures/
│
├─ docs/
│  ├─ notes/                  # Investigator の出力
│  └─ decisions/
│
├─ .claude/agents/            # Claude Code サブエージェント
│
├─ CONVENTIONS.md
├─ TASKS.md
├─ WORKTREE.md
└─ README.md
```

---

## 研究ワークフロー（推奨）

1. **Investigator**
   - コードベース / データセットの前提を理解
   - 調査結果を `docs/notes/` に記録
2. **Lead**
   - `TASKS.md` でタスクを定義
3. **Builder**
   - 変更を実装（開発用ワークツリー）
4. **Reviewer**
   - 実装をレビュー（読み取り専用）
5. **Runner**
   - 実験を実行（`experiments/`）
6. **Analyst**
   - 結果を集計（`analysis/`）
7. **Research Critic**
   - 実験の妥当性を評価
8. **Lead**
   - Go / No-Go 判断と次のステップ

詳細は `WORKTREE.md` を参照してください。

---

## 実験の実行

すべての実験は実験ディレクトリを通して実行する必要があります。

```bash
# 実験ディレクトリを作成
mkdir -p experiments/exp_YYYYMMDD_example/{logs,results}

# config.yaml と run.sh を編集
cd experiments/exp_YYYYMMDD_example
./run.sh
```

研究実験では `saliuitl.py` を直接実行**しないでください**。
これにより再現性とトレーサビリティが確保されます。

---

## 再現性に関する注意

- データセットとチェックポイントは Git から除外されている場合があります
- すべての実験条件は `config.yaml` に記録する必要があります
- ログと結果は派生成果物として扱われます

厳密なルールは `CONVENTIONS.md` を参照してください。

---

## ライセンスと帰属

本リポジトリは**オリジナルプロジェクトと同じライセンス**に従います。

学術研究でこのコードを使用する場合は、**オリジナルの論文とリポジトリを引用**してください。
本フォークはオリジナルの Saliuitl 手法の著作権を主張するものではありません。

---

## 免責事項

本フォークは**研究および実験目的**で使用されることを意図しています。
インフラ変更以外の修正は、アルゴリズム的貢献として認められる前に、
明確に文書化され、検証される必要があります。
