from fastai.vision.all import *
import matplotlib.pyplot as plt

from config import PATH


def train_model(path):
    # Load data
    data = ImageDataLoaders.from_folder(path, train='train', valid='val', item_tfms=Resize(460),
                                        batch_tfms=aug_transforms(size=224, min_scale=0.75), batch_size=16)

    # Print dataset sizes
    print(len(data.train_ds), len(data.valid_ds))

    # Load pre-trained ResNet50 model
    learn = cnn_learner(data, resnet50, metrics=error_rate)

    # Add ShowGraphCallback
    learn.add_cb(ShowGraphCallback())
    learn.recorder.live = True

    # Train the model
    learn.fine_tune(4)

    # Save the model
    learn.export('model.pkl')


if __name__ == '__main__':
    train_model(PATH)
