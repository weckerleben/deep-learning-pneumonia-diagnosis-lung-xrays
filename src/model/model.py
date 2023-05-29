import sys
from fastai.vision.all import *


def train_model(path):
    # Load data
    data = ImageDataLoaders.from_folder(path, train='train', valid='val', item_tfms=Resize(460),
                                        batch_tfms=aug_transforms(size=224, min_scale=0.75), batch_size=16)

    # Print dataset sizes
    print(len(data.train_ds), len(data.valid_ds))

    # Load pre-trained ResNet50 model
    learn = cnn_learner(data, resnet50, metrics=[accuracy, error_rate, Precision(), Recall(), F1Score()])

    # Save training output to a file
    with open('train_output.txt', 'w') as f:
        sys.stdout = f
        learn.fine_tune(10) # Train the model
        sys.stdout = sys.__stdout__  # Restore standard output

    # Save the model
    learn.export('model.pkl')
