import os
import gi
import Const

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from Common import copyContentsFromFile, setBackgroundColor, setColumns, createSubTab, createScrollbar, createSubFrame, \
    colorTrueFalse, getDriverVersion, getVulkanVersion, getDeviceSize, refresh_filter, getRamInGb, fetchImageFromUrl, getFormatValue


decoderTitle = ["Decoder name","Level","Macroblocks","Width","height"]
videoMixerParameterTitle = ["Parameter name","supported","Min","Max"]
videoMixerAttributeTitle = ["Attribute name","supported","Min","Max"]
videoMixerFeatureTitle = ["Feature name","supported"]


def vdpauinfo(tab2):

	def decoderCapabilities():

		os.system("cat /tmp/gpu-viewer/vdpauinfo.txt | awk '/Decoder capabilities:/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./'> /tmp/gpu-viewer/vdpauDecoder.txt")
		with open("/tmp/gpu-viewer/vdpauDecoder.txt","r") as file1:
			for i,line in  enumerate(file1):
				if "not" in line:
					decoderStore.append([line.split()[0].strip('\n'),"not supported","not supported","not supported","not supported",setBackgroundColor(i)])
				else:
					decoderStore.append([line.split()[0].strip('\n'),line.split()[1].strip('\n'),line.split()[2].strip('\n'),line.split()[3].strip('\n'),line.split()[4].strip('\n'),setBackgroundColor(i)])
	
	def vdpauVideoMixerParameter():
		
		os.system("cat /tmp/gpu-viewer/vdpauinfo.txt | awk '/Video mixer:/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/parameter name/{flag=1;next}/attribute name.*/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./' > /tmp/gpu-viewer/vdpauVideoMixerParameter.txt")
		with open("/tmp/gpu-viewer/vdpauVideoMixerParameter.txt","r") as file2:
			for i,line in enumerate(file2):
				if line.split()[1].strip('\n') == 'y':
					text = "True"
				else:
					text = "False"
				videoMixerParameterStore.append([line.split()[0].strip('\n'),text,"","",setBackgroundColor(i)])

	def vdpauVideoMixerAttribute():
		
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

	surfaceStore = Gtk.TreeStore(str,str,str,str)
	treeSurfaceLimits = Gtk.TreeView(surfaceStore,expand=True)

	surfaceScrollbar = createScrollbar(treeSurfaceLimits)
	surfaceGrid.add(surfaceScrollbar)

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
	vdpauVideoMixerParameter()
	vdpauVideoMixerAttribute()