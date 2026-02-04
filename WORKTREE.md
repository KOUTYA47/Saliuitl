# WORKTREE.md
*Parallel Research & Development Workflow with Claude Code Sub-agents*

## 目的
本ドキュメントは、**Claude Code のサブエージェント**と  
**Git Worktree** を組み合わせて、研究・実装・レビュー・解析を  
**安全かつ並列**に進めるための運用ルールを定義する。

本プロジェクトでは以下を重視する：
- 再現性（Reproducibility）
- 責務分離（Separation of Concerns）
- 思い込みの排除（Independent Contexts）
- 査読・引き継ぎ耐性

---

## 全体像（推奨アーキテクチャ）

```text
(main repo)
   |
   |-- repo-exp   : 実験実行（安定版）
   |-- repo-dev   : 実装・改変
   |-- repo-ana   : 解析・図表生成
```

それぞれの作業ディレクトリで **異なるサブエージェント**を使う。

---

## サブエージェントと担当

| Agent | 主な役割 | 作業場所 |
|---|---|---|
| lead | タスク分解・判断 | どこでも |
| investigator | 調査・棚卸し | dev / exp |
| builder | 実装 | repo-dev |
| reviewer | レビュー | repo-dev |
| runner | 実験実行 | repo-exp |
| analyst | 結果解析 | repo-ana |
| research-critic | 妥当性評価 | repo-ana |

※ reviewer / critic は **read-only** が原則

---

## Git Worktree の作成手順

### 前提
- 既存のリポジトリが `main` ブランチを持つ
- Git 2.7 以上

### 作成例
```bash
# リポジトリ直下で
git fetch

git worktree add ../repo-dev -b feature/dev
git worktree add ../repo-ana -b feature/analysis
git worktree add ../repo-exp main
```

---

## 各 Worktree の運用ルール

### repo-exp（実験）
- 追従ブランチ：`main`
- 変更禁止：src/, scripts/
- 実行物：
  - experiments/**
  - logs / results
- 使用Agent：
  - runner
  - investigator（調査のみ）

### repo-dev（実装）
- 追従ブランチ：feature/*
- 実装後は必ず reviewer を通す
- 使用Agent：
  - builder
  - reviewer
  - investigator

### repo-ana（解析）
- 追従ブランチ：feature/analysis
- experiments/**/results のみ入力に使う
- 使用Agent：
  - analyst
  - research-critic

---

## 標準フロー（研究1サイクル）

1. investigator  
   - 既存コード・論文・実験前提を docs/notes にまとめる
2. lead  
   - TASKS.md を作成（目的・受入条件を明確化）
3. builder  
   - 実装（repo-dev）
4. reviewer  
   - レビュー（No-Go なら差し戻し）
5. runner  
   - 実験実行（repo-exp）
6. analyst  
   - 集計・図表化（repo-ana）
7. research-critic  
   - 妥当性・論理性評価
8. lead  
   - Go / No-Go 判定、次タスク決定

---

## 事故防止ルール（重要）

### 実験の再現性
- 実験は必ず repo-exp で実行
- run.sh 以外での実行は禁止

### 思い込みの遮断
- reviewer / critic は実装・実験を行わない
- builder / runner は結論を出さない

### ドキュメント優先
- 調査結果は必ず docs/notes または docs/decisions に残す
- 「口頭・チャットのみ」は禁止

---

## よくある失敗と対策

| 失敗 | 対策 |
|---|---|
| 実験結果が再現できない | repo-exp + runner 限定 |
| 実装の暴走 | reviewer read-only |
| 主張の飛躍 | research-critic を必ず通す |
| 前提が共有されない | investigator → docs |

---

## 最終原則（Golden Rule）

> **「別の人（または3か月後の自分）が  
> この WORKTREE.md と CONVENTIONS.md だけで  
> 同じ研究を再現できるか？」**

YES でなければ、運用を見直す。

---
