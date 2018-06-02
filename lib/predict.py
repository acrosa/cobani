# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import glob
import os
import time
from shutil import copyfile
import numpy as np
import tensorflow as tf


def load_graph(model_file):
    graph = tf.Graph()
    graph_def = tf.GraphDef()

    with open(model_file, "rb") as f:
        graph_def.ParseFromString(f.read())
    with graph.as_default():
        tf.import_graph_def(graph_def)

    return graph


def read_tensor_from_image_file(file_name,
                                input_height=299,
                                input_width=299,
                                input_mean=0,
                                input_std=255):
    input_name = "file_reader"
    output_name = "normalized"
    file_reader = tf.read_file(file_name, input_name)
    if file_name.endswith(".png"):
        image_reader = tf.image.decode_png(
            file_reader, channels=3, name="png_reader")
    elif file_name.endswith(".gif"):
        image_reader = tf.squeeze(
            tf.image.decode_gif(file_reader, name="gif_reader"))
    elif file_name.endswith(".bmp"):
        image_reader = tf.image.decode_bmp(file_reader, name="bmp_reader")
    else:
        image_reader = tf.image.decode_jpeg(
            file_reader, channels=3, name="jpeg_reader")
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0)
    resized = tf.image.resize_bilinear(
        dims_expander, [input_height, input_width])
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    sess = tf.Session()
    result = sess.run(normalized)

    return result


def load_labels(label_file):
    label = []
    proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
    for l in proto_as_ascii_lines:
        label.append(l.rstrip())
    return label


def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]


def get_latest_file(dir):
    list_of_files = glob.glob(dir + '/*')
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def predict_images(config, camera_images):
    tfhub_module = config.get("tensorflow", "hub_model")
    input_height = config.getint("tensorflow", "input_height")
    input_width = config.getint("tensorflow", "input_width")
    input_mean = 0
    input_std = 255
    model_file = config.get("tensorflow", "model_file")
    label_file = config.get("tensorflow", "label_file")
    input_layer = config.get("tensorflow", "input_layer")
    output_layer = config.get("tensorflow", "output_layer")

    predictions = []
    for camera_image in camera_images:
        folder, image = camera_image

        # check image is valid, before analyzing it
        # sometimes cameras create empty files
        statinfo = os.stat(image)
        if statinfo.st_size > 0:
            graph = load_graph(model_file)
            t = read_tensor_from_image_file(
                image,
                input_height=input_height,
                input_width=input_width,
                input_mean=input_mean,
                input_std=input_std)

            input_name = "import/" + input_layer
            output_name = "import/" + output_layer
            input_operation = graph.get_operation_by_name(input_name)
            output_operation = graph.get_operation_by_name(output_name)

            with tf.Session(graph=graph) as sess:
                results = sess.run(output_operation.outputs[0], {
                    input_operation.outputs[0]: t
                })
            results = np.squeeze(results)

            top_k = results.argsort()[-5:][::-1]
            labels = load_labels(label_file)
            place = config.get("cameras", folder)
            threshold = 0.5
            print("Analyzing image: " + image + " from place: " + place)
            found_objects = []
            for i in top_k:
                print(labels[i], results[i])
                if results[i] >= threshold:
                    found_objects.append(labels[i])
            print("------------------------------------------------------------")
            predictions.append((place, found_objects, image))
    return predictions


def build_summary_text_for_change(prediction):
    place, labels, image = prediction
    return ",".join(labels)


def predict(config, repeat=-1):
    if repeat > 0:
        print("Checking and analyzing camera every " + str(repeat) + " seconds")
        while(True):
            prediction = predict_last_images(config)
            save_predictions(prediction)
            time.sleep(repeat)
    else:
        print("Checking and analyzing camera once")
        prediction = predict_last_images(config)
        save_predictions(prediction)


def predict_last_images(config):
    camera_images = []
    cameras_folders = get_immediate_subdirectories("images/all/")
    for folder in cameras_folders:
        camera_images.append((folder, get_latest_file("images/all/" + folder)))
    return predict_images(config, camera_images)


def save_predictions(predictions):
    print("saving predictions " + str(predictions))
    for prediction in predictions:
        place, labels, image = prediction
        if image:
            # save prediction description
            file = open("predictions/" + place + ".txt", "w+")
            file.write(build_summary_text_for_change(prediction))
            file.close()
            # save image
            copyfile(image, "predictions/" + place + ".jpg")
        else:
            print("Error, no image attached to predictions. Place:" +
                  place + " labels: " + labels)


def predict_changes(config, repeat=30):
    print("Checking camera every " + str(repeat) + " seconds")
    while(True):
        prediction = predict(config)
        save_prediction(prediction)
        time.sleep(repeat)
