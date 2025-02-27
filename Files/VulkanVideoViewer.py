import sys
import gi
gi.require_version('Gtk','4.0')
gi.require_version(namespace='Adw', version='1')

from gi.repository import Gtk,GdkPixbuf,GObject,Gio,Adw
from Common import ExpandDataObject, setup_expander,bind_expander,setup,bind1,add_tree_node, ExpandDataObject2,add_tree_node2,bind2,bind3,bind4,fetchContentsFromCommand


Adw.init()

import const
import Filenames
import subprocess
from Common import copyContentsFromFile, getGpuImage,create_scrollbar, getRamInGb,createSubTab,getDriverVersion,getDeviceSize, setMargin,fetchContentsFromCommand,getVulkanVersion,createMainFile,getLogo

def VulkanVideo(videoTab):



    def vProfiles(gpu):
        
        vulkanProfiles = fetchContentsFromCommand("vulkaninfo | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/Video Profiles/{flag=1;}flag' | awk /./"%(gpu,gpu+1))

        vkVideoTab_Store.remove_all()
        
        for i in vulkanProfiles:
            if "count" in i:
                toprow = ExpandDataObject(i.replace("count =",''),"")
            elif '==' in i:
                continue
            else:
                iter = ExpandDataObject(i,"")
                toprow.children.append(iter)
            
        vkVideoTab_Store.append(toprow)



    def radcall(combo,dummy):
        text = combo.props.selected
        print(text)
        vProfiles(text)

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



    vkVideoTab = Gtk.Box(spacing=10)
    vkVideoGrid = createSubTab(vkVideoTab,notebook,"Video Profiles")

    vkVideoColumnView = Gtk.ColumnView()
    vkVideoColumnView.props.show_row_separators = True
    vkVideoColumnView.props.show_column_separators = False

    factory_vkVideo = Gtk.SignalListItemFactory()
    factory_vkVideo.connect("setup",setup_expander)
    factory_vkVideo.connect("bind",bind_expander)

    factory_vkVideo_value = Gtk.SignalListItemFactory()
    factory_vkVideo_value.connect("setup",setup)
    factory_vkVideo_value.connect("bind",bind1)

    vkVideoSelection = Gtk.SingleSelection()
    vkVideoTab_Store = Gio.ListStore.new(ExpandDataObject)

    vkVideoModel = Gtk.TreeListModel.new(vkVideoTab_Store,False,True,add_tree_node)
    vkVideoSelection.set_model(vkVideoModel)

    vkVideoColumnView.set_model(vkVideoSelection)

    vkVideoColumnLhs = Gtk.ColumnViewColumn.new("Details",factory_vkVideo)
    vkVideoColumnLhs.set_resizable(True)
    vkVideoColumnRhs = Gtk.ColumnViewColumn.new("",factory_vkVideo_value)
    vkVideoColumnRhs.set_expand(True)

    vkVideoColumnView.append_column(vkVideoColumnLhs)
    vkVideoColumnView.append_column(vkVideoColumnRhs)

    vkVideoScrollbar = create_scrollbar(vkVideoColumnView)
    vkVideoGrid.attach(vkVideoScrollbar,0,0,1,1)

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
