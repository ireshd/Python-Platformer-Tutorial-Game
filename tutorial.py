import os
import random 
import math
from typing import Self
import pygame
from os import listdir
from os.path import isfile, join
pygame.init

pygame.display.set_caption("Platformer")

#Global Variables
WIDTH, HEIGHT = 800, 600 #Dimensions of Screen
FPS = 60
PLAYER_VEL = 5 #Speed player moves

window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites): # a function for flipping which side our character's animation is facing (right or left)
    return[pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheet(dir1, dir2, width, height, direction = False): #loads all the sprites for our character, jumping, falling, idle ,etc
    path = join("assets", dir1, dir2) #joins paths of assests, directory 1 and director 2
    images = [f for f in listdir(path) if isfile(join(path, f))]#loads every file in the directories from the parameter
    
    all_sprites = {} #dict for sprites, key = animation style, value = all images in that animation

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()#convert alpha loads transperent background image

        sprites = []
        for i in range(sprite_sheet.get_width() // width):#gets the width of the sprite and divides by the width parameter to split the image properly
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32) # creating a surface the size of our animation frame
            rect = pygame.Rect(i * width, 0, width, height) #location of the image we are exporting our animation frame
            surface.blit(sprite_sheet, (0, 0), rect)#blit = draw, drawing the sprite sheet at the new surface we created
            sprites.append(pygame.transform.scale2x(surface))#scaled surface to twice the size

        if direction:#if u want a multidirectional, we need to add two keys for each animation
            all_sprites[image.replace(".png", "") + "_right"] = sprites #strips .png from name and adds _right
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites) #strips .png from name, adds _left and flips all the sprite animations with the flip func 
        else:
            all_sprites[image.replace(".png", "")] = sprites #strips .png
    
    return all_sprites

def get_block(size): #gets terrian block from the asset
    path = join("assets", "Terrain", "Terrain.png")#joins paths
    image = pygame.image.load(path).convert_alpha() #loads paths
    surface = pygame.Surface((size,size), pygame.SRCALPHA, 32)#loads terrian surface (size of block)
    rect = pygame.Rect(96, 0, size, size) #terrian block starts 96 pixels into the image
    surface.blit(image, (0,0), rect)#draws the image
    return pygame.transform.scale2x(surface) # doubles the size


#inherits from pygame, Easy for pixel perfect collision, a Class for player
class Player(pygame.sprite.Sprite):
    COLOR = (0, 0, 225) #temp class var
    GRAVITY = 1 #rate of acceleration of gravity
    SPRITES = load_sprite_sheet("MainCharacters", "PinkMan", 32, 32, True)#sprite load
    ANIMATION_DELAY = 3


    def __init__(self, x, y, width, height): #intializing player values
        self.rect = pygame.Rect(x, y, width, height) #passing all the vars onto the rectangle, Rect is a tuple, pygame.rect allows us to use it in pygame equations
        self.x_vel = 0 #player horziontal velocity
        self.y_vel = 0 #player vertical velocity
        self.mask = None
        self.direction = "left" #which direction the player is facing
        self.animation_count = 0 #resets animation so it doesnt look strange 
        self.fall_count = 0 # fall count for how long spent falling
        self.jump_count = 0 # double jump count
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8 #-gravity works and is fluid as gravity is acceleration
        self.animation_count = 0 #resetting jump animation
        self.jump_count += 1 #incrementing jump count for when its run
        if self.jump_count >= 1:
            self.fall_count = 0 #gets rid of gravity that has been accounted for
            
    def move(self, dx , dy):#dx displacement on x, dy displacement on y 
        self.rect.x += dx #adds displacement onto players position 
        self.rect.y += dy
    
    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def move_left(self, vel):
        self.x_vel = -vel # -vel bc in pygames coordinate system, moving to the left brings closer to zero
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel #+vel bc in right is farther from zero
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
    
    def loop(self, fps):
            self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY) #min of 1 so we are falling at a noticably rate, fall count is time spent falling, divide by fps to get in seconds and multiple by gravity to add the amount of gravity in the game
            self.move(self.x_vel, self.y_vel) #if we call loop and we have velocity, it'll move in the respective direction
            self.fall_count += 1 #increments every frame spent falling
            
            if self.hit:
                self.hit_count += 1
            if self.hit_count > fps:
                self.hit = False
                self.hit_count = 0

            self.update_sprite()#calls update sprite animation method

    def landed(self):
        self.fall_count = 0 #reset fall count because you are on the ground
        self.y_vel = 0 #reset y_vel bc u cant travel farther
        self.jump_count = 0 #reset jump_count for double jump
    
    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update(self):
        self.rect = self.sprite.get_rect( topleft = (self.rect.x, self.rect.y)) #adjusts the rectangle to bound our character to a sprit, topleft has to be lower case
        self.mask = pygame.mask.from_surface(self.sprite) #this mask allows us to have pixel collisions between sprites, rather than rectangular collisions, it allows us to ignore transperent pixel even if inside the characters bounding box
        #Pixel perfect colision, NOTE HAS to be called mask


    def draw(self, win, offset_x): # win = window, (its a class function so it doesn't interfere with global draw)
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y)) #draws the animation at the player position
    
    def update_sprite(self):
        sprite_sheet = "idle" #default = idle, a sprite_sheet is the name of animation in the asset
        if self.hit:
            sprite_sheet = "hit"


        if self.y_vel < 0: # <0 = moving up
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2: # > 0 = falling, reason for gravity * 2 rather than 0 is because gravity always active so the animation glitches while on the ground
            sprite_sheet ="fall"

        if self.x_vel != 0: #if player is moving
            sprite_sheet = "run" #sprite sheet = running animation
        
        sprite_sheet_name = sprite_sheet + "_" + self.direction #renames to name_direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites) #picking a new index every animation frame every 5 frames 
        self.sprite = sprites[sprite_index]
        self.animation_count += 1 #updates counts
        self.update()

#inherits from pygame, A class for all objects
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name = None):
        super().__init__() #NOTE the following vars r needed for any sprite, so we are just writing a class for an easy intialization
        self.rect = pygame.Rect(x, y ,width, height) #rectangle
        self.image = pygame.Surface((width, height), pygame.SRCALPHA, 32) #image
        self.width = width
        self.height = height
        self.name = name
    
    def draw(self,win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y)) #drawing object

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size) # super req 4 parameter but since block is a square height = width = size
        block = get_block(size)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image) #colision mask

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire") # intializing the vars
        self.fire = load_sprite_sheet("Traps", "Fire", width, height) #loads sprite sheet
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"
    
    def off(self):
        self.animation_name = "off"
    
    def loop(self):#works the same way as player
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites) #picking a new index every animation frame every 5 frames 
        self.image = sprites[sprite_index]
        self.animation_count += 1 #updates counts
        self.rect = self.image.get_rect( topleft = (self.rect.x, self.rect.y)) #adjusts the rectangle to bound our character to a sprit, topleft has to be lower case
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))#joining assests and background path
    _, _, width, height = image.get_rect() #grabs the x, y, width, heigth
    tiles = [] 

    for i in range(WIDTH // width + 1): #a nested loop to calculate how many tiles are needed to fill the screen
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height) #notes the current position pygame is drawing the tiles
            tiles.append(pos) #adds tile position to the list
    return tiles, image 

def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)  #looping through every tile postion we have and drawing the bg_image
    
    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)
 
    pygame.display.update() #every frame we clear the screen

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0: #if player is falling 
                player.rect.bottom = obj.rect.top #the bottom of the player = top of the object when moving down
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom # bottom of an object = top of a player when moving up (hitting ur head)
                player.hit_head()
        
            collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update() #need to update mask/ rect
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj): # checks collision between obj and updated mask
            collided_object = obj
            break
    player.move(-dx,0) #moves player back to original
    player.update()
    return collided_object

def handle_move(player, objects): #player input movement function 
    keys = pygame.key.get_pressed() #through pygame, the method tell you which key is being pressed
    
    player.x_vel = 0 #it resets to not moving so when you click the respective key it moves to that direction. For example if we didnt do this, you would have to click a new direction key twice if your already in a different direction, ie left: -5 + right: +5 = 0 rather than right: +5 = 5 
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left: # if left arrow key move left, etc
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL) 
    
    verticle_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *verticle_collide]
    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()


def main (window): #to start game and event loop
    clock = pygame.time.Clock() 
    background, bg_image = get_background("Blue.png") #gets background according to the name of the PNG
    block_size = 96 #length of 1 side of a block in pixels

    player = Player(100,100,40,40)
    fire = Fire(200, HEIGHT-block_size - 64, 16 , 32)
    fire.on()
    floor = [Block(i * block_size, HEIGHT- block_size, block_size) for i in range(-WIDTH // block_size, WIDTH * 2 // block_size)]
    #^ Blocks that go left and right, Block() is size of block, while i in range is often the blocks need to be drawn/placed
    objects =[*floor, Block(0, HEIGHT - block_size * 2, block_size),
              Block(block_size * 3, HEIGHT - block_size * 4, block_size), fire ] #*breaks the items in floor into individuals

    offset_x = 0
    scroll_area_width = 200

    run = True #running the game
    while run:
        clock.tick(FPS) #makes while loop run 60x per second reguates across different devices

        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: #Ends main event loop when player exits game
                run = False
                break
            
            if event.type == pygame.KEYDOWN: #JUMPING, actives if key down, not doing inside of handle move bc then u can spam jumps
                if event.key == pygame.K_SPACE and player.jump_count < 2:# of jump count < 2
                    player.jump() # jump

        player.loop(FPS) #reason to call loop is bc it is passing the position of the player according to the movement
        fire.loop()
        handle_move(player, objects )
        
        draw(window, background, bg_image, player, objects, offset_x) # drawing the background

        if(player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel > 0) or (#right screen offset
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0): #left offset
            offset_x += player.x_vel

    pygame.quit()
    quit()  


if  __name__ == "__main__": #only runs main if we access file directly (so it does not run when importing from the file)
    main(window)