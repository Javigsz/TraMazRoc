import numpy as np
import pandas as pd
from pathlib import Path
import os.path

from sklearn.model_selection import train_test_split

import tensorflow as tf

from sklearn.metrics import r2_score


image_dir_train = Path('../red/img/train')
image_dir_test = Path('../red/img/test')


filepaths_train = pd.Series(list(image_dir_train.glob(r'*/*.jpg')), name='Filepath', dtype=str).astype(str)
filepaths_test = pd.Series(list(image_dir_test.glob(r'*/*.jpg')), name='Filepath', dtype=str).astype(str)

gsi_train = pd.Series(filepaths_train.apply(lambda x: os.path.split(os.path.split(x)[0])[1]), name='GSI', dtype=int).astype(int)
gsi_test = pd.Series(filepaths_test.apply(lambda x: os.path.split(os.path.split(x)[0])[1]), name='GSI', dtype=int).astype(int)

images_train = pd.concat([filepaths_train, gsi_train], axis=1).sample(frac=1.0, random_state=1).reset_index(drop=True)
images_test = pd.concat([filepaths_test, gsi_test], axis=1).sample(frac=1.0, random_state=1).reset_index(drop=True)


print(images_train)
print(images_test)

#---------------------------------------------------------------------------------

train_df = images_train.sample(400, random_state=1).reset_index(drop=True)

test_df = images_test.sample(80, random_state=1).reset_index(drop=True)

train_generator = tf.keras.preprocessing.image.ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2
)

test_generator = tf.keras.preprocessing.image.ImageDataGenerator(
    rescale=1./255
)

train_images = train_generator.flow_from_dataframe(
    dataframe=train_df,
    x_col='Filepath',
    y_col='GSI',
    target_size=(400, 400),
    color_mode='rgb',
    class_mode='raw',
    batch_size=40,
    shuffle=True,
    seed=42,
    subset='training'
)

val_images = train_generator.flow_from_dataframe(
    dataframe=train_df,
    x_col='Filepath',
    y_col='GSI',
    target_size=(400, 400),
    color_mode='rgb',
    class_mode='raw',
    batch_size=40,
    shuffle=True,
    seed=42,
    subset='validation'
)

test_images = test_generator.flow_from_dataframe(
    dataframe=test_df,
    x_col='Filepath',
    y_col='GSI',
    target_size=(400, 400),
    color_mode='rgb',
    class_mode='raw',
    batch_size=40,
    shuffle=False
)

#---------------------------------------------------------------------------------


inputs = tf.keras.Input(shape=(400, 400, 3))
x = tf.keras.layers.Conv2D(filters=64, kernel_size=(5, 5), activation='relu')(inputs)
x = tf.keras.layers.MaxPool2D()(x)
x = tf.keras.layers.Conv2D(filters=32, kernel_size=(5, 5), activation='relu')(x)
x = tf.keras.layers.MaxPool2D()(x)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dense(32, activation='relu')(x)
x = tf.keras.layers.Dense(16, activation='relu')(x)
outputs = tf.keras.layers.Dense(1, activation='linear')(x)

model = tf.keras.Model(inputs=inputs, outputs=outputs)

model.compile(
    optimizer='adam',
    loss='mse'
)

history = model.fit(
    train_images,
    validation_data=val_images,
    epochs=100,
    callbacks=[
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        )
    ]
)


#---------------------------------------------------------------------------------

predicted_gsi = np.squeeze(model.predict(test_images))
true_gsi = test_images.labels

r2 = r2_score(true_gsi, predicted_gsi)
print("Test R^2 Score: {:.5f}".format(r2))

print(predicted_gsi)
print(true_gsi)
