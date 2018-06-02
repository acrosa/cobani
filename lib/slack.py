# -*- coding: utf-8 -*-
import re
import time
import configparser
import slackbot
import signal
import sys
import glob
import io
from threading import Thread
from slackbot import settings
from slackbot.bot import Bot
from slackbot.bot import respond_to
from slackbot.bot import listen_to
from slackclient import SlackClient
import urllib2
from urllib2 import urlopen
import codecs
import json

config = configparser.ConfigParser()
config.read('.cobani')
slack_token = config.get("slack", "api-token")
sc = SlackClient(slack_token)


def bot(config):
    # Run interactive bot
    settings.API_TOKEN = config.get("slack", "api-token")
    bot = Bot()
    bot.run()


@respond_to('hi', re.IGNORECASE)
def hi(message):
    message.reply('I can understand hi or HI!')
    # react with thumb up emoji
    message.react('+1')


@respond_to('status')
def status(message):
    # Message is replied to the sender (prefixed with @user)
    message.reply('Let me check the house...')
    config = configparser.ConfigParser()
    config.read('.cobani')
    changes = get_saved_predictions()
    slack_send_changes(changes, upload_photo=True)


def get_files(dir, extension=""):
    return glob.glob(dir + '/*' + extension)


def get_saved_predictions():
    predictions_files = get_files(dir="predictions", extension="txt")
    predictions = []
    for f in predictions_files:
        file = open(f, "r")
        labels = file.read()
        file.close()
        image = f.replace(".txt", "") + ".jpg"
        predictions.append((f, labels, image))
    return predictions


def build_summary_text_for_change(change):
    place, labels, image = change
    summary = "\n - *" + place + "* found " + labels
    return summary


def slack_upload_image(image):
    with open(image, 'rb') as file_content:
        sc.api_call(
            "files.upload",
            channels=config.get("slack", "channel"),
            filename=image,
            file=io.BytesIO(file_content.read())
        )


def slack_send_message(text):
    sc.api_call(
        "chat.postMessage",
        channel=config.get("slack", "channel"),
        text=text
    )


def slack_send_changes(changes, upload_photo=False):
    for change in changes:
        place, labels, image = change
        # send summary
        summary = build_summary_text_for_change(change)
        slack_send_message(summary)
        # upload images
        if upload_photo:
            # TODO maybe enable but and resize images
            slack_upload_image(image)


def camera_predictions(config):
    predictions = lib.predict.predict(config)
    found = []
    for prediction in predictions:
        place, labels, image = prediction
        detected = ",".join(labels)
        found.append((place, detected, image))
    return found


def look_for_changes(config, upload_photo=False):
    print("Checking automatically for changes on cameras")
    predictions = get_saved_predictions()
    changes = []
    for prediction in predictions:
        place, labels, image = prediction
        previous = cameras_predictions.get(place)
        if previous != labels:
            changes.append((place, labels, image))
        cameras_predictions[place] = labels

    # build status message if there are changes
    if len(changes) > 0:
        slack_send_changes(changes, upload_photo)


# start polling for new cameras photos changes
cameras_predictions = {}


def changes(config, repeat=30):
    print("Checking camera every " + str(repeat) + " seconds")
    while(True):
        look_for_changes(config, upload_photo=False)
        time.sleep(repeat)
