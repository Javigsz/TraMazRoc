import numpy as np
import cv2
import math

#Clase que calcula los resultados para un macizo rocoso
class Results_RM:
	def __init__(self, rockmass = None):


		#Macizo del que se van a obtener los resultados

		self.rockmass = rockmass


		#GSI calculado mediante tratamiento de imagenes con OpenCV

		self.gsi_1 = None


		#GSI calculado mediante red neuronal

		self.gsi_2 = None


		#average: media de distancias entre discontinuidades del macizo

		self.average = None


        #variance: varianza de distancias entre discontinuidades del macizo

		self.variance = None


        #average_area: media de distancias entre discontinuidades en el area mas desgastada del macizo

		self.average_area = None


        #variance_area: media de distancias entre discontinuidades en el area mas desgastada del macizo

		self.variance_area = None


    #Funcion middle_line
	#Extrae los puntos de una imagen correspondientes a una recta que pasa por el centro de la imagen y
	#que tiene una pendiente determinada
	#param height: altura de la imagen (pixeles)
	#param width: anchura de la imagen (pixeles)
	#param slope: pendiente de la linea
	#return vector_image: vector con los puntos de la imagen calculados    

	def middle_line(self, height,width,slope):

		line_image = np.full((height, width, 3),255, dtype = np.uint8)

		#Se calcula la recta con pendiente "slope" que pasa por el centro de la imagen

		#Estos puntos estan en los ejes de las imagenes para que la recta corte totalmente a la imagen

		#Se obtienen dos puntos de la imagen: (px,py), (qx,qy)

		#Punto central de la imagen: (x1,y1)

		x1,y1 = ( (0 + width) / 2, (0 + height) / 2 )

		b = y1 - (slope * x1)

		px = 0.0

		py = b

		lenAB = math.sqrt(math.pow(px - x1, 2.0) + math.pow(py - y1, 2.0))

		qx = int(x1 + (x1 - px) / lenAB * 500)

		qy = int(y1 + (y1 - py) / lenAB * 500)


		#Se traza la recta calculada sobre una imagen

		cv2.line(line_image, (int(px), int(py)), (int(qx), int(qy)), 0, 1)


		#Se obtienen los puntos de la imagen correspondientes a la recta trazada

		v1,v2 = np.where(np.all(line_image==[0], axis=2))

		vector_image = np.column_stack((v1,v2))

		return vector_image



	#Funcion process_RM
	#Realiza el procesamiento del macizo rocoso para obtener el GSI mediante OpenCV
	#param self: clase results_RM
	#param threshold1: umbral para deteccion de bordes
	#param threshold2: umbral para deteccion de bordes
	#param funct_size: distancia de aproximacion de las curvas (contornos) a discontinuidades (rectas)
	#param dis_color: color para las discontinuidades de grupo predominante
	#param dis_size: tamaño del borde de las discontinuidades
	
	def process_RM(self, threshold1, threshold2, funct_size, dis_color, dis_size):

		#0 - Asignar los valores introducidos por el usuario

		if(dis_color=="Azul"):

			main_color = 255,0,0

		if(dis_color=="Verde"):

			main_color = 0,255,0

		if(dis_color=="Rojo"):

			main_color = 0,0,255

		if(dis_size=="Pequeño"):

			thickness = 1

		if(dis_size=="Mediano"):

			thickness = 2

		if(dis_size=="Grande"):

			thickness = 3

		#1 - Detectar todas las discontinuidades de la image

		self.rockmass.find_disconts(threshold1,threshold2,funct_size)


		#2 - Separar las discontinuidades en grupos dependiendo de su pendiente

		color = self.rockmass.calculate_slopes(0.05,0,thickness)


		#3 - Encontrar la discontinuidad mas predominante en la imagen

		main_slope = self.rockmass.find_main_slope(main_color,thickness)


		#4 - Extraer la zona de la imagen con mas discontinuidades de pendiente predominante

		self.rockmass.find_area(0.2)


		#5 - Extraer una linea de la imagen que se recorrera para calcular las distancias entre discontinuidades

			#5.1- Linea de la zona con mas discontinuidades de la imagen

		line_image = self.middle_line(self.rockmass.important_area.shape[0],self.rockmass.important_area.shape[1],-(1/main_slope[1]))

			#5.2 - Linea de la imagen completa

		line_image_2 = self.middle_line(self.rockmass.img.shape[0],self.rockmass.img.shape[1],-(1/main_slope[1]))


		#6 - Obtener el coeficiente que relaciona la distancia real con los pixeles en la imagen

		self.rockmass.get_coeff()


		#7 - Calcular las distancias entre discontinuidades (media y varianza)

			#7.1 - De la imagen completa

		self.get_distances(line_image_2, main_color)

			#7.2 - De el area de la imagen con mas discontinuidades

		self.get_distances_area(line_image, main_color)


		#8 - Calcular el GSI

		self.calculate_gsi_1()



	def process_nn(self,rockmass):

		x = y



	#Funcion get_distances
	#Calcula la distancia entre discontinuidades en la imagen total de un macizo rocoso
	#param self: clase results_rm
	#param line_image: puntos de una recta que corta a la imagen a partir de la cual se calculan las distancias
	#param color: color del grupo de discontinuidades predominante
	def get_distances(self,line_image,color):

		#Control de errores

		if(self.rockmass.img_process.any() == None):

			return

		if(self.rockmass.coefficient == None):

			return


		#Se calculan las distancias entre discontinuidades

		d=0

		ant = None

		distances = np.zeros(len(self.rockmass.disconts), dtype = float)


		for i in range(0,line_image.shape[0]):

			x,y = line_image[i]

			#Si el punto de la recta toca con una discontinuidad

			if (np.all(self.rockmass.img_process[x][y] == color)):

				if(ant == None):

					#Es la primera discontinuidad que toca la recta

					ant = (x,y)

				else:

					#Se calcula la distancia en pixeles con la distontinuidad anterior

					distances[d] = math.dist((x,y), ant)

					d = d+1

					ant = (x,y)

		distances = distances[distances != 0]


		#Se comprueba que se han obtenido al menos dos distancias para obtener resultados

		if(len(distances) > 1):

			self.average = round(np.average(distances) * self.rockmass.coefficient,3)

			self.variance = round(np.var(distances) * self.rockmass.coefficient,3)

		else: 

			self.average = "Error"

			self.variance = "Error"



	#Funcion get_distances_area
	#Calcula la distancia entre discontinuidades en el area con mas discontinuidades de la imagen del macizo
	#param self: clase results_rm
	#param line_image: puntos de una recta que corta a la imagen a partir de la cual se calculan las distancias
	#param color: color del grupo de discontinuidades predominante
	def get_distances_area(self,line_image,color):


		#Control de errores

		if(self.rockmass.important_area.any() == None):

			return

		if(self.rockmass.coefficient == None):

			return


		d=0

		ant = None


		#Vector con el numero maximo de distancias

		distances = np.zeros(len(self.rockmass.disconts), dtype = float)


		#Se calculan las distancias entre discontinuidades

		for i in range (0,line_image.shape[0]):

			x,y = line_image[i]

			if(np.all(self.rockmass.important_area[x][y] == color)):

				if(ant == None):
					ant = (x,y)

				else:

					distances[d] = math.dist((x,y), ant)
					d = d+1
					ant = (x,y)


		distances = distances[distances != 0]


		#Se comprueba que se han obtenido al menos dos distancias para obtener resultados

		if(len(distances) > 1):

			self.average_area = round(np.average(distances) * self.rockmass.coefficient,3)

			self.variance_area = round(np.var(distances) * self.rockmass.coefficient,3)

		else: 

			self.average_area = "Error"
			
			self.variance_area = "Error"


	#Funcion get_average
	#Devuelve la media de las distancias entre discontinuidades en la imagen total

	def get_average(self):

		if(self.average == None):

			return

		else:

			return self.average


	#Funcion get_average_area
	#Devuelve la media de las distancias entre discontinuidades en el area de la imagen con mas discontinuidades

	def get_average_area(self):

		if(self.average_area == None):

			return

		else:

			return self.average_area


	#Funcion get_variance
	#Devuelve la varianza de las distancias entre discontinuidades en la imagen total

	def get_variance(self):

		if(self.variance == None):

			return

		else:

			return self.variance


	#Funcion get_variance_area
	#Devuelve la varianza de las distancias entre discontinuidades en el area de la imagen con mas discontinuidades

	def get_variance_area(self):

		if(self.variance_area == None):

			return

		else:

			return self.variance_area


	#Funcion calculate_gesi_1
	#Calcula el GSI a partir de la media de las distancias del area con mas discontinuidades en la imagen

	def calculate_gsi_1(self):

		if(self.average_area == "Error"):

			return

		self.gsi_1 = round((2.8009 * self.average_area) + 14.278)


	#Funcion get_gesi_1
	#Devuelve el GSI calculado a partir de la media de las distancias del area con mas discontinuidades en la imagen

	def get_gsi_1(self):

		return self.gsi_1


	#Funcion get_gesi_2
	#Devuelve el GSI calculado a partir de la red neuronal

	def get_gsi_2(self):

		return self.gsi_2

	
