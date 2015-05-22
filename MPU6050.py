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
from ctypes import c_int16, c_int8
from time import sleep


class MPU6050:
    __mpu = Adafruit_I2C
    __buffer = [0] * 14

    def __init__(self, a_address=C.MPU6050_DEFAULT_ADDRESS, a_xAOff=None,
                 a_yAOff=None, a_zAOff=None, a_xGOff=None, a_yGOff=None,
                 a_zGOff=None):
        # Connect to the I2C bus with default address of device as 0x68
        self.__mpu = Adafruit_I2C(a_address)
        # Set clock source to gyro
        self.set_clock_source(C.MPU6050_CLOCK_PLL_XGYRO)
        # Set accelerometer range
        self.set_full_scale_accel_range(C.MPU6050_ACCEL_FS_2)
        # Set gyro range
        self.set_full_scale_gyro_range(C.MPU6050_GYRO_FS_250)
        # Take the MPU out of sleep mode
        self.wake_up()
        # Set offsets
        if a_xAOff is not None:
            self.set_x_accel_offset(a_xAOff)
        if a_yAOff is not None:
            self.set_y_accel_offset(a_yAOff)
        if a_zAOff is not None:
            self.set_z_accel_offset(a_zAOff)
        if a_xGOff is not None:
            self.set_x_gyro_offset(a_xGOff)
        if a_yGOff is not None:
            self.set_y_gyro_offset(a_yGOff)
        if a_zGOff is not None:
            self.set_z_gyro_offset(a_zGOff)

    def wake_up(self):
        self.write_bit(C.MPU6050_RA_PWR_MGMT_1, C.MPU6050_PWR1_SLEEP_BIT, 0)

    def write_bit(self, a_reg_add, a_bit_num, a_data):
        byte = self.__mpu.readU8(a_reg_add)
        if a_data == 1:
            byte = byte | (1 << a_bit_num)
        else:
            byte = byte & ~(1 << a_bit_num)
        self.__mpu.write8(a_reg_add, c_int8(byte).value)

    def write_bits(self, a_reg_add, a_bit_start, a_length, a_data):
        byte = self.__mpu.readU8(a_reg_add)
        mask = ((1 << a_length) - 1) << (a_bit_start - a_length + 1)
        # Get data in position and zero all non-important bits in data
        a_data = a_data << (a_bit_start - a_length + 1)
        a_data = a_data & mask
        # Clear all important bits in read byte and combine with data
        byte = byte & (~mask)
        byte = byte | a_data
        # Write the data to the I2C device
        self.__mpu.write8(a_reg_add, c_int8(byte).value)

    def set_clock_source(self, a_source):
        self.write_bits(C.MPU6050_RA_PWR_MGMT_1, C.MPU6050_PWR1_CLKSEL_BIT,
                        C.MPU6050_PWR1_CLKSEL_LENGTH, a_source)

    def set_full_scale_gyro_range(self, a_data):
        self.write_bits(C.MPU6050_RA_GYRO_CONFIG,
                        C.MPU6050_GCONFIG_FS_SEL_BIT,
                        C.MPU6050_GCONFIG_FS_SEL_LENGTH, a_data)

    def set_full_scale_accel_range(self, a_data):
        self.write_bits(C.MPU6050_RA_ACCEL_CONFIG,
                        C.MPU6050_ACONFIG_AFS_SEL_BIT,
                        C.MPU6050_ACONFIG_AFS_SEL_LENGTH, a_data)

    def reset(self):
        self.write_bit(C.MPU6050_RA_PWR_MGMT_1,
                       C.MPU6050_PWR1_DEVICE_RESET_BIT, 1)

    def set_sleep_enabled(self, a_enabled):
        self.write_bit(C.MPU6050_RA_PWR_MGMT_1,
                       C.MPU6050_PWR1_SLEEP_BIT, a_enabled)

    def set_memory_bank(self, a_bank, a_prefetch_enabled, a_user_bank):
        a_bank = a_bank & 0x1F
        if a_user_bank is True:
            a_bank = a_bank | 0x20
        if a_prefetch_enabled is True:
            a_bank = a_bank | 0x20
        self.__mpu.write8(C.MPU6050_RA_BANK_SEL, a_bank)

    def set_memory_start_address(self, a_address):
        self.__mpu.write8(C.MPU6050_RA_MEM_START_ADDR, a_address)

    def read_bits(self, a_reg_add, a_bit_start, a_length):
        byte = self.__mpu.readU8(a_reg_add)
        mask = ((1 << a_length) - 1) << (a_bit_start - a_length + 1)
        byte = byte & mask
        byte = byte >> (a_bit_start - a_length + 1)
        return byte

    def get_x_gyro_offset_tc(self):
        return self.read_bits(C.MPU6050_RA_XG_OFFS_TC,
                              C.MPU6050_TC_OFFSET_BIT,
                              C.MPU6050_TC_OFFSET_LENGTH)

    def get_y_gyro_offset_tc(self):
        return self.read_bits(C.MPU6050_RA_YG_OFFS_TC,
                              C.MPU6050_TC_OFFSET_BIT,
                              C.MPU6050_TC_OFFSET_LENGTH)

    def get_z_gyro_offset_tc(self):
        return self.read_bits(C.MPU6050_RA_ZG_OFFS_TC,
                              C.MPU6050_TC_OFFSET_BIT,
                              C.MPU6050_TC_OFFSET_LENGTH)

    def set_slave_address(self, a_num, a_address):
        self.__mpu.write8(C.MPU6050_RA_I2C_SLV0_ADDR + a_num*3, a_address)

    def set_I2C_master_mode_enabled(a_enabled):
        self.__mpu.write8(C.MPU6050_RA_USER_CTRL,
                          C.MPU6050_USERCTRL_I2C_MST_EN_BIT, a_enabled)

    def reset_I2C_master(self):
        self.__mpu.write8(C.MPU6050_RA_USER_CTRL,
                          C.MPU6050_USERCTRL_I2C_MST_RESET_BIT, 1)

    '''
    declaration:
    bool writeProgMemoryBlock(const uint8_t *data, uint16_t dataSize,
    uint8_t bank=0, uint8_t address=0, bool verify=true);

    implementation:
    bool MPU6050::writeProgMemoryBlock(const uint8_t *data, uint16_t dataSize,
    uint8_t bank, uint8_t address, bool verify) {
    return writeMemoryBlock(data, dataSize, bank, address, verify, true);
    '''

    def write_prog_memory_block(self, a_data_list, a_data_size, a_bank=0,
                                a_address=0, a_verify=True):

    def dmp_initialize(self):
        # Reset the MPU
        self.reset()
        # Sleep a bit while resetting
        sleep(50/1000)
        # Disable sleep mode
        self.set_sleep_enabled(0)

        # get MPU hardware revision
        '''DEBUG_PRINTLN(F("Selecting user bank 16..."));
        setMemoryBank(0x10, true, true);'''
        self.set_memory_bank(0x10, True, True)

        '''DEBUG_PRINTLN(F("Selecting memory byte 6..."));
        setMemoryStartAddress(0x06);'''
        self.set_memory_start_address(0x6)

        '''DEBUG_PRINTLN(F("Checking hardware revision..."));
        uint8_t hwRevision = readMemoryByte();
        DEBUG_PRINT(F("Revision @ user[16][6] = "));
        DEBUG_PRINTLNF(hwRevision, HEX);'''

        '''DEBUG_PRINTLN(F("Resetting memory bank selection to 0..."));
        setMemoryBank(0, false, false);'''
        self.set_memory_bank(0, False, False)

        # check OTP bank valid
        '''DEBUG_PRINTLN(F("Reading OTP bank valid flag..."));
        uint8_t otpValid = getOTPBankValid();
        DEBUG_PRINT(F("OTP bank is "));
        DEBUG_PRINTLN(otpValid ? F("valid!") : F("invalid!"));'''

        # get X/Y/Z gyro offsets
        '''DEBUG_PRINTLN(F("Reading gyro offset TC values..."));
        int8_t xgOffsetTC = getXGyroOffsetTC();
        int8_t ygOffsetTC = getYGyroOffsetTC();
        int8_t zgOffsetTC = getZGyroOffsetTC();'''
        x_g_offset_tc = self.get_x_gyro_offset_tc()
        y_g_offset_tc = self.get_y_gyro_offset_tc()
        z_g_offset_tc = self.get_z_gyro_offset_tc()
        '''DEBUG_PRINT(F("X gyro offset = "));
        DEBUG_PRINTLN(xgOffset);
        DEBUG_PRINT(F("Y gyro offset = "));
        DEBUG_PRINTLN(ygOffset);
        DEBUG_PRINT(F("Z gyro offset = "));
        DEBUG_PRINTLN(zgOffset);'''

        # setup weird slave stuff (?)
        '''DEBUG_PRINTLN(F("Setting slave 0 address to 0x7F..."));
        setSlaveAddress(0, 0x7F);'''
        self.set_slave_address(0, 0x7F)
        '''DEBUG_PRINTLN(F("Disabling I2C Master mode..."));
        setI2CMasterModeEnabled(false);'''
        self.set_I2C_master_mode_enabled(0)
        '''DEBUG_PRINTLN(F("Setting slave 0 address to 0x68 (self)..."));
        setSlaveAddress(0, 0x68);'''
        self.set_slave_address(0, 0x68)
        '''DEBUG_PRINTLN(F("Resetting I2C Master control..."));
        resetI2CMaster();'''
        self.resetI2CMaster()
        '''delay(20);'''
        sleep(20/1000)

        # load DMP code into memory banks
        '''DEBUG_PRINT(F("Writing DMP code to MPU memory banks ("));
        DEBUG_PRINT(MPU6050_DMP_CODE_SIZE);
        DEBUG_PRINTLN(F(" bytes)"));'''

        '''
        if (writeProgMemoryBlock(dmpMemory, MPU6050_DMP_CODE_SIZE))
        '''
        # TODO implement write_prog_memory_block
        if write_prog_memory_block(C.dmpMemory, C.MPU6050_DMP_CODE_SIZE):

            '''
            DEBUG_PRINTLN(F("Success! DMP code written and verified."));

            // write DMP configuration
            DEBUG_PRINT(F("Writing DMP configuration to MPU memory banks ("));
            DEBUG_PRINT(MPU6050_DMP_CONFIG_SIZE);
            '''
            # TODO
            '''
            DEBUG_PRINTLN(F(" bytes in config def)"));

            if (writeProgDMPConfigurationSet(dmpConfig, MPU6050_DMP_CONFIG_SIZE))
            '''
            # TODO implement write_prog_dmp_configuration_set
            if write_prog_dmp_configuration_set(C.dmpConfig,
                                                C.MPU6050_DMP_CONFIG_SIZE):

                '''
                DEBUG_PRINTLN(F("Success! DMP configuration written and verified."));

                DEBUG_PRINTLN(F("Setting clock source to Z Gyro..."));
                setClockSource(MPU6050_CLOCK_PLL_ZGYRO);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Setting DMP and FIFO_OFLOW interrupts enabled..."));
                setIntEnabled(0x12);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Setting sample rate to 200Hz..."));
                setRate(4); // 1khz / (1 + 4) = 200 Hz
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Setting external frame sync to TEMP_OUT_L[0]..."));
                setExternalFrameSync(MPU6050_EXT_SYNC_TEMP_OUT_L);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Setting DLPF bandwidth to 42Hz..."));
                setDLPFMode(MPU6050_DLPF_BW_42);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Setting gyro sensitivity to +/- 2000 deg/sec..."));
                setFullScaleGyroRange(MPU6050_GYRO_FS_2000);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Setting DMP configuration bytes (function unknown)..."));
                setDMPConfig1(0x03);
                setDMPConfig2(0x00);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Clearing OTP Bank flag..."));
                setOTPBankValid(false);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Setting X/Y/Z gyro offset TCs to previous values..."));
                setXGyroOffsetTC(xgOffsetTC);
                setYGyroOffsetTC(ygOffsetTC);
                setZGyroOffsetTC(zgOffsetTC);
                '''
                # TODO
                '''
                //DEBUG_PRINTLN(F("Setting X/Y/Z gyro user offsets to zero..."));
                //setXGyroOffset(0);
                //setYGyroOffset(0);
                //setZGyroOffset(0);

                DEBUG_PRINTLN(F("Writing final memory update 1/7 (function unknown)..."));
                uint8_t dmpUpdate[16], j;
                uint16_t pos = 0;
                for (j = 0; j < 4 || j < dmpUpdate[2] + 3; j++, pos++) dmpUpdate[j] = pgm_read_byte(&dmpUpdates[pos]);
                writeMemoryBlock(dmpUpdate + 3, dmpUpdate[2], dmpUpdate[0], dmpUpdate[1]);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Writing final memory update 2/7 (function unknown)..."));
                for (j = 0; j < 4 || j < dmpUpdate[2] + 3; j++, pos++) dmpUpdate[j] = pgm_read_byte(&dmpUpdates[pos]);
                writeMemoryBlock(dmpUpdate + 3, dmpUpdate[2], dmpUpdate[0], dmpUpdate[1]);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Resetting FIFO..."));
                resetFIFO();
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Reading FIFO count..."));
                uint16_t fifoCount = getFIFOCount();
                uint8_t fifoBuffer[128];
                '''
                # TODO
                '''
                DEBUG_PRINT(F("Current FIFO count="));
                DEBUG_PRINTLN(fifoCount);
                getFIFOBytes(fifoBuffer, fifoCount);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Setting motion detection threshold to 2..."));
                setMotionDetectionThreshold(2);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Setting zero-motion detection threshold to 156..."));
                setZeroMotionDetectionThreshold(156);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Setting motion detection duration to 80..."));
                setMotionDetectionDuration(80);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Setting zero-motion detection duration to 0..."));
                setZeroMotionDetectionDuration(0);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Resetting FIFO..."));
                resetFIFO();
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Enabling FIFO..."));
                setFIFOEnabled(true);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Enabling DMP..."));
                setDMPEnabled(true);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Resetting DMP..."));
                resetDMP();
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Writing final memory update 3/7 (function unknown)..."));
                for (j = 0; j < 4 || j < dmpUpdate[2] + 3; j++, pos++) dmpUpdate[j] = pgm_read_byte(&dmpUpdates[pos]);
                writeMemoryBlock(dmpUpdate + 3, dmpUpdate[2], dmpUpdate[0], dmpUpdate[1]);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Writing final memory update 4/7 (function unknown)..."));
                for (j = 0; j < 4 || j < dmpUpdate[2] + 3; j++, pos++) dmpUpdate[j] = pgm_read_byte(&dmpUpdates[pos]);
                writeMemoryBlock(dmpUpdate + 3, dmpUpdate[2], dmpUpdate[0], dmpUpdate[1]);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Writing final memory update 5/7 (function unknown)..."));
                for (j = 0; j < 4 || j < dmpUpdate[2] + 3; j++, pos++) dmpUpdate[j] = pgm_read_byte(&dmpUpdates[pos]);
                writeMemoryBlock(dmpUpdate + 3, dmpUpdate[2], dmpUpdate[0], dmpUpdate[1]);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Waiting for FIFO count > 2..."));
                while ((fifoCount = getFIFOCount()) < 3);
                '''
                # TODO
                '''
                DEBUG_PRINT(F("Current FIFO count="));
                DEBUG_PRINTLN(fifoCount);
                DEBUG_PRINTLN(F("Reading FIFO data..."));
                getFIFOBytes(fifoBuffer, fifoCount);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Reading interrupt status..."));
                uint8_t mpuIntStatus = getIntStatus();
                '''
                # TODO
                '''
                DEBUG_PRINT(F("Current interrupt status="));
                DEBUG_PRINTLNF(mpuIntStatus, HEX);

                DEBUG_PRINTLN(F("Reading final memory update 6/7 (function unknown)..."));
                for (j = 0; j < 4 || j < dmpUpdate[2] + 3; j++, pos++) dmpUpdate[j] = pgm_read_byte(&dmpUpdates[pos]);
                readMemoryBlock(dmpUpdate + 3, dmpUpdate[2], dmpUpdate[0], dmpUpdate[1]);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Waiting for FIFO count > 2..."));
                while ((fifoCount = getFIFOCount()) < 3);
                '''
                # TODO
                '''
                DEBUG_PRINT(F("Current FIFO count="));
                DEBUG_PRINTLN(fifoCount);

                DEBUG_PRINTLN(F("Reading FIFO data..."));
                getFIFOBytes(fifoBuffer, fifoCount);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Reading interrupt status..."));
                mpuIntStatus = getIntStatus();
                '''
                # TODO
                '''
                DEBUG_PRINT(F("Current interrupt status="));
                DEBUG_PRINTLNF(mpuIntStatus, HEX);

                DEBUG_PRINTLN(F("Writing final memory update 7/7 (function unknown)..."));
                for (j = 0; j < 4 || j < dmpUpdate[2] + 3; j++, pos++) dmpUpdate[j] = pgm_read_byte(&dmpUpdates[pos]);
                writeMemoryBlock(dmpUpdate + 3, dmpUpdate[2], dmpUpdate[0], dmpUpdate[1]);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("DMP is good to go! Finally."));

                DEBUG_PRINTLN(F("Disabling DMP (you turn it on later)..."));
                setDMPEnabled(false);
                '''
                # TODO
                '''
                DEBUG_PRINTLN(F("Setting up internal 42-byte (default) DMP packet buffer..."));
                dmpPacketSize = 42;
                /*if ((dmpPacketBuffer = (uint8_t *)malloc(42)) == 0) {
                    return 3; // TODO: proper error code for no memory
                }*/

                DEBUG_PRINTLN(F("Resetting FIFO and clearing INT status one last time..."));
                resetFIFO();
                getIntStatus();
                '''
                # TODO

            else:
                # configuration block loading failed
                return 2

        else:
            # main binary block loading failed
            return 1

        # success
        return 0

    def get_acceleration(self):
        raw_data = self.__mpu.readList(C.MPU6050_RA_ACCEL_XOUT_H, 6)
        accel = [0]*3
        accel[0] = c_int16(raw_data[0] << 8 | raw_data[1]).value
        accel[1] = c_int16(raw_data[2] << 8 | raw_data[3]).value
        accel[2] = c_int16(raw_data[4] << 8 | raw_data[5]).value
        return accel

    def get_rotation(self):
        raw_data = self.__mpu.readList(C.MPU6050_RA_GYRO_XOUT_H, 6)
        gyro = [0]*3
        gyro[0] = c_int16(raw_data[0] << 8 | raw_data[1]).value
        gyro[1] = c_int16(raw_data[2] << 8 | raw_data[3]).value
        gyro[2] = c_int16(raw_data[4] << 8 | raw_data[5]).value
        return gyro

    def set_x_accel_offset(self, a_offset):
        self.__mpu.write8(C.MPU6050_RA_XA_OFFS_H,
                          c_int8(a_offset >> 8).value)
        self.__mpu.write8(C.MPU6050_RA_XA_OFFS_L_TC, c_int8(a_offset).value)

    def set_y_accel_offset(self, a_offset):
        self.__mpu.write8(C.MPU6050_RA_YA_OFFS_H,
                          c_int8(a_offset >> 8).value)
        self.__mpu.write8(C.MPU6050_RA_YA_OFFS_L_TC, c_int8(a_offset).value)

    def set_z_accel_offset(self, a_offset):
        self.__mpu.write8(C.MPU6050_RA_ZA_OFFS_H,
                          c_int8(a_offset >> 8).value)
        self.__mpu.write8(C.MPU6050_RA_ZA_OFFS_L_TC, c_int8(a_offset).value)

    def set_x_gyro_offset(self, a_offset):
        self.__mpu.write8(C.MPU6050_RA_XG_OFFS_USRH,
                          c_int8(a_offset >> 8).value)
        self.__mpu.write8(C.MPU6050_RA_XG_OFFS_USRL, c_int8(a_offset).value)

    def set_y_gyro_offset(self, a_offset):
        self.__mpu.write8(C.MPU6050_RA_YG_OFFS_USRH,
                          c_int8(a_offset >> 8).value)
        self.__mpu.write8(C.MPU6050_RA_YG_OFFS_USRL, c_int8(a_offset).value)

    def set_z_gyro_offset(self, a_offset):
        self.__mpu.write8(C.MPU6050_RA_ZG_OFFS_USRH,
                          c_int8(a_offset >> 8).value)
        self.__mpu.write8(C.MPU6050_RA_ZG_OFFS_USRL, c_int8(a_offset).value)
