LED_RING = modules.led1
ROTARY = modules.rotary_encoder1
LIGHT_DETECTOR = myModules.light_level3
RESET_BUTTON = modules.button1
POTENTIONMETER = modules.potentiometer2

DIRECTIONS_NUMBER = 8

BLACK = 0x000000
RED =  0xFF0000
BLUE = 0x0000FF
YELLOW = 0xFFFF00

saved_raw_rotation = 0
saved_direction = 0

state_age_counter = 0
state_age_limit = 10
solar_state_age_limit = 20

class GameStates(Enum):
    OUTER_ASTEROID = 0,
    INNER_ASTEROID = 1,
    OUTER_SOLAR_FLARE = 2,
    INNER_SOLAR_FLARE = 3,
    GAME_OVER = 4,
    RANDOMIZE_EVENT = 5

game_state = GameStates.OUTER_ASTEROID
event_direction = 0
score = 0

class Directions(Enum):
    W = 0,
    NW = 1,
    N = 2,
    NE = 3,
    E = 4,
    SE = 5,
    S = 6,
    SW = 7

OUTER_ASTEROID_POSITIONS = [
    [0, 2],
    [0, 0],
    [2, 0],
    [4, 0],
    [4, 2],
    [4, 4],
    [2, 4],
    [0, 4]
]

INNER_ASTEROID_POSITIONS = [
    [1, 2],
    [1, 1],
    [2, 1],
    [3, 1],
    [3, 2],
    [3, 3],
    [2, 3],
    [1, 3]
]

RING_DIRECTIONS = [4, 5, 6, 7, 0, 1, 2, 3]

def disable_screen_pixels():
    for i in range(5):
        for j in range(5):
            led.unplot(i, j)

def light_ring_node(node_id):
    LED_RING.set_all(BLACK)
    LED_RING.set_brightness(60)

    if game_state == GameStates.OUTER_SOLAR_FLARE or game_state == GameStates.INNER_SOLAR_FLARE:
        if POTENTIONMETER.position() > 80:
            LED_RING.set_all(BLUE)
            LED_RING.set_brightness(20)
        else:
            LED_RING.set_all(YELLOW)
            LED_RING.set_brightness(20)
    else:
        if POTENTIONMETER.position() > 20:
            LED_RING.set_all(YELLOW)
            LED_RING.set_brightness(20)
    
    LED_RING.set_pixel_color(RING_DIRECTIONS[node_id], BLUE)

def light_screen_node(x, y):
    led.plot(x, y)

def happy_or_skull():
    if modules.button1.pressed():
        basic.show_icon(IconNames.SKULL)
    else:
        basic.show_icon(IconNames.HAPPY)

def update_direction(raw_rotation):
    global saved_raw_rotation
    global saved_direction

    if raw_rotation > saved_raw_rotation:
        new_direction = saved_direction + 1 
        new_direction %= DIRECTIONS_NUMBER
        return new_direction if new_direction < DIRECTIONS_NUMBER else 0
    elif raw_rotation < saved_raw_rotation:
        new_direction = saved_direction - 1
        new_direction %= DIRECTIONS_NUMBER
        return new_direction if new_direction >= 0 else DIRECTIONS_NUMBER - 1
    else:
        return saved_direction

def update_player_rotation():
    global saved_raw_rotation
    global saved_direction

    raw_rotation = ROTARY.position()

    if POTENTIONMETER.position() > 20:
        saved_raw_rotation = raw_rotation
        light_ring_node(direction)

    if saved_raw_rotation != raw_rotation:
        direction = update_direction(raw_rotation)

        light_ring_node(direction)

        saved_raw_rotation = raw_rotation
        saved_direction = direction

def paint_spaceship():
    light_screen_node(2, 2)

def paint_solar_flare():
    global game_state

    disable_screen_pixels()

    # paint outer layer for both solar events
    # left vertical
    light_screen_node(0, 0)
    light_screen_node(0, 1)
    light_screen_node(0, 2)
    light_screen_node(0, 3)
    light_screen_node(0, 4)
    # upper horizontal
    light_screen_node(1, 0)
    light_screen_node(2, 0)
    light_screen_node(3, 0)
    # lower horizontal
    light_screen_node(1, 4)
    light_screen_node(2, 4)
    light_screen_node(3, 4)
    # right vertical
    light_screen_node(4, 0)
    light_screen_node(4, 1)
    light_screen_node(4, 2)
    light_screen_node(4, 3)
    light_screen_node(4, 4)

    if game_state == GameStates.INNER_SOLAR_FLARE:
        # left vertical
        light_screen_node(1, 1)
        light_screen_node(1, 2)
        light_screen_node(1, 3)
        # upper horizontal
        light_screen_node(2, 1)
        # lower horizontal
        light_screen_node(2, 3)
        # right vertical
        light_screen_node(3, 1)
        light_screen_node(3, 2)
        light_screen_node(3, 3)

    paint_spaceship()

def paint_asteroid():
    global game_state
    global event_direction

    disable_screen_pixels()

    if game_state == GameStates.OUTER_ASTEROID:
        x, y = OUTER_ASTEROID_POSITIONS[event_direction]
        light_screen_node(x, y)

    if game_state == GameStates.INNER_ASTEROID:
        x, y = INNER_ASTEROID_POSITIONS[event_direction]
        light_screen_node(x, y)
    
    paint_spaceship()

def randomize_event():
    global game_state
    global event_direction

    randomNum = randint(0, 5)
    event_direction = randint(0, 7)

    # solar flare is rare event
    if randomNum == 0:
        game_state = GameStates.OUTER_SOLAR_FLARE
    else:
        game_state = GameStates.OUTER_ASTEROID 

def check_if_shields_ready_for_solar_blast():
    global game_state
    global saved_direction

    window_covers_enabled = LIGHT_DETECTOR.light_level() < 20
    power_distibuted = POTENTIONMETER.position() > 80

    light_ring_node(saved_direction)

    if window_covers_enabled and power_distibuted:
        return True

    return False

def on_reset_button_pressed():
    global game_state
    global state_age_counter
    global score

    game_state = GameStates.OUTER_ASTEROID
    state_age_counter = 0
    score = 0
    light_ring_node(saved_direction)

input.on_button_pressed(Button.A, on_reset_button_pressed)

def on_forever():
    global game_state
    global state_age_counter
    global state_age_limit
    global score

    update_player_rotation()

    ############################
    # GAME LOGIC STATE MACHINE #
    ############################
    if game_state == GameStates.RANDOMIZE_EVENT:
        randomize_event()
    
    elif game_state == GameStates.OUTER_ASTEROID:
        paint_asteroid()
        state_age_counter += 1
        if state_age_counter >= state_age_limit:
            game_state = GameStates.INNER_ASTEROID
            state_age_counter = 0
    
    elif game_state == GameStates.INNER_ASTEROID:
        paint_asteroid()
        state_age_counter += 1
        if state_age_counter >= state_age_limit:
            state_age_counter = 0
            if event_direction == saved_direction:
                score += 1
                game_state = GameStates.RANDOMIZE_EVENT
            else:
                game_state = GameStates.GAME_OVER
    
    elif game_state == GameStates.OUTER_SOLAR_FLARE:
        paint_solar_flare()
        state_age_counter += 1
        if state_age_counter >= solar_state_age_limit:
            game_state = GameStates.INNER_SOLAR_FLARE
            state_age_counter = 0

    elif game_state == GameStates.INNER_SOLAR_FLARE:
        paint_solar_flare()
        state_age_counter += 1
        if state_age_counter >= solar_state_age_limit:
            state_age_counter = 0
            if check_if_shields_ready_for_solar_blast():
                score += 3
                game_state = GameStates.RANDOMIZE_EVENT
            else:
                game_state = GameStates.GAME_OVER

    elif game_state == GameStates.GAME_OVER:
        state_age_counter += 1
        basic.show_icon(IconNames.SKULL)
        basic.show_number(score)

    if modules.button1.pressed():
        on_reset_button_pressed()

def onEvery_interval():
    on_forever()

loops.every_interval(200, onEvery_interval)
