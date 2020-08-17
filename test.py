#プロトタイプ1. 音符の配置を無視して、譜面全体で各レーンを押す回数のみから難易度を推定。これで上手くいったら泣く
import numpy as np 
import scipy as sp
import sklearn as sk #これはScikit-Learnのこと
import matplotlib as mpl 
import matplotlib.pylab as plt # Matplotlibの中の一番使う部分
import tensorflow as tf
import keras
import json
from keras.layers import Input #ネットワークの入力に用いる
from keras.layers import Dense #ネットワークの各層の変換に用いる（Dense: 通常の層（全結合層）を意味する）
from keras.models import Model #ニューラルネットワークモデル構築に用いる
from keras.datasets import mnist
from keras.utils import to_categorical
from keras.models import load_model

dai2_diffs = ["▽1","▽2","▽3","▽4","▽5","▽6","▽7","▽8","▽9","▽10","▽11","▽11+","▽12-","▽12","▽12+"]

model = load_model('prototype1.h5')

while True:
    print(model.predict(np.array([json.loads(input("input keys count> "))]), batch_size=1)[0])
