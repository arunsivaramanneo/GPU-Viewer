import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

HT = 35 # Height of the Tab

def AboutUs(tab4):

	frameAbout = ttk.LabelFrame(tab4)
	frameAbout.grid(column=0,row=0,padx=10)

	TreeAbout = ttk.Treeview(frameAbout,height=HT)
	TreeAbout.heading('#0',text="GPU Viewer 1.0",anchor="center")
	TreeAbout.column('#0',width=870)
	TreeAbout.grid(column=0,row=0,sticky=tk.NW)

	Aboutvsb = ttk.Scrollbar(frameAbout,orient="vertical",command=TreeAbout.yview)
	TreeAbout.configure(yscrollcommand=Aboutvsb.set)
	Aboutvsb.grid(column=0,row=0,sticky='nse')

	with open("../About GPU Viewer","r") as file1:
		i = 0
		for line in file1:
			TreeAbout.insert('','end',text=line,tags=i)
			if "github.com" in line:
				TreeAbout.tag_configure(i,foreground="BLUE")
			if "gmail.com" in line:
				TreeAbout.tag_configure(i,foreground="BLUE")
			if "paypal.me" in line:
				TreeAbout.tag_configure(i,foreground="BLUE")
			if i % 2 != 0 :
				TreeAbout.tag_configure(i,background="GRAY91")
			i = i + 1
