import contextlib
import torch
from fastai.vision.all import (
    ImageDataLoaders, Resize, aug_transforms,
    cnn_learner, resnet50, accuracy, error_rate,
    Precision, Recall, F1Score, CrossEntropyLossFlat
)


def get_class_weights(dls):
    """Calcula pesos inversamente proporcionales a la frecuencia de cada clase."""
    from collections import Counter
    import torch

    labels = [dls.vocab[label] for label in dls.train_ds.items]
    counts = Counter(labels)
    total = sum(counts.values())
    weights = [total / counts[cls] for cls in dls.vocab]
    return torch.tensor(weights, dtype=torch.float)


def train_model(path):
    # Cargar datos
    data = ImageDataLoaders.from_folder(
        path,
        train='train',
        valid='val',
        item_tfms=Resize(460),
        batch_tfms=aug_transforms(size=224, min_scale=0.75),
        batch_size=16
    )

    print(f'Train: {len(data.train_ds)} imágenes | Valid: {len(data.valid_ds)} imágenes')
    print(f'Clases: {data.vocab}')

    # Calcular class weights para manejar desbalance
    class_weights = get_class_weights(data)
    loss_func = CrossEntropyLossFlat(weight=class_weights)

    # Cargar ResNet50 preentrenado con class weights en la loss
    learn = cnn_learner(
        data,
        resnet50,
        metrics=[accuracy, error_rate, Precision(), Recall(), F1Score()],
        loss_func=loss_func
    )

    # Learning Rate Finder — descomentar para buscar el LR óptimo manualmente
    # learn.lr_find()

    # Fase 1: entrenar solo las capas nuevas (head) con el backbone congelado
    learn.freeze()
    learn.fit_one_cycle(3, lr_max=1e-3)

    # Fase 2: descongelar todo y fine-tune con LR diferenciado
    learn.unfreeze()
    learn.fit_one_cycle(7, lr_max=slice(1e-5, 1e-4))

    # Guardar output de entrenamiento de forma segura
    with open('train_output.txt', 'w') as f:
        with contextlib.redirect_stdout(f):
            learn.show_results()

    # Exportar el modelo
    learn.export('model.pkl')
    print('Modelo exportado correctamente.')
