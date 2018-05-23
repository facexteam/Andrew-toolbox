refinedet_config={
    "modelParam":{
        "weight": "/workspace/data/BK/process-mp4/models/ResNet/coco/refinedet_resnet101_512x512/coco_refinedet_resnet101_512x512_final.caffemodel",
        "deploy": "/workspace/data/BK/process-mp4/models/ResNet/coco/refinedet_resnet101_512x512/deploy.prototxt",
        "label": "/workspace/data/BK/process-mp4/models/ResNet/coco/refinedet_resnet101_512x512/coco_label.csv",
        "batch_size":1
    },
    "gpuId":0, # default 0
    'image_size':512,
    'need_label_dict': {
        1: 'person',
        3: 'car',
        4: 'motorbike',
        6: 'bus',
        8: 'truck',
        16: 'cat',
        17:'dog'
    },
    'need_label_thresholds': {
        1: 0.4,
        3: 0.4,
        4: 0.4,
        6: 0.4,
        8: 0.4,
        16:0.4,
        17:0.4

    }
}
face_detect_config={
    "modelParam": {
        "weight": "/workspace/data/BK/process-mp4/face-rd-18-t0/model/model.caffemodel",
        "deploy": "/workspace/data/BK/process-mp4/face-rd-18-t0/model/deploy.prototxt",
        "label": "/workspace/data/BK/process-mp4/face-rd-18-t0/model/labels.csv",
        "batch_size": 1
    },
    "gpuId": 1,  # not use , because caffe.set_mode_gpu()  and caffe.set_device() is global
    'image_size': 512,
    'need_label_dict': {
        1: 'face'
    },
    'need_label_thresholds': {
        1: 0.6
    }
}
