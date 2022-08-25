import tkinter

from interface import main_application
from rockmass import rockmass

def run():

	rockmass1 = rockmass.RockMass()
	 
	#Initializes the interface 
	app = main_application.MainApplication(rockmass1)
	app.eval('tk::PlaceWindow . center')
	app.title("Tratamiento Macizos Rocosos")

	app.mainloop()