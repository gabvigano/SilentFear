import math
import random


class Player:
    def __init__(self, client_number, generate_image, screen_size):
        random.seed(client_number + 3)  # set seed for the pseudo random color generator (+3 because the colors for the first seeds suck)

        self.enemies = []
        self.enemy_bullets = []

        self.x_size, self.y_size = 40, 40
        self.screen_size = screen_size
        self.x, self.y, self.angle, self.health, self.reload_enemy_damage = None, None, None, None, None

        color = tuple(random.choices(range(256), k=3))

        generate_image(client_number=client_number, name='player', size=(self.x_size, self.y_size), shape='circle', color=color)

        self.reset()

    def reset(self):
        pos_clip = 30
        self.x, self.y = (random.random() * (self.screen_size[0] - pos_clip * 2) + pos_clip), random.random() * (self.screen_size[1] - pos_clip * 2) + pos_clip
        self.angle = random.randint(-180, 180)
        self.health = 10
        self.reload_enemy_damage = 0

    def move(self, speed):
        angle_radians = math.radians(self.angle - 90)

        self.x += speed * math.cos(angle_radians)
        self.y += speed * math.sin(angle_radians)

        # limit movement inside the screen
        self.x = min((self.screen_size[0] - self.x_size), max(0, self.x))
        self.y = min((self.screen_size[1] - self.y_size), max(0, self.y))

    def health_check(self):
        if self.health <= 0:
            return True

        for bullet in self.enemy_bullets:
            if bullet.x >= self.x and (bullet.x + bullet.x_size) <= (self.x + self.x_size):
                if bullet.y >= self.y and (bullet.y + bullet.y_size) <= (self.y + self.y_size):
                    self.health -= 1
                    if self.health <= 0:
                        return True

        for enemy in self.enemies:
            distance = math.sqrt((self.x - enemy.x) ** 2 + (self.y - enemy.y) ** 2)

            if distance <= self.x_size:
                if self.reload_enemy_damage <= 50:
                    self.reload_enemy_damage += 1
                else:
                    self.health -= 1
                    self.reload_enemy_damage = 0
                    if self.health <= 0:
                        return True
