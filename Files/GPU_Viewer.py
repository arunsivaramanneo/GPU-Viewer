import tkinter as tk
from tkinter import ttk 
import OpenGLViewer
from OpenGLViewer import OpenGL
from vulkanviewer import Vulkan
from About import AboutUs
#from DeviceInfo import Info

win = tk.Tk() 

# Title of the Window

win.title("GPU Viewer")

win.resizable(0,0)

style = ttk.Style()
try:
	style.theme_use("alt")
except Exception as e:
	raise e
finally:

	# Creating Tabs for OpenGL , Vulkan So on ...
	GLimg = tk.PhotoImage(file="../Images/OpenGL.png")
	img1 = GLimg.subsample(4,4)
	tabcontrol = ttk.Notebook(win, padding=10)

	#tab1 = ttk.Frame(tabcontrol)
	#tabcontrol.add(tab1,text=icon)
	#tabcontrol.grid(column=0,row=0)

	#Info(tab1)

	tab2 = ttk.Frame(tabcontrol)
	tabcontrol.add(tab2, image=img1)
	tabcontrol.grid(column=0,row=0)



	OpenGL(tab2)


	# Vulkan Tab

	VKimg = tk.PhotoImage(file="../Images/Vulkan.png")
	img2 = VKimg.subsample(4,4)
	tab3 = ttk.Frame(tabcontrol)
	tabcontrol.add(tab3, image=img2)
	tabcontrol.grid(column=0,row=0)

	Vulkan(tab3)

	# About Us tab

	Abtimg = tk.PhotoImage(file="../Images/about.png")
	img3 = Abtimg.subsample(3,6)
	tab4 = ttk.Frame(tabcontrol)
	tabcontrol.add(tab4,image=img3)
	tabcontrol.grid(column=0,row=0)

	AboutUs(tab4)

	win.mainloop()