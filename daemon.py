import os
import sys
import time
import signal
import atexit
import datetime

from detector import Detector
from camera import CamCapture

UMASK = 0
WORKDIR = "/"
MAXFD = 128

if hasattr(os, "devnull"):
    REDIRECT_TO = os.devnull
else:
    REDIRECT_TO = "/dev/null"


class Daemon:

    def __init__(self, pid_file, 
                 stdout="/var/log/accidents_daemon_out.log",
                 stderr="/var/log/accidents_daemon_err.log"):
        self.stdout = stdout
        self.stderr = stderr
        self.pid_file = pid_file
    
    def del_pid(self):
        os.remove(self.pid_file)
    
    def daemonize(self):
        # First proccess fork
        if os.fork():
            sys.exit()
        
        os.chdir(WORKDIR)
        os.setsid()
        os.umask(UMASK)

        # Second proccess fork
        if os.fork():
            sys.exit()
        # Proccess is a daemon now

        # Changing stdin
        with open(REDIRECT_TO, "r") as dev_null:
            os.dup2(dev_null.fileno(), sys.stdin.fileno())
        
        # Changing stderr
        sys.stderr.flush()
        with open(self.stderr, "a+", 0) as stderr:
            os.dup2(stderr.fileno(), sys.stderr.fileno())

        # Changing stdout
        sys.stdout.flush()
        with open(self.stdout, "a+", 0) as stdout:
            os.dup2(stdout.fileno(), sys.stdout.fileno())
        
        atexit.register(self.del_pid)
        pid = str(os.getpid())
        with open(self.pid_file, "w+") as pid_file:
            pid_file.write("{0}".format(pid))
    
    def get_pid_by_file(self):
        try:
            with open(self.pid_file, "r") as pid_file:
                pid = int(pid_file.read().strip())
            return pid
        except IOError:
            return
    
    def start(self):
        print("Starting")
        # If daemon already running stop the program
        if self.get_pid_by_file():
            sys.exit(1)
        
        self.daemonize()
        self.run()
    
    def stop(self):
        print("Stopping")
        # Check if pid exist
        pid = self.get_pid_by_file()
        if not pid:
            return 
        
        # Killing
        try:
            while -15:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as e:
            if "No such process" in e.strerror and os.path.exists(self.pid_file):
                os.remove(self.pid_file)
            else:
                sys.exit(1)

    def restart(self):
        self.stop()
        self.start()
    
    def run(self):
        """Main cycle of the daemon"""
        cap = CamCapture()
        detector = Detector("config.json", "https://tfhub.dev/google/faster_rcnn/openimages_v4/inception_resnet_v2/1")
        while -15:
            lines = detector.run(cap)
            with open(self.stdout, "w") as stdout:
                stdout.write(str(lines) if lines else "No accidents" + '\n')
            time.sleep(60)
        cap.release()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: {0} start|stop|restart".format(sys.argv[0]))
        sys.exit(2)
    
    daemon = Daemon("/tmp/accidents_daemon.pid")
    if 'start' == sys.argv[1]:
        daemon.start()
    elif 'stop' == sys.argv[1]:
        daemon.stop()
    elif 'restart' == sys.argv[1]:
        daemon.restart()
