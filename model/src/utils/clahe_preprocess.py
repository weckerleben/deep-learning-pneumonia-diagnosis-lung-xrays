"""
clahe_preprocess.py — Mejora de contraste en radiografías con CLAHE.

CLAHE (Contrast Limited Adaptive Histogram Equalization) mejora la visibilidad
de estructuras pulmonares en radiografías, especialmente útil cuando las
imágenes tienen bajo contraste o exposición irregular.

Uso como script:
    python clahe_preprocess.py --input chest_xray/train --output chest_xray_clahe/train

Uso como función en la API o en training:
    from src.utils.clahe_preprocess import apply_clahe
    enhanced = apply_clahe('path/to/rx.jpg')
"""

import argparse
from pathlib import Path

import cv2
import numpy as np


def apply_clahe(image_path: str, clip_limit: float = 2.0, tile_size: int = 8) -> np.ndarray:
    """
    Aplica CLAHE a una radiografía y devuelve la imagen mejorada como array RGB.

    Args:
        image_path: Ruta a la imagen de entrada
        clip_limit: Límite de contraste (2.0 es un buen balance)
        tile_size: Tamaño de la grilla de tiles (8x8 es estándar para RX)

    Returns:
        np.ndarray: imagen RGB mejorada con CLAHE
    """
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f'No se pudo leer la imagen: {image_path}')

    # Convertir a escala de grises para aplicar CLAHE
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
    enhanced_gray = clahe.apply(gray)

    # Convertir de vuelta a RGB (3 canales idénticos) para compatibilidad con ResNet
    enhanced_rgb = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2RGB)
    return enhanced_rgb


def preprocess_dataset(input_dir: str, output_dir: str,
                        clip_limit: float = 2.0, tile_size: int = 8) -> None:
    """
    Aplica CLAHE a todas las imágenes de un dataset manteniendo la estructura de carpetas.

    Args:
        input_dir: Directorio raíz del dataset (ej: chest_xray/train)
        output_dir: Directorio de salida (ej: chest_xray_clahe/train)
        clip_limit: Límite de contraste para CLAHE
        tile_size: Tamaño de tiles para CLAHE
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    supported = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}

    image_files = [p for p in input_path.rglob('*') if p.suffix.lower() in supported]
    print(f'Procesando {len(image_files)} imágenes con CLAHE...')

    processed, skipped = 0, 0
    for img_path in image_files:
        # Mantener estructura de subcarpetas (clases)
        relative = img_path.relative_to(input_path)
        out_path = output_path / relative
        out_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            enhanced = apply_clahe(str(img_path), clip_limit, tile_size)
            cv2.imwrite(str(out_path), cv2.cvtColor(enhanced, cv2.COLOR_RGB2BGR))
            processed += 1
        except Exception as e:
            print(f'  [SKIP] {img_path.name}: {e}')
            skipped += 1

    print(f'Completado: {processed} procesadas, {skipped} omitidas.')
    print(f'Dataset CLAHE guardado en: {output_path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CLAHE preprocessing para radiografías')
    parser.add_argument('--input', required=True, help='Directorio de entrada del dataset')
    parser.add_argument('--output', required=True, help='Directorio de salida')
    parser.add_argument('--clip-limit', type=float, default=2.0,
                        help='Clip limit para CLAHE (default: 2.0)')
    parser.add_argument('--tile-size', type=int, default=8,
                        help='Tamaño de tiles (default: 8)')
    args = parser.parse_args()

    preprocess_dataset(args.input, args.output, args.clip_limit, args.tile_size)
