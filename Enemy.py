import math


class Enemy:
    def __init__(self, images, screen_size, player, enemies, bullets, speed, client_number=None, generate_image=None):
        self.player, self.enemies, self.bullets = player, enemies, bullets

        self.x_size, self.y_size = 40, 40

        if 'enemy' not in images[client_number]:
            generate_image(client_number=client_number, name='enemy', size=(self.x_size, self.y_size), shape='circle', color=(255, 0, 0))

        self.x, self.y = (screen_size[0] - self.x_size) / 2, -50

        self.speed = speed

    def update_position(self):
        delta_x = self.x - self.player.x
        delta_y = self.y - self.player.y

        distance = math.sqrt(delta_x ** 2 + delta_y ** 2)

        if distance >= self.player.x_size:  # this works only if player is a circles
            delta_x /= distance
            delta_y /= distance

            self.x -= delta_x * self.speed
            self.y -= delta_y * self.speed

    def die_check(self):
        for bullet in self.bullets:
            if bullet.x >= self.x and (bullet.x + bullet.x_size) <= (self.x + self.x_size):
                if bullet.y >= self.y and (bullet.y + bullet.y_size) <= (self.y + self.y_size):
                    self.enemies.remove(self)
                    self.bullets.remove(bullet)
                    return True
