import math


class Bullet:
    def __init__(self, images, screen_size, gun, bullets, speed, client_number=None, generate_image=None):
        self.screen_size, self.gun, self.bullets = screen_size, gun, bullets

        self.x_size, self.y_size = 6, 6

        if 'bullet' not in images[client_number]:
            generate_image(client_number=client_number, name='bullet', size=(self.x_size, self.y_size), shape='circle', color=(255, 255, 0))

        rect = images[client_number]['bullet'].get_rect()
        gun_rect = images[client_number]['gun'].get_rect()

        rect.center = gun_rect.center
        self.x, self.y = rect.topleft[0] + self.gun.x, rect.topleft[1] + self.gun.y

        self.speed = speed
        self.angle = self.gun.player.angle

    def update_position(self):
        angle_radians = math.radians(self.angle - 90)

        self.x += self.speed * math.cos(angle_radians)
        self.y += self.speed * math.sin(angle_radians)

        if self.x <= -10 or self.x >= (self.screen_size[0] + 10) or self.y <= -10 or self.y >= (self.screen_size[1] + 10):
            self.bullets.remove(self)
