#!/bin/bash

python app.py --nest --repeat 30 --store false >nest.out 2>nest.err &
python app.py --predict --repeat 120 >predict.out 2>predict.err &
python app.py --slack >slack.out 2>slack.err &
python app.py --slack_changes --repeat 10 >slack_changes.out 2>slack_changes.err &