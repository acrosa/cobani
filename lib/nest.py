# -*- coding: utf-8 -*-
import urllib2
from urllib2 import urlopen
import json
import time
import codecs
import os
from PIL import Image

nest_api_url = 'https://developer-api.nest.com'


def fetch_snapshots_urls(token):
    headers = {
        'Authorization': "Bearer {0}".format(token),
    }
    req = urllib2.Request(nest_api_url, None, headers)
    response = urllib2.urlopen(req)
    reader = codecs.getreader("utf-8")
    data = json.load(reader(response))

    # Verify the account has devices
    if 'devices' not in data:
        raise APIError(error_result("Nest account has no devices"))
    devices = data["devices"]

    # Verify the account has cameras
    if 'cameras' not in devices:
        raise APIError(error_result("Nest account has no cameras"))
    cameras = devices["cameras"]

    # Verify the account has 1 Nest Cam
    if len(cameras.keys()) < 1:
        raise APIError(error_result("Nest account has no cameras"))

    snapshots = {}
    for key in list(cameras.keys()):
        camera = cameras[key]

        # Verify the Nest Cam has a Snapshot URL field
        if 'snapshot_url' in camera:
            snapshot_url = camera["snapshot_url"]
            snapshots[key] = snapshot_url
        else:
            print("Error camera has no snapshot URL. Camera key: " + key)

    return snapshots


def timestamp_filename():
    return str(time.time()) + '.jpg'


def download_image_from_url(url=None, filename=timestamp_filename(), destination_dir="images/all"):
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    data = response.read()
    with open(destination_dir + "/" + str(filename), "wb") as code:
        code.write(data)
        code.flush()


def resize_image(filename, destination_max_width=500, destination_max_height=500):
    size = (destination_max_width, destination_max_height)
    image = Image.open(filename)
    image.thumbnail(size, Image.ANTIALIAS)
    image.save(filename, "JPEG")


def store_camera_image(token, store=True):
    try:
        print("Downloading image from cameras...")
        camera_images = fetch_snapshots_urls(token)
        for camera_key in camera_images:
            image_url = camera_images[camera_key]
            if store:
                filename = timestamp_filename()
            else:
                filename = "live.jpg"
            directory = "images/all/" + camera_key
            if not os.path.exists(directory):
                os.makedirs(directory)
            download_image_from_url(
                image_url, filename=filename, destination_dir=directory)
            resize_image(directory + "/" + filename)
            print("downloaded image: " + filename)
    except Exception as e:
        print("Exception trying to fetch camera image. Error: " + str(e))


def fetch(config, repeat=-1, store=True):
    token = config.get("nest", "token")
    if repeat > 0:
        print("repeats every " + str(repeat) + " seconds.")
        while(True):
            store_camera_image(token, store)
            time.sleep(repeat)
    else:
        store_camera_image(token, store)
