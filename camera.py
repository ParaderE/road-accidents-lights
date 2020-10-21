import cv2
import tensorflow as tf


class CamCapture(cv2.VideoCapture):
    """Class for camera video capture"""

    def __init__(self):
        super().__init__(0)
    
    def read(self, to_tensor=False *args, **kwargs):
        """Preprocess readed camera frame to tensor"""
        res, frame = super().read(*args, **kwargs)
        if to_tensor:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = cv2.GaussianBlur(image, (5,5), 0)
            tensor_image = tf.convert_to_tensor(image, dtype=tf.float32)
            tensor_image = tf.expand_dims(tensor_image, axis=0)
            return res, tensor_image
        else:
            return res, frame
    