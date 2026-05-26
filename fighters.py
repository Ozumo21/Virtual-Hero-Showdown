import pygame
import time
import json
import os
from os import listdir
from os.path import isfile, join

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, dir3, width, height, desired_width, desired_height, direction=False):
    path = join("assets", dir1, dir2, dir3)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        # Note: PNGs only in folder! No PSD files
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(int(sprite_sheet.get_width() // width)):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale(surface, (desired_width, desired_height)))
        
        if direction:
            all_sprites[image.replace(".png", "") + "_left"] = sprites
            all_sprites[image.replace(".png", "") + "_right"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites
    
    return all_sprites


class Fighter(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, playerid, position, input, inputlist, character, fps, sfx, screen_width, screen_height, training_mode, joystick):
        # self.rect = pygame.Rect(x, y, width, height)
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (x, y)
        self.projectile_rect = pygame.Rect(0, 0, width, height)
        self.projectile_rect.center = (x, y)
        self.x_vel = 0
        self.y_vel = 0
        self.gravity = screen_height/432
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.training_mode = training_mode

        # x_speed != x_back_speed
        self.x_speed = character['speed']
        self.x_back_speed = character['backspeed']
        self.jump = False
        self.jumping_forward = False
        self.jumping_backward = False
        self.jump_speed = character['jumpspeed']
        self.dash_multiplier = character['dash_multiplier']
        self.dash_time = character['dash_time']
        self.crouch = False
        self.block = False
        self.playerid = playerid
        self.position = position     # position on the stage (left or right)
        self.input = input     # which input device the player is using (keyboard, PS4 controller... )
        self.inputlist = inputlist
        if self.input == 'keyboard':
            self.left_key = pygame.key.key_code(self.inputlist['left'])
            self.right_key = pygame.key.key_code(self.inputlist['right'])
            self.up_key = pygame.key.key_code(self.inputlist['up'])
            self.down_key = pygame.key.key_code(self.inputlist['down'])
            self.attack1_key = pygame.key.key_code(self.inputlist['attack1'])
            self.attack2_key = pygame.key.key_code(self.inputlist['attack2'])
            self.special_key = pygame.key.key_code(self.inputlist['special'])
            self.block_key = pygame.key.key_code(self.inputlist['block'])
        elif self.input == 'controller':
            self.left_button = inputlist['left']
            self.right_button = inputlist['right']
            self.up_button = inputlist['up']
            self.down_button = inputlist['down']
            self.attack1_button = inputlist['attack1']
            self.attack2_button = inputlist['attack2']
            self.special_button = inputlist['special']
            self.block_button = inputlist['block']
            self.joystick = joystick
            

        # Note: width and height for load_sprite_sheets are set values 400x400 to extract sprites from sprite sheets, do not scale to screen dimensions!
        self.sprites = load_sprite_sheets("images", "characters", character['name'], 400, 400, self.screen_width * 5/24, self.screen_height * 10/27, True)
        self.attack_sprites = load_sprite_sheets("images", "characters", character['name'] + r"\attacks", 500, 400, self.screen_width * 25/96, self.screen_height * 10/27, True)
        
        self.sprite = self.sprites["idle_" + self.position][0]
        self.mask = None
        self.hitbox_sprite = self.sprites["idle_hitbox_" + self.position][0]
        self.hitbox_mask = None
        self.projectile_sprite = self.sprites["idle_hitbox_" + self.position][0]
        self.projectile_mask = None
        self.projectile_travel_frames = 0

        self.action = 'idle'
        self.action_list = ['idle']
        self.forward_dashing = False
        self.backward_dashing = False
        self.dash_start_time = 0
        self.forward_dash_input_time = 0
        self.backward_dash_input_time = 0

        self.health = 1000
        self.defeated = False
        self.pause = False

        self.attacking = False
        self.jump_attacking = False
        self.jump_attack_count = 1
        self.current_attack = ''
        self.current_projectile = ''
        self.current_projectile_start_time = 0
        self.attack_set = character['attacks']
        self.special_attack_set = character['special_attacks']
        self.attack_queue = []
        self.attack_start_time = 0
        self.attack_count = 1    # prevents attack_sequencer() from constantly calling attacks
        self.hitstun = False
        self.hitstun_time = 0
        self.hitstun_start_time = 0
        self.hitcount = 1
        self.animation_step = 0
        self.fps = fps

        # sfx
        self.hit_sfx = sfx[0]

        # pause intervals for when the fight is paused, ensures that character timers are paused
        self.dash_start_time_pause_interval = 0
        self.forward_dash_input_time_pause_interval = 0
        self.backward_dash_input_time_pause_interval = 0
        self.attack_start_time_pause_interval = 0
        self.hitstun_start_time_pause_interval = 0
    
    # rebind controls function required for when controllers are recognised mid match
    def rebind_controls(self, joystick):
        if self.input == 'keyboard':
            self.left_key = pygame.key.key_code(self.inputlist['left'])
            self.right_key = pygame.key.key_code(self.inputlist['right'])
            self.up_key = pygame.key.key_code(self.inputlist['up'])
            self.down_key = pygame.key.key_code(self.inputlist['down'])
            self.attack1_key = pygame.key.key_code(self.inputlist['attack1'])
            self.attack2_key = pygame.key.key_code(self.inputlist['attack2'])
            self.special_key = pygame.key.key_code(self.inputlist['special'])
            self.block_key = pygame.key.key_code(self.inputlist['block'])
        elif self.input == 'controller':
            self.left_button = self.inputlist['left']
            self.right_button = self.inputlist['right']
            self.up_button = self.inputlist['up']
            self.down_button = self.inputlist['down']
            self.attack1_button = self.inputlist['attack1']
            self.attack2_button = self.inputlist['attack2']
            self.special_button = self.inputlist['special']
            self.block_button = self.inputlist['block']
            self.joystick = joystick
    
    
    # moves character
    def move(self, dx, dy):
        self.y_vel += self.gravity
        dy += self.y_vel
        if self.rect.centerx + dx < self.screen_width * (5/96):
            dx = self.screen_width * (5/96) - self.rect.centerx
        if self.rect.centerx + dx > self.screen_width * (91/96):
            dx = self.screen_width * (91/96) - self.rect.centerx
        if self.rect.bottom + dy > self.screen_height * 5/6:
            self.y_vel = 0
            dy =  self.screen_height * 5/6 - self.rect.bottom
            self.jump = False
            self.jumping_backward = False
            self.jumping_forward = False
            self.jump_attack_count = 1
            if self.jump_attacking == True:
                self.attacking = False
                self.jump_attacking = False
                self.attack_queue = []
            if self.defeated == True:
                self.x_vel = 0
            if self.training_mode == True and self.hitstun == False:
                self.health = 1000
        self.rect.centerx += dx
        self.rect.centery += dy

    # move left
    def move_left(self, vel, back_vel):
        if self.position == 'left':
            self.x_vel = -back_vel
        elif self.position == 'right':
            self.x_vel = -vel

    # move right
    def move_right(self, vel, back_vel):
        if self.position == 'left':
            self.x_vel = vel
        elif self.position == 'right':
            self.x_vel = back_vel
    
    #jump
    def standing_jump(self, jumpspeed):
        self.jump = True
        self.y_vel = -jumpspeed
    def forward_jump(self, jumpspeed):
        self.jumping_forward = True
        self.jump = True
        self.y_vel = -jumpspeed
        # if self.position == 'left':
        #     self.move_right(vel, back_vel)
        # elif self.position == 'right':
        #     self.move_left(vel, back_vel)
    def back_jump(self, jumpspeed):
        self.jumping_backward = True
        self.jump = True
        self.y_vel = -jumpspeed
        # if self.position == 'left':
        #     self.move_left(vel, back_vel)
        # elif self.position == 'right':
        #     self.move_right(vel, back_vel)
    
    # dash
    def forward_dash(self):
        if self.position == 'left':
            self.move_right(self.x_speed * self.dash_multiplier, self.x_back_speed)
        elif self.position == 'right':
            self.move_left(self.x_speed * self.dash_multiplier, self.x_back_speed)
    def backward_dash(self):
        if self.position == 'left':
            self.move_left(self.x_speed, self.x_back_speed * self.dash_multiplier)
        elif self.position == 'right':
            self.move_right(self.x_speed, self.x_back_speed * self.dash_multiplier)
    
    # updates player movement
    def loop(self):
        self.move(self.x_vel, self.y_vel)
        self.update_sprite()

    # updates sprites based on player actions
    def update_sprite(self):
        # if self.jump == True and self.jumping_forward == True:
        #     sprite_sheet = "forward_jump"
        #     self.update_action("forward")
        # elif self.jump == True and self.jumping_backward == True:
        #     sprite_sheet = "backward_jump"
        #     self.update_action("backward")
        if self.defeated == True:
            sprite_sheet = "defeated"
            hitbox_sprite_sheet = 'idle_hitbox'
            # projectile_sprite_sheet = 'idle_hitbox'
            self.update_action("defeated")
        elif self.hitstun == True:
            hitbox_sprite_sheet = 'idle_hitbox'
            # projectile_sprite_sheet = 'idle_hitbox'
            if self.jump == True:
                sprite_sheet = "air_stun"
                self.update_action("air_stun")
            elif self.crouch == True and self.block == True:
                sprite_sheet = "crouch_block_stun"
                self.update_action("crouch_block_stun")
            elif self.block == True:
                sprite_sheet = "block_stun"
                self.update_action("block_stun")
            else:
                sprite_sheet = "idle_stun"
                self.update_action("idle_stun")
        elif self.attacking == True:
            sprite_sheet = self.current_attack
            hitbox_sprite_sheet = self.current_attack + '_hitbox'
            self.update_action(self.current_attack) # updating action sets animation_step to 0, fixes bug where detects animation step of previous action
            if self.current_attack in self.special_attack_set:
                if self.special_attack_set[self.current_attack]['projectile'] == True and self.animation_step == self.special_attack_set[self.current_attack]['projectile_start_frame']:
                    self.current_projectile = self.current_attack
                    self.current_projectile_start_time = time.time()
            #     else:
            #         projectile_sprite_sheet = 'idle_hitbox'
            # else:
            #     projectile_sprite_sheet = 'idle_hitbox'
        elif self.jump == True:
            sprite_sheet = "air"
            hitbox_sprite_sheet = 'idle_hitbox'
            # projectile_sprite_sheet = 'idle_hitbox'
            self.update_action("air")
        elif self.crouch == True and self.block == True:
            sprite_sheet = "crouch_block"
            hitbox_sprite_sheet = 'idle_hitbox'
            # projectile_sprite_sheet = 'idle_hitbox'
            self.update_action("crouch_block")
        elif self.crouch == True:
            sprite_sheet = "crouch"
            hitbox_sprite_sheet = 'idle_hitbox'
            # projectile_sprite_sheet = 'idle_hitbox'
            self.update_action("crouch")
        elif self.block == True:
            sprite_sheet = "block"
            hitbox_sprite_sheet = 'idle_hitbox'
            # projectile_sprite_sheet = 'idle_hitbox'
            self.update_action("block")
        elif self.forward_dashing == True:
            sprite_sheet = "forward_dash"
            hitbox_sprite_sheet = 'idle_hitbox'
            # projectile_sprite_sheet = 'idle_hitbox'
            self.update_action("forward_dash")
        elif self.backward_dashing == True:
            sprite_sheet = "backward_dash"
            hitbox_sprite_sheet = 'idle_hitbox'
            # projectile_sprite_sheet = 'idle_hitbox'
            self.update_action("backward_dash")
        elif abs(self.x_vel) == self.x_speed:
            sprite_sheet = "move_forward"
            hitbox_sprite_sheet = 'idle_hitbox'
            # projectile_sprite_sheet = 'idle_hitbox'
            self.update_action("move_forward")
        elif abs(self.x_vel) == self.x_back_speed:
            sprite_sheet = "move_backward"
            hitbox_sprite_sheet = 'idle_hitbox'
            # projectile_sprite_sheet = 'idle_hitbox'
            self.update_action("move_backward")
        else:
            sprite_sheet = "idle"
            hitbox_sprite_sheet = 'idle_hitbox'
            # projectile_sprite_sheet = 'idle_hitbox'
            self.update_action("idle")
        
        sprite_sheet_name = sprite_sheet + "_" + self.position
        hitbox_sprite_sheet_name = hitbox_sprite_sheet + "_" + self.position
        # projectile_sprite_sheet_name = projectile_sprite_sheet + "_" + self.position
        projectile_sprite_sheet_name = "idle_hitbox_" + self.position
        if self.current_projectile != '':
            projectile_sprites = self.attack_sprites[self.current_projectile + '_projectile_' + self.position]
            self.projectile_travel_frames = int(30 * (time.time() - self.current_projectile_start_time))
        else:
            projectile_sprites = self.sprites[projectile_sprite_sheet_name]
            self.projectile_travel_frames = 0
        if self.attacking == True:
            sprites = self.attack_sprites[sprite_sheet_name]
            hitbox_sprites = self.attack_sprites[hitbox_sprite_sheet_name]
            # if self.current_attack in self.special_attack_set:
            #     if self.special_attack_set[self.current_attack]['projectile'] == True and self.animation_step >= self.special_attack_set[self.current_attack]['projectile_start_frame']:
            #         self.current_projectile = self.current_attack
            #         projectile_sprites = self.attack_sprites[self.current_projectile + '_projectile_' + self.position]
            #         self.projectile_travel_frames = int(30 * (time.time() - self.current_projectile_start_time))
            #     else:
            #         projectile_sprites = self.sprites[projectile_sprite_sheet_name]
                    # self.projectile_travel_frames = 0
            # else:
            #     projectile_sprites = self.sprites[projectile_sprite_sheet_name]
                # self.projectile_travel_frames = 0
        elif self.attacking == False:
            sprites = self.sprites[sprite_sheet_name]
            hitbox_sprites = self.sprites[hitbox_sprite_sheet_name]
            # if self.projectile_travel_frames == 0:
            #     projectile_sprites = self.sprites[projectile_sprite_sheet_name]
            # else:
            #     projectile_sprites = self.attack_sprites[self.current_projectile + '_projectile_' + self.position]
            # if self.current_projectile != '':
            #     projectile_sprites = self.attack_sprites[self.current_projectile + '_projectile_' + self.position]
            # else:
            #     projectile_sprites = self.sprites[projectile_sprite_sheet_name]
        if self.projectile_rect.x < -self.screen_width*(5/24):
            # projectile_sprite_sheet = 'idle_hitbox'
            projectile_sprites = self.sprites[projectile_sprite_sheet_name]
            self.projectile_travel_frames = 0
            self.current_projectile = ''
        if self.projectile_rect.x > self.screen_width*(29/24):
            # projectile_sprite_sheet = 'idle_hitbox'
            projectile_sprites = self.sprites[projectile_sprite_sheet_name]
            self.projectile_travel_frames = 0
            self.current_projectile = ''
        
        # sprite_index = self.animation_step % len(sprites)
        self.animation_step += 1
        if self.animation_step >= len(sprites):
            self.animation_step = 0
            if self.attacking == True:
                self.attacking = False
                self.jump_attacking = False
                self.current_attack = ''
                self.attack_queue.pop(0)
                self.hitcount = 1
        self.hitbox_sprite = hitbox_sprites[self.animation_step]
        self.sprite = sprites[self.animation_step]
        self.projectile_sprite = projectile_sprites[0]
        # self.hitbox_sprite = hitbox_sprites[self.animation_step]
        # self.sprite = sprites[sprite_index]
        # self.animation_step += 1
        self.update()
    
    # updates rect size and mask based on sprite
    def update(self):
        self.rect = self.sprite.get_rect(center=(self.rect.centerx, self.rect.centery))
        if self.position == 'left':
            self.projectile_rect.x = self.rect.x + (self.projectile_travel_frames * 125 * (self.screen_width/1920))
        elif self.position == 'right':
            self.projectile_rect.x = self.rect.x - (self.projectile_travel_frames * 125 * (self.screen_width/1920))
        self.projectile_rect.y = self.rect.y
        self.mask = pygame.mask.from_surface(self.sprite)
        self.hitbox_mask = pygame.mask.from_surface(self.hitbox_sprite)
        self.projectile_mask = pygame.mask.from_surface(self.projectile_sprite)

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.animation_step = 0
        if len(self.action_list) > 10:
            self.action_list.pop(0)
    
    def add_attack(self, attack):
        if len(self.attack_queue) == 0:
            if attack in self.attack_set or attack in self.special_attack_set:
                self.attack_queue.append(attack)
                self.attack_start_time = time.time()
        
        # cancel from basic attack into special attack
        elif attack in self.special_attack_set and (self.attack_queue[-1]) in self.attack_set:
            if time.time() - self.attack_start_time < self.attack_set[self.attack_queue[-1]]['input_frame_duration'] / 30:
                self.attack_queue.append(attack)
        elif (self.attack_queue[-1] + attack) in self.attack_set:
            # if self.animation_step <= self.attack_set[self.attack_queue[-1] + attack]['cancel_frame_index']:
            if time.time() - self.attack_start_time < self.attack_set[self.attack_queue[-1]]['input_frame_duration'] / 30:
                self.attack_queue.append(self.attack_queue[-1] + attack)
        # print(self.attack_queue)
        # self.attack(attack)

    def attack_sequencer(self):
        if len(self.attack_queue) > 0 and self.attack_count == 1:
            self.attack(self.attack_queue[0])
            self.attack_count = 0
        if len(self.attack_queue) > 1 and self.animation_step >= self.attack_set[self.attack_queue[0]]['cancel_frame_index']:
            self.animation_step = 0    # fixes bug where if animation_step is higher than the cancel frame index of the next attack, it skips the next attack
            self.attack_queue.pop(0)
            self.hitcount = 1
            self.attack_count = 1

    def attack(self, attack):
        if self.jump == True and self.jump_attack_count == 0:
            pass
        else:
            self.attacking = True
            self.block = False
            self.crouch = False
            # self.forward_dashing = False
            # self.backward_dashing = False
            self.current_attack = attack
            if self.jump == True:
                self.jump_attacking = True
                self.jump_attack_count = 0
            # if self.attack_set[attack]['x_vel'] == 0:
            #     pass
            # else:
            #     if self.position == 'left':
            #         self.x_vel = self.attack_set[attack]['x_vel'] * (SCREEN_WIDTH/1920)
            #     elif self.position == 'right':
            #         self.x_vel = -self.attack_set[attack]['x_vel'] * (SCREEN_WIDTH/1920)
        # elif self.jump == False:
        #     if self.position == 'left':
        #         self.x_vel = self.attack_set[attack]['x_vel'] * (SCREEN_WIDTH/1920)
        #     elif self.position == 'right':
        #         self.x_vel = -self.attack_set[attack]['x_vel'] * (SCREEN_WIDTH/1920)
        #     self.y_vel = -self.attack_set[attack]['y_vel'] * (SCREEN_HEIGHT/1080)
        #     if self.y_vel < 0:
        #         self.jump = True

    def hit(self, opponent, attack):
        # fixes bug where the hitbox hits an opponent but self.current_attack = '' right after the attack animation has finished
        if attack == '' or self.defeated == True:
            pass
        else:
            self.attacking = False
            self.jump_attacking = False
            self.attack_queue = []
            self.attack_count = 1
            self.current_attack = ''
            # self.hitcount = 1
            self.x_vel = 0
            self.y_vel = 0
            # self.hit_sfx.play()

            # Updates position once hit
            if opponent.rect.centerx > self.rect.centerx:
                self.position = 'left'
            else:
                self.position = 'right'

            if attack in opponent.attack_set:
                opponent_attack_list = opponent.attack_set
            elif attack in opponent.special_attack_set:
                opponent_attack_list = opponent.special_attack_set
                
            if self.jump == True:
                self.hit_sfx.play()
                self.health -= opponent_attack_list[attack]['damage']
                if self.position == 'left':
                    self.x_vel = -opponent_attack_list[attack]['air_knockback_x'] * (self.screen_width/1920)
                elif self.position == 'right':
                    self.x_vel = opponent_attack_list[attack]['air_knockback_x'] * (self.screen_width/1920)
                self.y_vel = -opponent_attack_list[attack]['air_knockback_y'] * (self.screen_height/1080)
                self.hitstun = True
            elif self.block == True:
                self.hit_sfx.play()
                if (self.crouch == True and opponent_attack_list[attack]['type'] == 'overhead') or (self.crouch == False and opponent_attack_list[attack]['type'] == 'low'):
                    self.crouch = False
                    self.block = False
                    self.health -= opponent_attack_list[attack]['damage']
                    self.hitstun_start_time = time.time()
                    self.hitstun_time = opponent_attack_list[attack]['hitstun'] / self.fps
                    if self.position == 'left':
                        self.x_vel = -opponent_attack_list[attack]['knockback_x'] * (self.screen_width/1920)
                    elif self.position == 'right':
                        self.x_vel = opponent_attack_list[attack]['knockback_x'] * (self.screen_width/1920)
                    self.y_vel = -opponent_attack_list[attack]['knockback_y'] * (self.screen_height/1080)
                    if self.y_vel < 0:
                        self.jump = True
                else:
                    self.health -= opponent_attack_list[attack]['damage'] / 4
                    self.hitstun_start_time = time.time()
                    self.hitstun_time = opponent_attack_list[attack]['blockstun'] / self.fps
                    if self.position == 'left':
                        self.x_vel = -opponent_attack_list[attack]['knockback_x'] * (self.screen_width/1920) / 2
                    elif self.position == 'right':
                        self.x_vel = opponent_attack_list[attack]['knockback_x'] * (self.screen_width/1920) / 2
                    self.y_vel = 0
                self.hitstun = True
            elif self.block == False:
                if self.crouch == True and opponent_attack_list[attack]['type'] == 'high':
                    pass
                else:
                    self.hit_sfx.play()
                    self.health -= opponent_attack_list[attack]['damage']
                    self.hitstun_start_time = time.time()
                    self.hitstun_time = opponent_attack_list[attack]['hitstun'] / self.fps
                    if self.position == 'left':
                        self.x_vel = -opponent_attack_list[attack]['knockback_x'] * (self.screen_width/1920)
                    elif self.position == 'right':
                        self.x_vel = opponent_attack_list[attack]['knockback_x'] * (self.screen_width/1920)
                    self.y_vel = -opponent_attack_list[attack]['knockback_y'] * (self.screen_height/1080)
                    if self.y_vel < 0:
                        self.jump = True
                    self.hitstun = True
            if self.health <= 0:
                self.health = 0
                self.defeated = True
                if self.position == 'left':
                    self.x_vel = -15 * (self.screen_width/1920)
                elif self.position == 'right':
                    self.x_vel = 15 * (self.screen_width/1920)
                self.y_vel = -20 * (self.screen_height/1080)
            # print(self.health)
    
    # receives inputs
    def handle_actions(self, hitbox, projectile, opponent, opponent_hitbox, event_list):
        keys = pygame.key.get_pressed()
        if self.defeated == False:
            if pygame.sprite.collide_mask(hitbox, opponent) and self.hitcount == 1:
                if pygame.sprite.collide_mask(opponent_hitbox, self) and opponent.hitcount == 1:
                    opponent.hitcount = 0
                    self.hitcount = 0
                    opponent_current_hit_attack = self.current_attack # extra attack variable to hit the opponent when both players hit each other at the same time, as self.current_attack == '' after self is hit
                    self.hit(opponent, opponent.current_attack)
                    opponent.hit(self, opponent_current_hit_attack) # bug:self.current_attack == ''
                else:
                    self.hitcount = 0
                    opponent.hit(self, self.current_attack)
            if pygame.sprite.collide_mask(projectile, opponent) and self.hitcount == 1:
                # if pygame.sprite.collide_mask(opponent_projectile, self) and opponent.hitcount == 1:
                #     opponent.hitcount = 0
                #     self.hitcount = 0
                #     self.hit(opponent, opponent.current_projectile)
                #     opponent.hit(self, self.current_projectile)
                # else:
                self.hitcount = 0
                opponent.hit(self, self.current_projectile)
            if self.hitstun == True:
                self.forward_dashing = False
                self.backward_dashing = False
                if self.jump == True:
                    pass
                elif time.time() - self.hitstun_start_time > self.hitstun_time:
                    self.hitstun = False
            elif self.hitstun == False:
                self.attack_sequencer()
                if self.attacking == False and self.current_projectile == '':
                    self.attack_count = 1
                    self.hitcount = 1
                    self.x_vel = 0
                elif self.attacking == True:
                    if self.current_attack in self.attack_set:
                        if self.attack_set[self.current_attack]['vel_start_frame_index'] <= self.animation_step <= self.attack_set[self.current_attack]['vel_end_frame_index']:
                            if self.position == 'left':
                                self.x_vel = self.attack_set[self.current_attack]['x_vel'] * (self.screen_width/1920)
                            elif self.position == 'right':
                                self.x_vel = -self.attack_set[self.current_attack]['x_vel'] * (self.screen_width/1920)
                            if self.jump_attacking == False:
                                self.y_vel = -self.attack_set[self.current_attack]['y_vel'] * (self.screen_height/1080)
                            if self.y_vel < 0:
                                self.jump = True
                        else:
                            self.x_vel = 0
                            if self.jump_attacking == False:
                                self.y_vel = 0
                    elif self.current_attack in self.special_attack_set:
                        if self.special_attack_set[self.current_attack]['vel_start_frame_index'] <= self.animation_step <= self.special_attack_set[self.current_attack]['vel_end_frame_index']:
                            if self.position == 'left':
                                self.x_vel = self.special_attack_set[self.current_attack]['x_vel'] * (self.screen_width/1920)
                            elif self.position == 'right':
                                self.x_vel = -self.special_attack_set[self.current_attack]['x_vel'] * (self.screen_width/1920)
                            if self.jump_attacking == False:
                                self.y_vel = -self.special_attack_set[self.current_attack]['y_vel'] * (self.screen_height/1080)
                            if self.y_vel < 0:
                                self.jump = True
                        else:
                            self.x_vel = 0
                            if self.jump_attacking == False:
                                self.y_vel = 0

                if self.jump == True:
                    if self.jumping_forward == True:
                        if self.position == 'left':
                            self.move_right(self.x_speed, self.x_back_speed)
                        elif self.position == 'right':
                            self.move_left(self.x_speed, self.x_back_speed)
                    elif self.jumping_backward == True:
                        if self.position == 'left':
                            self.move_left(self.x_speed, self.x_back_speed)
                        elif self.position == 'right':
                            self.move_right(self.x_speed, self.x_back_speed)
                    for event in event_list:
                        if self.input == 'keyboard' and event.type == pygame.KEYDOWN and self.rect.bottom < self.screen_height * 89/108: # fixes bug where players could use jump attacks on the ground
                            if event.key == self.attack1_key:
                                if self.attacking == False:
                                    self.action_list.append('1')
                                self.add_attack('j1')
                            if event.key == self.attack2_key:
                                if self.attacking == False:
                                    self.action_list.append('2')
                                self.add_attack('j2')
                        if self.input == 'controller' and event.type == pygame.JOYBUTTONDOWN and self.rect.bottom < self.screen_height * 89/108 and event.instance_id == self.joystick.get_instance_id():
                            if event.button == self.attack1_button:
                                if self.attacking == False:
                                    self.action_list.append('1')
                                self.add_attack('j1')
                            if event.button == self.attack2_button:
                                if self.attacking == False:
                                    self.action_list.append('2')
                                self.add_attack('j2')

                elif self.jump == False:
                    if self.forward_dashing:
                        self.crouch = False
                        self.block = False
                        if time.time() - self.dash_start_time > self.dash_time:
                            self.forward_dashing = False
                            self.action_list.append('forward_dash')
                        self.forward_dash()
                    elif self.backward_dashing:
                        self.crouch = False
                        self.block = False
                        if time.time() - self.dash_start_time > self.dash_time:
                            self.backward_dashing = False
                            self.action_list.append('backward_dash')
                        self.backward_dash()
                    else:
                        # updates position only when not attacking
                        if self.attacking == False:
                            if opponent.rect.centerx > self.rect.centerx:
                                self.position = 'left'
                            else:
                                self.position = 'right'

                        for event in event_list:
                            if self.input == 'keyboard' and event.type == pygame.KEYDOWN:
                                if event.key == self.left_key:
                                    if self.position == 'left':
                                        self.action_list.append('move_backward')
                                        if (time.time() - self.backward_dash_input_time) < 0.3 and self.action_list[-2] == 'move_backward':
                                            if self.attacking == False:
                                                self.backward_dashing = True
                                            self.dash_start_time = time.time()
                                        self.backward_dash_input_time = time.time()
                                    elif self.position == 'right':
                                        self.action_list.append('move_forward')
                                        if (time.time() - self.forward_dash_input_time) < 0.3 and self.action_list[-2] == 'move_forward':
                                            if self.attacking == False:
                                                self.forward_dashing = True
                                            self.dash_start_time = time.time()
                                        self.forward_dash_input_time = time.time()
                                if event.key == self.right_key:
                                    if self.position == 'left':
                                        self.action_list.append('move_forward')
                                        if (time.time() - self.forward_dash_input_time) < 0.3 and self.action_list[-2] == 'move_forward':
                                            if self.attacking == False:
                                                self.forward_dashing = True
                                            self.dash_start_time = time.time()
                                        self.forward_dash_input_time = time.time()
                                    elif self.position == 'right':
                                        self.action_list.append('move_backward')
                                        if (time.time() - self.backward_dash_input_time) < 0.3 and self.action_list[-2] == 'move_backward':
                                            if self.attacking == False:
                                                self.backward_dashing = True
                                            self.dash_start_time = time.time()
                                        self.backward_dash_input_time = time.time()
                                if (event.key == self.block_key and self.crouch == True) or (event.key == self.down_key and self.block == True):
                                    self.action_list.append('crouch_block')
                                elif event.key == self.block_key:
                                    self.action_list.append('block')
                                elif event.key == self.down_key:
                                    self.action_list.append('crouch')
                                if event.key == self.up_key:
                                    self.action_list.append('air')

                                if event.key == self.attack1_key and keys[self.up_key] == False: # fixes bug where player can attack and jump at the same time
                                    # crouching attack 1
                                    if self.crouch == True:
                                        if self.attacking == False:
                                            self.action_list.append('1')
                                        if len(self.attack_queue) == 0 and 'c1' in self.attack_set:
                                            self.add_attack('c1')
                                        else:
                                            self.add_attack('1')
                                    # forward attack 1
                                    # elif self.action == 'move_forward':
                                    elif ((self.position == 'left' and keys[self.right_key]) and (keys[self.left_key] == False)) or ((self.position == 'right' and keys[self.left_key]) and (keys[self.right_key] == False)):
                                        if self.attacking == False:
                                            self.action_list.append('1')
                                        if len(self.attack_queue) == 0 and 'f1' in self.attack_set:
                                            self.add_attack('f1')
                                        else:
                                            self.add_attack('1')
                                    # backward attack 1
                                    # elif self.action == 'move_backward':
                                    elif ((self.position == 'left' and keys[self.left_key]) and (keys[self.right_key] == False)) or ((self.position == 'right' and keys[self.right_key]) and (keys[self.left_key] == False)):
                                        if self.attacking == False:
                                            self.action_list.append('1')
                                        if len(self.attack_queue) == 0 and 'b1' in self.attack_set:
                                            self.add_attack('b1')
                                        else:
                                            self.add_attack('1')
                                    # default attack 1
                                    else:
                                        if self.attacking == False:
                                            self.action_list.append('1')
                                        self.add_attack('1')

                                if event.key == self.attack2_key and keys[self.up_key] == False: # fixes bug where player can attack and jump at the same time
                                    # crouching attack 2
                                    if self.crouch == True:
                                        if self.attacking == False:
                                            self.action_list.append('2')
                                        if len(self.attack_queue) == 0 and 'c2' in self.attack_set:
                                            self.add_attack('c2')
                                        else:
                                            self.add_attack('2')
                                    # forward attack 2
                                    # elif self.action == 'move_forward':
                                    elif ((self.position == 'left' and keys[self.right_key]) and (keys[self.left_key] == False)) or ((self.position == 'right' and keys[self.left_key]) and (keys[self.right_key] == False)):
                                        if self.attacking == False:
                                            self.action_list.append('2')
                                        if len(self.attack_queue) == 0 and 'f2' in self.attack_set:
                                            self.add_attack('f2')
                                        else:
                                            self.add_attack('2')
                                    # backward attack 2
                                    # elif self.action == 'move_backward':
                                    elif ((self.position == 'left' and keys[self.left_key]) and (keys[self.right_key] == False)) or ((self.position == 'right' and keys[self.right_key]) and (keys[self.left_key] == False)):
                                        if self.attacking == False:
                                            self.action_list.append('2')
                                        if len(self.attack_queue) == 0 and 'b2' in self.attack_set:
                                            self.add_attack('b2')
                                        else:
                                            self.add_attack('2')
                                    # default attack 2
                                    else:
                                        if self.attacking == False:
                                            self.action_list.append('2')
                                        self.add_attack('2')

                                if event.key == self.special_key:
                                    # crouching special attack
                                    if keys[self.down_key]:
                                        if self.attacking == False:
                                            self.action_list.append('S')
                                        if 'cS' in self.special_attack_set:
                                            self.add_attack('cS')
                                        else:
                                            self.add_attack('S')
                                    # forward special attack
                                    elif ((self.position == 'left' and keys[self.right_key]) and (keys[self.left_key] == False)) or ((self.position == 'right' and keys[self.left_key]) and (keys[self.right_key] == False)):
                                        if self.attacking == False:
                                            self.action_list.append('S')
                                        if 'fS' in self.special_attack_set:
                                            self.add_attack('fS')
                                        else:
                                            self.add_attack('S')
                                    # backward special attack
                                    elif ((self.position == 'left' and keys[self.left_key]) and (keys[self.right_key] == False)) or ((self.position == 'right' and keys[self.right_key]) and (keys[self.left_key] == False)):
                                        if self.attacking == False:
                                            self.action_list.append('S')
                                        if 'bS' in self.special_attack_set:
                                            self.add_attack('bS')
                                        else:
                                            self.add_attack('S')
                                    # default special attack
                                    else:
                                        if self.attacking == False:
                                            self.action_list.append('S')
                                        self.add_attack('S')

                            if self.input == 'controller' and event.type == pygame.JOYBUTTONDOWN and event.instance_id == self.joystick.get_instance_id():
                                if event.button == self.left_button:
                                    if self.position == 'left':
                                        self.action_list.append('move_backward')
                                        if (time.time() - self.backward_dash_input_time) < 0.3 and self.action_list[-2] == 'move_backward':
                                            if self.attacking == False:
                                                self.backward_dashing = True
                                            self.dash_start_time = time.time()
                                        self.backward_dash_input_time = time.time()
                                    elif self.position == 'right':
                                        self.action_list.append('move_forward')
                                        if (time.time() - self.forward_dash_input_time) < 0.3 and self.action_list[-2] == 'move_forward':
                                            if self.attacking == False:
                                                self.forward_dashing = True
                                            self.dash_start_time = time.time()
                                        self.forward_dash_input_time = time.time()
                                if event.button == self.right_button:
                                    if self.position == 'left':
                                        self.action_list.append('move_forward')
                                        if (time.time() - self.forward_dash_input_time) < 0.3 and self.action_list[-2] == 'move_forward':
                                            if self.attacking == False:
                                                self.forward_dashing = True
                                            self.dash_start_time = time.time()
                                        self.forward_dash_input_time = time.time()
                                    elif self.position == 'right':
                                        self.action_list.append('move_backward')
                                        if (time.time() - self.backward_dash_input_time) < 0.3 and self.action_list[-2] == 'move_backward':
                                            if self.attacking == False:
                                                self.backward_dashing = True
                                            self.dash_start_time = time.time()
                                        self.backward_dash_input_time = time.time()
                                if (event.button == self.block_button and self.crouch == True) or (event.button == self.down_button and self.block == True):
                                    self.action_list.append('crouch_block')
                                elif event.button == self.block_button:
                                    self.action_list.append('block')
                                elif event.button == self.down_button:
                                    self.action_list.append('crouch')
                                if event.button == self.up_button:
                                    self.action_list.append('air')

                                if event.button == self.attack1_button and self.joystick.get_button(self.up_button) == False: # fixes bug where player can attack and jump at the same time
                                    # crouching attack 1
                                    if self.crouch == True:
                                        if self.attacking == False:
                                            self.action_list.append('1')
                                        if len(self.attack_queue) == 0 and 'c1' in self.attack_set:
                                            self.add_attack('c1')
                                        else:
                                            self.add_attack('1')
                                    # forward attack 1
                                    # elif self.action == 'move_forward':
                                    elif ((self.position == 'left' and self.joystick.get_button(self.right_button)) and (self.joystick.get_button(self.left_button) == False)) or ((self.position == 'right' and self.joystick.get_button(self.left_button)) and (self.joystick.get_button(self.right_button) == False)):
                                        if self.attacking == False:
                                            self.action_list.append('1')
                                        if len(self.attack_queue) == 0 and 'f1' in self.attack_set:
                                            self.add_attack('f1')
                                        else:
                                            self.add_attack('1')
                                    # backward attack 1
                                    # elif self.action == 'move_backward':
                                    elif ((self.position == 'left' and self.joystick.get_button(self.left_button)) and (self.joystick.get_button(self.right_button) == False)) or ((self.position == 'right' and self.joystick.get_button(self.right_button)) and (self.joystick.get_button(self.left_button) == False)):
                                        if self.attacking == False:
                                            self.action_list.append('1')
                                        if len(self.attack_queue) == 0 and 'b1' in self.attack_set:
                                            self.add_attack('b1')
                                        else:
                                            self.add_attack('1')
                                    # default attack 1
                                    else:
                                        if self.attacking == False:
                                            self.action_list.append('1')
                                        self.add_attack('1')

                                if event.button == self.attack2_button and self.joystick.get_button(self.up_button) == False: # fixes bug where player can attack and jump at the same time
                                    # crouching attack 2
                                    if self.crouch == True:
                                        if self.attacking == False:
                                            self.action_list.append('2')
                                        if len(self.attack_queue) == 0 and 'c2' in self.attack_set:
                                            self.add_attack('c2')
                                        else:
                                            self.add_attack('2')
                                    # forward attack 2
                                    # elif self.action == 'move_forward':
                                    elif ((self.position == 'left' and self.joystick.get_button(self.right_button)) and (self.joystick.get_button(self.left_button) == False)) or ((self.position == 'right' and self.joystick.get_button(self.left_button)) and (self.joystick.get_button(self.right_button) == False)):
                                        if self.attacking == False:
                                            self.action_list.append('2')
                                        if len(self.attack_queue) == 0 and 'f2' in self.attack_set:
                                            self.add_attack('f2')
                                        else:
                                            self.add_attack('2')
                                    # backward attack 2
                                    # elif self.action == 'move_backward':
                                    elif ((self.position == 'left' and self.joystick.get_button(self.left_button)) and (self.joystick.get_button(self.right_button) == False)) or ((self.position == 'right' and self.joystick.get_button(self.right_button)) and (self.joystick.get_button(self.left_button) == False)):
                                        if self.attacking == False:
                                            self.action_list.append('2')
                                        if len(self.attack_queue) == 0 and 'b2' in self.attack_set:
                                            self.add_attack('b2')
                                        else:
                                            self.add_attack('2')
                                    # default attack 2
                                    else:
                                        if self.attacking == False:
                                            self.action_list.append('2')
                                        self.add_attack('2')

                                if event.button == self.special_button:
                                    # crouching special attack
                                    if self.joystick.get_button(self.down_button):
                                        if self.attacking == False:
                                            self.action_list.append('S')
                                        if 'cS' in self.special_attack_set:
                                            self.add_attack('cS')
                                        else:
                                            self.add_attack('S')
                                    # forward special attack
                                    elif ((self.position == 'left' and self.joystick.get_button(self.right_button)) and (self.joystick.get_button(self.left_button) == False)) or ((self.position == 'right' and self.joystick.get_button(self.left_button)) and (self.joystick.get_button(self.right_button) == False)):
                                        if self.attacking == False:
                                            self.action_list.append('S')
                                        if 'fS' in self.special_attack_set:
                                            self.add_attack('fS')
                                        else:
                                            self.add_attack('S')
                                    # backward special attack
                                    elif ((self.position == 'left' and self.joystick.get_button(self.left_button)) and (self.joystick.get_button(self.right_button) == False)) or ((self.position == 'right' and self.joystick.get_button(self.right_button)) and (self.joystick.get_button(self.left_button) == False)):
                                        if self.attacking == False:
                                            self.action_list.append('S')
                                        if 'bS' in self.special_attack_set:
                                            self.add_attack('bS')
                                        else:
                                            self.add_attack('S')
                                    # default special attack
                                    else:
                                        if self.attacking == False:
                                            self.action_list.append('S')
                                        self.add_attack('S')
                        
                        if self.attacking == False:
                            if self.input == 'keyboard':
                                if keys[self.left_key] and self.crouch == False and self.block == False:
                                    self.move_left(self.x_speed, self.x_back_speed)
                                if keys[self.right_key] and self.crouch == False and self.block == False:
                                    self.move_right(self.x_speed, self.x_back_speed)
                                if keys[self.down_key]:
                                    self.crouch = True
                                else:
                                    self.crouch = False
                                if keys[self.block_key]:
                                    self.block = True
                                else:
                                    self.block = False
                                if keys[self.up_key] and keys[self.left_key] and self.jump == False:
                                    if self.position == 'left':
                                        self.back_jump(self.jump_speed)
                                    elif self.position == 'right':
                                        self.forward_jump(self.jump_speed)
                                elif keys[self.up_key] and keys[self.right_key] and self.jump == False:
                                    if self.position == 'left':
                                        self.forward_jump(self.jump_speed)
                                    elif self.position == 'right':
                                        self.back_jump(self.jump_speed)
                                elif keys[self.up_key] and self.jump == False:
                                    self.standing_jump(self.jump_speed)
                            if self.input == 'controller':
                                if self.joystick.get_button(self.left_button) and self.crouch == False and self.block == False:
                                    self.move_left(self.x_speed, self.x_back_speed)
                                if self.joystick.get_button(self.right_button) and self.crouch == False and self.block == False:
                                    self.move_right(self.x_speed, self.x_back_speed)
                                if self.joystick.get_button(self.down_button):
                                    self.crouch = True
                                else:
                                    self.crouch = False
                                if self.joystick.get_button(self.block_button):
                                    self.block = True
                                else:
                                    self.block = False
                                if self.joystick.get_button(self.up_button) and self.joystick.get_button(self.left_button) and self.jump == False:
                                    if self.position == 'left':
                                        self.back_jump(self.jump_speed)
                                    elif self.position == 'right':
                                        self.forward_jump(self.jump_speed)
                                elif self.joystick.get_button(self.up_button) and self.joystick.get_button(self.right_button) and self.jump == False:
                                    if self.position == 'left':
                                        self.forward_jump(self.jump_speed)
                                    elif self.position == 'right':
                                        self.back_jump(self.jump_speed)
                                elif self.joystick.get_button(self.up_button) and self.jump == False:
                                    self.standing_jump(self.jump_speed)

    def draw(self, screen):
        # pygame.draw.rect(screen, (255, 0, 0), self.rect)
        screen.blit(self.sprite, (self.rect.x, self.rect.y))

class Hitbox(pygame.sprite.Sprite):
    def __init__(self, player):
        self.rect = player.rect
        self.rect.center = player.rect.center
        self.mask = None
        self.player = player

        self.sprites = player.sprites
        self.attack_sprites = player.attack_sprites
        self.sprite = player.hitbox_sprite
    
    # updates sprites, rect size and mask
    def loop(self):
        self.sprite = self.player.hitbox_sprite
        self.rect = self.player.rect
        self.mask = self.player.hitbox_mask

    def draw(self, screen):
        # pygame.draw.rect(screen, (255, 0, 0), self.rect)
        screen.blit(self.sprite, (self.rect.x, self.rect.y))

class Projectile(pygame.sprite.Sprite):
    def __init__(self, player):
        self.rect = player.projectile_rect
        self.rect.center = player.projectile_rect.center
        self.mask = None
        self.player = player

        self.sprites = player.sprites
        self.attack_sprites = player.attack_sprites
        self.sprite = player.projectile_sprite
    
    # updates sprites, rect size and mask
    def loop(self):
        self.sprite = self.player.projectile_sprite
        self.rect = self.player.projectile_rect
        self.mask = self.player.projectile_mask

    def draw(self, screen):
        # pygame.draw.rect(screen, (255, 0, 0), self.rect)
        screen.blit(self.sprite, (self.rect.x, self.rect.y))