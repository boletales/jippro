import numpy as np 
import tensorflow as tf
import keras
import json
import random
import matplotlib.pylab as plt
import os
import sys
from keras.layers import Input
from keras.layers import Dense
from keras.models import Model
from keras.datasets import mnist
from keras.utils import to_categorical
from keras.layers import Conv2D, MaxPooling2D,AveragePooling2D,Conv1D,MaxPooling1D,AveragePooling1D, Flatten, Dropout,Reshape
from keras.layers.noise import GaussianNoise,AlphaDropout,GaussianDropout
from keras.layers.recurrent import LSTM,GRU,RNN,SimpleRNN
from keras.backend import reshape
from keras.callbacks import EarlyStopping

olddir = os.getcwd()
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

name=sys.argv[1]

dai2_diffs = ["▽1","▽2","▽3","▽4","▽5","▽6","▽7","▽8","▽9","▽10","▽11","▽11+","▽12-","▽12","▽12+"]

interval = 100

input_shape = (int(200*1000/interval),8)

hashs = json.load(open("./samples/"+str(name)+"_hashs.json"))
charts  = json.load(open("./samples/"+str(name)+"_samples.json"))
answers = json.load(open("./samples/"+str(name)+"_answers.json"))
songs = set(hashs)
testsongs = random.sample(set(hashs),int(len(list(songs))/10))
x_train_l = []
y_train_l = []
x_test_l  = []
y_test_l  = []
x_all_l  = []
y_all_l  = []
_hash = []
_data = list(zip(charts,answers,hashs))
random.shuffle(_data)
for chart,answer,hash in _data:
  if hash in testsongs:
    if not hash in _hash:
      x_test_l.append(chart)
      y_test_l.append(answer)
  else:
      x_train_l.append(chart)
      y_train_l.append(answer)

  if not hash in _hash:
    x_all_l.append(chart)
    y_all_l.append(answer)
  _hash.append(hash)


x_train_law = np.array(x_train_l+x_test_l)
x_train = x_train_law.reshape((len(x_train_law),)+input_shape)
y_train = np.array(y_train_l+y_test_l)
x_test_law = np.array(x_test_l)
x_test = x_test_law.reshape((len(x_test_law),)+input_shape)
y_test = np.array(y_test_l)
x_all_law = np.array(x_all_l)
x_all = x_all_law.reshape((len(x_all_law),)+input_shape)
y_all = np.array(y_all_l)

num_filters = 8
l2 = 0.001

inputs = Input(shape=input_shape,name="input")

layers = [
    Reshape((int(200*1000/interval),8,1)),
    Conv2D(num_filters, kernel_size=(5,8), activation="relu", name="c1", kernel_regularizer=keras.regularizers.l2(l2)),
    AveragePooling2D(pool_size=(5,1),name="p1"),
    Reshape((int(200*1000/interval/5)-1,8,1)),
    Conv2D(num_filters, kernel_size=(5,8), activation="relu", name="c2", kernel_regularizer=keras.regularizers.l2(l2)),
    AveragePooling2D(pool_size=(5,1),name="p2"),
    Reshape((int(200*1000/interval/25)-1,8)),
    GRU(16, input_shape = (int(200*1000/interval/16)-2,1) , kernel_regularizer=keras.regularizers.l2(l2)),
    Flatten( name="f"),
    Dense(8,activation="relu",name="d1", kernel_regularizer=keras.regularizers.l2(l2)),
    Dense(1,activation="relu",name="last", kernel_regularizer=keras.regularizers.l2(l2))
]
layers_instance = [inputs]
for layer in layers:
    print(layer.name)
    layers_instance.append(layer(layers_instance[-1]))

model = keras.Model(inputs=layers_instance[0],outputs=layers_instance[-1])
model.summary()
model.compile(
    loss=keras.losses.mean_squared_error,
    optimizer=keras.optimizers.Adam(),
)

epochs = 50
early_stopping = keras.callbacks.EarlyStopping(monitor='val_loss', patience=3, verbose=0, mode='auto')
history = model.fit(x_train,y_train,epochs=epochs,batch_size=64,verbose=1,validation_split=len(y_test)/len(y_train),callbacks=[early_stopping])


loss = history.history['loss']
val_loss = history.history['val_loss']

plt.plot(range(len(loss[0:]))[0:],np.sqrt(loss[0:]),"b", label="train")
plt.plot(range(len(loss[0:]))[0:],np.sqrt(val_loss[0:]),"r", label="validate")
plt.legend()
plt.title("loss")
plt.show()

print("↓全データ↓")
train_scores = np.sqrt(model.evaluate(x_all, y_all, verbose=0))
print(train_scores)

print("↓テストデータ↓")
test_scores = np.sqrt(model.evaluate(x_test, y_test, verbose=0))
print(test_scores)

model.save("prototype2.h5")

diff_predict = model.predict(x_all)
plt.scatter(y_all,diff_predict)
plt.plot([0,14],[-1,13])
plt.plot([0,14],[0 ,14])
plt.plot([0,14],[1 ,15])
plt.show()

os.chdir(olddir)
