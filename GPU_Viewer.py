import tkinter as tk
from tkinter import ttk 
import OpenGLViewer
from OpenGLViewer import OpenGL
from vulkanviewer import Vulkan
#from DeviceInfo import Info

win = tk.Tk() 

# Title of the Window

win.title("GPU Viewer")

win.resizable(0,0)


# Creating Tabs for OpenGL , Vulkan So on ...
GLimg = tk.PhotoImage(file="Images/opengl_logo.png")
img1 = GLimg.subsample(6,6)
tabcontrol = ttk.Notebook(win, padding=10)

#tab1 = ttk.Frame(tabcontrol)
#tabcontrol.add(tab1,text="Device Info.")
#tabcontrol.grid(column=0,row=0)

#Info(tab1)

tab2 = ttk.Frame(tabcontrol)
tabcontrol.add(tab2, image=img1)
tabcontrol.grid(column=0,row=0)



OpenGL(tab2)


VKimg = tk.PhotoImage(file="Images/Vulkan_logo.png")
img2 = VKimg.subsample(5,5)
tab3 = ttk.Frame(tabcontrol)
tabcontrol.add(tab3, image=img2)
tabcontrol.grid(column=0,row=0)

Vulkan(tab3)



win.mainloop()