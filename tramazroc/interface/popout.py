from PIL import Image
from PIL import ImageTk
import tkinter.messagebox
import customtkinter

#Clase PopOut
#Clase que representa la ventana de la interfaz que sirve de ayuda al usuario
class PopOut(tkinter.Toplevel):
    def __init__(self, master, message, **kwargs):
        super().__init__()
        
        self.title("Ayuda")                                                                 #titulo de la ventana
        master.eval(f'tk::PlaceWindow {str(self)} center')

        self.message = message                                                              #mensaje de ayuda

        self.lblerror = customtkinter.CTkLabel(self, text=self.message).pack()                            #etiqueta con el mensaje

        self.btnerror1 = customtkinter.CTkButton(self, text="Cerrar", command=self.close).pack()          #boton para cerrar la ventana

        self.lblerror2 = customtkinter.CTkLabel(self, text="Cierra esta ventana para continuar").pack()   #etiqueta "para continuar"

        #Deshabilita la ventana principal para que el usuario se fije en esta ventana de ayuda
        self.master.withdraw()

        #Captura cuando se cierra la ventana
        self.protocol("WM_DELETE_WINDOW", self.close)

    #Funcion que se ejecuta cuando se cierra esta ventana
    def close(self, event=None):

        #Rehabilita la ventana principal
        self.master.deiconify()

        self.destroy()
