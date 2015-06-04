import time
from MPU6050 import MPU6050
from MPU6050 import MPU6050IRQHandler
import Adafruit_BBIO.GPIO as GPIO

i2c_bus = 1
device_address = 0x68
# The offsets are different for each device and should be changed
# accordingly using a calibration procedure
x_accel_offset = -5489
y_accel_offset = -1441
z_accel_offset = 1305
x_gyro_offset = -2
y_gyro_offset = -72
z_gyro_offset = -5
enable_debug_output = True


class MPUContainer:
    mpu = None

    def __init__(self, i2c_bus, device_address, x_accel_offset, y_accel_offset,
                 z_accel_offset, x_gyro_offset, y_gyro_offset, z_gyro_offset,
                 enable_debug_output):

        self.mpu = MPU6050(i2c_bus, device_address, x_accel_offset,
                             y_accel_offset, z_accel_offset, x_gyro_offset,
                             y_gyro_offset, z_gyro_offset, enable_debug_output)

mpuC = MPUContainer(i2c_bus, device_address, x_accel_offset, y_accel_offset,
                 z_accel_offset, x_gyro_offset, y_gyro_offset, z_gyro_offset,
                 enable_debug_output)

mpuC.mpu.dmp_initialize()
mpuC.mpu.set_DMP_enabled(True)
mpuC.mpu_int_status = mpu.get_int_status()
print(hex(mpuC.mpu_int_status))

packet_size = mpuC.mpu.DMP_get_FIFO_packet_size()
print(packet_size)
FIFO_count = mpuC.mpu.get_FIFO_count()
print(FIFO_count)

handler = MPU6050IRQHandler(mpuC.mpu)

GPIO.setup("P9_11", GPIO.IN)
GPIO.add_event_detect("P9_11", GPIO.RISING, callback=handler.action)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
GPIO.cleanup()
