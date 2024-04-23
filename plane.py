from typing import Tuple
from math import pi, sin, cos, atan


def clamp(x, lo, hi):
    return max(lo, min(x, hi))

class CONST:
    g = 9.81
    rho = 1.225

class PlaneHW:
    def __init__(self):
        self.pitchControlRate = 0.1 # radians per second at full command
        self.mass = 1.0
        self.area = 0.5

    def getAeroData(self, state:Tuple[float, float, float, float, float]):
        x, y, vx, vy, pitch, alpha = state
        cl = clamp(2 * pi * alpha, -1, 1)
        cd = clamp(0.02 + 0.1 * alpha**2, -1, 1)
        return {"cl":cl, "cd":cd}


class PlaneState:
    def __init__(self, planeHw:PlaneHW, state:Tuple[float, float, float, float, float]):
        self.hw = planeHw
        self.x = state[0]
        self.y = state[1]
        self.vx = state[2]
        self.vy = state[3]
        self.pitch = state[4]
        self.alpha = None
        self.t = 0

        self.checkReasonable()
    
    def checkReasonable(self):
        assert self.x >= 0
        assert self.y >= 0
        assert self.vx > 0
        assert -pi/2 < self.pitch < pi/2

    def update(self, dt:float, cmd:float):
        cmd = clamp(cmd, -1, 1)
        self.pitch += cmd * dt * self.hw.pitchControlRate
        self.alpha = self.pitch - atan(self.vy / self.vx)
        aeroData = self.hw.getAeroData((self.x, self.y, self.vx, self.vy, self.pitch, self.alpha))
        cl, cd = aeroData["cl"], aeroData["cd"]
        v = (self.vx**2 + self.vy**2)**0.5
        lift = 0.5 * self.hw.area * cl * v**2 * CONST.rho
        drag = 0.5 * self.hw.area * cd * v**2 * CONST.rho
        print(cl, cd, cl/cd)
        ax = (-drag * cos(self.pitch) - lift * sin(self.pitch)) / self.hw.mass
        ay = (-drag * sin(self.pitch) + lift * cos(self.pitch)) / self.hw.mass - CONST.g

        self.vx += ax * dt
        self.vy += ay * dt

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.t += dt
        self.checkReasonable()

