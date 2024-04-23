from typing import Tuple
from math import pi, sin, cos, atan

def clamp(x, lo, hi):
    return max(lo, min(x, hi))

class CONST:
    g = 9.81
    rho = 1.225

class PlaneHW:
    def __init__(self):
        self.pitchControlRate = 0.5 # radians per second at full command
        self.mass = 1.0
        self.area = 0.5

    def getAeroData(self, state:Tuple[float, float, float, float, float]):
        x, y, vx, vy, pitch, alpha = state
        cl = clamp(2 * pi * alpha, -1.5, 1.5)
        cd = 0.02 + 0.1 * pi * abs(alpha)
        return {"cl":cl, "cd":cd}


class PlaneState:
    def __init__(self, planeHw:PlaneHW, state:Tuple[float, float, float, float, float]):
        self.hw = planeHw
        self.x = state[0]
        self.y = state[1]
        self.vx = state[2]
        self.vy = state[3]
        self.pitch = state[4]
        self.t = 0

        self.checkReasonable()
    
    def checkReasonable(self):
        assert self.x >= 0
        assert self.y >= 0
        assert self.vx > 0
        assert -pi/2 < self.pitch < pi/2

    @property
    def alpha(self):
        return self.pitch - atan(self.vy / self.vx)

    def update(self, dt:float, cmd:float):
        cmd = clamp(cmd, -1, 1)
        self.pitch += cmd * dt * self.hw.pitchControlRate
        aeroData = self.hw.getAeroData((self.x, self.y, self.vx, self.vy, self.pitch, self.alpha))
        cl, cd = aeroData["cl"], aeroData["cd"]
        v = (self.vx**2 + self.vy**2)**0.5
        lift = 0.5 * self.hw.area * cl * v**2 * CONST.rho
        drag = 0.5 * self.hw.area * cd * v**2 * CONST.rho
        print(f"lift: {cl:.2f}, drag: {cd:.3f}, L/D: {lift/drag:.2f}")

        drag_dir = -self.vx-self.vy*1j; drag_dir /= abs(drag_dir)
        lift_dir = drag_dir * -1j # rotate 90 degrees right
        lift:complex = lift_dir * lift
        drag:complex = drag_dir * drag
        fx = drag.real + lift.real
        fy = drag.imag + lift.imag - CONST.g * self.hw.mass

        # update components
        self.vx += fx/self.hw.mass * dt
        self.vy += fy/self.hw.mass * dt

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.t += dt
        self.checkReasonable()

