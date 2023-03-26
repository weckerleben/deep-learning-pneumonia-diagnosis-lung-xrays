from fastai.vision.all import *
from config import PATH

path = Path(PATH)
train_path = path/'train'
valid_path = path/'val'

pneumonia_types = ['normal', 'viral', 'bacterial']

def get_xray_type(x):
    for t in pneumonia_types:
        if t in x.name:
            return t
    return 'unknown'

dblock = DataBlock(
    blocks=(ImageBlock, CategoryBlock),
    get_items=get_image_files,
    splitter=RandomSplitter(valid_pct=0.2, seed=42),
    get_y=Pipeline([parent_label, get_xray_type]),
    item_tfms=[Resize(460)],
    batch_tfms=[*aug_transforms(size=224, max_warp=0), Normalize.from_stats(*imagenet_stats)]
)