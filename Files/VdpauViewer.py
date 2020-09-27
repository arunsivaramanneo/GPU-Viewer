import os
import gi
import Const

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from Common import copyContentsFromFile, setBackgroundColor, setColumns, createSubTab, createScrollbar, createSubFrame, \
    colorTrueFalse, getDriverVersion, getVulkanVersion, getDeviceSize, refresh_filter, getRamInGb, fetchImageFromUrl, getFormatValue


decoderTitle = ["Decoder name","Level","Macroblocks","Width","Height"]
videoMixerParameterTitle = ["Parameter name","Supported"]
videoMixerAttributeTitle = ["Attribute name","Supported"]
videoMixerFeatureTitle = ["Feature name","Supported"]
surfaceVideoTitle = ["Video Surface","Width","Height","Types"]
surfaceOutputTitle = ["Output Surface","Width","Height","Types"]
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
		with open("/tmp/gpu-viewer/vdpauVideoMixerFeature.txt","r") as file2:
			for i,line in enumerate(file2):
				if 'y'in line:
					text = "true"
					fgcolor = Const.COLOR2
				else:
					text = "false"
					fgcolor = Const.COLOR1
				if "HIGH" in line:
					videoMixerFeatureStore.append([(' '.join(line.split()[0:5])).strip('[]'),text,setBackgroundColor(i)])
				else:
					videoMixerFeatureStore.append([line.split()[0].strip('\n'),text,setBackgroundColor(i)])

	def VideoMixerParameter():
		
		os.system("cat /tmp/gpu-viewer/vdpauinfo.txt | awk '/parameter name/{flag=1;next}/attribute name.*/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./' > /tmp/gpu-viewer/vdpauVideoMixerParameter.txt")
		with open("/tmp/gpu-viewer/vdpauVideoMixerParameter.txt","r") as file2:
			for i,line in enumerate(file2):
				if line.split()[1].strip('\n') == 'y':
					text = "true"
				else:
					text = "false"
				videoMixerParameterStore.append([line.split()[0].strip('\n'),text,setBackgroundColor(i)])

	def VideoMixerAttribute():
		
		os.system("cat /tmp/gpu-viewer/vdpauinfo.txt | awk '/Video mixer:/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/attribute name/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./' > /tmp/gpu-viewer/vdpauVideoMixerAttribute.txt")
		with open("/tmp/gpu-viewer/vdpauVideoMixerAttribute.txt","r") as file2:
			for i,line in enumerate(file2):
				if line.split()[1].strip('\n') == 'y':
					text = "true"
				else:
					text = "false"
				videoMixerAttributeStore.append([line.split()[0].strip('\n'),text,setBackgroundColor(i)])

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

	videoMixerFeatureStore = Gtk.ListStore(str,str,str)
	treeVideoMixerFeature = Gtk.TreeView(videoMixerFeatureStore,expand=True)

	setColumns(treeVideoMixerFeature, videoMixerFeatureTitle, 350 ,0.0)

	videoMixerFeatureScrollbar = createScrollbar(treeVideoMixerFeature)
	videoMixerGrid.add(videoMixerFeatureScrollbar)

	videoMixerParameterStore = Gtk.ListStore(str,str,str)

	treeVideoMixerParameter = Gtk.TreeView(videoMixerParameterStore,expand=True)

	setColumns(treeVideoMixerParameter,videoMixerParameterTitle, 350, 0.0)

	videoMixerParameterScrollbar = createScrollbar(treeVideoMixerParameter)
	videoMixerGrid.attach_next_to(videoMixerParameterScrollbar,videoMixerFeatureScrollbar,Gtk.PositionType.BOTTOM, 1, 1)

	videoMixerAttributeStore = Gtk.ListStore(str,str,str)
	treeVideoMixerAttribute = Gtk.TreeView(videoMixerAttributeStore,expand=True)

	setColumns(treeVideoMixerAttribute, videoMixerAttributeTitle, 350, 0.0)

	videoMixerAttributeScrollbar = createScrollbar(treeVideoMixerAttribute)
	videoMixerGrid.attach_next_to(videoMixerAttributeScrollbar,videoMixerParameterScrollbar,Gtk.PositionType.BOTTOM, 1, 1)







	decoderCapabilities()
	videoSurfaceLimits()
	surfaceOutputLimits()
	surfaceBitmapLimits()
	VideoMixerFeature()
	VideoMixerParameter()
	VideoMixerAttribute()
