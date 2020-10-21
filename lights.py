import time
from queue import Queue

from gpiozero.gpio import LED


class LightManager:

    def __init__(self, config):
        self.config = config
        self.times = Queue()
    
    def turn_on(self, line):
        LED(self.config[line]).on()
        self.times.put((line, time.time))
        if self.times[-1][1] - time.time < 600:
            LED(self.times[-1][0]).off()
        