"""
Grad-CAM Visualization for YOLOv2

モデルが画像のどこに注目しているかを可視化する。
Clean/Attacked/Recovered画像のAttentionを比較し、
パッチが検出を妨害するメカニズムを分析する。
"""

import torch
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import cv2
import os
import argparse
from PIL import Image

# Add parent directory to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from darknet import Darknet


class GradCAM:
    """
    Grad-CAM implementation for Darknet/YOLOv2.

    Grad-CAM generates a heatmap showing which regions of the image
    are most important for the model's prediction.
    """

    def __init__(self, model, target_layer_idx=13):
        """
        Args:
            model: Darknet model
            target_layer_idx: Layer index for CAM extraction (default: 13 = 26x26)
        """
        self.model = model
        self.target_layer_idx = target_layer_idx
        self.gradients = None
        self.activations = None

        # Register hooks
        self._register_hooks()

    def _register_hooks(self):
        """Register forward and backward hooks on target layer."""

        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()

        # Get the target layer
        target_layer = self.model.models[self.target_layer_idx]

        # Register hooks
        target_layer.register_forward_hook(forward_hook)
        target_layer.register_full_backward_hook(backward_hook)

    def generate_cam(self, input_tensor, target_class=None):
        """
        Generate Grad-CAM heatmap.

        Args:
            input_tensor: Input image tensor [1, 3, H, W]
            target_class: Target class index (None = use max confidence)

        Returns:
            cam: Grad-CAM heatmap [H, W]
            detection_score: Detection confidence score
        """
        self.model.eval()

        # Forward pass
        input_tensor.requires_grad_(True)
        output = self.model(input_tensor)

        # Handle tuple output (some models return (output, feature_maps))
        if isinstance(output, tuple):
            output = output[0]

        # For YOLOv2, output shape is [batch, channels, H, W]
        # channels = anchors * (5 + num_classes)
        # e.g., [1, 425, 13, 13] for COCO (5 anchors * 85) or [1, 125, 13, 13] for VOC (5 anchors * 25)
        if isinstance(output, torch.Tensor) and output.dim() == 4:
            batch, channels, h, w = output.shape
            num_anchors = 5

            # Determine num_classes from channels
            num_params_per_anchor = channels // num_anchors  # 85 for COCO, 25 for VOC
            num_classes = num_params_per_anchor - 5

            # Reshape to [batch, anchors, params, H, W]
            output_reshaped = output.view(batch, num_anchors, num_params_per_anchor, h, w)

            # Extract objectness scores (index 4 for each anchor)
            # objectness is at index 4 in each anchor's predictions
            objectness = torch.sigmoid(output_reshaped[:, :, 4, :, :])  # [batch, anchors, H, W]

            # Take max over anchors
            max_objectness, _ = objectness.max(dim=1)  # [batch, H, W]

            # Use sum of objectness as target for gradient
            target = max_objectness.sum()
            detection_score = max_objectness.max().item()
        else:
            # Fallback
            try:
                target = output.sum() if isinstance(output, torch.Tensor) else torch.tensor(0.0, requires_grad=True)
                detection_score = 0.0
            except:
                target = torch.tensor(0.0, requires_grad=True)
                detection_score = 0.0

        # Backward pass
        self.model.zero_grad()
        target.backward()

        # Get gradients and activations
        gradients = self.gradients  # [1, C, H, W]
        activations = self.activations  # [1, C, H, W]

        # Global average pooling of gradients
        weights = gradients.mean(dim=(2, 3), keepdim=True)  # [1, C, 1, 1]

        # Weighted combination of activation maps
        cam = (weights * activations).sum(dim=1, keepdim=True)  # [1, 1, H, W]

        # ReLU and normalize
        cam = F.relu(cam)
        cam = cam.squeeze().cpu().numpy()

        # Normalize to [0, 1]
        if cam.max() > 0:
            cam = (cam - cam.min()) / (cam.max() - cam.min())

        return cam, detection_score


def load_image(image_path, size=416):
    """Load and preprocess image."""
    img = Image.open(image_path).convert('RGB')
    img = img.resize((size, size))
    img_np = np.array(img) / 255.0
    img_tensor = torch.from_numpy(img_np.transpose(2, 0, 1)).float().unsqueeze(0)
    return img_tensor, img_np


def overlay_cam(image, cam, alpha=0.5):
    """Overlay CAM heatmap on image."""
    # Resize CAM to image size
    cam_resized = cv2.resize(cam, (image.shape[1], image.shape[0]))

    # Apply colormap
    heatmap = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB) / 255.0

    # Overlay
    overlayed = alpha * heatmap + (1 - alpha) * image
    overlayed = np.clip(overlayed, 0, 1)

    return overlayed, cam_resized


def visualize_comparison(clean_path, attacked_path, recovered_path, output_path,
                         model, gradcam, device):
    """
    Create comparison visualization of Grad-CAM for Clean/Attacked/Recovered.
    """
    # Load images
    clean_tensor, clean_np = load_image(clean_path)
    attacked_tensor, attacked_np = load_image(attacked_path)

    # For recovered, we need to run the recovery process
    # For now, use attacked as placeholder if recovered doesn't exist
    if recovered_path and os.path.exists(recovered_path):
        recovered_tensor, recovered_np = load_image(recovered_path)
    else:
        recovered_tensor, recovered_np = attacked_tensor.clone(), attacked_np.copy()

    # Move to device
    clean_tensor = clean_tensor.to(device)
    attacked_tensor = attacked_tensor.to(device)
    recovered_tensor = recovered_tensor.to(device)

    # Generate Grad-CAMs
    clean_cam, clean_score = gradcam.generate_cam(clean_tensor)
    attacked_cam, attacked_score = gradcam.generate_cam(attacked_tensor)
    recovered_cam, recovered_score = gradcam.generate_cam(recovered_tensor)

    # Create overlays
    clean_overlay, clean_cam_resized = overlay_cam(clean_np, clean_cam)
    attacked_overlay, attacked_cam_resized = overlay_cam(attacked_np, attacked_cam)
    recovered_overlay, recovered_cam_resized = overlay_cam(recovered_np, recovered_cam)

    # Create figure
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    # Row 1: Original images
    axes[0, 0].imshow(clean_np)
    axes[0, 0].set_title(f'Clean\n(det_score: {clean_score:.3f})', fontsize=12)
    axes[0, 0].axis('off')

    axes[0, 1].imshow(attacked_np)
    axes[0, 1].set_title(f'Attacked\n(det_score: {attacked_score:.3f})', fontsize=12)
    axes[0, 1].axis('off')

    axes[0, 2].imshow(recovered_np)
    axes[0, 2].set_title(f'Recovered\n(det_score: {recovered_score:.3f})', fontsize=12)
    axes[0, 2].axis('off')

    # Row 2: Grad-CAM overlays
    axes[1, 0].imshow(clean_overlay)
    axes[1, 0].set_title('Clean Attention', fontsize=12)
    axes[1, 0].axis('off')

    axes[1, 1].imshow(attacked_overlay)
    axes[1, 1].set_title('Attacked Attention', fontsize=12)
    axes[1, 1].axis('off')

    axes[1, 2].imshow(recovered_overlay)
    axes[1, 2].set_title('Recovered Attention', fontsize=12)
    axes[1, 2].axis('off')

    plt.tight_layout()

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f'Saved: {output_path}')

    return {
        'clean_score': clean_score,
        'attacked_score': attacked_score,
        'recovered_score': recovered_score,
        'clean_cam': clean_cam_resized,
        'attacked_cam': attacked_cam_resized,
        'recovered_cam': recovered_cam_resized
    }


def main():
    parser = argparse.ArgumentParser(description='Grad-CAM visualization for YOLOv2')
    parser.add_argument('--clean_dir', type=str, required=True,
                        help='Directory containing clean images')
    parser.add_argument('--attacked_dir', type=str, required=True,
                        help='Directory containing attacked images')
    parser.add_argument('--recovered_dir', type=str, default=None,
                        help='Directory containing recovered images (optional)')
    parser.add_argument('--output_dir', type=str, default='experiments/exp_20260202_visual_recovery/gradcam',
                        help='Output directory for visualizations')
    parser.add_argument('--cfgfile', type=str, default='cfg/yolo.cfg',
                        help='YOLO config file')
    parser.add_argument('--weightfile', type=str, default='weights/yolo.weights',
                        help='YOLO weights file')
    parser.add_argument('--target_layer', type=int, default=13,
                        help='Target layer for Grad-CAM (default: 13)')
    parser.add_argument('--num_images', type=int, default=5,
                        help='Number of images to process')
    parser.add_argument('--cuda', action='store_true',
                        help='Use CUDA if available')

    args = parser.parse_args()

    # Device
    device = torch.device('cuda' if args.cuda and torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')

    # Load model
    print('Loading YOLOv2 model...')
    model = Darknet(args.cfgfile)
    model.load_weights(args.weightfile)
    model.to(device)
    model.eval()

    # Create Grad-CAM
    gradcam = GradCAM(model, target_layer_idx=args.target_layer)

    # Get image list
    clean_images = sorted([f for f in os.listdir(args.clean_dir)
                          if f.endswith(('.png', '.jpg', '.jpeg'))])[:args.num_images]

    print(f'Processing {len(clean_images)} images...')

    # Process each image
    results = []
    for i, img_name in enumerate(clean_images):
        clean_path = os.path.join(args.clean_dir, img_name)
        attacked_path = os.path.join(args.attacked_dir, img_name)

        if not os.path.exists(attacked_path):
            print(f'Skipping {img_name}: attacked version not found')
            continue

        recovered_path = None
        if args.recovered_dir:
            recovered_path = os.path.join(args.recovered_dir, img_name)

        output_path = os.path.join(args.output_dir, f'gradcam_{img_name}')

        try:
            result = visualize_comparison(
                clean_path, attacked_path, recovered_path,
                output_path, model, gradcam, device
            )
            result['image_name'] = img_name
            results.append(result)
        except Exception as e:
            print(f'Error processing {img_name}: {e}')
            continue

    # Summary
    print('\n' + '='*50)
    print('Summary of Detection Scores')
    print('='*50)
    print(f'{"Image":<20} {"Clean":>10} {"Attacked":>10} {"Recovered":>10}')
    print('-'*50)
    for r in results:
        print(f'{r["image_name"]:<20} {r["clean_score"]:>10.3f} {r["attacked_score"]:>10.3f} {r["recovered_score"]:>10.3f}')

    print(f'\nVisualizations saved to: {args.output_dir}')


if __name__ == '__main__':
    main()
