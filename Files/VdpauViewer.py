import os
import gi
import Const

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from Common import copyContentsFromFile, setBackgroundColor, setColumns, createSubTab, createScrollbar, createSubFrame, \
    colorTrueFalse, getDriverVersion, getVulkanVersion, getDeviceSize, refresh_filter, getRamInGb, fetchImageFromUrl, getFormatValue


decoderTitle = ["Decoder Name","Level","Macroblocks","Width","Height"]
videoMixerFeatureTitle = ["Name","Supported"]
surfaceVideoTitle = ["Video Surface","Width","Height","Types"]
surfaceOutputTitle = ["Output Surface","Width","Height","Types"]
SurfaceBitmapTitle = ["Bitmap Surface","Width","Height"]
vdpauinfoTitle = ["VDPAU Information","Details"]


def vdpauinfo(tab2):

	def vdpauInformation():

		os.system("cat /tmp/gpu-viewer/vdpauinfo.txt | grep -E 'API|string' > /tmp/gpu-viewer/vdpauInformation.txt")
		with open("/tmp/gpu-viewer/vdpauInformation.txt","r") as file:
			for i,line in enumerate(file):
				vdpauinfoStore.append(None,[' '.join(line.split()[0:2]).strip('[]'),' '.join(line.split()[2:]).strip('[]'),setBackgroundColor(i)])

		iter = vdpauinfoStore.append(None,["Supported Codecs:",' ',Const.BGCOLOR3])

		with open("/tmp/gpu-viewer/vdpauDecoder.txt","r") as file1:
			i = 1
			for line in  file1:
				if "not" not in line:
					vdpauinfoStore.append(iter,["",line.split()[0].strip('\n'),setBackgroundColor(i)])
					i = i+1

		treeVdpauInfo.expand_all()

	def decoderCapabilities():

		os.system("cat /tmp/gpu-viewer/vdpauinfo.txt | awk '/Decoder capabilities:/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./'> /tmp/gpu-viewer/vdpauDecoder.txt")
		with open("/tmp/gpu-viewer/vdpauDecoder.txt","r") as file1:
			for i,line in  enumerate(file1):
				if "not" in line:
					decoderStore.append([line.split()[0].strip('\n'),"not supported","not supported","not supported","not supported",setBackgroundColor(i)])
				else:
					decoderStore.append([line.split()[0].strip('\n'),line.split()[1].strip('\n'),line.split()[2].strip('\n'),line.split()[3].strip('\n'),line.split()[4].strip('\n'),setBackgroundColor(i)])
	
	def videoSurfaceLimits():
		os.system("cat /tmp/gpu-viewer/vdpauinfo.txt | awk '/Video surface:/{flag=1;next}/Decoder capabilities:/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Bitmap surface:/{flag=0}flag' | awk '/./' > /tmp/gpu-viewer/vdpauVideoSurfaceLimits.txt")
		with open("/tmp/gpu-viewer/vdpauVideoSurfaceLimits.txt","r") as file1:
			for i,line in enumerate(file1):
				surfaceVideoStore.append([line.split()[0].strip('\n'),line.split()[1].strip('\n'),line.split()[2].strip('\n'),(' '.join(line.split()[3:]).strip('[]')),setBackgroundColor(i)])

	def surfaceOutputLimits():
		os.system("cat /tmp/gpu-viewer/vdpauinfo.txt | awk '/Output surface:/{flag=1;next}/Bitmap surface:/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Bitmap surface:/{flag=0}flag' | awk '/./' > /tmp/gpu-viewer/vdpauSurfaceOutputLimits.txt")
		with open("/tmp/gpu-viewer/vdpauSurfaceOutputLimits.txt","r") as file:
			for i,line in enumerate(file):
				surfaceOutputStore.append([line.split()[0].strip('\n'),line.split()[1].strip('\n'),line.split()[2],(' '.join(line.split()[4:]).strip('[]')),setBackgroundColor(i)])

	def surfaceBitmapLimits():
		os.system("cat /tmp/gpu-viewer/vdpauinfo.txt | awk '/Bitmap surface:/{flag=1;next}/Video mixer:/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Video mixer:/{flag=0}flag' | awk '/./' > /tmp/gpu-viewer/vdpauSurfaceBitmapLimits.txt")
		with open("/tmp/gpu-viewer/vdpauSurfaceBitmapLimits.txt","r") as file:
			for i,line in enumerate(file):
				surfaceBitmapStore.append([line.split()[0].strip('\n'),line.split()[1].strip('\n'),line.split()[2].strip('\n'),setBackgroundColor(i)])

	def VideoMixerFeature():
		
		os.system("cat /tmp/gpu-viewer/vdpauinfo.txt | awk '/feature name/{flag=1;next}/parameter name.*/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./' > /tmp/gpu-viewer/vdpauVideoMixerFeature.txt")
		

		iter = videoMixerFeatureStore.append(None,["Features","",Const.BGCOLOR3,""])
		with open("/tmp/gpu-viewer/vdpauVideoMixerFeature.txt","r") as file2:
			for i,line in enumerate(file2):
				if 'y'in line:
					text = "true"
					fgcolor = Const.COLOR1
				else:
					text = "false"
					fgcolor = Const.COLOR2
				if "HIGH" in line:
					videoMixerFeatureStore.append(iter,[(' '.join(line.split()[0:5])).strip('[]'),text,setBackgroundColor(i),fgcolor])
				else:
					videoMixerFeatureStore.append(iter,[line.split()[0].strip('\n'),text,setBackgroundColor(i),fgcolor])
		
		os.system("cat /tmp/gpu-viewer/vdpauinfo.txt | awk '/parameter name/{flag=1;next}/attribute name.*/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./' > /tmp/gpu-viewer/vdpauVideoMixerParameter.txt")
		
		iter = videoMixerFeatureStore.append(None,["Parameters","",Const.BGCOLOR3,""])
		with open("/tmp/gpu-viewer/vdpauVideoMixerParameter.txt","r") as file2:
			for i,line in enumerate(file2):
				if line.split()[1].strip('\n') == 'y':
					text = "true"
					fgcolor = Const.COLOR1
				else:
					text = "false"
					fgcolor = Const.COLOR2
				videoMixerFeatureStore.append(iter,[line.split()[0].strip('\n'),text,setBackgroundColor(i),fgcolor])
		
		os.system("cat /tmp/gpu-viewer/vdpauinfo.txt | awk '/Video mixer:/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/attribute name/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./' > /tmp/gpu-viewer/vdpauVideoMixerAttribute.txt")
		
		iter = videoMixerFeatureStore.append(None,["Attributes","",Const.BGCOLOR3,""])
		with open("/tmp/gpu-viewer/vdpauVideoMixerAttribute.txt","r") as file2:
			for i,line in enumerate(file2):
				if line.split()[1].strip('\n') == 'y':
					text = "true"
					fgcolor = Const.COLOR1
				else:
					text = "false"
					fgcolor = Const.COLOR2
				videoMixerFeatureStore.append(iter,[line.split()[0].strip('\n'),text,setBackgroundColor(i),fgcolor])


		treeVideoMixerFeature.expand_all()


	grid = Gtk.Grid()
	tab2.add(grid)
	DevicesFrame = Gtk.Frame()
	grid.add(DevicesFrame)

	notebook = Gtk.Notebook()
	notebook.set_property("scrollable", True)
	notebook.set_property("enable-popup", True)
	grid.attach(notebook, 0, 2, 1, 1)

# ------- VDPAU information -------------------------------


	vdpauinfoTab = Gtk.Box(spacing=20)
	vdpauinfoGrid = createSubTab(vdpauinfoTab,notebook, "VDPAU Information")
	
	vdpauinfoStore = Gtk.TreeStore(str,str,str)
	treeVdpauInfo = Gtk.TreeView(vdpauinfoStore,expand=True)

	setColumns(treeVdpauInfo,vdpauinfoTitle,300,0.0)

	vdpauinfoScrollbar = createScrollbar(treeVdpauInfo)
	vdpauinfoGrid.add(vdpauinfoScrollbar)

# ------- Decoder Capabilities ----------------------------
	
	decoderTab = Gtk.Box(spacing=20)
	decoderGrid = createSubTab(decoderTab, notebook, "Decoder Capabilities")

	decoderStore = Gtk.ListStore(str,str,str,str,str,str)
	treeDecoder = Gtk.TreeView(decoderStore, expand=True)

	setColumns(treeDecoder, decoderTitle, 300, 0.0)

	decoderScrollbar = createScrollbar(treeDecoder)
	decoderGrid.add(decoderScrollbar)

# -------- Surface Limits -----------------------------------

	surfaceTab = Gtk.Box(spacing=20)
	surfaceGrid = createSubTab(surfaceTab,notebook,"Surface Limits")

	surfaceVideoStore = Gtk.ListStore(str,str,str,str,str)
	treeSurfaceVideoLimits = Gtk.TreeView(surfaceVideoStore,expand=True)

	setColumns(treeSurfaceVideoLimits,surfaceVideoTitle,300,0.0)

	surfaceVideoScrollbar = createScrollbar(treeSurfaceVideoLimits)
	surfaceGrid.add(surfaceVideoScrollbar)

	surfaceOutputStore = Gtk.ListStore(str,str,str,str,str)
	treeSurfaceOutputLimits = Gtk.TreeView(surfaceOutputStore,expand=True)

	setColumns(treeSurfaceOutputLimits,surfaceOutputTitle,300,0.0)

	surfaceOutputScrollbar = createScrollbar(treeSurfaceOutputLimits)
	surfaceGrid.attach_next_to(surfaceOutputScrollbar,surfaceVideoScrollbar,Gtk.PositionType.BOTTOM,1,1)

	surfaceBitmapStore = Gtk.ListStore(str,str,str,str)
	treeSurfaceBitmapLimits = Gtk.TreeView(surfaceBitmapStore,expand=True)

	setColumns(treeSurfaceBitmapLimits,SurfaceBitmapTitle,300,0.0)

	surfaceBitmapScrollbar = createScrollbar(treeSurfaceBitmapLimits)
	surfaceGrid.attach_next_to(surfaceBitmapScrollbar,surfaceOutputScrollbar,Gtk.PositionType.BOTTOM,1,1)
# -------- Video Mixer ---------------------------------------

	videoMixerTab = Gtk.Box(spacing=20)
	videoMixerGrid = createSubTab(videoMixerTab,notebook,"Video Mixer")
	videoMixerGrid.set_row_spacing(20)

	videoMixerFeatureStore = Gtk.TreeStore(str,str,str,str)
	treeVideoMixerFeature = Gtk.TreeView(videoMixerFeatureStore,expand=True)
	treeVideoMixerFeature.set_property("enable-tree-lines", True)
	treeVideoMixerFeature.set_enable_search(True)

	for i, column_title in enumerate(videoMixerFeatureTitle):
	    videoMixerrenderer = Gtk.CellRendererText()
	#        Queuerenderer.set_alignment(0.5, 0.5)
	    column = Gtk.TreeViewColumn(column_title, videoMixerrenderer, text=i)
	#        column.set_alignment(0.5)
	    column.add_attribute(videoMixerrenderer, "background", 2)
	    column.set_sort_column_id(i)
	    column.set_resizable(True)
	    column.set_reorderable(True)
	    if i > 0:
	        column.add_attribute(videoMixerrenderer, "foreground", 3)
	    treeVideoMixerFeature.set_property("can-focus", False)
	    treeVideoMixerFeature.append_column(column)

	
	videoMixerFeatureScrollbar = createScrollbar(treeVideoMixerFeature)
	videoMixerGrid.add(videoMixerFeatureScrollbar)




	decoderCapabilities()
	videoSurfaceLimits()
	surfaceOutputLimits()
	surfaceBitmapLimits()
	VideoMixerFeature()
	vdpauInformation()
