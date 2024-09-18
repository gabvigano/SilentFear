import socket

from Network import Host

import pygame
from random import randint

from Player import Player
from Enemy import Enemy
from Gun import Gun
from Bullet import Bullet


def get_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:  # noqa
        return None


host_type = input('who are you? [server/client]: ').lower()
port = 5555

if host_type == 'server':
    print('\nsetting up server...')

    server_ip = get_ip()

    if not server_ip:
        print('error: failed to get the ip address')
    else:
        print(f'server started: the server ip is: {server_ip}')

        server = Host(host_type=host_type, server_ip=server_ip, port=port)

elif host_type == 'client':
    server_ip = input('\nenter the server ip: ')

    client = Host(host_type=host_type, server_ip=server_ip, port=port)

else:
    print('\nhost type not valid')
    exit()

host = server if host_type == 'server' else client  # noqa

pygame.init()

screen_size = (1536, 864)  # (2560, 1440)
FPS = 120
display = pygame.display.set_mode(screen_size)
pygame.display.set_caption(host_type + ('_' + str(host.client_number) if host_type == 'client' else ''))
clock = pygame.time.Clock()
text_font = pygame.font.SysFont('dejavusansmono', 15)
game_over_font = pygame.font.SysFont('dejavusansmono', 40)

close = False
client_send_data = False
game_over = False
resume = False
victory = False

enemies = []
bullets = []

images = {}
clients_data = {}

reload, reload_enemy = 0, 0


def generate_local_images(client_number, name, size, shape, color):
    global images
    if client_number not in images:
        images[client_number] = {}

    image = pygame.Surface(size, pygame.SRCALPHA)

    if shape == 'rect':
        pygame.draw.rect(image, color, image.get_rect())
    elif shape == 'circle':
        pygame.draw.circle(image, color, (size[0] // 2, size[1] // 2), size[0] / 2)

    images[client_number][name] = image
    return image


def encode_images(client_number):  # noqa
    encoded_images = {}

    for name, image in images[client_number].items():
        encoded_images[name] = {'str': pygame.image.tostring(image, 'RGBA'), 'size': image.get_size()}

    return encoded_images


def decode_images(client_number, encoded_images):  # noqa
    if client_number not in images:
        images[client_number] = {}

    for name, image in encoded_images.items():
        images[client_number][name] = pygame.image.fromstring(image['str'], image['size'], 'RGBA')


def draw_objects():
    display.fill((0, 0, 0))
    display.blit(text_font.render(f'FPS: {clock.get_fps():.1f} / {FPS}', 1, (255, 255, 255)), (screen_size[0] - 170, 25))
    display.blit(text_font.render(f'HEALTH: {player.health}', 1, (255, 255, 255)), (25, 25))
    for bullet in bullets:  # noqa
        display.blit(images[host.client_number]['bullet'], (bullet.x, bullet.y))

    display.blit(images[host.client_number]['player'], (player.x, player.y))

    display.blit(gun.rotate(images[host.client_number]['gun']), (gun.x, gun.y))

    if host_type == 'server':
        for enemy in enemies:  # noqa
            display.blit(images[host.client_number]['enemy'], (enemy.x, enemy.y))

    for client_number, data in clients_data.items():  # noqa
        if client_number in images:
            for name, instance in data.items():
                if name == 'bullets':
                    for bullet in instance:  # noqa
                        display.blit(images[client_number]['bullet'], (bullet.x, bullet.y))
                elif name == 'player':
                    display.blit(images[client_number]['player'], (instance.x, instance.y))
                elif name == 'gun':
                    display.blit(instance.rotate(images[client_number]['gun']), (instance.x, instance.y))
                elif name == 'enemies':
                    for enemy in instance:  # noqa
                        display.blit(images[client_number]['enemy'], (enemy.x, enemy.y))

    # write game over at the end so there are no object over it
    if game_over:
        display.blit(game_over_font.render(f'GAME OVER: YOU ' + ('WON' if victory else 'LOST'), 1, (0, 255, 0) if victory else (255, 0, 0)), (screen_size[0] / 2 - 150, screen_size[1] / 2))


def render():
    pygame.display.update()
    clock.tick(FPS)


player = Player(client_number=host.client_number, generate_image=generate_local_images, screen_size=screen_size)
gun = Gun(client_number=host.client_number, generate_image=generate_local_images, player=player)

# creates the first bullet and enemy in order to store the image, then deletes it
bullets.append(Bullet(client_number=host.client_number, generate_image=generate_local_images, images=images, screen_size=screen_size, gun=gun, bullets=bullets, speed=7))
enemies.append(Enemy(client_number=host.client_number, generate_image=generate_local_images, images=images, screen_size=screen_size, player=player, enemies=enemies, bullets=bullets, speed=randint(1, 3)))

bullets.clear()
enemies.clear()

if host_type == 'server':
    server.server_send({'images': encode_images(client_number=host.client_number)}, images=True)
else:
    clients_data = client.client_send({'images': encode_images(client_number=host.client_number)})

    if len(clients_data.values()) > 0:
        if 'images' in list(clients_data.values())[0]:
            client_number = list(clients_data.keys())[0]
            decode_images(client_number, clients_data[client_number]['images'])
            clients_data.clear()

while not close:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            close = True

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LSHIFT]:
        run = True
    else:
        run = False

    player.angle = player.angle % 360
    if player.angle > 180:
        player.angle -= 360

    if keys[pygame.K_w] and not game_over:
        player.move(4 if not run else 8)
    if keys[pygame.K_s] and not game_over:
        player.move(-4 if not run else -8)
    if keys[pygame.K_a] and not game_over:
        player.angle -= 4
    if keys[pygame.K_d] and not game_over:
        player.angle += 4
    if keys[pygame.K_SPACE] and reload >= 20 and not game_over:
        bullets.append(Bullet(client_number=host.client_number, generate_image=generate_local_images, images=images, screen_size=screen_size, gun=gun, bullets=bullets, speed=14))
        reload = 0

    if host_type == 'server' and keys[pygame.K_e] and reload_enemy >= 10 and not game_over:
        enemies.append(Enemy(client_number=host.client_number, generate_image=generate_local_images, images=images, screen_size=screen_size, player=player, enemies=enemies, bullets=bullets, speed=randint(2, 4)))
        reload_enemy = 0

    for bullet in bullets:
        bullet.update_position()

    # game over on this client
    if player.health_check():
        game_over = True

    # resume
    if host_type == 'server' and game_over and keys[pygame.K_r]:
        resume = True

    if host_type == 'server':
        clients_data = server.server_send({'player': player,
                                           'gun': gun,
                                           'bullets': bullets,
                                           'enemies': enemies,
                                           'game_over': game_over,
                                           'resume': resume})
    else:
        if client_send_data:
            clients_data = client.client_send({'player': player,
                                               'gun': gun,
                                               'bullets': bullets,
                                               'game_over': game_over})
        else:
            client_send_data = True

    # game over and resume on other client
    for client_number in clients_data.keys():
        if 'game_over' in clients_data[client_number].keys() and clients_data[client_number]['game_over'] and not game_over:
            game_over = True
            victory = True
        if 'resume' in clients_data[client_number].keys() and clients_data[client_number]['resume']:
            resume = True

    # resume
    if resume:
        game_over = False
        victory = False
        resume = False
        player.reset()
        enemies.clear()
        bullets.clear()

    # update the player attacked by the enemies if there is a client connected
    attacked_player = player
    for client_number in clients_data.keys():
        if 'player' in clients_data[client_number].keys():
            attacked_player = clients_data[client_number]['player']

    # check if enemies are still alive, update the attacked player and update the enemies position
    if host_type == 'server':
        for enemy in enemies:
            if not enemy.die_check() and not game_over:
                enemy.player = attacked_player
                enemy.update_position()

        player.enemies = enemies

    if len(clients_data.values()) > 0:
        # give each player the other's bullet in order to kill each other
        for client_number, data in clients_data.items():
            if 'enemies' in data:
                player.enemies = data['enemies']
            if 'bullets' in data:
                player.enemy_bullets = data['bullets']

        # at the first message, receive the images and store them in the dictionary
        if 'images' in list(clients_data.values())[0]:
            client_number = list(clients_data.keys())[0]
            decode_images(client_number, clients_data[client_number]['images'])
            clients_data.clear()

    reload += 1
    reload_enemy += 1

    draw_objects()
    render()

pygame.quit()
exit()
