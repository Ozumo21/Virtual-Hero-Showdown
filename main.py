import os
import pygame, sys
import time
import json
from os import listdir
from os.path import isfile, join
from screeninfo import get_monitors     # required because pygame display info bugs out and returns incorrect screen sizes
from pygame import mixer
from fighters import Fighter, Hitbox, Projectile
from attacks import fighter_red_attacks, red_attacks, yellow_attacks, red_special_attacks, yellow_special_attacks


# Default aspect ratio = 1920 x 1080

# centre the screen
os.environ['SDL_VIDEO_CENTERED'] = '1'

# initialise Pygame
mixer.init()
pygame.init()
pygame.joystick.init()

# hide mouse
pygame.mouse.set_visible(False)

# load game options
def load_options(option_file):
    with open(os.path.join(option_file), 'r+') as file:
        options = json.load(file)
    return options

options = load_options("options.json")
settings = options["settings"]
player1_keyboard = options["player1_keyboard"]
player2_keyboard = options["player2_keyboard"]
player1_input_device = 'keyboard'
player2_input_device = 'keyboard'
music_volume = settings["music_volume"]
sfx_volume = settings["sfx_volume"]

# store controllers
joysticks = {}
player1_joystick = None
player2_joystick = None
player_joysticks = [player1_joystick, player2_joystick]

# controller keybinds in terms of playstation controller button numbers
controller_keybinds = {
    'left': 13,
    'right': 14,
    'up': 11,
    'down': 12,
    'attack1': 2,
    'attack2': 0, 
    'special': 3,
    'block': 1
}

# save game options
def save_options(option_file):
    new_options = {
        "settings": settings,
        "player1_keyboard": player1_keyboard,
        "player2_keyboard": player2_keyboard
    }
    with open(os.path.join(option_file), 'w') as file:
        json.dump(new_options, file)

# save_options("options.json")

# set caption and screen size
monitors = get_monitors() # gets correct screen sizes
for monitor in monitors:
    if monitor.is_primary:
        SCREEN_WIDTH = monitor.width # constant screen_width of display
        SCREEN_HEIGHT = monitor.height # constant screen_height of display
# print(SCREEN_WIDTH, SCREEN_HEIGHT)

# variable screen width, height for game
if settings['windowed_mode'] == 'windowed':
    screen_width = settings['screen_resolution'][0]
    screen_height = settings['screen_resolution'][1]
else:
    screen_width = SCREEN_WIDTH
    screen_height = SCREEN_HEIGHT
    
pygame.display.set_caption("Virtual Hero Showdown")
if settings['windowed_mode'] == 'fullscreen':
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode((screen_width, screen_height))


# variables
FPS = 30
# music_volume = 10
# sfx_volume = 10

# initialise player characters
def initialise_characters():
    fighter_red = {
        'name': "Fighter_Red",
        'speed': screen_width/192,
        'backspeed': screen_width/240,
        'jumpspeed': screen_height/36,
        'attacks': fighter_red_attacks
    }
    red_enforcer = {
        'name': "Red_Enforcer",
        'speed': screen_width/192,
        'backspeed': screen_width/240,
        'jumpspeed': screen_height/36,
        'attacks': fighter_red_attacks
    }
    red = {
        'name': "Red",
        'speed': screen_width/180,
        'backspeed': screen_width * (3/700),
        'jumpspeed': screen_height/36,
        'dash_multiplier': 4,
        'dash_time': 0.15,
        'attacks': red_attacks,
        'special_attacks': red_special_attacks
    }
    yellow = {
        'name': "Yellow",
        'speed': screen_width/270,
        'backspeed': screen_width/350,
        'jumpspeed': screen_height/36,
        'dash_multiplier': 3,
        'dash_time': 0.3,
        'attacks': yellow_attacks,
        'special_attacks': yellow_special_attacks
    }
    characters = [fighter_red, red_enforcer, red, yellow]
    return characters
characters = initialise_characters()

# load music and sounds
pygame.mixer.music.load(join("assets", "audio", "music", "menu_bgm.mp3"))
pygame.mixer.music.set_volume(music_volume / 10)
pygame.mixer.music.play(-1, 0.0, 0)
hit_fx = pygame.mixer.Sound(join("assets", "audio", "sfx", "hit.mp3"))
menu_navigate_fx = pygame.mixer.Sound(join("assets", "audio", "sfx", "menu_navigate.mp3"))
menu_select_fx = pygame.mixer.Sound(join("assets", "audio", "sfx", "menu_select.mp3"))
menu_return_fx = pygame.mixer.Sound(join("assets", "audio", "sfx", "menu_return.mp3"))
def initialise_sfx_volume():
    hit_fx.set_volume(sfx_volume / 10)
    menu_navigate_fx.set_volume(sfx_volume / 10)
    menu_select_fx.set_volume(sfx_volume / 10)
    menu_return_fx.set_volume(sfx_volume / 10)
initialise_sfx_volume()

sfx = [hit_fx]

# load background images
void_bg = pygame.image.load(join("assets", "images", "backgrounds", "void.jpg")).convert_alpha()
secret_facility_alt_bg = pygame.image.load(join("assets", "images", "backgrounds", "secret_facility_alt.jpg")).convert_alpha()
secret_facility_bg = pygame.image.load(join("assets", "images", "backgrounds", "secret_facility.jpg")).convert_alpha()
studio_bg = pygame.image.load(join("assets", "images", "backgrounds", "studio.jpg")).convert_alpha()
virtual_grid_alt_bg = pygame.image.load(join("assets", "images", "backgrounds", "virtual_grid_alt.jpg")).convert_alpha()
virtual_grid_bg = pygame.image.load(join("assets", "images", "backgrounds", "virtual_grid.jpg")).convert_alpha()

menu_bg = pygame.image.load(join("assets", "images", "ui", "main_menu.png")).convert_alpha()
stage_bg = studio_bg

# load ui images
pause_image = pygame.image.load(join("assets", "images", "ui", "pause.png")).convert_alpha()
fight_image = pygame.image.load(join("assets", "images", "ui", "Fight.png")).convert_alpha()
menu_panel_image = pygame.image.load(join("assets", "images", "ui", "menu_panel.png")).convert_alpha()
# settings_panel_selection_bars_image = pygame.image.load(join("assets", "images", "ui", "settings_panel_selection_bars.png")).convert_alpha()
settings_panel_image = pygame.image.load(join("assets", "images", "ui", "settings_panel.png")).convert_alpha()
settings_panel_set_text_image = pygame.image.load(join("assets", "images", "ui", "settings_panel_set_text.png")).convert_alpha()
controls_panel_image = pygame.image.load(join("assets", "images", "ui", "controls_panel.png")).convert_alpha()
controls_panel_icons_image = pygame.image.load(join("assets", "images", "ui", "controls_panel_icons.png")).convert_alpha()
fight_select_panel_image = pygame.image.load(join("assets", "images", "ui", "fight_select_panel.png")).convert_alpha()
player1_selector_image = pygame.image.load(join("assets", "images", "ui", "player1_selector.png")).convert_alpha()
player2_selector_image = pygame.image.load(join("assets", "images", "ui", "player2_selector.png")).convert_alpha()
move_list_image = pygame.image.load(join("assets", "images", "ui", "move_list.png")).convert_alpha()
tutorial_image = pygame.image.load(join("assets", "images", "ui", "tutorial_panel.png")).convert_alpha()
end_screen_image = pygame.image.load(join("assets", "images", "ui", "fight_end_screen.png")).convert_alpha()

# load fonts
main_menu_font = pygame.font.Font(r"assets\fonts\Alien-Encounters-Regular.ttf", int(screen_width / 19.2))
main_submenu_font = pygame.font.Font(r"assets\fonts\Alien-Encounters-Regular.ttf", int(screen_width / 24))
menu_panel_font = pygame.font.Font(r"assets\fonts\Alien-Encounters-Regular.ttf", int(screen_width / 24))
round_font = pygame.font.Font(r"assets\fonts\Alien-Encounters-Regular.ttf", int(screen_width / 12))
timer_font = pygame.font.Font(r"assets\fonts\Alien-Encounters-Regular.ttf", int(screen_width / 16))
settings_options_font = pygame.font.Font(r"assets\fonts\Alien-Encounters-Regular.ttf", int(screen_width / 38.4))
player_ready_font = pygame.font.Font(r"assets\fonts\Alien-Encounters-Regular.ttf", int(screen_width / (128/3)))
end_screen_font = pygame.font.Font(r"assets\fonts\Alien-Encounters-Regular.ttf", int(screen_width / 12.8))

def initialise_fonts():
    global main_menu_font
    global main_submenu_font
    global menu_panel_font
    global round_font
    global timer_font
    global settings_options_font
    global player_ready_font
    main_menu_font = pygame.font.Font(r"assets\fonts\Alien-Encounters-Regular.ttf", int(screen_width / 19.2))
    main_submenu_font = pygame.font.Font(r"assets\fonts\Alien-Encounters-Regular.ttf", int(screen_width / 24))
    menu_panel_font = pygame.font.Font(r"assets\fonts\Alien-Encounters-Regular.ttf", int(screen_width / 24))
    round_font = pygame.font.Font(r"assets\fonts\Alien-Encounters-Regular.ttf", int(screen_width / 12))
    timer_font = pygame.font.Font(r"assets\fonts\Alien-Encounters-Regular.ttf", int(screen_width / 16))
    settings_options_font = pygame.font.Font(r"assets\fonts\Alien-Encounters-Regular.ttf", int(screen_width / 38.4))
    player_ready_font = pygame.font.Font(r"assets\fonts\Alien-Encounters-Regular.ttf", int(screen_width / (128/3)))

def draw_text(text, font, colour, centerx, centery):
    text = font.render(text, True, colour)
    x = centerx - (text.get_width() / 2)
    y = centery - (text.get_height() / 2)
    screen.blit(text, (x, y))

def draw_text_topleft(text, font, colour, x, y):
    text = font.render(text, True, colour)
    screen.blit(text, (x, y))

# draw background
def draw_background(bg_image, width, height):
    # bg_image = pygame.image.load(join("assets", "images", "backgrounds", name)).convert_alpha()
    scaled_bg = pygame.transform.scale(bg_image, (width, height))

    # fit the image to screen (by height)
    # scaled_width = bg_image.get_width() * (height / bg_image.get_height())
    # scaled_bg = pygame.transform.scale(bg_image, (scaled_width, height))

    # center the image
    # scaled_bg_rect = scaled_bg.get_rect()
    # scaled_bg_rect.center = (width/2, height/2)

    # screen.blit(scaled_bg, (scaled_bg_rect))
    screen.blit(scaled_bg, (0, 0))

def draw_image(image, centerx, centery, width, height):
    # image = pygame.image.load(join("assets", "images", "ui", name)).convert_alpha()
    scaled_img = pygame.transform.scale(image, (width, height))
    screen.blit(scaled_img, (centerx - (width / 2), centery - (height / 2)))

# draw healthbar
def draw_healthbar(playerid, health, x, y):
    border_rect = pygame.Rect(0, 0, screen_width * (3/8), screen_height * (7/108))
    health_rect = pygame.Rect(0, 0, screen_width * (35/96) * (health/1000), screen_height * (5/108))
    if playerid == 1:
        border_rect.topright = (x, y)
        health_rect.topright = (x - screen_width * (1/192), y + screen_height * (1/108))
    elif playerid == 2:
        border_rect.topleft = (x, y)
        health_rect.topleft = (x + screen_width * (1/192), y + screen_height * (1/108))
    pygame.draw.rect(screen, (0, 0, 0), border_rect)
    pygame.draw.rect(screen, (255, 255 * (health / 1000), 0), health_rect)

# draw rectangle
def draw_rectangle(x, y, width, height, colour):
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, colour, rect)

def fight(player1, player2, player1_hitbox, player2_hitbox, player1_projectile, player2_projectile):
    draw_background(stage_bg, screen_width, screen_height)
    draw_healthbar(1, player1.health, screen_width * (5/12), screen_height * (1/18))
    draw_healthbar(2, player2.health, screen_width * (7/12), screen_height * (1/18))

    # displays both players
    player1.draw(screen)
    player1_hitbox.draw(screen)
    player1_projectile.draw(screen)
    player2.draw(screen)
    player2_hitbox.draw(screen)
    player2_projectile.draw(screen)

    # updates player movement
    # player1.loop()
    # player2.loop()
    # player1_hitbox.loop()
    # player2_hitbox.loop()

def pause(player):
    player.pause = True
    player.dash_start_time_pause_interval = time.time() - player.dash_start_time
    player.forward_dash_input_time_pause_interval = time.time() - player.forward_dash_input_time
    player.backward_dash_input_time_pause_interval = time.time() - player.backward_dash_input_time
    player.attack_start_time_pause_interval = time.time() - player.attack_start_time
    player.hitstun_start_time_pause_interval = time.time() - player.hitstun_start_time

def unpause(player):
    player.pause = False
    player.dash_start_time = time.time() - player.dash_start_time_pause_interval
    player.forward_dash_input_time = time.time() - player.forward_dash_input_time_pause_interval
    player.backward_dash_input_time = time.time() - player.backward_dash_input_time_pause_interval
    player.attack_start_time = time.time() - player.attack_start_time_pause_interval
    player.hitstun_start_time = time.time() - player.hitstun_start_time_pause_interval

# sets player state to default when round is timeout
def timeout(player):
    player.x_vel = 0
    player.hitstun = False
    player.attacking = False
    player.crouch = False
    player.block = False
    player.forward_dashing = False
    player.backward_dashing = False

# main loop
def main():
    clock = pygame.time.Clock()

    run = True
    game_state = 'menu'
    global screen_width
    global screen_height
    global screen
    global characters
    global music_volume
    global sfx_volume
    global player1_keyboard
    global player2_keyboard
    global player1_input_device
    global player2_input_device
    global player1_joystick
    global player2_joystick
    global stage_bg
    
    player1 = None
    player2 = None
    
    main_menu_options = ['fight', 'help', 'options', 'exit']
    main_menu_hover_option = 'fight'
    main_menu_selected_option = ''
    
    fight_panel_characters = [characters[2], characters[3]]
    fight_panel_player1_hover_character = characters[2]
    fight_panel_player2_hover_character = characters[3]
    fight_panel_player1_selected_character = ''
    fight_panel_player2_selected_character = ''
    fight_panel_selection_type = 'character'
    
    stage_selections = ['1', '2', '3', '4']
    stage_hover_selection = '1'
    
    pause_menu_options = ['resume', 'move list', 'main menu']
    pause_menu_hover_option = 'resume'
    move_list_selected = False
    
    end_screen_menu_options = ['play again', 'main menu']
    end_screen_hover_option = 'play again'
    
    help_submenu_options = ['training', 'tutorial']
    help_submenu_hover_option = 'training'
    help_submenu_selected_option = ''
    
    training_mode = False
    
    options_submenu_options = ['settings', 'controls']
    options_submenu_hover_option = 'settings'
    options_submenu_selected_option = ''
    
    settings_panel_options = ['resolution', 'window_mode', 'music', 'sfx']
    settings_panel_hover_option = 'resolution'
    settings_panel_selected_option = ''

    screen_resolution_options = [[960, 540], [1280, 720], [1280, 800], [1600, 900], [1600, 1000], [1920, 1080], [1920, 1200], [2560, 1440], [2560, 1600], [3840, 2160], [3840, 2400]]
    all_resolutions = [[960, 540], [1280, 720], [1280, 800], [1600, 900], [1600, 1000], [1920, 1080], [1920, 1200], [2560, 1440], [2560, 1600], [3840, 2160], [3840, 2400]]
    for resolution in all_resolutions:
        if resolution[0] > SCREEN_WIDTH or resolution[1] > SCREEN_HEIGHT:
            screen_resolution_options.remove(resolution)
    screen_resolution_hover_option = screen_resolution_options[screen_resolution_options.index(settings["screen_resolution"])]
    
    window_mode_options = ['windowed', 'borderless', 'fullscreen']
    window_mode_hover_option = window_mode_options[window_mode_options.index(settings["windowed_mode"])]
    
    music_volume_options = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    music_volume_hover_option = music_volume_options[music_volume_options.index(settings["music_volume"])]
    
    sfx_volume_options = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    sfx_volume_hover_option = sfx_volume_options[sfx_volume_options.index(settings["sfx_volume"])]
    
    controls_panel_keybinds = ['up', 'left', 'down', 'right', 'attack1', 'attack2', 'special', 'block']
    controls_panel_player1_keybind_inputs = [player1_keyboard['up'], player1_keyboard['left'], player1_keyboard['down'], player1_keyboard['right'], player1_keyboard['attack1'], player1_keyboard['attack2'], player1_keyboard['special'], player1_keyboard['block']]
    controls_panel_player2_keybind_inputs = [player2_keyboard['up'], player2_keyboard['left'], player2_keyboard['down'], player2_keyboard['right'], player2_keyboard['attack1'], player2_keyboard['attack2'], player2_keyboard['special'], player2_keyboard['block']]
    controls_panel_controller_button_inputs = ['Dpad up', 'Dpad left', 'Dpad down', 'Dpad right', 'square', 'triangle', 'cross', 'circle'] 
    controls_panel_player1_hover_keybind = 'up'
    controls_panel_player2_hover_keybind = 'up'
    controls_panel_player1_selected_keybind = ''
    controls_panel_player2_selected_keybind = ''

    # round_state = 'start'
    # round_number = 1
    # round_start_time = time.time()
    # round_end_time = 0
    # timer_duration = 99
    # round_timer = 0
    # round_time_pause_interval = 0

    player1_wins = 0
    player2_wins = 0
    player_victory = ''

    while run:
        clock.tick(FPS)
        event_list = pygame.event.get()

        # update background based on screen size (for testing purposes only, needs to be removed later on)
        # screen_width, screen_height = screen.get_size()
        
        # if len(joysticks) >= 2:
        #     player1_input_device = 'controller'
        #     player2_input_device = 'controller'
        #     player1_joystick = joysticks[list(joysticks.keys())[0]]
        #     player2_joystick = joysticks[list(joysticks.keys())[1]]
        # elif len(joysticks) == 1:
        #     player1_input_device = 'controller'
        #     player2_input_device = 'keyboard'
        #     player1_joystick = joysticks[list(joysticks.keys())[0]]
        #     player2_joystick = None
        # elif len(joysticks) == 0:
        #     player1_input_device = 'keyboard'
        #     player2_input_device = 'keyboard'
        #     player1_joystick = None
        #     player2_joystick = None
        
        if game_state == 'menu':
            draw_background(menu_bg, screen_width, screen_height)
            for option in main_menu_options:
                if option == main_menu_hover_option:
                    draw_text_topleft(option, main_menu_font, (255, 255, 0), screen_width/38.4, screen_height * ((19/54) + (main_menu_options.index(option)) * (4/27)))
                else:
                    draw_text_topleft(option, main_menu_font, (255, 255, 255), screen_width/38.4, screen_height * ((19/54) + (main_menu_options.index(option)) * (4/27)))
            if main_menu_selected_option == '':
                for event in event_list:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.key.key_code('s') or event.key == pygame.key.key_code('down'):
                            main_menu_hover_option = main_menu_options[main_menu_options.index(main_menu_hover_option) - 3]
                            menu_navigate_fx.play()
                        if event.key == pygame.key.key_code('w') or event.key == pygame.key.key_code('up'):
                            main_menu_hover_option = main_menu_options[main_menu_options.index(main_menu_hover_option) - 1]
                            menu_navigate_fx.play()
                        if event.key == pygame.key.key_code('return') or event.key == pygame.key.key_code('space'):
                            main_menu_selected_option = main_menu_hover_option
                            menu_select_fx.play()

                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.button == 12:
                            main_menu_hover_option = main_menu_options[main_menu_options.index(main_menu_hover_option) - 3]
                            menu_navigate_fx.play()
                        if event.button == 11:
                            main_menu_hover_option = main_menu_options[main_menu_options.index(main_menu_hover_option) - 1]
                            menu_navigate_fx.play()
                        if event.button == 0:
                            main_menu_selected_option = main_menu_hover_option
                            menu_select_fx.play()

            elif main_menu_selected_option == 'fight':
                draw_image(fight_select_panel_image, screen_width/(128/95), screen_height/(27/13), screen_width/(192/85), screen_height/(6/5))
                for character in fight_panel_characters:
                    if character == fight_panel_player1_hover_character:
                        draw_image(player1_selector_image, screen_width*((65/96) + fight_panel_characters.index(character) * (25/192)), screen_height/(36/11), screen_width/(64/5), screen_height/(36/5))
                    if character == fight_panel_player2_hover_character:
                        draw_image(player2_selector_image, screen_width*((65/96) + fight_panel_characters.index(character) * (25/192)), screen_height/(36/11), screen_width/(64/5), screen_height/(36/5))
                if fight_panel_player1_selected_character != '':
                    draw_text('player 1 ready', player_ready_font, (255, 255, 0), screen_width/(128/81), screen_height/(108/47))
                if fight_panel_player2_selected_character != '':
                    draw_text('player 2 ready', player_ready_font, (255, 255, 0), screen_width/(48/41), screen_height/(108/47))
                if fight_panel_selection_type == 'character':
                    if fight_panel_player1_selected_character != '':
                        for event in event_list:
                            if player1_input_device == 'keyboard' and event.type == pygame.KEYDOWN:
                                if event.key == pygame.key.key_code('escape'):
                                    fight_panel_player1_selected_character = ''
                                    menu_return_fx.play()
                            if player1_input_device == 'controller' and event.type == pygame.JOYBUTTONDOWN:
                                if player1_joystick.get_button(1):
                                    fight_panel_player1_selected_character = ''
                                    menu_return_fx.play()
                    elif fight_panel_player1_selected_character == '':
                        for event in event_list:
                            if player1_input_device == 'keyboard' and event.type == pygame.KEYDOWN:
                                if event.key == pygame.key.key_code('a') or event.key == pygame.key.key_code('d'):
                                    fight_panel_player1_hover_character = fight_panel_characters[fight_panel_characters.index(fight_panel_player1_hover_character) - 1]
                                    menu_navigate_fx.play()
                                if event.key == pygame.key.key_code('space'):
                                    fight_panel_player1_selected_character = fight_panel_player1_hover_character
                                    if fight_panel_player2_selected_character != '':
                                        fight_panel_selection_type = 'stage'
                                    menu_select_fx.play()
                                if event.key == pygame.key.key_code('escape'):
                                    main_menu_selected_option = ''
                                    fight_panel_player1_hover_character = characters[2]
                                    fight_panel_player2_hover_character = characters[3]
                                    fight_panel_player1_selected_character = ''
                                    fight_panel_player2_selected_character = ''
                                    menu_return_fx.play()
                            if player1_input_device == 'controller' and event.type == pygame.JOYBUTTONDOWN:
                                if player1_joystick.get_button(13) or player1_joystick.get_button(14):
                                    fight_panel_player1_hover_character = fight_panel_characters[fight_panel_characters.index(fight_panel_player1_hover_character) - 1]
                                    menu_navigate_fx.play()
                                if player1_joystick.get_button(0):
                                    fight_panel_player1_selected_character = fight_panel_player1_hover_character
                                    if fight_panel_player2_selected_character != '':
                                        fight_panel_selection_type = 'stage'
                                    menu_select_fx.play()
                                if player1_joystick.get_button(1):
                                    main_menu_selected_option = ''
                                    fight_panel_player1_hover_character = characters[2]
                                    fight_panel_player2_hover_character = characters[3]
                                    fight_panel_player1_selected_character = ''
                                    fight_panel_player2_selected_character = ''
                                    menu_return_fx.play()
                    if fight_panel_player2_selected_character != '':
                        for event in event_list:
                            if player2_input_device == 'keyboard' and event.type == pygame.KEYDOWN:
                                if event.key == pygame.key.key_code('backspace'):
                                    fight_panel_player2_selected_character = ''
                                    menu_return_fx.play()
                            if player2_input_device == 'controller' and event.type == pygame.JOYBUTTONDOWN:
                                if player2_joystick.get_button(1):
                                    fight_panel_player2_selected_character = ''
                                    menu_return_fx.play()
                    elif fight_panel_player2_selected_character == '':
                        for event in event_list:
                            if player2_input_device == 'keyboard' and event.type == pygame.KEYDOWN:
                                if event.key == pygame.key.key_code('left') or event.key == pygame.key.key_code('right'):
                                    fight_panel_player2_hover_character = fight_panel_characters[fight_panel_characters.index(fight_panel_player2_hover_character) - 1]
                                    menu_navigate_fx.play()
                                if event.key == pygame.key.key_code('return'):
                                    fight_panel_player2_selected_character = fight_panel_player2_hover_character
                                    if fight_panel_player1_selected_character != '':
                                        fight_panel_selection_type = 'stage'
                                    menu_select_fx.play()
                                if event.key == pygame.key.key_code('backspace'):
                                    main_menu_selected_option = ''
                                    fight_panel_player1_hover_character = characters[2]
                                    fight_panel_player2_hover_character = characters[3]
                                    fight_panel_player1_selected_character = ''
                                    fight_panel_player2_selected_character = ''
                                    menu_return_fx.play()
                            if player2_input_device == 'controller' and event.type == pygame.JOYBUTTONDOWN:
                                if player2_joystick.get_button(13) or player2_joystick.get_button(14):
                                    fight_panel_player2_hover_character = fight_panel_characters[fight_panel_characters.index(fight_panel_player2_hover_character) - 1]
                                    menu_navigate_fx.play()
                                if player2_joystick.get_button(0):
                                    fight_panel_player2_selected_character = fight_panel_player2_hover_character
                                    if fight_panel_player1_selected_character != '':
                                        fight_panel_selection_type = 'stage'
                                    menu_select_fx.play()
                                if player2_joystick.get_button(1):
                                    main_menu_selected_option = ''
                                    fight_panel_player1_hover_character = characters[2]
                                    fight_panel_player2_hover_character = characters[3]
                                    fight_panel_player1_selected_character = ''
                                    fight_panel_player2_selected_character = ''
                                    menu_return_fx.play()
                elif fight_panel_selection_type == 'stage':
                    for stage in stage_selections:
                        if stage == stage_hover_selection:
                            draw_text(stage, main_menu_font, (255, 255, 0), screen_width * ((75/128) + stage_selections.index(stage) * (5/48)), screen_height/(54/35))
                            if stage == '1':
                                draw_text('studio', player_ready_font, (255, 255, 255), screen_width/(128/95), screen_height/(24/19))
                            elif stage == '2':
                                draw_text('void', player_ready_font, (255, 255, 255), screen_width/(128/95), screen_height/(24/19))
                            elif stage == '3':
                                draw_text('secret facility', player_ready_font, (255, 255, 255), screen_width/(128/95), screen_height/(24/19))
                            elif stage == '4':
                                draw_text('virtual grid', player_ready_font, (255, 255, 255), screen_width/(128/95), screen_height/(24/19))
                        else:
                            draw_text(stage, main_menu_font, (255, 255, 255), screen_width * ((75/128) + stage_selections.index(stage) * (5/48)), screen_height/(54/35))
                    for event in event_list:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.key.key_code('a') or event.key == pygame.key.key_code('left'):
                                stage_hover_selection = stage_selections[stage_selections.index(stage_hover_selection) - 1]
                                menu_navigate_fx.play()
                            if event.key == pygame.key.key_code('d') or event.key == pygame.key.key_code('right'):
                                stage_hover_selection = stage_selections[stage_selections.index(stage_hover_selection) - 3]
                                menu_navigate_fx.play()
                            if event.key == pygame.key.key_code('space') or event.key == pygame.key.key_code('return'):
                                menu_select_fx.play()
                                player1_character = fight_panel_player1_selected_character
                                player2_character = fight_panel_player2_selected_character
                                if stage_hover_selection == '1':
                                    stage_bg = studio_bg
                                    pygame.mixer.music.load(join("assets", "audio", "music", "studio_bgm.mp3"))
                                elif stage_hover_selection == '2':
                                    stage_bg = void_bg
                                    pygame.mixer.music.load(join("assets", "audio", "music", "void_bgm.mp3"))
                                elif stage_hover_selection == '3':
                                    if player1_character == characters[3] or player2_character == characters[3]:
                                        stage_bg = secret_facility_alt_bg
                                    else:
                                        stage_bg = secret_facility_bg
                                    pygame.mixer.music.load(join("assets", "audio", "music", "secret_facility_bgm.mp3"))
                                elif stage_hover_selection == '4':
                                    if player1_character == characters[3] or player2_character == characters[3]:
                                        stage_bg = virtual_grid_alt_bg
                                    else:
                                        stage_bg = virtual_grid_bg
                                    pygame.mixer.music.load(join("assets", "audio", "music", "virtual_grid_bgm.mp3"))
                                fight_panel_player1_selected_character = ''
                                fight_panel_player2_selected_character = ''
                                stage_hover_selection = '1'
                                main_menu_selected_option = ''
                                pause_menu_hover_option = 'resume'
                                fight_panel_selection_type = 'character'
                                training_mode = False
                                if player1_input_device == 'keyboard':
                                    player1 = Fighter(screen_width * 2/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 1, 'left', player1_input_device, player1_keyboard, player1_character, FPS, sfx, screen_width, screen_height, training_mode, player1_joystick)
                                elif player1_input_device == 'controller':
                                    player1 = Fighter(screen_width * 2/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 1, 'left', player1_input_device, controller_keybinds, player1_character, FPS, sfx, screen_width, screen_height, training_mode, player1_joystick)
                                if player2_input_device == 'keyboard':
                                    player2 = Fighter(screen_width * 3/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 2, 'right', player2_input_device, player2_keyboard, player2_character, FPS, sfx, screen_width, screen_height, training_mode, player2_joystick)
                                elif player2_input_device == 'controller':
                                    player2 = Fighter(screen_width * 3/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 2, 'right', player2_input_device, controller_keybinds, player2_character, FPS, sfx, screen_width, screen_height, training_mode, player2_joystick)
                                pygame.mixer.music.play(-1, 0.0, 0)
                                player1_hitbox = Hitbox(player1)
                                player2_hitbox = Hitbox(player2)
                                player1_projectile = Projectile(player1)
                                player2_projectile = Projectile(player2)
                                game_state = 'fight'
                                round_state = 'start'
                                round_number = 1
                                round_start_time = time.time()
                                round_end_time = 0
                                timer_duration = 99
                                round_timer = 0
                                round_time_pause_interval = 0
                                player1_wins = 0
                                player2_wins = 0
                                player_victory = ''
                            if event.key == pygame.key.key_code('escape') or event.key == pygame.key.key_code('backspace'):
                                fight_panel_selection_type = 'character'
                                stage_hover_selection = '1'
                                fight_panel_player1_selected_character = ''
                                fight_panel_player2_selected_character = ''
                                menu_return_fx.play()
                        if event.type == pygame.JOYBUTTONDOWN:
                            if event.button == 13:
                                stage_hover_selection = stage_selections[stage_selections.index(stage_hover_selection) - 1]
                                menu_navigate_fx.play()
                            if event.button == 14:
                                stage_hover_selection = stage_selections[stage_selections.index(stage_hover_selection) - 3]
                                menu_navigate_fx.play()
                            if event.button == 0:
                                menu_select_fx.play()
                                player1_character = fight_panel_player1_selected_character
                                player2_character = fight_panel_player2_selected_character
                                if stage_hover_selection == '1':
                                    stage_bg = studio_bg
                                    pygame.mixer.music.load(join("assets", "audio", "music", "studio_bgm.mp3"))
                                elif stage_hover_selection == '2':
                                    stage_bg = void_bg
                                    pygame.mixer.music.load(join("assets", "audio", "music", "void_bgm.mp3"))
                                elif stage_hover_selection == '3':
                                    if player1_character == characters[3] or player2_character == characters[3]:
                                        stage_bg = secret_facility_alt_bg
                                    else:
                                        stage_bg = secret_facility_bg
                                    pygame.mixer.music.load(join("assets", "audio", "music", "secret_facility_bgm.mp3"))
                                elif stage_hover_selection == '4':
                                    if player1_character == characters[3] or player2_character == characters[3]:
                                        stage_bg = virtual_grid_alt_bg
                                    else:
                                        stage_bg = virtual_grid_bg
                                    pygame.mixer.music.load(join("assets", "audio", "music", "virtual_grid_bgm.mp3"))
                                fight_panel_player1_selected_character = ''
                                fight_panel_player2_selected_character = ''
                                stage_hover_selection = '1'
                                main_menu_selected_option = ''
                                pause_menu_hover_option = 'resume'
                                fight_panel_selection_type = 'character'
                                training_mode = False
                                if player1_input_device == 'keyboard':
                                    player1 = Fighter(screen_width * 2/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 1, 'left', player1_input_device, player1_keyboard, player1_character, FPS, sfx, screen_width, screen_height, training_mode, player1_joystick)
                                elif player1_input_device == 'controller':
                                    player1 = Fighter(screen_width * 2/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 1, 'left', player1_input_device, controller_keybinds, player1_character, FPS, sfx, screen_width, screen_height, training_mode, player1_joystick)
                                if player2_input_device == 'keyboard':
                                    player2 = Fighter(screen_width * 3/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 2, 'right', player2_input_device, player2_keyboard, player2_character, FPS, sfx, screen_width, screen_height, training_mode, player2_joystick)
                                elif player2_input_device == 'controller':
                                    player2 = Fighter(screen_width * 3/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 2, 'right', player2_input_device, controller_keybinds, player2_character, FPS, sfx, screen_width, screen_height, training_mode, player2_joystick)
                                pygame.mixer.music.play(-1, 0.0, 0)
                                player1_hitbox = Hitbox(player1)
                                player2_hitbox = Hitbox(player2)
                                player1_projectile = Projectile(player1)
                                player2_projectile = Projectile(player2)
                                game_state = 'fight'
                                round_state = 'start'
                                round_number = 1
                                round_start_time = time.time()
                                round_end_time = 0
                                timer_duration = 99
                                round_timer = 0
                                round_time_pause_interval = 0
                                player1_wins = 0
                                player2_wins = 0
                                player_victory = ''
                            if event.button == 1:
                                fight_panel_selection_type = 'character'
                                stage_hover_selection = '1'
                                fight_panel_player1_selected_character = ''
                                fight_panel_player2_selected_character = ''
                                menu_return_fx.play()
            elif main_menu_selected_option == 'help':
                for option in help_submenu_options:
                    if option == help_submenu_hover_option:
                        draw_text_topleft(option, main_submenu_font, (255, 255, 0), screen_width/(48/13), screen_height * ((1/2) + (help_submenu_options.index(option)) * (4/27)))
                    else:
                        draw_text_topleft(option, main_submenu_font, (255, 255, 255), screen_width/(48/13), screen_height * ((1/2) + (help_submenu_options.index(option)) * (4/27)))
                if help_submenu_selected_option == '':
                    for event in event_list:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.key.key_code('s') or event.key == pygame.key.key_code('down'):
                                help_submenu_hover_option = help_submenu_options[help_submenu_options.index(help_submenu_hover_option) - 1]
                                menu_navigate_fx.play()
                            if event.key == pygame.key.key_code('w') or event.key == pygame.key.key_code('up'):
                                help_submenu_hover_option = help_submenu_options[help_submenu_options.index(help_submenu_hover_option) - 1]
                                menu_navigate_fx.play()
                            if event.key == pygame.key.key_code('return') or event.key == pygame.key.key_code('space'):
                                help_submenu_selected_option = help_submenu_hover_option
                                menu_select_fx.play()
                            if event.key == pygame.key.key_code('backspace') or event.key == pygame.key.key_code('escape'):
                                main_menu_selected_option = ''
                                help_submenu_hover_option = 'training'
                                menu_return_fx.play()
                        if event.type == pygame.JOYBUTTONDOWN:
                            if event.button == 12:
                                help_submenu_hover_option = help_submenu_options[help_submenu_options.index(help_submenu_hover_option) - 1]
                                menu_navigate_fx.play()
                            if event.button == 11:
                                help_submenu_hover_option = help_submenu_options[help_submenu_options.index(help_submenu_hover_option) - 1]
                                menu_navigate_fx.play()
                            if event.button == 0:
                                help_submenu_selected_option = help_submenu_hover_option
                                menu_select_fx.play()
                            if event.button == 1:
                                main_menu_selected_option = ''
                                help_submenu_hover_option = 'training'
                                menu_return_fx.play()
                elif help_submenu_selected_option == 'training':
                    draw_image(fight_select_panel_image, screen_width/(128/95), screen_height/(27/13), screen_width/(192/85), screen_height/(6/5))
                    for character in fight_panel_characters:
                        if character == fight_panel_player1_hover_character:
                            draw_image(player1_selector_image, screen_width*((65/96) + fight_panel_characters.index(character) * (25/192)), screen_height/(36/11), screen_width/(64/5), screen_height/(36/5))
                        if character == fight_panel_player2_hover_character:
                            draw_image(player2_selector_image, screen_width*((65/96) + fight_panel_characters.index(character) * (25/192)), screen_height/(36/11), screen_width/(64/5), screen_height/(36/5))
                    if fight_panel_player1_selected_character != '':
                        draw_text('player 1 ready', player_ready_font, (255, 255, 0), screen_width/(128/81), screen_height/(108/47))
                    if fight_panel_player2_selected_character != '':
                        draw_text('player 2 ready', player_ready_font, (255, 255, 0), screen_width/(48/41), screen_height/(108/47))
                    if fight_panel_selection_type == 'character':
                        if fight_panel_player1_selected_character != '':
                            for event in event_list:
                                if player1_input_device == 'keyboard' and event.type == pygame.KEYDOWN:
                                    if event.key == pygame.key.key_code('escape'):
                                        fight_panel_player1_selected_character = ''
                                        menu_return_fx.play()
                                if player1_input_device == 'controller' and event.type == pygame.JOYBUTTONDOWN:
                                    if player1_joystick.get_button(1):
                                        fight_panel_player1_selected_character = ''
                                        menu_return_fx.play()
                        elif fight_panel_player1_selected_character == '':
                            for event in event_list:
                                if player1_input_device == 'keyboard' and event.type == pygame.KEYDOWN:
                                    if event.key == pygame.key.key_code('a') or event.key == pygame.key.key_code('d'):
                                        fight_panel_player1_hover_character = fight_panel_characters[fight_panel_characters.index(fight_panel_player1_hover_character) - 1]
                                        menu_navigate_fx.play()
                                    if event.key == pygame.key.key_code('space'):
                                        fight_panel_player1_selected_character = fight_panel_player1_hover_character
                                        if fight_panel_player2_selected_character != '':
                                            fight_panel_selection_type = 'stage'
                                        menu_select_fx.play()
                                    if event.key == pygame.key.key_code('escape'):
                                        help_submenu_selected_option = ''
                                        fight_panel_player1_hover_character = characters[2]
                                        fight_panel_player2_hover_character = characters[3]
                                        fight_panel_player1_selected_character = ''
                                        fight_panel_player2_selected_character = ''
                                        menu_return_fx.play()
                                if player1_input_device == 'controller' and event.type == pygame.JOYBUTTONDOWN:
                                    if player1_joystick.get_button(13) or player1_joystick.get_button(14):
                                        fight_panel_player1_hover_character = fight_panel_characters[fight_panel_characters.index(fight_panel_player1_hover_character) - 1]
                                        menu_navigate_fx.play()
                                    if player1_joystick.get_button(0):
                                        fight_panel_player1_selected_character = fight_panel_player1_hover_character
                                        if fight_panel_player2_selected_character != '':
                                            fight_panel_selection_type = 'stage'
                                        menu_select_fx.play()
                                    if player1_joystick.get_button(1):
                                        help_submenu_selected_option = ''
                                        fight_panel_player1_hover_character = characters[2]
                                        fight_panel_player2_hover_character = characters[3]
                                        fight_panel_player1_selected_character = ''
                                        fight_panel_player2_selected_character = ''
                                        menu_return_fx.play()
                        if fight_panel_player2_selected_character != '':
                            for event in event_list:
                                if player2_input_device == 'keyboard' and event.type == pygame.KEYDOWN:
                                    if event.key == pygame.key.key_code('backspace'):
                                        fight_panel_player2_selected_character = ''
                                        menu_return_fx.play()
                                if player2_input_device == 'controller' and event.type == pygame.JOYBUTTONDOWN:
                                    if player2_joystick.get_button(1):
                                        fight_panel_player2_selected_character = ''
                                        menu_return_fx.play()
                        elif fight_panel_player2_selected_character == '':
                            for event in event_list:
                                if player2_input_device == 'keyboard' and event.type == pygame.KEYDOWN:
                                    if event.key == pygame.key.key_code('left') or event.key == pygame.key.key_code('right'):
                                        fight_panel_player2_hover_character = fight_panel_characters[fight_panel_characters.index(fight_panel_player2_hover_character) - 1]
                                        menu_navigate_fx.play()
                                    if event.key == pygame.key.key_code('return'):
                                        fight_panel_player2_selected_character = fight_panel_player2_hover_character
                                        if fight_panel_player1_selected_character != '':
                                            fight_panel_selection_type = 'stage'
                                        menu_select_fx.play()
                                    if event.key == pygame.key.key_code('backspace'):
                                        help_submenu_selected_option = ''
                                        fight_panel_player1_hover_character = characters[2]
                                        fight_panel_player2_hover_character = characters[3]
                                        fight_panel_player1_selected_character = ''
                                        fight_panel_player2_selected_character = ''
                                        menu_return_fx.play()
                                if player2_input_device == 'controller' and event.type == pygame.JOYBUTTONDOWN:
                                    if player2_joystick.get_button(13) or player2_joystick.get_button(14):
                                        fight_panel_player2_hover_character = fight_panel_characters[fight_panel_characters.index(fight_panel_player2_hover_character) - 1]
                                        menu_navigate_fx.play()
                                    if player2_joystick.get_button(0):
                                        fight_panel_player2_selected_character = fight_panel_player2_hover_character
                                        if fight_panel_player1_selected_character != '':
                                            fight_panel_selection_type = 'stage'
                                        menu_select_fx.play()
                                    if player2_joystick.get_button(1):
                                        help_submenu_selected_option = ''
                                        fight_panel_player1_hover_character = characters[2]
                                        fight_panel_player2_hover_character = characters[3]
                                        fight_panel_player1_selected_character = ''
                                        fight_panel_player2_selected_character = ''
                                        menu_return_fx.play()
                    elif fight_panel_selection_type == 'stage':
                        for stage in stage_selections:
                            if stage == stage_hover_selection:
                                draw_text(stage, main_menu_font, (255, 255, 0), screen_width * ((75/128) + stage_selections.index(stage) * (5/48)), screen_height/(54/35))
                                if stage == '1':
                                    draw_text('studio', player_ready_font, (255, 255, 255), screen_width/(128/95), screen_height/(24/19))
                                elif stage == '2':
                                    draw_text('void', player_ready_font, (255, 255, 255), screen_width/(128/95), screen_height/(24/19))
                                elif stage == '3':
                                    draw_text('secret facility', player_ready_font, (255, 255, 255), screen_width/(128/95), screen_height/(24/19))
                                elif stage == '4':
                                    draw_text('virtual grid', player_ready_font, (255, 255, 255), screen_width/(128/95), screen_height/(24/19))
                            else:
                                draw_text(stage, main_menu_font, (255, 255, 255), screen_width * ((75/128) + stage_selections.index(stage) * (5/48)), screen_height/(54/35))
                        for event in event_list:
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.key.key_code('a') or event.key == pygame.key.key_code('left'):
                                    stage_hover_selection = stage_selections[stage_selections.index(stage_hover_selection) - 1]
                                    menu_navigate_fx.play()
                                if event.key == pygame.key.key_code('d') or event.key == pygame.key.key_code('right'):
                                    stage_hover_selection = stage_selections[stage_selections.index(stage_hover_selection) - 3]
                                    menu_navigate_fx.play()
                                if event.key == pygame.key.key_code('space') or event.key == pygame.key.key_code('return'):
                                    menu_select_fx.play()
                                    player1_character = fight_panel_player1_selected_character
                                    player2_character = fight_panel_player2_selected_character
                                    if stage_hover_selection == '1':
                                        stage_bg = studio_bg
                                        pygame.mixer.music.load(join("assets", "audio", "music", "studio_bgm.mp3"))
                                    elif stage_hover_selection == '2':
                                        stage_bg = void_bg
                                        pygame.mixer.music.load(join("assets", "audio", "music", "void_bgm.mp3"))
                                    elif stage_hover_selection == '3':
                                        if player1_character == characters[3] or player2_character == characters[3]:
                                            stage_bg = secret_facility_alt_bg
                                        else:
                                            stage_bg = secret_facility_bg
                                        pygame.mixer.music.load(join("assets", "audio", "music", "secret_facility_bgm.mp3"))
                                    elif stage_hover_selection == '4':
                                        if player1_character == characters[3] or player2_character == characters[3]:
                                            stage_bg = virtual_grid_alt_bg
                                        else:
                                            stage_bg = virtual_grid_bg
                                        pygame.mixer.music.load(join("assets", "audio", "music", "virtual_grid_bgm.mp3"))
                                    fight_panel_player1_selected_character = ''
                                    fight_panel_player2_selected_character = ''
                                    stage_hover_selection = '1'
                                    main_menu_selected_option = ''
                                    help_submenu_selected_option = ''
                                    pause_menu_hover_option = 'resume'
                                    fight_panel_selection_type = 'character'
                                    training_mode = True
                                    if player1_input_device == 'keyboard':
                                        player1 = Fighter(screen_width * 2/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 1, 'left', player1_input_device, player1_keyboard, player1_character, FPS, sfx, screen_width, screen_height, training_mode, player1_joystick)
                                    elif player1_input_device == 'controller':
                                        player1 = Fighter(screen_width * 2/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 1, 'left', player1_input_device, controller_keybinds, player1_character, FPS, sfx, screen_width, screen_height, training_mode, player1_joystick)
                                    if player2_input_device == 'keyboard':
                                        player2 = Fighter(screen_width * 3/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 2, 'right', player2_input_device, player2_keyboard, player2_character, FPS, sfx, screen_width, screen_height, training_mode, player2_joystick)
                                    elif player2_input_device == 'controller':
                                        player2 = Fighter(screen_width * 3/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 2, 'right', player2_input_device, controller_keybinds, player2_character, FPS, sfx, screen_width, screen_height, training_mode, player2_joystick)
                                    pygame.mixer.music.play(-1, 0.0, 0)
                                    player1_hitbox = Hitbox(player1)
                                    player2_hitbox = Hitbox(player2)
                                    player1_projectile = Projectile(player1)
                                    player2_projectile = Projectile(player2)
                                    game_state = 'fight'
                                    round_state = 'start'
                                    round_number = 1
                                    round_start_time = time.time()
                                    round_end_time = 0
                                    timer_duration = 99
                                    round_timer = 0
                                    round_time_pause_interval = 0
                                    player1_wins = 0
                                    player2_wins = 0
                                    player_victory = ''
                                if event.key == pygame.key.key_code('escape') or event.key == pygame.key.key_code('backspace'):
                                    fight_panel_selection_type = 'character'
                                    stage_hover_selection = '1'
                                    fight_panel_player1_selected_character = ''
                                    fight_panel_player2_selected_character = ''
                                    menu_return_fx.play()
                            if event.type == pygame.JOYBUTTONDOWN:
                                if event.button == 13:
                                    stage_hover_selection = stage_selections[stage_selections.index(stage_hover_selection) - 1]
                                    menu_navigate_fx.play()
                                if event.button == 14:
                                    stage_hover_selection = stage_selections[stage_selections.index(stage_hover_selection) - 3]
                                    menu_navigate_fx.play()
                                if event.button == 0:
                                    menu_select_fx.play()
                                    player1_character = fight_panel_player1_selected_character
                                    player2_character = fight_panel_player2_selected_character
                                    if stage_hover_selection == '1':
                                        stage_bg = studio_bg
                                        pygame.mixer.music.load(join("assets", "audio", "music", "studio_bgm.mp3"))
                                    elif stage_hover_selection == '2':
                                        stage_bg = void_bg
                                        pygame.mixer.music.load(join("assets", "audio", "music", "void_bgm.mp3"))
                                    elif stage_hover_selection == '3':
                                        if player1_character == characters[3] or player2_character == characters[3]:
                                            stage_bg = secret_facility_alt_bg
                                        else:
                                            stage_bg = secret_facility_bg
                                        pygame.mixer.music.load(join("assets", "audio", "music", "secret_facility_bgm.mp3"))
                                    elif stage_hover_selection == '4':
                                        if player1_character == characters[3] or player2_character == characters[3]:
                                            stage_bg = virtual_grid_alt_bg
                                        else:
                                            stage_bg = virtual_grid_bg
                                        pygame.mixer.music.load(join("assets", "audio", "music", "virtual_grid_bgm.mp3"))
                                    fight_panel_player1_selected_character = ''
                                    fight_panel_player2_selected_character = ''
                                    stage_hover_selection = '1'
                                    main_menu_selected_option = ''
                                    help_submenu_selected_option = ''
                                    pause_menu_hover_option = 'resume'
                                    fight_panel_selection_type = 'character'
                                    training_mode = True
                                    if player1_input_device == 'keyboard':
                                        player1 = Fighter(screen_width * 2/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 1, 'left', player1_input_device, player1_keyboard, player1_character, FPS, sfx, screen_width, screen_height, training_mode, player1_joystick)
                                    elif player1_input_device == 'controller':
                                        player1 = Fighter(screen_width * 2/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 1, 'left', player1_input_device, controller_keybinds, player1_character, FPS, sfx, screen_width, screen_height, training_mode, player1_joystick)
                                    if player2_input_device == 'keyboard':
                                        player2 = Fighter(screen_width * 3/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 2, 'right', player2_input_device, player2_keyboard, player2_character, FPS, sfx, screen_width, screen_height, training_mode, player2_joystick)
                                    elif player2_input_device == 'controller':
                                        player2 = Fighter(screen_width * 3/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 2, 'right', player2_input_device, controller_keybinds, player2_character, FPS, sfx, screen_width, screen_height, training_mode, player2_joystick)
                                    pygame.mixer.music.play(-1, 0.0, 0)
                                    player1_hitbox = Hitbox(player1)
                                    player2_hitbox = Hitbox(player2)
                                    player1_projectile = Projectile(player1)
                                    player2_projectile = Projectile(player2)
                                    game_state = 'fight'
                                    round_state = 'start'
                                    round_number = 1
                                    round_start_time = time.time()
                                    round_end_time = 0
                                    timer_duration = 99
                                    round_timer = 0
                                    round_time_pause_interval = 0
                                    player1_wins = 0
                                    player2_wins = 0
                                    player_victory = ''
                                if event.button == 1:
                                    fight_panel_selection_type = 'character'
                                    stage_hover_selection = '1'
                                    fight_panel_player1_selected_character = ''
                                    fight_panel_player2_selected_character = ''
                                    menu_return_fx.play()
                elif help_submenu_selected_option == 'tutorial':
                    draw_image(tutorial_image, screen_width/(128/95), screen_height/(27/13), screen_width/(192/85), screen_height/(6/5))
                    for event in event_list:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.key.key_code('return') or event.key == pygame.key.key_code('space') or event.key == pygame.key.key_code('backspace') or event.key == pygame.key.key_code('escape'):
                                help_submenu_selected_option = ''
                                menu_return_fx.play()
                        if event.type == pygame.JOYBUTTONDOWN:
                            if event.button == 0 or event.button == 1:
                                help_submenu_selected_option = ''
                                menu_return_fx.play()
            elif main_menu_selected_option == 'options':
                for option in options_submenu_options:
                    if option == options_submenu_hover_option:
                        draw_text_topleft(option, main_submenu_font, (255, 255, 0), screen_width/(48/13), screen_height * ((1/2) + (options_submenu_options.index(option)) * (4/27)))
                    else:
                        draw_text_topleft(option, main_submenu_font, (255, 255, 255), screen_width/(48/13), screen_height * ((1/2) + (options_submenu_options.index(option)) * (4/27)))
                if options_submenu_selected_option == '':
                    for event in event_list:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.key.key_code('s') or event.key == pygame.key.key_code('down'):
                                options_submenu_hover_option = options_submenu_options[options_submenu_options.index(options_submenu_hover_option) - 1]
                                menu_navigate_fx.play()
                            if event.key == pygame.key.key_code('w') or event.key == pygame.key.key_code('up'):
                                options_submenu_hover_option = options_submenu_options[options_submenu_options.index(options_submenu_hover_option) - 1]
                                menu_navigate_fx.play()
                            if event.key == pygame.key.key_code('return') or event.key == pygame.key.key_code('space'):
                                options_submenu_selected_option = options_submenu_hover_option
                                menu_select_fx.play()
                            if event.key == pygame.key.key_code('backspace') or event.key == pygame.key.key_code('escape'):
                                main_menu_selected_option = ''
                                options_submenu_hover_option = 'settings'
                                menu_return_fx.play()
                        if event.type == pygame.JOYBUTTONDOWN:
                            if event.button == 12:
                                options_submenu_hover_option = options_submenu_options[options_submenu_options.index(options_submenu_hover_option) - 1]
                                menu_navigate_fx.play()
                            if event.button == 11:
                                options_submenu_hover_option = options_submenu_options[options_submenu_options.index(options_submenu_hover_option) - 1]
                                menu_navigate_fx.play()
                            if event.button == 0:
                                options_submenu_selected_option = options_submenu_hover_option
                                menu_select_fx.play()
                            if event.button == 1:
                                main_menu_selected_option = ''
                                options_submenu_hover_option = 'settings'
                                menu_return_fx.play()
                elif options_submenu_selected_option == 'settings':
                    # draw_image(menu_panel_image, SCREEN_WIDTH/(128/95), SCREEN_HEIGHT/(27/13), SCREEN_WIDTH/(192/85), SCREEN_HEIGHT/(6/5))
                    # draw_image(settings_panel_selection_bars_image, SCREEN_WIDTH/(128/95), SCREEN_HEIGHT/(27/13), SCREEN_WIDTH/(192/85), SCREEN_HEIGHT/(6/5))
                    # draw_text_topleft('settings', menu_panel_font, (255, 255, 255), SCREEN_WIDTH/(8/5), SCREEN_HEIGHT/12)
                    draw_image(settings_panel_image, screen_width/(128/95), screen_height/(27/13), screen_width/(192/85), screen_height/(6/5))
                    for setting in settings_panel_options:
                        if setting == settings_panel_selected_option:
                            draw_rectangle(screen_width/(32/17), screen_height * ((7/36) + (settings_panel_options.index(setting)) * (5/36)), screen_width/(12/5), screen_height/(54/5), (163, 163, 0))
                        elif setting == settings_panel_hover_option:
                            draw_rectangle(screen_width/(32/17), screen_height * ((7/36) + (settings_panel_options.index(setting)) * (5/36)), screen_width/(12/5), screen_height/(54/5), (70, 70, 0))
                    if settings_panel_selected_option == '':
                        for event in event_list:
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.key.key_code('s') or event.key == pygame.key.key_code('down'):
                                    settings_panel_hover_option = settings_panel_options[settings_panel_options.index(settings_panel_hover_option) - 3]
                                    menu_navigate_fx.play()
                                if event.key == pygame.key.key_code('w') or event.key == pygame.key.key_code('up'):
                                    settings_panel_hover_option = settings_panel_options[settings_panel_options.index(settings_panel_hover_option) - 1]
                                    menu_navigate_fx.play()
                                if event.key == pygame.key.key_code('return') or event.key == pygame.key.key_code('space'):
                                    settings_panel_selected_option = settings_panel_hover_option
                                    menu_select_fx.play()
                                if event.key == pygame.key.key_code('backspace') or event.key == pygame.key.key_code('escape'):
                                    options_submenu_selected_option = ''
                                    settings_panel_hover_option = 'resolution'
                                    menu_return_fx.play()
                            if event.type == pygame.JOYBUTTONDOWN:
                                if event.button == 12:
                                    settings_panel_hover_option = settings_panel_options[settings_panel_options.index(settings_panel_hover_option) - 3]
                                    menu_navigate_fx.play()
                                if event.button == 11:
                                    settings_panel_hover_option = settings_panel_options[settings_panel_options.index(settings_panel_hover_option) - 1]
                                    menu_navigate_fx.play()
                                if event.button == 0:
                                    settings_panel_selected_option = settings_panel_hover_option
                                    menu_select_fx.play()
                                if event.button == 1:
                                    options_submenu_selected_option = ''
                                    settings_panel_hover_option = 'resolution'
                                    menu_return_fx.play()
                    elif settings_panel_selected_option == 'resolution':
                        for event in event_list:
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.key.key_code('a') or event.key == pygame.key.key_code('left'):
                                    screen_resolution_hover_option = screen_resolution_options[screen_resolution_options.index(screen_resolution_hover_option) - 1]
                                    menu_navigate_fx.play()
                                if event.key == pygame.key.key_code('d') or event.key == pygame.key.key_code('right'):
                                    screen_resolution_hover_option = screen_resolution_options[screen_resolution_options.index(screen_resolution_hover_option) - len(screen_resolution_options) + 1]
                                    menu_navigate_fx.play()
                                if event.key == pygame.key.key_code('return') or event.key == pygame.key.key_code('space'):
                                    if settings['windowed_mode'] == 'windowed':
                                        screen_width = screen_resolution_hover_option[0]
                                        screen_height = screen_resolution_hover_option[1]
                                    menu_select_fx.play()
                                    settings['screen_resolution'][0] = screen_resolution_hover_option[0]
                                    settings['screen_resolution'][1] = screen_resolution_hover_option[1]
                                    pygame.display.set_mode((screen_width, screen_height))
                                    # characters and fonts need to be updated due to the screen resolution changing
                                    characters = initialise_characters()
                                    fight_panel_characters = [characters[2], characters[3]]
                                    fight_panel_player1_hover_character = characters[2]
                                    fight_panel_player2_hover_character = characters[3]
                                    initialise_fonts()
                                    save_options("options.json")
                                    settings_panel_selected_option = ''
                                if event.key == pygame.key.key_code('backspace') or event.key == pygame.key.key_code('escape'):
                                    screen_resolution_hover_option = screen_resolution_options[screen_resolution_options.index(settings["screen_resolution"])]
                                    settings_panel_selected_option = ''
                                    menu_return_fx.play()
                            if event.type == pygame.JOYBUTTONDOWN:
                                if event.button == 13:
                                    screen_resolution_hover_option = screen_resolution_options[screen_resolution_options.index(screen_resolution_hover_option) - 1]
                                    menu_navigate_fx.play()
                                if event.button == 14:
                                    screen_resolution_hover_option = screen_resolution_options[screen_resolution_options.index(screen_resolution_hover_option) - len(screen_resolution_options) + 1]
                                    menu_navigate_fx.play()
                                if event.button == 0:
                                    if settings['windowed_mode'] == 'windowed':
                                        screen_width = screen_resolution_hover_option[0]
                                        screen_height = screen_resolution_hover_option[1]
                                    menu_select_fx.play()
                                    settings['screen_resolution'][0] = screen_resolution_hover_option[0]
                                    settings['screen_resolution'][1] = screen_resolution_hover_option[1]
                                    pygame.display.set_mode((screen_width, screen_height))
                                    # characters and fonts need to be updated due to the screen resolution changing
                                    characters = initialise_characters()
                                    fight_panel_characters = [characters[2], characters[3]]
                                    fight_panel_player1_hover_character = characters[2]
                                    fight_panel_player2_hover_character = characters[3]
                                    initialise_fonts()
                                    save_options("options.json")
                                    settings_panel_selected_option = ''
                                if event.button == 1:
                                    screen_resolution_hover_option = screen_resolution_options[screen_resolution_options.index(settings["screen_resolution"])]
                                    settings_panel_selected_option = ''
                                    menu_return_fx.play()
                    elif settings_panel_selected_option == 'window_mode':
                        for event in event_list:
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.key.key_code('a') or event.key == pygame.key.key_code('left'):
                                    window_mode_hover_option = window_mode_options[window_mode_options.index(window_mode_hover_option) - 1]
                                    menu_navigate_fx.play()
                                if event.key == pygame.key.key_code('d') or event.key == pygame.key.key_code('right'):
                                    window_mode_hover_option = window_mode_options[window_mode_options.index(window_mode_hover_option) - len(window_mode_options) + 1]
                                    menu_navigate_fx.play()
                                if event.key == pygame.key.key_code('return') or event.key == pygame.key.key_code('space'):
                                    menu_select_fx.play()
                                    if window_mode_hover_option == "windowed":
                                        screen_width = screen_resolution_hover_option[0]
                                        screen_height = screen_resolution_hover_option[1]
                                        pygame.display.set_mode((screen_width, screen_height))
                                    else:
                                        screen_width = SCREEN_WIDTH
                                        screen_height = SCREEN_HEIGHT
                                        if window_mode_hover_option == "fullscreen":
                                            pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
                                        elif window_mode_hover_option == "borderless":
                                            pygame.display.set_mode((screen_width, screen_height))
                                    settings['windowed_mode'] = window_mode_hover_option
                                    # characters and fonts need to be updated due to the screen resolution changing
                                    characters = initialise_characters()
                                    fight_panel_characters = [characters[2], characters[3]]
                                    fight_panel_player1_hover_character = characters[2]
                                    fight_panel_player2_hover_character = characters[3]
                                    initialise_fonts()
                                    save_options("options.json")
                                    settings_panel_selected_option = ''
                                if event.key == pygame.key.key_code('backspace') or event.key == pygame.key.key_code('escape'):
                                    window_mode_hover_option = window_mode_options[window_mode_options.index(settings["windowed_mode"])]
                                    settings_panel_selected_option = ''
                                    menu_return_fx.play()
                            if event.type == pygame.JOYBUTTONDOWN:
                                if event.button == 13:
                                    window_mode_hover_option = window_mode_options[window_mode_options.index(window_mode_hover_option) - 1]
                                    menu_navigate_fx.play()
                                if event.button == 14:
                                    window_mode_hover_option = window_mode_options[window_mode_options.index(window_mode_hover_option) - len(window_mode_options) + 1]
                                    menu_navigate_fx.play()
                                if event.button == 0:
                                    menu_select_fx.play()
                                    if window_mode_hover_option == "windowed":
                                        screen_width = screen_resolution_hover_option[0]
                                        screen_height = screen_resolution_hover_option[1]
                                        pygame.display.set_mode((screen_width, screen_height))
                                    else:
                                        screen_width = SCREEN_WIDTH
                                        screen_height = SCREEN_HEIGHT
                                        if window_mode_hover_option == "fullscreen":
                                            pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
                                        elif window_mode_hover_option == "borderless":
                                            pygame.display.set_mode((screen_width, screen_height))
                                    settings['windowed_mode'] = window_mode_hover_option
                                    # characters and fonts need to be updated due to the screen resolution changing
                                    characters = initialise_characters()
                                    fight_panel_characters = [characters[2], characters[3]]
                                    fight_panel_player1_hover_character = characters[2]
                                    fight_panel_player2_hover_character = characters[3]
                                    initialise_fonts()
                                    save_options("options.json")
                                    settings_panel_selected_option = ''
                                if event.button == 1:
                                    window_mode_hover_option = window_mode_options[window_mode_options.index(settings["windowed_mode"])]
                                    settings_panel_selected_option = ''
                                    menu_return_fx.play()
                    elif settings_panel_selected_option == 'music':
                        for event in event_list:
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.key.key_code('a') or event.key == pygame.key.key_code('left'):
                                    music_volume_hover_option = music_volume_options[music_volume_options.index(music_volume_hover_option) - 1]
                                    menu_navigate_fx.play()
                                if event.key == pygame.key.key_code('d') or event.key == pygame.key.key_code('right'):
                                    music_volume_hover_option = music_volume_options[music_volume_options.index(music_volume_hover_option) - len(music_volume_options) + 1]
                                    menu_navigate_fx.play()
                                if event.key == pygame.key.key_code('return') or event.key == pygame.key.key_code('space'):
                                    menu_select_fx.play()
                                    music_volume = music_volume_hover_option
                                    settings['music_volume'] = music_volume_hover_option
                                    pygame.mixer.music.set_volume(music_volume / 10)
                                    save_options("options.json")
                                    settings_panel_selected_option = ''
                                if event.key == pygame.key.key_code('backspace') or event.key == pygame.key.key_code('escape'):
                                    music_volume_hover_option = music_volume_options[music_volume_options.index(settings["music_volume"])]
                                    settings_panel_selected_option = ''
                                    menu_return_fx.play()
                            if event.type == pygame.JOYBUTTONDOWN:
                                if event.button == 13:
                                    music_volume_hover_option = music_volume_options[music_volume_options.index(music_volume_hover_option) - 1]
                                    menu_navigate_fx.play()
                                if event.button == 14:
                                    music_volume_hover_option = music_volume_options[music_volume_options.index(music_volume_hover_option) - len(music_volume_options) + 1]
                                    menu_navigate_fx.play()
                                if event.button == 0:
                                    menu_select_fx.play()
                                    music_volume = music_volume_hover_option
                                    settings['music_volume'] = music_volume_hover_option
                                    pygame.mixer.music.set_volume(music_volume / 10)
                                    save_options("options.json")
                                    settings_panel_selected_option = ''
                                if event.button == 1:
                                    music_volume_hover_option = music_volume_options[music_volume_options.index(settings["music_volume"])]
                                    settings_panel_selected_option = ''
                                    menu_return_fx.play()
                    elif settings_panel_selected_option == 'sfx':
                        for event in event_list:
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.key.key_code('a') or event.key == pygame.key.key_code('left'):
                                    sfx_volume_hover_option = sfx_volume_options[sfx_volume_options.index(sfx_volume_hover_option) - 1]
                                    menu_navigate_fx.play()
                                if event.key == pygame.key.key_code('d') or event.key == pygame.key.key_code('right'):
                                    sfx_volume_hover_option = sfx_volume_options[sfx_volume_options.index(sfx_volume_hover_option) - len(sfx_volume_options) + 1]
                                    menu_navigate_fx.play()
                                if event.key == pygame.key.key_code('return') or event.key == pygame.key.key_code('space'):
                                    menu_select_fx.play()
                                    sfx_volume = sfx_volume_hover_option
                                    settings['sfx_volume'] = sfx_volume_hover_option
                                    initialise_sfx_volume()
                                    save_options("options.json")
                                    settings_panel_selected_option = ''
                                if event.key == pygame.key.key_code('backspace') or event.key == pygame.key.key_code('escape'):
                                    sfx_volume_hover_option = sfx_volume_options[sfx_volume_options.index(settings["sfx_volume"])]
                                    settings_panel_selected_option = ''
                                    menu_return_fx.play()
                            if event.type == pygame.JOYBUTTONDOWN:
                                if event.button == 13:
                                    sfx_volume_hover_option = sfx_volume_options[sfx_volume_options.index(sfx_volume_hover_option) - 1]
                                    menu_navigate_fx.play()
                                if event.button == 14:
                                    sfx_volume_hover_option = sfx_volume_options[sfx_volume_options.index(sfx_volume_hover_option) - len(sfx_volume_options) + 1]
                                    menu_navigate_fx.play()
                                if event.button == 0:
                                    menu_select_fx.play()
                                    sfx_volume = sfx_volume_hover_option
                                    settings['sfx_volume'] = sfx_volume_hover_option
                                    initialise_sfx_volume()
                                    save_options("options.json")
                                    settings_panel_selected_option = ''
                                if event.button == 1:
                                    sfx_volume_hover_option = sfx_volume_options[sfx_volume_options.index(settings["sfx_volume"])]
                                    settings_panel_selected_option = ''
                                    menu_return_fx.play()
                    
                    # options text
                    draw_image(settings_panel_set_text_image, screen_width/(128/95), screen_height/(27/13), screen_width/(192/85), screen_height/(6/5))
                    draw_text(f"{screen_resolution_hover_option[0]}x{screen_resolution_hover_option[1]}", settings_options_font, (255, 255, 255), screen_width/(384/325), screen_height/4)
                    draw_text(window_mode_hover_option, settings_options_font, (255, 255, 255), screen_width/(384/325), screen_height/(18/7))
                    
                    # music, sfx volume bars
                    draw_rectangle(screen_width/(192/145), screen_height/(216/107), screen_width * (35/192) * (music_volume_hover_option/10), screen_height/(108/5), (255, 255, 0))
                    draw_rectangle(screen_width/(192/145), screen_height/(27/17), screen_width * (35/192) * (sfx_volume_hover_option/10), screen_height/(108/5), (255, 255, 0))
                elif options_submenu_selected_option == 'controls':
                    draw_image(controls_panel_image, screen_width/(128/95), screen_height/(27/13), screen_width/(192/85), screen_height/(6/5))
                    draw_text(player1_input_device, settings_options_font, (255, 255, 255), screen_width/(128/81), screen_height/(216/49))
                    draw_text(player2_input_device, settings_options_font, (255, 255, 255), screen_width/(48/41), screen_height/(216/49))
                    for keybind in controls_panel_keybinds:
                        if keybind == controls_panel_player1_selected_keybind:
                            draw_rectangle(screen_width/(24/13), screen_height * ((307/1080) + (controls_panel_keybinds.index(keybind)) * (2/27)), screen_width/(16/3), screen_height/(72/5), (163, 163, 0))
                        elif keybind == controls_panel_player1_hover_keybind:
                            draw_rectangle(screen_width/(24/13), screen_height * ((307/1080) + (controls_panel_keybinds.index(keybind)) * (2/27)), screen_width/(16/3), screen_height/(72/5), (70, 70, 0))
                        if keybind == controls_panel_player2_selected_keybind:
                            draw_rectangle(screen_width/(384/293), screen_height * ((307/1080) + (controls_panel_keybinds.index(keybind)) * (2/27)), screen_width/(16/3), screen_height/(72/5), (163, 163, 0))
                        elif keybind == controls_panel_player2_hover_keybind:
                            draw_rectangle(screen_width/(384/293), screen_height * ((307/1080) + (controls_panel_keybinds.index(keybind)) * (2/27)), screen_width/(16/3), screen_height/(72/5), (70, 70, 0))
                    if player1_input_device == 'keyboard':
                        if controls_panel_player1_selected_keybind == '':
                            for event in event_list:
                                if event.type == pygame.KEYDOWN:
                                    if event.key == pygame.key.key_code('s') and controls_panel_player2_selected_keybind == '':
                                        controls_panel_player1_hover_keybind = controls_panel_keybinds[controls_panel_keybinds.index(controls_panel_player1_hover_keybind) - 7]
                                        menu_navigate_fx.play()
                                    if event.key == pygame.key.key_code('w') and controls_panel_player2_selected_keybind == '':
                                        controls_panel_player1_hover_keybind = controls_panel_keybinds[controls_panel_keybinds.index(controls_panel_player1_hover_keybind) - 1]
                                        menu_navigate_fx.play()
                                    if event.key == pygame.key.key_code('space') and controls_panel_player2_selected_keybind == '':
                                        controls_panel_player1_selected_keybind = controls_panel_player1_hover_keybind
                                        menu_select_fx.play()
                                    if event.key == pygame.key.key_code('escape'):
                                        options_submenu_selected_option = ''
                                        menu_return_fx.play()
                                        controls_panel_player1_hover_keybind = 'up'
                                        controls_panel_player2_hover_keybind = 'up'
                                        controls_panel_player1_selected_keybind = ''
                                        controls_panel_player2_selected_keybind = ''
                        elif controls_panel_player1_selected_keybind != '':
                            for event in event_list:
                                if event.type == pygame.KEYDOWN:
                                    if event.key == pygame.key.key_code('space'):
                                        menu_select_fx.play()
                                        player1_keyboard[controls_panel_player1_selected_keybind] = controls_panel_player1_keybind_inputs[controls_panel_keybinds.index(controls_panel_player1_selected_keybind)]
                                        save_options('options.json')
                                        controls_panel_player1_selected_keybind = ''
                                    elif event.key == pygame.key.key_code('escape'):
                                        controls_panel_player1_keybind_inputs[controls_panel_keybinds.index(controls_panel_player1_selected_keybind)] = player1_keyboard[controls_panel_player1_selected_keybind]
                                        controls_panel_player1_selected_keybind = ''
                                        menu_return_fx.play()
                                    elif event.key == pygame.key.key_code('return') or event.key == pygame.key.key_code('backspace'):
                                        menu_return_fx.play()
                                    elif pygame.key.name(event.key) in controls_panel_player1_keybind_inputs or pygame.key.name(event.key) in controls_panel_player2_keybind_inputs:
                                        menu_return_fx.play()
                                    else:
                                        controls_panel_player1_keybind_inputs[controls_panel_keybinds.index(controls_panel_player1_selected_keybind)] = pygame.key.name(event.key)
                                        menu_navigate_fx.play()
                    else:
                        for event in event_list:
                            if event.type == pygame.JOYBUTTONDOWN:
                                if event.button == 1:
                                    options_submenu_selected_option = ''
                                    menu_return_fx.play()
                                    controls_panel_player1_hover_keybind = 'up'
                                    controls_panel_player2_hover_keybind = 'up'
                                    controls_panel_player1_selected_keybind = ''
                                    controls_panel_player2_selected_keybind = ''
                    if player2_input_device == 'keyboard':
                        if controls_panel_player2_selected_keybind == '':
                            for event in event_list:
                                if event.type == pygame.KEYDOWN:
                                    if event.key == pygame.key.key_code('down') and controls_panel_player1_selected_keybind == '':
                                        controls_panel_player2_hover_keybind = controls_panel_keybinds[controls_panel_keybinds.index(controls_panel_player2_hover_keybind) - 7]
                                        menu_navigate_fx.play()
                                    if event.key == pygame.key.key_code('up') and controls_panel_player1_selected_keybind == '':
                                        controls_panel_player2_hover_keybind = controls_panel_keybinds[controls_panel_keybinds.index(controls_panel_player2_hover_keybind) - 1]
                                        menu_navigate_fx.play()
                                    if event.key == pygame.key.key_code('return') and controls_panel_player1_selected_keybind == '':
                                        controls_panel_player2_selected_keybind = controls_panel_player2_hover_keybind
                                        menu_select_fx.play()
                                    if event.key == pygame.key.key_code('backspace'):
                                        options_submenu_selected_option = ''
                                        menu_return_fx.play()
                                        controls_panel_player1_hover_keybind = 'up'
                                        controls_panel_player2_hover_keybind = 'up'
                                        controls_panel_player1_selected_keybind = ''
                                        controls_panel_player2_selected_keybind = ''
                        elif controls_panel_player2_selected_keybind != '':
                            for event in event_list:
                                if event.type == pygame.KEYDOWN:
                                    if event.key == pygame.key.key_code('return'):
                                        menu_select_fx.play()
                                        player2_keyboard[controls_panel_player2_selected_keybind] = controls_panel_player2_keybind_inputs[controls_panel_keybinds.index(controls_panel_player2_selected_keybind)]
                                        save_options('options.json')
                                        controls_panel_player2_selected_keybind = ''
                                    elif event.key == pygame.key.key_code('backspace'):
                                        controls_panel_player2_keybind_inputs[controls_panel_keybinds.index(controls_panel_player2_selected_keybind)] = player2_keyboard[controls_panel_player2_selected_keybind]
                                        controls_panel_player2_selected_keybind = ''
                                        menu_return_fx.play()
                                    elif event.key == pygame.key.key_code('space') or event.key == pygame.key.key_code('escape'):
                                        menu_return_fx.play()
                                    elif pygame.key.name(event.key) in controls_panel_player1_keybind_inputs or pygame.key.name(event.key) in controls_panel_player2_keybind_inputs:
                                        menu_return_fx.play()
                                    else:
                                        controls_panel_player2_keybind_inputs[controls_panel_keybinds.index(controls_panel_player2_selected_keybind)] = pygame.key.name(event.key)
                                        menu_navigate_fx.play()
                    else:
                        for event in event_list:
                            if event.type == pygame.JOYBUTTONDOWN:
                                if event.button == 1:
                                    options_submenu_selected_option = ''
                                    menu_return_fx.play()
                                    controls_panel_player1_hover_keybind = 'up'
                                    controls_panel_player2_hover_keybind = 'up'
                                    controls_panel_player1_selected_keybind = ''
                                    controls_panel_player2_selected_keybind = ''
                    # icons images, keybind input images
                    draw_image(controls_panel_icons_image, screen_width/(128/95), screen_height/(27/13), screen_width/(192/85), screen_height/(6/5))
                    if player1_input_device == 'keyboard':
                        for input in controls_panel_player1_keybind_inputs:
                            draw_text(input, settings_options_font, (255, 255, 255), screen_width/(384/253), screen_height * ((29/90) + (controls_panel_player1_keybind_inputs.index(input)) * (2/27)))
                    elif player1_input_device == 'controller':
                        for input in controls_panel_controller_button_inputs:
                            draw_text(input, settings_options_font, (255, 255, 255), screen_width/(384/253), screen_height * ((29/90) + (controls_panel_controller_button_inputs.index(input)) * (2/27)))
                    if player2_input_device == 'keyboard':
                        for input in controls_panel_player2_keybind_inputs:
                            draw_text(input, settings_options_font, (255, 255, 255), screen_width/(192/169), screen_height * ((29/90) + (controls_panel_player2_keybind_inputs.index(input)) * (2/27)))
                    elif player2_input_device == 'controller':
                        for input in controls_panel_controller_button_inputs:
                            draw_text(input, settings_options_font, (255, 255, 255), screen_width/(192/169), screen_height * ((29/90) + (controls_panel_controller_button_inputs.index(input)) * (2/27)))

            elif main_menu_selected_option == 'exit':
                pygame.quit()
                sys.exit()
                
        elif game_state == 'fight':
            fight(player1, player2, player1_hitbox, player2_hitbox, player1_projectile, player2_projectile)
            draw_text(str(round_timer), timer_font, (255, 255, 0), screen_width/2, screen_height/10)
            if round_state != 'pause':
                player1.loop()
                player2.loop()
                player1_hitbox.loop()
                player2_hitbox.loop()
                player1_projectile.loop()
                player2_projectile.loop()
            elif round_state == 'pause':
                draw_image(pause_image, screen_width/2, screen_height/2, screen_width, screen_height)
                for option in pause_menu_options:
                    if option == pause_menu_hover_option:
                        draw_text(option, settings_options_font, (255, 255, 0), screen_width/2, screen_height * ((25/36) + (pause_menu_options.index(option)) * (5/54)))
                    else:
                        draw_text(option, settings_options_font, (255, 255, 255), screen_width/2, screen_height * ((25/36) + (pause_menu_options.index(option)) * (5/54)))
                if move_list_selected == True:
                    draw_image(move_list_image, screen_width/2, screen_height/2, screen_width, screen_height)
                    for event in event_list:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.key.key_code('space') or event.key == pygame.key.key_code('return') or event.key == pygame.key.key_code('escape') or event.key == pygame.key.key_code('backspace'):
                                menu_return_fx.play()
                                move_list_selected = False
                                pause_menu_hover_option = 'resume'
                        if event.type == pygame.JOYBUTTONDOWN:
                            if event.button == 0 or event.button == 1:
                                menu_return_fx.play()
                                move_list_selected = False
                                pause_menu_hover_option = 'resume'
                else:
                    for event in event_list:
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.key.key_code('s') or event.key == pygame.key.key_code('down'):
                                pause_menu_hover_option = pause_menu_options[pause_menu_options.index(pause_menu_hover_option) - 2]
                                menu_navigate_fx.play()
                            if event.key == pygame.key.key_code('w') or event.key == pygame.key.key_code('up'):
                                pause_menu_hover_option = pause_menu_options[pause_menu_options.index(pause_menu_hover_option) - 1]
                                menu_navigate_fx.play()
                            if event.key == pygame.key.key_code('space') or event.key == pygame.key.key_code('return'):
                                if pause_menu_hover_option == 'resume':
                                    menu_select_fx.play()
                                    round_state = 'running'
                                    unpause(player1)
                                    unpause(player2)
                                    round_start_time = time.time() - round_time_pause_interval
                                elif pause_menu_hover_option == 'move list':
                                    menu_select_fx.play()
                                    move_list_selected = True
                                elif pause_menu_hover_option == 'main menu':
                                    menu_select_fx.play()
                                    pygame.mixer.music.load(join("assets", "audio", "music", "menu_bgm.mp3"))
                                    pygame.mixer.music.play(-1, 0.0, 0)
                                    game_state = 'menu'
                                    pause_menu_hover_option == 'resume'
                                    fight_panel_player1_hover_character = characters[2]
                                    fight_panel_player2_hover_character = characters[3]
                        if event.type == pygame.JOYBUTTONDOWN:
                            if event.button == 12:
                                pause_menu_hover_option = pause_menu_options[pause_menu_options.index(pause_menu_hover_option) - 2]
                                menu_navigate_fx.play()
                            if event.button == 11:
                                pause_menu_hover_option = pause_menu_options[pause_menu_options.index(pause_menu_hover_option) - 1]
                                menu_navigate_fx.play()
                            if event.button == 0:
                                if pause_menu_hover_option == 'resume':
                                    menu_select_fx.play()
                                    round_state = 'running'
                                    unpause(player1)
                                    unpause(player2)
                                    round_start_time = time.time() - round_time_pause_interval
                                elif pause_menu_hover_option == 'move list':
                                    menu_select_fx.play()
                                    move_list_selected = True
                                elif pause_menu_hover_option == 'main menu':
                                    menu_select_fx.play()
                                    pygame.mixer.music.load(join("assets", "audio", "music", "menu_bgm.mp3"))
                                    pygame.mixer.music.play(-1, 0.0, 0)
                                    game_state = 'menu'
                                    pause_menu_hover_option == 'resume'
                                    fight_panel_player1_hover_character = characters[2]
                                    fight_panel_player2_hover_character = characters[3]
                                    
            if round_state == 'running':
                if training_mode == False:
                    round_timer = int(timer_duration - (time.time() - round_start_time))
                else:
                    round_timer = timer_duration
                player1.handle_actions(player1_hitbox, player1_projectile, player2, player2_hitbox, event_list)
                player2.handle_actions(player2_hitbox, player2_projectile, player1, player1_hitbox, event_list)
                if round_timer <= 0:
                    round_timer = 0
                    timeout(player1)
                    timeout(player2)
                    if player1.health == player2.health:
                        round_state = 'end'
                        player_victory = ''
                        round_end_time = time.time()
                    elif player1.health > player2.health:
                        round_state = 'end'
                        player_victory = '1'
                        player1_wins += 1
                        round_end_time = time.time()
                    elif player2.health > player1.health:
                        round_state = 'end'
                        player_victory = '2'
                        player2_wins += 1
                        round_end_time = time.time()
                if player1.defeated == True and player2.defeated == True:
                    round_state = 'end'
                    player_victory = ''
                    round_end_time = time.time()
                elif player1.defeated == True:
                    round_state = 'end'
                    player_victory = '2'
                    player2_wins += 1
                    player2.x_vel = 0
                    round_end_time = time.time()
                elif player2.defeated == True:
                    round_state = 'end'
                    player_victory = '1'
                    player1_wins += 1
                    player1.x_vel = 0
                    round_end_time = time.time()
                for event in event_list:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.key.key_code('backspace') or event.key == pygame.key.key_code('escape'):
                            menu_return_fx.play()
                            round_state = 'pause'
                            pause(player1)
                            pause(player2)
                            round_time_pause_interval = time.time() - round_start_time
                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.button == 6: # options button on playstation
                            menu_return_fx.play()
                            round_state = 'pause'
                            pause(player1)
                            pause(player2)
                            round_time_pause_interval = time.time() - round_start_time
            if round_state == 'start':
                round_timer = timer_duration
                # draw_text(f"Round {round_number}", round_font, (255, 255, 0), SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
                if time.time() - round_start_time > 4:
                    round_state = 'running'
                    round_start_time = time.time()
                elif time.time() - round_start_time > 2:
                    draw_image(fight_image, screen_width / 2, screen_height / 2, screen_width * 5/12, screen_height * 20/27)
                else:
                    draw_text(f"Round {round_number}", round_font, (255, 255, 0), screen_width/2, screen_height/2)
            if round_state == 'end':
                if time.time() - round_end_time > 3:
                    if (player1_wins == 2 or player2_wins == 2) and training_mode == False:
                        end_screen_hover_option == 'play again'
                        round_state = 'end_screen'
                    else:
                        if player1_input_device == 'keyboard':
                            player1 = Fighter(screen_width * 2/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 1, 'left', player1_input_device, player1_keyboard, player1_character, FPS, sfx, screen_width, screen_height, training_mode, player1_joystick)
                        elif player1_input_device == 'controller':
                            player1 = Fighter(screen_width * 2/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 1, 'left', player1_input_device, controller_keybinds, player1_character, FPS, sfx, screen_width, screen_height, training_mode, player1_joystick)
                        if player2_input_device == 'keyboard':
                            player2 = Fighter(screen_width * 3/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 2, 'right', player2_input_device, player2_keyboard, player2_character, FPS, sfx, screen_width, screen_height, training_mode, player2_joystick)
                        elif player2_input_device == 'controller':
                            player2 = Fighter(screen_width * 3/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 2, 'right', player2_input_device, controller_keybinds, player2_character, FPS, sfx, screen_width, screen_height, training_mode, player2_joystick)
                        player1_hitbox = Hitbox(player1)
                        player2_hitbox = Hitbox(player2)
                        player1_projectile = Projectile(player1)
                        player2_projectile = Projectile(player2)
                        round_start_time = time.time()
                        round_number += 1
                        round_state = 'start'
                        player_victory = ''
                elif player_victory == '':
                    draw_text("Draw", round_font, (255, 255, 0), screen_width/2, screen_height/2)
                else:
                    draw_text(f"Player {player_victory} wins", round_font, (255, 255, 0), screen_width/2, screen_height/2)
            if round_state == 'end_screen':
                draw_image(end_screen_image, screen_width/2, screen_height/2, screen_width, screen_height)
                draw_text(f"player {player_victory} wins", end_screen_font, (255, 255, 0), screen_width/2, screen_height/(54/13))
                for option in end_screen_menu_options:
                    if option == end_screen_hover_option:
                        draw_text(option, settings_options_font, (255, 255, 0), screen_width/2, screen_height * ((85/108) + (end_screen_menu_options.index(option)) * (5/54)))
                    else:
                        draw_text(option, settings_options_font, (255, 255, 255), screen_width/2, screen_height * ((85/108) + (end_screen_menu_options.index(option)) * (5/54)))
                for event in event_list:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.key.key_code('s') or event.key == pygame.key.key_code('down') or event.key == pygame.key.key_code('w') or event.key == pygame.key.key_code('up'):
                            end_screen_hover_option = end_screen_menu_options[end_screen_menu_options.index(end_screen_hover_option) - 1]
                            menu_navigate_fx.play()
                        if event.key == pygame.key.key_code('space') or event.key == pygame.key.key_code('return'):
                            if end_screen_hover_option == 'play again':
                                menu_select_fx.play()
                                if player1_input_device == 'keyboard':
                                    player1 = Fighter(screen_width * 2/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 1, 'left', player1_input_device, player1_keyboard, player1_character, FPS, sfx, screen_width, screen_height, training_mode, player1_joystick)
                                elif player1_input_device == 'controller':
                                    player1 = Fighter(screen_width * 2/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 1, 'left', player1_input_device, controller_keybinds, player1_character, FPS, sfx, screen_width, screen_height, training_mode, player1_joystick)
                                if player2_input_device == 'keyboard':
                                    player2 = Fighter(screen_width * 3/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 2, 'right', player2_input_device, player2_keyboard, player2_character, FPS, sfx, screen_width, screen_height, training_mode, player2_joystick)
                                elif player2_input_device == 'controller':
                                    player2 = Fighter(screen_width * 3/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 2, 'right', player2_input_device, controller_keybinds, player2_character, FPS, sfx, screen_width, screen_height, training_mode, player2_joystick)
                                pygame.mixer.music.play(-1, 0.0, 0)
                                player1_hitbox = Hitbox(player1)
                                player2_hitbox = Hitbox(player2)
                                player1_projectile = Projectile(player1)
                                player2_projectile = Projectile(player2)
                                round_start_time = time.time()
                                round_number = 1
                                round_state = 'start'
                                player1_wins = 0
                                player2_wins = 0
                                player_victory = ''
                            elif end_screen_hover_option == 'main menu':
                                menu_select_fx.play()
                                pygame.mixer.music.load(join("assets", "audio", "music", "menu_bgm.mp3"))
                                pygame.mixer.music.play(-1, 0.0, 0)
                                game_state = 'menu'
                                fight_panel_player1_hover_character = characters[2]
                                fight_panel_player2_hover_character = characters[3]
                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.button == 12 or event.button == 11:
                            end_screen_hover_option = end_screen_menu_options[end_screen_menu_options.index(end_screen_hover_option) - 1]
                            menu_navigate_fx.play()
                        if event.button == 0:
                            if end_screen_hover_option == 'play again':
                                menu_select_fx.play()
                                if player1_input_device == 'keyboard':
                                    player1 = Fighter(screen_width * 2/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 1, 'left', player1_input_device, player1_keyboard, player1_character, FPS, sfx, screen_width, screen_height, training_mode, player1_joystick)
                                elif player1_input_device == 'controller':
                                    player1 = Fighter(screen_width * 2/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 1, 'left', player1_input_device, controller_keybinds, player1_character, FPS, sfx, screen_width, screen_height, training_mode, player1_joystick)
                                if player2_input_device == 'keyboard':
                                    player2 = Fighter(screen_width * 3/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 2, 'right', player2_input_device, player2_keyboard, player2_character, FPS, sfx, screen_width, screen_height, training_mode, player2_joystick)
                                elif player2_input_device == 'controller':
                                    player2 = Fighter(screen_width * 3/5, screen_height * 35/54, screen_width * 5/24, screen_height * 10/27, 2, 'right', player2_input_device, controller_keybinds, player2_character, FPS, sfx, screen_width, screen_height, training_mode, player2_joystick)
                                pygame.mixer.music.play(-1, 0.0, 0)
                                player1_hitbox = Hitbox(player1)
                                player2_hitbox = Hitbox(player2)
                                player1_projectile = Projectile(player1)
                                player2_projectile = Projectile(player2)
                                round_start_time = time.time()
                                round_number = 1
                                round_state = 'start'
                                player1_wins = 0
                                player2_wins = 0
                                player_victory = ''
                            elif end_screen_hover_option == 'main menu':
                                menu_select_fx.play()
                                pygame.mixer.music.load(join("assets", "audio", "music", "menu_bgm.mp3"))
                                pygame.mixer.music.play(-1, 0.0, 0)
                                game_state = 'menu'
                                fight_panel_player1_hover_character = characters[2]
                                fight_panel_player2_hover_character = characters[3]
                    
                
        # main loop event handler
        for event in event_list:
            if event.type == pygame.JOYDEVICEADDED:
                joystick = pygame.joystick.Joystick(event.device_index)
                joysticks[joystick.get_instance_id()] = joystick
                if len(joysticks) >= 2:
                    player1_input_device = 'controller'
                    player2_input_device = 'controller'
                    player1_joystick = joysticks[list(joysticks.keys())[0]]
                    player2_joystick = joysticks[list(joysticks.keys())[1]]
                elif len(joysticks) == 1:
                    player1_input_device = 'controller'
                    player2_input_device = 'keyboard'
                    player1_joystick = joysticks[list(joysticks.keys())[0]]
                    player2_joystick = None
                elif len(joysticks) == 0:
                    player1_input_device = 'keyboard'
                    player2_input_device = 'keyboard'
                    player1_joystick = None
                    player2_joystick = None
                if player1 != None and player2 != None:
                    player1.input = player1_input_device
                    player2.input = player2_input_device
                    if player1_input_device == 'keyboard':
                        player1.inputlist = player1_keyboard
                    elif player1_input_device == 'controller':
                        player1.inputlist = controller_keybinds
                    if player2_input_device == 'keyboard':
                        player2.inputlist = player2_keyboard
                    elif player2_input_device == 'controller':
                        player2.inputlist = controller_keybinds
                    player1.rebind_controls(player1_joystick)
                    player2.rebind_controls(player2_joystick)
            if event.type == pygame.JOYDEVICEREMOVED:
                del joysticks[event.instance_id]
                if len(joysticks) >= 2:
                    player1_input_device = 'controller'
                    player2_input_device = 'controller'
                    player1_joystick = joysticks[list(joysticks.keys())[0]]
                    player2_joystick = joysticks[list(joysticks.keys())[1]]
                elif len(joysticks) == 1:
                    player1_input_device = 'controller'
                    player2_input_device = 'keyboard'
                    player1_joystick = joysticks[list(joysticks.keys())[0]]
                    player2_joystick = None
                elif len(joysticks) == 0:
                    player1_input_device = 'keyboard'
                    player2_input_device = 'keyboard'
                    player1_joystick = None
                    player2_joystick = None
                if player1 != None and player2 != None:
                    player1.input = player1_input_device
                    player2.input = player2_input_device
                    if player1_input_device == 'keyboard':
                        player1.inputlist = player1_keyboard
                    elif player1_input_device == 'controller':
                        player1.inputlist = controller_keybinds
                    if player2_input_device == 'keyboard':
                        player2.inputlist = player2_keyboard
                    elif player2_input_device == 'controller':
                        player2.inputlist = controller_keybinds
                    player1.rebind_controls(player1_joystick)
                    player2.rebind_controls(player2_joystick)
            if event.type == pygame.QUIT:
                run = False
                break
        
        pygame.display.update()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
