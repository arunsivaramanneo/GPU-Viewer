import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

HT = 22 # Height of the Tab
HT2 = 10
COLOR1 = "GRAY91" # even number line background
COLOR2 = "BLUE" 
ANCHOR1 = "center"
WIDTH1 = 930

def AboutUs(tab4):

	frameAbout = ttk.LabelFrame(tab4,text="About GPU Viewer",padding=10)
	frameAbout.grid(column=0,row=0)

	TreeAbout = ttk.Treeview(frameAbout,height=HT)
	TreeAbout.heading('#0',text="GPU Viewer 1.0",anchor=ANCHOR1)
	TreeAbout.column('#0',width=WIDTH1)
	TreeAbout.grid(column=0,row=0)

	Aboutvsb = ttk.Scrollbar(frameAbout,orient="vertical",command=TreeAbout.yview)
	TreeAbout.configure(yscrollcommand=Aboutvsb.set)
	Aboutvsb.grid(column=0,row=0,sticky='nse')

	with open("../About GPU Viewer","r") as file1:
		i = 0
		for line in file1:
			TreeAbout.insert('','end',text=line,tags=i)
			if "github.com" in line:
				TreeAbout.tag_configure(i,foreground=COLOR2)
			if "gmail.com" in line:
				TreeAbout.tag_configure(i,foreground=COLOR2)
			if "paypal.me" in line:
				TreeAbout.tag_configure(i,foreground=COLOR2)
			if i % 2 != 0 :
				TreeAbout.tag_configure(i,background=COLOR1)
			i = i + 1

	frameChangeLog = ttk.LabelFrame(tab4,text="Change Log",padding=10)
	frameChangeLog.grid(column=0,row=1,pady=10)
	TreeChangeLog = ttk.Treeview(frameChangeLog,height=HT2)
	TreeChangeLog.heading('#0',text="Change Log",anchor=ANCHOR1)
	TreeChangeLog.column('#0',width=WIDTH1)
	TreeChangeLog.grid(column=0,row=1,sticky=tk.NW)

	Changelogvsb = ttk.Scrollbar(frameChangeLog,orient="vertical",command=TreeChangeLog.yview)
	TreeChangeLog.configure(yscrollcommand=Changelogvsb.set)
	Changelogvsb.grid(column=0,row=1,sticky='nse')

	with open("../Change Log","r") as file1:
		i = 0
		for line in file1:
			TreeChangeLog.insert('','end',text=line,tags=i)
			if i % 2 != 0:
				TreeChangeLog.tag_configure(i,background=COLOR1)
			i = i + 1
