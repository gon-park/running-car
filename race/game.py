import os
import pygame
import random
import math

from race import car as c

# Color
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 180)
RED = (255, 0, 0)

# Action State
RUN = 3
EXIT = 4

# Track
GUIDE_WIDHT = 1

# Car
START_POINT = (30, 330)
MAX_BEAM_LEN = 100


class Game:
    def __init__(self, width, height, ticks=60, auto=True):
        pygame.init()
        pygame.display.set_caption("Car tutorial")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        map_path = os.path.join(current_dir, "simple_map.png")
        self.map_surface = pygame.image.load(map_path)
        self.map_mask = pygame.mask.from_surface(self.map_surface)

        mask_fx = pygame.mask.from_surface(pygame.transform.flip(self.map_surface, True, False))
        mask_fy = pygame.mask.from_surface(pygame.transform.flip(self.map_surface, False, True))
        mask_fx_fy = pygame.mask.from_surface(pygame.transform.flip(self.map_surface, True, True))
        self.flipped_masks = [[self.map_mask, mask_fy], [mask_fx, mask_fx_fy]]

        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.auto = auto
        self.action_status = RUN
        self.car = c.Car(*START_POINT)
        self.dt = 0
        self.ticks = ticks
        self.clock = pygame.time.Clock()

        self.beam_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

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
            self.draw_screen()

            self.clock.tick(self.ticks)

        pygame.quit()

    def process_moving_car(self):
        if self.auto is True:
            # Car Acceleration
            self.car.acceleration = random.randrange(int(-self.car.max_acceleration / 4),
                                                     int(self.car.max_acceleration))
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
                        math.copysign(self.car.break_deceleration,
                                 self.car.velocity.x)
                else:
                    self.car.acceleration = -self.car.velocity.x / self.dt
            else:
                if abs(self.car.velocity.x) > self.dt * self.car.free_deceleration:
                    self.car.acceleration = - \
                        math.copysign(self.car.free_deceleration,
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

        # print(f'car.accel: {self.car.acceleration}')
        # print(f'car.steering: {self.car.steering}')

    def check_and_reset_position(self):
        is_reset = False

        if self.car.real_position.x > self.width:
            # car.position.x = 0.0
            self.car.__init__(*START_POINT, angle=random.randrange(0, 360))
            is_reset = True
        elif self.car.position.x < 0.0:
            # car.position.x = float(self.width / ppu)
            self.car.__init__(*START_POINT, angle=random.randrange(0, 360))
            is_reset = True

        if self.car.real_position.y > self.height:
            # car.position.y = 0.0
            self.car.__init__(*START_POINT, angle=random.randrange(0, 360))
            is_reset = True
        elif self.car.position.y < 0.0:
            # car.position.y = float(self.height / ppu)
            self.car.__init__(*START_POINT, angle=random.randrange(0, 360))
            is_reset = True

        return is_reset

    def draw_screen(self, background=BLACK):
        # Draw background
        self.screen.fill(background)

        # draw track
        self.screen.blit(self.map_surface, self.map_surface.get_rect())

        # Draw car
        self.screen.blit(self.car.rotated, self.car.real_position)

        # Draw line
        self.draw_beam(self.car.center_position, self.car.angle)
        self.draw_beam(self.car.center_position, self.car.angle + 45)
        self.draw_beam(self.car.center_position, self.car.angle - 45)

        pygame.display.update()

    def draw_beam(self, start_position, angle):
        # c = math.cos(math.radians(angle))
        # s = math.sin(math.radians(angle))

        # flip_x = c < 0
        # flip_y = s < 0
        # filpped_mask = self.flipped_masks[flip_x][flip_y]

        x_dest = start_position.x + MAX_BEAM_LEN * math.cos(-math.radians(angle))
        y_dest = start_position.y + MAX_BEAM_LEN * math.sin(-math.radians(angle))

        self.beam_surface.fill((0, 0, 0, 0))

        # draw a single beam to the beam surface based on computed final point
        pygame.draw.line(self.beam_surface, BLUE, start_position, (x_dest, y_dest))
        beam_mask = pygame.mask.from_surface(self.beam_surface)

        # find overlap between "global mask" and current beam mask
        # offset_x = self.width - start_position.x if flip_x else start_position.x
        # offset_y = self.height - start_position.y if flip_y else start_position.y
        hit = self.map_mask.overlap(beam_mask, (0, 0))
        if hit is not None:
            # hx = self.width - start_position.x if flip_x else start_position.x
            # hy = self.height - start_position.y if flip_y else start_position.y
            # hit_pos = (hx, hy)
            pygame.draw.line(self.screen, WHITE, start_position, hit)
            pygame.draw.circle(self.screen, RED, hit, 3)
            # pygame.draw.circle(self.screen, RED, hit_pos, 3)
        else:
            pygame.draw.line(self.screen, WHITE, start_position, (x_dest, y_dest))
