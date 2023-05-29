import torch.onnx as onnx
from fastai.vision.all import *
from config import PATH

# Load the trained model
model_path = PATH + "/model.pkl"
model = load_learner(model_path)

# Export the model to ONNX format
dummy_input = torch.randn(1, 3, 224, 224)  # Input example
onnx_path = PATH + "/model.onnx"
onnx.export(model.model, dummy_input, onnx_path)
