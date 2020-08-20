import os
import pygame
import math

from math import sin, radians, degrees
from pygame.math import Vector2
from sympy import Point, Polygon, Line

PPU = 32
MAX_DISTANCE = 100


class Car:

    def __init__(self, x, y, angle=0.0, length=4, max_steering=30, max_acceleration=2):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "mini_car.png")

        self.car_image = pygame.image.load(image_path)
        self.position = Vector2(x / PPU, y / PPU)
        self.real_position = Vector2(x, y)

        self.velocity = Vector2(0.0, 0.0)
        self.angle = angle
        self.length = length
        self.max_acceleration = max_acceleration
        self.max_steering = max_steering
        self.max_velocity = 20

        self.acceleration = 0.0
        self.steering = 0.0
        self.free_deceleration = 2.0
        self.break_deceleration = 7.0

        self.rotated = pygame.transform.rotate(self.car_image, self.angle)
        self.center_position = Vector2(
            self.real_position.x + self.car_image.get_rect().width / 2,
            self.real_position.y + self.car_image.get_rect().height / 2)

        # line
        self.point_minus_45_angle = (0.0, 0.0)
        self.point_zero_angle = (0.0, 0.0)
        self.point_plus_45_angle = (0.0, 0.0)

    def update(self, dt):
        self.velocity += (self.acceleration * dt, 0)
        self.velocity.x = max(-self.max_velocity,
                              min(self.velocity.x, self.max_velocity))

        if self.steering:
            turning_radius = self.length / sin(radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius
        else:
            angular_velocity = 0

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += degrees(angular_velocity) * dt

        # Make car rect
        self.rotated = pygame.transform.rotate(self.car_image, self.angle)
        rotated_rect = self.rotated.get_rect()

        # Calculate position
        self.real_position = self.position * PPU
        self.center_position.x = self.real_position.x + rotated_rect.width / 2
        self.center_position.y = self.real_position.y + rotated_rect.height / 2

        # Calulate angle
        # self.calculate_angle_distance()

    # def calculate_angle_distance(self):
    #     radian_zero = math.radians(-self.angle)
    #     radian_minus_45 = math.radians(-(self.angle + 45))
    #     radian_plus_45 = math.radians(-(self.angle - 45))
    #
    #     self.point_zero_angle = self.calculate_angle_point_with_map(
    #         self.center_position, radian_zero)
    #     self.point_minus_45_angle = self.calculate_angle_point_with_map(
    #         self.center_position, radian_minus_45)
    #     self.point_plus_45_angle = self.calculate_angle_point_with_map(
    #         self.center_position, radian_plus_45)
    #
    # def calculate_angle_point_with_map(self, start_point, radian):
    #     # radian에 존재하는 point b 의 위치를 구한다.
    #     b = (start_point[0] + (MAX_DISTANCE * math.cos(radian)),
    #          start_point[1] + (MAX_DISTANCE * math.sin(radian)))
    #
    #     return b
