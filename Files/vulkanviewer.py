import tkinter as tk
from tkinter import ttk 
import os

HT = 30
HT2 = 13
HT3 = 13
COLOR1 = "GRAY91"
COLOR2 = "GREEN"
COLOR3 = "RED"
ANCHOR1 = "center"
WIDTH1 = 600
WIDTH2 = 245
WIDTH3 = 100
PAD1 = 10
RANGE1 = 100

def Vulkan(tab2):

	
	# Creating Tabs for different Features

	#Creating Feature Tab
	os.system("vulkaninfo > vulkaninfo.txt")

	tabcontrol = ttk.Notebook(tab2, padding=PAD1)
	#tabcontrol.enable_traversal()
	
	# Creating the Features Tab

	DeviceTab = ttk.Frame(tabcontrol,padding=PAD1)
	tabcontrol.add(DeviceTab,text="Device")
	tabcontrol.grid(column=0,row=1,padx=5)

	FeatureTab = ttk.Frame(tabcontrol)
	tabcontrol.add(FeatureTab, text="Features",padding=PAD1)
	tabcontrol.grid(column=0,row=1)

 	#Creating Limits Tab

	LimitsTab = ttk.Frame(tabcontrol)
	tabcontrol.add(LimitsTab,text = "Limits",padding=PAD1)
	tabcontrol.grid(column=0,row=1)

	# creating the Extensions Tab

	ExtensionsTab = ttk.Frame(tabcontrol)
	tabcontrol.add(ExtensionsTab,text = "Extensions",padding=PAD1)
	tabcontrol.grid(column=0,row=1)

	# Creating the Formats tab

	FormatTab = ttk.Frame(tabcontrol)
	tabcontrol.add(FormatTab,text= "Formats",padding=PAD1)
	tabcontrol.grid(column=0,row=1)

	# Creating the Memory Type Tab

	MemoryTypeTab = ttk.Frame(tabcontrol)
	tabcontrol.add(MemoryTypeTab,text="Memory Type",padding=PAD1)
	tabcontrol.grid(column=0,row=1)

	# Creating Queue Tab

	QueueTab = ttk.Frame(tabcontrol)
	tabcontrol.add(QueueTab,text="Queues Families",padding=PAD1)
	tabcontrol.grid(column=0,row=1)

	#Creating Instance Tab

	InstanceTab = ttk.Frame(tabcontrol)
	tabcontrol.add(InstanceTab,text="Instance Extensions",padding=PAD1)
	tabcontrol.grid(column=0,row=1)

	radvar = tk.IntVar()

	def treeview_sort_column(tv, col, reverse):
	  #  print('sorting %s!' % col)
	    l = [(tv.set(k, col), k) for k in tv.get_children('')]
	    l.sort(reverse=reverse)

	    # rearrange items in sorted positions
	    for index, (val, k) in enumerate(l):
	      #  print('Moving Index:%r, Value:%r, k:%r' % (index, val, k))
	        tv.move(k, '', index)

	    # reverse sort next time
	    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))
	 
	def Devices():
		
		# Creating a Treeview for the Device Tab

		frameDevice = ttk.LabelFrame(DeviceTab,text="Device Info.",padding=PAD1)
		frameDevice.grid(column=0,row=0)

		TreeDevice = ttk.Treeview(frameDevice,height=HT3)
		TreeDevice['columns'] =('value')
		TreeDevice.column('#0',width=WIDTH1,anchor='center')
		TreeDevice.column('value',width=WIDTH2,anchor='nw') 

		TreeDevice.grid(column=0,row=0)

		Dsb = ttk.Scrollbar(frameDevice, orient="vertical", command=TreeDevice.yview)
		TreeDevice.configure(yscrollcommand=Dsb.set)
		Dsb.grid(column=0,row=0,sticky='nse')

		GPU = radvar.get()
		# Fetching the required details using grep, Awk and Cat Commands

		for i in range(GPUcount):
			if GPU == i:
				os.system("cat vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceLimits:/{flag=0}flag' | awk '/==.*/{flag=1;next}flag' | grep -v driver > VKDDeviceinfo1.txt"%i)	

		os.system("cat VKDDeviceinfo1.txt | awk '{gsub(/=.*/,'True');}1' > VKDDeviceinfo.txt")
		os.system("cat VKDDeviceinfo1.txt | grep -o =.* | grep -o ' .*' > VKDDeviceinfo2.txt")

		# Storing the RHS values into a list

		with open("VKDDeviceinfo2.txt","r") as file1:
			value = []
			for line in file1:
				value.append(line)
		
		# This should take care of api version from 0.0.0 to 5.9.99
		for i in range(5):
			for k in range(10):
				for j in range(RANGE1):
					if "(%d.%d.%d)"%(i,k,j) in value[0]:
						value[0] = " %d.%d.%d"%(i,k,j)
						break

		for i in range(len(value)):
			if i > 0 :
				if "0x" in value[i]:
					value[i] = int(value[i],16)
					value[i] = str(" %d"%value[i])


	
		# Printing the Details into the Treeview
		try:
			with open("VKDDeviceinfo.txt","r") as file1:
				file1.seek(0,0)
				i = 0
				for line in file1:
					TreeDevice.insert('','end',text=line,values=(value[i],),tags=i)
					if i % 2 != 0 :
						TreeDevice.tag_configure(i,background=COLOR1)
					i = i + 1			
		except Exception as e:
			raise e
		finally:

			# Physical Device Sparse properties
			frameSparse = ttk.LabelFrame(DeviceTab,text="Device Sparse Properties",padding=PAD1)
			frameSparse.grid(column=0,row=1,pady=10)
			cols = ("Device Sparse Properties","Value")
			TreeSparse = ttk.Treeview(frameSparse,columns=cols,height=HT2,show="headings")
			TreeSparse.column('Device Sparse Properties',width=WIDTH1,anchor='sw')
			TreeSparse.column('Value',width=WIDTH2) 
			for each in cols:
				TreeSparse.heading(each,text=each,command=lambda each_=each: treeview_sort_column(TreeSparse, each_, True))

			TreeSparse.grid(column=0,row=1)

			ssb = ttk.Scrollbar(frameSparse, orient="vertical", command=TreeSparse.yview)
			TreeSparse.configure(yscrollcommand=ssb.set)
			ssb.grid(column=0,row=1,sticky='nse')

			for i in range(GPUcount):
				if GPU == i:
					os.system("cat vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Extensions.*/{flag=0}flag' | awk '/VkPhysicalDeviceSparseProperties:/{flag=1;next}/Device Extensions.*/{flag=0}flag' | grep = | sort > VKDDevicesparseinfo1.txt"%i)

			os.system("cat VKDDevicesparseinfo1.txt | awk '{gsub(/=.*/,'True');}1' > VKDDevicesparseinfo.txt")
		
			with open("VKDDevicesparseinfo1.txt","r") as file1:
				value = []
				for line in file1:
					if '= 1' in line:
						value.append("true")
					else:
						value.append("false")
			try:
				with open("VKDDevicesparseinfo.txt","r") as file1:
					file1.seek(0,0)
					i = 0
					for line in file1:
						TreeSparse.insert('','end',values=(line,value[i],),tags=(value[i],i))
						if value[i] == "true":
							TreeSparse.tag_configure(value[i],foreground=COLOR2)
						else:
							TreeSparse.tag_configure(value[i],foreground=COLOR3)
						if i % 2 != 0 :
							TreeSparse.tag_configure(i,background=COLOR1)
						i = i + 1			
			except Exception as e:
				raise e


	def Features():

		frameFeatures = ttk.LabelFrame(FeatureTab,text="Device Features",padding=PAD1)
		frameFeatures.grid(column=0,row=0)
		cols = ('Device Features','Value')
		TreeFeatures = ttk.Treeview(frameFeatures,columns=cols,height=HT,show="headings")
		TreeFeatures.column('Device Features',width=WIDTH1)
		TreeFeatures.column('Value',width=WIDTH2,anchor=ANCHOR1)

		for each in cols:
			TreeFeatures.heading(each,text=each,command=lambda each_=each: treeview_sort_column(TreeFeatures, each_, True))

		TreeFeatures.grid(column=0,row=0)

		fsb = ttk.Scrollbar(frameFeatures, orient="vertical", command=TreeFeatures.yview)
		TreeFeatures.configure(yscrollcommand=fsb.set)
		fsb.grid(column=0,row=0,sticky='nse')


		GPU = radvar.get()

		for i in range(GPUcount):
			if GPU == i :
				os.system("cat vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Format Properties:/{flag=0}flag' | awk '/VkPhysicalDeviceFeatures:/{flag=1; next}/Format Properties:/{flag=0}flag' | awk '/==/{flag=1 ; next} flag' | grep = | sort > VKDFeatures1.txt"%i)

		os.system("cat VKDFeatures1.txt | awk '{gsub(/= 1/,'True');print}' | awk '{gsub(/= 0/,'False');print}' > VKDFeatures.txt")
		
		with open("VKDFeatures1.txt","r") as file1:
			value = []
			for line in file1:
				if '= 1' in line:
					value.append("true")
				else:
					value.append("false")

		style = ttk.Style()

		try:
			with open("VKDFeatures.txt","r") as file1:
				file1.seek(0,0)
				i = 0
				for line in file1:
					TreeFeatures.insert('','end',values=(line,value[i]),tags=(value[i],i))
					if value[i] == "true":
						TreeFeatures.tag_configure(value[i],foreground=COLOR2)
						#style.configure('Treeview',foreground=COLOR2)

					else:
						TreeFeatures.tag_configure(value[i],foreground=COLOR3)
					if i % 2 != 0:
						TreeFeatures.tag_configure(i,background=COLOR1)
					i = i + 1			
		except Exception as e:
			raise e
		
	def Limits():

		frameLimits = ttk.LabelFrame(LimitsTab,text="Device Limits",padding=PAD1)
		frameLimits.grid(column=0,row=0)
		TreeLimits = ttk.Treeview(frameLimits,height = HT)
		TreeLimits['columns'] = ('value')
		TreeLimits.heading("#0", text='Device Limits')
		TreeLimits.column('#0',width=WIDTH1)
		TreeLimits.heading('value',text="Limits",anchor='sw')
		TreeLimits.column('value',width=WIDTH2,anchor='nw')

		TreeLimits.grid(column=0,row=0,sticky=tk.W)

		lsb = ttk.Scrollbar(frameLimits, orient="vertical", command=TreeLimits.yview)
		TreeLimits.configure(yscrollcommand=lsb.set)
		lsb.grid(column=0,row=0,sticky='nse')

		GPU = radvar.get()

		for i in range(GPUcount):
			if GPU == i :
				os.system("cat vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceSparseProperties:/{flag=0}flag'| awk '/--/{flag=1 ; next} flag' | sort > VKDlimits1.txt"%i)

		os.system("cat VKDlimits1.txt | awk '{gsub(/=.*/,'True');}1' > VKDlimits.txt")
		os.system("cat VKDlimits1.txt | grep -o '=.*' | grep -o '[ -].*' > VKDlimits2.txt")

		with open("VKDlimits2.txt","r") as file1:
			value = []
			for line in file1:
					value.append(line)

		# finding and converting any hexadecimal value to decimal
		
		for i in range(len(value)):
			if "0x" in value[i]:
				value[i] = int(value[i],16)

		try:
			with open("VKDlimits.txt","r") as file1:
				count = len(file1.readlines())
				i = 0
				file1.seek(0,0)
				for line in file1:
					TreeLimits.insert('','end',text=line, values=value[i],tags=(i))
					if i % 2 != 0:
						TreeLimits.tag_configure(i,background=COLOR1)
					i = i + 1
		except Exception as e:
			raise e
		
	def Extensions():

		frameExtension = ttk.LabelFrame(ExtensionsTab,text="Device Extensions",padding=PAD1)
		frameExtension.grid(column=0,row=0)
		cols = ("Device Extensions","Version")
		TreeExtension = ttk.Treeview(frameExtension,columns=cols,show="headings",height=HT)
		TreeExtension.column('Device Extensions',width=WIDTH1,anchor="sw")
		TreeExtension.column('Version',width=WIDTH2,anchor=ANCHOR1)
		for each in cols:
			TreeExtension.heading(each,text=each,command=lambda each_=each: treeview_sort_column(TreeExtension, each_, True))

		TreeExtension.grid(column=0,row=0)
		

		esb = ttk.Scrollbar(frameExtension, orient="vertical", command=TreeExtension.yview)
		TreeExtension.configure(yscrollcommand=esb.set)
		esb.grid(column=0,row=0,sticky='nse')

		GPU = radvar.get()

		for i in range(GPUcount):
			if GPU == i :
				os.system("cat vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkQueueFamilyProperties/{flag=0}flag'|awk '/Device Extensions/{flag=1; next}/VkQueueFamilyProperties/{flag=0} flag' | grep VK_ | sort > VKDExtensions1.txt"%i)
					
		os.system("cat VKDExtensions1.txt | awk '{gsub(/:.*/,'True');print} ' > VKDExtensions.txt")
		
		# This should take care of further versioning till 100
		with open("VKDExtensions1.txt","r") as file1:
			value = []
			for line in file1:
				for j in range(RANGE1):
					if ": extension revision  %d"%j in line:
						value.append("0.0.%d"%j)
						break
					if ": extension revision %2d"%j in line:
						value.append("0.0.%2d"%j)
						break

		try:
			with open("VKDExtensions.txt","r") as file1:
				count = len(file1.readlines())
				tabcontrol.tab(3,text="Extensions(%d)"%count)
				file1.seek(0,0)
				i = 0
				for line in file1:
					TreeExtension.insert('','end',values=(line,value[i]),tags=i)
					if i % 2 != 0:
						TreeExtension.tag_configure(i,background=COLOR1)
					i = i + 1			
		except Exception as e:
			raise e
		
	def Format():

		frameFormat = ttk.LabelFrame(FormatTab,text="Device Formats",padding=PAD1)
		frameFormat.grid(column=0,row=0)
		cols = ('Formats','Linear','Optimal','Buffer')
		TreeFormat = ttk.Treeview(frameFormat,columns=cols,show="headings",height=HT)
		TreeFormat.column('Formats',width=545,anchor='sw')
		TreeFormat.column("Linear",width=WIDTH3,anchor=ANCHOR1)
		TreeFormat.column("Optimal",width=WIDTH3,anchor=ANCHOR1)
		TreeFormat.column("Buffer",width=WIDTH3,anchor=ANCHOR1)
		for each in cols:
			TreeFormat.heading(each,text=each,command=lambda each_=each: treeview_sort_column(TreeFormat, each_, True))

		TreeFormat.grid(column=0,row=0)
		
		vsb = ttk.Scrollbar(frameFormat, orient="vertical", command=TreeFormat.yview)
		TreeFormat.configure(yscrollcommand=vsb.set)
		vsb.grid(column=0,row=0,sticky='nse')


		GPU = radvar.get()

		for i in range(GPUcount):
			if GPU == i :
				os.system("cat vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | grep ^FORMAT_   > VKDFORMATS.txt"%i)
				os.system("cat vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /linearTiling.*/{f=1}'> VKDFORMATSlinear.txt"%i)
				os.system("cat vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /optimalTiling.*/{f=1}'> VKDFORMATSoptimal.txt"%i)
				os.system("cat vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /bufferFeatures.*/{f=1}'> VKDFORMATSBuffer.txt"%i)

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
		try:
			with open("VKDFORMATS.txt","r") as file1:
				file1.seek(0,0)
				tabcontrol.tab(4,text="Formats(%d)"%Formats)
				i = 0
				for line in file1:
					TreeFormat.insert('','end',values=(line,linear[i],optimal[i],Buffer[i]),tags=i)
					if i % 2 != 0 :
						TreeFormat.tag_configure(i,background=COLOR1)
					i = i + 1			
		except Exception as e:
			raise e

	def MemoryTypes():

		cols = ('Types','Heap Index','Device_Local','Host_Visible','Host_Coherent','Host_Cached','Lazily_Allocated')
		frameType = ttk.LabelFrame(MemoryTypeTab,text="Memory Types",padding=PAD1)
		frameType.grid(column=0,row=0)
		TreeMemory = ttk.Treeview(frameType,columns=cols,show="headings",height=HT2)
		TreeMemory.column('Types',width=95,anchor=ANCHOR1)
		TreeMemory.column('Heap Index',width=WIDTH3,anchor=ANCHOR1)
		TreeMemory.column('Device_Local',width=120,anchor=ANCHOR1)
		TreeMemory.column('Host_Visible',width=120,anchor=ANCHOR1)
		TreeMemory.column('Host_Coherent',width=120,anchor=ANCHOR1)
		TreeMemory.column('Host_Cached',width=140,anchor=ANCHOR1)
		TreeMemory.column('Lazily_Allocated',width=150,anchor=ANCHOR1)
		for each in cols:
			TreeMemory.heading(each,text=each,command=lambda each_=each: treeview_sort_column(TreeMemory, each_, True))
		TreeMemory.grid(column=0,row=0)
		
		Mvsb = ttk.Scrollbar(frameType, orient="vertical", command=TreeMemory.yview)
		TreeMemory.configure(yscrollcommand=Mvsb.set)
		Mvsb.grid(column=0,row=0,sticky='nse')

		GPU = radvar.get()
		for i in range(GPUcount):
			if GPU == i :
				os.system("cat vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceFeatures:/{flag=0}flag'|awk '/VkPhysicalDeviceMemoryProperties:/{flag=1; next}/VkPhysicalDeviceFeatures:/{flag=0} flag' > VKDMemoryType.txt"%i)
			
		with open("VKDMemoryType.txt","r") as file1:
			heapIndex = []
			for line in file1:
				for j in range(RANGE1):
					if "heapIndex" in line:
						if "= %d"%j in line:
							heapIndex.append(j)
							break


		Device_Local = []
		Host_Visible = []
		Host_Coherent = []
		Host_Cached = []
		Lazily_Allocated = []
		Flags = []
		Mcount = 0

		with open("VKDMemoryType.txt","r") as file1:
			for line in file1:
				if "memoryTypes" in line:
					Mcount = Mcount + 1
				for i in range(32):
					if " %s:"%hex(i) in line:
						dec = int(hex(i),16)
						binary = bin(dec)[2:]
						for j in range(len(binary)):
							if binary[j] == '0':
								Flags.insert(j,"false")
							if binary[j] == '1':
								Flags.insert(j,"true")
						for j in range(5-len(binary)):
							Flags.insert(0,"false")
						for i in range(len(Flags)):
							if i == 0:
								Lazily_Allocated.append(Flags[i])
							elif i == 1 :
								Host_Cached.append(Flags[i])
							elif i == 2 :
								Host_Coherent.append(Flags[i])
							elif i == 3 :
								Host_Visible.append(Flags[i])
							elif i == 4 :
								Device_Local.append(Flags[i])

	
		try:
			for i in range(Mcount):
				TreeMemory.insert('','end',values=(i,heapIndex[i],Device_Local[i],Host_Visible[i],Host_Coherent[i],Host_Cached[i],Lazily_Allocated[i]),tags=(i))
				if i % 2 != 0:
					TreeMemory.tag_configure(i,background=COLOR1)
		except Exception as e:
			raise e
		finally:


			# Memory Heap Details to be populated
			cols = ('Heaps','Device Size','HEAP_DEVICE_LOCAL')
			frameHeap = ttk.LabelFrame(MemoryTypeTab,text="Memory Heaps",padding=PAD1)
			frameHeap.grid(column=0,row=1,pady=PAD1)
			TreeHeap = ttk.Treeview(frameHeap,columns=cols,show="headings",height=HT3)
			TreeHeap.column('Heaps',width=95,anchor=ANCHOR1)
			TreeHeap.column('Device Size',width=300,anchor=ANCHOR1)
			TreeHeap.column('HEAP_DEVICE_LOCAL',width=450,anchor=ANCHOR1)
			for each in cols:
				TreeHeap.heading(each,text=each,command=lambda each_=each: treeview_sort_column(TreeHeap, each_, True))
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
						for j in range(1024):
							for k in range(RANGE1):
								if "(%d.%02d GiB)"%(j,k) in line:
									size.append("%d.%02d GB"%(j,k))
									break
								elif "(%d.%02d MiB)"%(j,k) in line:
									size.append("%d.%02d MB"%(j,k))
									break
							

			try:
				for i in range(HCount):
					TreeHeap.insert('','end',values=(i,size[i],HEAP_DEVICE_LOCAL[i]),tags=(i))
					if i % 2 != 0:
						TreeHeap.tag_configure(i,background=COLOR1)

				tabcontrol.tab(5,text="Memory Types(%d) & Heaps(%d)"%(Mcount,HCount))
			except Exception as e:
				raise e
	
	def Queues():

		frameQueue = ttk.LabelFrame(QueueTab,text="Queues",padding=PAD1)
		frameQueue.grid(column=0,row=0)

		TreeQueue = ttk.Treeview(frameQueue,height=HT)
		TreeQueue['columns'] = ('count','bits','Gbit','Cbit','Tbit','sbit')
		TreeQueue.heading('#0',text="Queue Family")
		TreeQueue.column('#0',width=WIDTH3,anchor=ANCHOR1)
		
		TreeQueue.heading('count',text='Queue Count')
		TreeQueue.column('count',width=WIDTH3,anchor=ANCHOR1)
		TreeQueue.heading('bits',text="timestampValidBits")
		TreeQueue.column('bits',width=150,anchor=ANCHOR1)
		TreeQueue.heading('Gbit',text="GRAPHICS_BIT")
		TreeQueue.column('Gbit',width=105,anchor=ANCHOR1)
		TreeQueue.heading('Cbit',text='COMPUTE_BIT')
		TreeQueue.column('Cbit',width=110,anchor=ANCHOR1)
		TreeQueue.heading('Tbit',text="TRANSFER_BIT")
		TreeQueue.column('Tbit',width=110,anchor=ANCHOR1)
		TreeQueue.heading('sbit',text="SPARSE_BINDING_BIT",anchor='center')
		TreeQueue.column('sbit',width=170,anchor=ANCHOR1)
		TreeQueue.grid(column=0,row=0)

		Qvsb = ttk.Scrollbar(frameQueue, orient="vertical", command=TreeQueue.yview)
		TreeQueue.configure(yscrollcommand=Qvsb.set)
		Qvsb.grid(column=0,row=0,sticky='nse')


		GPU = radvar.get()
		for i in range(GPUcount):
			if GPU == i :
				os.system("cat vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceMemoryProperties:/{flag=0}flag'|awk '/VkQueue.*/{flag=1; next}/VkPhysicalDeviceMemoryProperties:/{flag=0} flag' > VKDQueues.txt"%i)

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

		try:
			for i in range(count):
				TreeQueue.insert('','end',text=i,values=(qCount[i],qBits[i],GBit[i],CBit[i],TBit[i],SBit[i]),tags=i)
				if i % 2 != 0:
					TreeQueue.tag_configure(i,background=COLOR1)
			tabcontrol.tab(6,text="Queue Families(%d)"%count)
		except Exception as e:
			raise e
	
	def Instance():

	
		os.system("cat vulkaninfo.txt | awk '/Instance Extensions	count.*/{flag=1;next}/Layers: count.*/{flag=0}flag'| grep VK_ | sort > VKDInstanceExtensions1.txt")
		os.system("cat VKDInstanceExtensions1.txt | awk '{gsub(/:.*/,'True');print} ' > VKDInstanceExtensions.txt")
		
		frame1 = ttk.LabelFrame(InstanceTab,text="Instance Extensions",padding=PAD1)
		frame1.grid(column=0,row=0)	
		frame2 = ttk.LabelFrame(InstanceTab,text="Layers",padding=PAD1)
		frame2.grid(column=0,row=1,pady=PAD1)
		
		TreeInstance = ttk.Treeview(frame1, height=HT2)
		TreeInstance.heading("#0", text='Instance Extensions')
		TreeInstance.column('#0',width=WIDTH1,anchor=ANCHOR1)
		TreeInstance['column'] = ('version')
		TreeInstance.grid(column=0,row=0)
		TreeInstance.heading('version',text="Version")
		TreeInstance.column('version',width=WIDTH2,anchor=ANCHOR1)

		Isb = ttk.Scrollbar(frame1, orient="vertical", command=TreeInstance.yview)
		TreeInstance.configure(yscrollcommand=Isb.set)
		Isb.grid(column=0,row=0,sticky='nse')

		# This should take care of further versioning till 100
		with open("VKDInstanceExtensions1.txt","r") as file1:
			value = []
			for line in file1:
				for j in range(RANGE1):
					if ": extension revision  %d"%j in line:
						value.append("0.0.%d"%j)
						break
					if ": extension revision %2d"%j in line:
						value.append("0.0.%2d"%j)
						break
		try:
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
		except Exception as e:
			raise e
		finally:
			os.system("rm VKDInstanceExtensions*.txt")

			TreeLayer = ttk.Treeview(frame2,height=HT3)
			TreeLayer['columns'] =('value1','value2','value3')
			TreeLayer.heading('#0',text='Instance Layers')
			TreeLayer.column('#0',width=450,anchor=ANCHOR1)
			TreeLayer.heading('value1',text='Vulkan Version')
			TreeLayer.column('value1',width=120,anchor=ANCHOR1)
			TreeLayer.heading('value2',text="Layer Version")
			TreeLayer.column('value2',width=120,anchor=ANCHOR1)
			TreeLayer.heading('value3',text='Extension Count')
			TreeLayer.column('value3',width=150,anchor=ANCHOR1)
			TreeLayer.grid(column=0,row=1)

			lsb = ttk.Scrollbar(frame2, orient="vertical", command=TreeLayer.yview)
			TreeLayer.configure(yscrollcommand=lsb.set)
			lsb.grid(column=0,row=1,sticky='nse')

			os.system("cat vulkaninfo.txt | awk '/Layers: count.*/{flag=1;next}/Presentable Surfaces.*/{flag=0}flag' > VKDLayer1.txt")
			os.system("cat VKDLayer1.txt | grep _LAYER_ | awk '{gsub(/\(.*/,'True');print} ' > VKDLayer.txt")

			Vversion = []
			with open("VKDLayer1.txt","r") as file1:
				for line in file1:
					for j in range(RANGE1):
						if "Vulkan version 1.0.%d,"%j in line:
							Vversion.append("1.0.%d"%j)
							
						


			LVersion = []
			with open("VKDLayer1.txt","r") as file1:
				for line in file1:
					for j in range(RANGE1):
						if "layer version %d"%j in line:
							LVersion.append("0.0.%d"%j)
							break

			ECount = []
			with open("VKDLayer1.txt","r") as file1:
				for line in file1:
					for j in range(RANGE1):
						if "Layer Extensions	count = %d"%j in line:
							ECount.append("%d"%j)
							break



			try:
				count2 = len(LVersion)
				tabcontrol.tab(7,text="Instances(%d) & Layers(%d)"%(count1,count2))
				with open("VKDLayer.txt","r") as file1:
					i = 0
					for line in file1:
						TreeLayer.insert('','end',text=line,values=(Vversion[i],LVersion[i],ECount[i]),tags=i)
						if i % 2 != 0:
							TreeLayer.tag_configure(i,background=COLOR1)
						i = i + 1						
			except Exception as e:
				raise e
	
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
		os.system("rm VKD*.txt")


	frame1 = ttk.LabelFrame(tab2,text="")
	frame1.grid(column=0,row=0)
	os.system("cat vulkaninfo.txt | grep Name | grep -o  =.* | grep -o ' .*' > GPU.txt")

	with open("GPU.txt","r") as file2:
		GPUcount=len(file2.readlines())
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
		if i > 1:
			GPU.grid(column=2,row=i-2)


	os.system("rm GPU.txt")
	
