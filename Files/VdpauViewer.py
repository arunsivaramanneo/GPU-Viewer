import gi
import const
import Filenames
import subprocess
from Common import ExpandDataObject, setup_expander,bind_expander,setup,bind1,add_tree_node

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk,GObject,Gio,Adw
Adw.init()

from Common import setBackgroundColor, setColumns, createSubTab, create_scrollbar, createSubFrame, \
    colorTrueFalse, getDriverVersion, getVulkanVersion, getDeviceSize, refresh_filter, getRamInGb, fetchImageFromUrl, getFormatValue


decoderTitle = ["Decoder Name","Level","Macroblocks","Width","Height"]
videoMixerFeatureTitle = ["Name","Supported"]
surfaceVideoTitle = ["Surface","Width","Height","Types"]
surfaceOutputTitle = ["Output Surface","Width","Height","Types"]
SurfaceBitmapTitle = ["Bitmap Surface","Width","Height"]
vdpauinfoTitle = ["VDPAU Information","Details"]


def vdpauinfo(tab2):

	def vdpauInformation():

		fetch_vdpau_information_command = "cat %s | grep -E 'API|string' " %(Filenames.vdpauinfo_output_file)
		fetch_Vdpau_information_process = subprocess.Popen(fetch_vdpau_information_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
		vdpauinfo_information = fetch_Vdpau_information_process.communicate()[0].splitlines()

		for i,line in enumerate(vdpauinfo_information):
		#	vdpauinfoStore.append(None,[' '.join(line.split()[0:2]).strip('[]'),' '.join(line.split()[2:]).strip('[]'),setBackgroundColor(i)])
			toprow = ExpandDataObject(' '.join(line.split()[0:2]).strip('[]'),' '.join(line.split()[2:]).strip('[]'))
			vdpauinfoStore.append(toprow)	  
		#iter = vdpauinfoStore.append(None,["Supported Codecs:",' ',const.BGCOLOR3])
		
		iter = ExpandDataObject("Supported Codecs:",' ')
	#	vdpauinfoStore.append(iter)

		fetch_vdpau_decoder_capabilities_command = "cat %s | awk '/Decoder capabilities:/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./'" %(Filenames.vdpauinfo_output_file)
		fetch_vdpau_decoder_capabilities_process = subprocess.Popen(fetch_vdpau_decoder_capabilities_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
		vdpau_decoder_capabilities = fetch_vdpau_decoder_capabilities_process.communicate()[0].splitlines()
		
		i = 0
		for line in  vdpau_decoder_capabilities:
			if "not" not in line:
				iter2 = ExpandDataObject(line.split()[0].strip('\n')," ")
				iter.children.append(iter2)
			#	vdpauinfoStore.append(iter,[line.split()[0].strip('\n')," ",setBackgroundColor(i)])
				i = i + 1
		vdpauinfoStore.append(iter)

	#	treeVdpauInfo.expand_all()

	def decoderCapabilities():

		fetch_vdpau_decoder_capabilities_command = "cat %s | awk '/Decoder capabilities:/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./'" %(Filenames.vdpauinfo_output_file)
		fetch_vdpau_decoder_capabilities_process = subprocess.Popen(fetch_vdpau_decoder_capabilities_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
		vdpau_decoder_capabilities = fetch_vdpau_decoder_capabilities_process.communicate()[0].splitlines()

		for i,line in  enumerate(vdpau_decoder_capabilities):
			if "not" in line:
				decoderStore.append([line.split()[0].strip('\n'),"not supported","not supported","not supported","not supported",setBackgroundColor(i)])
			else:
				decoderStore.append([line.split()[0].strip('\n'),line.split()[1].strip('\n'),line.split()[2].strip('\n'),line.split()[3].strip('\n'),line.split()[4].strip('\n'),setBackgroundColor(i)])
	
	def videoSurfaceLimits():
		
		fetch_vdpau_surface_limits_command = "cat %s | awk '/Video surface:/{flag=1;next}/Decoder capabilities:/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Bitmap surface:/{flag=0}flag' | awk '/./'" %(Filenames.vdpauinfo_output_file)
		fetch_vdpau_surface_limits_process = subprocess.Popen(fetch_vdpau_surface_limits_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
		vdpau_surface_limits = fetch_vdpau_surface_limits_process.communicate()[0].splitlines()
	
		iter = surfaceVideoStore.append(None,["Video Surface","","","",const.BGCOLOR3])
		for i,line in enumerate(vdpau_surface_limits):
			surfaceVideoStore.append(iter,[line.split()[0].strip('\n'),line.split()[1].strip('\n'),line.split()[2].strip('\n'),(' '.join(line.split()[3:]).strip('[]')),setBackgroundColor(i)])

		fetch_vdpau_surface_output_limits_command = "cat %s | awk '/Output surface:/{flag=1;next}/Bitmap surface:/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Bitmap surface:/{flag=0}flag' | awk '/./' " %(Filenames.vdpauinfo_output_file)
		fetch_vdpau_surface_output_limits_process = subprocess.Popen(fetch_vdpau_surface_output_limits_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
		vdpau_surface_output_limits = fetch_vdpau_surface_output_limits_process.communicate()[0].splitlines()

		iter = surfaceVideoStore.append(None,["Output Surface","","","",const.BGCOLOR3])
		for i,line in enumerate(vdpau_surface_output_limits):
			surfaceVideoStore.append(iter,[line.split()[0].strip('\n'),line.split()[1].strip('\n'),line.split()[2],(' '.join(line.split()[4:]).strip('[]')),setBackgroundColor(i)])

		fetch_vdpau_surface_bitmap_limits_command = "cat %s | awk '/Bitmap surface:/{flag=1;next}/Video mixer:/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Video mixer:/{flag=0}flag' | awk '/./' " %(Filenames.vdpauinfo_output_file)
		fetch_vdpau_surface_bitmap_limits_process = subprocess.Popen(fetch_vdpau_surface_bitmap_limits_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
		vdpau_surface_bitmap_limits = fetch_vdpau_surface_bitmap_limits_process.communicate()[0].splitlines()

		iter = surfaceVideoStore.append(None,["Bitmap Surface","","","",const.BGCOLOR3])
		for i,line in enumerate(vdpau_surface_bitmap_limits):
			surfaceVideoStore.append(iter,[line.split()[0].strip('\n'),line.split()[1].strip('\n'),line.split()[2].strip('\n'),"",setBackgroundColor(i)])

		treeSurfaceVideoLimits.expand_all()

		
	def VideoMixerFeature():
		
		fetch_vdpau_mixer_features_command = "cat %s | awk '/feature name/{flag=1;next}/parameter name.*/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./' " %(Filenames.vdpauinfo_output_file)
		fetch_vdpau_mixer_features_process = subprocess.Popen(fetch_vdpau_mixer_features_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
		vdpau_video_mixer_feature = fetch_vdpau_mixer_features_process.communicate()[0].splitlines()

		iter = videoMixerFeatureStore.append(None,["Features","",const.BGCOLOR3,""])
		for i,line in enumerate(vdpau_video_mixer_feature):
			if 'y'in line:
				text = "true"
				fgcolor = const.COLOR1
			else:
				text = "false"
				fgcolor = const.COLOR2
			if "HIGH" in line:
				videoMixerFeatureStore.append(iter,[(' '.join(line.split()[0:5])).strip('[]'),text,setBackgroundColor(i),fgcolor])
			else:
				videoMixerFeatureStore.append(iter,[line.split()[0].strip('\n'),text,setBackgroundColor(i),fgcolor])
		
		fetch_vdpau_mixer_parameter_command = "cat %s | awk '/parameter name/{flag=1;next}/attribute name.*/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./' " %(Filenames.vdpauinfo_output_file)
		fetch_vdpau_mixer_parameter_process = subprocess.Popen(fetch_vdpau_mixer_parameter_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
		vdpau_video_mixer_parameters =  fetch_vdpau_mixer_parameter_process.communicate()[0].splitlines()

		iter = videoMixerFeatureStore.append(None,["Parameters","",const.BGCOLOR3,""])
		for i,line in enumerate(vdpau_video_mixer_parameters):
			if line.split()[1].strip('\n') == 'y':
				text = "true"
				fgcolor = const.COLOR1
			else:
				text = "false"
				fgcolor = const.COLOR2
			videoMixerFeatureStore.append(iter,[line.split()[0].strip('\n'),text,setBackgroundColor(i),fgcolor])
		
		fetch_vdpau_mixer_attribute_command = "cat %s | awk '/Video mixer:/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/attribute name/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./' " %(Filenames.vdpauinfo_output_file)
		fetch_vdpau_mixer_attribute_process = subprocess.Popen(fetch_vdpau_mixer_attribute_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
		vdpau_video_mixer_attribute = fetch_vdpau_mixer_attribute_process.communicate()[0].splitlines()

		iter = videoMixerFeatureStore.append(None,["Attributes","",const.BGCOLOR3,""])
		for i,line in enumerate(vdpau_video_mixer_attribute):
			if line.split()[1].strip('\n') == 'y':
				text = "true"
				fgcolor = const.COLOR1
			else:
				text = "false"
				fgcolor = const.COLOR2
			videoMixerFeatureStore.append(iter,[line.split()[0].strip('\n'),text,setBackgroundColor(i),fgcolor])


		treeVideoMixerFeature.expand_all()


	grid = Gtk.Grid()
	tab2.append(grid)
	DevicesFrame = Gtk.Frame()
	grid.attach(DevicesFrame,0,0,1,1)

	notebook = Gtk.Notebook()
	notebook.set_property("scrollable", True)
	notebook.set_property("enable-popup", True)
	grid.attach(notebook, 0, 2, 1, 1)

# ------- VDPAU information -------------------------------


	vdpauinfoTab = Gtk.Box(spacing=20)
	vdpauinfoGrid = createSubTab(vdpauinfoTab,notebook, "VDPAU Information")
	
	vdpauinfoColumnView = Gtk.ColumnView()
	vdpauinfoColumnView.props.show_row_separators = True
	vdpauinfoColumnView.props.show_column_separators = False
	
	factory_vdpau = Gtk.SignalListItemFactory()
	factory_vdpau.connect("setup",setup_expander)
	factory_vdpau.connect("bind",bind_expander)
	
	factory_vdpau_value = Gtk.SignalListItemFactory()
	factory_vdpau_value.connect("setup",setup)
	factory_vdpau_value.connect("bind",bind1)
	
	vdpauSelection = Gtk.SingleSelection()
	vdpauinfoStore = Gio.ListStore.new(ExpandDataObject)
	
	vdpauModel = Gtk.TreeListModel.new(vdpauinfoStore,False,True,add_tree_node)
	vdpauSelection.set_model(vdpauModel)
	
	vdpauinfoColumnView.set_model(vdpauSelection)
	
	vdpauColumnLhs = Gtk.ColumnViewColumn.new("VDPAU Information",factory_vdpau)
	vdpauColumnLhs.set_resizable(True)
	vdpauColumnRhs = Gtk.ColumnViewColumn.new("Details",factory_vdpau_value)
	vdpauColumnRhs.set_expand(True)
	
	vdpauinfoColumnView.append_column(vdpauColumnLhs)
	vdpauinfoColumnView.append_column(vdpauColumnRhs)

	
#	vdpauinfoStore = Gtk.TreeStore(str,str,str)
#	treeVdpauInfo = Gtk.TreeView.new_with_model(vdpauinfoStore)
#	treeVdpauInfo.set_property("enable-grid-lines",1)

#	setColumns(treeVdpauInfo,vdpauinfoTitle,300,0.0)

	vdpauinfoScrollbar = create_scrollbar(vdpauinfoColumnView)
	vdpauinfoGrid.attach(vdpauinfoScrollbar,0,0,1,1)

# ------- Decoder Capabilities ----------------------------
	
	decoderTab = Gtk.Box(spacing=20)
	decoderGrid = createSubTab(decoderTab, notebook, "Decoder Capabilities")

	decoderStore = Gtk.ListStore(str,str,str,str,str,str)
	treeDecoder = Gtk.TreeView.new_with_model(decoderStore)
	treeDecoder.set_property("enable-grid-lines",1)

	setColumns(treeDecoder, decoderTitle, 300, 0.0)

	decoderScrollbar = create_scrollbar(treeDecoder)
	decoderGrid.attach(decoderScrollbar,0,0,1,1)

# -------- Surface Limits -----------------------------------

	surfaceTab = Gtk.Box(spacing=20)
	surfaceGrid = createSubTab(surfaceTab,notebook,"Surface Limits")

	surfaceVideoStore = Gtk.TreeStore(str,str,str,str,str)
	treeSurfaceVideoLimits = Gtk.TreeView.new_with_model(surfaceVideoStore)
	treeSurfaceVideoLimits.set_property("enable-grid-lines",1)

	setColumns(treeSurfaceVideoLimits,surfaceVideoTitle,300,0.0)

	surfaceVideoScrollbar = create_scrollbar(treeSurfaceVideoLimits)
	surfaceGrid.attach(surfaceVideoScrollbar,0,0,1,1)

	
# -------- Video Mixer ---------------------------------------

	videoMixerTab = Gtk.Box(spacing=20)
	videoMixerGrid = createSubTab(videoMixerTab,notebook,"Video Mixer")
	videoMixerGrid.set_row_spacing(20)

	videoMixerFeatureStore = Gtk.TreeStore(str,str,str,str)
	treeVideoMixerFeature = Gtk.TreeView.new_with_model(videoMixerFeatureStore)
	treeVideoMixerFeature.set_property("enable-grid-lines", 1)
	treeVideoMixerFeature.set_enable_search(True)

	for i, column_title in enumerate(videoMixerFeatureTitle):
		videoMixerrenderer = Gtk.CellRendererText()
		column = Gtk.TreeViewColumn(column_title, videoMixerrenderer, text=i)
		column.add_attribute(videoMixerrenderer, "background", 2)
		column.set_sort_column_id(i)
		column.set_resizable(True)
		column.set_reorderable(True)
		if i > 0:
			column.add_attribute(videoMixerrenderer, "foreground", 3)
		treeVideoMixerFeature.set_property("can-focus", False)
		treeVideoMixerFeature.append_column(column)

	
	videoMixerFeatureScrollbar = create_scrollbar(treeVideoMixerFeature)
	videoMixerGrid.attach(videoMixerFeatureScrollbar,0,0,1,1)




	decoderCapabilities()
	videoSurfaceLimits()
	VideoMixerFeature()
	vdpauInformation()
