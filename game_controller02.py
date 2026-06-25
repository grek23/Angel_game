import pygame
from sys import exit
import random
import os

#tutorial: https://www.youtube.com/watch?v=AY9MnQ4x3zk
# left off at the 2:10:31 mark
pygame.init()
pygame.joystick.init()
pygame.mixer.init()

if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Controller detected: {joystick.get_name()}")
else:
    joystick = None
    print("No controller detected")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path,relative_path)


pygame.mixer.music.load( resource_path('audio/background_music01.mp3'))
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)
 
jump_sound = pygame.mixer.Sound(resource_path('audio/jump_cartoon.wav'))
collect_sound = pygame.mixer.Sound(resource_path('audio/coin.wav'))
crash_sound = pygame.mixer.Sound(resource_path('audio/crash01.wav'))

#Globals
global GAME_WIDTH
global GAME_HEIGHT
global SCREEN
global CLOCK
#global GAME_ACTIVE
global SCORE
global START_TIME
global TEST_FONT
 
GAME_WIDTH = 800    #px
GAME_HEIGHT = 400   #px

SCREEN = pygame.display.set_mode((GAME_WIDTH,GAME_HEIGHT))
CLOCK = pygame.time.Clock()
#GAME_ACTIVE = True
SCORE = 0
START_TIME = 0
TEST_FONT = pygame.font.Font(resource_path('font/Pixeltype.ttf'), 40) #was 50

scale_factor = .1
original_truck_left = pygame.image.load(resource_path('graphics/monster_truck/monster_truck03_large.png'))
new_width = int(original_truck_left.get_width()*scale_factor)
new_height = int(original_truck_left.get_height()*scale_factor)
shrunk_truck_left = pygame.transform.smoothscale(original_truck_left,(new_width,new_height))

original_truck_right = pygame.image.load(resource_path('graphics/monster_truck/monster_truck01_large.png'))
new_width = int(original_truck_right.get_width()*scale_factor)
new_height = int(original_truck_right.get_height()*scale_factor)
shrunk_truck_right = pygame.transform.smoothscale(original_truck_right,(new_width,new_height))

smoke_image = IMAGE = pygame.image.load(resource_path('graphics/smoke.png')).convert_alpha()

class Game:
    def __init__(self, font):
        self.game_active = True
        self.game_first = True
        self.font = font
        self.start_image = pygame.image.load(resource_path('graphics/Player/angel_px_right.png')).convert_alpha()
        self.start_image_rect = self.start_image.get_rect(midbottom=(400,155))

    def draw_instructions(self, screen):
        screen.blit(self.start_image, self.start_image_rect)
        surf_1 = self.font.render(f"Help Angel collect tennis balls and avoid obsticles.", False, (64,64,64))
        rect = surf_1.get_rect(center=(400,50))
        screen.blit(surf_1,rect)

        surf_2 = self.font.render(f"Press <Space Bar> to jump.", False, (64,64,64))
        rect = surf_2.get_rect(center=(400,200))
        screen.blit(surf_2,rect)

        surf_3 = self.font.render(f"Press <left arrow> to move left.", False, (64,64,64))
        rect = surf_3.get_rect(center=(400,250))
        screen.blit(surf_3,rect)

        surf_3 = self.font.render(f"Press <right arrow> to move right.", False, (64,64,64))
        rect = surf_3.get_rect(center=(400,300))
        screen.blit(surf_3,rect)

        surf_4 = self.font.render(f"Press  <Space Bar>  or controller button <5> to start!", False, (64,64,64))
        rect = surf_4.get_rect(center=(400,350))
        screen.blit(surf_4,rect)


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width=120, height=20):
        super().__init__()

        self.image = pygame.Surface((width,height))
        self.image.fill((187,128,68))
        self.rect = self.image.get_rect(topleft=(x,y))

class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(resource_path('graphics/Player/angel_px_right.png')).convert_alpha()
        self.rect = self.image.get_rect(midbottom=(300,300))
        self.gravity = 0
        self.on_ground = False

    def reset(self):
        self.rect = self.image.get_rect(midbottom=(300,300))
        self.gravity = 0

    def jump(self):

        if self.on_ground:
            self.gravity = -25
    
    def apply_gravity(self, platforms):
        
        self.on_ground = False
        self.gravity += 1
        self.rect.y += self.gravity

        landed = False

        #ground collision
        if self.rect.bottom >= 300:
            self.rect.bottom = 300
            self.gravity = 0
            landed = True
            self.on_ground = True
        
        #platform collision
        for platform in platforms:

            if (self.rect.colliderect(platform.rect) and self.gravity > 0 and self.rect.bottom <= platform.rect.bottom):
                self.rect.bottom = platform.rect.top
                self.gravity = 0
                landed = True
                self.on_ground = True
        
        return landed
    
    def move(self,direction):
        if direction > 0:
            #moving right
            self.image = pygame.image.load(resource_path('graphics/Player/angel_px_right.png')).convert_alpha()
            self.rect.x += 5
        elif direction < 0:
            #moving left
            self.image = pygame.image.load(resource_path('graphics/Player/angel_px_left.png')).convert_alpha()
            self.rect.x -= 5
    
    def update(self):
        pass
        #self.apply_gravity()

class Ball(pygame.sprite.Sprite):
    
    def __init__(self):
        super().__init__()
        self.radius = 10
        self.image = pygame.Surface((self.radius *2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, "yellow", (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()
        self.reset()
    
    def reset(self):

        self.x = 800
        self.y = random.randint(0,300)
        self.vx = -3
        self.vy = 0
        self.gravity = 0.5

        self.rect.center = (self.x, self.y)
    
    def update(self):

        self.x += self.vx
        self.y += self.vy

        self.vy += self.gravity

        floor_y = 300 - self.radius

        if self.y >= floor_y:
            self.y = floor_y
            #self.vy = -12
            self.vy *= -0.8

        if self.x < -20:
            self.reset()

        self.rect.center = (int(self.x), int(self.y))

class Snail(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.speed = random.randint(3,7) 
        self.image = pygame.image.load(resource_path('graphics/snail/snail1.png')).convert_alpha()
        #self.image = pygame.image.load('graphics/monster_truck/monster_truck01.png').convert_alpha()
        #self.image = shrunk_truck_left
        self.rect = self.image.get_rect(midbottom=(random.randint(750,800),300))
    
    def reset(self):
        self.rect = self.image.get_rect(midbottom=(random.randint(750,800),300))

    def update(self):
        self.rect.x -= self.speed

        if self.rect.right <= 0:
            self.kill()

def scale(img: pygame.Surface, factor):
    w,h = img.get_width()*factor, img.get_height()*factor
    return pygame.transform.scale(img, (int(w), int(h)))

class SmokeParticle:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.scale_k = 0.2
        self.img = scale(smoke_image, self.scale_k)
        self.alpha = 255
        self.alpha_rate = 10
        self.alive = True
        self.vx = 0
        self.scale_k_rate = 0.05
        self.vy = 4 + random.randint(7, 10) / 10
        self.k = 0.2 * random.random() * random.choice([-2, 1])
    
    def update(self):
        self.x += self.vx
        self.vx += self.k
        self.y += self.vy
        self.vy += 0.99
        self.scale_k += self.scale_k_rate
        #self.scale_k == 0.005
        self.alpha -= self.alpha_rate
        if self.alpha < 0:
            self.alpha = 0
            self.alive = False
        self.alpha_rate -= 0.1
        if self.alpha_rate < 1.5:
            self.alpha_rate = 1.5
        self.img = scale(smoke_image, self.scale_k)
        self.img.set_alpha(self.alpha)
    
    def draw(self):
        SCREEN.blit(self.img, self.img.get_rect(center = (self.x,self.y)))

class Smoke():
    def __init__(self):
        super().__init__()
        self.x = 0
        self.y = 0
        self.particles = []
        self.frames = 0
    
    def update(self):
        self.particles = [i for i in self.particles if i.alive]
        
        for i in self.particles:
            i.update()
    
    def draw(self):
        for i in self.particles:
            i.draw()
    
    def burst(self, x, y, count=15):
        for _ in range(count):
            px = x + random.randint(-8, 8)
            py = y + random.randint(-3, 3)
            self.particles.append(SmokeParticle(px,py))

class MonsterTruck(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.direction = random.choice([True,False])
        self.speed = random.randint(2,7)
        if self.direction:
            print(f"Should be going left: {self.direction}")
            self.image = shrunk_truck_left
            self.rect = self.image.get_rect(midbottom=(random.randint(600,800),300))
        else:
            print(f"Should be going right: {self.direction}")
            self.image = shrunk_truck_right
            self.rect = self.image.get_rect(midbottom=(random.randint(0,80),300))
    
    def reset(self):
        if self.direction:
            self.image = shrunk_truck_left
            self.rect = self.image.get_rect(midbottom=(random.randint(600,800),300))
        else:
            self.image = shrunk_truck_right
            self.rect = self.image.get_rect(midbottom=(random.randint(0,80),300))

    def update(self):
        if self.direction:
            self.rect.x -= self.speed
        else:
            self.rect.x += self.speed

        if self.rect.right <= 0:
            self.kill()

class Score:

    def __init__(self, font):
        self.font = font
        self.value = 0
    
    def add(self, points):
        self.value += points
        print(f"Score is now {self.value}")

    def reset(self):
        self.value = 0

    def draw(self, screen):
        surf = self.font.render(f"Score: {self.value}", False, (64,64,64))
        rect = surf.get_rect(center=(375,50))
        screen.blit(surf,rect)

class Game_Time:

    def __init__(self, font):
        self.value = 0
        self.seconds = 300
        self.font = font
    
    def reset(self):
        self.value = 0
        self.seconds = 300

    def update(self):
        self.value += 1

        if self.value == 60:
            self.seconds -= 1
            self.value = 0

        if self.seconds <= 0:
            self.seconds = 0
            return False
    
    def draw(self, screen):
        surf = self.font.render(f"T - {self.seconds}", False, (64,64,64))
        rect = surf.get_rect(center=(600,50))
        screen.blit(surf,rect)

class LevelManager:
    def __init__(self, font):
        self.level = 1
        self.font = font
        self.winning_value = 150

    def update(self, score, platforms, all_sprites):

        old_level = self.level
        if score >= self.winning_value:
            print("You wont the game!")
        elif score >= 100:
            self.level = 3
        elif score >= 20:
            self.level = 2
        else:
            self.level = 1

        if old_level != self.level:
            self.load_level(platforms, all_sprites)
            
    def reset(self):
        self.level = 1
    
    def draw(self, screen,score):
        if score < 150:
            surf = self.font.render(f"Level - {self.level}", False, (64,64,64))
            rect = surf.get_rect(center=(100,50))
            screen.blit(surf,rect)
        else:
            #Handle winning game
            surf = self.font.render(f"YOU WON!!!", False, (64,64,64))
            rect = surf.get_rect(center=(100,50))
            screen.blit(surf,rect)
    
    def load_level(self, platforms, all_sprites):

        for platform in platforms:
            platform.kill()

        if self.level == 1:
            p1 = Platform(450,220)
            p2 = Platform(150,100)
            platforms.add(p1,p2)
            all_sprites.add(p1,p2)
        elif self.level == 2:
            p1 = Platform(150,100)
            platforms.add(p1)
            all_sprites.add(p1)
        elif self.level == 3:
            p1 = Platform(200, 150)
            platforms.add(p1)
            all_sprites.add(p1)


def check_collisions(player, ball, snails, trucks, score):
    if player.rect.colliderect(ball.rect):
        print("Angel got the ball game!")
        collect_sound.play()
        score.add(5)
        ball.reset()

    if pygame.sprite.spritecollide(player, snails, False):
        print(f"collision with snail.")
        crash_sound.play()
        return False
    
    if pygame.sprite.spritecollide(player, trucks, False):
        print(f"Collision with Monster Truck!")
        crash_sound.play()
        score.add(-3)
    
    return True
    
def reset_game(player, ball, snails, trucks, score, game_time):
    
    score.reset()
    game_time.reset()
    player.reset()
    ball.reset()

    for snail in snails:
        snail.kill()
    
    for truck in trucks:
        truck.kill()
    
    starter_snail = Snail()
    starter_truck = MonsterTruck()
    snails.add(starter_snail)
    trucks.add(starter_truck)
    pygame.mixer.music.unpause()

def main():
    
    global TEST_FONT
    global SCREEN

    angel_game = Game(TEST_FONT)
    print(f"New game!")

    #background X
    background_x = 0

    #set up the background images
    sky_surf = pygame.image.load(resource_path('graphics/sky.png')).convert()
    ground_surf = pygame.image.load(resource_path('graphics/ground.png')).convert()

    #set up the score
    game_over_surf = TEST_FONT.render("Game  Over!", False, (64,64,64))
    game_over_rect = game_over_surf.get_rect(center = (400,50))
    restart_surf = TEST_FONT.render("Press  space  bar or button <5> to  continue.", False, (64,64,64))
    restart_rect = restart_surf.get_rect(center = (400,350))

    #Set up the winning screen!
    game_won_surf = TEST_FONT.render("YOU WON!!!", False, (64,64,64))
    game_won_rect = game_won_surf.get_rect(center = (400,50))

    angel_game_over_surf = pygame.image.load(resource_path('graphics/Player/Angel_game_over01.png')).convert_alpha()
    angel_game_over_rect = angel_game_over_surf.get_rect(center = (400,200))

    #Set up the player
    player = Player()

    #set up the platform
    platforms = pygame.sprite.Group()
    platforms.add(Platform(450,220))
    platforms.add(Platform(150,100))

    #set up the ball
    ball = Ball()

    #Set up the snail(s)
    snails = pygame.sprite.Group()
    snails.add(Snail())

    #Set up the Truck(s)
    trucks = pygame.sprite.Group()
    trucks.add(MonsterTruck())

    #Set up the score
    score = Score(TEST_FONT)

    #Set up timer
    game_time = Game_Time(TEST_FONT)

    #set up smoke
    smoke = Smoke()

    #Set up all Sprites
    all_sprites = pygame.sprite.Group()
    all_sprites.add(snails)
    all_sprites.add(player)
    all_sprites.add(ball)
    all_sprites.add(trucks)
    all_sprites.add(platforms)
    #all_sprites.add(smokes)

    #Set up the level Manager
    level_manager = LevelManager(TEST_FONT)

    SPAWN_SNAIL = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_SNAIL, 2000)

    SPAWN_TRUCK = pygame.USEREVENT + 2
    pygame.time.set_timer(SPAWN_TRUCK, 5000)
 
    while True:
        
        SPAWN_SNAIL = pygame.USEREVENT + 1
        SPAWN_TRUCK = pygame.USEREVENT + 2
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("Space Bar")
                    jump_sound.play()
                    smoke.burst(player.rect.centerx, player.rect.bottom)
                    player.jump()
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 1:
                    print(f"Joystick button {event.button}")
                    jump_sound.play()
                    smoke.burst(player.rect.centerx, player.rect.bottom)
                    player.jump()
                        
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and angel_game.game_active == False:
                    #need to restart the game
                    print(f"starting new game!")
                    reset_game(player, ball, snails, trucks, score, game_time)
                    #angel_game.game_active = True
                    angel_game.game_first = True
            if event.type == pygame.JOYBUTTONDOWN and angel_game.game_active == False:
                if event.button == 5:
                    #need to restart the game
                    print(f"starting new game! Joystick button = {event.button}")
                    reset_game(player, ball, snails, trucks, score, game_time)
                    angel_game.game_active = True
                

            if event.type == SPAWN_SNAIL:
                new_snail = Snail()

                snails.add(new_snail)
                all_sprites.add(new_snail)
                pygame.time.set_timer(SPAWN_SNAIL, random.randint(1000,3000))
                print(f"Snails = {len(snails)}")
            
            if event.type == SPAWN_TRUCK:
                new_truck = MonsterTruck()

                trucks.add(new_truck)
                all_sprites.add(new_truck)
                pygame.time.set_timer(SPAWN_TRUCK, random.randint(4000, 7000))
                print(f"Trucks = {len(trucks)}")
                    
        # Game Loop
        if angel_game.game_first:
            SCREEN.fill((187,128,68))
            angel_game.draw_instructions(SCREEN)
            #reset_game(player, ball, snails, trucks, score, game_time)
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                angel_game.game_first = False
                angel_game.game_active = True
                reset_game(player, ball, snails, trucks, score, game_time)
            
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 5:
                    angel_game.game_first = False
                    angel_game.game_active = True
                    reset_game(player, ball, snails, trucks, score, game_time)

        elif angel_game.game_active and score.value < level_manager.winning_value:
            #background
            background_x -= 2
            if background_x <= -800:
                background_x = 0
            
            SCREEN.blit(sky_surf,(background_x,0))
            SCREEN.blit(sky_surf,(background_x+800,0))
            #SCREEN.blit(sky_surf,(0,0))
            SCREEN.blit(ground_surf,(0,300))

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.move(-1)
        
                if player.rect.bottom >= 300:
                    if random.randint(1,8) == 1:
                        pass
                    
                print(f"player.rect.y: g {player.rect.y}")

            if keys[pygame.K_RIGHT]:
                player.move(1)

                if player.rect.bottom >= 300:
                    if random.randint(1,8) == 1:
                        pass    
                print(f"player.rect.y: f {player.rect.y}")

            if joystick:
                x_axis = joystick.get_axis(0)

                if x_axis < -0.3:
                    player.move(-1)
                if x_axis > 0.3:
                    player.move(1)


            all_sprites.draw(SCREEN)
            game_time.draw(SCREEN)
            score.draw(SCREEN)
            level_manager.draw(SCREEN, score.value)

            angel_game.game_active = check_collisions(player, ball, snails, trucks, score)
            
            
            smoke.draw()
            smoke.update()
            level_manager.update(score.value, platforms, all_sprites)
            player.apply_gravity(platforms)
            all_sprites.update()
            game_time.update()
        
        elif angel_game.game_active and score.value >= level_manager.winning_value:
            print("You won!!!")
            all_sprites.empty()
            all_sprites.add(player)
            all_sprites.add(ball)
            all_sprites.add(platforms)
            pygame.mixer.music.pause()
            SCREEN.fill((94,129,162))
            SCREEN.blit(game_won_surf, game_won_rect)

            time_remaining_surf = TEST_FONT.render(f"Time Remaining = {game_time.seconds}", False, (64,64,64))
            time_remaining_rect = time_remaining_surf.get_rect(center = (400,150))
            SCREEN.blit(time_remaining_surf, time_remaining_rect)
            SCREEN.blit(restart_surf, restart_rect)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                angel_game.game_first = True
                angel_game.game_active = True
                score.reset()
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 5:
                    angel_game.game_first = True
                    angel_game.game_active = True
                    score.reset()

        else:
            #game over screen
            all_sprites.empty()
            all_sprites.add(player)
            all_sprites.add(ball)
            all_sprites.add(platforms)
            pygame.mixer.music.pause()
            SCREEN.fill((94,129,162))
            SCREEN.blit(game_over_surf, game_over_rect)
            SCREEN.blit(angel_game_over_surf, angel_game_over_rect)
            SCREEN.blit(restart_surf, restart_rect)
            #angel_game.game_first = True
            
        pygame.display.update()
        dt = CLOCK.tick(60) /1000
        

if __name__ == '__main__':
    main()