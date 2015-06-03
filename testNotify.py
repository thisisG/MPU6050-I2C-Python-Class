import sys
import time
from watchdog.observers import Observer

if __name__ == "__main__":
    path = '/sys/class/gpio/gpio30/value'
    event_handler = eventHappened()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def eventHappened():
    print('event!')
