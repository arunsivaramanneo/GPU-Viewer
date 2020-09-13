import os
import gi
import Const

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from Common import copyContentsFromFile, setBackgroundColor, setColumns, createSubTab, createScrollbar, createSubFrame, \
    colorTrueFalse, getDriverVersion, getVulkanVersion, getDeviceSize, refresh_filter, getRamInGb, fetchImageFromUrl, getFormatValue


decoderTitle = ["Name","Level","MACROBLOCKS","Width","height"]

def vdpauinfo(tab2):

	def decoderCapabilities():

		os.system("vdpauinfo | awk '/Decoder capabilities:/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./'> /tmp/gpu-viewer/vdpauinfo.txt")
		with open("/tmp/gpu-viewer/vdpauinfo.txt","r") as file1:
			for i,line in  enumerate(file1):
				print(line.split())
				if "not" in line:
					decoderStore.append([line.split()[0].strip('\n'),"not supported","not supported","not supported","not supported",setBackgroundColor(i)])
				else:
					decoderStore.append([line.split()[0].strip('\n'),line.split()[1].strip('\n'),line.split()[2].strip('\n'),line.split()[3].strip('\n'),line.split()[4].strip('\n'),setBackgroundColor(i)])
	
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

	videoMixerStore = Gtk.TreeStore(str,str,str,str)

	treeVideoMixer = Gtk.TreeView(videoMixerStore,expand=True)

	videoMixerScrollbar = createScrollbar(treeVideoMixer)
	videoMixerGrid.add(videoMixerScrollbar)

	decoderCapabilities()