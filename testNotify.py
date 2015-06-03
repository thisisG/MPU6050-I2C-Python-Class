import sys
import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

class MyHandler(FileSystemEventHandler):
    """
    # React to changes in YAML files, handling create, update, unlink
    # explicitly. Ignore directories. Warning: does not handle move
    # operations (mv f1.yaml f2.yaml) isn't handled.
    """

    def catch_all(self, event, op):

        if event.is_directory:
            print event.src_path

        filename = event.src_path
        print(filename)
        #extension = os.path.splitext(filename)[-1].lower()
        #if extension == '.yaml':
        #    print "YAML: (%s) %s" % (op, filename)
        #    err = validyaml(filename)
        #    if err is not None:
        #        notify("%s\n\n%s" % (os.path.basename(filename), str(err)))
        #        print "ERROR in loading yaml (%s)" % err

    def on_created(self, event):
        self.catch_all(event, 'NEW')

    def on_modified(self, event):
        self.catch_all(event, 'MOD')

def eventHappened():
    print('event!')


#path = '/sys/devices/virtual/gpio/gpio30'
path = '.'
observer = Observer()
event_handler = MyHandler()
observer.schedule(event_handler, path, recursive=True)
observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
