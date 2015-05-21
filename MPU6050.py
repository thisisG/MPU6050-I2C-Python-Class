__author__ = 'Geir Istad'
'''
MPU6050 Python I2C Class
Copyright (c) 2015 Geir Istad

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


Code based on
I2Cdev library collection - MPU6050 I2C device class
by Jeff Rowberg <jeff@rowberg.net>
============================================
I2Cdev device library code is placed under the MIT license
Copyright (c) 2012 Jeff Rowberg
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
===============================================
'''

from Adafruit_I2C import Adafruit_I2C
from MPUConstants import MPUConstants as C
from ctypes import c_int16


class MPU6050:
    __mpu = Adafruit_I2C
    __buffer = [0] * 14

    def __init__(self, a_address=C.MPU6050_DEFAULT_ADDRESS, a_xAOff=0,
                 a_yAOff=0, a_zAOff=0, a_xGOff=0, a_yGOff=0, a_zGOff=0):
        # Connect to the I2C bus with default address of device as 0x68
        self.__mpu = Adafruit_I2C(a_address)
        # Set clock source to gyro
        self.__set_clock_source(C.MPU6050_CLOCK_PLL_XGYRO)
        # Set accelerometer range
        self.__set_full_scale_accel_range(C.MPU6050_ACCEL_FS_2)
        # Set gyro range
        self.__set_full_scale_gyro_range(C.MPU6050_GYRO_FS_250)
        # Set offsets
        self.set_x_accel_offset(a_xAOff)
        self.set_y_accel_offset(a_yAOff)
        self.set_z_accel_offset(a_zAOff)
        self.set_x_gyro_offset(a_xGOff)
        self.set_y_gyro_offset(a_xGOff)
        self.set_z_gyro_offset(a_zGOff)
        # Take the MPU out of sleep mode
        self.__wake_up()

    def __wake_up(self):
        self.__write_bit(C.MPU6050_RA_PWR_MGMT_1, C.MPU6050_PWR1_SLEEP_BIT, 0)

    def __write_bit(self, a_reg_add, a_bit_num, a_data):
        byte = self.__mpu.readU8(a_reg_add)
        if a_data == 1:
            byte = byte | (1 << a_bit_num)
        else:
            byte = byte & ~(1 << a_bit_num)
        self.__mpu.write8(a_reg_add, byte)

    def __write_bits(self, a_reg_add, a_bit_start, a_length, a_data):
        byte = self.__mpu.readU8(a_reg_add)
        mask = ((1 << a_length) - 1) << (a_bit_start - a_length + 1)
        # Get data in position and zero all non-important bits in data
        a_data = a_data << (a_bit_start - a_length + 1)
        a_data = a_data & mask
        # Clear all important bits in read byte and combine with data
        byte = byte & (~mask)
        byte = byte | a_data
        # Write the data to the I2C device
        self.__mpu.write8(a_reg_add, byte)

    def __set_clock_source(self, a_source):
        self.__write_bits(C.MPU6050_RA_PWR_MGMT_1, C.MPU6050_PWR1_CLKSEL_BIT,
                          C.MPU6050_PWR1_CLKSEL_LENGTH, a_source)

    def __set_full_scale_gyro_range(self, a_data):
        self.__write_bits(C.MPU6050_RA_GYRO_CONFIG,
                          C.MPU6050_GCONFIG_FS_SEL_BIT,
                          C.MPU6050_GCONFIG_FS_SEL_LENGTH, a_data)

    def __set_full_scale_accel_range(self, a_data):
        self.__write_bits(C.MPU6050_RA_ACCEL_CONFIG,
                          C.MPU6050_ACONFIG_AFS_SEL_BIT,
                          C.MPU6050_ACONFIG_AFS_SEL_LENGTH, a_data)

    def get_acceleration(self):
        raw_data = self.__mpu.readList(C.MPU6050_RA_ACCEL_XOUT_H, 6)
        accel = [0]*3
        accel[0] = c_int16(raw_data[0] << 8 | raw_data[1]).value
        accel[1] = c_int16(raw_data[2] << 8 | raw_data[3]).value
        accel[2] = c_int16(raw_data[4] << 8 | raw_data[5]).value
        return accel

    def get_rotation(self):
        raw_data = self.__mpu.readList(C.MPU6050_RA_ACCEL_XOUT_H, 6)
        gyro = [0]*3
        gyro[0] = c_int16(raw_data[0] << 8 | raw_data[1]).value
        gyro[1] = c_int16(raw_data[2] << 8 | raw_data[3]).value
        gyro[2] = c_int16(raw_data[4] << 8 | raw_data[5]).value
        return gyro

    def set_x_accel_offset(self, a_offset):
        self.__mpu.write16(C.MPU6050_RA_XA_OFFS_H, a_offset)

    def set_y_accel_offset(self, a_offset):
        self.__mpu.write16(C.MPU6050_RA_YA_OFFS_H, a_offset)

    def set_z_accel_offset(self, a_offset):
        self.__mpu.write16(C.MPU6050_RA_ZA_OFFS_H, a_offset)

    def set_x_gyro_offset(self, a_offset):
        self.__write_bits(
            C.MPU6050_RA_XG_OFFS_TC, C.MPU6050_TC_OFFSET_BIT,
            C.MPU6050_TC_OFFSET_LENGTH, a_offset)

    def set_y_gyro_offset(self, a_offset):
        self.__write_bits(
            C.MPU6050_RA_YG_OFFS_TC, C.MPU6050_TC_OFFSET_BIT,
            C.MPU6050_TC_OFFSET_LENGTH, a_offset)

    def set_z_gyro_offset(self, a_offset):
        self.__write_bits(
            C.MPU6050_RA_ZG_OFFS_TC, C.MPU6050_TC_OFFSET_BIT,
            C.MPU6050_TC_OFFSET_LENGTH, a_offset)
