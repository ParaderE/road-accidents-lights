import json

import cv2
import tensorflow as tf
import tensorflow_hub as hub


def process_image(image):
    """Process cv2 image to tensorflow tensor to pass it to detector"""
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.GaussianBlur(image, (5,5), 0)
    tensor_image = tf.convert_to_tensor(image, dtype=tf.float32)
    tensor_image = tf.expand_dims(tensor_image, axis=0)
    return tensor_image


def detect_cars(detector, image):
    objects = detector(image)
    objects = {key: val.numpy() for key, val in objects.items()}
    return objects


print("type \"q\" to stop program")

lines = json.load("config.json")
lines_functions = dict()
for key, line in lines.items():
    x1, y1, x2, y2 = lines
    lines_functions[key] = lambda x: ((y1 - y2) * x + (x1 * y2 - x2 * y1)) / (x1 - x2)

module_handle = "https://tfhub.dev/google/faster_rcnn/openimages_v4/inception_resnet_v2/1"
detector = hub.load(module_handle).signatures['default']

cap = cv2.VideoCapture(0)

while -15:
    res, frame = cap.read()

    if not res:
        print("Error while getting new frame")
        break

    tensor = process_image(frame)
    result = detect_cars()

    boxes, classes, scores = result['detection_boxes'], result["detection_class_entities"], result["detection_scores"]
    for i in range(boxes.shape[0]):


cap.release()
cv2.destroyAllWindows()