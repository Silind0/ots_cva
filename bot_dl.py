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

model = YOLO("model/classify/kirkir_classify_model_best.pt")

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

def processGameScreen(model, result):
    global start
    global player
    global over
    global enemies


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


def bot(model, result):
    global start
    global over
    global player

    print('entering bot() function')

    decision = result.summary()[0]['name']
    if decision == 'KEY_UP':
        pressKey(Key.up)
    elif decision == 'KEY_DOWN':
        pressKey(Key.down)
    elif decision == 'KEY_LEFT':
        pressKey(Key.left)
    elif decision == 'KEY_RIGHT':
        pressKey(Key.right)
    elif decision == "KEY_FIRE":
        pressKey(KeyCode.from_char('z'))
    else:
        releaseAllKeys()



#################### Main Loop #####################
while True:
    last_time = time.time()

    frame = stream.read()

    if frame is None:
        break


    #For mss backend
    drop_alpha = frame[:,:,:3] # BGR

    results = model(drop_alpha)

    print('process')
    if len(results) > 0:
        print('process')
        processGameScreen(model = model, result = results[0])
        bot(model = model, result = results[0])
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
