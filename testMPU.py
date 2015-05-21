__author__ = 'Geir'

from MPU6050 import MPU6050

mpu = MPU6050(0x68, -5478, -1456, 1321, -5, -16, -8)

while True:
    print(mpu.get_acceleration())