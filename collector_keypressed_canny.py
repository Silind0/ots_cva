import numpy as np    #pip install "numpy<2" - yolo не рабоает с numpy2, нужно установить 1-ю версию
import cv2
import time
from vidgear.gears import ScreenGear
from ultralytics import YOLO
import pyautogui
import uuid
import os
import time
import pygetwindow as gw
from pynput import keyboard


############## Description ###################
# 1 раз в 1 секунду сохраняет canny скриншот в папку images/canny_keys/
# Регулируется через (time.time() - last_time) < 1
##############################################

############## Window Name ###################
window_name = "TIC-80"
#################################



model = YOLO("yolo11n.pt")

os.chdir(os.path.dirname(os.path.abspath(__file__)))
IMAGES_PATH = "data/images/canny_keys/"

KEY_RIGHT = "KEY_RIGHT"
KEY_LEFT = "KEY_LEFT"
KEY_UP = "KEY_UP"
KEY_DOWN = "KEY_DOWN"
KEY_NONE = "KEY_NONE"
KEY_FIRE = "KEY_FIRE"

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

#colorspace="COLOR_RGBA2BGR"
#backend="mss" / "PIL"
options = {'top': int(w[0]), 'left': int(w[1]), 'width': int(w[0]+w[2]), 'height': int(w[1]+w[3])}
print(options)
# stream = ScreenGear(logging=False, backend="pil", **options).start()
stream = ScreenGear(logging=False, backend="mss", **options).start()

last_time = time.time()
# frame = stream.read()


def on_press(key):
    try:
        global last_time
        global frame

        if (time.time() - last_time) < 1:
            return

        print('alphanumeric key {0} pressed'.format(key.char))
        if key == keyboard.KeyCode.from_char('z'):
            capture(folder=KEY_FIRE)
    except AttributeError:
        print('special key {0} pressed'.format(key))
        if key == keyboard.Key.space:
            capture(folder=KEY_NONE)
        elif key == keyboard.Key.left:
            capture(folder=KEY_LEFT)
        elif key == keyboard.Key.right:
            capture(folder=KEY_RIGHT)
        elif key == keyboard.Key.up:
            capture(folder=KEY_UP)
        elif key == keyboard.Key.down:
            capture(folder=KEY_DOWN)


def on_release(key):
    print('{0} released'.format(key))
    if key == keyboard.KeyCode.from_char('q'):
        # Stop listener
        stopAll()
        return False

listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)

listener.start()

def capture(folder):
    global last_time
    frame = stream.read()
    last_time = time.time()

    if frame is None:
        return

    print('Saved: ' + folder)

    # For mss backend
    drop_alpha = frame[:, :, :3]  # BGR
    gray = cv2.cvtColor(drop_alpha, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(gray, threshold1=119, threshold2=250)

    # For PIL backend
    # drop_alpha = frame[..., ::-1][:,:,:3][..., ::-1]
    # rgb = cv2.cvtColor(drop_alpha, cv2.COLOR_BGR2RGB)

    imgname = os.path.join(IMAGES_PATH + folder + '/'  + str(uuid.uuid1()) + '.jpg')

    cv2.imwrite(imgname, canny)  # Необходимо отключить при замере производительности
    # cv2.imshow('YOLO',  drop_alpha)

    # results = model(rgb)
    # cv2.imshow('YOLO', results[0].plot()[..., ::-1])

    # print("fps: {}".format(1 / (time.time() - last_time)))

    # time.sleep(2)  # необходимо отключить при замере производительности
    # listener.stop()
    last_time = time.time()

def stopAll():
    listener.stop()
    cv2.destroyAllWindows()
    stream.stop()
    print('Done.')


#################### Loop
while True:
    last_time2 = time.time()
    time.sleep(1)


