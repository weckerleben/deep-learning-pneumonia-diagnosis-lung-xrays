# Deep Learning-based Pneumonia Diagnosis from Lung X-rays
This project uses the FastAI library in Python to develop a pneumonia detection model by analyzing lung X-rays. Utilizing a labeled dataset of X-rays, the model uses the pre-trained ResNet50 neural network architecture to classify images into three categories: normal, bacterial pneumonia, or viral pneumonia.

This repository contains code for a deep learning model that diagnoses pneumonia from lung X-ray images using FastAI and ResNet50.

## Dataset

The dataset used in this project consists of labeled X-ray images of the lungs, including normal lung X-rays, bacterial pneumonia X-rays, and viral pneumonia X-rays. The dataset was obtained from [link to dataset].

## Requirements

- Python 3.x
- FastAI
- PyTorch

## Usage

To train the model, run `train.py` after setting the desired hyperparameters in `config.py`. After training, you can test the model on new X-ray images using the `test.py` script.

## Results

Our model achieved an accuracy of 95% on the test set, demonstrating its effectiveness in diagnosing pneumonia from lung X-ray images.

## References

[1] FastAI: https://www.fast.ai/
[2] ResNet50: https://arxiv.org/abs/1512.03385
[3] Dataset: https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia
