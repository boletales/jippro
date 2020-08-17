#プロトタイプ1. 音符の配置を無視して、譜面全体で各レーンを押す回数のみから難易度を推定。これで上手くいったら泣く
import numpy as np 
import tensorflow as tf
import keras
import json
from keras.layers import Input #ネットワークの入力に用いる
from keras.layers import Dense #ネットワークの各層の変換に用いる（Dense: 通常の層（全結合層）を意味する）
from keras.models import Model #ニューラルネットワークモデル構築に用いる
from keras.datasets import mnist
from keras.utils import to_categorical
from keras.models import load_model
import sys,os,re,hashlib,json,codecs,numpy,math
from util import *

headerstr='{"name" : "第2もどき難易度_新","symbol" : "⊿","data_url" : "./dai2modoki_data.json","level_order" : ["1","2","3","4","5","6","7","8","9","10","11","11+","12-","12","12+","枠外"]}'

models = load_models()
dai2_data = load_dai2()
dai2_data_insane = load_dai2_insane()

modoki_sheet = []


def recursiveAssess(path):
    if os.path.isfile(path) and os.path.splitext(path)[1] in bmsexts:
        assess(path)
    elif os.path.isdir(path):
        files = os.listdir(path)
        for file in files:
            recursiveAssess(path+"/"+file)
            
def assess(path):
    song = convertBMS(path,dai2_data,dai2_data_insane,True)
    if song:
        diffdata = assessDiff(song,models)
        print(symbol+diffdata["fraclv"] + "\t\t"+song["title"])
        modoki_sheet.append(diffdata)

recursiveAssess(sys.argv[1])
datastr = json.dumps(modoki_sheet, ensure_ascii=False)
with open("./dai2modoki/dai2modoki_header.json",encoding="utf-8",mode="w") as f:
    f.write(headerstr)

with open("./dai2modoki/dai2modoki_data.json",encoding="utf-8",mode="w") as f:
    f.write(datastr)

with open("./dai2modoki/dai2modoki_QMS.json",encoding="utf-8",mode="w") as f:
    f.write('{"Datas":'+datastr+',"Header":'+headerstr+"}")