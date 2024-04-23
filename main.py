#!/usr/bin/env python
import cmath
from math import degrees
import pygame
import os
from plane import PlaneState, PlaneHW

os.environ['SDL_VIDEO_WINDOW_POS'] = f"{1440},{0}"
pygame.init()

W, H = 2500, 1400
screen = pygame.display.set_mode((W, H), pygame.NOFRAME)
clock = pygame.time.Clock()

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
font = pygame.font.Font(None, 36)

H_0 = 1000
plane = PlaneState((0, H_0, 10, 0, 0))
def drawPlane():
    # rectangle for now
    W2 = W//2
    H2 = H//2
    offset = 200
    pitch = plane.pitch
    offset *= cmath.exp(1j * pitch)
    
    # draw plane
    pygame.draw.line(screen, BLUE, (W2-+offset.real/2, H2+offset.imag/2), (W2+offset.real/2, H2-offset.imag/2), 10)

    # draw airspeed
    pygame.draw.line(screen, RED, (W2, H2), (W2+plane.tas_x*10, H2-plane.tas_y*10), 1)

    speed = font.render(f" Vx: {plane.vx:.1f}, Vy: {plane.vy:.2f}, glide: {-plane.vx/plane.vy:.2f}", True, WHITE)
    screen.blit(speed, (10, 10))

    wspeed = font.render(f" Wx: {plane.windGen.getWind(0)[0]:.1f}, Wy: {plane.windGen.getWind(0)[1]:.2f}", True, WHITE)
    screen.blit(wspeed, (10, 40))

    pitch = font.render(f"pitch: {degrees(plane.pitch):.2f}, alpha: {degrees(plane.alpha):.2f}", True, WHITE)
    screen.blit(pitch, (10, 70))

    pos = font.render(f"x: {plane.x:.0f}, y: {plane.y:.0f}", True, WHITE)
    screen.blit(pos, (10, 100))

    time = font.render(f"t: {plane.t:.2f}", True, WHITE)
    screen.blit(time, (10, 130))

    pygame.draw.circle(screen, WHITE, (150, H-150), 120, width=5)
    pygame.draw.circle(screen, RED, (150, H-150), 5)

    pygame.draw.line(screen, WHITE, (150, H-150), (150-(plane.tas_x-plane.vx)*20, H-150+(plane.tas_y-plane.vy)*20), 2)

def handleInputs():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_DOWN]:
        plane.update(0.02, 1)
    elif keys[pygame.K_UP]:
        plane.update(0.02, -1)
    else:
        plane.update(0.02, 0)

while True:
    screen.fill(BLACK)
    clock.tick(50)
    if any(event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q) for event in pygame.event.get()):
        break

    try:
        handleInputs()
    except AssertionError:
        print("Crash!")
        break
    drawPlane()
    pygame.display.flip()

print("Achieved time:", plane.t)
print("Distance", plane.x)
dh = H_0 - plane.y # height lost

print(f"Glide ratio: {plane.x/dh:.2f}")
