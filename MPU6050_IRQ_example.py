import time
from MPU6050 import MPU6050
from MPU6050 import MPU6050IRQHandler
import Adafruit_BBIO.GPIO as GPIO

i2c_bus = 1
device_address = 0x68
# The offsets are different for each device and should be changed to
# sutiable figures using a calibration procedure
x_accel_offset = -5489
y_accel_offset = -1441
z_accel_offset = 1305
x_gyro_offset = -2
y_gyro_offset = -72
z_gyro_offset = -5
enable_debug_output = True
enable_logging = True
log_file = 'mpulog.csv'

mpu = MPU6050(i2c_bus, device_address, x_accel_offset,
              y_accel_offset, z_accel_offset, x_gyro_offset,
              y_gyro_offset, z_gyro_offset, enable_debug_output)
mpuC = MPU6050IRQHandler(mpu, enable_logging, log_file)

GPIO.setup("P9_11", GPIO.IN)
GPIO.add_event_detect("P9_11", GPIO.RISING, callback=mpuC.action)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
GPIO.cleanup()
