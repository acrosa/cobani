# -*- coding: utf-8 -*-
import urllib2
from urllib2 import urlopen
import json
import time
import codecs
import os
from PIL import Image
try:
    import picamera
except Exception:
    print("[WARNING] picamera is needed to fetch Raspberry Pi snapshots.")
from time import sleep


def resize_image(filename, destination_max_width=500, destination_max_height=500):
    size = (destination_max_width, destination_max_height)
    image = Image.open(filename)
    image.thumbnail(size, Image.ANTIALIAS)
    image.save(filename, "JPEG")


def timestamp_filename():
    return str(time.time()) + '.jpg'


def store_camera_image():
    try:
        camera = picamera.PiCamera()
        camera.start_preview()
        sleep(5)
        directory = "images/all/picamera"
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = timestamp_filename()
        camera_file = directory + "/" + str(filename)
        camera.capture(camera_file)
        print("Saved camera file: " + camera_file)
        camera.stop_preview()
    except Exception as e:
        print("Exception trying to fetch camera from raspberry pi camera. Error: " + str(e))


def fetch(config, repeat=-1):
    if repeat > 0:
        print("repeats every " + str(repeat) + " seconds.")
    if repeat > 0:
        while(True):
            store_camera_image()
            time.sleep(repeat)
    else:
        store_camera_image()
