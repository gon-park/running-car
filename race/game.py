import os
import pygame
import random
import math

from race import car as c
from math import sin, radians, degrees, copysign

# Color
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 180)
RED = (255, 0, 0)

# Action State
BUILD1 = 1
BUILD2 = 2
RUN = 3
EXIT = 4

# Track
ALLOWED_DISTANCE = 50
TRACK_WIDHT = 3


class Game:
    def __init__(self, width, height, ticks=30, auto=True):
        pygame.init()
        pygame.display.set_caption("Car tutorial")

        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.auto = auto
        self.action_status = BUILD1
        self.car = c.Car(self.width / 10, self.height / 10)
        self.dt = 0
        self.ticks = ticks
        self.clock = pygame.time.Clock()
        self.track_position = ([], [])

    def make_track(self):
        self.draw_screen()
        mousedown = False
        distance = 10000
        track_index = 0

        while self.action_status is BUILD1 or self.action_status is BUILD2:
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                self.action_status = EXIT

            if event.type == pygame.MOUSEBUTTONDOWN:
                mousedown = True

            elif event.type == pygame.MOUSEBUTTONUP:
                mousedown = False
                print(f'Map draw end position: {event.pos}')
                distance = math.sqrt(
                    ((self.track_position[track_index][0][0]-event.pos[0])**2)+((self.track_position[track_index][0][1]-event.pos[1])**2))
                print(f'Distance between start and end: {distance}')

                if distance < ALLOWED_DISTANCE:
                    if track_index == 0:
                        track_index = 1
                    else:
                        self.action_status = RUN
                        break

                self.track_position[track_index].clear()
                self.draw_screen()
                if track_index == 1:
                    pygame.draw.lines(self.screen, RED, False,
                                      self.track_position[0], TRACK_WIDHT)
                    pygame.draw.line(
                        self.screen, RED, self.track_position[0][0], self.track_position[0][-1], TRACK_WIDHT)
                distance = 10000

            elif event.type == pygame.MOUSEMOTION:
                if mousedown:
                    if len(self.track_position[track_index]) == 0:
                        print(f'Map draw start position: {event.pos}')
                    self.track_position[track_index].append(event.pos)

                    if len(self.track_position[track_index]) > 1:
                        if math.sqrt(((self.track_position[track_index][0][0]-event.pos[0])**2)+((self.track_position[track_index][0][1]-event.pos[1])**2)) < ALLOWED_DISTANCE:
                            pygame.draw.line(
                                self.screen, BLUE, self.track_position[track_index][-2], self.track_position[track_index][-1], TRACK_WIDHT)
                        else:
                            pygame.draw.line(
                                self.screen, RED, self.track_position[track_index][-2], self.track_position[track_index][-1], TRACK_WIDHT)

            pygame.display.update()

    def run_car(self):
        while self.action_status is RUN:
            self.dt = self.clock.get_time() / 200

            # Event queue
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                self.action_status = EXIT

            # Process moving
            self.process_moving_car()

            # Car check position
            self.check_and_reset_position()

            # Car update
            self.car.update(self.dt)

            # Draw
            self.draw_screen(car=self.car, track=self.track_position)

            self.clock.tick(self.ticks)

        pygame.quit()

    def process_moving_car(self):
        if self.auto is True:
            # Car Acceleration
            self.car.acceleration = random.randrange(int(-self.car.max_acceleration / 2),
                                                     self.car.max_acceleration)
            # Car Steering
            self.car.steering += random.randrange(-self.car.max_steering,
                                                  self.car.max_steering) * self.dt

        else:
            # User input
            pressed = pygame.key.get_pressed()

            # Car Acceleration
            if pressed[pygame.K_UP]:
                if self.car.velocity.x < 0:
                    self.car.acceleration = self.car.break_deceleration
                else:
                    self.car.acceleration += 1 * self.dt
            elif pressed[pygame.K_DOWN]:
                if self.car.velocity.x > 0:
                    self.car.acceleration = -self.car.break_deceleration
                else:
                    self.car.acceleration -= 1 * self.dt
            elif pressed[pygame.K_SPACE]:
                if abs(self.car.velocity.x) > self.dt * self.car.break_deceleration:
                    self.car.acceleration = - \
                        copysign(self.car.break_deceleration,
                                 self.car.velocity.x)
                else:
                    self.car.acceleration = -self.car.velocity.x / self.dt
            else:
                if abs(self.car.velocity.x) > self.dt * self.car.free_deceleration:
                    self.car.acceleration = - \
                        copysign(self.car.free_deceleration,
                                 self.car.velocity.x)
                else:
                    if self.dt != 0:
                        self.car.acceleration = -self.car.velocity.x / self.dt

            # Car Steering
            if pressed[pygame.K_RIGHT]:
                self.car.steering -= 30 * self.dt
            elif pressed[pygame.K_LEFT]:
                self.car.steering += 30 * self.dt
            else:
                self.car.steering = 0

        self.car.acceleration = max(-self.car.max_acceleration,
                                    min(self.car.acceleration, self.car.max_acceleration))
        self.car.steering = max(-self.car.max_steering,
                                min(self.car.steering, self.car.max_steering))

        print(f'car.accel: {self.car.acceleration}')
        print(f'car.steering: {self.car.steering}')

    def check_and_reset_position(self):
        is_reset = False

        if self.car.real_position.x > self.width:
            # car.position.x = 0.0
            self.car.__init__(self.width / 10, self.height /
                              10, angle=random.randrange(0, 360))
            is_reset = True
        elif self.car.position.x < 0.0:
            # car.position.x = float(self.width / ppu)
            self.car.__init__(self.width / 10, self.height /
                              10, angle=random.randrange(0, 360))
            is_reset = True

        if self.car.real_position.y > self.height:
            # car.position.y = 0.0
            self.car.__init__(self.width / 10, self.height /
                              10, angle=random.randrange(0, 360))
            is_reset = True
        elif self.car.position.y < 0.0:
            # car.position.y = float(self.height / ppu)
            self.car.__init__(self.width / 10, self.height /
                              10, angle=random.randrange(0, 360))
            is_reset = True

        return is_reset

    def draw_screen(self, background=BLACK, car=None, track=None):
        # Draw background
        self.screen.fill(background)

        # draw track
        if track:
            pygame.draw.lines(self.screen, RED, False, track[0], TRACK_WIDHT)
            pygame.draw.lines(self.screen, BLUE, False, track[1], TRACK_WIDHT)
            pygame.draw.line(
                self.screen, RED, track[0][0], track[0][-1], TRACK_WIDHT)
            pygame.draw.line(
                self.screen, BLUE, track[1][0], track[1][-1], TRACK_WIDHT)

        # if car:
        # Draw car
        self.screen.blit(self.car.rotated, self.car.real_position)

        # Draw middle circle
        print(f'position: {self.car.center_position}')
        pygame.draw.circle(self.screen, RED, self.car.center_position, 4, 0)

        pygame.display.flip()
