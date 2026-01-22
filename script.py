import pygame
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1200
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Simple Game")

#define game variables
tile_size = 50
game_over = 0

#load images
bg_img = pygame.image.load('assets/img/bg.png')
restart_img = pygame.image.load('assets/img/btns/restart.png')

pygame.transform.scale(bg_img, (screen_width, screen_height))

def draw_grid():
    for line in range(0, 24):
        pygame.draw.line(screen, (255,255,255), (0, line * tile_size), (screen_width, line * tile_size))
        pygame.draw.line(screen, (255,255,255), (line * tile_size, 0), (line * tile_size, screen_height))

class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_pressed = False

    def draw(self):
        action = False

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] and self.is_pressed == False:
                action = True
                self.is_pressed = True
            else:
                self.is_pressed = False

        screen.blit(self.image, self.rect)

        return action

class Player:
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 3

        if game_over == 0:
            key = pygame.key.get_pressed()

            if key[pygame.K_a] and self.rect.x > 0:
                dx -= 5
                self.counter += 1
                self.is_flip = True
            if key[pygame.K_a] == False and key[pygame.K_d] == False:
                self.counter = 0
                self.index = 0
                if self.is_flip:
                    self.image = pygame.transform.flip(self.images_right[self.index], True, False)
                else:
                    self.image = self.images_right[self.index]
            if key[pygame.K_d] and self.rect.x < screen_width - self.rect.width:
                dx += 5
                self.counter += 1
                self.is_flip = False
            if key[pygame.K_w] and self.is_jumping == False and self.in_air == False:
                self.vel_y = -15
                self.is_jumping = True
            if not key[pygame.K_w]:
                self.is_jumping = False

            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0

            if self.is_flip:
                self.image = pygame.transform.flip(self.images_right[self.index], True, False)
            else:
                self.image = self.images_right[self.index]

            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            self.in_air = True
            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    self.in_air = False
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0

            damage_cooldown = 30

            if pygame.sprite.spritecollide(self, blob_group, False) or pygame.sprite.spritecollide(self, swamp_group, False):
                if self.damage_counter >= damage_cooldown:
                    self.lives -= 1
                    print(self.lives)
                    self.damage_counter = 0
                else:
                    self.damage_counter += 1

                if self.lives <= 0:
                    game_over = 1
                    self.index = 0
            else:
                self.damage_counter = 30

            self.rect.x += dx
            self.rect.y += dy

            if self.rect.bottom > screen_height:
                self.rect.bottom = screen_height
                dy = 0
        else:
            if self.counter > walk_cooldown:
                self.counter = 0
                if self.index < 3:
                    self.index += 1
            else:
                self.counter += 1

            self.image = self.images_dead[self.index]

        draw_x = self.rect.x - self.image_offset_x
        draw_y = self.rect.y - self.image_offset_y

        screen.blit(self.image, (draw_x, draw_y))

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_dead = []
        self.index = 0
        self.counter = 0
        self.lives = 3
        self.in_air = False

        for num in range(0, 12):
            img_right = pygame.image.load(f'assets/img/player/walk/c_{num}.png')
            img_right = pygame.transform.scale(img_right, (128, 93))
            self.images_right.append(img_right)

        for num in range(0, 4):
            img = pygame.image.load(f'assets/img/player/dead/c_{num}.png')
            img = pygame.transform.scale(img, (88, 93))
            self.images_dead.append(img)

        self.image = self.images_right[self.index]
        self.rect = pygame.Rect(x, y, 50, 85)

        self.image_offset_x = (128 - 50) // 2
        self.image_offset_y = 93 - 95

        self.rect.x = x
        self.rect.y = y
        self.width = 50
        self.height = 85
        self.vel_y = 0
        self.is_jumping = False
        self.is_flip = False
        self.damage_counter = 0


class World:
    def __init__(self, data):
        self.tile_list = []

        #load images
        grass_img = pygame.image.load('assets/img/grass_tile.png')

        row_count = 0
        for row in data:
            col_count = 0
            index = 0

            for tile in row:
                left_tile = row[index - 1] if index > 0 else 1
                right_tile = row[index + 1] if index < len(row) - 1 else 1
                index += 1

                if tile == 1:
                    if left_tile == 0 and right_tile == 0:
                        img = pygame.transform.scale(pygame.image.load('assets/img/grass_tile_round.png'), (tile_size, tile_size))
                    elif left_tile == 0:
                        img = pygame.transform.scale(pygame.image.load('assets/img/grass_tile_round_left.png'), (tile_size, tile_size))
                    elif right_tile == 0:
                        img = pygame.transform.scale(pygame.image.load('assets/img/grass_tile_round_right.png'), (tile_size, tile_size))
                    else:
                        img = pygame.transform.scale(grass_img, (tile_size, tile_size))

                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    swamp = Swamp(col_count * tile_size, row_count * tile_size)
                    swamp_group.add(swamp)
                if tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 30)
                    blob_group.add(blob)
                col_count += 1

            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            # pygame.draw.rect(screen, (255,255,255), tile[1], 2)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.index = 0
        self.counter = 0
        self.images = []
        for num in range(0, 7):
            img = pygame.image.load(f'assets/img/enemies/red_slime_{num}.png')
            img = pygame.transform.scale(img, (47, 32))
            self.images.append(img)

        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        walk_cooldown = 3
        self.counter += 1
        self.move_counter += 1

        if self.move_counter > 100:
            self.move_counter = 0
            self.move_direction = -self.move_direction

        self.rect.x += self.move_direction

        if self.counter > walk_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0

        self.image = self.images[self.index]
        screen.blit(self.image, (self.rect.x, self.rect.y))

class Swamp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        swamp_img = pygame.image.load('assets/img/swamp_tile.png')
        self.image = pygame.transform.scale(swamp_img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

world_data = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 3, 0],
    [0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 1, 1, 0, 0, 0, 0, 1, 1, 2, 2, 2, 2, 1, 1],
    [0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1],
]

player = Player(100, screen_height - 150)
blob_group = pygame.sprite.Group()
swamp_group = pygame.sprite.Group()
world = World(world_data)

restart_btn = Button(screen_width // 2 - 200, screen_height // 2 - 150, restart_img)

run = True
while run:
    clock.tick(fps)

    background_image = screen.blit(bg_img, (0,0))

    game_over = player.update(game_over)
    blob_group.update()
    swamp_group.draw(screen)
    world.draw()
    # draw_grid()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if game_over:
        action = restart_btn.draw()
        if action:
            game_over = 0
            player.reset(100, screen_height - 150)


    pygame.display.update()

pygame.quit()