import tkinter as tk
import itertools
from tkinter import ttk 
from tkinter import scrolledtext
import subprocess
import os

def Vulkan(tab2):

	
	# Creating Tabs for different Features

	#Creating Feature Tab
	os.system("vulkaninfo > vulkaninfo.txt")

	tabcontrol = ttk.Notebook(tab2, padding=10)
	#tabcontrol.enable_traversal()
	
	# Creating the Features Tab

	FeatureTab = ttk.Frame(tabcontrol)
	tabcontrol.add(FeatureTab, text="Features")
	tabcontrol.grid(column=0,row=1,padx=10)

 	#Creating Limits Tab

	LimitsTab = ttk.Frame(tabcontrol)
	tabcontrol.add(LimitsTab,text = "Limits")
	tabcontrol.grid(column=0,row=1)

	# creating the Extensions Tab

	ExtensionsTab = ttk.Frame(tabcontrol)
	tabcontrol.add(ExtensionsTab,text = "Extensions")
	tabcontrol.grid(column=0,row=1)

	# Creating the Formats tab

	FormatTab = ttk.Frame(tabcontrol)
	tabcontrol.add(FormatTab,text= "Formats")
	tabcontrol.grid(column=0,row=1)

	radvar = tk.IntVar()

	def logo():
		pass

	def Features():

		#frame2 = ttk.LabelFrame(FeatureTab, text="Device Features")
		#frame2.grid(column=0,row=1)

		#FS = scrolledtext.ScrolledText(frame2, width=100,height=30,bg="LIGHT GRAY")
		#FS.grid(column=0,row=1)

		TreeFeatures = ttk.Treeview(FeatureTab,height=30)
		TreeFeatures['columns'] =('value')
		TreeFeatures.heading("#0", text='Device Features')
		TreeFeatures.column('#0',width=620)
		TreeFeatures.heading('value',text="Value")
		TreeFeatures.column('value',width=100)

		TreeFeatures.grid(column=0,row=0)


		GPU = radvar.get()
		if GPU == 0 :
			os.system("cat vulkaninfo.txt | awk '/GPU0/{flag=1;next}/Format Properties:/{flag=0}flag' | awk '/VkPhysicalDeviceFeatures:/{flag=1; next}/Format Properties:/{flag=0}flag' | awk '/==/{flag=1 ; next} flag' | grep = | sort > VKDFeatures1.txt")
			os.system("cat VKDFeatures1.txt | awk '{gsub(/= 1/,'True');print}' | awk '{gsub(/= 0/,'False');print}' > VKDFeatures.txt")
			os.system("cat VKDFeatures1.txt | grep -o '= [1,0]' > VKDFeatures2.txt")
			
		elif GPU == 1 :
			os.system("cat vulkaninfo.txt | awk '/GPU1/{flag=1;next}/Format Properties:/{flag=0}flag' | awk '/VkPhysicalDeviceFeatures:/{flag=1; next}/Format Properties:/{flag=0}flag' | awk '/==/{flag=1 ; next} flag' | grep = |sort > VKDFeatures1.txt")
			os.system("cat VKDFeatures1.txt | awk '{gsub(/= 1/,'True');print}' | awk '{gsub(/= 0/,'False');print}' > VKDFeatures.txt")
			os.system("cat VKDFeatures1.txt | grep -o '= [1,0]' > VKDFeatures2.txt")
		
		with open("VKDFeatures2.txt","r") as file1:
			value = []
			for line in file1:
				if line == '= 1\n':
					value.append("true")
				else:
					value.append("false")
			
		with open("VKDFeatures.txt","r") as file1:
			file1.seek(0,0)
			i = 0
			for line in file1:
				TreeFeatures.insert('','end',text=line,values=(value[i]))
				i = i + 1
		
		os.system("rm VKDFeatures*.txt")	

	
	def Limits():
		
		frame3 = ttk.LabelFrame(LimitsTab, text="Device Limits")
		frame3.grid(column=0,row=0)


		TreeLimits = ttk.Treeview(LimitsTab,height = 30)
		TreeLimits['columns'] = ('value')
		TreeLimits.heading("#0", text='Device Limits')
		TreeLimits.column('#0',width=520)
		TreeLimits.heading('value',text="Limits")
		TreeLimits.column('value',width=200)

		TreeLimits.grid(column=0,row=0,sticky=tk.W)

		#DL = scrolledtext.ScrolledText(frame3,width=100,height=40,bg="LIGHT GRAY")
		#DL.grid(column=0,row=1)
		GPU = radvar.get()
		if GPU == 0 :
			os.system("cat vulkaninfo.txt | awk '/GPU0/{flag=1;next}/VkPhysicalDeviceSparseProperties:/{flag=0}flag'| awk '/--/{flag=1 ; next} flag' | sort > VKDlimits1.txt")
			os.system("cat VKDlimits1.txt | awk '{gsub(/=.*/,'True');}1' > VKDlimits.txt")
			os.system("cat VKDlimits1.txt | grep -o '=.*' | grep -o '[ -].*' > limits.txt")
		elif GPU == 1 :
			os.system("cat vulkaninfo.txt | awk '/GPU1/{flag=1;next}/VkPhysicalDeviceSparseProperties:/{flag=0}flag'| awk '/--/{flag=1 ; next} flag' | sort > VKDlimits1.txt")
			os.system("cat VKDlimits1.txt | awk '{gsub(/=.*/,'True');}1' > VKDlimits.txt")
			os.system("cat VKDlimits1.txt | grep -o '=.*' | grep -o '[ -].*' > limits.txt")

		with open("limits.txt","r") as file1:
			value = []
			for line in file1:
					value.append(line)

		with open("VKDlimits.txt","r") as file1:
			count = len(file1.readlines())
			i = 0
			print(count)
			file1.seek(0,0)
			for line in file1:
				TreeLimits.insert('','end',text=line, values= value[i])
				i = i + 1

		#DL.configure(state='disabled',foreground="BLUE")
		os.system("rm *limits.txt")		

	def Extensions():


		#frame4 = ttk.LabelFrame(ExtensionsTab, text="Device Extension ")
		#frame4.grid(column=0,row=0)

		te = ttk.Treeview(ExtensionsTab, height=30)
		te.heading("#0", text='Name')
		te.column('#0',width=522)
		te['column'] = ('version')
		te.grid(column=0,row=0)
		te.heading('version',text="Version")
		te.column('version',width=200)

		#ES = scrolledtext.ScrolledText(frame4,width=100,height=30,bg="LIGHT GRAY")
		#ES.grid(column=0,row=1)
		GPU = radvar.get()
		
		if GPU == 0 :
			os.system("cat vulkaninfo.txt | awk '/GPU0/{flag=1;next}/VkQueueFamilyProperties/{flag=0}flag'|awk '/Device Extensions/{flag=1; next}/VkQueueFamilyProperties/{flag=0} flag' | grep VK_ | sort > VKDExtensions1.txt")
			os.system("cat VKDExtensions1.txt | awk '{gsub(/:.*/,'True');print} ' > VKDExtensions.txt")
			os.system("cat VKDExtensions1.txt | grep -o ':.*' > version.txt")
		elif GPU == 1 :
			os.system("cat vulkaninfo.txt | awk '/GPU1/{flag=1;next}/VkQueueFamilyProperties/{flag=0}flag'|awk '/Device Extensions/{flag=1; next}/VkQueueFamilyProperties/{flag=0} flag'| grep VK_ |sort > VKDExtensions1.txt")
			os.system("cat VKDExtensions1.txt | awk '{gsub(/:.*/,'True');print} ' > VKDExtensions.txt")
			os.system("cat VKDExtensions1.txt | grep -o ':.*' > version.txt")

		with open("version.txt","r") as file1:
			value = []
			for line in file1:
				if line == ': extension revision  1\n':
					value.append("0.0.1")
				else:
					value.append("0.0.68")


		with open("VKDExtensions.txt","r") as file1:
			count = len(file1.readlines())
			#frame4.configure(text = count)
			tabcontrol.tab(2,text="Extensions(%d)"%count)
			file1.seek(0,0)
			i = 0
			for line in file1:
				te.insert('','end',text=line,values=(value[i]))
				i = i + 1


		#ES.configure(state='disabled',foreground="BLUE")
		os.system("rm VKDExtensions.txt")


	def Format():
		#frame5 = ttk.LabelFrame(FormatTab, text="Formats ")
		#frame5.grid(column=0,row=0)

		tf = ttk.Treeview(FormatTab, height=30)
		tf['columns'] = ("linear","optimal","Buffer")
		tf.heading("#0", text='Format')
		tf.column('#0',width=500)
		tf.heading("linear",text="linear")
		tf.column("linear",width=75)
		tf.heading("optimal",text="optimal")
		tf.column("optimal",width=75)
		tf.heading("Buffer",text= "Buffer")
		tf.column("Buffer",width=75)
		tf.grid(column=0,row=0)
		tf.xview()
		tf.yview()

		GPU = radvar.get()
		if GPU == 0 :
			os.system("cat vulkaninfo.txt | awk '/GPU0/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | grep ^FORMAT_ | grep -v _UNKNOWN_  > VKDFORMATS.txt")
		elif GPU == 1 :
			os.system("cat vulkaninfo.txt | awk '/GPU1/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | grep ^FORMAT_ | grep -v _UNKNOWN_ > VKDFORMATS.txt")



		with open("VKDFORMATS.txt","r") as file1:
			count = len(file1.readlines())
			print(count)
			file1.seek(0,0)
			for line in file1:
				tf.insert('','end',text=line)
			

				
		os.system("rm VKDFORMATS*.txt")

	def radcall():
		radsel= radvar.get()
		if radsel == 0:
			Features()
			Limits()
			Extensions()
			Format()
		if radsel == 1:
			Features()
			Limits()
			Extensions()
			Format()


	frame1 = ttk.LabelFrame(tab2,text="")
	frame1.grid(column=0,row=0)
	os.system("cat vulkaninfo.txt | grep Name | grep -o  =.* | grep -o ' .*' > GPU.txt")

	with open("GPU.txt","r") as file2:
		count=len(file2.readlines())
		list = []
		file2.seek(0,0)
		for line in file2:
			list.append(line)

	DS = ttk.Label(frame1, text="Available Device(s) :")
	DS.grid(column=0,row=0, padx=100, pady=10)
	
	for i in range(len(list)):
		GPU = tk.Radiobutton(frame1,text=list[i], variable=radvar,value=i,command=radcall)
		GPU.grid(column=1,row=i,sticky=tk.W)
		if i == 0:
			GPU.invoke()

	os.system("rm GPU.txt")
	



	

