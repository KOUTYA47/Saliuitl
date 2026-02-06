"""
Oracle Inpainting Test

Ground-truthマスク（パッチ位置の正解）を使用してインペインティングを行い、
biharmonicインペインティングの上限性能を確認する。

目的: マスク精度の問題 vs インペインティング手法の問題を切り分ける
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import cv2
import os
import argparse
from PIL import Image
from skimage.restoration import inpaint_biharmonic


def find_patch_region(clean_img, attacked_img, threshold=30):
    """
    Clean画像とAttacked画像の差分からパッチ領域を検出する。

    Args:
        clean_img: クリーン画像 (H, W, 3), uint8
        attacked_img: 攻撃画像 (H, W, 3), uint8
        threshold: 差分閾値

    Returns:
        mask: パッチ領域のバイナリマスク (H, W), bool
        bbox: パッチのバウンディングボックス (x, y, w, h)
    """
    # 差分計算
    diff = np.abs(clean_img.astype(np.float32) - attacked_img.astype(np.float32))
    diff_gray = diff.mean(axis=2)

    # 閾値処理
    mask = diff_gray > threshold

    # モルフォロジー処理でノイズ除去
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_uint8 = mask.astype(np.uint8) * 255
    mask_uint8 = cv2.morphologyEx(mask_uint8, cv2.MORPH_CLOSE, kernel)
    mask_uint8 = cv2.morphologyEx(mask_uint8, cv2.MORPH_OPEN, kernel)
    mask = mask_uint8 > 0

    # バウンディングボックス
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
        bbox = (x, y, w, h)
    else:
        bbox = None

    return mask, bbox


def oracle_inpaint(attacked_img, mask):
    """
    Oracleマスクを使用してbiharmonicインペインティングを実行。

    Args:
        attacked_img: 攻撃画像 (H, W, 3), float [0, 1]
        mask: パッチ領域のマスク (H, W), bool

    Returns:
        inpainted: インペインティング後の画像 (H, W, 3), float [0, 1]
    """
    inpainted = inpaint_biharmonic(attacked_img, mask, channel_axis=-1)
    return inpainted


def compare_masks(generated_mask, oracle_mask):
    """
    生成マスクとOracleマスクを比較。

    Returns:
        iou: Intersection over Union
        precision: 正確さ（oracleの何%をカバーしているか）
        recall: 再現率（生成マスクの何%がoracleと一致するか）
    """
    intersection = (generated_mask & oracle_mask).sum()
    union = (generated_mask | oracle_mask).sum()

    iou = intersection / union if union > 0 else 0

    oracle_total = oracle_mask.sum()
    generated_total = generated_mask.sum()

    precision = intersection / generated_total if generated_total > 0 else 0
    recall = intersection / oracle_total if oracle_total > 0 else 0

    return iou, precision, recall


def visualize_oracle_test(clean_path, attacked_path, output_path,
                          generated_mask=None, diff_threshold=30):
    """
    Oracle inpaintingのテスト結果を可視化。
    """
    # 画像読み込み
    clean_img = np.array(Image.open(clean_path).convert('RGB').resize((416, 416)))
    attacked_img = np.array(Image.open(attacked_path).convert('RGB').resize((416, 416)))

    # Oracle mask生成（差分ベース）
    oracle_mask, bbox = find_patch_region(clean_img, attacked_img, threshold=diff_threshold)

    # マスクを少し膨張（境界のアーティファクト防止）
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    oracle_mask_dilated = cv2.dilate(oracle_mask.astype(np.uint8), kernel, iterations=2) > 0

    # Oracle inpainting
    attacked_float = attacked_img / 255.0
    oracle_inpainted = oracle_inpaint(attacked_float, oracle_mask_dilated)

    # マスクカバレッジ
    mask_coverage = oracle_mask.sum() / oracle_mask.size * 100

    # 可視化
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    # Row 1: 画像比較
    axes[0, 0].imshow(clean_img)
    axes[0, 0].set_title('Clean (Ground Truth)', fontsize=12)
    axes[0, 0].axis('off')

    axes[0, 1].imshow(attacked_img)
    axes[0, 1].set_title('Attacked', fontsize=12)
    if bbox:
        x, y, w, h = bbox
        rect = plt.Rectangle((x, y), w, h, fill=False, edgecolor='red', linewidth=2)
        axes[0, 1].add_patch(rect)
    axes[0, 1].axis('off')

    axes[0, 2].imshow((oracle_inpainted * 255).astype(np.uint8))
    axes[0, 2].set_title('Oracle Inpainted (Biharmonic)', fontsize=12)
    axes[0, 2].axis('off')

    # Row 2: マスクと差分
    # 差分画像
    diff = np.abs(clean_img.astype(np.float32) - attacked_img.astype(np.float32))
    axes[1, 0].imshow(diff.mean(axis=2), cmap='hot')
    axes[1, 0].set_title('Difference (Clean vs Attacked)', fontsize=12)
    axes[1, 0].axis('off')

    # Oracle mask
    axes[1, 1].imshow(oracle_mask_dilated, cmap='gray')
    axes[1, 1].set_title(f'Oracle Mask (dilated)\n{mask_coverage:.1f}% of image', fontsize=12)
    axes[1, 1].axis('off')

    # Inpainting結果と元画像の差分
    inpainted_diff = np.abs(clean_img.astype(np.float32) - (oracle_inpainted * 255))
    axes[1, 2].imshow(inpainted_diff.mean(axis=2), cmap='hot')
    inpaint_error = inpainted_diff.mean()
    axes[1, 2].set_title(f'Residual Error (Clean vs Inpainted)\nMean: {inpaint_error:.2f}', fontsize=12)
    axes[1, 2].axis('off')

    plt.suptitle(os.path.basename(clean_path), fontsize=14, fontweight='bold')
    plt.tight_layout()

    # 保存
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f'Saved: {output_path}')

    return {
        'mask_coverage': mask_coverage,
        'inpaint_error': inpaint_error,
        'bbox': bbox,
        'oracle_mask': oracle_mask_dilated,
        'oracle_inpainted': oracle_inpainted
    }


def main():
    parser = argparse.ArgumentParser(description='Oracle Inpainting Test')
    parser.add_argument('--clean_dir', type=str, required=True,
                        help='Directory containing clean images')
    parser.add_argument('--attacked_dir', type=str, required=True,
                        help='Directory containing attacked images')
    parser.add_argument('--output_dir', type=str,
                        default='experiments/exp_20260202_visual_recovery/oracle_test',
                        help='Output directory')
    parser.add_argument('--diff_threshold', type=int, default=30,
                        help='Threshold for patch detection')
    parser.add_argument('--num_images', type=int, default=10,
                        help='Number of images to process')

    args = parser.parse_args()

    # 画像リスト取得
    clean_images = sorted([f for f in os.listdir(args.clean_dir)
                          if f.endswith(('.png', '.jpg', '.jpeg'))])[:args.num_images]

    print(f'Processing {len(clean_images)} images...')
    print(f'Diff threshold: {args.diff_threshold}')

    results = []
    for img_name in clean_images:
        clean_path = os.path.join(args.clean_dir, img_name)
        attacked_path = os.path.join(args.attacked_dir, img_name)

        if not os.path.exists(attacked_path):
            print(f'Skipping {img_name}: attacked version not found')
            continue

        output_path = os.path.join(args.output_dir, f'oracle_{img_name}')

        try:
            result = visualize_oracle_test(
                clean_path, attacked_path, output_path,
                diff_threshold=args.diff_threshold
            )
            result['image_name'] = img_name
            results.append(result)
        except Exception as e:
            print(f'Error processing {img_name}: {e}')
            import traceback
            traceback.print_exc()
            continue

    # サマリー
    print('\n' + '='*60)
    print('Oracle Inpainting Test Summary')
    print('='*60)
    print(f'{"Image":<25} {"Mask %":>10} {"Error":>10}')
    print('-'*60)

    total_error = 0
    for r in results:
        print(f'{r["image_name"]:<25} {r["mask_coverage"]:>10.2f} {r["inpaint_error"]:>10.2f}')
        total_error += r["inpaint_error"]

    avg_error = total_error / len(results) if results else 0
    print('-'*60)
    print(f'{"Average":<25} {"":>10} {avg_error:>10.2f}')

    print(f'\nResults saved to: {args.output_dir}')


if __name__ == '__main__':
    main()
