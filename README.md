# ots_cva

## Tools
1. https://www.makesense.ai/
2. TIC-80
3. Game: https://tic80.com/play?cart=1834
4. MacBook Pro 2018 (Intel)
5. Python 3.12
6. https://www.makesense.ai to create annotations
7. https://abhitronix.github.io/vidgear for fast scree capture 
8. Ultralytics YOLO11 as detection and classify model

## Notebook:
in "notebook" folder
or available online:
https://colab.research.google.com/drive/1w9jT-_ge6285LqSzqHQrclPMyj1vvzB5?usp=sharing

## Getting started
Don't forget to replace window_name variable to your's (before running .py scripts)

## Project Structure
### Data collectors:
./collector_timed_colorful.py - Timed image collection
./collector_keypressed_colorful.py - collect images when press controls in game
./collector_keypressed_gray.py - same, but greyscale images
./collector_keypressed_canny.py - collect images for Canny Edge Detection

### Bots
./bot_script.py - usual game bot. Uses CV to find enemies, player, controls
./bot_dl.py - pure dl bot
./bot_dl_canny.py - same, but trained on Canny Edge images,

### Data
./data/images - Initial collected data
./data/images_labels - labels created with www.makesense.ai

### Datasets







