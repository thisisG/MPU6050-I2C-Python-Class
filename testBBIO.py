import Adafruit_BBIO.GPIO as GPIO
GPIO.setup("P9_11", GPIO.IN)
def E():
    print('edge!')

GPIO.add_event_detect("P9_11", GPIO.RISING, callback=E)
