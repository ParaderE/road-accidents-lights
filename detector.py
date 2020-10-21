from sys import stdin
import json
import time

import cv2
import pandas as pd
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub


class Detector:

    def __init__(self, config, path_to_detector, lights_manager=None):
        lines = json.load("config.json")
        self.lines_functions = dict()
        for key, line in lines.items():
            x1, y1, x2, y2 = lines
            self.lines_functions[key] = lambda x: ((y1 - y2) * x + (x1 * y2 - x2 * y1)) / (x1 - x2)
        self.detector = hub.load(path_to_detector).signature['default']
        self.manager = lights_manager
        self.vehicles_on_prev_iteration = []
    
    def detect(self, image):
        objects = self.detector(image)
        objects = {key: val.numpy() for key, val in objects.items()}
        return objects
    
    def filter(self, boxes, classes, scores):
        """Filter all detected objects to be vehicles with score greater then 0.7"""
        m = np.concatenate((boxes, classes, scores), axis=1)
        df = pd.DataFrame(m, columns=['ymin', 'xmin', 'ymax', 'xmax', 'class', 'score'])
        return df.loc[
                      ((df['class'] == "vehicle") | (df['class'] == "truck") | (df['class'] == "car")) & (df['score'] >= 0.7),
                      ['ymin', 'xmin', 'ymax', 'xmax']
                    ]
    
    def compare_vehicle(self, a, b) -> bool:
        """Check if the cars are the same"""
        return (np.abs(a - b) < 10).all()
    
    def put_on_the_line(self, car) -> int:
        """Detect on which line car is located"""
        for i in self.lines_functions.keys():
            if abs(self.lines_functions[i](car[1]) - car[0]) < 10 and abs(self.lines_functions[i + 1](car[3]) - car[0]) < 10:
                return i
    
    def run(self, cap):
        """Detector iteration"""
        res, frame = cap.read(to_tensor=True)

        if not res:
            raise ValueError

        result = self.detect()

        boxes, classes, scores = result['detection_boxes'], result["detection_class_entities"], result["detection_scores"]
        detected_vehicles = self.filter(boxes, classes, scores)

        lines = []
        for vehicle in detected_vehicles:
            line = self.put_on_the_line(vehicle)
            for prev_line, prev_vehicle in self.vehicles_on_prev_iteration:
                if prev_line == line:
                    if self.compare_vehicle(vehicle, prev_vehicle):
                        lines.append(line)
                        if self.manager:
                            self.manager.turn_on(line)
        
        self.vehicles_on_prev_iteration = [(self.put_on_the_line(vehicle), vehicle) for vehicle in detected_vehicles]
        return lines
