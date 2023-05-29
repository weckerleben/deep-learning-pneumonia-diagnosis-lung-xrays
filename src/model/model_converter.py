import torch
from fastai.vision.all import load_learner
from src.config.config import TRAINED_MODEL_PATH

# Load the trained model
model_path = TRAINED_MODEL_PATH + "/model.pkl"
model = load_learner(model_path)

torch_model = model.model

torch_model_path = TRAINED_MODEL_PATH + '/model.pt'
torch.save(torch_model.state_dict(), torch_model_path)