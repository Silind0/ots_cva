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
# 1 раз в 2 секунды сохраняет скриншот в папку images
# Регулируется через time.sleep(2)
##############################################

############## Window Name ###################
window_name = "TIC-80"
##############################################



model = YOLO("yolo11n.pt")

os.chdir(os.path.dirname(os.path.abspath(__file__)))
IMAGES_PATH = "data/images/"

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

#################### Loop
try:
    while True:
        last_time = time.time()

        frame = stream.read()

        if frame is None:
            break

    
        #For mss backend
        drop_alpha = frame[:,:,:3] # BGR
        rgb = cv2.cvtColor(drop_alpha, cv2.COLOR_BGR2RGB)

        #For PIL backend
        # drop_alpha = frame[..., ::-1][:,:,:3][..., ::-1]
        # rgb = cv2.cvtColor(drop_alpha, cv2.COLOR_BGR2RGB)


        imgname = os.path.join(IMAGES_PATH + str(uuid.uuid1())+'.jpg')

        cv2.imwrite(imgname,  drop_alpha) # Необходимо отключить при замере производительности
        # cv2.imshow('YOLO',  drop_alpha)

        # results = model(rgb)
        # cv2.imshow('YOLO', results[0].plot()[..., ::-1])

        print("fps: {}".format(1 / (time.time() - last_time)))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(drop_alpha[1])
            print(drop_alpha.shape)
            cv2.destroyAllWindows()
            stream.stop()
            break

        time.sleep(2) # необходимо отключить при замере производительности

finally:
    # listener.stop()
    print('Done.')
    print(drop_alpha[1])
    print(drop_alpha.shape)
    cv2.destroyAllWindows()
    stream.stop()