import numpy as np    #pip install "numpy<2" - yolo не рабоает с numpy2, нужно установить 1-ю версию
import cv2
from matplotlib.pyplot import title
from vidgear.gears import ScreenGear
from ultralytics import YOLO
import pyautogui
import uuid
import os
import time
import pygetwindow as gw
from pynput.keyboard import Key, Controller, KeyCode
import random


############## Window Name ###################
window_name = "TIC-80"
#################################

# model = YOLO("model/detection/kir_detection_best_100.pt") # 5 fps
model = YOLO("model/detection/best_openvino_model/") # 12 fps
# model = YOLO("model/detection/best_onnx_model/best.onnx") # Не взлетело, но у меня нет Cuda - MacBook 2018 Intel...

os.chdir(os.path.dirname(os.path.abspath(__file__)))

titles = gw.getAllTitles()
print(titles)

windows = []
for win in titles:
    geometry = gw.getWindowGeometry(win)
    if window_name in win:
        print(f'Window title: {win}')
        print(f'> top-left X coordinate: {geometry[0]}')
        print(f'> top-left Y coordinate: {geometry[1]}')
        print(f'> width: {geometry[2]}')
        print(f'> height: {geometry[3]}\n')
        windows.append(geometry)

w = windows[0]

w_x = w[0]
w_y = w[1]
w_width = w[2]
w_height = w[3]

aspect_x = None
aspect_y = None


#colorspace="COLOR_RGBA2BGR"
#backend="mss" / "PIL"
options = {'top': int(w[0]), 'left': int(w[1]), 'width': int(w[0]+w[2]), 'height': int(w[1]+w[3])}
print(options)
# stream = ScreenGear(logging=False, backend="pil", **options).start()
stream = ScreenGear(logging=False, backend="mss", **options).start()

keyboard = Controller()

############# Bot Game #####################
#represent our classes:
enemies_labels = [
    '5_Common_Enemy',
    '6_Radiation_Man',
    '7_Organ',
    '8_Sentinel',
    '9_Mouth',
    '10_Miner',
    '11_Tank_Purple',
    '12_Tank_Green'
]

bullet_labels = [
    '13_Bullet'
]

game_start_labels = [
    '2_Game_Start',
    '3_Press_Fire'
]

game_over_labels = [
    '1_Game_Over'
]

bonus_labels = [
    '0_Bonus'
]

player_labels = [
    '4_Player'
]

over = None
player = None
start = None
enemies = []
bullets = []
bonuses = []

press_start_time = None

keys_current_pressed = set()

def releaseKey(key):
    print('releasing key:', key)
    keyboard.release(key)
    keys_current_pressed.remove(key)

def releaseAllKeys():
    sett = keys_current_pressed.copy()
    for a in sett:
        releaseKey(a)

def pressKey(key):
    print('pressing key:', key)
    releaseAllKeys()

    keyboard.press(key)
    keys_current_pressed.add(key)

def isKeyPressed(key):
    return key in keys_current_pressed

def getBoxCenter(box):
    (left, top, right, bottom) = box
    return ( int((left + ((right - left)/2)).item()), int((top + ((bottom - top)/2)).item()) )

def processGameState(model, results):
    global start
    global player
    global over
    global enemies

    boxes = results.boxes

    for box in boxes:
        b = box.xyxy[0] # get box coordinates in (left, top, right, bottom) format
        c = model.names[int(box.cls)]


        if c in game_start_labels:
            start = b
            coord = getBoxCenter(b)
            print("start center= ", coord[0], coord[1])


        if c in player_labels:
            player = b
            coord = getBoxCenter(b)
            print("player center= ", coord[0], coord[1])


        if c in game_over_labels:
            over = getBoxCenter(b)
            print("pause center= ", over[0], over[1])


        if c in enemies_labels:
            enemies.append(b)

        if c in bullet_labels:
            bullets.append(b)

        if c in bonus_labels:
            bonuses.append(b)


def clearState():
    global over
    global player
    global start
    global enemies
    global bullets
    global bonuses

    over = None
    player = None
    start = None
    enemies = []
    bullets = []
    bonuses = []


def clickStart():
    global start
    global press_start_time

    press_start_time = None
    pressKey(KeyCode.from_char('z'))

def decideMoveKey():
    print('decide move func')
    global player
    global bullets
    global enemies


    #Trully decide
    if len(enemies) > 0:
        (px, py) = getBoxCenter(player)
        fw, fh = w_width, w_height

        # Bullets evasion
        for bullet in bullets:
            (bx, by) = getBoxCenter(bullet)
            if abs(by - py) < 20 and abs(bx - px) < 30:  # Horizontal bullet
                if px < fw - 10:
                    return Key.right
                elif px > 10:
                    return Key.left
            elif abs(bx - px) < 20 and abs(by - py) < 30:  # Vertical bullet
                if py < fh - 10:
                    return Key.down
                elif py > 10:
                    return Key.up

        # Run away from near enemies
        for enemy in enemies:
            (ex, ey) = getBoxCenter(enemy)
            dx = ex - px
            dy = ey - py
            if abs(dx) < 30 and abs(dy) < 30:
                if abs(dx) > abs(dy):
                    return Key.left if dx > 0 and px > 10 else Key.right
                else:
                    return Key.up if dy > 0 and py > 10 else Key.down

        # Fight towards enemy
        if enemies:
            enemies.sort(key=lambda e: (e[0] - px)**2 + (e[1] - py)**2)
            (tx, ty) = getBoxCenter(enemies[0])

            dx = tx - px
            dy = ty - py

            if abs(dx) > abs(dy):
                if dx > 0 and px < fw - 10:
                    return Key.right
                elif dx < 0 and px > 10:
                    return Key.left
            else:
                if dy > 0 and py < fh - 10:
                    return Key.down
                elif dy < 0 and py > 10:
                    return Key.up

    if len(enemies) == 0:
        return None


    return None


def movePlayer():
    global press_start_time

    key = decideMoveKey()

    if key is None:
        releaseAllKeys()
    else:
        pressKey(key)


    press_start_time = time.time() #Запоминаем время нажаия


def bot():
    global start
    global over
    global player

    print('entering bot() function')
    #print(start)
    if start is not None: # if there message about "Press fire" then start game/match
        releaseAllKeys()
        clickStart()
        clearState()

    if (over is not None):
        releaseAllKeys()
        clickStart()
        clearState()

    if (len(enemies) < 1):
        releaseAllKeys()

    if (over is None) & (player is not None):  # if there is player and game no "Game over message"
        movePlayer()



#################### Main Loop #####################
while True:
    last_time = time.time()

    frame = stream.read()

    if frame is None:
        break


    #For mss backend
    drop_alpha = frame[:,:,:3] # BGR
    # rgb = cv2.cvtColor(drop_alpha, cv2.COLOR_BGR2RGB)

    #For PIL backend
    # drop_alpha = frame[..., ::-1][:,:,:3][..., ::-1]
    # rgb = cv2.cvtColor(drop_alpha, cv2.COLOR_BGR2RGB)

    results = model(drop_alpha)

    # показ плота сбивает акивное окно.... убираем
    # plot = results[0].plot()
    # plot_height = plot.shape[0]
    # plot_widht = plot.shape[1]
    # print('plot_size=', plot_widht, plot_height)
    # aspect_x = w_width / plot_widht
    # aspect_y = w_height / plot_height
    # cv2.imshow('YOLO', plot)      # окно перестаёт быть активным, поэтому убираем показ.

    if len(results) > 0:
        print('process')
        processGameState(model = model, results = results[0])
        bot()
        clearState()

    print("fps: {}".format(1 / (time.time() - last_time)))


    if cv2.waitKey(1) & 0xFF == ord('q'):
        print(drop_alpha[1])
        print(drop_alpha.shape)
        cv2.destroyAllWindows()
        stream.stop()
        break

print('Done.')
cv2.destroyAllWindows()
stream.stop()
