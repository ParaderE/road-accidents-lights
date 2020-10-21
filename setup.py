import os
import time
import json
import logging
from itertools import groupby
from camera import CamCapture
logging.basicConfig(level=logging.INFO)
try:
    from tqdm import tqdm
except ImportError as e:
    logging.warning(e)
    a = input("Install tqdm [y/N]?")
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


def detect_lines(images):
    logging.info("Lines detection: Running")
    lines = np.zeros((len(images), 4))
    for i in tqdm(range(len(images))):
        frame = images[i]
        frame = cv2.GaussianBlur(frame, (5,5), 0)
        edges = cv2.Cany(frame, 100, 200)
        lines[i, :] = cv2.HoughLinesP(edges, 1, np.pi/180, 200, 100, 10)
    logging.info("Line detection: Complete")
    return lines


def group_lines(lines):
    logging.info("Model fitting: Running")
    clasters = DBSCAN(min_samples=1, verbose=True).fit(lines)
    labels = clasters.labels_.T
    lines = np.concatenate((lines, labels), axis=1)
    logging.info("Model fitting: Complete")
    return lines

def config(lines):
    logging.info("Writing to config file: Running")
    json_file = dict()
    for key, group in tqdm(groupby(lines, lambda x: x[-1])):
        mean = np.mean(group, axis=0)
        json_file[key] = mean
    logging.info("Writing to config file: Complete")
    return json.dumps(json_file, "config.json")


if __name__ == "__main__":
    cap = CamCapture()
    logging.info("Image shooting: Running")
    images = list()
    for i in tqdm(range(100)):
        _, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        images.append(frame)
        time.sleep(1)
    cap.release()
    logging.info("Image shooting: Complete")

    lines = detect_lines(images)
    lines = group_lines(lines)
    config_js = config(lines)
    with open("config.json", "r+") as f:
        f.write(config_js)

    prompt = input("Include trafic lights turning on/off [Y/n]?")
    if not prompt or prompt.lower().startswith("y"):
        print("Please, make configuration in board_config.json")
        with open("board_config.json", "w") as a:
            a.write("""{
                # key - number of the line from the left
                # value - pin for that line
                }""")
        os.environ["LIGHTS"] = 1
    else:
        os.environ["LIGHTS"] = 0
    print("Configuration complete. Run main.py to start working")

    cv2.destroyAllWindows()
