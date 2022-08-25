#main_application.py

from tkinter import filedialog
from PIL import Image
from PIL import ImageTk
import tkinter.messagebox
import customtkinter
import cv2
import imutils
import numpy as np
import argparse
import random as rng

from interface import popout
from rockmass import rockmass
from rockmass import results

#Parametros de color de la interfaz

customtkinter.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"

customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

#Clase MainApplication
#Representa la ventana principal de la aplicacion

class MainApplication(tkinter.Tk):

    def __init__(self, rockmass, *args, **kwargs):

        super().__init__()

        #Macizo rocoso cuyos valores seran asignados tras la introduccion de los datos por parte del usuario

        #- rockmass

        #Icono de la aplicacion

        ico = Image.open('tramazroc/interface/icon.png')

        photo = ImageTk.PhotoImage(ico)

        self.wm_iconphoto(False, photo)       


        #Titulo y parametros de la ventana principal

        self.title("Tratamiento macizos rocosos")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # Llamada a "on_closing" cuando se cierra la ventana

        self.resizable(False, False)


        # ============ Se crean tres "frames" ============

        #Frame de la izquierda

        self.frame_left = customtkinter.CTkFrame(master=self, highlightbackground="black", highlightthickness=2)


        #Frame de la derecha

        self.frame_right = customtkinter.CTkFrame(master=self, highlightbackground="black", highlightthickness=2)


        #Frame del centro

        self.frame_center = customtkinter.CTkFrame(master=self, highlightbackground="black", highlightthickness=2)


        # ============ Objetos del Frame izquierdo ============

        #Etiqueta "Datos de Entrada"

        self.label_1 = customtkinter.CTkLabel(master=self.frame_left,
                                              text="Datos de entrada",
                                              text_font=("Roboto Medium", -20))  


        #Etiqueta "Imagen de entrada"

        self.label_2 = customtkinter.CTkLabel(master=self.frame_left,
                                              text="Imagen de entrada",
                                              text_font=("Roboto Medium", -12))  


        #Boton "Elegir imagen"

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Elegir imagen",
                                                command= lambda : self.choose_image(rockmass))


        #Etiqueta con la imagen de entrada

        self.lblInputImage = customtkinter.CTkLabel(master=self.frame_left, text="")


        #Etiqueta "Escala"

        self.label_3 = customtkinter.CTkLabel(master=self.frame_left,
                                              text="Escala (cuánto abarca la imagen)",
                                              text_font=("Roboto Medium", -12))


        #Etiqueta "Atura"

        self.label_4 = customtkinter.CTkLabel(master=self.frame_left,
                                              text="Altura (cm)",
                                              text_font=("Roboto Medium", -12))


        #Etiqueta "Anchura"

        self.label_5 = customtkinter.CTkLabel(master=self.frame_left,
                                              text="Anchura (cm)",
                                              text_font=("Roboto Medium", -12))


        #Entrada de texto para la Altura

        self.entry_1 = customtkinter.CTkEntry(master=self.frame_left,
                                              width=50)


        #Entrada de texto para la Anchura

        self.entry_2 = customtkinter.CTkEntry(master=self.frame_left,
                                              width=50)


        #Boton "Procesar"

        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Procesar",
                                                command = lambda : self.detect_scale(rockmass))


        #Boton "Mas informacion"

        self.button_3 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Más información",
                                                command = self.moreinfo)


        #Etiquetas "cm"

        self.label_cm_1 = customtkinter.CTkLabel(master=self.frame_left,
                                              text="cm",
                                              text_font=("Roboto Medium", -12))

        self.label_cm_2 = customtkinter.CTkLabel(master=self.frame_left,
                                              text="cm",
                                              text_font=("Roboto Medium", -12))



        #Etiqueta "Caracteristicas de las discontinuidades"

        self.labelscale1 = customtkinter.CTkLabel(self.frame_left,
                                              text="Caracteristicas de las discontinuidades:",
                                              text_font=("Roboto Medium", -12))


        #Caja para seleccionar color de discontinuidades

        self.combobox_1 = customtkinter.CTkComboBox(master=self.frame_left,
                                                    values=["Verde", "Azul", "Rojo"])

        #Valor por defecto

        self.combobox_1.set("Verde")


        #Caja para seleccionar grosor de discontinuidades

        self.combobox_2 = customtkinter.CTkComboBox(master=self.frame_left,
                                                    values=["Pequeño", "Mediano", "Grande"])

        #Valor por defecto

        self.combobox_2.set("Pequeño")


        # ============ Objetos del "frame" central ============

        #Etiqueta "Imagen de salida"

        self.label_6 = customtkinter.CTkLabel(master=self.frame_center,
                                              text="Imagen de salida",
                                              text_font=("Roboto Medium", -20))


        #Etiqueta con la imagen de salida

        self.lblOutputImage = customtkinter.CTkLabel(master=self.frame_center)



        # ============ Objetos del "Frame" Derecho ============


        #Etiqueta "Datos de salida"

        self.label_7 = customtkinter.CTkLabel(master=self.frame_right,
                                              text="Datos de salida",
                                              text_font=("Roboto Medium", -20)) 


        #Etiqueta "Area procesada"

        self.label_8 = customtkinter.CTkLabel(master=self.frame_right,
                                              text="Área procesada",
                                              text_font=("Roboto Medium", -12))


        #Etiqueta con la imagen del area procesada

        self.lblAreaImage = customtkinter.CTkLabel(master=self.frame_right, text="")



        self.label_9 = customtkinter.CTkLabel(master=self.frame_right,
                                              text_font=("Roboto Medium", -18))

        self.label_10 = customtkinter.CTkLabel(master=self.frame_right,
                                              text_font=("Roboto Medium", -18))

        self.label_11 = customtkinter.CTkLabel(master=self.frame_right,
                                              text_font=("Roboto Medium", -12))

        self.label_12 = customtkinter.CTkLabel(master=self.frame_right,
                                              text_font=("Roboto Medium", -12))

        #Boton "Descargar Imagen"

        self.button_4 = customtkinter.CTkButton(master=self.frame_right,
                                                text="Descargar imagen",
                                                command = lambda : self.download_image(rockmass))


        self.button_5 = customtkinter.CTkButton(master=self.frame_right,
                                                text="Salir",
                                                command = lambda : self.on_closing())


        # ================  Se colocan los objetos en el marco inicial del programa ===================

        self.frame_left.grid(row=0, column=0, sticky="nswe")

        self.label_1.grid(row=0, column=0, columnspan = 3, pady=10 )

        self.label_2.grid(row=1, column=0, columnspan = 3)

        self.button_1.grid(row=2, column=0, columnspan = 3)

        self.lblInputImage.grid(row=3, column=0, columnspan = 3, pady=10)

        self.label_3.grid(row=4, column=0, columnspan = 3, padx = 50)

        self.label_4.grid(row=5, column=0)

        self.label_5.grid(row=6, column=0)

        self.entry_1.grid(row=5, column=1)

        self.entry_2.grid(row=6, column=1)

        self.button_2.grid(row=10, column=0, columnspan = 3, pady=(40,10))

        self.button_3.grid(row=11, column=0, columnspan = 3, pady=(5,50))



    #Funcion que se ejecuta al pulsar el boton "Mas informacion"
    #Crea una ventana con mas informacion e instrucciones del programa

    def moreinfo(self):

        message = 'Aplicación de tratamiento de macizos rocosos.\n\n Instrucciones:'\
        '\n - Sube una imagen de un macizo rocoso. \n- Escribe una escala valida (entre 50 y 1000 cm)'\
        '\n- Presiona el boton Procesar.'\
        '\n- La imagen deberá tener una calidad decente y un \n tamaño superior a 800x800 para un funcionamiento\n correcto del programa.\n'

        popout.PopOut(self,message)



    #Funcion que asigna imagen al macizo rocoso que se procesara

    def choose_image(self, rockmass):

        #Formato de imagenes por defecto aunque existen mas compatibles

        path_image = filedialog.askopenfilename(filetypes = [
            ("image", ".jpeg"),
            ("image", ".png"),
            ("image", ".JPG"),
            ("image", ".jpg")])

        if len(path_image) > 0:
            
            #Se lee la imagen y se redimensiona

            image = cv2.imread(path_image)

            rockmass.img = image

            image= imutils.resize(image, height=380)

            imageToShow= imutils.resize(image, width=180)


            #Proceso para hacer visible a la imagen desde la interfaz

            imageToShow = cv2.cvtColor(imageToShow, cv2.COLOR_BGR2RGB)

            im = Image.fromarray(imageToShow)

            img = ImageTk.PhotoImage(image=im)

            self.lblInputImage.configure(image=img)

            self.lblInputImage.image = img       


            #Se vacia la imagen de salida cada vez que se lee una nueva imagen de entrada

            self.lblOutputImage.image = ""     


    #Funcion que se ejecuta cuando se pulsa el boton "Procesar"
    #Funcion que comprueba si los valores de entrada son correctos
    #Si es asi, inicia el procesamiento del macizo y la obtencion de los resultados

    def detect_scale(self, rockmass):

        text = self.entry_1.get()

        text2 = self.entry_2.get()

        image = rockmass.img

        if rockmass.img is None:

            #Si no existe imagen, se le comunica al usuario en una nueva ventana

            popout.PopOut(self, "Introduce una imagen valida")
            
        else:

            if (text and self.has_numbers(text)) or (text2 and self.has_numbers(text2)):

                #Si existe imagen y la escala es correcta

                #Se vacia la imagen anterior en caso de que se haya introducido otra imagen distinta

                rockmass.img_final = None

                #Se asignan los valores de escala al macizo

                if(text):

                    rockmass.scale[0] = text

                else:

                    rockmass.scale[0] = 0

                if(text2):

                    rockmass.scale[1] = text2

                else:

                    rockmass.scale[1] = 0


                results1 = results.Results_RM(rockmass)

                #con los parametros inicializados, se calculan los resultados

                results1.process_RM(50, 100, 20, self.combobox_1.get(), self.combobox_2.get())


                #Se visualiza la imagen final en el "Frame" central

                self.frame_center.grid(row=0, column=1, sticky="nswe")

                imageToShow = cv2.cvtColor(rockmass.img_final, cv2.COLOR_BGR2RGB)

                if(imageToShow.shape[0]>700):

                    imageToShow = imutils.resize(imageToShow, height=700)

                if(imageToShow.shape[1]>900):

                    imageToShow = imutils.resize(imageToShow, width=900)

                im = Image.fromarray(imageToShow)

                img = ImageTk.PhotoImage(image=im)

                self.lblOutputImage.configure(image=img)

                self.lblOutputImage.imageToShow = img

                self.lblOutputImage.grid(row=1, column=0)
                              
                self.label_6.grid(row=0, column=0, pady=10, padx=10)

                self.eval('tk::PlaceWindow . center')


                #Se colocan mas elementos con opciones en el Frame de la izquierda

                self.combobox_1.grid(row=8,column=0,padx=(70,0),pady=(10,20))

                self.combobox_2.grid(row=9,column=0,padx=(70,0),pady=(0,20))

                self.labelscale1.grid(row=7,column=0, padx=(43,0), pady=(30,0))


                #Se coloca el marco de la derecha con la imagen del area procesada de la imagen total

                self.frame_right.grid(row=0, column=2, sticky="nswe")

                imageToShow2 = cv2.cvtColor(rockmass.important_area, cv2.COLOR_BGR2RGB)

                if(imageToShow2.shape[0]>180):

                    imageToShow2 = imutils.resize(imageToShow2, height=380)

                if(imageToShow2.shape[1]>150):

                    imageToShow2 = imutils.resize(imageToShow2, width=180)

                im2 = Image.fromarray(imageToShow2)

                img2 = ImageTk.PhotoImage(image=im2)

                self.lblAreaImage.configure(image=img2)

                self.lblAreaImage.imageToShow2 = img2


                #Si con la imagen introducida no se han podido obtener resultados, se le notifica al usuario.

                if(results1.get_average_area() == "Error" or results1.get_gsi_1() < 0 or results1.get_gsi_1() > 100):

                    if(results1.get_average_area() == "Error"):

                        popout.PopOut(self, "No se han detectado suficientes discontinuidades para calcular distancias. Asegúrate de: \n - Elegir una imagen mas grande \n - Escoger una imagen de mayor calidad")

                    else:

                        if(results1.get_gsi_1() < 0 or results1.get_gsi_1() > 100):

                            popout.PopOut(self, "La escala introducida  es demasiado grande o pequeña y se han obtenido resultados falsos. Asegúrate de: \n - Comprobar que los datos introducidos son correctos")


                    self.frame_right.grid_forget()

                    self.frame_center.grid_forget()

                    self.combobox_1.grid_forget()

                    self.combobox_2.grid_forget()

                    self.labelscale1.grid_forget()

                    self.eval('tk::PlaceWindow . center')

                else:

                    #Se colocan los resultados en el frame Derecho

                    mytext_1= f"GSI: {results1.get_gsi_1()} "

                    if(0 < results1.get_gsi_1() <= 20):

                        mytext_2 = "Calidad MUY MALA"

                    if(20 < results1.get_gsi_1() <= 40):

                        mytext_2 = "Calidad MALA"

                    if(40 < results1.get_gsi_1() <= 60):

                        mytext_2 = "Calidad REGULAR"

                    if(60 < results1.get_gsi_1() <= 80):

                        mytext_2 = "Calidad BUENA"

                    if(80 < results1.get_gsi_1() < 100):

                        mytext_2 = "Calidad MUY BUENA"

                    mytext_3= f"Resultados"
                    #mytext_4= f"Varianza total: {results1.get_variance()} cm"
                    self.label_9.configure(text = mytext_1)

                    self.label_10.configure(text = mytext_2)

                    self.label_11.configure(text = mytext_3)
                    #self.label_12.configure(text = mytext_4)

                    self.label_7.grid(column=0, row=0, pady=10, padx=10)

                    self.label_8.grid(column=0, row=1)

                    self.lblAreaImage.grid(column=0, row=2, pady=20, padx=20)

                    self.label_9.grid(column=0, row = 4)

                    self.label_10.grid(column=0, row = 5)

                    #self.label_11.grid(column=0, row = 3, pady=(30,10))
                    #self.label_12.grid(column=0, row = 6)

                    self.button_4.grid(column=0, row = 6, pady=(180,10))

                    self.button_5.grid(column=0, row = 7, pady=(5,0))


                #Se vacian los valores de escala

                text = 0

                text2 = 0

                mytext_2 = 0

                mytext_1 = 0

                self.label_11.grid(column=0, row = 3, pady = (30,10))
                
            else:

                #Si no existe escala o no es valida, se le notifica al usuario en una nueva ventana

                popout.PopOut(self, "Introduce una escala válida")



    #Funcion que se ejecuta cuando se cierra la ventana principal del programa

    def on_closing(self, event=0):

        self.destroy()



    #Funcion que se ejecuta cuando se pulsa el boton "Descargar imagen"
    #Guarda la imagen que se muestra al usuario a su equipo

    def download_image(self, rockmass):

        imageToDownload = cv2.cvtColor(rockmass.img_final, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(imageToDownload)

        file = filedialog.asksaveasfile(mode='wb', defaultextension=".png", filetypes=(("PNG file", "*.png"),("All Files", "*.*") ))
        

        if file:
            image.save(file)



    #Funcion has_numbers
    #Comprueba si los caracteres de una cadena son todos numeros positivos
    #param inputString: cadena de caracteres
    #return true/false

    def has_numbers(self, inputString):

        return all(char.isdigit() for char in inputString)
