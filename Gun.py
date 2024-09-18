import pygame


class Gun:
    def __init__(self, client_number, generate_image, player):
        self.player = player

        self.x_size, self.y_size = 10, 30

        generate_image(client_number=client_number, name='gun', size=(self.x_size, self.y_size), shape='rect', color=(100, 100, 100))

        self.x, self.y = (self.player.x + self.player.x_size), (self.player.y + (self.player.y_size - self.y_size) / 2)

    def rotate(self, image):
        image = pygame.transform.rotate(image, -self.player.angle)

        player_vect = pygame.math.Vector2(self.player.x + self.player.x_size / 2, self.player.y + self.player.y_size / 2)
        gun_vect = pygame.math.Vector2((self.player.x + self.player.x_size) + self.x_size / 2, (self.player.y + (self.player.y_size - self.y_size) / 2) + self.y_size / 2)

        rect = image.get_rect()

        new_pos = (gun_vect - player_vect).rotate(self.player.angle) + player_vect

        rect.center = new_pos

        self.x, self.y = rect.topleft

        return image
