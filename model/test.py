"""
test.py — Evaluación formal del modelo en el test set.

Uso:
    python test.py --model trained_model/model.pkl --test-path chest_xray/test

Genera:
    - Confusion matrix (imagen PNG)
    - Classification report por clase (consola + test_results.txt)
    - Top losses (imágenes peor clasificadas)
"""

import argparse
from pathlib import Path

from fastai.vision.all import (
    load_learner, get_image_files, ImageDataLoaders, Resize,
    ClassificationInterpretation
)


def evaluate(model_path: str, test_path: str, output_dir: str = '.') -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    print(f'Cargando modelo: {model_path}')
    learn = load_learner(model_path)

    print(f'Cargando test set: {test_path}')
    test_files = get_image_files(test_path)
    print(f'  → {len(test_files)} imágenes encontradas')

    # DataLoader de test (sin labels — FastAI infiere del nombre de carpeta)
    test_dl = learn.dls.test_dl(test_files)
    preds, _ = learn.get_preds(dl=test_dl)

    # Reconstruir con labels reales para interpretación
    # Se usa from_folder para tener los labels correctos del test set
    test_data = ImageDataLoaders.from_folder(
        Path(test_path).parent,
        train='train',
        valid='test',
        item_tfms=Resize(224),
        batch_size=32
    )
    learn.dls = test_data

    interp = ClassificationInterpretation.from_learner(learn, ds_idx=1)

    # ── Confusion Matrix ───────────────────────────────────────────────────────
    print('\n=== Confusion Matrix ===')
    interp.plot_confusion_matrix(figsize=(8, 8), dpi=100)

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.savefig(output / 'confusion_matrix.png', bbox_inches='tight')
    plt.close()
    print(f'  → Guardada en {output}/confusion_matrix.png')

    # ── Classification Report ──────────────────────────────────────────────────
    from sklearn.metrics import classification_report
    import torch

    pred_classes = preds.argmax(dim=1).numpy()

    # Obtener labels reales del valid set (test set)
    true_labels = [learn.dls.valid_ds.items[i].parent.name for i in range(len(learn.dls.valid_ds))]
    true_indices = [learn.dls.vocab.o2i[lbl] for lbl in true_labels]

    report = classification_report(
        true_indices[:len(pred_classes)],
        pred_classes,
        target_names=learn.dls.vocab,
        digits=4
    )

    print('\n=== Classification Report ===')
    print(report)

    results_path = output / 'test_results.txt'
    with open(results_path, 'w') as f:
        f.write('=== NeumoScan — Test Set Evaluation ===\n\n')
        f.write(f'Model: {model_path}\n')
        f.write(f'Test set: {test_path}\n')
        f.write(f'Images: {len(test_files)}\n\n')
        f.write('=== Confusion Matrix ===\n')
        f.write('Ver confusion_matrix.png\n\n')
        f.write('=== Classification Report ===\n')
        f.write(report)
    print(f'\nResultados guardados en {results_path}')

    # ── Top Losses (peores predicciones) ──────────────────────────────────────
    print('\n=== Top Losses (9 peores predicciones) ===')
    interp.plot_top_losses(9, nrows=3, figsize=(12, 12))
    plt.savefig(output / 'top_losses.png', bbox_inches='tight')
    plt.close()
    print(f'  → Guardada en {output}/top_losses.png')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluación formal del modelo NeumoScan')
    parser.add_argument('--model', default='trained_model/model.pkl',
                        help='Ruta al modelo .pkl exportado')
    parser.add_argument('--test-path', default='chest_xray/test',
                        help='Directorio del test set (con subcarpetas por clase)')
    parser.add_argument('--output', default='.',
                        help='Directorio donde guardar los resultados')
    args = parser.parse_args()

    evaluate(args.model, args.test_path, args.output)
