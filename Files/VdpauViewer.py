import gi
import const
import Filenames
import subprocess
from Common import ExpandDataObject, setup_expander,bind_expander,setup,bind1,add_tree_node, ExpandDataObject2,add_tree_node2,bind2,bind3,bind4,setMargin

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk,GObject,Gio,Adw
Adw.init()

from Common import createSubTab, create_scrollbar

class DataObject(GObject.GObject):
    def __init__(self, column1: str,column2: str,column3: str,column4: str,column5: str):
        super(DataObject, self).__init__()
        self.column1 = column1
        self.column2 = column2
        self.column3 = column3
        self.column4 = column4
        self.column4 = column5

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
				decoderStore.append(ExpandDataObject2(line.split()[0].strip('\n'),"not supported","not supported","not supported","not supported"))
			else:
				decoderStore.append(ExpandDataObject2(line.split()[0].strip('\n'),line.split()[1].strip('\n'),line.split()[2].strip('\n'),line.split()[3].strip('\n'),line.split()[4].strip('\n')))
	
	def videoSurfaceLimits():
		
		fetch_vdpau_surface_limits_command = "cat %s | awk '/Video surface:/{flag=1;next}/Decoder capabilities:/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Bitmap surface:/{flag=0}flag' | awk '/./'" %(Filenames.vdpauinfo_output_file)
		fetch_vdpau_surface_limits_process = subprocess.Popen(fetch_vdpau_surface_limits_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
		vdpau_surface_limits = fetch_vdpau_surface_limits_process.communicate()[0].splitlines()
	
		toprow = ExpandDataObject2("Video Surface","","","","")
		for i,line in enumerate(vdpau_surface_limits):
			iter = ExpandDataObject2(line.split()[0].strip('\n'),line.split()[1].strip('\n'),line.split()[2].strip('\n'),(' '.join(line.split()[3:]).strip('[]')),"")
			toprow.children.append(iter)
		surfaceVideoStore.append(toprow)

		fetch_vdpau_surface_output_limits_command = "cat %s | awk '/Output surface:/{flag=1;next}/Bitmap surface:/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Bitmap surface:/{flag=0}flag' | awk '/./' " %(Filenames.vdpauinfo_output_file)
		fetch_vdpau_surface_output_limits_process = subprocess.Popen(fetch_vdpau_surface_output_limits_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
		vdpau_surface_output_limits = fetch_vdpau_surface_output_limits_process.communicate()[0].splitlines()

		toprow = ExpandDataObject2("Output Surface","","","","")
		for i,line in enumerate(vdpau_surface_output_limits):
			iter = ExpandDataObject2(line.split()[0].strip('\n'),line.split()[1].strip('\n'),line.split()[2],(' '.join(line.split()[4:]).strip('[]')),"")
			toprow.children.append(iter)
		surfaceVideoStore.append(toprow)

		fetch_vdpau_surface_bitmap_limits_command = "cat %s | awk '/Bitmap surface:/{flag=1;next}/Video mixer:/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Video mixer:/{flag=0}flag' | awk '/./' " %(Filenames.vdpauinfo_output_file)
		fetch_vdpau_surface_bitmap_limits_process = subprocess.Popen(fetch_vdpau_surface_bitmap_limits_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
		vdpau_surface_bitmap_limits = fetch_vdpau_surface_bitmap_limits_process.communicate()[0].splitlines()

		toprow = ExpandDataObject2("Bitmap Surface","","","","")
		for i,line in enumerate(vdpau_surface_bitmap_limits):
			iter = ExpandDataObject2(line.split()[0].strip('\n'),line.split()[1].strip('\n'),line.split()[2].strip('\n'),"",setBackgroundColor(i))
			toprow.children.append(iter)
		surfaceVideoStore.append(toprow)

		
	def VideoMixerFeature():
		
		fetch_vdpau_mixer_features_command = "cat %s | awk '/feature name/{flag=1;next}/parameter name.*/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./' " %(Filenames.vdpauinfo_output_file)
		fetch_vdpau_mixer_features_process = subprocess.Popen(fetch_vdpau_mixer_features_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
		vdpau_video_mixer_feature = fetch_vdpau_mixer_features_process.communicate()[0].splitlines()

		toprow = ExpandDataObject2("Features","","","","")
		for i,line in enumerate(vdpau_video_mixer_feature):
			if 'y'in line:
				text = "true"
				fgcolor = const.COLOR1
			else:
				text = "false"
				fgcolor = const.COLOR2
			if "HIGH" in line:
				iter = ExpandDataObject2((' '.join(line.split()[0:5])).strip('[]'),text,"","","")
				toprow.children.append(iter)
			else:
				iter = ExpandDataObject2(line.split()[0].strip('\n'),text,"","","")
				toprow.children.append(iter)
		videoMixerFeatureStore.append(toprow)
		
		fetch_vdpau_mixer_parameter_command = "cat %s | awk '/parameter name/{flag=1;next}/attribute name.*/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./' " %(Filenames.vdpauinfo_output_file)
		fetch_vdpau_mixer_parameter_process = subprocess.Popen(fetch_vdpau_mixer_parameter_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
		vdpau_video_mixer_parameters =  fetch_vdpau_mixer_parameter_process.communicate()[0].splitlines()

		toprow = ExpandDataObject2("Parameters","","","","")
		for i,line in enumerate(vdpau_video_mixer_parameters):
			if line.split()[1].strip('\n') == 'y':
				text = "true"
				fgcolor = const.COLOR1
			else:
				text = "false"
			iter = ExpandDataObject2(line.split()[0].strip('\n'),text,"","","")
			toprow.children.append(iter)

		videoMixerFeatureStore.append(toprow)		
		
		fetch_vdpau_mixer_attribute_command = "cat %s | awk '/Video mixer:/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/attribute name/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/-------.*/{flag=1;next}/Output surface:/{flag=0}flag' | awk '/./' " %(Filenames.vdpauinfo_output_file)
		fetch_vdpau_mixer_attribute_process = subprocess.Popen(fetch_vdpau_mixer_attribute_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
		vdpau_video_mixer_attribute = fetch_vdpau_mixer_attribute_process.communicate()[0].splitlines()

		toprow = ExpandDataObject2("Attributes","","","","")
		for i,line in enumerate(vdpau_video_mixer_attribute):
			if line.split()[1].strip('\n') == 'y':
				text = "true"
				fgcolor = const.COLOR1
			else:
				text = "false"
			iter = ExpandDataObject2(line.split()[0].strip('\n'),text,"","","")
			toprow.children.append(iter)

		videoMixerFeatureStore.append(toprow	)

	

	def _on_search_method_changed(search_entry,filterColumn):
		filterColumn.changed(Gtk.FilterChange.DIFFERENT)

	def _do_filter_decoder_view(item, filter_list_model):
		search_text_widget = decoderSearchEntry.get_text()
		return search_text_widget.upper() in item.data.upper()


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

	decoderInfoColumnView = Gtk.ColumnView()
	decoderInfoColumnView.props.show_row_separators = True
	decoderInfoColumnView.props.show_column_separators = False
	
	factory_decoder = Gtk.SignalListItemFactory()
	factory_decoder.connect("setup",setup_expander)
	factory_decoder.connect("bind",bind_expander)
	
	factory_decoder_value1 = Gtk.SignalListItemFactory()
	factory_decoder_value1.connect("setup",setup)
	factory_decoder_value1.connect("bind",bind1)
	

	factory_decoder_value2 = Gtk.SignalListItemFactory()
	factory_decoder_value2.connect("setup",setup)
	factory_decoder_value2.connect("bind",bind2)


	factory_decoder_value3 = Gtk.SignalListItemFactory()
	factory_decoder_value3.connect("setup",setup)
	factory_decoder_value3.connect("bind",bind3)


	factory_decoder_value4 = Gtk.SignalListItemFactory()
	factory_decoder_value4.connect("setup",setup)
	factory_decoder_value4.connect("bind",bind4)

	decoderSelection = Gtk.SingleSelection()
	decoderStore = Gio.ListStore.new(ExpandDataObject2)
	filterSortDecoderStore = Gtk.FilterListModel(model=decoderStore)
	filter_decoder = Gtk.CustomFilter.new(_do_filter_decoder_view, filterSortDecoderStore)
	filterSortDecoderStore.set_filter(filter_decoder)
	
	vdpauModel = Gtk.TreeListModel.new(filterSortDecoderStore,False,True,add_tree_node2)
	decoderSelection.set_model(vdpauModel)
	
	decoderInfoColumnView.set_model(decoderSelection)
	
	decoderColumnLhs = Gtk.ColumnViewColumn.new("Decoder name",factory_decoder)
	decoderColumnLhs.set_resizable(True)
	decoderColumnRhs1 = Gtk.ColumnViewColumn.new("Level",factory_decoder_value1)
	decoderColumnRhs1.set_expand(True)
	decoderColumnRhs2 = Gtk.ColumnViewColumn.new("Macroblocks",factory_decoder_value2)
	decoderColumnRhs2.set_expand(True)
	decoderColumnRhs3 = Gtk.ColumnViewColumn.new("Width",factory_decoder_value3)
	decoderColumnRhs3.set_expand(True)
	decoderColumnRhs4 = Gtk.ColumnViewColumn.new("Height",factory_decoder_value4)
	decoderColumnRhs4.set_expand(True)
	
	decoderInfoColumnView.append_column(decoderColumnLhs)
	decoderInfoColumnView.append_column(decoderColumnRhs1)
	decoderInfoColumnView.append_column(decoderColumnRhs2)
	decoderInfoColumnView.append_column(decoderColumnRhs3)
	decoderInfoColumnView.append_column(decoderColumnRhs4)

#	decoderStore = Gtk.ListStore(str,str,str,str,str,str)
#	treeDecoder = Gtk.TreeView.new_with_model(decoderStore)
#	treeDecoder.set_property("enable-grid-lines",1)

#	setColumns(treeDecoder, decoderTitle, 300, 0.0)
	decoderSearchEntry = Gtk.SearchEntry()
	setMargin(decoderSearchEntry,0,5,0)
	decoderSearchEntry.set_property("placeholder_text","Type here to filter.....")
	decoderSearchEntry.connect("search-changed", _on_search_method_changed,filter_decoder)

	decoderScrollbar = create_scrollbar(decoderInfoColumnView)
	decoderGrid.attach(decoderSearchEntry,0,0,15,1)
	decoderGrid.attach_next_to(decoderScrollbar, decoderSearchEntry, Gtk.PositionType.BOTTOM, 15, 1)


# -------- Surface Limits -----------------------------------

	surfaceTab = Gtk.Box(spacing=20)
	surfaceGrid = createSubTab(surfaceTab,notebook,"Surface Limits")

	vdpauSurfaceColumnView = Gtk.ColumnView()
	vdpauSurfaceColumnView.props.show_row_separators = True
	vdpauSurfaceColumnView.props.show_column_separators = False
	
	factory_surface_limits = Gtk.SignalListItemFactory()
	factory_surface_limits.connect("setup",setup_expander)
	factory_surface_limits.connect("bind",bind_expander)
	
	factory_surface_limits_value1 = Gtk.SignalListItemFactory()
	factory_surface_limits_value1.connect("setup",setup)
	factory_surface_limits_value1.connect("bind",bind1)
	

	factory_surface_limits_value2 = Gtk.SignalListItemFactory()
	factory_surface_limits_value2.connect("setup",setup)
	factory_surface_limits_value2.connect("bind",bind2)


	factory_surface_limits_value3 = Gtk.SignalListItemFactory()
	factory_surface_limits_value3.connect("setup",setup)
	factory_surface_limits_value3.connect("bind",bind3)


	vdpauSurfaceSelection = Gtk.SingleSelection()
	surfaceVideoStore = Gio.ListStore.new(ExpandDataObject2)
	
	vdpauSurfaceModel = Gtk.TreeListModel.new(surfaceVideoStore,False,True,add_tree_node2)
	vdpauSurfaceSelection.set_model(vdpauSurfaceModel)
	
	vdpauSurfaceColumnView.set_model(vdpauSurfaceSelection)
	
	vdpauSurfaceColumnLhs = Gtk.ColumnViewColumn.new("Suface",factory_surface_limits)
	vdpauSurfaceColumnLhs.set_resizable(True)
	vdpauSurfaceColumnLhs.set_expand(True)
	vdpauSurfaceColumnRhs1 = Gtk.ColumnViewColumn.new("Width",factory_surface_limits_value1)
	vdpauSurfaceColumnRhs1.set_expand(True)
	vdpauSurfaceColumnRhs2 = Gtk.ColumnViewColumn.new("Height",factory_surface_limits_value2)
	vdpauSurfaceColumnRhs2.set_expand(True)
	vdpauSurfaceColumnRhs3 = Gtk.ColumnViewColumn.new("Types",factory_surface_limits_value3)
	vdpauSurfaceColumnRhs3.set_expand(True)
	
	vdpauSurfaceColumnView.append_column(vdpauSurfaceColumnLhs)
	vdpauSurfaceColumnView.append_column(vdpauSurfaceColumnRhs1)
	vdpauSurfaceColumnView.append_column(vdpauSurfaceColumnRhs2)
	vdpauSurfaceColumnView.append_column(vdpauSurfaceColumnRhs3)


#	surfaceVideoStore = Gtk.TreeStore(str,str,str,str,str)
#	treeSurfaceVideoLimits = Gtk.TreeView.new_with_model(surfaceVideoStore)
#	treeSurfaceVideoLimits.set_property("enable-grid-lines",1)

#	setColumns(treeSurfaceVideoLimits,surfaceVideoTitle,300,0.0)

	surfaceVideoScrollbar = create_scrollbar(vdpauSurfaceColumnView)
	surfaceGrid.attach(surfaceVideoScrollbar,0,0,1,1)

	
# -------- Video Mixer ---------------------------------------

	videoMixerTab = Gtk.Box(spacing=20)
	videoMixerGrid = createSubTab(videoMixerTab,notebook,"Video Mixer")
	videoMixerGrid.set_row_spacing(20)

	videoMixerColumnView = Gtk.ColumnView()
	videoMixerColumnView.props.show_row_separators = True
	videoMixerColumnView.props.show_column_separators = False
	
	factory_video_mixer = Gtk.SignalListItemFactory()
	factory_video_mixer.connect("setup",setup_expander)
	factory_video_mixer.connect("bind",bind_expander)
	
	factory_video_mixer_value = Gtk.SignalListItemFactory()
	factory_video_mixer_value.connect("setup",setup)
	factory_video_mixer_value.connect("bind",bind1)

	videoMixerSelection = Gtk.SingleSelection()
	videoMixerFeatureStore = Gio.ListStore.new(ExpandDataObject2)
	
	videoMixerModel = Gtk.TreeListModel.new(videoMixerFeatureStore,False,True,add_tree_node2)
	videoMixerSelection.set_model(videoMixerModel)
	
	videoMixerColumnView.set_model(videoMixerSelection)
	
	videoMixerColumnLhs = Gtk.ColumnViewColumn.new("Name",factory_video_mixer)
	videoMixerColumnLhs.set_resizable(True)
	videoMixerColumnRhs1 = Gtk.ColumnViewColumn.new("Supported",factory_video_mixer_value)
	videoMixerColumnRhs1.set_expand(True)
	
	videoMixerColumnView.append_column(videoMixerColumnLhs)
	videoMixerColumnView.append_column(videoMixerColumnRhs1)
	
	videoMixerFeatureScrollbar = create_scrollbar(videoMixerColumnView)
	videoMixerGrid.attach(videoMixerFeatureScrollbar,0,0,1,1)




	decoderCapabilities()
	videoSurfaceLimits()
	VideoMixerFeature()
	vdpauInformation()
