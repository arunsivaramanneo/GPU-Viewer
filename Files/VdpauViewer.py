import os
import gi
import Const

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from Common import copyContentsFromFile, setBackgroundColor, setColumns, createSubTab, createScrollbar, createSubFrame, \
    colorTrueFalse, getDriverVersion, getVulkanVersion, getDeviceSize, refresh_filter, getRamInGb, fetchImageFromUrl, getFormatValue


decoderTitle = ["Decoder name","Level","Macroblocks","Width","Height"]
videoMixerParameterTitle = ["Parameter name","Supported","Min","Max"]
videoMixerAttributeTitle = ["Attribute name","Supported","Min","Max"]
videoMixerFeatureTitle = ["Feature name","Supported"]
surfaceVideoTitle = ["Video Surface","Width","Height","Types"]
surfaceOutputTitle = ["Output Surface","Width","Height","Native","Types"]
SurfaceBitmapTitle = ["Bitmap Surface","Width","Height"]


def vdpauinfo(tab2):

	def decoderCapabilities():

		os.system("cat /tmp/gpu-viewer/vdpauinfo.txt | awk '/Decoder capabilities:/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./'> /tmp/gpu-viewer/vdpauDecoder.txt")
		with open("/tmp/gpu-viewer/vdpauDecoder.txt","r") as file1:
			for i,line in  enumerate(file1):
				if "not" in line:
					decoderStore.append([line.split()[0].strip('\n'),"not supported","not supported","not supported","not supported",setBackgroundColor(i)])
				else:
					decoderStore.append([line.split()[0].strip('\n'),line.split()[1].strip('\n'),line.split()[2].strip('\n'),line.split()[3].strip('\n'),line.split()[4].strip('\n'),setBackgroundColor(i)])
	
	def surfaceOutputLimits():
		os.system("cat /tmp/gpu-viewer/vdpauinfo.txt | awk '/Output surface:/{flag=1;next}/Bitmap surface:/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Bitmap surface:/{flag=0}flag' | awk '/./' > /tmp/gpu-viewer/vdpauSurfaceOutputLimits.txt")
		with open("/tmp/gpu-viewer/vdpauSurfaceOutputLimits.txt","r") as file:
			for i,line in enumerate(file):
				surfaceOutputStore.append([line.split()[0].strip('\n'),line.split()[1].strip('\n'),line.split()[2].strip('\n'),line.split()[3].strip('\n'),line.split()[4].strip('\n')+" "+line.split()[5].strip('\n')+" "+line.split()[6].strip('\n')+" "+line.split()[7].strip('\n')+" "+line.split()[8].strip('\n')+" "+line.split()[9].strip('\n')+" "+line.split()[10].strip('\n')+" "+line.split()[11].strip('\n')+" "+line.split()[12].strip('\n')+" "+line.split()[13].strip('\n'),setBackgroundColor(i)])

	def surfaceBitmapLimits():
		os.system("cat /tmp/gpu-viewer/vdpauinfo.txt | awk '/Bitmap surface:/{flag=1;next}/Video mixer:/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Video mixer:/{flag=0}flag' | awk '/./' > /tmp/gpu-viewer/vdpauSurfaceBitmapLimits.txt")
		with open("/tmp/gpu-viewer/vdpauSurfaceBitmapLimits.txt","r") as file:
			for i,line in enumerate(file):
				surfaceBitmapStore.append([line.split()[0].strip('\n'),line.split()[1].strip('\n'),line.split()[2].strip('\n'),setBackgroundColor(i)])



	def VideoMixerParameter():
		
		os.system("cat /tmp/gpu-viewer/vdpauinfo.txt | awk '/Video mixer:/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/parameter name/{flag=1;next}/attribute name.*/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./' > /tmp/gpu-viewer/vdpauVideoMixerParameter.txt")
		with open("/tmp/gpu-viewer/vdpauVideoMixerParameter.txt","r") as file2:
			for i,line in enumerate(file2):
				if line.split()[1].strip('\n') == 'y':
					text = "True"
				else:
					text = "False"
				videoMixerParameterStore.append([line.split()[0].strip('\n'),text,"","",setBackgroundColor(i)])

	def VideoMixerAttribute():
		
		os.system("cat /tmp/gpu-viewer/vdpauinfo.txt | awk '/Video mixer:/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/attribute name/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./' > /tmp/gpu-viewer/vdpauVideoMixerAttribute.txt")
		with open("/tmp/gpu-viewer/vdpauVideoMixerAttribute.txt","r") as file2:
			for i,line in enumerate(file2):
				if line.split()[1].strip('\n') == 'y':
					text = "True"
				else:
					text = "False"
				videoMixerAttributeStore.append([line.split()[0].strip('\n'),text,"","",setBackgroundColor(i)])

	grid = Gtk.Grid()
	tab2.add(grid)
	DevicesFrame = Gtk.Frame()
	grid.add(DevicesFrame)

	notebook = Gtk.Notebook()
	notebook.set_property("scrollable", True)
	notebook.set_property("enable-popup", True)
	grid.attach(notebook, 0, 2, 1, 1)

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

	setColumns(treeSurfaceVideoLimits,surfaceVideoTitle,200,0.0)

	surfaceVideoScrollbar = createScrollbar(treeSurfaceVideoLimits)
	surfaceGrid.add(surfaceVideoScrollbar)

	surfaceOutputStore = Gtk.ListStore(str,str,str,str,str,str)
	treeSurfaceOutputLimits = Gtk.TreeView(surfaceOutputStore,expand=True)

	setColumns(treeSurfaceOutputLimits,surfaceOutputTitle,200,0.0)

	surfaceOutputScrollbar = createScrollbar(treeSurfaceOutputLimits)
	surfaceGrid.attach_next_to(surfaceOutputScrollbar,surfaceVideoScrollbar,Gtk.PositionType.BOTTOM,1,1)

	surfaceBitmapStore = Gtk.ListStore(str,str,str,str)
	treeSurfaceBitmapLimits = Gtk.TreeView(surfaceBitmapStore,expand=True)

	setColumns(treeSurfaceBitmapLimits,SurfaceBitmapTitle,200,0.0)

	surfaceBitmapScrollbar = createScrollbar(treeSurfaceBitmapLimits)
	surfaceGrid.attach_next_to(surfaceBitmapScrollbar,surfaceOutputScrollbar,Gtk.PositionType.BOTTOM,1,1)
# -------- Video Mixer ---------------------------------------

	videoMixerTab = Gtk.Box(spacing=20)
	videoMixerGrid = createSubTab(videoMixerTab,notebook,"Video Mixer")

	videoMixerFeatureStore = Gtk.ListStore(str,str,str)
	treeVideoMixerFeature = Gtk.TreeView(videoMixerFeatureStore,expand=True)

	setColumns(treeVideoMixerFeature, videoMixerFeatureTitle, 300 ,0.0)

	videoMixerFeatureScrollbar = createScrollbar(treeVideoMixerFeature)
	videoMixerGrid.add(videoMixerFeatureScrollbar)

	videoMixerParameterStore = Gtk.ListStore(str,str,str,str,str)

	treeVideoMixerParameter = Gtk.TreeView(videoMixerParameterStore,expand=True)

	setColumns(treeVideoMixerParameter,videoMixerParameterTitle, 300, 0.0)

	videoMixerParameterScrollbar = createScrollbar(treeVideoMixerParameter)
	videoMixerGrid.attach_next_to(videoMixerParameterScrollbar,videoMixerFeatureScrollbar,Gtk.PositionType.BOTTOM, 1, 1)

	videoMixerAttributeStore = Gtk.ListStore(str,str,str,str,str)
	treeVideoMixerAttribute = Gtk.TreeView(videoMixerAttributeStore,expand=True)

	setColumns(treeVideoMixerAttribute, videoMixerAttributeTitle, 300, 0.0)

	videoMixerAttributeScrollbar = createScrollbar(treeVideoMixerAttribute)
	videoMixerGrid.attach_next_to(videoMixerAttributeScrollbar,videoMixerParameterScrollbar,Gtk.PositionType.BOTTOM, 1, 1)







	decoderCapabilities()
	surfaceOutputLimits()
	surfaceBitmapLimits()
	VideoMixerParameter()
	VideoMixerAttribute()