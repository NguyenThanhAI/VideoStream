import sys
import os
import numpy as np
import mrcnn.config
import mrcnn.utils
from mrcnn.model import MaskRCNN

class MaskRCNNConfig(mrcnn.config.Config):
    NAME = "coco_pretrained_model_config"
    IMAGES_PER_GPU = 1
    GPU_COUNT = 1
    NUM_CLASSES = 1 + 80
    DETECTION_MIN_CONFIDENCE = 0.0

ROOT_DIR = os.path.abspath("../")
sys.path.append(ROOT_DIR)


class Detector(object):
    def __init__(self, checkpoint_name="mask_rcnn_cars_and_vehicles_0008.h5", detection_vehicle_thresh=0.4):
        PRETRAINED_DIR = ROOT_DIR

        PRETRAINED_PATH = os.path.join(PRETRAINED_DIR, checkpoint_name)

        LOG_DIR = os.path.join(PRETRAINED_DIR, "logs")

        self.model = MaskRCNN(mode="inference", config=MaskRCNNConfig(), model_dir=LOG_DIR)

        self.model.load_weights(filepath=PRETRAINED_PATH, by_name=True)

        self.detection_vehicle_thresh = detection_vehicle_thresh

    def __call__(self, frame):

        rgb_frame = frame[:, :, ::-1]

        results = self.model.detect([rgb_frame], verbose=0)

        result = results[0]

        rois, scores, class_ids, masks = result["rois"], result["scores"], result["class_ids"], result["masks"]

        masks = np.transpose(masks, axes=(2, 0, 1))

        detections_list = []

        for det_id, (roi, score, class_id, mask) in enumerate(zip(rois, scores, class_ids, masks)):
            if score >= self.detection_vehicle_thresh and class_id in [3, 8, 6]:
                detections_list.append()
