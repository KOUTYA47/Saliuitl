#!/usr/bin/env python3
"""
extract_detection_features.py
─────────────────────────────
Clean/Attacked画像の特徴マップから4属性（クラスタ数, 平均クラスタ内距離,
距離のstd, 活性ニューロン数）をbeta毎に抽出し、
論文中のグラフを再現する。

出力:
  - CSV: per-image, per-beta, clean/attacked の4属性
  - PNG: 4属性の比較グラフ（divergenceハイライト付き）

Usage (Docker内):
  python scripts/extract_detection_features.py \
    --dataset voc \
    --imgdir data/voc/clean \
    --patch_imgdir data/voc/1p \
    --effective_files effective_1p.npy \
    --det_net_path checkpoints/final_detection/2dcnn_raw_voc_5_atk_det.pth \
    --outdir experiments/exp_20260209_detection_features \
    --lim 10
"""
import sys, os, copy, argparse, warnings
import numpy as np
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from scipy.spatial import distance_matrix
from tqdm import tqdm

# ── project imports ──
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from darknet import Darknet
from helper import do_detect, clustering_data_preprocessing

warnings.filterwarnings("ignore")

# ───────────── args ─────────────
parser = argparse.ArgumentParser()
parser.add_argument("--dataset", default="voc", choices=("inria", "voc"))
parser.add_argument("--imgdir", required=True)
parser.add_argument("--patch_imgdir", required=True)
parser.add_argument("--effective_files", default=None)
parser.add_argument("--cfg", default="cfg/yolo.cfg")
parser.add_argument("--weightfile", default="weights/yolo.weights")
parser.add_argument("--det_net_path", required=True)
parser.add_argument("--ensemble_step", default=5, type=int)
parser.add_argument("--dbscan_eps", default=1.0, type=float)
parser.add_argument("--dbscan_min_pts", default=4, type=int)
parser.add_argument("--nn_det_threshold", default=0.5, type=float)
parser.add_argument("--outdir", default="experiments/exp_20260209_detection_features")
parser.add_argument("--lim", default=10, type=int)
args = parser.parse_args()

os.makedirs(args.outdir, exist_ok=True)
os.makedirs(os.path.join(args.outdir, "figures"), exist_ok=True)
device = "cuda" if torch.cuda.is_available() else "cpu"

# ───────────── beta_iteration (saliuitl.pyから抽出) ─────────────
def beta_iteration(beta, fm, dbscan_eps, dbscan_min_pts):
    """beta閾値で二値化 → DBSCAN → 4属性を返す"""
    binarized_fm = np.array(fm >= np.max(fm) * beta, dtype="float32")
    x, y = np.where(binarized_fm > 0)
    if len(x) == 0:
        return [0, 0.0, 0.0, 0.0]
    thing = np.hstack((x.reshape(-1, 1), y.reshape(-1, 1)))
    # StandardScaler OFF by default (with_mean=False, with_std=False)
    thing = StandardScaler(with_mean=False, with_std=False).fit_transform(thing)
    cluster = DBSCAN(eps=dbscan_eps, min_samples=dbscan_min_pts).fit(thing)
    clusters = np.unique(cluster.labels_)
    n_clusters = len([l for l in clusters if l != -1])

    avg_ic_d = []
    for cluster_label in clusters:
        if cluster_label == -1:
            continue
        data_c = thing[cluster.labels_ == cluster_label]
        data_samp = data_c[np.random.choice(len(data_c), size=min(1000, len(data_c)), replace=False)]
        dmx = distance_matrix(data_samp, data_samp)
        dmx = dmx[np.tril_indices(dmx.shape[0], k=-1)]
        if len(dmx):
            avg_ic_d.append(np.mean(dmx))

    avg_intracluster_d = np.mean(avg_ic_d) if avg_ic_d else 0.0
    avg_intracluster_std = np.std(avg_ic_d) if avg_ic_d else 0.0
    importance = float(binarized_fm.sum())

    return [n_clusters, avg_intracluster_d, avg_intracluster_std, importance]


# ───────────── load models ─────────────
print("Loading YOLOv2...")
model = Darknet(args.cfg)
model.load_weights(args.weightfile)
model = model.eval().cuda()

print("Loading Attack Detector...")
import nets.attack_detector
net = nets.attack_detector.cnn_raw(in_feats=4)
net = net.to(device)
if device == "cuda":
    net = torch.nn.DataParallel(net)
checkpoint = torch.load(args.det_net_path)
net.load_state_dict(checkpoint["net"])
net.eval()

# ───────────── load effective files ─────────────
patchdir = args.patch_imgdir
if args.effective_files is not None:
    eff_files = list(np.load(os.path.join(patchdir, args.effective_files)))
    eff_files = [x.split(".")[0] for x in eff_files]
else:
    eff_files = None

# ───────────── beta list ─────────────
betas = [round(0.0 + x * 0.01, 2) for x in range(0, 100, args.ensemble_step)]
print(f"Beta values ({len(betas)}): {betas}")

# ───────────── main loop ─────────────
transform = transforms.ToTensor()
imgdir = args.imgdir
val_dataset = sorted(os.listdir(imgdir))[: args.lim]

all_records = []  # for CSV
per_image_data = []  # for plotting

for imgfile in tqdm(val_dataset):
    if not (imgfile.endswith(".jpg") or imgfile.endswith(".png")):
        continue
    nameee = imgfile.split(".")[0]
    if eff_files is not None and nameee not in eff_files:
        continue

    patchfile = os.path.join(patchdir, imgfile)
    cleanfile = os.path.join(imgdir, imgfile)
    if not os.path.exists(patchfile):
        continue

    # ── forward pass: clean ──
    clean_img = Image.open(cleanfile).convert("RGB")
    clean_tensor = transform(clean_img).cuda().unsqueeze(0)
    clean_boxes, clean_fm = do_detect(model, clean_tensor, 0.4, 0.4, True, direct_cuda_img=True)
    if not len(clean_boxes):
        continue

    # ── forward pass: attacked ──
    atk_img = Image.open(patchfile).convert("RGB")
    atk_tensor = transform(atk_img).cuda().unsqueeze(0)
    atk_boxes, atk_fm = do_detect(model, atk_tensor, 0.4, 0.4, True, direct_cuda_img=True)

    # ── feature maps → 2D spatial map ──
    fm_clean = np.sum(clean_fm[0].detach().cpu().numpy(), axis=0)
    fm_atk = np.sum(atk_fm[0].detach().cpu().numpy(), axis=0)

    # ── extract 4 attrs per beta ──
    clean_attrs = []  # (num_betas, 4)
    atk_attrs = []

    for beta in betas:
        ca = beta_iteration(beta, fm_clean, args.dbscan_eps, args.dbscan_min_pts)
        aa = beta_iteration(beta, fm_atk, args.dbscan_eps, args.dbscan_min_pts)
        clean_attrs.append(ca)
        atk_attrs.append(aa)

    clean_attrs = np.array(clean_attrs)  # (num_betas, 4)
    atk_attrs = np.array(atk_attrs)

    # ── L∞ normalization (per-channel across betas) + 2x-1 scaling ──
    clean_norm = clean_attrs.copy()
    atk_norm = atk_attrs.copy()
    # Replicate saliuitl.py's normalization:
    # vector_s → reshape(1, num_betas, 4) → transpose(0,2,1) → (1, 4, num_betas)
    # nn.functional.normalize(dim=2, p=inf) → per-channel max across betas
    # 2*x - 1
    for feat_idx in range(4):
        # Only attacked is used in actual detection, but we normalize both for comparison
        max_val = np.max(np.abs(atk_attrs[:, feat_idx]))
        if max_val > 0:
            atk_norm[:, feat_idx] = atk_attrs[:, feat_idx] / max_val
        max_val_c = np.max(np.abs(clean_attrs[:, feat_idx]))
        if max_val_c > 0:
            clean_norm[:, feat_idx] = clean_attrs[:, feat_idx] / max_val_c
    # 2x - 1 transform
    atk_scaled = 2 * atk_norm - 1
    clean_scaled = 2 * clean_norm - 1

    # ── AD inference (on attacked) ──
    vs = np.array([a for a in atk_attrs]).reshape(1, len(betas), 4)
    vs_tensor = torch.Tensor(clustering_data_preprocessing(vs, skip=True))
    detector_input = 2 * nn.functional.normalize(vs_tensor, dim=2, p=float("inf")) - 1
    with torch.no_grad():
        det_output = net(detector_input.to(device))
    det_score = float(det_output.detach().cpu().numpy().flatten()[0])

    # ── AD inference (on clean) ──
    vs_c = np.array([a for a in clean_attrs]).reshape(1, len(betas), 4)
    vs_c_tensor = torch.Tensor(clustering_data_preprocessing(vs_c, skip=True))
    det_input_c = 2 * nn.functional.normalize(vs_c_tensor, dim=2, p=float("inf")) - 1
    with torch.no_grad():
        det_output_c = net(det_input_c.to(device))
    det_score_clean = float(det_output_c.detach().cpu().numpy().flatten()[0])

    # ── save records ──
    for bi, beta in enumerate(betas):
        for img_type, attrs in [("clean", clean_attrs), ("attacked", atk_attrs)]:
            all_records.append({
                "image": nameee,
                "type": img_type,
                "beta": beta,
                "n_clusters": attrs[bi, 0],
                "avg_intra_dist": attrs[bi, 1],
                "std_intra_dist": attrs[bi, 2],
                "importance": attrs[bi, 3],
            })

    per_image_data.append({
        "image": nameee,
        "betas": betas,
        "clean_raw": clean_attrs,
        "atk_raw": atk_attrs,
        "clean_scaled": clean_scaled,
        "atk_scaled": atk_scaled,
        "det_score_atk": det_score,
        "det_score_clean": det_score_clean,
    })
    print(f"  {nameee}: AD_score(atk)={det_score:.4f}, AD_score(clean)={det_score_clean:.4f}")

# ───────────── save CSV ─────────────
import csv
csv_path = os.path.join(args.outdir, "detection_features.csv")
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "image", "type", "beta", "n_clusters", "avg_intra_dist", "std_intra_dist", "importance"])
    writer.writeheader()
    writer.writerows(all_records)
print(f"Saved {len(all_records)} records to {csv_path}")

if not per_image_data:
    print("No images processed. Exiting.")
    sys.exit(0)

# ───────────── plotting ─────────────
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch

# Font setup: try Japanese font, fall back to DejaVu
try:
    import matplotlib.font_manager as fm
    jp_fonts = [f.fname for f in fm.fontManager.ttflist
                if any(n in f.name for n in ["Noto Sans CJK", "IPAGothic", "IPAexGothic", "Takao"])]
    if jp_fonts:
        plt.rcParams["font.family"] = fm.FontProperties(fname=jp_fonts[0]).get_name()
        print(f"Using Japanese font: {jp_fonts[0]}")
    else:
        raise FileNotFoundError
except Exception:
    print("Japanese font not found. Using English labels.")
    plt.rcParams["font.family"] = "DejaVu Sans"

ATTR_LABELS = [
    "Number of Clusters\n(n_clusters)",
    "Mean Intra-Cluster Distance\n(avg_intra_dist)",
    "Std of Intra-Cluster Distance\n(std_intra_dist)",
    "Active Neurons\n(importance)"
]
ATTR_SHORT = ["n_clusters", "avg_intra_dist", "std_intra_dist", "importance"]


# ─── Figure 1: Raw attribute values (mean) with divergence ───
def plot_mean_with_divergence(per_image_data, outpath):
    betas = np.array(per_image_data[0]["betas"])
    n = len(per_image_data)

    clean_stack = np.stack([d["clean_raw"] for d in per_image_data])  # (N, B, 4)
    atk_stack = np.stack([d["atk_raw"] for d in per_image_data])

    clean_mean = clean_stack.mean(axis=0)  # (B, 4)
    atk_mean = atk_stack.mean(axis=0)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        f"Detection Stage: 4 Clustering Attributes — Clean vs Attacked (n={n} images)\n"
        "Shaded area = divergence that AD uses for attack/benign classification",
        fontsize=13, fontweight="bold")

    for idx, ax in enumerate(axes.flat):
        c_vals = clean_mean[:, idx]
        a_vals = atk_mean[:, idx]

        # Individual images (faint)
        for d in per_image_data:
            ax.plot(betas, d["clean_raw"][:, idx], color="steelblue", alpha=0.10, linewidth=0.6)
            ax.plot(betas, d["atk_raw"][:, idx], color="indianred", alpha=0.10, linewidth=0.6)

        # Mean lines
        ax.plot(betas, c_vals, color="royalblue", linewidth=2.5, label="Clean (mean)", zorder=5)
        ax.plot(betas, a_vals, color="crimson", linewidth=2.5, label="Attacked (mean)", zorder=5)

        # Divergence shading
        ax.fill_between(betas, c_vals, a_vals, alpha=0.30, color="gold",
                         label="Divergence", zorder=3)

        # Max divergence annotation
        div = np.abs(a_vals - c_vals)
        max_idx = np.argmax(div)
        mid_y = (c_vals[max_idx] + a_vals[max_idx]) / 2
        ax.annotate(
            f"Max div.\n  b={betas[max_idx]:.2f}",
            xy=(betas[max_idx], mid_y),
            fontsize=8, ha="center",
            arrowprops=dict(arrowstyle="->", color="darkorange", lw=1.5),
            xytext=(min(betas[max_idx] + 0.12, 0.9),
                    mid_y + div.max() * 0.35),
            color="darkorange", fontweight="bold", zorder=10)

        ax.set_title(ATTR_LABELS[idx], fontsize=11)
        ax.set_xlabel("beta (saliency threshold)")
        ax.set_ylabel("Raw value")
        ax.legend(fontsize=8, loc="upper right")
        ax.grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.92])
    plt.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {outpath}")


# ─── Figure 2: Normalized AD input [-1,1] with detection score ───
def plot_normalized_ad_input(per_image_data, outpath):
    betas = np.array(per_image_data[0]["betas"])
    n = len(per_image_data)

    clean_stack = np.stack([d["clean_scaled"] for d in per_image_data])
    atk_stack = np.stack([d["atk_scaled"] for d in per_image_data])
    clean_mean = clean_stack.mean(axis=0)
    atk_mean = atk_stack.mean(axis=0)

    det_scores_atk = [d["det_score_atk"] for d in per_image_data]
    det_scores_clean = [d["det_score_clean"] for d in per_image_data]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        f"AD Input (L-inf normalized, scaled to [-1, 1]) — n={n} images\n"
        f"AD output: Attacked mean={np.mean(det_scores_atk):.4f},  "
        f"Clean mean={np.mean(det_scores_clean):.4f}   "
        f"(threshold={args.nn_det_threshold})",
        fontsize=12, fontweight="bold")

    for idx, ax in enumerate(axes.flat):
        c_vals = clean_mean[:, idx]
        a_vals = atk_mean[:, idx]

        for d in per_image_data:
            ax.plot(betas, d["clean_scaled"][:, idx], color="steelblue", alpha=0.10, linewidth=0.6)
            ax.plot(betas, d["atk_scaled"][:, idx], color="indianred", alpha=0.10, linewidth=0.6)

        ax.plot(betas, c_vals, color="royalblue", linewidth=2.5, label="Clean (mean)", zorder=5)
        ax.plot(betas, a_vals, color="crimson", linewidth=2.5, label="Attacked (mean)", zorder=5)

        ax.fill_between(betas, c_vals, a_vals, alpha=0.25, color="gold", label="Divergence", zorder=3)
        ax.axhline(y=0, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)

        ax.set_title(ATTR_LABELS[idx], fontsize=11)
        ax.set_xlabel("beta (saliency threshold)")
        ax.set_ylabel("Normalized value [-1, 1]")
        ax.set_ylim(-1.15, 1.15)
        ax.legend(fontsize=8, loc="best")
        ax.grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.89])
    plt.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {outpath}")


# ─── Figure 3: Single image detail with attribution ───
def plot_single_image(data, outpath):
    betas = np.array(data["betas"])
    detected = data["det_score_atk"] >= args.nn_det_threshold
    verdict = "ATTACK DETECTED" if detected else "Benign"

    fig = plt.figure(figsize=(16, 13))
    gs = gridspec.GridSpec(3, 2, height_ratios=[1, 1, 0.45], hspace=0.38, wspace=0.3)

    fig.suptitle(
        f"Image: {data['image']}   |   "
        f"AD Score: Attacked={data['det_score_atk']:.4f}, Clean={data['det_score_clean']:.4f}\n"
        f"Verdict: {verdict}  (threshold={args.nn_det_threshold})",
        fontsize=13, fontweight="bold",
        color="red" if detected else "green")

    # Top 2 rows: 4 attribute panels
    for idx in range(4):
        row, col = idx // 2, idx % 2
        ax = fig.add_subplot(gs[row, col])

        c_raw = data["clean_raw"][:, idx]
        a_raw = data["atk_raw"][:, idx]

        ax.plot(betas, c_raw, "o-", color="royalblue", linewidth=2, markersize=4, label="Clean")
        ax.plot(betas, a_raw, "s-", color="crimson", linewidth=2, markersize=4, label="Attacked")
        ax.fill_between(betas, c_raw, a_raw, alpha=0.20, color="gold")

        # Highlight top-25% divergence betas with red background
        div = np.abs(a_raw - c_raw)
        if div.max() > 0:
            threshold_div = np.percentile(div, 75)
            for i in range(len(betas)):
                if div[i] >= threshold_div:
                    lo = betas[max(0, i)] - 0.025
                    hi = betas[min(len(betas)-1, i)] + 0.025
                    ax.axvspan(lo, hi, alpha=0.12, color="red", zorder=1)

        ax.set_title(ATTR_LABELS[idx], fontsize=10)
        ax.set_xlabel("beta")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    # Bottom row: per-attribute divergence bar chart
    ax_bar = fig.add_subplot(gs[2, :])
    divergences = []
    for idx in range(4):
        c_raw = data["clean_raw"][:, idx]
        a_raw = data["atk_raw"][:, idx]
        mean_div = np.mean(np.abs(a_raw - c_raw))
        max_range = max(np.max(np.abs(a_raw)), np.max(np.abs(c_raw)), 1e-9)
        rel_div = mean_div / max_range * 100
        divergences.append(rel_div)

    max_div = max(divergences)
    colors = ["#e74c3c" if d == max_div else "#3498db" for d in divergences]
    bars = ax_bar.barh(ATTR_SHORT, divergences, color=colors, edgecolor="white", height=0.6)
    ax_bar.set_xlabel("Mean Relative Divergence (%)")
    ax_bar.set_title("Per-Attribute Discrimination Power  (red = strongest signal for AD)",
                     fontsize=10, fontweight="bold")
    for bar, val in zip(bars, divergences):
        ax_bar.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                    f"{val:.1f}%", va="center", fontsize=9, fontweight="bold")
    ax_bar.grid(True, alpha=0.3, axis="x")

    plt.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {outpath}")


# ─── Execute plots ───
print("\n=== Generating plots ===")

plot_mean_with_divergence(
    per_image_data,
    os.path.join(args.outdir, "figures", "mean_raw_attributes.png"))

plot_normalized_ad_input(
    per_image_data,
    os.path.join(args.outdir, "figures", "mean_normalized_ad_input.png"))

# 個別画像 (最大3枚)
for i, d in enumerate(per_image_data[:3]):
    plot_single_image(
        d,
        os.path.join(args.outdir, "figures", f"single_{d['image']}.png"))

# ─── Summary ───
print(f"\n=== Summary ===")
print(f"Images processed: {len(per_image_data)}")
print(f"CSV: {csv_path}")
print(f"Figures: {os.path.join(args.outdir, 'figures/')}")
det_atk = [d["det_score_atk"] for d in per_image_data]
det_cln = [d["det_score_clean"] for d in per_image_data]
print(f"AD Score (attacked): mean={np.mean(det_atk):.4f}, min={np.min(det_atk):.4f}, max={np.max(det_atk):.4f}")
print(f"AD Score (clean):    mean={np.mean(det_cln):.4f}, min={np.min(det_cln):.4f}, max={np.max(det_cln):.4f}")
