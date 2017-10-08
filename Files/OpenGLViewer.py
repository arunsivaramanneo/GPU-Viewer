import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Toplevel
from Framebuffer import FrameBuffer
from tkinter import messagebox
import os


COLOR1 = "GRAY91" # even number line background
COLOR2 = "BLUE"   # Extensions count foreground color

def OpenGL(tab1):



# Creating the first Frame to display the OpenGL Version Core and String details along with Hardware 

	frame1 = ttk.LabelFrame(tab1, text="OpenGL Information",padding=10)
	frame1.grid(column=0,row=0, padx=20, pady=10)


	frame2 = ttk.LabelFrame(tab1, text="Extensions ")
	frame2.grid(column=0,row=1,padx=20, sticky=tk.W)

	frame3 = ttk.LabelFrame(tab1,padding=5)
	frame3.grid(column=0,row=2,padx=20, sticky=tk.W)

	frame4 = ttk.LabelFrame(tab1, text="",width=900,padding=10)
	frame4.grid(column=0,row=4)

	

	os.system("glxinfo | grep string | grep -v glx > OpenGL_Information.txt")
	os.system("cat OpenGL_Information.txt | grep -o :.* | grep -o ' .*' > OpenGLRHS.txt")
	os.system("cat OpenGL_Information.txt | awk '{gsub(/string.*/,'True');print}' > OpenGLLHS.txt")

	TreeGL = ttk.Treeview(frame1,height=9)
	TreeGL ['columns'] = ('values')
	#TreeGL.heading('#0',text='')
	TreeGL.column('#0',width=460, anchor="sw")
	#TreeGL.heading('values',text="")
	TreeGL.column('values',width=450)

	TreeGL.grid(column=0,row=0)


	with open("OpenGLRHS.txt","r") as file1:
		value = []
		for line in file1:
			value.append(line)

	with open("OpenGLLHS.txt","r") as file1:
		i = 0
		for line in file1:
			TreeGL.insert('','end',text=line,values=(value[i],),tag=i)
			if i % 2 != 0:
				TreeGL.tag_configure(i,background=COLOR1)
			i = i + 1


	
# Creating a new window for OpenGL Limits
	def clickMe():
		win2 = Toplevel()
		win2.title("OpenGL Limits")
		win2.resizable(0,0)
		frame5 = ttk.LabelFrame(win2,text="OpenGL hardware limits",padding=10)
		frame5.grid(column=0,row=0, padx=20,pady=10)

	
		os.system("glxinfo -l | awk '/OpenGL limits:/{flag=1}/GLX Visuals.*/{flag=0} flag' | awk '/OpenGL limits:/{flag=1;next}/OpenGL ES profile/{flag=0} flag' | grep = > OpenGL_Limits.txt")
		
		#sc4 = scrolledtext.ScrolledText(win2, width=80, height=10)
		cols = ('value1','value2','value3','value4')
		TreeGLLimits = ttk.Treeview(frame5,columns=cols,show="headings",height=15)
		TreeGLLimits.heading('value1',text="OpenGL hardware limits")
		TreeGLLimits.column('value1',width=700)
		TreeGLLimits.heading('value3',text="Va",anchor="se")
		TreeGLLimits.column('value3',width=100,anchor="se")
		TreeGLLimits.heading('value4',text="lue",anchor="sw")
		TreeGLLimits.column('value4',width=100,anchor='sw')
		TreeGLLimits.grid(column=0,row=0)
		TreeGLLimits["displaycolumns"] = ('value1','value3','value4')

		lsb = ttk.Scrollbar(frame5, orient="vertical", command=TreeGLLimits.yview)
		TreeGLLimits.configure(yscrollcommand=lsb.set)
		lsb.grid(column=0,row=0,sticky='nse')

		limits = []
	
		with open("OpenGL_Limits.txt","r") as file3:
			i = 0
			for line in file3:
				limits.append(line)

		for i in range(len(limits)):
			TreeGLLimits.insert('','end',values=limits[i],tags=i)
			if i % 2 != 0:
				TreeGLLimits.tag_configure(i,background=COLOR1)
			
			if "=" not in limits[i]:
				TreeGLLimits.tag_configure(i,foreground=COLOR2,background="GRAY70")
			i = i + 1
		

		os.system("rm OpenGL_Limit*.txt")
	
		win2.mainloop()
		

# Adding a Button for OpenGL Limits
	Button_limits =  ttk.Button(frame1, text="Show OpenGL Limits", command=clickMe)
	Button_limits.grid(column=0,row=1,padx=5,pady=10, sticky=tk.W)

	Button_FrameBuffer = ttk.Button(frame1,text="Show GLX Frame Buffer Configuration",command=FrameBuffer)
	Button_FrameBuffer.grid(column=0,row=1,pady=10)
	

	

# Configuring different Radio Buttons
	
	radvar = tk.IntVar()
	radvar1 = tk.IntVar()

	def Radio():

		for i in frame3.winfo_children():
			i.destroy()

		os.system("cat extensions.txt | awk 'gsub(/GL_|_.*/,'true')'| uniq > Vendor.txt")


		vCount = []
		vendorList = []
		with open("Vendor.txt","r") as file1:
			for line in file1:
				vendorList.append(line)

	
		vendorList = [i.strip(' ') for i in vendorList]
		vendorList = [i.strip('\n ') for i in vendorList]
		vendorList.insert(0,"ALL")

		radsel1 = radvar1.get()

		if radsel1 == 1:
			frame3.configure(text="OpenGL")
		elif radsel1 == 2:
			frame3.configure(text="OpenGL ES")
		
		with open("extensions.txt","r") as file1:
			for i in range(len(vendorList)):
				file1.seek(0,0)
				GL_All = []
				for line in file1:
					if vendorList[i] == "ALL":
						GL_All.append(line)
					elif vendorList[i] != "ALL" and vendorList[i] != "GLX" :
						if "_%s_"%vendorList[i] in line :
							GL_All.append(line)
					elif vendorList[i] == "GLX":
						if "GLX_" in line:
							GL_All.append(line)
				vCount.append(len(GL_All))


		j = 0
		for i in range(len(vendorList)):

			rad = tk.Radiobutton(frame3, text="%s(%d)"%(vendorList[i],vCount[i]), variable=radvar, value=i,font=('Helvetica',11),command=radcall)
			
			if len(vendorList) <= 9:
				rad.grid(column=i,row=2,pady=12,sticky=tk.W)
			else:
				rad.grid(column=i,row=2,pady=2,sticky=tk.W)
				if i > 9:
					rad.grid(column=j,row=3, sticky=tk.W)
					j = j + 1
			if i == 0:
				rad.invoke()
		
	

	def select():
		radsel1 = radvar1.get()
	
		if radsel1 == 1:
			os.system("glxinfo -s | awk '/OpenGL extensions/{flag=1;next}/OpenGL ES profile/{flag=0} flag' | grep GL_ | sort > extensions.txt")
			os.system("glxinfo -s | awk '/client glx extensions/{flag=1; next}/GLX version/{flag=0} flag' | grep GLX_ | sort >> extensions.txt")
			
			
		if radsel1 == 2:
			os.system("glxinfo -s | awk '/OpenGL ES profile/{flag=1;next}/80 GLX Visuals/{flag=0} flag' | grep GL_ | sort > extensions.txt")
			
		
		Radio()
		radcall()
		

	def radcall():

		GL_All = []
		List = []

		radsel=radvar.get()


		with open("Vendor.txt","r") as file1:
			for line in file1:
				List.append(line)

		List = [i.strip(' ') for i in List]
		List = [i.strip('\n ') for i in List]
		List.insert(0," ALL")
	
		with open("extensions.txt","r") as file1:
			for line in file1:
				if List[radsel] == " ALL":
					GL_All.append(line)
				elif List[radsel] != " ALL" and List[radsel] != "GLX" :
					if "_%s_"%List[radsel] in line:
						GL_All.append(line)
				elif List[radsel] == "GLX":
					if "GLX_" in line:
						GL_All.append(line)
		
		TreeGLAll = ttk.Treeview(frame4,height=17)
		TreeGLAll.column('#0',width=910)
		TreeGLAll.grid(column=0,row=2)

		Allsb = ttk.Scrollbar(frame4, orient="vertical", command=TreeGLAll.yview)
		TreeGLAll.configure(yscrollcommand=Allsb.set)
		Allsb.grid(column=0,row=2,sticky='nse')

		for i in range(len(List)):
			if radsel == i:
				frame4.configure(text=List[i]) 
				count = len(GL_All)
				for i in range(count):
					TreeGLAll.insert('','end',text=GL_All[i].strip(' '),tags=i)
					if i % 2 != 0:
						TreeGLAll.tag_configure(i,background=COLOR1)
				

		

	with open("OpenGLLHS.txt","r") as file1:
		OpenGLrad = tk.Radiobutton(frame2,text="OpenGL", variable=radvar1, value=1,font=('Helvetica',11),command=select)
		OpenGLrad.grid(column=0,row=1)
		OpenGLrad.invoke()
		for line in file1:
			if "OpenGL ES" in line:
				OpenGLESrad = tk.Radiobutton(frame2,text="OpenGL ES", variable=radvar1, value=2,font=('Helvetica',11),command=select)
				OpenGLESrad.grid(column=1,row=1)

	os.system("rm OpenGL*.txt")

	










