import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import os




def OpenGL(tab1):



# Creating the first Frame to display the OpenGL Version Core and String details along with Hardware 

	frame1 = ttk.LabelFrame(tab1, text="OpenGL Information")
	frame1.grid(column=0,row=0, padx=20, pady=20)
	os.system("glxinfo | grep string | grep -v glx > OpenGL_Information.txt")


# Creating the Scrolled text box to display the above OpenGL_Information.txt

	sc1 = scrolledtext.ScrolledText(frame1, width=100, height=10)

# Opening the OpenGL_Information.txt file in read mode

	with open("OpenGL_Information.txt","r") as file1:
		for line in file1:
			sc1.insert('insert',line)
			sc1.grid(column=0,row=0)

		sc1.configure(state='disabled',foreground="BLUE") # Keeping the scrolled text box uneditable to the end-user

# Creating a new window for OpenGL Limits

	def clickMe():
		win2 = tk.Tk()
		win2.title("OpenGL Limits")

		frame4 = ttk.LabelFrame(win2, text="OpenGL Limits")
		frame4.grid(column=0,row=0, padx=20,pady=20)
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

	radvar = tk.IntVar();
	def radcall():
		frame3 = ttk.LabelFrame(tab1, text="")
		frame3.grid(column=0,row=2)
		radsel=radvar.get()
		label1 = ttk.Label(frame2, text="No :")
		label1.grid(column=0,row=2)
		if radsel == 1:
			os.system("glxinfo -s | awk '/OpenGL extensions/{flag=1;next}/OpenGL ES profile/{flag=0} flag' | grep GL_ | sort > extensions.txt")
			os.system("glxinfo -s | awk '/client glx extensions/{flag=1; next}/GLX version/{flag=0} flag' | grep GLX_ | sort >> extensions.txt")
			frame3.configure(text="All") 
			sc2 = scrolledtext.ScrolledText(frame3, width=100, height=15)
			with open("extensions.txt") as file2:
				count = len(file2.readlines())
				Allcount = ttk.Entry(frame2, width=5)
				Allcount.insert('insert',count)
				Allcount.configure(state='disabled',foreground="BLUE")
				Allcount.grid(column=1,row=2)
				file2.seek(0,0)
				for line in file2:
					sc2.insert('insert',line)
					sc2.grid(column=0,row=2)

				sc2.configure(state='disabled',foreground="BLUE")

		if radsel == 2:
			os.system("cat extensions.txt | grep _AMD > AMD_extensions.txt")
			#os.system("sort extensions.txt | uniq > extensions.txt")
			sc2 = scrolledtext.ScrolledText(frame3, width=100, height=15)
			frame3.configure(text="AMD")
			with open("AMD_extensions.txt") as file2:
				count = len(file2.readlines())
				AMDcount = ttk.Entry(frame2, width=5)
				AMDcount.insert('insert',count)
				AMDcount.configure(state='disabled',foreground="BLUE")
				AMDcount.grid(column=1,row=2)
				file2.seek(0,0)
				for line in file2:
					sc2.insert('insert',line)
					sc2.grid(column=0,row=2)

				sc2.configure(state='disabled',foreground='red')
				os.system("rm AMD*.txt")

		if radsel == 3:
			os.system("cat extensions.txt | grep _ARB > ARB_extensions.txt")
			#os.system("sort extensions1.txt | uniq > extensions.txt")
			frame3.configure(text="ARB")
			sc2 = scrolledtext.ScrolledText(frame3, width=100, height=15)
			with open("ARB_extensions.txt") as file2:
				count = len(file2.readlines())
				ARBcount = ttk.Entry(frame2, width=5)
				ARBcount.insert('insert',count)
				ARBcount.configure(state='disabled',foreground="BLUE")
				ARBcount.grid(column=1,row=2)
				file2.seek(0,0)
				for line in file2:
					sc2.insert('insert',line)
					sc2.grid(column=0,row=2)

				sc2.configure(state='disabled',foreground="orange")
				os.system("rm ARB*.txt")

		if radsel == 4:
			os.system("cat extensions.txt | grep _EXT > EXT_extensions.txt")
			#os.system("sort extensions1.txt | uniq > extensions.txt")
			frame3.configure(text="EXT")
			sc2 = scrolledtext.ScrolledText(frame3, width=100, height=15)
			with open("EXT_extensions.txt") as file2:
				count = len(file2.readlines())
				EXTcount = ttk.Entry(frame2, width=5)
				EXTcount.insert('insert',count)
				EXTcount.configure(state='disabled',foreground="BLUE")
				EXTcount.grid(column=1,row=2)
				file2.seek(0,0)
				for line in file2:
					sc2.insert('insert',line)
					sc2.grid(column=0,row=2)

				sc2.configure(state='disabled',foreground='BLACK')
				os.system("rm EXT*.txt")

		if radsel == 5:
			os.system("cat extensions.txt | grep _NV > NV_extensions.txt")
			#os.system("sort extensions1.txt | uniq > extensions.txt")
			frame3.configure(text="NV")
			sc2 = scrolledtext.ScrolledText(frame3, width=100, height=15)
			with open("NV_extensions.txt") as file2:
				count = len(file2.readlines())
				NVcount = ttk.Entry(frame2, width=5)
				NVcount.insert('insert',count)
				NVcount.configure(state='disabled',foreground="BLUE")
				NVcount.grid(column=1,row=2)
				file2.seek(0,0)
				for line in file2:
					sc2.insert('insert',line)
					sc2.grid(column=0,row=2)

				sc2.configure(state='disabled',foreground="GREEN")
				os.system("rm NV*.txt")

		if radsel == 6:
			os.system("cat extensions.txt | grep _ATI > ATI_extensions.txt")
			#os.system("sort extensions1.txt | uniq > extensions.txt")
			frame3.configure(text="ATI")
			sc2 = scrolledtext.ScrolledText(frame3, width=100, height=15)
			with open("ATI_extensions.txt") as file2:
				count = len(file2.readlines())
				ATIcount = ttk.Entry(frame2, width=5)
				ATIcount.insert('insert',count)
				ATIcount.configure(state='disabled',foreground="BLUE")
				ATIcount.grid(column=1,row=2)
				file2.seek(0,0)
				for line in file2:
					sc2.insert('insert',line)
					sc2.grid(column=0,row=2)

				sc2.configure(state='disabled',foreground="RED")
				os.system("rm ATI*.txt")

		if radsel == 7:
			os.system("cat extensions.txt | grep _KHR > KHR_extensions.txt")
			#os.system("sort extensions1.txt | uniq > extensions.txt")
			frame3.configure(text="KHR")
			sc2 = scrolledtext.ScrolledText(frame3, width=100, height=15)
			with open("KHR_extensions.txt") as file2:
				count = len(file2.readlines())
				KHRcount = ttk.Entry(frame2, width=5)
				KHRcount.insert('insert',count)
				KHRcount.configure(state='disabled',foreground="BLUE")
				KHRcount.grid(column=1,row=2)
				file2.seek(0,0)
				for line in file2:
					sc2.insert('insert',line)
					sc2.grid(column=0,row=2)

				sc2.configure(state='disabled',foreground="BROWN")
				os.system("rm KHR*.txt")

		if radsel == 8:
			os.system("cat extensions.txt | grep _MESA > MESA_extensions.txt")
			#os.system("sort extensions1.txt | uniq > extensions.txt")
			frame3.configure(text="MESA")
			sc2 = scrolledtext.ScrolledText(frame3, width=100, height=15)
			with open("MESA_extensions.txt") as file2:
				count = len(file2.readlines())
				KHRcount = ttk.Entry(frame2, width=5)
				KHRcount.insert('insert',count)
				KHRcount.configure(state='disabled',foreground="BLUE")
				KHRcount.grid(column=1,row=2)
				file2.seek(0,0)
				if count  > 0:
					for line in file2:
						sc2.insert('insert',line)
						sc2.grid(column=0,row=2)
				else:
					for line in file2:
						sc2.insert('insert',BLANK)
						sc2.grid(column=0,row=2)
					print("Zero")

				sc2.configure(state='disabled',foreground="PURPLE")
				os.system("rm MESA*.txt")

		if radsel == 10:
			os.system("cat extensions.txt | grep -v _AMD | grep -v _MESA | grep -v _NV | grep -v _ATI | grep -v _ARB | grep -v _SGI | grep -v _KHR | grep -v _EXT > Others_extensions.txt")
			#os.system("sort extensions1.txt | uniq > extensions.txt")
			frame3.configure(text="GLX")
			sc2 = scrolledtext.ScrolledText(frame3, width=100, height=15)
			with open("Others_extensions.txt") as file2:
				count = len(file2.readlines())
				Otherscount = ttk.Entry(frame2, width=5)
				Otherscount.insert('insert',count)
				Otherscount.configure(state='disabled',foreground="BLUE")
				Otherscount.grid(column=1,row=2)
				file2.seek(0,0)
				for line in file2:
					sc2.insert('insert',line)
					sc2.grid(column=0,row=2)


				sc2.configure(state='disabled', foreground='violet')
				os.system("rm Others*.txt")
	
		if radsel == 9:
			os.system("cat extensions.txt | grep _SGI > SGI_extensions.txt")
			#os.system("sort extensions1.txt | uniq > extensions.txt")
			frame3.configure(text="SGI/SGIX")
			sc2 = scrolledtext.ScrolledText(frame3, width=100, height=15)
			with open("SGI_extensions.txt") as file2:
				count = len(file2.readlines())
				KHRcount = ttk.Entry(frame2, width=5)
				KHRcount.insert('insert',count)
				KHRcount.configure(state='disabled',foreground="BLUE")
				KHRcount.grid(column=1,row=2)
				file2.seek(0,0)
				for line in file2:
					sc2.insert('insert',line)
					sc2.grid(column=0,row=2)

				sc2.configure(state='disabled',foreground="INDIGO")
				os.system("rm SGI*.txt")


	frame2 = ttk.LabelFrame(tab1, text="OpenGL Extensions ")
	frame2.grid(column=0,row=1,padx=20, sticky=tk.W)
	

	rad1 = tk.Radiobutton(frame2, text="All", variable=radvar, value=1, command=radcall)
	rad1.grid(column=0,row=1)
	rad1.invoke()
	rad2 = tk.Radiobutton(frame2, text="AMD", variable=radvar, value=2, command=radcall)
	rad2.grid(column=1,row=1)
	rad3 = tk.Radiobutton(frame2, text="ARB", variable=radvar, value=3, command=radcall)
	rad3.grid(column=2,row=1)
	rad4 = tk.Radiobutton(frame2, text="ATI", variable=radvar, value=6, command=radcall)
	rad4.grid(column=3,row=1)
	rad5 = tk.Radiobutton(frame2, text="EXT", variable=radvar, value=4, command=radcall)
	rad5.grid(column=4,row=1)
	rad6 = tk.Radiobutton(frame2, text="NV", variable=radvar, value=5, command=radcall)
	rad6.grid(column=6,row=1)
	rad7 = tk.Radiobutton(frame2, text="KHR", variable=radvar, value=7, command=radcall)
	rad7.grid(column=5,row=1)
	rad8 = tk.Radiobutton(frame2, text="MESA", variable=radvar, value=8, command=radcall)
	rad8.grid(column=7,row=1)
	rad9 = tk.Radiobutton(frame2, text="SGI", variable=radvar, value=9, command=radcall)
	rad9.grid(column=8,row=1)
	rad10 = tk.Radiobutton(frame2, text="Others", variable=radvar, value=10, command=radcall)
	rad10.grid(column=9,row=1)


#OpenGL()


#win.mainloop()