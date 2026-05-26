# input frame duration is the duration window that allows other inputs to be chained into combos

# vel_start_frame_index and vel_end_frame_index are frame indexes between which the player velocity changes

'''
Attack Naming System
- j1: jumping attack
- f1: forward attack
- b1: backward attack
- c1: crouching attack
- 1: normal attack

'''


fighter_red_attacks = {
    '1': {'damage': 20, 'type': 'high', 'x_vel': 0, 'y_vel': 0, 'hitstun': 12, 'blockstun': 6, 'knockback_x': 0, 'knockback_y': 0, 'air_knockback_x': 5, 'air_knockback_y': 15, 'input_frame_duration': 10, 'cancel_frame_index': 10},
    '11': {'damage': 40, 'type': 'low', 'x_vel': 0, 'y_vel': 0, 'hitstun': 12, 'blockstun': 6, 'knockback_x': 0, 'knockback_y': 0, 'air_knockback_x': 5, 'air_knockback_y': 15, 'input_frame_duration': 18, 'cancel_frame_index': 8},
    '111': {'damage': 70, 'type': 'low', 'x_vel': 20, 'y_vel': 0, 'hitstun': 12, 'blockstun': 6, 'knockback_x': 5, 'knockback_y': 15, 'air_knockback_x': 5, 'air_knockback_y': 30, 'input_frame_duration': 26, 'cancel_frame_index': 8},
    'c2': {'damage': 70, 'type': 'low', 'x_vel': 10, 'y_vel': 0, 'hitstun': 0, 'blockstun': 3, 'knockback_x': 10, 'knockback_y': 10, 'air_knockback_x': 5, 'air_knockback_y': 10, 'input_frame_duration': 0, 'cancel_frame_index': 0},
    'j2': {'damage': 60, 'type': 'overhead', 'x_vel': 0, 'y_vel': 0, 'hitstun': 0, 'blockstun': 3, 'knockback_x': 10, 'knockback_y': 10, 'air_knockback_x': 5, 'air_knockback_y': 10, 'input_frame_duration': 0, 'cancel_frame_index': 0},
}

red_attacks = {
    '1': {'damage': 30, 'type': 'high', 'x_vel': 2, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 4, 'hitstun': 13, 'blockstun': 7, 'knockback_x': 0, 'knockback_y': 0, 'air_knockback_x': 5, 'air_knockback_y': 15, 'input_frame_duration': 8, 'cancel_frame_index': 8},
    '11': {'damage': 50, 'type': 'mid', 'x_vel': 8, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 7, 'hitstun': 17, 'blockstun': 12, 'knockback_x': 8, 'knockback_y': 0, 'air_knockback_x': 5, 'air_knockback_y': 15, 'input_frame_duration': 20, 'cancel_frame_index': 12},
    '111': {'damage': 80, 'type': 'mid', 'x_vel': 15, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 7, 'hitstun': 1, 'blockstun': 7, 'knockback_x': 17, 'knockback_y': 22, 'air_knockback_x': 15, 'air_knockback_y': 20, 'input_frame_duration': 32, 'cancel_frame_index': 12},
    '2': {'damage': 50, 'type': 'mid', 'x_vel': 10, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 4, 'hitstun': 17, 'blockstun': 12, 'knockback_x': 3, 'knockback_y': 0, 'air_knockback_x': 5, 'air_knockback_y': 15, 'input_frame_duration': 10, 'cancel_frame_index': 10},
    '22': {'damage': 50, 'type': 'mid', 'x_vel': 10, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 4, 'hitstun': 17, 'blockstun': 12, 'knockback_x': 3, 'knockback_y': 0, 'air_knockback_x': 5, 'air_knockback_y': 15, 'input_frame_duration': 20, 'cancel_frame_index': 10},
    '221': {'damage': 50, 'type': 'mid', 'x_vel': 8, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 7, 'hitstun': 1, 'blockstun': 12, 'knockback_x': 8, 'knockback_y': 15, 'air_knockback_x': 5, 'air_knockback_y': 15, 'input_frame_duration': 20, 'cancel_frame_index': 12},
    'c1': {'damage': 30, 'type': 'low', 'x_vel': 0, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 4, 'hitstun': 13, 'blockstun': 7, 'knockback_x': 0, 'knockback_y': 0, 'air_knockback_x': 5, 'air_knockback_y': 15, 'input_frame_duration': 8, 'cancel_frame_index': 8},
    'c2': {'damage': 50, 'type': 'low', 'x_vel': 4, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 5, 'hitstun': 1, 'blockstun': 7, 'knockback_x': 5, 'knockback_y': 15, 'air_knockback_x': 5, 'air_knockback_y': 15, 'input_frame_duration': 10, 'cancel_frame_index': 10},
    'j1': {'damage': 40, 'type': 'overhead', 'x_vel': 0, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 0, 'hitstun': 8, 'blockstun': 3, 'knockback_x': 8, 'knockback_y': 0, 'air_knockback_x': 5, 'air_knockback_y': 12, 'input_frame_duration': 0, 'cancel_frame_index': 0},
    'j2': {'damage': 50, 'type': 'overhead', 'x_vel': 0, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 0, 'hitstun': 0, 'blockstun': 3, 'knockback_x': 15, 'knockback_y': 15, 'air_knockback_x': 10, 'air_knockback_y': 12, 'input_frame_duration': 0, 'cancel_frame_index': 0},
}

red_special_attacks = {
    'S': {'damage': 100, 'type': 'high', 'x_vel': 50, 'y_vel': 0, 'vel_start_frame_index': 4, 'vel_end_frame_index': 14, 'hitstun': 15, 'blockstun': 8, 'knockback_x': 14, 'knockback_y': 15, 'air_knockback_x': 14, 'air_knockback_y': 12, 'input_frame_duration': 0, 'cancel_frame_index': 0, 'projectile': False, 'projectile_start_frame': 0},
}

yellow_attacks = {
    '1': {'damage': 30, 'type': 'high', 'x_vel': 2, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 4, 'hitstun': 13, 'blockstun': 7, 'knockback_x': 0, 'knockback_y': 0, 'air_knockback_x': 5, 'air_knockback_y': 15, 'input_frame_duration': 8, 'cancel_frame_index': 8},
    '11': {'damage': 50, 'type': 'mid', 'x_vel': 8, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 7, 'hitstun': 17, 'blockstun': 12, 'knockback_x': 8, 'knockback_y': 0, 'air_knockback_x': 5, 'air_knockback_y': 15, 'input_frame_duration': 20, 'cancel_frame_index': 12},
    '111': {'damage': 80, 'type': 'mid', 'x_vel': 10, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 7, 'hitstun': 11, 'blockstun': 7, 'knockback_x': 17, 'knockback_y': 22, 'air_knockback_x': 15, 'air_knockback_y': 20, 'input_frame_duration': 32, 'cancel_frame_index': 12},
    'f1': {'damage': 60, 'type': 'overhead', 'x_vel': 10, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 12, 'hitstun': 15, 'blockstun': 7, 'knockback_x': 6, 'knockback_y': 0, 'air_knockback_x': 10, 'air_knockback_y': 15, 'input_frame_duration': 13, 'cancel_frame_index': 13},
    'f11': {'damage': 80, 'type': 'mid', 'x_vel': 10, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 7, 'hitstun': 1, 'blockstun': 7, 'knockback_x': 17, 'knockback_y': 22, 'air_knockback_x': 15, 'air_knockback_y': 20, 'input_frame_duration': 25, 'cancel_frame_index': 12},
    '2': {'damage': 50, 'type': 'mid', 'x_vel': 10, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 4, 'hitstun': 17, 'blockstun': 12, 'knockback_x': 3, 'knockback_y': 0, 'air_knockback_x': 5, 'air_knockback_y': 15, 'input_frame_duration': 10, 'cancel_frame_index': 10},
    '21': {'damage': 80, 'type': 'mid', 'x_vel': 10, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 7, 'hitstun': 1, 'blockstun': 7, 'knockback_x': 17, 'knockback_y': 22, 'air_knockback_x': 15, 'air_knockback_y': 20, 'input_frame_duration': 22, 'cancel_frame_index': 12},
    'c1': {'damage': 30, 'type': 'low', 'x_vel': 0, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 4, 'hitstun': 13, 'blockstun': 7, 'knockback_x': 0, 'knockback_y': 0, 'air_knockback_x': 5, 'air_knockback_y': 15, 'input_frame_duration': 8, 'cancel_frame_index': 8},
    'c2': {'damage': 50, 'type': 'low', 'x_vel': 4, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 5, 'hitstun': 1, 'blockstun': 7, 'knockback_x': 5, 'knockback_y': 15, 'air_knockback_x': 5, 'air_knockback_y': 15, 'input_frame_duration': 10, 'cancel_frame_index': 10},
    'j1': {'damage': 40, 'type': 'overhead', 'x_vel': 0, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 0, 'hitstun': 8, 'blockstun': 3, 'knockback_x': 8, 'knockback_y': 0, 'air_knockback_x': 5, 'air_knockback_y': 12, 'input_frame_duration': 0, 'cancel_frame_index': 0},
    'j2': {'damage': 50, 'type': 'overhead', 'x_vel': 0, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 0, 'hitstun': 1, 'blockstun': 3, 'knockback_x': 15, 'knockback_y': 15, 'air_knockback_x': 10, 'air_knockback_y': 12, 'input_frame_duration': 0, 'cancel_frame_index': 0},
}

yellow_special_attacks = {
    'S': {'damage': 80, 'type': 'high', 'x_vel': 0, 'y_vel': 0, 'vel_start_frame_index': 0, 'vel_end_frame_index': 0, 'hitstun': 15, 'blockstun': 8, 'knockback_x': 7, 'knockback_y': 0, 'air_knockback_x': 10, 'air_knockback_y': 12, 'input_frame_duration': 0, 'cancel_frame_index': 0, 'projectile': True, 'projectile_start_frame': 6},
}