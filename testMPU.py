__author__ = 'Geir'

from MPU6050 import MPU6050

mpu = MPU6050()

while True:
    print(mpu.get_acceleration())