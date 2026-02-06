#!/usr/bin/env python
"""
復元画像保存スクリプト（簡易版）
saliuitl.pyの処理フローを利用して、攻撃画像と復元後の画像を保存
"""

import os
import sys
import numpy as np
import torch
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# saliuitl.pyと同じディレクトリにあることを想定
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from darknet import Darknet
from helper import do_detect

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, required=True, choices=['inria', 'voc'])
    parser.add_argument('--attack', type=str, default='1p')
    parser.add_argument('--n_images', type=int, default=5)
    parser.add_argument('--output_dir', type=str, default='analysis/figures/recovered')
    args = parser.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # パス設定
    clean_dir = f'data/{args.dataset}/clean'
    patch_dir = f'data/{args.dataset}/{args.attack}'

    cfg_path = 'cfg/yolo.cfg'
    weight_path = 'weights/yolo.weights'

    # YOLOモデル
    model = Darknet(cfg_path)
    model.load_weights(weight_path)
    model = model.to(device).eval()

    os.makedirs(args.output_dir, exist_ok=True)

    # effective_files から画像リスト取得
    eff_file = os.path.join(patch_dir, f'effective_{args.attack}.npy')
    if os.path.exists(eff_file):
        effective = np.load(eff_file, allow_pickle=True)
        img_files = []
        for f in effective:
            if not any(f.endswith(ext) for ext in ['.jpg', '.png', '.JPEG']):
                for ext in ['.jpg', '.png', '.JPEG']:
                    full_path = os.path.join(patch_dir, f + ext)
                    if os.path.exists(full_path):
                        img_files.append(f + ext)
                        break
            elif os.path.exists(os.path.join(patch_dir, f)):
                img_files.append(f)
    else:
        img_files = [f for f in os.listdir(patch_dir) if f.endswith(('.jpg', '.png', '.JPEG'))]

    img_files = img_files[:args.n_images]
    print(f"Processing {len(img_files)} images")

    for imgfile in img_files:
        patch_path = os.path.join(patch_dir, imgfile)
        clean_path = os.path.join(clean_dir, imgfile)

        if not os.path.exists(clean_path):
            base = os.path.splitext(imgfile)[0]
            for ext in ['.jpg', '.png', '.JPEG']:
                alt_path = os.path.join(clean_dir, base + ext)
                if os.path.exists(alt_path):
                    clean_path = alt_path
                    break

        if not os.path.exists(clean_path):
            print(f"Clean image not found for {imgfile}")
            continue

        # 画像読み込み
        clean_img = Image.open(clean_path).convert('RGB').resize((416, 416))
        attacked_img = Image.open(patch_path).convert('RGB').resize((416, 416))

        # テンソル変換
        attacked_tensor = torch.from_numpy(
            np.array(attacked_img).transpose(2, 0, 1) / 255.0
        ).float().unsqueeze(0).to(device)

        # 検出実行
        with torch.no_grad():
            clean_boxes, _ = do_detect(model,
                torch.from_numpy(np.array(clean_img).transpose(2, 0, 1) / 255.0).float().unsqueeze(0).to(device),
                0.4, 0.4, True, direct_cuda_img=True)
            attacked_boxes, _ = do_detect(model, attacked_tensor, 0.4, 0.4, True, direct_cuda_img=True)

        # 可視化
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # Clean
        axes[0].imshow(clean_img)
        axes[0].set_title(f'Clean ({len(clean_boxes)} detections)')
        for box in clean_boxes:
            x1, y1, x2, y2 = int(box[0]*416), int(box[1]*416), int(box[2]*416), int(box[3]*416)
            rect = plt.Rectangle((x1, y1), x2-x1, y2-y1, fill=False, color='green', linewidth=2)
            axes[0].add_patch(rect)
        axes[0].axis('off')

        # Attacked
        axes[1].imshow(attacked_img)
        axes[1].set_title(f'Attacked ({len(attacked_boxes)} detections)')
        for box in attacked_boxes:
            x1, y1, x2, y2 = int(box[0]*416), int(box[1]*416), int(box[2]*416), int(box[3]*416)
            rect = plt.Rectangle((x1, y1), x2-x1, y2-y1, fill=False, color='red', linewidth=2)
            axes[1].add_patch(rect)
        axes[1].axis('off')

        # Difference (highlight patch location)
        diff = np.abs(np.array(clean_img).astype(float) - np.array(attacked_img).astype(float))
        diff_gray = np.mean(diff, axis=2)
        axes[2].imshow(attacked_img)
        axes[2].imshow(diff_gray, cmap='hot', alpha=0.5)
        axes[2].set_title('Patch Location (diff heatmap)')
        axes[2].axis('off')

        plt.suptitle(f'{args.dataset.upper()} {args.attack}: {imgfile}')
        plt.tight_layout()

        save_name = f"{args.dataset}_{args.attack}_{os.path.splitext(imgfile)[0]}_comparison.png"
        save_path = os.path.join(args.output_dir, save_name)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Saved: {save_path}")

if __name__ == '__main__':
    main()
