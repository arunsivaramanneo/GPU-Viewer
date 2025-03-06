import sys
import gi
gi.require_version('Gtk','4.0')
gi.require_version(namespace='Adw', version='1')

from gi.repository import Gtk,GdkPixbuf,GObject,Gio,Adw
from Common import ExpandDataObject, setup_expander,bind_expander,setup,bind1,add_tree_node, ExpandDataObject2,add_tree_node2,bind2,bind3,bind4,fetchContentsFromCommand
from itertools import islice

Adw.init()

import const
import Filenames
import subprocess
from Common import copyContentsFromFile, getGpuImage,create_scrollbar, getRamInGb,createSubTab,getDriverVersion,getDeviceSize, setMargin,fetchContentsFromCommand,getVulkanVersion,createMainFile,getLogo

def VulkanVideo(videoTab):



    def vProfiles(gpu):
        
        vulkanVideoProfiles = fetchContentsFromCommand("vulkaninfo | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/Video Profiles/{flag=1;}flag' | awk /./ "%(gpu,gpu+1))

        vkVideoProfilesTab_Store.remove_all()
        
        for i in vulkanVideoProfiles:
            if "count" in i:
                toprow = ExpandDataObject(i.replace("count =",''),"")
            elif '==' in i:
                continue
            else:
                iter = ExpandDataObject(i,"")
                toprow.children.append(iter)
            
        vkVideoProfilesTab_Store.append(toprow)

    def vCapabilities(gpu):

        vulkanVideoCapabilities = fetchContentsFromCommand("vulkaninfo --show-video-props | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/Video Profiles/{flag=1;next}flag' | awk /./ "%(gpu,gpu+1))

        toprow = []; iter = None
        for i in vulkanVideoCapabilities:
            if "support" in i:
                if iter == None:
                    toprow = ExpandDataObject(i,"")
                else:
                    vkVideoCapabilitiesTab_Store.append(toprow)
                    toprow = ExpandDataObject(i,"")
                iter = i
                continue
            elif "Video Profile" in i or "Video Formats" in i:
                iter1 = ExpandDataObject(i,"")
                toprow.children.append(iter1)
                continue
            elif '----' in i or '==' in i:
                continue
            else:
                iter2 = ExpandDataObject(i,"")
                iter1.children.append(iter2)
            #    continue
                
        vkVideoCapabilitiesTab_Store.append(toprow)

    def radcall(combo,dummy):
        text = combo.props.selected
        print(text)
        vProfiles(text)
        vCapabilities(text)

        gpu_image = getGpuImage(gpu_list[text])
        image_renderer.set_pixbuf(gpu_image)






    grid = Gtk.Grid()
    grid.set_row_spacing(10)
    videoTab.append(grid)
    DevicesFrame = Gtk.Frame()
    grid.attach(DevicesFrame,0,1,1,1)




    # ---------------------------- Creating Vkvideo Tab ----------------------------------------------------------


    notebook = Gtk.Notebook()
    notebook.set_property("scrollable", True)
    notebook.set_property("enable-popup", True)
    grid.attach(notebook, 0, 2, 1, 1)

 # --------------------- Vulkan Video Profiles ---------------------------------------------------------------------

    vkVideoProfilesTab = Gtk.Box(spacing=10)
    vkVideoProfilesGrid = createSubTab(vkVideoProfilesTab,notebook,"Video Profiles")

    vkVideoProfilesColumnView = Gtk.ColumnView()
    vkVideoProfilesColumnView.props.show_row_separators = True
    vkVideoProfilesColumnView.props.show_column_separators = False

    factory_vkVideoProfiles = Gtk.SignalListItemFactory()
    factory_vkVideoProfiles.connect("setup",setup_expander)
    factory_vkVideoProfiles.connect("bind",bind_expander)

    factory_vkVideoProfiles_value = Gtk.SignalListItemFactory()
    factory_vkVideoProfiles_value.connect("setup",setup)
    factory_vkVideoProfiles_value.connect("bind",bind1)

    vkVideoProfilesSelection = Gtk.SingleSelection()
    vkVideoProfilesTab_Store = Gio.ListStore.new(ExpandDataObject)

    vkVideoModel = Gtk.TreeListModel.new(vkVideoProfilesTab_Store,False,True,add_tree_node)
    vkVideoProfilesSelection.set_model(vkVideoModel)

    vkVideoProfilesColumnView.set_model(vkVideoProfilesSelection)

    vkVideoProfilesColumnLhs = Gtk.ColumnViewColumn.new("Details",factory_vkVideoProfiles)
    vkVideoProfilesColumnLhs.set_resizable(True)
    vkVideoProfilesColumnRhs = Gtk.ColumnViewColumn.new("",factory_vkVideoProfiles_value)
    vkVideoProfilesColumnRhs.set_expand(True)

    vkVideoProfilesColumnView.append_column(vkVideoProfilesColumnLhs)
    vkVideoProfilesColumnView.append_column(vkVideoProfilesColumnRhs)

    vkVideoProfilesScrollbar = create_scrollbar(vkVideoProfilesColumnView)
    vkVideoProfilesGrid.attach(vkVideoProfilesScrollbar,0,0,1,1)


# -------------------- Vulkan Video Capabilities -------------------------------------------------------------------------------


    vkVideoCapabilitiesTab = Gtk.Box(spacing=10)
    vkVideoCapabilitiesGrid = createSubTab(vkVideoCapabilitiesTab,notebook,"Video Capabilities")

    vkVideoCapabilitiesColumnView = Gtk.ColumnView()
    vkVideoCapabilitiesColumnView.props.show_row_separators = True
    vkVideoCapabilitiesColumnView.props.show_column_separators = False

    factory_vkVideoCapabilities = Gtk.SignalListItemFactory()
    factory_vkVideoCapabilities.connect("setup",setup_expander)
    factory_vkVideoCapabilities.connect("bind",bind_expander)

    factory_vkVideoCapabilities_value = Gtk.SignalListItemFactory()
    factory_vkVideoCapabilities_value.connect("setup",setup)
    factory_vkVideoCapabilities_value.connect("bind",bind1)

    vkVideoCapabilitiesSelection = Gtk.SingleSelection()
    vkVideoCapabilitiesTab_Store = Gio.ListStore.new(ExpandDataObject)

    vkVideoModel = Gtk.TreeListModel.new(vkVideoCapabilitiesTab_Store,False,True,add_tree_node)
    vkVideoCapabilitiesSelection.set_model(vkVideoModel)

    vkVideoCapabilitiesColumnView.set_model(vkVideoCapabilitiesSelection)

    vkVideoCapabilitiesColumnLhs = Gtk.ColumnViewColumn.new("Details",factory_vkVideoCapabilities)
    vkVideoCapabilitiesColumnLhs.set_resizable(True)
    vkVideoCapabilitiesColumnRhs = Gtk.ColumnViewColumn.new("",factory_vkVideoCapabilities_value)
    vkVideoCapabilitiesColumnRhs.set_expand(True)

    vkVideoCapabilitiesColumnView.append_column(vkVideoCapabilitiesColumnLhs)
    vkVideoCapabilitiesColumnView.append_column(vkVideoCapabilitiesColumnRhs)

    vkVideoCapabilitiesScrollbar = create_scrollbar(vkVideoCapabilitiesColumnView)
    vkVideoCapabilitiesGrid.attach(vkVideoCapabilitiesScrollbar,0,0,1,1)


# -------------------- Vulkan Video Formats -------------------------------------------------------------------------------

    vkVideoFormatsTab = Gtk.Box(spacing=10)
    vkVideoFormatsGrid = createSubTab(vkVideoFormatsTab,notebook,"Video Formats")

    vkVideoFormatsColumnView = Gtk.ColumnView()
    vkVideoFormatsColumnView.props.show_row_separators = True
    vkVideoFormatsColumnView.props.show_column_separators = False

    factory_vkVideoFormats = Gtk.SignalListItemFactory()
    factory_vkVideoFormats.connect("setup",setup_expander)
    factory_vkVideoFormats.connect("bind",bind_expander)

    factory_vkVideoFormats_value = Gtk.SignalListItemFactory()
    factory_vkVideoFormats_value.connect("setup",setup)
    factory_vkVideoFormats_value.connect("bind",bind1)

    vkVideoFormatsSelection = Gtk.SingleSelection()
    vkVideoFormatsTab_Store = Gio.ListStore.new(ExpandDataObject)

    vkVideoModel = Gtk.TreeListModel.new(vkVideoFormatsTab_Store,False,True,add_tree_node)
    vkVideoFormatsSelection.set_model(vkVideoModel)

    vkVideoFormatsColumnView.set_model(vkVideoFormatsSelection)

    vkVideoFormatsColumnLhs = Gtk.ColumnViewColumn.new("Details",factory_vkVideoFormats)
    vkVideoFormatsColumnLhs.set_resizable(True)
    vkVideoFormatsColumnRhs = Gtk.ColumnViewColumn.new("",factory_vkVideoFormats_value)
    vkVideoFormatsColumnRhs.set_expand(True)

    vkVideoFormatsColumnView.append_column(vkVideoFormatsColumnLhs)
    vkVideoFormatsColumnView.append_column(vkVideoFormatsColumnRhs)

    vkVideoFormatsScrollbar = create_scrollbar(vkVideoFormatsColumnView)
    vkVideoFormatsGrid.attach(vkVideoFormatsScrollbar,0,0,1,1)


    DevicesGrid = Gtk.Grid()
#    videoTab.append(DevicesGrid)
    DevicesGrid.set_row_spacing(10)
    DevicesFrame.set_child(DevicesGrid)
#    print(fetchContentsFromCommand(Filenames.fetch_vulkaninfo_ouput_command+Filenames.fetch_device_name_command))
    gpu_list = fetchContentsFromCommand(Filenames.fetch_vulkaninfo_ouput_command+Filenames.fetch_device_name_command)
    availableDevices = Gtk.Label()
    setMargin(availableDevices,300,10,10)
    gpu_image = Gtk.Image()
    availableDevices.set_text("Available Device(s) :")
    DevicesGrid.attach(availableDevices, 10, 2, 20, 1)
    gpu_image = GdkPixbuf.Pixbuf.new_from_file_at_size(const.APP_LOGO_PNG, 100, 100)
    image_renderer = Gtk.Picture.new_for_pixbuf(gpu_image)
    gpu_DropDown = Gtk.DropDown()
    gpu_DropDown_list = Gtk.StringList()
    gpu_DropDown.set_model(gpu_DropDown_list)
    gpu_DropDown.connect('notify::selected-item',radcall)
    for i in range(len(gpu_list)-1):
        if "Video Profiles" in fetchContentsFromCommand("vulkaninfo | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | grep 'Video Profiles'"%(i,i+1))[0]:
            gpu_DropDown_list.append(gpu_list[i])


    setMargin(gpu_DropDown,30,10,10)
    setMargin(image_renderer,30,10,10)
    DevicesGrid.attach_next_to(gpu_DropDown,availableDevices,Gtk.PositionType.RIGHT,30,1)
    DevicesGrid.attach_next_to(image_renderer,gpu_DropDown,Gtk.PositionType.RIGHT,30,1)
