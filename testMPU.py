__author__ = 'Geir'

from MPU6050 import MPU6050

mpu = mpu = MPU6050(0x68, -5489, -1441, 1305, -2, -72, -5, True)
#mpu = MPU6050(0x68, -5489)

#mpu = MPU6050(0x68, 0, 0, 0, 0, 0, 0)
#mpu = MPU6050()
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
FIFO_list = list()
while count < 100:
    FIFO_count = mpu.get_FIFO_count()
    FIFO_list.append(FIFO_count)
    mpu_int_status = mpu.get_int_status()
    #print('Fifo_count start loop: ' + str(FIFO_count))
    #print('int status: ' + hex(mpu_int_status))
    while FIFO_count < packet_size:
        FIFO_count = mpu.get_FIFO_count()
        #print('fifo count: ' + str(FIFO_count))
    FIFO_buffer = mpu.get_FIFO_bytes(FIFO_buffer,packet_size)
    #print(FIFO_buffer)
    #quat = mpu.DMP_get_quaternion(FIFO_buffer)
    #accel = mpu.DMP_get_acceleration_int16(FIFO_buffer)
    #grav = mpu.DMP_get_gravity(quat)
    #lin_accel = mpu.DMP_get_linear_accel_int16(accel, grav)
    #print(accel.x)
    #print(accel.y)
    #print(accel.z)
    count += 1
    #print(mpu.get_acceleration())
    #print(mpu.get_rotation())
    if FIFO_count == 1024:
        mpu.reset_FIFO()
    overflow += 1
    print('count: ' + str(count) + ' overflow: ' + str(overflow))
print('overflows: ' + str(overflow))
print(FIFO_list)