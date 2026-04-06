"""
gradcam.py — Visualización de Grad-CAM para explicabilidad del modelo.

Grad-CAM resalta las regiones de la radiografía que activaron la predicción,
lo cual es esencial en diagnóstico médico para validar que el modelo "mira"
las zonas correctas (pulmones) y no artefactos irrelevantes.

Uso:
    python gradcam.py --model trained_model/model.pkl --image path/a/rx.jpg
    python gradcam.py --model trained_model/model.pkl --folder chest_xray/test/NORMAL --n 6

Genera:
    - gradcam_output/<nombre_imagen>_gradcam.png
"""

import argparse
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import torch
import torch.nn.functional as F
from fastai.vision.all import load_learner, PILImage


class GradCAM:
    """
    Implementación de Gradient-weighted Class Activation Mapping (Grad-CAM).
    Referencia: Selvaraju et al. (2017) — https://arxiv.org/abs/1610.02391
    """

    def __init__(self, learner):
        self.learn = learner
        self.model = learner.model.eval()
        self.gradients = None
        self.activations = None
        self._register_hooks()

    def _register_hooks(self):
        """Registra hooks en la última capa convolucional de ResNet50 (layer4)."""
        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()

        # Última capa convolucional de ResNet50
        target_layer = self.model[0][-1][-1]
        target_layer.register_forward_hook(forward_hook)
        target_layer.register_full_backward_hook(backward_hook)

    def generate(self, img_path: str):
        """
        Genera el mapa Grad-CAM para una imagen dada.

        Returns:
            pred_class (str): clase predicha
            prob (float): probabilidad de la clase predicha
            heatmap (np.ndarray): mapa de calor normalizado [0, 1]
            original_img (PIL.Image): imagen original
        """
        img = PILImage.create(img_path)
        pred_class, pred_idx, probs = self.learn.predict(img)
        prob = float(probs.max())

        # Forward pass con gradientes habilitados
        self.model.zero_grad()
        x = self.learn.dls.test_dl([img_path]).one_batch()[0]
        output = self.model(x)
        score = output[0, pred_idx]
        score.backward()

        # Grad-CAM: promedio de gradientes por canal → pesos de activación
        weights = self.gradients.mean(dim=[2, 3], keepdim=True)
        cam = (weights * self.activations).sum(dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = cam.squeeze().cpu().numpy()

        # Normalizar entre 0 y 1
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)

        return str(pred_class), prob, cam, img

    def visualize(self, img_path: str, output_dir: str = 'gradcam_output') -> str:
        """Genera y guarda la visualización Grad-CAM superpuesta a la imagen."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        pred_class, prob, heatmap, original_img = self.generate(img_path)

        # Redimensionar heatmap al tamaño original
        import cv2
        w, h = original_img.size
        heatmap_resized = cv2.resize(heatmap, (w, h))
        heatmap_colored = cv2.applyColorMap(
            (heatmap_resized * 255).astype(np.uint8), cv2.COLORMAP_JET
        )
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

        # Superponer con la imagen original
        original_np = np.array(original_img.convert('RGB'))
        superimposed = cv2.addWeighted(original_np, 0.6, heatmap_colored, 0.4, 0)

        # Plot
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        axes[0].imshow(original_np, cmap='gray' if original_np.ndim == 2 else None)
        axes[0].set_title('Original')
        axes[0].axis('off')

        axes[1].imshow(heatmap_resized, cmap='jet')
        axes[1].set_title('Grad-CAM Heatmap')
        axes[1].axis('off')

        axes[2].imshow(superimposed)
        axes[2].set_title(f'Overlay\n{pred_class} ({prob:.1%})')
        axes[2].axis('off')

        plt.suptitle(f'Grad-CAM — {Path(img_path).name}', fontsize=13, fontweight='bold')
        plt.tight_layout()

        out_name = Path(img_path).stem + '_gradcam.png'
        out_path = Path(output_dir) / out_name
        plt.savefig(out_path, dpi=120, bbox_inches='tight')
        plt.close()

        print(f'[{pred_class} {prob:.1%}] → {out_path}')
        return str(out_path)


def main():
    parser = argparse.ArgumentParser(description='Grad-CAM para NeumoScan')
    parser.add_argument('--model', default='trained_model/model.pkl',
                        help='Ruta al modelo .pkl exportado')
    parser.add_argument('--image', default=None,
                        help='Ruta a una imagen individual')
    parser.add_argument('--folder', default=None,
                        help='Carpeta con imágenes a procesar')
    parser.add_argument('--n', type=int, default=5,
                        help='Número de imágenes del folder a procesar')
    parser.add_argument('--output', default='gradcam_output',
                        help='Carpeta de salida para las visualizaciones')
    args = parser.parse_args()

    print(f'Cargando modelo: {args.model}')
    learn = load_learner(args.model)
    gcam = GradCAM(learn)

    if args.image:
        gcam.visualize(args.image, args.output)

    elif args.folder:
        from fastai.vision.all import get_image_files
        images = get_image_files(args.folder)[:args.n]
        print(f'Procesando {len(images)} imágenes de {args.folder}')
        for img_path in images:
            gcam.visualize(str(img_path), args.output)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
