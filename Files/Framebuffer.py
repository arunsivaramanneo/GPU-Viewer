import tkinter as tk
import os
from tkinter import Toplevel
from tkinter import ttk

def FrameBuffer():

	win = Toplevel()
	win.title("GLX Frame Buffer Configuration")
	win.resizable(0,0)



	frame1 = ttk.LabelFrame(win,text= "GLX Frame Buffer Configuration",padding=10)
	frame1.grid(column=0,row=0,padx=10,pady=10)
	radvar = tk.IntVar()



	FrameBufferHeading = ["visual","x","bf","lv","rg","d","st","colorbuffer"," ","sr","ax","dp","st","accumbuffer","ms"," "]
	FrameBufferLength = [120,35,35,35,35,35,35,140,35,35,35,35,35,140,70,75]
	FrameBufferList = ["dep","cl","sp","sz","l","ci","b","ro","r","g","b","a","F","gb","bf","th","cl","r","g","b","a","ns","b"]

	TreeFrameBuffer1 = ttk.Treeview(frame1,height=0)
	TreeFrameBuffer1['column'] =('value0','value1','value2','value3','value4','value5','value6','value7','value8','value9','value10','value11','value12','value13',
		'value14','value15')
	TreeFrameBuffer1.column('#0',width=10)

	for i in range(len(FrameBufferHeading)):
		TreeFrameBuffer1.heading('value%d'%i,text=FrameBufferHeading[i])
		TreeFrameBuffer1.column('value%d'%i,width=FrameBufferLength[i])

	TreeFrameBuffer1['show']='headings'
	TreeFrameBuffer1.grid(column=0,row=1,sticky=tk.W)

	TreeFrameBuffer2 = ttk.Treeview(frame1,height=15)

	TreeFrameBuffer2['column'] = ('valueid','value0','value1','value2','value3','value4','value5','value6','value7','value8','value9','value10','value11','value12','value13',
		'value14','value15','value16','value17','value18','value19','value20','value21','value22','valuecaveat')

	TreeFrameBuffer2.heading('valueid',text='Id')
	TreeFrameBuffer2.column('valueid',width=50,anchor='center')
	TreeFrameBuffer2.heading('valuecaveat',text='caveat')
	TreeFrameBuffer2.column('valuecaveat',width=75,anchor='center')

	for i in range(len(FrameBufferList)):
		TreeFrameBuffer2.heading('value%d'%i,text=FrameBufferList[i])
		TreeFrameBuffer2.column('value%d'%i,width=35,anchor='center')

	TreeFrameBuffer2['show']='headings'
	TreeFrameBuffer2.column('#0',width=10)
	TreeFrameBuffer2.grid(column=0,row=2)

	FrameBuffersb = ttk.Scrollbar(frame1, orient="vertical", command=TreeFrameBuffer2.yview)
	TreeFrameBuffer2.configure(yscrollcommand=FrameBuffersb.set)
	FrameBuffersb.grid(column=0,row=2,sticky='nse')

	def radcall():

		radsel = radvar.get()

		for i in TreeFrameBuffer2.get_children():
	  	  TreeFrameBuffer2.delete(i)

		if radsel == 1:

			os.system("glxinfo | awk '/GLX Visuals.*/{flag=1;next}/GLXFBConfigs.*/{flag=0}flag' | awk '/----.*/{flag=1;next}flag' > FrameBufferGLXVisuals.txt")

			with open("FrameBufferGLXVisuals.txt","r") as file1:
				GLXCount = len(file1.readlines())
				file1.seek(0,0)
				i = 0
				rad1.configure(text="%d GLX Visuals"%(GLXCount-1))
				for line in file1:
					TreeFrameBuffer2.insert('','end',values=line,tags=i)
					if i % 2 != 0:
						TreeFrameBuffer2.tag_configure(i,background='GRAY91')
					i = i + 1

			os.system("rm FrameBuffer*.txt")

		if radsel == 2:

			os.system("glxinfo | awk '/GLXFBConfigs.*/{flag=1;next}flag' | awk '/----.*/{flag=1;next}flag' > FrameBufferGLXFBConfigs.txt")
			with open("FrameBufferGLXFBConfigs.txt","r") as file1:
				FBCount = len(file1.readlines())
				file1.seek(0,0)
				i = 0
				rad2.configure(text="%d GLXFBConfigs"%(FBCount-1))
				for line in file1:
					TreeFrameBuffer2.insert('','end',values=line,tags=i)
					if i % 2 != 0:
						TreeFrameBuffer2.tag_configure(i,background='GRAY91')
					i = i + 1

			os.system("rm FrameBuffer*.txt")


	rad1 = tk.Radiobutton(frame1, text="GLX Visuals", variable=radvar, value=1,command=radcall)
	rad1.grid(column=0,row=0,pady=10,sticky = tk.W)
	rad1.invoke()

	rad2 = tk.Radiobutton(frame1,text="GLXFBConfigs",variable=radvar,value=2,command=radcall)
	rad2.grid(column=0,row=0,pady=10)
	#rad2.invoke()

	win.mainloop()