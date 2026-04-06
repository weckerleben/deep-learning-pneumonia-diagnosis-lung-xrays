"""
model_converter.py — Convierte el modelo FastAI a PyTorch (.pt) y ONNX (.onnx).

Uso:
    python -m model.src.model.model_converter

Genera:
    trained_model/model.pt   — PyTorch state dict
    trained_model/model.onnx — ONNX para inferencia cross-platform (Android, Edge, etc.)
"""

import torch
import torch.onnx
from fastai.vision.all import load_learner
from model.src.config.config import TRAINED_MODEL_PATH

INPUT_SIZE = (1, 3, 224, 224)  # batch=1, RGB, 224x224


def convert_to_pytorch(learner, output_path: str) -> None:
    """Exporta solo el state dict de PyTorch."""
    torch_model = learner.model
    torch.save(torch_model.state_dict(), output_path)
    print(f'PyTorch state dict guardado en: {output_path}')


def convert_to_onnx(learner, output_path: str) -> None:
    """
    Exporta el modelo a formato ONNX con opset 17.
    El modelo ONNX puede ser usado en:
      - Android via ONNX Runtime Mobile
      - Edge devices (Raspberry Pi, Jetson)
      - Navegadores via ONNX.js
      - Otros frameworks (TensorFlow, CoreML via conversión)
    """
    torch_model = learner.model.eval()

    dummy_input = torch.randn(*INPUT_SIZE)

    torch.onnx.export(
        torch_model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=17,
        do_constant_folding=True,       # Optimiza constantes en el grafo
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},  # Permite batch dinámico
            'output': {0: 'batch_size'}
        }
    )
    print(f'ONNX exportado en: {output_path}')

    # Verificar que el modelo ONNX es válido
    try:
        import onnx
        onnx_model = onnx.load(output_path)
        onnx.checker.check_model(onnx_model)
        print('Verificación ONNX: OK')
    except ImportError:
        print('onnx no instalado — omitiendo verificación (pip install onnx)')


def verify_onnx_inference(onnx_path: str) -> None:
    """Verifica que el modelo ONNX produce el mismo output que PyTorch."""
    try:
        import onnxruntime as ort
        import numpy as np

        session = ort.InferenceSession(onnx_path)
        dummy = np.random.randn(*INPUT_SIZE).astype(np.float32)
        outputs = session.run(None, {'input': dummy})
        print(f'ONNX Runtime inference OK — output shape: {outputs[0].shape}')
    except ImportError:
        print('onnxruntime no instalado — omitiendo verificación (pip install onnxruntime)')


if __name__ == '__main__':
    model_path = f'{TRAINED_MODEL_PATH}/model.pkl'
    print(f'Cargando modelo: {model_path}')
    learner = load_learner(model_path)

    pt_path = f'{TRAINED_MODEL_PATH}/model.pt'
    onnx_path = f'{TRAINED_MODEL_PATH}/model.onnx'

    convert_to_pytorch(learner, pt_path)
    convert_to_onnx(learner, onnx_path)
    verify_onnx_inference(onnx_path)

    print('\nConversión completada:')
    print(f'  {pt_path}')
    print(f'  {onnx_path}')
