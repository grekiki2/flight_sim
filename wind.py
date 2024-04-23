import numpy as np
import random

class WindGen:
    def __init__(self):
        self.wind_x = 0
        self.wind_y = 0
        self.t = 0
    
    def getWind(self, dt:float):
        self.t += dt
        if self.t<2:
            return 0, 0
        return 10, 0

def randomRot(x, y, angleLim):
    angle = random.uniform(-angleLim, angleLim)
    angle = np.deg2rad(angle)
    return x*np.cos(angle)-y*np.sin(angle), x*np.sin(angle)+y*np.cos(angle)

class RWalkWindGen:
    def __init__(self):
        self.c_x = 0
        self.c_y = 0
        self.vc_x = -1
        self.vc_y = 1
        self.dx = 0
        self.dy = 0

        self.stepVC = 2
        self.limC = 5
        self.stepVD = 0.1
        self.springD = 0.01
        

    def getWind(self, dt:float):
        self.vc_x, self.vc_y = randomRot(self.vc_x, self.vc_y, self.stepVC)

        self.dx += random.uniform(-self.stepVD, self.stepVD)
        self.dy += random.uniform(-self.stepVD, self.stepVD)
        d = (self.dx**2 + self.dy**2)**0.5
        self.dx -= self.springD * self.dx * d
        self.dy -= self.springD * self.dy * d

        self.c_x += self.vc_x * dt
        self.c_y += self.vc_y * dt

        if self.c_x > self.limC:
            self.vc_x = -abs(self.vc_x)
        if self.c_x < -self.limC:
            self.vc_x = abs(self.vc_x)
        if self.c_y > self.limC:
            self.vc_y = -abs(self.vc_y)
        if self.c_y < -self.limC:
            self.vc_y = abs(self.vc_y)

        return self.c_x+self.dx, self.c_y+self.dy
        # return self.dx, self.dy
        # return self.vc_x, self.vc_y