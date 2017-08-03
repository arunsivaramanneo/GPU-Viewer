import tkinter as tk
from tkinter import ttk 
from tkinter import scrolledtext
import subprocess
import os


def Features(tab2):

	tabcontrol = ttk.Notebook(tab2, padding=10)
	FeatureTab = ttk.Frame(tabcontrol)
	tabcontrol.add(FeatureTab, text="Features")
	tabcontrol.pack(expand=1, fill="both")

	FS = scrolledtext.ScrolledText(FeatureTab, width="100",height=40)
	FS.grid(column=0,row=0)

	#os.system("vulkaninfo | awk '/VkPhysicalDeviceFeatures:/{flag=1; next}/Format Properties:/{flag=0} flag' > Features.txt")

	with open("Features.txt","r") as file1:
		for line in file1:
			FS.insert('insert',line)

def Vulkan(tab2):
	
	#Determining the number of GPU's

	os.system("vulkaninfo | grep '^GPU id' | grep GPU > GPU.txt")

	with open("GPU.txt","r") as file2:
		count=len(file2.readlines())
		print(count)
		list = []
		file2.seek(0,0)
		for line in file2:
			list.append(line)

	print(len(list))



	number = tk.StringVar()
	DS = ttk.Label(tab2, text="Select Device :")
	DS.grid(column=0,row=0,padx=50, pady=20)
	DCB = ttk.Combobox(tab2,width=30,textvariable=number,state='readonly')
	DCB['values'] = list
	DCB.grid(column=1,row=0)

