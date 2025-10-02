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
        
        vulkanVideoProfiles = fetchContentsFromCommand("vulkaninfo | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/Video Profiles/{flag=1;}flag' | awk /./ | awk '!/===/' "%(gpu,gpu+1))
        vulkanVideoProfilesUniq = fetchContentsFromCommand(r"vulkaninfo | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/Video Profiles/{flag=1;next}flag' | awk /./ | awk '!/===/' | awk '{gsub(/\(.*/, 'True');print}' | uniq "%(gpu,gpu+1))
        
        vulkanVideoProfilesCount = []
        for i in range(len(vulkanVideoProfilesUniq)):
            count = 0
            for profile in vulkanVideoProfiles:
                if vulkanVideoProfilesUniq[i] in profile:
                    count = count + 1
            vulkanVideoProfilesCount.append(count)

        vkVideoProfilesTab_Store.remove_all()
        vulkanVideoProfilesUniq.append("")

        j = 0; k = 0 ; group = None
        for line in vulkanVideoProfiles:
            if 'Video Profiles' in line:
                toprow = ExpandDataObject(line.replace('count =',''),"")
                continue
            if vulkanVideoProfilesUniq[j] in line and j <= len(vulkanVideoProfilesUniq) - 2:
                iter = ExpandDataObject(vulkanVideoProfilesUniq[j].replace("placeholder =","")+": %d" %vulkanVideoProfilesCount[j],"")
                toprow.children.append(iter)
                iter2 = ExpandDataObject(line.replace("placeholder =",""),"")
                iter.children.append(iter2)
                j = j + 1
            else:
                if vulkanVideoProfilesUniq[j] in line:
                    iter2 = ExpandDataObject(line.replace("placeholder =",""),"")
                    iter.children.append(iter2)
                    continue
                else:
                    iter2 = ExpandDataObject(line.replace("placeholder =",""),"")
                    iter.children.append(iter2)
                #    iter.children.append(iter2)
                    continue


        vkVideoProfilesTab_Store.append(toprow)

    def vDefinitions(gpu):

        vulkanVideoProfileDefinition = fetchContentsFromCommand("vulkaninfo --show-video-props | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/Video Profiles/{flag=1;next}flag' | awk '/Video Profile Definition/{flag=1}/Video Profile Capabilities/{flag=0}flag'| awk /./ | awk '!/---|===/' "%(gpu,gpu+1))
        vulkanVideoProfileDefinitionLHS = fetchContentsFromCommand("vulkaninfo --show-video-props | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/Video Profiles/{flag=1;next}flag' | awk '/Video Profile Definition/{flag=1}/Video Profile Capabilities/{flag=0}flag'| awk /./ | awk '!/---|===/' | awk '{gsub(/[=,:].*/,'True')l}1' "%(gpu,gpu+1))
        vulkanVideoProfileDefinitionRHS = fetchContentsFromCommand("vulkaninfo --show-video-props | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/Video Profiles/{flag=1;next}flag' | awk '/Video Profile Definition/{flag=1}/Video Profile Capabilities/{flag=0}flag'| awk /./ | awk '!/---|===/' | grep -o [=].* | grep -o ' .*' "%(gpu,gpu+1))

        vulkanVideoProfiles = fetchContentsFromCommand("vulkaninfo | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/Video Profiles/{flag=1;}flag' | awk /./ | awk '!/===/' | grep placeholder "%(gpu,gpu+1))
        vulkanVideoProfiles.append("")

        vkVideoProfileDefinitionTab_Store.remove_all()
        group = None
        j = 0;i =0 ;k = 0
        for line in vulkanVideoProfileDefinition:
            if '=' in line and "Video Profile Definition" not in line:
                rhs = vulkanVideoProfileDefinitionRHS[k].replace('count =','')
                k = k + 1
            else:
                rhs = ""
            if "Video Profile Definition" in line:
                if group == None:
                    iter1 = ExpandDataObject((vulkanVideoProfiles[j]).replace("placeholder =",""),"")
                else:
                    vkVideoProfileDefinitionTab_Store.append(iter1)
                    iter1 = ExpandDataObject((vulkanVideoProfiles[j]).replace("placeholder =",""),"")
                j = j + 1
                i = i + 1
                group = line
                continue
            elif "\t" in line and "\t\t" not in line:
                iter2 = ExpandDataObject(vulkanVideoProfileDefinitionLHS[i].strip("\t"),rhs)
                iter1.children.append(iter2)
                i = i + 1
                continue
            elif "\t\t" in line and "\t\t\t" not in line:
                iter3 = ExpandDataObject(vulkanVideoProfileDefinitionLHS[i].strip("\t"),rhs)
                iter2.children.append(iter3)
                i = i + 1
                continue
            elif "\t\t\t" in line and "\t\t\t\t" not in line:
                iter4 = ExpandDataObject(vulkanVideoProfileDefinitionLHS[i].strip("\t"),rhs)
                iter3.children.append(iter4)
                i = i + 1
                continue            
            elif "\t\t\t\t" in line and "\t\t\t\t\t" not in line:
                iter5 = ExpandDataObject(vulkanVideoProfileDefinitionLHS[i].strip("\t"),rhs)
                iter4.children.append(iter5)
                i = i + 1
                continue    
            else:
                iter6 = ExpandDataObject(vulkanVideoProfileDefinitionLHS[i].strip("\t"),rhs)
                iter5.children.append(iter6)
                i = i + 1
    #        #   continue
            
                
        vkVideoProfileDefinitionTab_Store.append(iter1)

    def vCapabitlies(gpu):

        vulkanVideoCapabilities = fetchContentsFromCommand("vulkaninfo --show-video-props | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/Video Profiles/{flag=1;next}flag' | awk '/Video Profile Capabilities/{flag=1}/Video Formats/{flag=0}flag'| awk /./ | awk '!/---|===/' "%(gpu,gpu+1))
        vulkanVideoCapabilitiesLHS = fetchContentsFromCommand("vulkaninfo --show-video-props | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/Video Profiles/{flag=1;next}flag' | awk '/Video Profile Capabilities/{flag=1}/Video Formats/{flag=0}flag'| awk /./ | awk '!/---|===/' | awk '{gsub(/[=,:].*/,'True')l}1' "%(gpu,gpu+1))
        vulkanVideoCapabilitiesRHS = fetchContentsFromCommand("vulkaninfo --show-video-props | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/Video Profiles/{flag=1;next}flag' | awk '/Video Profile Capabilities/{flag=1}/Video Formats/{flag=0}flag'| awk /./ | awk '!/---|===/' | grep -o [=].* | grep -o ' .*' "%(gpu,gpu+1))

        vulkanVideoProfiles = fetchContentsFromCommand("vulkaninfo | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/Video Profiles/{flag=1;}flag' | awk /./ | awk '!/===/' | grep placeholder "%(gpu,gpu+1))
        vulkanVideoProfiles.append("")

        vkVideoCapabilitiesTab_Store.remove_all()
        toprow = []; group = None
        j = 0;i = 0 ; k = 0
        for line in vulkanVideoCapabilities:
            if '=' in line:
                rhs = vulkanVideoCapabilitiesRHS[k].replace('count =','')
                k = k + 1
            else:
                rhs = ""
            if "Video Profile Capabilities" in line:
                if group == None:
                    iter1 = ExpandDataObject((vulkanVideoProfiles[j]).replace("placeholder =",""),"")
                else:
                    vkVideoCapabilitiesTab_Store.append(iter1)
                    iter1 = ExpandDataObject((vulkanVideoProfiles[j]).replace("placeholder =",""),"")
                j = j + 1
                i = i + 1
                group = line
                continue
            elif "\t" in line and "\t\t" not in line:
                iter2 = ExpandDataObject(vulkanVideoCapabilitiesLHS[i].strip("\t"),rhs)
                iter1.children.append(iter2)
                i = i + 1
                continue
            elif "\t\t" in line and "\t\t\t" not in line:
                iter3 = ExpandDataObject(vulkanVideoCapabilitiesLHS[i].strip("\t"),rhs)
                iter2.children.append(iter3)
                i = i + 1
                continue
            elif "\t\t\t" in line and "\t\t\t\t" not in line:
                iter4 = ExpandDataObject(vulkanVideoCapabilitiesLHS[i].strip("\t"),rhs)
                iter3.children.append(iter4)
                i = i + 1
                continue            
            elif "\t\t\t\t" in line and "\t\t\t\t\t" not in line:
                iter5 = ExpandDataObject(vulkanVideoCapabilitiesLHS[i].strip("\t"),rhs)
                iter4.children.append(iter5)
                i = i + 1
                continue    
            else:
                iter6 = ExpandDataObject(vulkanVideoCapabilitiesLHS[i].strip("\t"),rhs)
                iter5.children.append(iter6)
                i = i + 1
    #        #    continue
                
        vkVideoCapabilitiesTab_Store.append(iter1)

    def vFormats(gpu):

        vulkanVideoFormats = fetchContentsFromCommand("vulkaninfo --show-video-props | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/Video Profiles/{flag=1;next}flag' | awk '/Video Formats:/{flag=1}/Video Profile Definition/{flag=0}flag'| awk '/./' | awk '!/---|===/' "%(gpu,gpu+1))
        vulkanVideoFormatsLHS = fetchContentsFromCommand("vulkaninfo --show-video-props | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/Video Profiles/{flag=1;next}flag' | awk '/Video Formats:/{flag=1}/Video Profile Definition/{flag=0}flag'| awk '/./' | awk '!/---|===/' | awk '{gsub(/[=,:].*/,'True')l}1' "%(gpu,gpu+1))
        vulkanVideoFormatsRHS = fetchContentsFromCommand("vulkaninfo --show-video-props | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/Video Profiles/{flag=1;next}flag' | awk '/Video Formats:/{flag=1}/Video Profile Definition/{flag=0}flag'| awk '/./' | awk '!/---|===/' | grep -o [=].* | grep -o ' .*' "%(gpu,gpu+1))

        vulkanVideoProfiles = fetchContentsFromCommand("vulkaninfo | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/Video Profiles/{flag=1;}flag' | awk /./ | awk '!/===/' | grep placeholder "%(gpu,gpu+1))
        vulkanVideoProfiles.append("")

        vkVideoFormatsTab_Store.remove_all()
        toprow = []; group = None
        j = 1;i = 0; k = 0;
        toprow = ExpandDataObject(vulkanVideoProfiles[0].replace("placeholder = ",""),"")
        for line in vulkanVideoFormats:
            if '=' in line:
                rhs = vulkanVideoFormatsRHS[k].replace('count =','')
                k = k + 1
            else:
                rhs = ""
            if  line.strip(":") in vulkanVideoProfiles[j].replace("placeholder = ",""):
                if group == None:
                    vkVideoFormatsTab_Store.append(toprow)
                    toprow = ExpandDataObject(vulkanVideoProfiles[j].replace("placeholder = ",""),"")
                else:
                    vkVideoFormatsTab_Store.append(toprow)
                    toprow = ExpandDataObject(vulkanVideoProfiles[j].replace("placeholder = ",""),"")
                j = j + 1
                i = i + 1
                group = line
                continue
            elif "Video Formats" in line:
                iter1 = ExpandDataObject(vulkanVideoFormatsLHS[i].strip("\t"),rhs)
                toprow.children.append(iter1)
                i = i + 1
                continue
            elif "\t" in line and "\t\t" not in line:
                iter2 = ExpandDataObject(vulkanVideoFormatsLHS[i].strip("\t"),rhs)
                iter1.children.append(iter2)
                i = i + 1
                continue
            elif "\t\t" in line and "\t\t\t" not in line:
                iter3 = ExpandDataObject(vulkanVideoFormatsLHS[i].strip("\t"),rhs)
                iter2.children.append(iter3)
                i = i + 1
                continue
            elif "\t\t\t" in line and "\t\t\t\t" not in line:
                iter4 = ExpandDataObject(vulkanVideoFormatsLHS[i].strip("\t"),rhs)
                iter3.children.append(iter4)
                i = i + 1
                continue            
            elif "\t\t\t\t" in line and "\t\t\t\t\t" not in line:
                iter5 = ExpandDataObject(vulkanVideoFormatsLHS[i].strip("\t"),rhs)
                iter4.children.append(iter5)
                i = i + 1
                continue    
            else:
                iter6 = ExpandDataObject(vulkanVideoFormatsLHS[i].strip("\t"),rhs)
                iter5.children.append(iter6)
                i = i + 1
    #        #    continue
                
        vkVideoFormatsTab_Store.append(toprow)

    def on_gpu_dropdown_changed(combo,dummy):
        text = combo.props.selected_item
        for gpu in range(len(gpu_list)):
            if gpu_list[gpu] in text.get_string():
                vProfiles(gpu)
                vDefinitions(gpu)
                vCapabitlies(gpu)
                vFormats(gpu)

                gpu_image = getGpuImage(gpu_list[gpu])
                image_renderer.set_pixbuf(gpu_image)





    h_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)
    h_box.set_halign(Gtk.Align.CENTER)
    
    # Add a top margin to create space between the header bar and the content
    h_box.set_margin_top(10)
    h_box.set_margin_bottom(10)
    h_box.set_margin_start(10)

    # Create the label for the devices
    label = Gtk.Label.new("Available Device(s) :")
    h_box.append(label)

    # Create a list with some dummy device names
    gpu_list = fetchContentsFromCommand(Filenames.fetch_vulkaninfo_ouput_command+Filenames.fetch_device_name_command)
    
    # Create the gpu_dropdown, populated from the list of strings
    gpu_Dropdown = Gtk.DropDown()
    gpu_Dropdown.add_css_class(css_class="card")
    gpu_Dropdown_list = Gtk.StringList()
    gpu_Dropdown.set_model(gpu_Dropdown_list)
    gpu_Dropdown.set_margin_start(10)
    h_box.append(gpu_Dropdown)
    
    for i in range(len(gpu_list)):
        if (fetchContentsFromCommand("vulkaninfo | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | grep 'Video Profiles'"%(i,i+1))):
            gpu_Dropdown_list.append(gpu_list[i])
    # Add the horizontal box to the main vertical box
    videoTab.append(h_box)
    
    split_view_container = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
    split_view_container.set_vexpand(True)
    split_view_container.set_hexpand(True)
    
    # Create a new NavigationSplitView
    split_view = Adw.NavigationSplitView.new()
    split_view.set_vexpand(True)
    split_view.set_hexpand(True)

    # Create the sidebar content using a Gtk.ListBox for tabs
    sidebar_listbox = Gtk.ListBox.new()
    sidebar_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
    sidebar_listbox.set_vexpand(True)
    sidebar_listbox.add_css_class(css_class="boxed-list")
    sidebar_listbox.add_css_class(css_class="sidebar")
    


#    sidebar_listbox.add_css_class(css_class="frame")
    # Set the show-separators property to False
    sidebar_listbox.set_show_separators(True)
    
    # Add the tabs to the sidebar ListBox
    tabs = [
        "Video Profiles", "Profile Definition", "Video Capabilities", "Video Formats"
    ]

    content_stack = Gtk.Stack.new()
    
    for tab_name in tabs:
        row = Gtk.ListBoxRow()
        label = Gtk.Label.new(tab_name)
        # Add padding to the label inside the row
        label.set_margin_top(10)
        label.set_margin_bottom(10)
        row.set_child(label)
        sidebar_listbox.append(row)


        # Create a box for the content of this specific tab
        content_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        
        if tab_name == "Video Profiles":
 # --------------------- Vulkan Video Profiles ---------------------------------------------------------------------
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
            content_box.append(vkVideoProfilesScrollbar)
        
        elif tab_name == "Profile Definition":
        # --------------------- Vulkan Video Profile Definition ---------------------------------------------------------------------

            vkVideoProfileDefinitionColumnView = Gtk.ColumnView()
            vkVideoProfileDefinitionColumnView.props.show_row_separators = True
            vkVideoProfileDefinitionColumnView.props.show_column_separators = False

            factory_vkVideoProfileDefinition = Gtk.SignalListItemFactory()
            factory_vkVideoProfileDefinition.connect("setup",setup_expander)
            factory_vkVideoProfileDefinition.connect("bind",bind_expander)

            factory_vkVideoProfileDefinition_value = Gtk.SignalListItemFactory()
            factory_vkVideoProfileDefinition_value.connect("setup",setup)
            factory_vkVideoProfileDefinition_value.connect("bind",bind1)

            vkVideoProfileDefinitionSelection = Gtk.SingleSelection()
            vkVideoProfileDefinitionTab_Store = Gio.ListStore.new(ExpandDataObject)

            vkVideoModel = Gtk.TreeListModel.new(vkVideoProfileDefinitionTab_Store,False,True,add_tree_node)
            vkVideoProfileDefinitionSelection.set_model(vkVideoModel)

            vkVideoProfileDefinitionColumnView.set_model(vkVideoProfileDefinitionSelection)

            vkVideoProfileDefinitionColumnLhs = Gtk.ColumnViewColumn.new("Details",factory_vkVideoProfileDefinition)
            vkVideoProfileDefinitionColumnLhs.set_resizable(True)
            vkVideoProfileDefinitionColumnRhs = Gtk.ColumnViewColumn.new("Value",factory_vkVideoProfileDefinition_value)
            vkVideoProfileDefinitionColumnRhs.set_expand(True)

            vkVideoProfileDefinitionColumnView.append_column(vkVideoProfileDefinitionColumnLhs)
            vkVideoProfileDefinitionColumnView.append_column(vkVideoProfileDefinitionColumnRhs)

            vkVideoProfileDefinitionScrollbar = create_scrollbar(vkVideoProfileDefinitionColumnView)
            content_box.append(vkVideoProfileDefinitionScrollbar)

        elif tab_name == "Video Capabilities":
        # -------------------- Vulkan Video Capabilities -------------------------------------------------------------------------------

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
            vkVideoCapabilitiesColumnRhs = Gtk.ColumnViewColumn.new("Value",factory_vkVideoCapabilities_value)
            vkVideoCapabilitiesColumnRhs.set_expand(True)

            vkVideoCapabilitiesColumnView.append_column(vkVideoCapabilitiesColumnLhs)
            vkVideoCapabilitiesColumnView.append_column(vkVideoCapabilitiesColumnRhs)

            vkVideoCapabilitiesScrollbar = create_scrollbar(vkVideoCapabilitiesColumnView)

            content_box.append(vkVideoCapabilitiesScrollbar)
        elif tab_name == "Video Formats":
        
            # -------------------- Vulkan Video Formats -------------------------------------------------------------------------------

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
            vkVideoFormatsColumnRhs = Gtk.ColumnViewColumn.new("Value",factory_vkVideoFormats_value)
            vkVideoFormatsColumnRhs.set_expand(True)

            vkVideoFormatsColumnView.append_column(vkVideoFormatsColumnLhs)
            vkVideoFormatsColumnView.append_column(vkVideoFormatsColumnRhs)

            vkVideoFormatsScrollbar = create_scrollbar(vkVideoFormatsColumnView)
            content_box.append(vkVideoFormatsScrollbar)

        content_stack.add_titled(content_box, tab_name.replace(" ", "-").lower(), tab_name)

    gpu_Dropdown.connect("notify::selected-item", on_gpu_dropdown_changed)

    gpu_image = Gtk.Image()
    gpu_image = GdkPixbuf.Pixbuf.new_from_file_at_size(const.APP_LOGO_PNG, 100, 100)
    image_renderer = Gtk.Picture.new_for_pixbuf(gpu_image)
    gpu_Dropdown.set_margin_end(10)
    h_box.append(image_renderer)

    on_gpu_dropdown_changed(gpu_Dropdown,dummy=0)
    # Create a scrolled window for the sidebar list
    sidebar_scrolled_window = Gtk.ScrolledWindow.new()
    sidebar_scrolled_window.set_child(sidebar_listbox)

    # Connect the listbox signal to change the stack page
    def on_row_activated(listbox, row):
        # Get the label from the activated row to find the tab's name
        tab_label = row.get_child()
        tab_name = tab_label.get_label()
        
        # The name for the stack child is the tab name, with spaces replaced by dashes and lowercase
        child_name = tab_name.replace(" ", "-").lower()

        # Set the visible child of the stack using its name
        content_stack.set_visible_child_name(child_name)
        
    sidebar_listbox.connect("row-activated", on_row_activated)
    sidebar_listbox.select_row(sidebar_listbox.get_row_at_index(0))
#    content_stack.set_visible_child_name("System Information")
    # Set a minimum width for the sidebar


    # Create the Adw.NavigationPage wrappers for the sidebar and content
    sidebar_page = Adw.NavigationPage.new(sidebar_scrolled_window, "Sidebar")
    content_page = Adw.NavigationPage.new(content_stack, "Content")
    
    # Set the sidebar and content for the split view using the new pages
    split_view.set_sidebar(sidebar_page)
    split_view.set_content(content_page)
    
    # Add the split view to its new container
    split_view_container.append(split_view)
    
    # Add the split view container to the main vertical box
    videoTab.append(split_view_container)

    return videoTab