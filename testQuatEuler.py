__author__ = 'Geir'

from MPU6050 import MPU6050

mpu = mpu = MPU6050(1, 0x68, -5489, -1441, 1305, -2, -72, -5, True)

mpu.dmp_initialize()
mpu.set_DMP_enabled(True)
mpu_int_status = mpu.get_int_status()
print(hex(mpu_int_status))

packet_size = mpu.DMP_get_FIFO_packet_size()
print(packet_size)
FIFO_count = mpu.get_FIFO_count()
print(FIFO_count)

count = 0
FIFO_buffer = [0]*64

FIFO_count_list = list()
while count < 10000:
    FIFO_count = mpu.get_FIFO_count()
    mpu_int_status = mpu.get_int_status()
    while FIFO_count < packet_size:
        FIFO_count = mpu.get_FIFO_count()
    if FIFO_count == 1024:
        mpu.reset_FIFO()
        print('overflow!')
    else:
        FIFO_buffer = mpu.get_FIFO_bytes(FIFO_buffer, packet_size)
        accel = mpu.DMP_get_acceleration_int16(FIFO_buffer)
        quat = mpu.DMP_get_quaternion_int16(FIFO_buffer)
        grav = mpu.DMP_get_gravity(quat)
        yaw_pitch_roll = mpu.DMP_get_euler_yaw_pitch_roll(quat, grav)
        if count % 100 == 0:
            print('yaw: ' + str(yaw_pitch_roll.x))
            print('pitch: ' + str(yaw_pitch_roll.y))
            print('roll: ' + str(yaw_pitch_roll.z))
        count += 1
