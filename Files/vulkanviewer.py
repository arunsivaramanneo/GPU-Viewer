import tkinter as tk
from tkinter import ttk 
import os

HT = 32
HT2 = 16
COLOR1 = "GRAY91"
COLOR2 = "GREEN"
COLOR3 = "RED"
ANCHOR1 = "center"
WIDTH1 = 600
WIDTH2 = 250

def Vulkan(tab2):

	
	# Creating Tabs for different Features

	#Creating Feature Tab
	os.system("vulkaninfo > vulkaninfo.txt")

	tabcontrol = ttk.Notebook(tab2, padding=10)
	#tabcontrol.enable_traversal()
	
	# Creating the Features Tab

	DeviceTab = ttk.Frame(tabcontrol,padding=10)
	tabcontrol.add(DeviceTab,text="Device")
	tabcontrol.grid(column=0,row=1,padx=5)

	FeatureTab = ttk.Frame(tabcontrol)
	tabcontrol.add(FeatureTab, text="Features",padding=10)
	tabcontrol.grid(column=0,row=1)

 	#Creating Limits Tab

	LimitsTab = ttk.Frame(tabcontrol)
	tabcontrol.add(LimitsTab,text = "Limits",padding=10)
	tabcontrol.grid(column=0,row=1)

	# creating the Extensions Tab

	ExtensionsTab = ttk.Frame(tabcontrol)
	tabcontrol.add(ExtensionsTab,text = "Extensions",padding=10)
	tabcontrol.grid(column=0,row=1)

	# Creating the Formats tab

	FormatTab = ttk.Frame(tabcontrol)
	tabcontrol.add(FormatTab,text= "Formats",padding=10)
	tabcontrol.grid(column=0,row=1)

	# Creating the Memory Type Tab

	MemoryTypeTab = ttk.Frame(tabcontrol)
	tabcontrol.add(MemoryTypeTab,text="Memory Type",padding=10)
	tabcontrol.grid(column=0,row=1)

	# Creating Queue Tab

	QueueTab = ttk.Frame(tabcontrol)
	tabcontrol.add(QueueTab,text="Queues Families",padding=10)
	tabcontrol.grid(column=0,row=1)

	#Creating Instance Tab

	InstanceTab = ttk.Frame(tabcontrol)
	tabcontrol.add(InstanceTab,text="Instance Extensions",padding=10)
	tabcontrol.grid(column=0,row=1)

	radvar = tk.IntVar()

	
	def Devices():
		
		# Creating a Treeview for the Device Tab

		TreeDevice = ttk.Treeview(DeviceTab,height=HT)
		TreeDevice['columns'] =('value')
		TreeDevice.column('#0',width=WIDTH1,anchor='sw')
		TreeDevice.column('value',width=WIDTH2,anchor='nw') 

		TreeDevice.grid(column=0,row=0)

		GPU = radvar.get()

		# Fetching the required details using grep, Awk and Cat Commands

		if GPU == 0:
			os.system("cat vulkaninfo.txt | awk '/GPU0/{flag=1;next}/VkPhysicalDeviceLimits:/{flag=0}flag' | awk '/==.*/{flag=1;next}flag' | grep -v driver > Deviceinfo1.txt")
			os.system("cat Deviceinfo1.txt | awk '{gsub(/=.*/,'True');}1' > Deviceinfo.txt")
			os.system("cat Deviceinfo1.txt | grep -o =.* | grep -o ' .*' > Deviceinfo2.txt")

		elif GPU == 1:

			os.system("cat vulkaninfo.txt | awk '/GPU1/{flag=1;next}/VkPhysicalDeviceLimits:/{flag=0}flag' | awk '/==.*/{flag=1;next}flag' | grep -v driver > Deviceinfo1.txt")
			os.system("cat Deviceinfo1.txt | awk '{gsub(/=.*/,'True');}1' > Deviceinfo.txt")
			os.system("cat Deviceinfo1.txt | grep -o =.* | grep -o ' .*' > Deviceinfo2.txt")

		elif GPU == 2:

			os.system("cat vulkaninfo.txt | awk '/GPU2/{flag=1;next}/VkPhysicalDeviceLimits:/{flag=0}flag' | awk '/==.*/{flag=1;next}flag' | grep -v driver > Deviceinfo1.txt")
			os.system("cat Deviceinfo1.txt | awk '{gsub(/=.*/,'True');}1' > Deviceinfo.txt")
			os.system("cat Deviceinfo1.txt | grep -o =.* | grep -o ' .*' > Deviceinfo2.txt")


		# Storing the RHS values into a list

		with open("Deviceinfo2.txt","r") as file1:
			value = []
			for line in file1:
				value.append(line)
		
		# This should take care of api version from 0.0.0 to 5.9.99
		for i in range(5):
			for k in range(10):
				for j in range(100):
					if "(%d.%d.%d)"%(i,k,j) in value[0]:
						value[0] = " %d.%d.%d"%(i,k,j)
						break

		for i in range(len(value)):
			if i > 0 :
				if "0x" in value[i]:
					value[i] = int(value[i],16)
					value[i] = str(" %d"%value[i])



		# Printing the Details into the Treeview
		
		with open("Deviceinfo.txt","r") as file1:
			file1.seek(0,0)
			i = 0
			for line in file1:
				TreeDevice.insert('','end',text=line,values=(value[i],),tags=i)
				if i % 2 != 0 :
					TreeDevice.tag_configure(i,background=COLOR1)
				i = i + 1

		os.system("rm Device*.txt")

	def Features():

		TreeFeatures = ttk.Treeview(FeatureTab,height=HT)
		TreeFeatures['columns'] =('value')
		TreeFeatures.heading("#0", text='Device Features')
		TreeFeatures.column('#0',width=WIDTH1)
		TreeFeatures.heading('value',text="Value")
		TreeFeatures.column('value',width=WIDTH2,anchor=ANCHOR1)

		TreeFeatures.grid(column=0,row=0)

		fsb = ttk.Scrollbar(FeatureTab, orient="vertical", command=TreeFeatures.yview)
		TreeFeatures.configure(yscrollcommand=fsb.set)
		fsb.grid(column=0,row=0,sticky='nse')


		GPU = radvar.get()
		if GPU == 0 :
			os.system("cat vulkaninfo.txt | awk '/GPU0/{flag=1;next}/Format Properties:/{flag=0}flag' | awk '/VkPhysicalDeviceFeatures:/{flag=1; next}/Format Properties:/{flag=0}flag' | awk '/==/{flag=1 ; next} flag' | grep = | sort > VKDFeatures1.txt")
			os.system("cat VKDFeatures1.txt | awk '{gsub(/= 1/,'True');print}' | awk '{gsub(/= 0/,'False');print}' > VKDFeatures.txt")
			
		elif GPU == 1 :
			os.system("cat vulkaninfo.txt | awk '/GPU1/{flag=1;next}/Format Properties:/{flag=0}flag' | awk '/VkPhysicalDeviceFeatures:/{flag=1; next}/Format Properties:/{flag=0}flag' | awk '/==/{flag=1 ; next} flag' | grep = |sort > VKDFeatures1.txt")
			os.system("cat VKDFeatures1.txt | awk '{gsub(/= 1/,'True');print}' | awk '{gsub(/= 0/,'False');print}' > VKDFeatures.txt")

		elif GPU == 2 :
			os.system("cat vulkaninfo.txt | awk '/GPU2/{flag=1;next}/Format Properties:/{flag=0}flag' | awk '/VkPhysicalDeviceFeatures:/{flag=1; next}/Format Properties:/{flag=0}flag' | awk '/==/{flag=1 ; next} flag' | grep = |sort > VKDFeatures1.txt")
			os.system("cat VKDFeatures1.txt | awk '{gsub(/= 1/,'True');print}' | awk '{gsub(/= 0/,'False');print}' > VKDFeatures.txt")

		
		with open("VKDFeatures1.txt","r") as file1:
			value = []
			for line in file1:
				if '= 1' in line:
					value.append("true")
				else:
					value.append("false")
			
		with open("VKDFeatures.txt","r") as file1:
			file1.seek(0,0)
			i = 0
			for line in file1:
				TreeFeatures.insert('','end',text=line,values=(value[i]),tags=(value[i],i))
				if value[i] == "true":
					TreeFeatures.tag_configure(value[i],foreground=COLOR2)
				else:
					TreeFeatures.tag_configure(value[i],foreground=COLOR3)
				if i % 2 != 0:
					TreeFeatures.tag_configure(i,background=COLOR1)
				i = i + 1
		
		os.system("rm VKDFeatures*.txt")	

	
	def Limits():


		TreeLimits = ttk.Treeview(LimitsTab,height = HT,selectmode='extended')
		TreeLimits['columns'] = ('value')
		TreeLimits.heading("#0", text='Device Limits')
		TreeLimits.column('#0',width=WIDTH1)
		TreeLimits.heading('value',text="Limits")
		TreeLimits.column('value',width=WIDTH2,anchor='nw')

		TreeLimits.grid(column=0,row=0,sticky=tk.W)

		lsb = ttk.Scrollbar(LimitsTab, orient="vertical", command=TreeLimits.yview)
		TreeLimits.configure(yscrollcommand=lsb.set)
		lsb.grid(column=0,row=0,sticky='nse')

		GPU = radvar.get()
		if GPU == 0 :
			os.system("cat vulkaninfo.txt | awk '/GPU0/{flag=1;next}/VkPhysicalDeviceSparseProperties:/{flag=0}flag'| awk '/--/{flag=1 ; next} flag' | sort > VKDlimits1.txt")
			os.system("cat VKDlimits1.txt | awk '{gsub(/=.*/,'True');}1' > VKDlimits.txt")
			os.system("cat VKDlimits1.txt | grep -o '=.*' | grep -o '[ -].*' > limits.txt")
		elif GPU == 1 :
			os.system("cat vulkaninfo.txt | awk '/GPU1/{flag=1;next}/VkPhysicalDeviceSparseProperties:/{flag=0}flag'| awk '/--/{flag=1 ; next} flag' | sort > VKDlimits1.txt")
			os.system("cat VKDlimits1.txt | awk '{gsub(/=.*/,'True');}1' > VKDlimits.txt")
			os.system("cat VKDlimits1.txt | grep -o '=.*' | grep -o '[ -].*' > limits.txt")

		elif GPU == 2 :
			os.system("cat vulkaninfo.txt | awk '/GPU2/{flag=1;next}/VkPhysicalDeviceSparseProperties:/{flag=0}flag'| awk '/--/{flag=1 ; next} flag' | sort > VKDlimits1.txt")
			os.system("cat VKDlimits1.txt | awk '{gsub(/=.*/,'True');}1' > VKDlimits.txt")
			os.system("cat VKDlimits1.txt | grep -o '=.*' | grep -o '[ -].*' > limits.txt")

		with open("limits.txt","r") as file1:
			value = []
			for line in file1:
					value.append(line)

		# finding and converting any hexadecimal value to decimal
		
		for i in range(len(value)):
			if "0x" in value[i]:
				value[i] = int(value[i],16)
		with open("VKDlimits.txt","r") as file1:
			count = len(file1.readlines())
			i = 0
			file1.seek(0,0)
			for line in file1:
				TreeLimits.insert('','end',text=line, values= value[i],tags=(i))
				if i % 2 != 0:
					TreeLimits.tag_configure(i,background=COLOR1)
				i = i + 1

		os.system("rm *limits*.txt")		

	def Extensions():


		TreeExtension = ttk.Treeview(ExtensionsTab, height=HT)
		TreeExtension.heading("#0", text='Device Extensions')
		TreeExtension.column('#0',width=WIDTH1,anchor=ANCHOR1)
		TreeExtension['column'] = ('version')
		TreeExtension.grid(column=0,row=0)
		TreeExtension.heading('version',text="Version")
		TreeExtension.column('version',width=WIDTH2,anchor=ANCHOR1)

		esb = ttk.Scrollbar(ExtensionsTab, orient="vertical", command=TreeExtension.yview)
		TreeExtension.configure(yscrollcommand=esb.set)
		esb.grid(column=0,row=0,sticky='nse')

		GPU = radvar.get()
		
		if GPU == 0 :
			os.system("cat vulkaninfo.txt | awk '/GPU0/{flag=1;next}/VkQueueFamilyProperties/{flag=0}flag'|awk '/Device Extensions/{flag=1; next}/VkQueueFamilyProperties/{flag=0} flag' | grep VK_ | sort > VKDExtensions1.txt")
			os.system("cat VKDExtensions1.txt | awk '{gsub(/:.*/,'True');print} ' > VKDExtensions.txt")
			
		
		elif GPU == 1 :
			os.system("cat vulkaninfo.txt | awk '/GPU1/{flag=1;next}/VkQueueFamilyProperties/{flag=0}flag'|awk '/Device Extensions/{flag=1; next}/VkQueueFamilyProperties/{flag=0} flag'| grep VK_ |sort > VKDExtensions1.txt")
			os.system("cat VKDExtensions1.txt | awk '{gsub(/:.*/,'True');print} ' > VKDExtensions.txt")
			

		elif GPU == 2 :
			os.system("cat vulkaninfo.txt | awk '/GPU2/{flag=1;next}/VkQueueFamilyProperties/{flag=0}flag'|awk '/Device Extensions/{flag=1; next}/VkQueueFamilyProperties/{flag=0} flag'| grep VK_ |sort > VKDExtensions1.txt")
			os.system("cat VKDExtensions1.txt | awk '{gsub(/:.*/,'True');print} ' > VKDExtensions.txt")

		
		# This should take care of further versioning till 100
		with open("VKDExtensions1.txt","r") as file1:
			value = []
			for line in file1:
				for j in range(100):
					if ": extension revision  %d"%j in line:
						value.append("0.0.%d"%j)
						break
					if ": extension revision %2d"%j in line:
						value.append("0.0.%2d"%j)
						break


		with open("VKDExtensions.txt","r") as file1:
			count = len(file1.readlines())
			tabcontrol.tab(3,text="Extensions(%d)"%count)
			file1.seek(0,0)
			i = 0
			for line in file1:
				TreeExtension.insert('','end',text=line,values=(value[i]),tags=i)
				if i % 2 != 0:
					TreeExtension.tag_configure(i,background=COLOR1)
				i = i + 1

		os.system("rm VKDExtensions*.txt")


	def Format():

		TreeFormat = ttk.Treeview(FormatTab, height=HT)
		TreeFormat['columns'] = ("linear","optimal","Buffer")
		TreeFormat.heading("#0", text='Format')
		TreeFormat.column('#0',width=550)
		TreeFormat.heading("linear",text="linear")
		TreeFormat.column("linear",width=100,anchor=ANCHOR1)
		TreeFormat.heading("optimal",text="optimal")
		TreeFormat.column("optimal",width=100,anchor=ANCHOR1)
		TreeFormat.heading("Buffer",text= "Buffer")
		TreeFormat.column("Buffer",width=100,anchor=ANCHOR1)
		TreeFormat.grid(column=0,row=0)
		
		vsb = ttk.Scrollbar(FormatTab, orient="vertical", command=TreeFormat.yview)
		TreeFormat.configure(yscrollcommand=vsb.set)
		vsb.grid(column=0,row=0,sticky='nse')



		GPU = radvar.get()
		if GPU == 0 :
			os.system("cat vulkaninfo.txt | awk '/GPU0/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | grep ^FORMAT_   > VKDFORMATS.txt")
			os.system("cat vulkaninfo.txt | awk '/GPU0/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /linearTiling.*/{f=1}'> VKDFORMATSlinear.txt")
			os.system("cat vulkaninfo.txt | awk '/GPU0/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /optimalTiling.*/{f=1}'> VKDFORMATSoptimal.txt")
			os.system("cat vulkaninfo.txt | awk '/GPU0/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /bufferFeatures.*/{f=1}'> VKDFORMATSBuffer.txt")
		

		elif GPU == 1 :
			os.system("cat vulkaninfo.txt | awk '/GPU1/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | grep ^FORMAT_  > VKDFORMATS.txt")
			os.system("cat vulkaninfo.txt | awk '/GPU1/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /linearTiling.*/{f=1}'> VKDFORMATSlinear.txt")
			os.system("cat vulkaninfo.txt | awk '/GPU1/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /optimalTiling.*/{f=1}'> VKDFORMATSoptimal.txt")
			os.system("cat vulkaninfo.txt | awk '/GPU1/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /bufferFeatures.*/{f=1}'> VKDFORMATSBuffer.txt")
		
		elif GPU == 2 :
			os.system("cat vulkaninfo.txt | awk '/GPU2/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | grep ^FORMAT_  > VKDFORMATS.txt")
			os.system("cat vulkaninfo.txt | awk '/GPU2/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /linearTiling.*/{f=1}'> VKDFORMATSlinear.txt")
			os.system("cat vulkaninfo.txt | awk '/GPU2/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /optimalTiling.*/{f=1}'> VKDFORMATSoptimal.txt")
			os.system("cat vulkaninfo.txt | awk '/GPU2/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /bufferFeatures.*/{f=1}'> VKDFORMATSBuffer.txt")
		

		linear = []
		optimal = []
		Buffer = []

		# Linear values 

		with open("VKDFORMATSlinear.txt","r") as file1:
			count = len(file1.readlines())
			file1.seek(0,0)
			for line in file1:
				if line == "		None\n":
					linear.append("false")
				else:
					linear.append("true")

		# Optimal Values

		with open("VKDFORMATSoptimal.txt","r") as file1:
			for line in file1:
				if line == "		None\n":
					optimal.append("false")
				else:
					optimal.append("true")



		with open("VKDFORMATSBuffer.txt","r") as file1:
			for line in file1:
				if line == "		None\n":
					Buffer.append("false")
				else:
					Buffer.append("true")

		# counting the number of formats supported
		Formats = 0
		for i in range(count):
			if linear[i] == "true" or optimal[i] == "true" or Buffer[i] == "true":
				Formats = Formats + 1

		with open("VKDFORMATS.txt","r") as file1:
			file1.seek(0,0)
			tabcontrol.tab(4,text="Formats(%d)"%Formats)
			i = 0
			for line in file1:
				TreeFormat.insert('','end',text=line,values=(linear[i],optimal[i],Buffer[i]),tags=i)
				if i % 2 != 0 :
					TreeFormat.tag_configure(i,background=COLOR1)
				i = i + 1

				
		os.system("rm VKDFORMATS*.txt")

	def MemoryTypes():


		frameType = ttk.LabelFrame(MemoryTypeTab,text="Types")
		frameType.grid(column=0,row=0,pady=15)
		TreeMemory = ttk.Treeview(frameType,height=HT2)
		TreeMemory['columns'] = ('value1','value2','value3','value4','value5','value6')
		TreeMemory.heading('#0',text="Types")
		TreeMemory.column('#0',width=95,anchor=ANCHOR1)
		TreeMemory.heading('value1',text="Heap Index")
		TreeMemory.column('value1',width=100,anchor=ANCHOR1)
		TreeMemory.heading('value2',text="Device_Local")
		TreeMemory.column('value2',width=120,anchor=ANCHOR1)
		TreeMemory.heading('value3',text="Host_Visible")
		TreeMemory.column('value3',width=120,anchor=ANCHOR1)
		TreeMemory.heading('value4',text="Host_Coherent")
		TreeMemory.column('value4',width=120,anchor=ANCHOR1)
		TreeMemory.heading('value5',text="Host_Cached")
		TreeMemory.column('value5',width=140,anchor=ANCHOR1)
		TreeMemory.heading('value6',text="Lazily_Allocated")
		TreeMemory.column('value6',width=150,anchor=ANCHOR1)
		TreeMemory.grid(column=0,row=0)
		
		Mvsb = ttk.Scrollbar(frameType, orient="vertical", command=TreeMemory.yview)
		TreeMemory.configure(yscrollcommand=Mvsb.set)
		Mvsb.grid(column=0,row=0,sticky='nse')

		GPU = radvar.get()
		if GPU == 0 :
			os.system("cat vulkaninfo.txt | awk '/GPU0/{flag=1;next}/VkPhysicalDeviceFeatures:/{flag=0}flag'|awk '/VkPhysicalDeviceMemoryProperties:/{flag=1; next}/VkPhysicalDeviceFeatures:/{flag=0} flag' > VKDMemoryType.txt")
			
			
		elif GPU == 1 :
			os.system("cat vulkaninfo.txt | awk '/GPU1/{flag=1;next}/VkPhysicalDeviceFeatures:/{flag=0}flag'|awk '/VkPhysicalDeviceMemoryProperties:/{flag=1; next}/VkPhysicalDeviceFeatures:/{flag=0} flag' > VKDMemoryType.txt")
			
			
		
		elif GPU == 2 :
			os.system("cat vulkaninfo.txt | awk '/GPU2/{flag=1;next}/VkPhysicalDeviceFeatures:/{flag=0}flag'|awk '/VkPhysicalDeviceMemoryProperties:/{flag=1; next}/VkPhysicalDeviceFeatures:/{flag=0} flag' > VKDMemoryType.txt")
			
			
		

		with open("VKDMemoryType.txt","r") as file1:
			heapIndex = []
			for line in file1:
				for j in range(100):
					if "heapIndex" in line:
						if "= %d"%j in line:
							heapIndex.append(j)
							break


		Device_Local = []
		Host_Visible = []
		Host_Coherent = []
		Host_Cached = []
		Lazily_Allocated = []
		Mcount = 0

		with open("VKDMemoryType.txt","r") as file1:
			for line in file1:
				if "memoryTypes" in line:
					Mcount = Mcount + 1
				if " 0x0:\n" in line:
					Device_Local.append("false")
					Host_Visible.append("false")
					Host_Coherent.append("false")
					Host_Cached.append("false")
					Lazily_Allocated.append("false")

				if " 0x1:" in line:
					Device_Local.append("true")
					Host_Visible.append("false")
					Host_Coherent.append("false")
					Host_Cached.append("false")
					Lazily_Allocated.append("false")

				if " 0x2:" in line:
					Device_Local.append("false")
					Host_Visible.append("true")
					Host_Coherent.append("false")
					Host_Cached.append("false")
					Lazily_Allocated.append("false")
				
				if " 0x3:" in line:
					Device_Local.append("true")
					Host_Visible.append("true")
					Host_Coherent.append("false")
					Host_Cached.append("false")
					Lazily_Allocated.append("false")
				
				if " 0x4:" in line:
					Device_Local.append("false")
					Host_Visible.append("false")
					Host_Coherent.append("true")
					Host_Cached.append("false")
					Lazily_Allocated.append("false")
				
				if " 0x5:" in line:
					Device_Local.append("true")
					Host_Visible.append("false")
					Host_Coherent.append("true")
					Host_Cached.append("false")
					Lazily_Allocated.append("false")
					
				if " 0x6:" in line:
					Device_Local.append("false")
					Host_Visible.append("true")
					Host_Coherent.append("true")
					Host_Cached.append("false")
					Lazily_Allocated.append("false")
					
				if " 0x7:" in line:
					Device_Local.append("true")
					Host_Visible.append("true")
					Host_Coherent.append("true")
					Host_Cached.append("false")
					Lazily_Allocated.append("false")

				if " 0x8:" in line:
					Device_Local.append("false")
					Host_Visible.append("false")
					Host_Coherent.append("false")
					Host_Cached.append("true")
					Lazily_Allocated.append("false")
			
				if line == " 0x9:\n":
					Device_Local.append("true")
					Host_Visible.append("false")
					Host_Coherent.append("false")
					Host_Cached.append("true")
					Lazily_Allocated.append("false")
			
				if " 0xa:" in line:
					Device_Local.append("false")
					Host_Visible.append("true")
					Host_Coherent.append("false")
					Host_Cached.append("true")
					Lazily_Allocated.append("false")
			
				if " 0xb:" in line:
					Device_Local.append("true")
					Host_Visible.append("true")
					Host_Coherent.append("false")
					Host_Cached.append("true")
					Lazily_Allocated.append("false")
			
				if " 0xc:" in line:
					Device_Local.append("false")
					Host_Visible.append("false")
					Host_Coherent.append("true")
					Host_Cached.append("true")
					Lazily_Allocated.append("false")
			
				if " 0xd:" in line:
					Device_Local.append("true")
					Host_Visible.append("false")
					Host_Coherent.append("true")
					Host_Cached.append("true")
					Lazily_Allocated.append("false")
								
				if " 0xe:" in line:
					Device_Local.append("false")
					Host_Visible.append("true")
					Host_Coherent.append("true")
					Host_Cached.append("true")
					Lazily_Allocated.append("false")

				if " 0xf:" in line:
					Device_Local.append("true")
					Host_Visible.append("true")
					Host_Coherent.append("true")
					Host_Cached.append("true")
					Lazily_Allocated.append("false")
			
			

			
			for i in range(Mcount):
				TreeMemory.insert('','end',text=i,values=(heapIndex[i],Device_Local[i],Host_Visible[i],Host_Coherent[i],Host_Cached[i],Lazily_Allocated[i]),tags=(i))
				if i % 2 != 0:
					TreeMemory.tag_configure(i,background=COLOR1)
				

		

		# Memory Heap Details to be populated

		frameHeap = ttk.LabelFrame(MemoryTypeTab,text="Heaps")
		frameHeap.grid(column=0,row=1)
		TreeHeap = ttk.Treeview(frameHeap,height=10)
		TreeHeap['columns'] = ('value1','value2')
		TreeHeap.heading('#0',text='Heaps')
		TreeHeap.column('#0',width=95,anchor=ANCHOR1)
		TreeHeap.heading('value1',text='Device Size')
		TreeHeap.column('value1',width=300,anchor=ANCHOR1)
		TreeHeap.heading('value2',text='HEAP_DEVICE_LOCAL')
		TreeHeap.column('value2',width=450,anchor=ANCHOR1)
		TreeHeap.grid(column=0,row=1)

		Hvsb = ttk.Scrollbar(frameHeap, orient="vertical", command=TreeHeap.yview)
		TreeMemory.configure(yscrollcommand=Hvsb.set)
		Hvsb.grid(column=0,row=1,sticky='nse')

		HCount = 0
		size = []
		HEAP_DEVICE_LOCAL = []

		with open("VKDMemoryType.txt","r") as file1:
			for line in file1:
				if "memoryHeaps" in line:
					HCount = HCount + 1
				if "HEAP_DEVICE_LOCAL" in line:
					HEAP_DEVICE_LOCAL.append("true")
				if "None" in line:
					HEAP_DEVICE_LOCAL.append("false")
				if "size " in line:
					for j in range(100):
						for k in range(100):
							if "(%d.%d GiB)"%(j,k) in line:
								size.append("%d.%d GB"%(j,k))
								break
							elif "(%d.%d0 GiB)"%(j,k) in line:
								size.append("%d.%d0 GB"%(j,k))
								break


		tabcontrol.tab(5,text="Memory Types(%d) & Heaps(%d)"%(Mcount,HCount))
		for i in range(HCount):
				TreeHeap.insert('','end',text=i,values=(size[i],HEAP_DEVICE_LOCAL[i]),tags=(i))
				if i % 2 != 0:
					TreeHeap.tag_configure(i,background=COLOR1)

		os.system("rm VKDMemory*.txt")

	def Queues():


		TreeQueue = ttk.Treeview(QueueTab,height=HT)
		TreeQueue['columns'] = ('count','bits','Gbit','Cbit','Tbit','sbit')
		TreeQueue.heading('#0',text="Queue Family")
		TreeQueue.column('#0',width=100,anchor=ANCHOR1)
		
		TreeQueue.heading('count',text='Queue Count')
		TreeQueue.column('count',width=100,anchor=ANCHOR1)
		TreeQueue.heading('bits',text="timestampValidBits")
		TreeQueue.column('bits',width=150,anchor=ANCHOR1)
		TreeQueue.heading('Gbit',text="GRAPHICS_BIT")
		TreeQueue.column('Gbit',width=110,anchor=ANCHOR1)
		TreeQueue.heading('Cbit',text='COMPUTE_BIT')
		TreeQueue.column('Cbit',width=110,anchor=ANCHOR1)
		TreeQueue.heading('Tbit',text="TRANSFER_BIT")
		TreeQueue.column('Tbit',width=110,anchor=ANCHOR1)
		TreeQueue.heading('sbit',text="SPARSE_BINDING_BIT",anchor='center')
		TreeQueue.column('sbit',width=170,anchor=ANCHOR1)
		TreeQueue.grid(column=0,row=0)

		Qvsb = ttk.Scrollbar(QueueTab, orient="vertical", command=TreeQueue.yview)
		TreeQueue.configure(yscrollcommand=Qvsb.set)
		Qvsb.grid(column=0,row=0,sticky='nse')


		GPU = radvar.get()
		if GPU == 0 :
			os.system("cat vulkaninfo.txt | awk '/GPU0/{flag=1;next}/VkPhysicalDeviceMemoryProperties:/{flag=0}flag'|awk '/VkQueue.*/{flag=1; next}/VkPhysicalDeviceMemoryProperties:/{flag=0} flag' > VKDQueues.txt")
			os.system("cat VKDQueues.txt | grep Count | grep -o =.* | grep -o ' .*' > VKDQueuecount.txt")
			os.system("cat VKDQueues.txt | grep times | grep -o =.* | grep -o ' .*' > VKDQueuebits.txt")
			os.system("cat VKDQueues.txt | grep Flags | grep -o =.* | grep -o ' .*' > VKDQueueFlags.txt")

		elif GPU == 1 :
			os.system("cat vulkaninfo.txt | awk '/GPU1/{flag=1;next}/VkPhysicalDeviceMemoryProperties:/{flag=0}flag'|awk '/VkQueue.*/{flag=1; next}/VkPhysicalDeviceMemoryProperties:/{flag=0} flag' > VKDQueues.txt")
			os.system("cat VKDQueues.txt | grep Count | grep -o =.* | grep -o ' .*' > VKDQueuecount.txt")
			os.system("cat VKDQueues.txt | grep times | grep -o =.* | grep -o ' .*' > VKDQueuebits.txt")
			os.system("cat VKDQueues.txt | grep Flags | grep -o =.* | grep -o ' .*' > VKDQueueFlags.txt")

		elif GPU == 2 :
			os.system("cat vulkaninfo.txt | awk '/GPU2/{flag=1;next}/VkPhysicalDeviceMemoryProperties:/{flag=0}flag'|awk '/VkQueue.*/{flag=1; next}/VkPhysicalDeviceMemoryProperties:/{flag=0} flag' > VKDQueues.txt")
			os.system("cat VKDQueues.txt | grep Count | grep -o =.* | grep -o ' .*' > VKDQueuecount.txt")
			os.system("cat VKDQueues.txt | grep times | grep -o =.* | grep -o ' .*' > VKDQueuebits.txt")
			os.system("cat VKDQueues.txt | grep Flags | grep -o =.* | grep -o ' .*' > VKDQueueFlags.txt")

		qCount = []
		qBits = []
		GBit = []
		CBit = []
		TBit = []
		SBit = []

		# finding and storing the value for Flags
		with open("VKDQueueFlags.txt","r") as file1:
			for line in file1:
				if "GRAPHICS" in line:
					GBit.append("true")
				else:
					GBit.append("false")
				if "COMPUTE" in line:
					CBit.append("true")
				else:
					CBit.append("false")
				if "TRANSFER" in line:
					TBit.append("true")
				else:
					TBit.append("false")
				if "SPARSE" in line:
					SBit.append("true")
				else:
					SBit.append("false")

		with open("VKDQueuecount.txt","r") as file1:
			count = len(file1.readlines())
			file1.seek(0,0)
			for line in file1:
				qCount.append(int(line))

		with open("VKDQueuebits.txt","r") as file1:
			for line in file1:
				qBits.append(int(line))

		tabcontrol.tab(6,text="Queue Families(%d)"%count)
		for i in range(count):
			TreeQueue.insert('','end',text=i,values=(qCount[i],qBits[i],GBit[i],CBit[i],TBit[i],SBit[i]),tags=i)
			if i % 2 != 0:
				TreeQueue.tag_configure(i,background=COLOR1)

		os.system("rm VKDQueue*.txt")

	def Instance():

	
		os.system("cat vulkaninfo.txt | awk '/Instance Extensions	count.*/{flag=1;next}/Layers: count.*/{flag=0}flag'| grep VK_ | sort > VKDInstanceExtensions1.txt")
		os.system("cat VKDInstanceExtensions1.txt | awk '{gsub(/:.*/,'True');print} ' > VKDInstanceExtensions.txt")
		
		frame1 = ttk.LabelFrame(InstanceTab,text="Instance Extensions")
		frame1.grid(column=0,row=0,pady=13)	
		frame2 = ttk.LabelFrame(InstanceTab,text="Layers")
		frame2.grid(column=0,row=1)
		
		TreeInstance = ttk.Treeview(frame1, height=HT2)
		TreeInstance.heading("#0", text='Instance Extensions')
		TreeInstance.column('#0',width=WIDTH1,anchor=ANCHOR1)
		TreeInstance['column'] = ('version')
		TreeInstance.grid(column=0,row=0)
		TreeInstance.heading('version',text="Version")
		TreeInstance.column('version',width=WIDTH2-5,anchor=ANCHOR1)

		Isb = ttk.Scrollbar(frame1, orient="vertical", command=TreeInstance.yview)
		TreeInstance.configure(yscrollcommand=Isb.set)
		Isb.grid(column=0,row=0,sticky='nse')

		# This should take care of further versioning till 100
		with open("VKDInstanceExtensions1.txt","r") as file1:
			value = []
			for line in file1:
				for j in range(100):
					if ": extension revision  %d"%j in line:
						value.append("0.0.%d"%j)
						break
					if ": extension revision %2d"%j in line:
						value.append("0.0.%2d"%j)
						break


		with open("VKDInstanceExtensions.txt","r") as file1:
			count1 = len(file1.readlines())
			tabcontrol.tab(7,text="Instances(%d)"%count1)
			file1.seek(0,0)
			i = 0
			for line in file1:
				TreeInstance.insert('','end',text=line,values=(value[i]),tags=i)
				if i % 2 != 0:
					TreeInstance.tag_configure(i,background=COLOR1)
				i = i + 1

		os.system("rm VKDInstanceExtensions*.txt")

		TreeLayer = ttk.Treeview(frame2,height=10)
		TreeLayer['columns'] =('value1','value2','value3')
		TreeLayer.heading('#0',text='Layer Name')
		TreeLayer.column('#0',width=460,anchor=ANCHOR1)
		TreeLayer.heading('value1',text='Vulkan Version')
		TreeLayer.column('value1',width=113,anchor=ANCHOR1)
		TreeLayer.heading('value2',text="Layer Version")
		TreeLayer.column('value2',width=112,anchor=ANCHOR1)
		TreeLayer.heading('value3',text='Extension Count')
		TreeLayer.column('value3',width=150,anchor=ANCHOR1)
		TreeLayer.grid(column=0,row=1,pady=10)

		lsb = ttk.Scrollbar(frame2, orient="vertical", command=TreeLayer.yview)
		TreeLayer.configure(yscrollcommand=lsb.set)
		lsb.grid(column=0,row=1,sticky='nse',pady=10)

		os.system("cat vulkaninfo.txt | awk '/Layers: count.*/{flag=1;next}/Presentable Surfaces.*/{flag=0}flag' > VKDLayer1.txt")
		os.system("cat VKDLayer1.txt | grep VK_ | awk '{gsub(/\(.*/,'True');print} ' > VKDLayer.txt")

		Vversion = []
		with open("VKDLayer1.txt","r") as file1:
			for line in file1:
				for j in range(100):
					if "Vulkan version 1.0.%d,"%j in line:
						Vversion.append("1.0.%d"%j)
						
					


		LVersion = []
		with open("VKDLayer1.txt","r") as file1:
			for line in file1:
				for j in range(100):
					if "layer version %d"%j in line:
						LVersion.append("0.0.%d"%j)
						break

		ECount = []
		with open("VKDLayer1.txt","r") as file1:
			for line in file1:
				for j in range(100):
					if "Layer Extensions	count = %d"%j in line:
						ECount.append("%d"%j)
						break





		count2 = len(LVersion)
		tabcontrol.tab(7,text="Instances(%d) & Layers(%d)"%(count1,count2))
		with open("VKDLayer.txt","r") as file1:
			i = 0
			for line in file1:
				TreeLayer.insert('','end',text=line,values=(Vversion[i],LVersion[i],ECount[i]),tags=i)
				if i % 2 != 0:
					TreeLayer.tag_configure(i,background=COLOR1)
				i = i + 1				

		os.system("rm VKDL*.txt")


	def radcall():
		radsel= radvar.get()
		if radsel == 0:
			Devices()
			Features()
			Limits()
			Extensions()
			Format()
			MemoryTypes()
			Queues()
		elif radsel == 1:
			Devices()
			Features()
			Limits()
			Extensions()
			Format()
			MemoryTypes()
			Queues()
		elif radsel == 2:
			Devices()
			Features()
			Limits()
			Extensions()
			Format()
			MemoryTypes()
			Queues()
		
		Instance()


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
		GPU.grid(column=1,row=i,sticky=tk.W,padx=30)
		if i == 0:
			GPU.invoke()


	os.system("rm GPU.txt")
	
