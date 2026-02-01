#!/usr/bin/env python
"""
復元画像保存スクリプト
攻撃画像と復元後の画像を並べて保存する
"""

import os
import argparse
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from skimage.restoration import inpaint
from sklearn.cluster import DBSCAN
import copy
from tqdm import tqdm

from darknet import Darknet
from helper import do_detect, nms, clustering_data_preprocessing
import nets.attack_detector

def save_comparison(original, attacked, recovered, mask, save_path, title=""):
    """3枚の画像を横に並べて保存"""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))

    axes[0].imshow(original)
    axes[0].set_title('Clean')
    axes[0].axis('off')

    axes[1].imshow(attacked)
    axes[1].set_title('Attacked')
    axes[1].axis('off')

    axes[2].imshow(recovered)
    axes[2].set_title('Recovered')
    axes[2].axis('off')

    axes[3].imshow(mask, cmap='hot')
    axes[3].set_title('Detection Mask')
    axes[3].axis('off')

    plt.suptitle(title)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

def process_image(model, detector, img_path, clean_path, args, device):
    """1枚の画像を処理して復元"""
    # 画像読み込み
    attacked_img = Image.open(img_path).convert('RGB')
    clean_img = Image.open(clean_path).convert('RGB')

    # テンソル変換
    attacked_tensor = torch.from_numpy(np.array(attacked_img).transpose(2, 0, 1) / 255.0).float().unsqueeze(0).to(device)

    # 特徴マップ抽出と検出
    with torch.no_grad():
        boxes, feature_map = do_detect(model, attacked_tensor, 0.4, 0.4, True, p=None, direct_cuda_img=True)

    fm = feature_map[0].detach().cpu().numpy()
    fm = np.sum(fm, axis=0)

    # DBSCANクラスタリングで属性抽出
    clus_feats = ['n_clusters', 'mean_clus_dist', 'sd', 'impscore']
    vector_s = []
    biginfo = []

    revran = [0.0 + x * 0.01 for x in range(0, 100, args.ensemble_step)]

    for beta in revran:
        bfm = (fm >= np.quantile(fm, beta)).astype(float)
        p = np.where(bfm > 0)

        if len(p[0]) > 0:
            clust = DBSCAN(eps=args.dbscan_eps, min_samples=args.dbscan_min_pts).fit(np.array(p).T)
            labels = clust.labels_
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)

            distances = []
            for label in set(labels):
                if label != -1:
                    cluster_points = np.array(p).T[labels == label]
                    if len(cluster_points) > 1:
                        center = cluster_points.mean(axis=0)
                        dist = np.sqrt(np.sum((cluster_points - center) ** 2, axis=1)).mean()
                        distances.append(dist)

            mean_dist = np.mean(distances) if distances else 0
            sd_dist = np.std(distances) if distances else 0
            imp_score = np.sum(fm * bfm) / max(1, np.sum(bfm))

            vector_s.append([n_clusters, mean_dist, sd_dist, imp_score])
            biginfo.append((bfm, labels, p))
        else:
            vector_s.append([0, 0, 0, 0])
            biginfo.append((bfm, [], ([], [])))

    # Attack Detector
    vector_s = np.array(vector_s).reshape((1, len(vector_s), len(clus_feats)))
    detector_input = 2 * nn.functional.normalize(
        torch.Tensor(clustering_data_preprocessing(vector_s, skip=True)),
        dim=2, p=float('inf')
    ) - 1

    with torch.no_grad():
        detection_score = detector(detector_input.to(device)).cpu().numpy()

    detected = detection_score >= args.nn_det_threshold

    # マスク生成と復元
    if detected:
        my_mask = np.zeros(fm.shape)
        revran_inp = list(reversed([0.0 + x * 0.01 for x in range(0, 100, args.inpainting_step)]))[:-1]

        for beta in revran_inp:
            idx = int(beta * 100 / args.ensemble_step)
            if idx < len(biginfo):
                bfm, labels, p = biginfo[idx]
                if len(p[0]) > 0:
                    # マスク更新
                    my_mask = np.maximum(my_mask, bfm)

        # インペインティング
        in_img = attacked_tensor.squeeze(0).cpu().numpy()

        # マスクを画像サイズにリサイズ
        mask_resized = np.array(Image.fromarray((my_mask * 255).astype(np.uint8)).resize(
            (in_img.shape[2], in_img.shape[1]), Image.NEAREST
        )) / 255.0

        if args.inpaint == 'biharmonic':
            recovered = inpaint.inpaint_biharmonic(in_img, mask_resized, channel_axis=0)
        elif args.inpaint == 'zero':
            recovered = in_img.copy()
            p = np.where(mask_resized > 0)
            recovered[:, p[0], p[1]] = 0
        else:
            recovered = in_img

        recovered_img = (recovered.transpose(1, 2, 0) * 255).astype(np.uint8)
    else:
        recovered_img = np.array(attacked_img)
        my_mask = np.zeros(fm.shape)

    return {
        'clean': np.array(clean_img),
        'attacked': np.array(attacked_img),
        'recovered': recovered_img,
        'mask': my_mask,
        'detected': detected,
        'score': detection_score[0][0]
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, required=True, choices=['inria', 'voc', 'cifar', 'imagenet'])
    parser.add_argument('--attack', type=str, default='1p', help='Attack type: 1p, 2p, trig, mo')
    parser.add_argument('--n_images', type=int, default=5, help='Number of images to process')
    parser.add_argument('--ensemble_step', type=int, default=5)
    parser.add_argument('--inpainting_step', type=int, default=5)
    parser.add_argument('--inpaint', type=str, default='biharmonic')
    parser.add_argument('--nn_det_threshold', type=float, default=0.5)
    parser.add_argument('--dbscan_eps', type=float, default=1.0)
    parser.add_argument('--dbscan_min_pts', type=int, default=4)
    parser.add_argument('--output_dir', type=str, default='analysis/figures/recovered')
    args = parser.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # パス設定
    if args.dataset in ['inria', 'voc']:
        clean_dir = f'data/{args.dataset}/clean'
        patch_dir = f'data/{args.dataset}/{args.attack}'
        det_path = f'checkpoints/final_detection/2dcnn_raw_{args.dataset if args.dataset == "inria" else "VOC"}_5_atk_det.pth'
        cfg_path = 'cfg/yolo.cfg'
        weight_path = 'weights/yolo.weights'

        # YOLOモデル
        model = Darknet(cfg_path)
        model.load_weights(weight_path)
        model = model.to(device).eval()
    else:
        print(f"Dataset {args.dataset} not fully supported for visualization yet")
        return

    # Attack Detector
    detector = nets.attack_detector.cnn_raw(in_feats=4).to(device)
    checkpoint = torch.load(det_path, map_location=device)
    # Remove "module." prefix if present (from DataParallel)
    state_dict = checkpoint['net']
    new_state_dict = {}
    for k, v in state_dict.items():
        if k.startswith('module.'):
            new_state_dict[k[7:]] = v
        else:
            new_state_dict[k] = v
    detector.load_state_dict(new_state_dict)
    detector.eval()

    # 出力ディレクトリ
    os.makedirs(args.output_dir, exist_ok=True)

    # effective_files から画像リスト取得
    eff_file = os.path.join(patch_dir, f'effective_{args.attack}.npy')
    if os.path.exists(eff_file):
        effective = np.load(eff_file, allow_pickle=True)
        # ファイル名にはベース名のみが含まれている場合があるので、拡張子を補完
        img_files = []
        for f in effective:
            # 拡張子がない場合は探す
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

    print(f"Processing {len(img_files)} images from {args.dataset}/{args.attack}")

    for imgfile in tqdm(img_files):
        patch_path = os.path.join(patch_dir, imgfile)
        clean_path = os.path.join(clean_dir, imgfile)

        if not os.path.exists(clean_path):
            # 拡張子を変えて試す
            base = os.path.splitext(imgfile)[0]
            for ext in ['.jpg', '.png', '.JPEG']:
                alt_path = os.path.join(clean_dir, base + ext)
                if os.path.exists(alt_path):
                    clean_path = alt_path
                    break

        if not os.path.exists(clean_path):
            print(f"Clean image not found for {imgfile}")
            continue

        result = process_image(model, detector, patch_path, clean_path, args, device)

        # 保存
        save_name = f"{args.dataset}_{args.attack}_{os.path.splitext(imgfile)[0]}.png"
        save_path = os.path.join(args.output_dir, save_name)

        title = f"{args.dataset.upper()} {args.attack} - Score: {result['score']:.4f} - {'Detected' if result['detected'] else 'Not Detected'}"
        save_comparison(
            result['clean'],
            result['attacked'],
            result['recovered'],
            result['mask'],
            save_path,
            title
        )
        print(f"Saved: {save_path}")

if __name__ == '__main__':
    main()
