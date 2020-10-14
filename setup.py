import os
import time
import json
import logging
from itertools import groupby
logging.basicConfig(level=logging.INFO)
try:
    from tqdm import tqdm
except ImportError as e:
    logging.warning(e)
    a = input("Install tqdm: [y/N] ")
    if a.startswith("y"):
        os.system("pip install --user tqdm")
        from tqdm import tqdm
    else:
        logging.info("Progress bars disabled")
        tqdm = lambda x: x

try:
    import cv2
    import numpy as np
    from sklearn.cluster import DBSCAN
except ImportError as e:
    logging.error(e)
    exit(1)
logging.info("Imports: Complete")

cap = cv2.VideoCapture(0)
logging.info("Image shooting: Running")
images = list()
for i in tqdm(range(100)):
    _, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    images.append(frame)
    time.sleep(1)
cap.release()
logging.info("Image shooting: Complete")

logging.info("Lines detection: Running")
lines = np.zeros((100, 4))
for i in tqdm(range(len(images))):
    frame = images[i]
    frame = cv2.GaussianBlur(frame, (5,5), 0)
    edges = cv2.Cany(frame, 100, 200)
    lines[i, :] = cv2.HoughLinesP(edges, 1, np.pi/180, 200, 100, 10)
logging.info("Line detection: Complete")

logging.info("Model fitting: Running")
clasters = DBSCAN(min_samples=1, verbose=True).fit(lines)
labels = clasters.labels_.T
lines = np.caoncatenate((lines, labels), axis=1)
logging.info("Model fitting: Complete")

logging.info("Writing to config file: Running")
json_file = dict()
for key, group in tqdm(groupby(lines, lambda x: x[-1])):
    mean = np.mean(group, axis=0)
    json_file[key] = mean
json.dump(json_file, "config.json")
logging.info("Writing to config file: Complete")
print("Configuration complete. Run main.py to start working")

cv2.destroyAllWindows()
