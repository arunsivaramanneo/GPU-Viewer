import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

HT = 36 # Height of the Tab

def AboutUs(tab4):

	frameAbout = ttk.LabelFrame(tab4)
	frameAbout.grid(column=0,row=0)

	TreeAbout = ttk.Treeview(frameAbout,height=HT)
	TreeAbout.heading('#0',text="GPU Viewer 1.0",anchor="center")
	TreeAbout.column('#0',width=775)
	TreeAbout.grid(column=0,row=0,sticky=tk.S)

	Aboutvsb = ttk.Scrollbar(frameAbout,orient="vertical",command=TreeAbout.yview)
	TreeAbout.configure(yscrollcommand=Aboutvsb.set)
	Aboutvsb.grid(column=0,row=0,sticky='nse')

	with open("LICENSE","r") as file1:
		i = 0
		for line in file1:
			TreeAbout.insert('','end',text=line,tags=i)
			if i % 2 != 0:
				TreeAbout.tag_configure(i,background="GRAY91")
			i = i + 1
