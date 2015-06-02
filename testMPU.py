__author__ = 'Geir'

from MPU6050 import MPU6050
from time import clock

mpu = mpu = MPU6050(1, 0x68, -5489, -1441, 1305, -2, -72, -5, True)

mpu.dmp_initialize()
mpu.set_DMP_enabled(True)
mpu_int_status = mpu.get_int_status()
print(hex(mpu_int_status))
while False:
    print(mpu.get_acceleration())
    print(mpu.get_rotation())

packet_size = mpu.DMP_get_FIFO_packet_size()
print(packet_size)
FIFO_count = mpu.get_FIFO_count()
print(FIFO_count)

count = 0
FIFO_buffer = [0]*64
overflow = 0
no_overflow = 0
crazy_high_number = 0
start_time = clock()
# FIFO_list = list()
FIFO_count_list = list()
while count < 10000:
    FIFO_count = mpu.get_FIFO_count()
    # FIFO_list.append(FIFO_count)
    mpu_int_status = mpu.get_int_status()
    FIFO_count_list.append(mpu_int_status)
    while FIFO_count < packet_size:
        FIFO_count = mpu.get_FIFO_count()
    count += 1
    if FIFO_count == 1024:
        mpu.reset_FIFO()
        overflow += 1
        print('count: ' + str(count) + ' overflow: ' + str(overflow))
    else:
        no_overflow += 1
        FIFO_buffer = mpu.get_FIFO_bytes(FIFO_buffer, packet_size)
        # print(FIFO_buffer)
        accel = mpu.DMP_get_acceleration_int16(FIFO_buffer)
        # print(str(accel.x) + " " + str(accel.y) + " " + str(accel.z))
        if (accel.x > 12000) or (accel.x < -12000) or (accel.y > 12000) or \
                (accel.y < -12000) or (accel.z > 12000) or (accel.z < -12000):
            crazy_high += 1

end_time = clock()
delta_time = end_time - start_time
FIFO_sum = 0
FIFO_max = 0
FIFO_min = 1025
for n in FIFO_count_list:
    FIFO_sum += n
    if n < FIFO_min:
        FIFO_min = n
    if n > FIFO_max:
        FIFO_max = n
FIFO_average = FIFO_sum / len(FIFO_count_list)
print('FIFO_average: ' + str(FIFO_average))
print('FIFO_min: ' + str(FIFO_min))
print('FIFO_max: ' + str(FIFO_max))
print('overflows: ' + str(overflow))
print('no_overflows: ' + str(no_overflow))
print('delta time = ' + str(delta_time))
# print(FIFO_list)
