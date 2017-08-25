import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import os


def OpenGL(tab1):



# Creating the first Frame to display the OpenGL Version Core and String details along with Hardware 

	frame1 = ttk.LabelFrame(tab1, text="OpenGL Information")
	frame1.grid(column=0,row=0, padx=20, pady=20)


	frame2 = ttk.LabelFrame(tab1, text="Extensions ")
	frame2.grid(column=0,row=1,padx=20, sticky=tk.W)

	frame3 = ttk.LabelFrame(tab1, text=" ")
	frame3.grid(column=0,row=2,padx=20, sticky=tk.W)

	frame4 = ttk.LabelFrame(tab1, text="")
	frame4.grid(column=0,row=4)

	

	os.system("glxinfo | grep string | grep -v glx > OpenGL_Information.txt")
	os.system("cat OpenGL_Information.txt | grep -o :.* | grep -o ' .*' > OpenGLRHS.txt")
	os.system("cat OpenGL_Information.txt | awk '{gsub(/string.*/,'True');print}' > OpenGLLHS.txt")

	TreeGL = ttk.Treeview(frame1,height=9)
	TreeGL ['columns'] = ('values')
	#TreeGL.heading('#0',text='')
	TreeGL.column('#0',width=400, anchor="s")
	#TreeGL.heading('values',text="")
	TreeGL.column('values',width=325)

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
				TreeGL.tag_configure(i,background="GRAY91")
			i = i + 1


	os.system("rm OpenGL*.txt")
# Creating a new window for OpenGL Limits

	def clickMe():
		win2 = tk.Tk()
		win2.title("OpenGL Limits")
		win2.resizable(0,0)

		frame5 = ttk.LabelFrame(tab1, text="OpenGL Limits")
		frame5.grid(column=0,row=0, padx=20,pady=20)

		
		os.system("glxinfo -l | awk '/OpenGL limits:/{flag=1;next}/OpenGL ES profile/{flag=0} flag' > OpenGL_Limits.txt")

		sc4 = scrolledtext.ScrolledText(win2, width=80, height=10)

		with open("OpenGL_Limits.txt","r") as file3:
			for line in file3:
				sc4.insert('insert',line)
				sc4.grid(column=0,row=0)

		sc4.configure(state="disabled",foreground="BLUE")
# Adding a Button for OpenGL Limits
	Button_limits =  ttk.Button(frame1, text="OpenGL Limits", command=clickMe)
	Button_limits.grid(column=0,row=1,padx=5, pady=10, sticky=tk.W)


# Configuring different Radio Buttons
	
	radvar = tk.IntVar()
	radvar1 = tk.IntVar()

	def select():
		radsel1 = radvar1.get()

		if radsel1 == 1:
			os.system("glxinfo -s | awk '/OpenGL extensions/{flag=1;next}/OpenGL ES profile/{flag=0} flag' | grep GL_ | sort > extensions.txt")
			os.system("glxinfo -s | awk '/client glx extensions/{flag=1; next}/GLX version/{flag=0} flag' | grep GLX_ | sort >> extensions.txt")
			radcall()
		if radsel1 == 2:
			os.system("glxinfo -s | awk '/OpenGL ES profile/{flag=1;next}/80 GLX Visuals/{flag=0} flag' | grep GL_ | sort > extensions.txt")
			radcall()


	def radcall():
		
		radsel=radvar.get()
		label1 = ttk.Label(frame3, text="No :")
		label1.grid(column=0,row=4)
		TotExt = ttk.Entry(frame3, width=5)
		TotExt.grid(column=1,row=4)
		TreeGLAll = ttk.Treeview(frame4,height=15)
		TreeGLAll.column('#0',width=725)
		TreeGLAll.grid(column=0,row=2)

		Allsb = ttk.Scrollbar(frame4, orient="vertical", command=TreeGLAll.yview)
		TreeGLAll.configure(yscrollcommand=Allsb.set)
		Allsb.grid(column=0,row=2,sticky='nse')

		if radsel == 1:
			frame4.configure(text="All") 
			with open("extensions.txt") as file2:
				count = len(file2.readlines())
				TotExt.insert('insert',count)
				TotExt.configure(state='disabled',foreground="BLUE")
				file2.seek(0,0)
				i = 0
				if count  > 0:
					for line in file2:
						TreeGLAll.insert('','end',text=line,tags=i)
						if i % 2 != 0:
							TreeGLAll.tag_configure(i,background="GRAY91")
						i = i + 1
				else:
					TreeGLAll.insert('','end',text="No extensions available")

					


		if radsel == 2:
			os.system("cat extensions.txt | grep _AMD > AMD_extensions.txt")
			
			frame4.configure(text="AMD")
			with open("AMD_extensions.txt") as file2:
				count = len(file2.readlines())
				TotExt.insert('insert',count)
				TotExt.configure(state='disabled',foreground="BLUE")
				file2.seek(0,0)
				i = 0
				if count  > 0:
					for line in file2:
						TreeGLAll.insert('','end',text=line,tags=i)
						if i % 2 != 0:
							TreeGLAll.tag_configure(i,background="GRAY91")
						i = i + 1
				else:
					TreeGLAll.insert('','end',text="No extensions available")

				os.system("rm AMD*.txt")

		if radsel == 3:
			os.system("cat extensions.txt | grep _ARB > ARB_extensions.txt")
			#os.system("sort extensions1.txt | uniq > extensions.txt")
			frame4.configure(text="ARB")
			
			with open("ARB_extensions.txt") as file2:
				count = len(file2.readlines())
				TotExt.insert('insert',count)
				TotExt.configure(state='disabled',foreground="BLUE")
				file2.seek(0,0)
				i = 0
				if count  > 0:
					for line in file2:
						TreeGLAll.insert('','end',text=line,tags=i)
						if i % 2 != 0:
							TreeGLAll.tag_configure(i,background="GRAY91")
						i = i + 1
				else:
					TreeGLAll.insert('','end',text="No extensions available")

				os.system("rm ARB*.txt")

		if radsel == 4:
			os.system("cat extensions.txt | grep _EXT > EXT_extensions.txt")
			#os.system("sort extensions1.txt | uniq > extensions.txt")
			frame4.configure(text="EXT")
			
			with open("EXT_extensions.txt") as file2:
				count = len(file2.readlines())
				TotExt.insert('insert',count)
				TotExt.configure(state='disabled',foreground="BLUE")
				file2.seek(0,0)
				i = 0
				if count  > 0:
					for line in file2:
						TreeGLAll.insert('','end',text=line,tags=i)
						if i % 2 != 0:
							TreeGLAll.tag_configure(i,background="GRAY91")
						i = i + 1
				else:
					TreeGLAll.insert('','end',text="No extensions available")

				os.system("rm EXT*.txt")

		if radsel == 5:
			os.system("cat extensions.txt | grep _NV > NV_extensions.txt")
			#os.system("sort extensions1.txt | uniq > extensions.txt")
			frame4.configure(text="NV")
			
			with open("NV_extensions.txt") as file2:
				count = len(file2.readlines())
				TotExt.insert('insert',count)
				TotExt.configure(state='disabled',foreground="BLUE")
				file2.seek(0,0)
				i = 0
				if count  > 0:
					for line in file2:
						TreeGLAll.insert('','end',text=line,tags=i)
						if i % 2 != 0:
							TreeGLAll.tag_configure(i,background="GRAY91")
						i = i + 1
				else:
					TreeGLAll.insert('','end',text="No extensions available")
				os.system("rm NV*.txt")

		if radsel == 6:
			os.system("cat extensions.txt | grep _ATI > ATI_extensions.txt")
			#os.system("sort extensions1.txt | uniq > extensions.txt")
			frame4.configure(text="ATI")
			
			with open("ATI_extensions.txt") as file2:
				count = len(file2.readlines())
				TotExt.insert('insert',count)
				TotExt.configure(state='disabled',foreground="BLUE")
				file2.seek(0,0)
				i = 0
				if count  > 0:
					for line in file2:
						TreeGLAll.insert('','end',text=line,tags=i)
						if i % 2 != 0:
							TreeGLAll.tag_configure(i,background="GRAY91")
						i = i + 1
				else:
					TreeGLAll.insert('','end',text="No extensions available")
				os.system("rm ATI*.txt")

		if radsel == 7:
			os.system("cat extensions.txt | grep _KHR > KHR_extensions.txt")
			#os.system("sort extensions1.txt | uniq > extensions.txt")
			frame4.configure(text="KHR")
			
			with open("KHR_extensions.txt") as file2:
				count = len(file2.readlines())
				TotExt.insert('insert',count)
				TotExt.configure(state='disabled',foreground="BLUE")
				file2.seek(0,0)
				i = 0
				if count  > 0:
					for line in file2:
						TreeGLAll.insert('','end',text=line,tags=i)
						if i % 2 != 0:
							TreeGLAll.tag_configure(i,background="GRAY91")
						i = i + 1
				else:
					TreeGLAll.insert('','end',text="No extensions available")

				os.system("rm KHR*.txt")

		if radsel == 8:
			os.system("cat extensions.txt | grep _MESA > MESA_extensions.txt")
			#os.system("sort extensions1.txt | uniq > extensions.txt")
			frame4.configure(text="MESA")
			
			with open("MESA_extensions.txt") as file2:
				count = len(file2.readlines())
				TotExt.insert('insert',count)
				TotExt.configure(state='disabled',foreground="BLUE")
				file2.seek(0,0)
				i = 0
				if count  > 0:
					for line in file2:
						TreeGLAll.insert('','end',text=line,tags=i)
						if i % 2 != 0:
							TreeGLAll.tag_configure(i,background="GRAY91")
						i = i + 1
				else:
					TreeGLAll.insert('','end',text="No extensions available")

				os.system("rm MESA*.txt")

		if radsel == 10:
			os.system("cat extensions.txt | grep -v _AMD | grep -v _MESA | grep -v _NV | grep -v _ATI | grep -v _ARB | grep -v _SGI | grep -v _KHR | grep -v _EXT | grep -v _IBM | grep -v _OES > Others_extensions.txt")
			frame4.configure(text="Other extensions") 
			with open("Others_extensions.txt") as file2:
				count = len(file2.readlines())
				TotExt.insert('insert',count)
				TotExt.configure(state='disabled',foreground="BLUE")
				file2.seek(0,0)
				i = 0
				if count  > 0:
					for line in file2:
						TreeGLAll.insert('','end',text=line,tags=i)
						if i % 2 != 0:
							TreeGLAll.tag_configure(i,background="GRAY91")
						i = i + 1
				else:
					TreeGLAll.insert('','end',text="No extensions available")
				os.system("rm Others*.txt")
	
		if radsel == 9:
			os.system("cat extensions.txt | grep _SGI > SGI_extensions.txt")
			frame4.configure(text="SGI/SGIX")
			
			with open("SGI_extensions.txt") as file2:
				count = len(file2.readlines())
				TotExt.insert('insert',count)
				TotExt.configure(state='disabled',foreground="BLUE")
				file2.seek(0,0)
				i = 0
				if count  > 0:
					for line in file2:
						TreeGLAll.insert('','end',text=line,tags=i)
						if i % 2 != 0:
							TreeGLAll.tag_configure(i,background="GRAY91")
						i = i + 1
				else:
					TreeGLAll.insert('','end',text="No extensions available")

				os.system("rm SGI*.txt")

		if radsel == 11:
			os.system("cat extensions.txt | grep _IBM > IBM_extensions.txt")
			frame4.configure(text="IBM")
		
			with open("IBM_extensions.txt") as file2:
				count = len(file2.readlines())
				TotExt.insert('insert',count)
				TotExt.configure(state='disabled',foreground="BLUE")
				file2.seek(0,0)
				i = 0
				if count  > 0:
					for line in file2:
						TreeGLAll.insert('','end',text=line,tags=i)
						if i % 2 != 0:
							TreeGLAll.tag_configure(i,background="GRAY91")
						i = i + 1
				else:
					TreeGLAll.insert('','end',text="No extensions available")
				os.system("rm IBM*.txt")

		if radsel == 12:
			os.system("cat extensions.txt | grep _OES > OES_extensions.txt")
			frame4.configure(text="OES")
		
			with open("OES_extensions.txt") as file2:
				count = len(file2.readlines())
				TotExt.insert('insert',count)
				TotExt.configure(state='disabled',foreground="BLUE")
				file2.seek(0,0)
				i = 0
				if count  > 0:
					for line in file2:
						TreeGLAll.insert('','end',text=line,tags=i)
						if i % 2 != 0:
							TreeGLAll.tag_configure(i,background="GRAY91")
						i = i + 1
				else:
					TreeGLAll.insert('','end',text="No extensions available")

				os.system("rm OES*.txt")




	OpenGLrad = tk.Radiobutton(frame2,text="OpenGL", variable=radvar1, value=1,command=select)
	OpenGLrad.grid(column=0,row=1)
	OpenGLrad.invoke()

	OpenGLESrad = tk.Radiobutton(frame2,text="OpenGL ES", variable=radvar1, value=2,command=select)
	OpenGLESrad.grid(column=1,row=1)

	

	
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

