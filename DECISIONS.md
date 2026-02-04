# DECISIONS.md
研究上の重要な判断と、その理由を記録する。

---

## D-YYYY-MM-DD: <判断の要約タイトル>

### 背景（Background）
- この判断が必要になった理由
- 直面していた問題・選択肢

### 検討した選択肢（Options）
- Option A:
- Option B:
- Option C:

### 判断（Decision）
- 採用した選択肢：

### 判断理由（Rationale）
- なぜこれを選んだか
- 技術的・実務的・研究的理由

### 却下理由（Why not others）
- 他の選択肢を採用しなかった理由

### 影響範囲（Impact）
- どの実験・コード・結果に影響するか

### 備考（Notes）
- 将来見直す可能性
- 未解決の懸念

---

## D-2026-02-02: 復元画像保存機能をsaliuitl.py本体に追加

### 背景（Background）
- ユーザーから復元画像の出力を要求された
- 当初、別スクリプト（save_recovered_images.py）を作成したが、復元ロジックが複雑で正確に再現できなかった

### 検討した選択肢（Options）
- Option A: 別スクリプトで復元ロジックを再実装
- Option B: saliuitl.py に画像保存オプションを追加
- Option C: saliuitl.py の出力をパイプして後処理

### 判断（Decision）
- 採用した選択肢：Option B（saliuitl.py本体に追加）

### 判断理由（Rationale）
- 復元処理が反復的で複雑（β値ごとにDBSCANクラスタリング→インペインティング→再検出）
- 本体に追加すれば、`in_img`（復元画像）に直接アクセス可能
- 追加オプション（--save_images）でデフォルト動作に影響なし

### 却下理由（Why not others）
- Option A: 別スクリプトでの再実装は不正確になった（マスクが大きすぎる問題）
- Option C: 復元途中の画像はstdoutに出力されないため不可

### 影響範囲（Impact）
- saliuitl.py に3つの引数追加（--save_images, --save_images_dir, --save_images_limit）
- matplotlib の条件付きインポート追加
- 復元処理後に画像保存コード追加（約50行）

### 備考（Notes）
- 物体検出（INRIA/VOC）のみ対応、分類タスク（CIFAR/ImageNet）は未対応
- Detection Maskの可視化に問題あり（特徴マップサイズが小さい）

---

## D-2026-02-05: Oracle TestによるボトルネックをマスクRR精度と特定

### 背景（Background）
- R-2026-02-02-Eで「成功」判定でもパッチが視覚的に残存する問題を発見
- 原因候補: (A) マスク精度の問題 vs (B) インペインティング手法の問題
- 定量的な切り分けが必要

### 検討した選択肢（Options）
- Option A: マスク生成アルゴリズムの詳細分析
- Option B: Oracle Testで上限性能を測定し、差分からボトルネックを特定
- Option C: 複数のインペインティング手法（zero, mean, diffusion）を比較

### 判断（Decision）
- 採用した選択肢：Option B（Oracle Test）

### 判断理由（Rationale）
- Oracle Testは「マスクが完璧な場合」の上限性能を示す
- Biharmonicとの差 = マスク不正確性による損失を直接測定可能
- 全データセットで実施することで、タスク間の差異も明確化

### 却下理由（Why not others）
- Option A: 実装詳細の分析は時間がかかり、定量的評価が困難
- Option C: インペインティング手法の比較はマスク精度の問題と混在する

### 影響範囲（Impact）
- 物体検出: インペインティング品質の影響が大きい（Oracle vs Bio: **+22.8%**）
- 画像分類: インペインティング品質の影響は限定的（**+0.8%**）
- **結論**: 物体検出ではインペインティング品質改善に余地あり、ただしマスク精度の問題は別途改善が必要

### 備考（Notes）
- 高解像度特徴マップ（Layer 10: 52×52）の使用が有望
- ただしADモデルの再学習が必要になる可能性あり
