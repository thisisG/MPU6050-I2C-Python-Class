__author__ = 'Geir'

from MPU6050 import MPU6050
from time import clock

mpu = mpu = MPU6050(0x68, -5489, -1441, 1305, -2, -72, -5, True)

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
start_time = clock()
#FIFO_list = list()
while count < 1000:
    FIFO_count = mpu.get_FIFO_count()
    #FIFO_list.append(FIFO_count)
    mpu_int_status = mpu.get_int_status()
    while FIFO_count < packet_size:
        FIFO_count = mpu.get_FIFO_count()
    FIFO_buffer = mpu.get_FIFO_bytes(FIFO_buffer,packet_size)
    if FIFO_count == 1024:
        mpu.reset_FIFO()
        overflow += 1
        print('count: ' + str(count) + ' overflow: ' + str(overflow))
    else:
        no_overflow += 1
    count += 1
end_time = clock()
delta_time = end_time - start_time
print('overflows: ' + str(overflow))
print('no_overflows: ' + str(no_overflow))
print('delta time = ' + str(delta_time))
#print(FIFO_list)
