import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Toplevel
import os


COLOR1 = "GRAY91" # even number line background
COLOR2 = "BLUE"   # Extensions count foreground color

def OpenGL(tab1):



# Creating the first Frame to display the OpenGL Version Core and String details along with Hardware 

	frame1 = ttk.LabelFrame(tab1, text="OpenGL Information",padding=10)
	frame1.grid(column=0,row=0, padx=20, pady=10)


	frame2 = ttk.LabelFrame(tab1, text="Extensions ")
	frame2.grid(column=0,row=1,padx=20, sticky=tk.W)

	frame3 = ttk.LabelFrame(tab1, text=" ")
	frame3.grid(column=0,row=2,padx=20, sticky=tk.W)

	frame4 = ttk.LabelFrame(tab1, text="",padding=10)
	frame4.grid(column=0,row=4)

	

	os.system("glxinfo | grep string | grep -v glx > OpenGL_Information.txt")
	os.system("cat OpenGL_Information.txt | grep -o :.* | grep -o ' .*' > OpenGLRHS.txt")
	os.system("cat OpenGL_Information.txt | awk '{gsub(/string.*/,'True');print}' > OpenGLLHS.txt")

	TreeGL = ttk.Treeview(frame1,height=9)
	TreeGL ['columns'] = ('values')
	#TreeGL.heading('#0',text='')
	TreeGL.column('#0',width=500, anchor="s")
	#TreeGL.heading('values',text="")
	TreeGL.column('values',width=350)

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


	os.system("rm OpenGL*.txt")
# Creating a new window for OpenGL Limits

	def clickMe():
		win2 = Toplevel()
		win2.title("OpenGL Limits")
		win2.resizable(0,0)
		frame5 = ttk.LabelFrame(win2,padding=10)
		frame5.grid(column=0,row=0, padx=20,pady=10)

		
		os.system("glxinfo -l | awk '/OpenGL limits:/{flag=1;next}/OpenGL ES profile/{flag=0} flag' > OpenGL_Limits.txt")
		

		#sc4 = scrolledtext.ScrolledText(win2, width=80, height=10)

		TreeGLLimits = ttk.Treeview(frame5,height=15)
		TreeGLLimits.heading('#0',text="OpenGL Limits")
		TreeGLLimits.column('#0',width=800)
		TreeGLLimits.grid(column=0,row=0)

		lsb = ttk.Scrollbar(frame5, orient="vertical", command=TreeGLLimits.yview)
		TreeGLLimits.configure(yscrollcommand=lsb.set)
		lsb.grid(column=0,row=0,sticky='nse')

	
		with open("OpenGL_Limits.txt","r") as file3:
			i = 0
			for line in file3:
				TreeGLLimits.insert('','end',text=line,tags=i)
				if i % 2 != 0:
					TreeGLLimits.tag_configure(i,background=COLOR1)
				i = i + 1
			

		os.system("rm OpenGL_Limit*.txt")
		win2.mainloop()
		

# Adding a Button for OpenGL Limits
	Button_limits =  ttk.Button(frame1, text="OpenGL Limits", command=clickMe)
	Button_limits.grid(column=0,row=1,padx=5, pady=10, sticky=tk.W)
	

	

# Configuring different Radio Buttons
	
	radvar = tk.IntVar()
	radvar1 = tk.IntVar()

	def Radio():

		
		rad1 = tk.Radiobutton(frame3, text="All", variable=radvar, value=1, command=radcall)
		rad1.grid(column=0,row=2,sticky = tk.W)
		rad1.invoke()
		rad2 = tk.Radiobutton(frame3, text="AMD", variable=radvar, value=2, command=radcall)
		rad2.grid(column=1,row=2,sticky=tk.W)
		rad3 = tk.Radiobutton(frame3, text="ARB", variable=radvar, value=3, command=radcall)
		rad3.grid(column=2,row=2,sticky=tk.W)
		rad4 = tk.Radiobutton(frame3, text="ATI", variable=radvar, value=6, command=radcall)
		rad4.grid(column=3,row=2,sticky=tk.W)
		rad5 = tk.Radiobutton(frame3, text="EXT", variable=radvar, value=4, command=radcall)
		rad5.grid(column=4,row=2,sticky=tk.W)
		rad6 = tk.Radiobutton(frame3, text="IBM", variable=radvar, value=11, command=radcall)
		rad6.grid(column=5,row=2,sticky=tk.W)
		rad7 = tk.Radiobutton(frame3, text="KHR", variable=radvar, value=7, command=radcall)
		rad7.grid(column=6,row=2,sticky=tk.W)
		rad8 = tk.Radiobutton(frame3, text="MESA", variable=radvar, value=8, command=radcall)
		rad8.grid(column=7,row=2,sticky=tk.W)
		rad9 = tk.Radiobutton(frame3, text="NV", variable=radvar, value=5, command=radcall)
		rad9.grid(column=8,row=2,sticky=tk.W)
		rad10 = tk.Radiobutton(frame3, text="SGI", variable=radvar, value=9, command=radcall)
		rad10.grid(column=9,row=2,sticky=tk.W)
		rad11 = tk.Radiobutton(frame3,text="OES", variable=radvar, value=12, command=radcall)
		rad11.grid(column=10,row=2,sticky=tk.W)
		rad12 = tk.Radiobutton(frame3, text="Others", variable=radvar, value=10, command=radcall)
		rad12.grid(column=11,row=2, sticky=tk.W)
	

	def select():
		radsel1 = radvar1.get()

		if radsel1 == 1:
			os.system("glxinfo -s | awk '/OpenGL extensions/{flag=1;next}/OpenGL ES profile/{flag=0} flag' | grep GL_ | sort > extensions.txt")
			os.system("glxinfo -s | awk '/client glx extensions/{flag=1; next}/GLX version/{flag=0} flag' | grep GLX_ | sort >> extensions.txt")
			Radio()
			
		if radsel1 == 2:
			os.system("glxinfo -s | awk '/OpenGL ES profile/{flag=1;next}/80 GLX Visuals/{flag=0} flag' | grep GL_ | sort > extensions.txt")
			Radio()

		
		radcall()



	def radcall():

		GL_All = []
		GL_ARB = []
		GL_AMD = []
		GL_ATI = []
		GL_EXT = []
		GL_IBM = []
		GL_KHR = []
		GL_SGI = []
		GL_NV = []
		GL_MESA =[]
		GL_OES = []
		GL_Others = []

		with open("extensions.txt") as file1:
			for line in file1:
				if "_ARB" in line:
					GL_ARB.append(line)
					GL_All.append(line)
				elif "_AMD" in line:
					GL_AMD.append(line)
					GL_All.append(line)
				elif "_NV" in line:
					GL_NV.append(line)
					GL_All.append(line)
				elif "_MESA" in line:
					GL_MESA.append(line)
					GL_All.append(line)
				elif "_EXT" in line:
					GL_EXT.append(line)
					GL_All.append(line)
				elif "_IBM" in line:
					GL_IBM.append(line)
					GL_All.append(line)
				elif "_SGI" in line:
					GL_SGI.append(line)
					GL_All.append(line)
				elif "_KHR" in line:
					GL_KHR.append(line)
					GL_All.append(line)
				elif "_ATI" in line:
					GL_ATI.append(line)
					GL_All.append(line)
				elif "_OES" in line:
					GL_OES.append(line)
					GL_All.append(line)
				else:
					GL_Others.append(line)
					GL_All.append(line)
		
		radsel=radvar.get()
		label1 = ttk.Label(frame3, text="No :")
		label1.grid(column=0,row=4)
		TotExt = ttk.Entry(frame3, width=5)
		TotExt.grid(column=1,row=4)
		TreeGLAll = ttk.Treeview(frame4,height=16)
		TreeGLAll.column('#0',width=850)
		TreeGLAll.grid(column=0,row=2)

		Allsb = ttk.Scrollbar(frame4, orient="vertical", command=TreeGLAll.yview)
		TreeGLAll.configure(yscrollcommand=Allsb.set)
		Allsb.grid(column=0,row=2,sticky='nse')

		if radsel == 1:
			frame4.configure(text="All") 
			count = len(GL_All)
			TotExt.insert('insert',count)
			TotExt.configure(state='disabled',foreground=COLOR2)
			if count > 0:
				for i in range(count):
					TreeGLAll.insert('','end',text=GL_All[i],tags=i)
					if i % 2 != 0:
						TreeGLAll.tag_configure(i,background=COLOR1)

			else:
				TreeGLAll.insert('','end',text="No extensions available")
					

		if radsel == 2:
			
			frame4.configure(text="AMD")
			count = len(GL_AMD)
			TotExt.insert('insert',count)
			TotExt.configure(state='disabled',foreground=COLOR2)
			if count > 0:
				for i in range(count):
					TreeGLAll.insert('','end',text=GL_AMD[i],tags=i)
					if i % 2 != 0:
						TreeGLAll.tag_configure(i,background=COLOR1)
			else:
				TreeGLAll.insert('','end',text="No extensions available")

		if radsel == 3:
			
			frame4.configure(text="ARB")
			count = len(GL_ARB)
			TotExt.insert('insert',count)
			TotExt.configure(state='disabled',foreground=COLOR2)
			if count > 0:
				for i in range(count):
					TreeGLAll.insert('','end',text=GL_ARB[i],tags=i)
					if i % 2 != 0:
						TreeGLAll.tag_configure(i,background=COLOR1)
			else:
				TreeGLAll.insert('','end',text="No extensions available")

		if radsel == 4:
		
			frame4.configure(text="EXT")
			
			count = len(GL_EXT)
			TotExt.insert('insert',count)
			TotExt.configure(state='disabled',foreground=COLOR2)
			if count > 0:
				for i in range(count):
					TreeGLAll.insert('','end',text=GL_EXT[i],tags=i)
					if i % 2 != 0:
						TreeGLAll.tag_configure(i,background=COLOR1)
			else:
				TreeGLAll.insert('','end',text="No extensions available")


		if radsel == 5:
			
			frame4.configure(text="NV")
			count = len(GL_NV)
			TotExt.insert('insert',count)
			TotExt.configure(state='disabled',foreground=COLOR2)
			if count > 0 :
				for i in range(count):
					TreeGLAll.insert('','end',text=GL_NV[i],tags=i)
					if i % 2 != 0:
						TreeGLAll.tag_configure(i,background=COLOR1)
			else:
				TreeGLAll.insert('','end',text="No extensions available")


		if radsel == 6:
			
			frame4.configure(text="ATI")
			count = len(GL_ATI)
			TotExt.insert('insert',count)
			TotExt.configure(state='disabled',foreground=COLOR2)
			if count > 0:
				for i in range(count):
					TreeGLAll.insert('','end',text=GL_ATI[i],tags=i)
					if i % 2 != 0:
						TreeGLAll.tag_configure(i,background=COLOR1)
			else:
				TreeGLAll.insert('','end',text="No extensions available")

		if radsel == 7:

			frame4.configure(text="KHR")
			count = len(GL_KHR)
			TotExt.insert('insert',count)
			TotExt.configure(state='disabled',foreground=COLOR2)
			if count > 0:
				for i in range(count):
					TreeGLAll.insert('','end',text=GL_KHR[i],tags=i)
					if i % 2 != 0:
						TreeGLAll.tag_configure(i,background=COLOR1)
			else:
				TreeGLAll.insert('','end',text="No extensions available")


		if radsel == 8:
			
			frame4.configure(text="MESA")
			count = len(GL_MESA)
			TotExt.insert('insert',count)
			TotExt.configure(state='disabled',foreground=COLOR2)
			if count > 0:
				for i in range(count):
					TreeGLAll.insert('','end',text=GL_MESA[i],tags=i)
					if i % 2 != 0:
						TreeGLAll.tag_configure(i,background=COLOR1)
			else:
				TreeGLAll.insert('','end',text="No extensions available")
				

		if radsel == 10:
			
			frame4.configure(text="Other extensions") 
			count = len(GL_Others)
			TotExt.insert('insert',count)
			TotExt.configure(state='disabled',foreground=COLOR2)
			if count > 0:
				for i in range(count):
					TreeGLAll.insert('','end',text=GL_Others[i],tags=i)
					if i % 2 != 0:
						TreeGLAll.tag_configure(i,background=COLOR1)
			else:
				TreeGLAll.insert('','end',text="No extensions available")
					
		if radsel == 9:
			
			frame4.configure(text="SGI/SGIX")
			
			count = len(GL_SGI)
			TotExt.insert('insert',count)
			TotExt.configure(state='disabled',foreground=COLOR2)
			if count > 0:
				for i in range(count):
					TreeGLAll.insert('','end',text=GL_SGI[i],tags=i)
					if i % 2 != 0:
						TreeGLAll.tag_configure(i,background=COLOR1)
			else:
				TreeGLAll.insert('','end',text="No extensions available")

		if radsel == 11:

			frame4.configure(text="IBM")
		
			count = len(GL_IBM)
			TotExt.insert('insert',count)
			TotExt.configure(state='disabled',foreground=COLOR2)
			if count > 0:
				for i in range(count):
					TreeGLAll.insert('','end',text=GL_IBM[i],tags=i)
					if i % 2 != 0:
						TreeGLAll.tag_configure(i,background=COLOR1)
			else:
				TreeGLAll.insert('','end',text="No extensions available")
				
		if radsel == 12:

			frame4.configure(text="OES")
			count = len(GL_OES)
			TotExt.insert('insert',count)
			TotExt.configure(state='disabled',foreground=COLOR2)
			if count > 0:
				for i in range(count):
					TreeGLAll.insert('','end',text=GL_OES[i],tags=i)
					if i % 2 != 0:
						TreeGLAll.tag_configure(i,background=COLOR1)
			else:
				TreeGLAll.insert('','end',text="No extensions available")



	OpenGLrad = tk.Radiobutton(frame2,text="OpenGL", variable=radvar1, value=1,command=select)
	OpenGLrad.grid(column=0,row=1)
	OpenGLrad.invoke()

	OpenGLESrad = tk.Radiobutton(frame2,text="OpenGL ES", variable=radvar1, value=2,command=select)
	OpenGLESrad.grid(column=1,row=1)









