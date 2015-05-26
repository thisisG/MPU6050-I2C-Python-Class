from numpy.f2py.auxfuncs import throw_error

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
    __debug = False

    def __init__(self, a_address=C.MPU6050_DEFAULT_ADDRESS, a_xAOff=None,
                 a_yAOff=None, a_zAOff=None, a_xGOff=None, a_yGOff=None,
                 a_zGOff=None, a_debug=False):
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
        if a_xAOff != None:
            self.set_x_accel_offset(a_xAOff)
        if a_yAOff != None:
            self.set_y_accel_offset(a_yAOff)
        if a_zAOff != None:
            self.set_z_accel_offset(a_zAOff)
        if a_xGOff != None:
            self.set_x_gyro_offset(a_xGOff)
        if a_yGOff != None:
            self.set_y_gyro_offset(a_yGOff)
        if a_zGOff != None:
            self.set_z_gyro_offset(a_zGOff)
        self.__debug = a_debug

    def wake_up(self):
        self.write_bit(C.MPU6050_RA_PWR_MGMT_1, C.MPU6050_PWR1_SLEEP_BIT, 0)

    def write_bit(self, a_reg_add, a_bit_num, a_bit):
        byte = self.__mpu.readU8(a_reg_add)
        if (a_bit == 1) or (a_bit == True):
            byte = byte | (1 << a_bit_num)
        else:
            byte = byte & ~(1 << a_bit_num)
        self.__mpu.write8(a_reg_add, c_int8(byte).value)

    def read_bits(self, a_reg_add, a_bit_start, a_length):
        byte = self.__mpu.readU8(a_reg_add)
        mask = ((1 << a_length) - 1) << (a_bit_start - a_length + 1)
        byte = byte & mask
        byte = byte >> (a_bit_start - a_length + 1)
        return byte

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
        set_bit = 0
        if (a_enabled == 1) or (a_enabled == True):
            set_bit = 1
        self.write_bit(C.MPU6050_RA_PWR_MGMT_1,
                       C.MPU6050_PWR1_SLEEP_BIT, set_bit)

    def set_memory_bank(self, a_bank, a_prefetch_enabled, a_user_bank):
        a_bank = a_bank & 0x1F
        if a_user_bank == True:
            a_bank = a_bank | 0x20
        if a_prefetch_enabled == True:
            a_bank = a_bank | 0x20
        self.__mpu.write8(C.MPU6050_RA_BANK_SEL, a_bank)

    def set_memory_start_address(self, a_address):
        self.__mpu.write8(C.MPU6050_RA_MEM_START_ADDR, a_address)

    def get_x_gyro_offset_TC(self):
        return self.read_bits(C.MPU6050_RA_XG_OFFS_TC,
                              C.MPU6050_TC_OFFSET_BIT,
                              C.MPU6050_TC_OFFSET_LENGTH)

    def set_x_gyro_offset_TC(self, a_offset):
        self.__mpu.write_bits(C.MPU6050_RA_XG_OFFS_TC,
                              C.MPU6050_TC_OFFSET_BIT,
                              C.MPU6050_TC_OFFSET_LENGTH, a_offset)

    def get_y_gyro_offset_TC(self):
        return self.read_bits(C.MPU6050_RA_YG_OFFS_TC,
                              C.MPU6050_TC_OFFSET_BIT,
                              C.MPU6050_TC_OFFSET_LENGTH)

    def set_y_gyro_offset_TC(self, a_offset):
        self.__mpu.write_bits(C.MPU6050_RA_YG_OFFS_TC,
                              C.MPU6050_TC_OFFSET_BIT,
                              C.MPU6050_TC_OFFSET_LENGTH, a_offset)

    def get_z_gyro_offset_TC(self):
        return self.read_bits(C.MPU6050_RA_ZG_OFFS_TC,
                              C.MPU6050_TC_OFFSET_BIT,
                              C.MPU6050_TC_OFFSET_LENGTH)

    def set_z_gyro_offset_TC(self, a_offset):
        self.__mpu.write_bits(C.MPU6050_RA_ZG_OFFS_TC,
                              C.MPU6050_TC_OFFSET_BIT,
                              C.MPU6050_TC_OFFSET_LENGTH, a_offset)

    def set_slave_address(self, a_num, a_address):
        self.__mpu.write8(C.MPU6050_RA_I2C_SLV0_ADDR + a_num*3, a_address)

    def set_I2C_master_mode_enabled(self, a_enabled):
        self.__mpu.write8(C.MPU6050_RA_USER_CTRL,
                          C.MPU6050_USERCTRL_I2C_MST_EN_BIT, a_enabled)

    def reset_I2C_master(self):
        self.__mpu.write8(C.MPU6050_RA_USER_CTRL,
                          C.MPU6050_USERCTRL_I2C_MST_RESET_BIT, 1)

    def write_memory_block(self, a_data_list, a_data_size, a_bank, a_address,
                           a_verify):
        self.set_memory_bank(a_bank)
        self.set_memory_start_address(a_address)

        # For each a_data_item we want to write it to the board to a certain
        # memory bank and address
        for i in range(0, a_data_size):
            # Write each data to memory
            self.__mpu.write8(C.MPU6050_RA_MEM_R_W, a_data_list[i])

            if a_verify:
                # TODO implement verification
                pass

            # If we've filled the bank, change the memory bank
            if a_address == 255:
                a_address = 0
                a_bank += 1
                self.set_memory_bank(a_bank)
            else:
                a_address += 1

            # Either way update the memory address
            self.set_memory_start_address(a_address)

        # TODO Implement a check to ensure the thrutiness of the function, most
        # likely using the verify stage
        return True

    def write_prog_memory_block(self, a_data_list, a_data_size, a_bank=0,
                                a_address=0, a_verify=True):
        return self.write_memory_block(a_data_list, a_data_size, a_bank,
                                       a_address, a_verify)

    def write_DMP_configuration_set(self, a_data_list, a_data_size):
        index = 0
        while index < a_data_size:
            bank = a_data_list[index]
            offset = a_data_list[index+1]
            length = a_data_list[index+2]
            index += 3
            success = False

            # Normal case
            if length > 0:
                data_selection = list()
                for subindex in range(0, length):
                    data_selection.append(a_data_list[index + subindex])
                success = self.write_memory_block(data_selection, length, bank,
                                                  offset, True)
                index += length
            # Special undocumented case
            else:
                special = a_data_list[index]
                index += 1
                if special == 0x01:
                    # TODO Figure out if this can return True/False
                    success = self.__mpu.write8(C.MPU6050_RA_INT_ENABLE, 0x32)

            if success == False:
                # TODO implement error messagemajigger
                return False
                pass
        return True

    def write_prog_dmp_configuration_set(self, a_data_list, a_data_size):
        return self.writeDMPConfigurationSet(a_data_list, a_data_size)

    def set_int_enable(self, a_enabled):
        self.__mpu.write8(C.MPU6050_RA_INT_ENABLE, a_enabled)

    def set_rate(self, a_rate):
        self.__mpu.write8(C.SMPLRT_DIV, a_rate)

    def set_external_frame_sync(self, a_sync):
        self.__mpu.write_bits(C.MPU6050_RA_CONFIG,
                              C.MPU6050_CFG_EXT_SYNC_SET_BIT,
                              C.MPU6050_CFG_EXT_SYNC_SET_LENGTH, a_sync)

    def set_DLF_mode(self, a_mode):
        self.__mpu.write_bits(C.MPU6050_RA_CONFIG, C.MPU6050_CFG_DLPF_CFG_BIT,
                              C.MPU6050_CFG_DLPF_CFG_LENGTH, a_mode)

    def get_DMP_config_1(self):
        return self.__mpu.readU8(C.MPU6050_RA_DMP_CFG_1)

    def set_DMP_config_1(self, a_config):
        self.__mpu.write8(C.MPU6050_RA_DMP_CFG_1, a_config)

    def get_DMP_config_2(self):
        return self.__mpu.readU8(C.MPU6050_RA_DMP_CFG_2)

    def set_DMP_config_2(self, a_config):
        self.__mpu.write8(C.MPU6050_RA_DMP_CFG_2, a_config)

    def set_OTP_bank_valid(self, a_enabled):
        self.write_bit(
            C.MPU6050_RA_XG_OFFS_TC, C.MPU6050_TC_OTP_BNK_VLD_BIT, a_enabled)

    def reset_FIFO(self):
        self.write_bit(C.MPU6050_RA_USER_CTRL,
                       C.MPU6050_USERCTRL_FIFO_RESET_BIT, True)

    def read_bytes(self, a_data_list, a_address, a_length):
        if a_length > len(a_data_list):
            print('read_bytes, length of passed list too short')
            return a_data_list
        for x in xrange(0, a_length):
            a_data_list[0] = self.__mpu.readU8(a_address + x)
        return a_data_list

    def get_FIFO_count(self):
        data = [0]*2
        data = read_bytes(data, C.MPU6050_ra_FIFO_COUNTH, 2)
        return (data[0] << 8) | data[1]

    def get_FIFO_bytes(self, a_FIFO_buffer, a_FIFO_count):
        data = self.read_bytes(a_FIFO_buffer, C.MPU6050_RA_FIFO_R_W,
                               a_FIFO_count)

    def set_motion_detection_threshold(self, a_threshold):
        self.__mpu.write8(C.MPU6050_RA_MOT_THR, a_threshold)

    def set_zero_motion_detection_threshold(self, a_threshold):
        self.__mpu.write8(C.MPU6050_RA_ZRMOT_THR, a_threshold)

    def set_motion_detection_duration(self, a_duration):
        self.__mpu.write8(C.MPU6050_RA_MOT_DUR, a_duration)

    def set_zero_motion_detection_duration(self, a_duration):
        self.__mpu.write8(C.MPU6050_RA_ZRMOT_DUR, a_duration)

    def set_FIFO_enabled(self, a_enabled):
        bit = 0
        if (a_enabled == 1) or (a_enabled == True):
            bit = 1
        self.write_bit(C.MPU6050_RA_USER_CTRL,
                       C.MPU6050_USERCTRL_FIFO_EN_BIT, bit)

    def set_DMP_enabled(self, a_enabled):
        bit = 0
        if (a_enabled == 1) or (a_enabled == True):
            bit = 1
        self.write_bit(C.MPU6050_RA_USER_CTRL,
                       C.MPU6050_USERCTRL_DMP_EN_BIT, bit)

    def reset_DMP(self):
        self.write_bit(C.MPU6050_RA_USER_CTRL,
                       C.MPU6050_USERCTRL_DMP_RESET_BIT, True)

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
        x_g_offset_TC = self.get_x_gyro_offset_TC()
        y_g_offset_TC = self.get_y_gyro_offset_TC()
        z_g_offset_TC = self.get_z_gyro_offset_TC()
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
        if self.write_prog_memory_block(C.dmpMemory, C.MPU6050_DMP_CODE_SIZE):

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
            if self.write_prog_dmp_configuration_set(C.dmpConfig,
                                                     C.MPU6050_DMP_CONFIG_SIZE):

                '''
                DEBUG_PRINTLN(F("Success! DMP configuration written and verified."));

                DEBUG_PRINTLN(F("Setting clock source to Z Gyro..."));
                seTClockSource(MPU6050_CLOCK_PLL_ZGYRO);
                '''
                self.set_clock_source(C.MPU6050_CLOCK_PLL_ZGYRO)
                '''
                DEBUG_PRINTLN(F("Setting DMP and FIFO_OFLOW interrupts enabled..."));
                setIntEnabled(0x12);
                '''
                self.set_int_enable(0x12)
                '''
                DEBUG_PRINTLN(F("Setting sample rate to 200Hz..."));
                setRate(4); // 1khz / (1 + 4) = 200 Hz
                '''
                self.set_rate(4)
                '''
                DEBUG_PRINTLN(F("Setting external frame sync to TEMP_OUT_L[0]..."));
                setExternalFrameSync(MPU6050_EXT_SYNC_TEMP_OUT_L);
                '''
                self.set_external_frame_sync(C.MPU6050_EXT_SYNC_TEMP_OUT_L)
                '''
                DEBUG_PRINTLN(F("Setting DLPF bandwidth to 42Hz..."));
                setDLPFMode(MPU6050_DLPF_BW_42);
                '''
                self.set_DLF_mode(C.MPU6050_DLPF_BW_42)
                '''
                DEBUG_PRINTLN(F("Setting gyro sensitivity to +/- 2000 deg/sec..."));
                setFullScaleGyroRange(MPU6050_GYRO_FS_2000);
                '''
                self.set_full_scale_gyro_range(C.MPU6050_GYRO_FS_2000)
                '''
                DEBUG_PRINTLN(F("Setting DMP configuration bytes (function unknown)..."));
                setDMPConfig1(0x03);
                setDMPConfig2(0x00);
                '''
                self.set_DMP_config_1(0x03)
                self.set_DMP_config_2(0x00)
                '''
                DEBUG_PRINTLN(F("Clearing OTP Bank flag..."));
                setOTPBankValid(false);
                '''
                set_OTP_bank_valid(0)
                '''
                DEBUG_PRINTLN(F("Setting X/Y/Z gyro offset TCs to previous values..."));
                setXGyroOffsetTC(xgOffsetTC);
                setYGyroOffsetTC(ygOffsetTC);
                setZGyroOffsetTC(zgOffsetTC);
                '''
                self.set_x_gyro_oggset_TC(x_g_offset_TC)
                self.set_y_gyro_oggset_TC(y_g_offset_TC)
                self.set_z_gyro_oggset_TC(z_g_offset_TC)
                '''
                //DEBUG_PRINTLN(F("Setting X/Y/Z gyro user offsets to zero..."));
                //setXGyroOffset(0);
                //setYGyroOffset(0);
                //setZGyroOffset(0);
                '''
                self.set_x_gyro_offset(0)
                self.set_y_gyro_offset(0)
                self.set_z_gyro_offset(0)
                '''
                DEBUG_PRINTLN(F("Writing final memory update 1/7 (function unknown)..."));
                uint8_t dmpUpdate[16], j;
                uint16_t pos = 0;
                for (j = 0; j < 4 || j < dmpUpdate[2] + 3; j++, pos++)
                {
                    dmpUpdate[j] = pgm_read_byte(&dmpUpdates[pos]);
                }
                writeMemoryBlock(dmpUpdate + 3, dmpUpdate[2], dmpUpdate[0], dmpUpdate[1]);
                '''
                pos = 0
                j = 0
                dmp_update = [0]*16
                while (j < 4) or (j < dmp_update[2]+3):
                    dmp_update[j] = C.dmpUpdates[pos]
                    pos += 1
                    j +=1
                # Write as block from pos 3
                self.write_memory_block(dmp_update[3:], dmp_update[2],
                                        dmp_update[0], dmp_update[1])
                '''
                DEBUG_PRINTLN(F("Writing final memory update 2/7 (function unknown)..."));
                for (j = 0; j < 4 || j < dmpUpdate[2] + 3; j++, pos++)
                {
                    dmpUpdate[j] = pgm_read_byte(&dmpUpdates[pos]);
                }
                writeMemoryBlock(dmpUpdate + 3, dmpUpdate[2], dmpUpdate[0], dmpUpdate[1]);
                '''
                j = 0
                while (j < 4) or (j < dmp_update[2]+3):
                    dmp_update[j] = C.dmpUpdates[pos]
                    pos += 1
                    j +=1
                # Write as block from pos 3
                self.write_memory_block(dmp_update[3:], dmp_update[2],
                                        dmp_update[0], dmp_update[1])
                '''
                DEBUG_PRINTLN(F("Resetting FIFO..."));
                resetFIFO();
                '''
                self.reset_FIFO()
                '''
                DEBUG_PRINTLN(F("Reading FIFO count..."));
                uint16_t fifoCount = getFIFOCount();
                '''
                FIFO_count = self.get_FIFO_count()
                '''
                DEBUG_PRINT(F("Current FIFO count="));
                DEBUG_PRINTLN(fifoCount);
                uint8_t fifoBuffer[128];
                getFIFOBytes(fifoBuffer, fifoCount);
                '''
                FIFO_buffer = [0]*128
                FIFO_buffer = self.get_FIFO_bytes(FIFO_buffer, FIFO_count)
                '''
                DEBUG_PRINTLN(F("Setting motion detection threshold to 2..."));
                setMotionDetectionThreshold(2);
                '''
                self.set_motion_detection_threshold(2)
                '''
                DEBUG_PRINTLN(F("Setting zero-motion detection threshold to 156..."));
                setZeroMotionDetectionThreshold(156);
                '''
                self.set_zero_motion_detection_threshold(156)
                '''
                DEBUG_PRINTLN(F("Setting motion detection duration to 80..."));
                setMotionDetectionDuration(80);
                '''
                self.set_motion_detection_duration(80)
                '''
                DEBUG_PRINTLN(F("Setting zero-motion detection duration to 0..."));
                setZeroMotionDetectionDuration(0);
                '''
                self.set_zero_motion_detection_duration(0)
                '''
                DEBUG_PRINTLN(F("Resetting FIFO..."));
                resetFIFO();
                '''
                self.reset_FIFO()
                '''
                DEBUG_PRINTLN(F("Enabling FIFO..."));
                setFIFOEnabled(true);
                '''
                self.set_FIFO_enabled(True)
                '''
                DEBUG_PRINTLN(F("Enabling DMP..."));
                setDMPEnabled(true);
                '''
                self.set_DMP_enabled(True)
                '''
                DEBUG_PRINTLN(F("Resetting DMP..."));
                resetDMP();
                '''
                self.reset_DMP()
                '''
                DEBUG_PRINTLN(F("Writing final memory update 3/7 (function unknown)..."));
                for (j = 0; j < 4 || j < dmpUpdate[2] + 3; j++, pos++)
                {
                    dmpUpdate[j] = pgm_read_byte(&dmpUpdates[pos]);
                }
                writeMemoryBlock(dmpUpdate + 3, dmpUpdate[2], dmpUpdate[0], dmpUpdate[1]);
                '''
                j = 0
                while (j < 4) or (j < dmp_update[2]+3):
                    dmp_update[j] = C.dmpUpdates[pos]
                    pos += 1
                    j +=1
                # Write as block from pos 3
                self.write_memory_block(dmp_update[3:], dmp_update[2],
                                        dmp_update[0], dmp_update[1])
                '''
                DEBUG_PRINTLN(F("Writing final memory update 4/7 (function unknown)..."));
                for (j = 0; j < 4 || j < dmpUpdate[2] + 3; j++, pos++) dmpUpdate[j] = pgm_read_byte(&dmpUpdates[pos]);
                writeMemoryBlock(dmpUpdate + 3, dmpUpdate[2], dmpUpdate[0], dmpUpdate[1]);
                '''
                j = 0
                while (j < 4) or (j < dmp_update[2]+3):
                    dmp_update[j] = C.dmpUpdates[pos]
                    pos += 1
                    j +=1
                # Write as block from pos 3
                self.write_memory_block(dmp_update[3:], dmp_update[2],
                                        dmp_update[0], dmp_update[1])
                '''
                DEBUG_PRINTLN(F("Writing final memory update 5/7 (function unknown)..."));
                for (j = 0; j < 4 || j < dmpUpdate[2] + 3; j++, pos++) dmpUpdate[j] = pgm_read_byte(&dmpUpdates[pos]);
                writeMemoryBlock(dmpUpdate + 3, dmpUpdate[2], dmpUpdate[0], dmpUpdate[1]);
                '''
                j = 0
                while (j < 4) or (j < dmp_update[2]+3):
                    dmp_update[j] = C.dmpUpdates[pos]
                    pos += 1
                    j +=1
                # Write as block from pos 3
                self.write_memory_block(dmp_update[3:], dmp_update[2],
                                        dmp_update[0], dmp_update[1])
                '''
                DEBUG_PRINTLN(F("Waiting for FIFO count > 2..."));
                while ((fifoCount = getFIFOCount()) < 3);
                '''
                while True:
                    FIFO_count = self.get_FIFO_count()
                    if FIFO_count > 2:
                        break
                '''
                DEBUG_PRINT(F("Current FIFO count="));
                DEBUG_PRINTLN(fifoCount);
                DEBUG_PRINTLN(F("Reading FIFO data..."));
                getFIFOBytes(fifoBuffer, fifoCount);
                '''
                FIFO_buffer = self.get_FIFO_bytes(FIFO_buffer, FIFO_count)
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
