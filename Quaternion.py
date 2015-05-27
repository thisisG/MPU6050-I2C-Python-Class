__author__ = 'Geir Istad'
"""
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
I2Cdev library collection - 3D math helper
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
"""
from math import sqrt


class Quaternion:
    w = 0.0
    x = 0.0
    y = 0.0
    z = 0.0

    def __init__(self, a_w=1.0, a_x=0.0, a_y=0.0, a_z=0.0):
        self.w = a_w
        self.x = a_x
        self.y = a_y
        self.z = a_z

    def get_product(self, a_q):
        result = Quaternion(
            self.w * a_q.w - self.x * a_q.x - self.y * a_q.y - self.z * a_q.z,
            self.w * a_q.x + self.x * a_q.w + self.y * a_q.z - self.z * a_q.y,
            self.w * a_q.y - self.x * a_q.z + self.y * a_q.w + self.z * a_q.x,
            self.w * a_q.z + self.x * a_q.y - self.y * a_q.x + self.z * a_q.w)
        return result

    def get_conjugate(self):
        result = Quaternion(self.w, -self.x, -self.y, -self.z)
        return result

    def get_magnitude(self):
        return sqrt(self.w * self.w + self.x * self.x + self.y * self.y +
                    self.z * self.z)

    def normalize(self):
        m = self.get_magnitude()
        self.w = self.w / m
        self.x = self.x / m
        self.y = self.y / m
        self.z = self.z / m

    def get_normalized(self):
        result = Quaternion(self.w, self.x, self.y, self.z)
        result.normalize()
        return result
