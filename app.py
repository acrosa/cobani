# -*- coding: utf-8 -*-
import argparse
import configparser
import datetime

import lib.train
import lib.camera
import lib.nest
import lib.slack
import lib.plugin_loader

if __name__ == "__main__":
    desc = "Cobani security. " \
           "Allows to train a model with downloaded data from Raspberry Pi and Nest cameras."
    parser = argparse.ArgumentParser(description=desc)

    config = configparser.ConfigParser()
    config.read('.cobani')

    # Train machine learning model and store it locally at directory
    parser.add_argument("--train", required=False,
                        help="trains a new model and saves it in the specified directory.", action='store_true')

    # Predicts using the trained model.
    parser.add_argument("--predict", required=False,
                        help="predicts using the trained model. By default will look at the last imagge downloaded on the 'images/all' folder.", action='store_true')

    # Starts the Slack bot.
    parser.add_argument("--slack", required=False,
                        help="Starts a Slack bot.", action='store_true')
    parser.add_argument("--slack_changes", required=False,
                        help="Starts a Slack bot that notifies on camera changes.", action='store_true')

    # fetch Nest camera images and store them locally
    parser.add_argument("--nest", required=False,
                        help="fetches last image from Nest cameras.", action='store_true')
    parser.add_argument("--repeat", required=False,
                        help="keeps fetching new images with the delay specified in seconds.", default=-1)
    parser.add_argument("--store", required=False,
                        help="keeps only one photo as the latest image.", default=True)

    # fetch Nest camera images and store them locally
    parser.add_argument("--picamera", required=False,
                        help="fetches last image from the Raspberry Pi Camera.", action='store_true')

    # Parse the command-line arguments.
    args = parser.parse_args()

    # Get the arguments.
    if args.nest:
        print("[RUN] Fetching Nest images")
        lib.nest.fetch(config, int(args.repeat), args.store == "true")

    if args.picamera:
        print("[RUN] Fetching Raspberry Pi Camera images")
        lib.camera.fetch(config, int(args.repeat))

    if args.train:
        print("[RUN] Training model")
        saved_model_dir = "model/ " + str(datetime.datetime.now())
        lib.train.train(config, saved_model_dir)

    if args.predict:
        print("[RUN] Analyzing image")
        lib.predict.predict(config, int(args.repeat))

    if args.slack:
        print("[RUN] Starting interactive slack bot")
        lib.slack.bot(config)

    if args.slack_changes:
        print("[RUN] Starting camera changes slack bot")
        lib.slack.changes(config, int(args.repeat))
