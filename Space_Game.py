import pygame
import os
import random

pygame.font.init()
pygame.mixer.init()

WIDTH = 800
HEIGHT = 600

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
COOLDOWN = 30

BACK_GROUND = pygame.image.load(os.path.join("Space_Game", "background_space.png"))

MISSION_SHIP = pygame.image.load(os.path.join("Space_Game", "mission_ship.png"))

RED_ENEMY_SHIP = pygame.image.load(os.path.join("Space_Game", "enemy_ship_red.png"))
GREEN_ENEMY_SHIP = pygame.image.load(os.path.join("Space_Game", "enemy_ship_green.png"))
BLUE_ENEMY_SHIP = pygame.image.load(os.path.join("Space_Game", "enemy_ship_blue.png"))

PLAYER_LASER = pygame.image.load(os.path.join("Space_Game", "blue_rocket.png"))

ENEMY_LASER_1 = pygame.image.load(os.path.join("Space_Game", "laser01.png"))
ENEMY_LASER_2 = pygame.image.load(os.path.join("Space_Game", "laser02.png"))
ENEMY_LASER_3 = pygame.image.load(os.path.join("Space_Game", "laser03.png"))

SHIELD_IMAGE = pygame.image.load(os.path.join("Space_Game", "spr_shield.png"))
SHIELD_IMAGE = pygame.transform.scale(SHIELD_IMAGE, (MISSION_SHIP.get_width(), MISSION_SHIP.get_height()))
HEART_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join("Space_Game", "heart.png")), (50, 28))

laser_sound = pygame.mixer.Sound(os.path.join("Space_Game", "laser1.wav"))
explosion_sound = pygame.mixer.Sound(os.path.join("Space_Game", "explosion1.wav"))
background_music = os.path.join("Space_Game", "space-walk.wav")

def collide(object1, object2):
    off_set_x = object1.x - object2.x
    off_set_y = object1.y - object2.y
    return object1.mask.overlap(object2.mask, (off_set_x, off_set_y)) is not None

class Lazer:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def move(self, velocity):
        self.y += velocity

    def draw(self, window):
        window.blit(self.img, (self.x + 20, self.y))

    def collision(self, object):
        return collide(object, self)

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

class Ship:
    def __init__(self, x, y, health):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def cool_down(self):
        if self.cool_down_counter >= COOLDOWN:
            self.cool_down_counter = 0
        else:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Lazer(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            laser_sound.play()

    def move_lasers(self, velocity, object):
        self.cool_down()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(object):
                object.health -= 10
                self.lasers.remove(laser)

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class PlayerShip(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = MISSION_SHIP
        self.laser_img = PLAYER_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.shield = False
        self.shield_time = 0
        self.shield_hits = 0

    def move_lasers(self, velocity, objects):
        self.cool_down()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for object in objects:
                    if laser.collision(object):
                        objects.remove(object)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height(), self.ship_img.get_width(), 7))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height(), int(self.ship_img.get_width() * (self.health / self.max_health)), 7))

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        self.healthbar(window)
        if self.shield:
            window.blit(SHIELD_IMAGE, (self.x, self.y))  # Kalkan gemiyi kaplayacak şekilde
        for laser in self.lasers:
            laser.draw(window)

    def activate_shield(self):
        self.shield = True
        self.shield_time = pygame.time.get_ticks()
        self.shield_hits = 0

    def update_shield(self):
        if self.shield:
            if pygame.time.get_ticks() - self.shield_time > 8000 or self.shield_hits >= 5:
                self.shield = False

class EnemyShip(Ship):
    COLOR_MAP = {
        "red": [RED_ENEMY_SHIP, ENEMY_LASER_1],
        "green": [GREEN_ENEMY_SHIP, ENEMY_LASER_2],
        "blue": [BLUE_ENEMY_SHIP, ENEMY_LASER_3]
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, velocity):
        self.y += velocity

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Lazer(self.x - 10, self.y + 12, self.laser_img)
            self.lasers.append(laser)

class PowerUp:
    def __init__(self, x, y, img, effect):
        self.x = x
        self.y = y
        self.img = img
        self.effect = effect
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, velocity):
        self.y += velocity

    def collision(self, player):
        return collide(self, player)

def main():
    global COOLDOWN, laser_velocity, enemy_velocity
    run = True
    FPS = 60
    enemies = []
    powerups = []
    player_velocity = 5
    enemy_velocity = 1
    laser_velocity = 5
    enemy_length = 0
    level = 0

    main_font = pygame.font.SysFont("Algerian", 30)
    lost_font = pygame.font.SysFont("Algerian", 90)

    clock = pygame.time.Clock()

    player = PlayerShip(350, 450)
    lost = False

    def draws():
        WIN.blit(BACK_GROUND, (0, 0))
        player.draw(WIN)
        level_label = main_font.render("LEVEL: {}".format(level), 1, (255, 255, 255))
        WIN.blit(level_label, (660, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        for powerup in powerups:
            powerup.draw(WIN)

        if lost:
            lost_label = lost_font.render("GAME OVER", 1, (200, 0, 0))
            WIN.blit(lost_label, (WIDTH / 2 - int((lost_label.get_width() / 2)), HEIGHT / 2 - int((lost_label.get_height() / 2))))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        draws()
        player.update_shield()

        if player.health <= 0:
            lost = True
            run = False
            COOLDOWN = 30
            laser_velocity = 5
            enemy_velocity = 1
            continue

        if len(enemies) == 0 and not lost:
            enemy_velocity += 1
            laser_velocity += 1
            enemy_length += 3
            level += 1
            COOLDOWN = max(COOLDOWN - 5, 5)
            for i in range(enemy_length):
                enemy = EnemyShip(random.randrange(1, 700), random.randrange(-1500, -100), random.choice(["red", "green", "blue"]))
                enemies.append(enemy)

            if random.randrange(0, 2) == 1:
                powerup_type = random.choice(["shield", "health"])
                powerup_image = SHIELD_IMAGE if powerup_type == "shield" else HEART_IMAGE
                powerup = PowerUp(random.randrange(50, WIDTH - 50), random.randrange(-1000, -100), powerup_image, powerup_type)
                powerups.append(powerup)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and player.x > 0:
            player.x -= player_velocity
        if keys[pygame.K_RIGHT] and player.x < 720:
            player.x += player_velocity
        if keys[pygame.K_UP] and player.y > 0:
            player.y -= player_velocity
        if keys[pygame.K_DOWN] and player.y < 470:
            player.y += player_velocity
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies:
            enemy.move(enemy_velocity)
            enemy.move_lasers(laser_velocity, player)
            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                if not player.shield:
                    player.health -= 10
                else:
                    player.shield_hits += 1
                enemies.remove(enemy)
                explosion_sound.play()

            if enemy.y > HEIGHT:
                enemies.remove(enemy)

        player.move_lasers(-laser_velocity, enemies)

        for powerup in powerups[:]:
            powerup.move(2)
            if powerup.collision(player):
                if powerup.effect == "shield":
                    player.activate_shield()
                elif powerup.effect == "health" and player.health < player.max_health:
                    player.health = min(player.health + 20, player.max_health)
                powerups.remove(powerup)
            elif powerup.y > HEIGHT:
                powerups.remove(powerup)

def main_menu():
    pygame.mixer.music.load(background_music)
    pygame.mixer.music.play(-1)

    title_font = pygame.font.SysFont('Algerian', 50)
    run = True
    while run:
        WIN.blit(BACK_GROUND, (0, 0))
        main_text = title_font.render('PRESS TO START GAME', 1, (255, 255, 255))
        WIN.blit(main_text, (int(WIDTH / 2 - main_text.get_width() / 2), int(HEIGHT / 2 - main_text.get_height() / 2)))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()

main_menu()
