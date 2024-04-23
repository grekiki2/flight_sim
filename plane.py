from typing import Tuple
from math import pi, sin, cos, atan, degrees
import numpy as np

def clamp(x, lo, hi):
    return max(lo, min(x, hi))

class CONST:
    g = 9.81
    rho = 1.225

class PlaneHW:
    def __init__(self):
        self.pitchControlRate = 0.5
        self.mass = 1.1
        self.area = 0.29
        self.characterstic_len = 0.18
        self.AR = 8 # includes efficiency factor
        self.cl_x = [-20, -15, 0, 15, 20] # degrees as on airfoiltools
        self.cl_y = [0, -1, 0.4, 1.5, 0]

        self.cd_x = [-20, -15, -10, -5, 0, 5, 10, 15, 20] # degrees as on airfoiltools
        self.cd_y = [0.1, 0.03, 0.01, 0.008, 0.005, 0.008, 0.015, 0.035, 0.1]

    def getAeroData(self, state:Tuple[float, float, float, float, float]):
        x, y, vx, vy, pitch, alpha = state
        # re = (vx**2+vy**2)**0.5 * self.characterstic_len / 1.4e-5
        # print(f"kRe: {re/1000:.0f}")
        alpha_deg = degrees(alpha)
        cl = np.interp(alpha_deg, self.cl_x, self.cl_y)
        cd_p = np.interp(alpha_deg, self.cd_x, self.cd_y)
        cd_i = + cl**2 / (pi * self.AR)
        
        print(f"lift: {cl:.2f}, drag: {cd_p:.3f} + {cd_i:.3f}, LD: {cl/(cd_p+cd_i):.1f}")

        return {"cl":cl, "cd":cd_p+cd_i}


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

