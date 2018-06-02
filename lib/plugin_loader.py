# -*- coding: utf-8 -*-
import imp
import os

PluginFolder = "./lib/plugins"
MainModule = "__init__"


def getPlugins():
    plugins = []
    possibleplugins = os.listdir(PluginFolder)
    for i in possibleplugins:
        location = os.path.join(PluginFolder, i)
        if not os.path.isdir(location) or not MainModule + ".py" in os.listdir(location):
            continue
        info = imp.find_module(MainModule, [location])
        plugins.append({"name": i, "info": info})
    return plugins


def loadPlugin(plugin):
    return imp.load_module(MainModule, *plugin["info"])


for i in getPlugins():
    print("[PLUGIN] " + i["name"])
    plugin = loadPlugin(i)
    plugin.run()
