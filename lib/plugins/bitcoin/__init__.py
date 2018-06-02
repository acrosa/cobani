# -*- coding: utf-8 -*-
import urllib2
import codecs
import json
import re
from urllib2 import urlopen
from slackbot.bot import respond_to
from slackbot.bot import listen_to


@respond_to('bitcoin', re.IGNORECASE)
def bitcoin(message):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
    req = urllib2.Request(
        "https://api.coindesk.com/v1/bpi/currentprice.json", None, headers)
    response = urllib2.urlopen(req)
    reader = codecs.getreader("utf-8")
    data = json.load(reader(response))
    message.reply('El bitcoin esta a $' +
                  str(data.get("bpi").get("USD").get("rate")) + '. 🤑')


def run():
    pass
