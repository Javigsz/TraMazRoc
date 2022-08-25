import cv2
import numpy as np
from numpy import array, linspace
import argparse
import random as rng

#Clase que representa un macizo rocoso

class RockMass:

    def __init__(self, scale = 0, img = None):

        #scale: cuanto abarca la imagen en distancia real tanto horizontal como vertical (en cm)

        self.scale = np.zeros(2,dtype=float)  

        #img: imagen inicial sin procesar del macizo rocoso  

        self.img = img

        #discontinuidades detectadas en la imagen
        #cada distontinuidad esta representada por dos puntos, la recta que les une es la distontinuidad
        #fila ejemplo del vector: [x1] [y1] [x2] [y2]

        self.disconts = None


        #important_area: extracto de la imagen inicial que posee el mayor numero de discontinuidades    

        self.important_area = None


        #img_final: imagen con todas las discontinuidades para que se muestren al usuario

        self.img_final = None


        #img_process: imagen que se somete a distintos cambios a lo largo del procesamiento del programa

        self.img_process = None 


        #img_points: imagen donde cada discontinuidad se representa con un punto
        #sirve para detectar el area con el mayor numero de discontinuidades   

        self.img_points = None


        #pendientes de todas las discontinuidades
        #cada pendiente esta representada por la pendiente, el indice de la discontinuidad y el grupo al que pertenece
        #fila del vector: [pendiente] [indice en vector dictontinuidades] [grupo de pendientes]

        self.slopes = None        


        #numero de grupos distintos de discontinuidades basados en su pendiente

        self.num_groups = None


        #coeficiente de conversion de pixeles a cm

        self.coefficient = None


    #Funcion find_disconts
    #Detecta las discontinuidades de una imagen
    #param self: clase rockmass
    #param threshold1: umbral para detectar bordes en una imagen
    #param threshold2: umbral para detectar bordes en una imagen
    #param tam_approx: maxima distancia entre los bordes de la imagen (curvas) y las rectas aproximadas de estas curvas

    def find_disconts(self,threshold1,threshold2,tam_approx):

        #Control de errores

        if(self.img.any() == None):
            return


        #Preprocesamiento de imagen

        img_blur = cv2.GaussianBlur(self.img, (3,3), 0)


        #Deteccion de bordes y contornos en la imagen

        edges = cv2.Canny(img_blur, threshold1, threshold2)

        contours, hierarchy = cv2.findContours(edges, cv2.RETR_LIST,  cv2.CHAIN_APPROX_NONE)

        num_discounts = 0


        #Detectar cuantas discontinuidades existen en la imagen

        for i in range(len(contours)):
            
            approximations = cv2.approxPolyDP(contours[i], tam_approx, True)

            num_discounts = (len(approximations) - 1) + num_discounts



        #Vector de discontinuidades

        pre_lines = np.zeros(shape=(num_discounts,4),dtype=int)

        

        #Transformacion de bordes (curvas) a discontinuidades (rectas)

        l=0

        for i in range(len(contours)):
            
            approximations = cv2.approxPolyDP(contours[i], tam_approx, True)

            cont=1
            while(cont<len(approximations)):

                xx1 = int(approximations[cont-1][0][0])

                yy1 = int(approximations[cont-1][0][1])

                xx2 = int(approximations[cont][0][0])

                yy2 = int(approximations[cont][0][1])

                cont+=1

                pre_lines[l][0] = xx1

                pre_lines[l][1] = yy1

                pre_lines[l][2] = xx2

                pre_lines[l][3] = yy2

                l+=1



        #Almacenar las discontinuidades en un formato adecuado para funciones posteriores

        self.disconts = np.zeros(shape=(l+1,1,4),dtype=int)

        for i in range(0,l):

            self.disconts[i][0] = pre_lines[i]



	#Funcion calculate_slopes
    #Calcula las pendientes de las discontinuidades y las clasifica en grupos
    #param self: clase rockmass
    #param margin: margen de distancia entre grupos de discontinuidades
    #return color: vector con los colores de cada grupo de discontinuidades
    def calculate_slopes(self,margin,accum,thickness):

        #Control de errores

        if(self.disconts.any() == None):

            return


        #Se asignan las imagenes de procesamiento y final

        self.img_process = self.img.copy()

        self.img_final = self.img.copy()


        #Vector de pendientes y grupos de pendientes con tamaño maximo

        slopes = np.zeros(len(self.disconts))

        groups = np.zeros(len(self.disconts))


        #Se calcula la pendiente de cada discontinuidad

        j = 0

        for i in self.disconts:

            for x1,y1,x2,y2 in i:

                if(x1 == x2):

                    slopes[j] = 100

                else:

                    slopes[j] = (y2-y1)/(x2-x1)

                j = j+1



        #Se almacenan las discontinuidades en un array con su indice de discontinuidad y su grupo

        labels = np.arange(0, len(slopes), 1, dtype=int)

        self.slopes = np.column_stack((slopes, labels))

        self.slopes = self.slopes[np.argsort(self.slopes[:, 0])]

        self.slopes = np.column_stack((self.slopes, groups))

        g = -1

        index = 0


        #Se asigna a cada discontinuidad su grupo dependiendo de su pendiente

        for i,x,z in self.slopes:

            if g == -1:

                g = 0

                ant = i

                self.slopes[index][2] = g

            else: 

                dif = i - ant

                accum = accum + dif

                if dif < margin:

                    self.slopes[index][2] = g

                else:

                    g = g+1

                    self.slopes[index][2] = g

                dif = 0

                ant = i

            index = index + 1


        k=g+1
        color = np.zeros((k,3), dtype=object)

        self.num_groups = k


        #Se asigna un color a cada grupo de discontinuidad

        for i in range(0,k):
            color[i] = rng.randint(1,256), rng.randint(1,256), rng.randint(1,256)


        #Se pinta sobre las imagenes final y de procesamiento las lineas de las discontinuidades

        for j in range(0,len(self.disconts)):

            group = int(self.slopes[j][2])

            line = int(self.slopes[j][1])

            x1,y1,x2,y2 = self.disconts[line][0]

            cv2.line(self.img_process,(x1,y1),(x2,y2),color[group],1)

            cv2.line(self.img_final,(x1,y1),(x2,y2),color[group],thickness)

        return color

    

    #Funcion find_main_slope
    #Encuentra la pendiente mas predominante de la imagen
    #param self: clase rockmass
    #return line_slope_group, line_slope, num_dist_max: el grupo de discontinuidades predominantes, la media de dichas pendientes 
    #y el numero maximo de distancias entre discontinuidades

    def find_main_slope(self,main_color,thickness):

        #Grupo con mas discontinuidades

        line_slope_group = np.argmax(np.bincount(self.slopes[:,2].astype(int)))


        #Numero maximo de distancias

        num_dist_max = (np.count_nonzero(self.slopes[:,2] == line_slope_group)) -1


        #Vector con la media de las pendientes de las discontinuidades por grupo

        aver_slopes = np.zeros(num_dist_max+1, dtype = float)


        #Se crea la imagen con puntos que se usara para detectar el area con mas discontinuidades

        self.img_points = np.zeros((self.img.shape[0], self.img.shape[1], 3), dtype=np.uint8)


        #Se calcula la media de la pendiente de las discontinuidades del grupo predominante (grupo con mas discontinuidades)

        i = 0       

        for j in range(0,len(self.disconts)):

            group = int(self.slopes[j][2])

            if(group == line_slope_group):

                line = int(self.slopes[j][1])

                x1,y1,x2,y2 = self.disconts[line][0]
                
                aver_slopes[i] = self.slopes[j][0]

                i = i +1

                midx=int((x2+x1)/2)

                midy=int((y2+y1)/2)

                #Se pinta sobre la imagen de puntos cada punto correspondiente a cada discontinuidad del grupo predominante

                cv2.line(self.img_points,(midx,midy),(midx,midy),(255,255,255),50)

                #Se pinta sobre la imagen final y sobre la imagen de procesamiento el color que elige el usuario

                cv2.line(self.img_final,(x1,y1),(x2,y2),main_color,thickness)

                cv2.line(self.img_process,(x1,y1),(x2,y2),main_color,1)


        line_slope = np.average(aver_slopes)

        return line_slope_group, line_slope, num_dist_max



    #Funcion find_area
    #Encuentra el area de la imagen con mas discontinuidades
    #param self: clase rockmass
    #param percentage: porcentaje de la imagen inicial del macizo rocoso que se quiere extraer
    #return top_l, bot_r, top_r, bot_l: pixeles de la imagen inicial que corresponden a las esquinas de la imagen extraida
    def find_area(self,percentage):

        #Control de errores

        if(self.img_points.any() == None or self.img_final.any() == None):

            return


        drawing3 = cv2.cvtColor(self.img_points, cv2.COLOR_BGR2GRAY)

        #Metodo de coincidencia de plantilla:

            # TM_SQDIFF_NORMED (este ha dado buenos resultados)

            # TM_SQDIFF 

            # TM_CCORR 

            # TM_CCORR_NORMED

            # TM_CCOEFF 

            # TM_CCOEFF_NORMED 

        match_method = cv2.TM_SQDIFF_NORMED


        #Altura y anchura de la imagen que se extraera

        h = int(self.img_points.shape[0]*percentage)

        w = int(self.img_points.shape[1]*percentage)


        #Imagen que sirve como plantilla para encontrar el area con mas discontinuidades

        #Es una imagen con solo pixeles blancos

        array_created = np.full((h, w, 3),255, dtype = np.uint8)

        array_created = cv2.cvtColor(array_created, cv2.COLOR_BGR2GRAY)


        #Se detecta el area mas deteriorada comparando la imagen creada (toda blanca) con la imagen de puntos blancos

        result = cv2.matchTemplate(drawing3, array_created, match_method)

        _minVal, _maxVal, minLoc, maxLoc = cv2.minMaxLoc(result, None)

        if (match_method == cv2.TM_SQDIFF or match_method == cv2.TM_SQDIFF_NORMED):

            top_left = minLoc

        else:

            top_left = maxLoc


        #Se marca en la imagen final el area con mas discontinuidades

        bottom_right = (top_left[0] + w, top_left[1] + h)

        cv2.rectangle(self.img_final, top_left, bottom_right, (255,0,0), 2, 8, 0 )
        

        #Se recorta de la imagen de procesamiento el area con mas discontinuidades

        self.important_area = self.img_process[top_left[1]:top_left[1] + array_created.shape[0],top_left[0]:top_left[0] + array_created.shape[1]]


    #Funcion get_coeff
    #Encuentra el coeficiente que relaciona la distancia real con los pixeles de la imagen
    #param self: clase rockmass

    def get_coeff(self):

        #Si el usuario introduce altura y anchura real

        if(self.scale[0] != 0 and self.scale[1]!= 0):

            coef = np.zeros(2,dtype=float)

            coef[0] = self.scale[0]/self.img.shape[0]

            coef[1] = self.scale[1]/self.img.shape[1]

            coef = np.average(coef)

        else:

            #Si el usuario solo introduce anchura

            if(self.scale[0] != 0):

                coef = self.scale[0]/self.img.shape[0]

            else:

                #Si solo ha introducido altura

                coef = self.scale[1]/self.img.shape[1]

        self.coefficient = coef
