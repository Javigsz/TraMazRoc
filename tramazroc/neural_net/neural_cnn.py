import numpy as np
import pandas as pd
from pathlib import Path
import os.path
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split

import tensorflow as tf

from sklearn.metrics import r2_score

#Clase neural_cnn

class neural_cnn:
    
        def __init__(self, train_path = None, test_path = None):

                #Carpeta con las imagenes de entrenamiento

                self.train_path = train_path

                #Carpeta con las imagenes de test

                self.test_path = test_path

                #Numero de imagenes de entrenamiento

                self.num_train = 400

                #Numero de imagenes de test

                self.num_test = 80

                #Porcentaje de conjunto de validacion

                self.val_percen = 0.2

                #Modelo de red neuronal entrenado

                self.model = None

        def train(self):

                #Obtencion del conjunto de datos de imagenes con su GSI

                image_dir_train = Path(self.train_path)
                
                image_dir_test = Path(self.test_path)


                filepaths_train = pd.Series(list(image_dir_train.glob(r'*/*.jpg')), name='Filepath', dtype=str).astype(str)
                
                filepaths_test = pd.Series(list(image_dir_test.glob(r'*/*.jpg')), name='Filepath', dtype=str).astype(str)


                gsi_train = pd.Series(filepaths_train.apply(lambda x: os.path.split(os.path.split(x)[0])[1]), name='GSI', dtype=int).astype(int)
                
                gsi_test = pd.Series(filepaths_test.apply(lambda x: os.path.split(os.path.split(x)[0])[1]), name='GSI', dtype=int).astype(int)


                images_train = pd.concat([filepaths_train, gsi_train], axis=1).sample(frac=1.0, random_state=1).reset_index(drop=True)
                
                images_test = pd.concat([filepaths_test, gsi_test], axis=1).sample(frac=1.0, random_state=1).reset_index(drop=True)


                #Creacion del conjunto de entrenamiento y de test

                train_df = images_train.sample(self.num_train, random_state=1).reset_index(drop=True)

                test_df = images_test.sample(self.num_test, random_state=1).reset_index(drop=True)
                
                train_generator = tf.keras.preprocessing.image.ImageDataGenerator(
                    rescale=1./255,
                    validation_split=self.val_percen
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

                #Creacion del modelo

                inputs = tf.keras.Input(shape=(400, 400, 3))
                x = tf.keras.layers.Conv2D(filters=64, kernel_size=(5, 5), activation='relu')(inputs)
                x = tf.keras.layers.MaxPool2D()(x)
                x = tf.keras.layers.Conv2D(filters=32, kernel_size=(5, 5), activation='relu')(x)
                x = tf.keras.layers.MaxPool2D()(x)
                x = tf.keras.layers.GlobalAveragePooling2D()(x)
                x = tf.keras.layers.Dense(32, activation='relu')(x)
                x = tf.keras.layers.Dense(16, activation='relu')(x)
                outputs = tf.keras.layers.Dense(1, activation='linear')(x)

                self.model = tf.keras.Model(inputs=inputs, outputs=outputs)

                self.model.compile(
                    optimizer='adam',
                    loss='mse'
                )

                #Entrenamiento del modelo

                history = self.model.fit(
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


                #Pruebas de rendimiento del modelo

                predicted_gsi = np.squeeze(self.model.predict(test_images))
                true_gsi = test_images.labels

                r2 = r2_score(true_gsi, predicted_gsi)
                print("Test R^2 Score: {:.5f}".format(r2))

                ypred = self.model.predict(test_images)

                mse = tf.keras.losses.MeanSquaredError()
 
                print("MSE: %.4f" % mse(test_df["GSI"], ypred))

                x_ax = range(len(ypred))
                plt.scatter(x_ax, test_df["GSI"], s=5, color="blue", label="original")
                plt.scatter(x_ax, ypred, s=5, color="red", label="predicted")
                plt.legend()
                plt.show()

                #Se guarda el modelo para no entrenar cada vez que se ejecuta este modulo

                self.model.save('saved_model/my_model')
                

        def predict(self,image):

                #Se carga el modelo guardado en otras ejecuciones

                new_model = tf.keras.models.load_model('saved_model/my_model')

                #Si no existe, se entrena el modelo

                if(new_model == None):

                        self.train()
                        
                        new_model = tf.keras.models.load_model('saved_model/my_model')

                new_model.summary()

                print(np.squeeze(new_model.predict(image)))
                

if __name__=="__main__":


        #Es necesario modificar las dos variables siguientes para indicar donde se han situado las imagenes de train y test
        
        test_path =""

        train_path =""

        net = neural_cnn(train_path,test_path)

        #Como el programa no usa la red para la clasificacion, se muestra a continuiacion un ejemplo
        #de como clasificar una imagen con el modelo ya creado anteriormente

        #net.train()

        #Es necesario modificar la variable siguientes para indicar donde se ha situado la imagenen
        
        img_path = ""
        img = tf.keras.utils.load_img(img_path, target_size=(400, 400))

        #Preprocesamiento de la imagen

        img_array = tf.keras.utils.img_to_array(img)
        img_batch = np.expand_dims(img_array, axis=0)

        img_preprocessed = img_batch

        img_preprocessed = img_preprocessed/255

        #Predict
        
        net.predict(img_preprocessed)

            
