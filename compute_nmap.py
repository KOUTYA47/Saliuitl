"""
nmAP (normalized mean Average Precision) 計算スクリプト

論文定義（Section 4.1）:
- adversarial nmAP = mAP(recovered attacked images) / mAP(clean images, no defense)
- clean nmAP = mAP(clean images with defense) / mAP(clean images, no defense)

Ground truth: クリーン画像に対するモデルの予測 h(xi)

saliuitl.py --save_outcomes の出力形式:
- clean_map: [cx, cy, w, h, class_id, 0, 0] (7列)
- rec_map: [cx, cy, w, h, class_id, conf] (6列)
"""

import numpy as np
import argparse
from collections import defaultdict


def compute_iou_cxcywh(box1, box2):
    """
    Compute IoU between two boxes in (cx, cy, w, h) format.
    """
    # Convert to (x1, y1, x2, y2)
    x1_1 = box1[0] - box1[2] / 2
    y1_1 = box1[1] - box1[3] / 2
    x2_1 = box1[0] + box1[2] / 2
    y2_1 = box1[1] + box1[3] / 2

    x1_2 = box2[0] - box2[2] / 2
    y1_2 = box2[1] - box2[3] / 2
    x2_2 = box2[0] + box2[2] / 2
    y2_2 = box2[1] + box2[3] / 2

    # Intersection
    xi1 = max(x1_1, x1_2)
    yi1 = max(y1_1, y1_2)
    xi2 = min(x2_1, x2_2)
    yi2 = min(y2_1, y2_2)

    inter_w = max(0, xi2 - xi1)
    inter_h = max(0, yi2 - yi1)
    inter_area = inter_w * inter_h

    # Union
    area1 = box1[2] * box1[3]
    area2 = box2[2] * box2[3]
    union_area = area1 + area2 - inter_area

    if union_area <= 0:
        return 0.0

    return inter_area / union_area


def compute_ap(recalls, precisions):
    """
    Compute Average Precision using all-point interpolation.
    """
    recalls = np.concatenate(([0.0], recalls, [1.0]))
    precisions = np.concatenate(([0.0], precisions, [0.0]))

    for i in range(len(precisions) - 1, 0, -1):
        precisions[i - 1] = max(precisions[i - 1], precisions[i])

    i = np.where(recalls[1:] != recalls[:-1])[0]
    ap = np.sum((recalls[i + 1] - recalls[i]) * precisions[i + 1])

    return ap


def compute_map(gt_boxes_list, pred_boxes_list, iou_threshold=0.5):
    """
    Compute mAP over a list of images.

    Data format (from saliuitl.py --save_outcomes):
    - gt_boxes (clean_map): [cx, cy, w, h, class_id, 0, 0]
    - pred_boxes (rec_map): [cx, cy, w, h, class_id, conf]
    """
    all_predictions = defaultdict(list)
    all_gt_counts = defaultdict(int)

    for img_idx, (gt_boxes, pred_boxes) in enumerate(zip(gt_boxes_list, pred_boxes_list)):
        gt_boxes = np.array(gt_boxes) if len(gt_boxes) > 0 else np.zeros((0, 7))
        pred_boxes = np.array(pred_boxes) if len(pred_boxes) > 0 else np.zeros((0, 6))

        # Count GT per class (class_id at index 4)
        if len(gt_boxes) > 0:
            for gt in gt_boxes:
                cls = int(gt[4])
                all_gt_counts[cls] += 1

        gt_matched = [False] * len(gt_boxes)

        # Sort predictions by confidence (conf at index 5)
        if len(pred_boxes) > 0:
            sorted_indices = np.argsort(-pred_boxes[:, 5])
            pred_boxes = pred_boxes[sorted_indices]

            for pred in pred_boxes:
                cls = int(pred[4])
                conf = pred[5]

                best_iou = 0
                best_gt_idx = -1

                for gt_idx, gt in enumerate(gt_boxes):
                    gt_cls = int(gt[4])
                    if gt_cls != cls:
                        continue
                    if gt_matched[gt_idx]:
                        continue

                    iou = compute_iou_cxcywh(pred[:4], gt[:4])
                    if iou > best_iou:
                        best_iou = iou
                        best_gt_idx = gt_idx

                if best_iou >= iou_threshold and best_gt_idx >= 0:
                    gt_matched[best_gt_idx] = True
                    all_predictions[cls].append((conf, 1, img_idx))  # TP
                else:
                    all_predictions[cls].append((conf, 0, img_idx))  # FP

    # Compute AP per class
    ap_per_class = {}

    for cls in set(list(all_predictions.keys()) + list(all_gt_counts.keys())):
        preds = all_predictions.get(cls, [])
        n_gt = all_gt_counts.get(cls, 0)

        if n_gt == 0:
            continue

        if len(preds) == 0:
            ap_per_class[cls] = 0.0
            continue

        preds = sorted(preds, key=lambda x: -x[0])
        tp = np.array([p[1] for p in preds])
        tp_cumsum = np.cumsum(tp)
        fp_cumsum = np.cumsum(1 - tp)

        precision = tp_cumsum / (tp_cumsum + fp_cumsum)
        recall = tp_cumsum / n_gt

        ap = compute_ap(recall, precision)
        ap_per_class[cls] = ap

    if len(ap_per_class) > 0:
        mAP = np.mean(list(ap_per_class.values()))
    else:
        mAP = 0.0

    return mAP, ap_per_class


def load_outcomes(filepath):
    """
    Load outcomes saved by saliuitl.py --save_outcomes
    """
    data = np.load(filepath, allow_pickle=True)
    return data


def main():
    parser = argparse.ArgumentParser(description='Compute nmAP from saliuitl outcomes')
    parser.add_argument('--attacked_outcomes', type=str, required=True,
                        help='Path to attacked image outcomes (.npy)')
    parser.add_argument('--clean_outcomes', type=str, default=None,
                        help='Path to clean image outcomes (.npy) for baseline mAP')
    parser.add_argument('--iou_threshold', type=float, default=0.5,
                        help='IoU threshold for mAP calculation')
    args = parser.parse_args()

    print("=" * 50)
    print("nmAP Calculation")
    print("=" * 50)

    # Load attacked outcomes
    attacked_data = load_outcomes(args.attacked_outcomes)

    gt_boxes_list = []
    rec_boxes_list = []

    for item in attacked_data:
        clean_map, rec_map = item
        gt_boxes_list.append(clean_map)
        rec_boxes_list.append(rec_map)

    print(f"\nAttacked images: {len(attacked_data)} samples")

    # Compute mAP for recovered attacked images
    adv_map, adv_ap = compute_map(gt_boxes_list, rec_boxes_list, args.iou_threshold)
    print(f"Adversarial mAP (recovered): {adv_map:.4f}")

    # If clean outcomes provided, compute baseline mAP
    if args.clean_outcomes:
        clean_data = load_outcomes(args.clean_outcomes)

        clean_gt_list = []
        clean_pred_list = []

        for item in clean_data:
            clean_map, pred_map = item
            clean_gt_list.append(clean_map)
            clean_pred_list.append(pred_map)

        print(f"Clean images: {len(clean_data)} samples")

        # For baseline: clean images without recovery
        # GT = clean detections, Pred = also clean detections (no attack)
        # This should give mAP close to 1.0
        baseline_map, _ = compute_map(clean_gt_list, clean_pred_list, args.iou_threshold)
        print(f"Baseline mAP (clean, no attack): {baseline_map:.4f}")

        # Compute nmAP
        if baseline_map > 0:
            adv_nmap = adv_map / baseline_map
            clean_nmap = baseline_map / baseline_map
            print(f"\n{'=' * 50}")
            print("nmAP Results")
            print(f"{'=' * 50}")
            print(f"Adversarial nmAP: {adv_nmap:.4f}")
            print(f"Clean nmAP: {clean_nmap:.4f}")
        else:
            print("\nWarning: Baseline mAP is 0, cannot compute nmAP")
    else:
        print("\nNote: Clean outcomes not provided.")
        print(f"Adversarial nmAP (assuming baseline=1.0): {adv_map:.4f}")


if __name__ == '__main__':
    main()
