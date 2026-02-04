#!/usr/bin/env python3
"""
HTMLファイル内の表を画像に差し替えるスクリプト
"""
import re
import os

BASE_DIR = "/mnt/d/csprog/ooki/Saliuitl"
HTML_PATH = f"{BASE_DIR}/docs/slides_draft_final.html"

# HTMLファイルを読み込み
with open(HTML_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 表と対応する画像のマッピング
# (表内の特徴的テキスト, 画像パス)
table_mappings = [
    (r'物体検出.*INRIA.*VOC.*YOLOv2', 'slides_material/tables/table_slide5_dataset.png'),
    (r'閾値集合.*インペインティング.*biharmonic', 'slides_material/tables/table_slide5_params.png'),
    (r'VOC.*1-patch.*0\.540.*0\.538', 'slides_material/tables/table_slide6_rr.png'),
    (r'VOC 1p.*Adv\. nmAP.*0\.509.*0\.694', 'slides_material/tables/table_slide7_nmap.png'),
    (r'VOC.*4.*0\.30s.*0\.07s.*23%', 'slides_material/tables/table_slide8_timing.png'),
    (r'Recovery Rate.*概ね再現', 'slides_material/tables/table_slide12_conclusion.png'),
]

# 全ての表を検索
table_pattern = r'<table[^>]*>.*?</table>'
tables = list(re.finditer(table_pattern, content, re.DOTALL))

print(f"Found {len(tables)} tables in HTML")

replaced_count = 0
for pattern, img_path in table_mappings:
    for match in tables:
        table_content = match.group()
        if re.search(pattern, table_content, re.DOTALL | re.IGNORECASE):
            # 画像タグで置換
            img_tag = f'''<div style="text-align: center; margin: 20px 0;">
<img src="{img_path}" alt="Table" style="max-width: 85%; height: auto;">
</div>'''
            content = content.replace(table_content, img_tag, 1)
            print(f"Replaced table with {img_path}")
            replaced_count += 1
            break

# 結果を保存
with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

# 残りの表を確認
remaining = len(re.findall(table_pattern, content, re.DOTALL))
print(f"\nReplaced: {replaced_count} tables")
print(f"Remaining: {remaining} tables")
print(f"Updated: {HTML_PATH}")
