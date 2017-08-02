import tkinter as tk
import OpenGLViewer
from OpenGLViewer import OpenGL

win = tk.Tk() 


# Title of the Window

win.title("GPU Viewer 0.9")

win.resizable(0,0)

OpenGL(win)

win.mainloop()