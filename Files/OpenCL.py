import gi
import  const
import subprocess
import Filenames

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk,Gio,Adw,GdkPixbuf

from Common import setup_expander, createSubTab, create_scrollbar, bind_expander,setMargin, setup,bind1, createMainFile, fetchContentsFromCommand,ExpandDataObject,add_tree_node,getGpuImage

platformDetailsHeader = ["Platform Information ", "Details "]
deviceDetailsHeader = ["Device Information ", "Details "]
deviceMemoryImageHeader = ["Device Information ", "Details "]


def openCL(tab):
    def getPlatformNames():

        createMainFile(Filenames.opencl_plaform_and_device_names_file,Filenames.fetch_platform_and_device_names_command)
        oclPlatformName = fetchContentsFromCommand(Filenames.fetch_platform_names_command)
        oclPlatformName = [i.strip(' ') for i in oclPlatformName]
        oclPlatformName = [i.strip('\n') for i in oclPlatformName]
        return oclPlatformName

    def selectDevice(dropdown,dummy):
        selected =dropdown.props.selected_item
        DeviceDetails_Store.remove_all()
        DeviceMemoryImage_store.remove_all()
        DeviceVector_store.remove_all()
        DeviceQueueExecution_store.remove_all()
        value = 0
        if selected is not None:
            value = dropdown.props.selected
            getDeviceDetails(value)
            getDeviceMemoryImageDetails(value)
            getDeviceVectorDetails(value)
            getDeviceQueueExecutionCapabilities(value)

    def getDeviceNames(value):
        
        oclPlatformslocal = []
        oclPlatformslocal = oclPlatformslocal + oclPlatforms
        oclPlatformslocal.append("BLANK")

        for i in range(len(oclPlatformslocal)):
            oclPlatformslocal[i] = [j.replace("(", "\\(") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = [j.replace(")", "\\)") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = ''.join(oclPlatformslocal[i])

        fetch_device_names_command = "cat %s | awk '/%s.*/{flag=1;next}/Platform.*/{flag=0}flag'| grep -o :.* | grep -o ' .*' | awk /./"%(Filenames.opencl_plaform_and_device_names_file,oclPlatforms[value])

        Devices_list = Gtk.StringList()
        Devices_dropdown.set_model(Devices_list)
        oclDeviceNames = fetchContentsFromCommand(fetch_device_names_command)
        oclDeviceNames = [i.strip(' ') for i in oclDeviceNames]
        oclDeviceNames = [i.strip('\n') for i in oclDeviceNames]

        numberOfDevicesEntry.set_text(str(len(oclDeviceNames)))
        numberOfDevicesEntry.set_editable(False)

        for i in oclDeviceNames:
            Devices_list.append(i)

    def getPlatfromDetails(value):

        oclPlatformslocal = []
        oclPlatformslocal = oclPlatformslocal + oclPlatforms
        oclPlatformslocal.append("BLANK")

        for i in range(len(oclPlatformslocal)):
            oclPlatformslocal[i] = [j.replace("(", "\\(") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = [j.replace(")", "\\)") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = ''.join(oclPlatformslocal[i])

        fetch_platform_details_file_command = "cat %s | awk '/Number of platforms.*/{flag=1;next}/Number of devices/{flag=0}flag' | awk '/%s/{flag=1;next}/Platform Name/{flag=0}flag' | awk /./ " %(Filenames.opencl_output_file,oclPlatformslocal[value])
        createMainFile(Filenames.opencl_platform_details_file,fetch_platform_details_file_command)

        oclPlatformDetailsLHS = fetchContentsFromCommand(Filenames.fetch_platform_details_lhs_command)
        oclPlatformDetailsRHS = fetchContentsFromCommand(Filenames.fetch_platform_details_rhs_command)
        platformDetails_Store.remove_all()

        for i in range(len(oclPlatformDetailsLHS)):
            if "Extensions" in oclPlatformDetailsLHS[i] and "suffix" not in oclPlatformDetailsLHS[i]:
                if "Version" in oclPlatformDetailsLHS[i]:
                    continue
                oclPlatformExtensions = oclPlatformDetailsRHS[i].split(' ')
                oclPlatformExtensions = list(filter(None,oclPlatformExtensions))
                toprow = ExpandDataObject(oclPlatformDetailsLHS[i].strip('\n'),
                                                           str(len(oclPlatformExtensions)))
                for j in range(len(oclPlatformExtensions)):
                    iter = ExpandDataObject(oclPlatformExtensions[j].strip('\n'), " ")
                    toprow.children.append(iter)
            else:
                toprow = ExpandDataObject(oclPlatformDetailsLHS[i].strip('\n'),
                                                    oclPlatformDetailsRHS[i].strip('\n'))
            platformDetails_Store.append(toprow)

    def getDeviceDetails(value):

        value2 = platform_dropdown.props.selected

        oclPlatformslocal = []
        oclPlatformslocal = oclPlatformslocal + oclPlatforms
        oclPlatformslocal.append("BLANK")

        for i in range(len(oclPlatformslocal)):
            oclPlatformslocal[i] = [j.replace("(", "\\(") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = [j.replace(")", "\\)") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = ''.join(oclPlatformslocal[i])


        fetch_device_details_file_command = "cat %s | awk '/%s/&& ++n == 2,/%s*/' | awk '/Device Name.*/&& ++n == %d,/Preferred \\/.*/' | grep -v Preferred | grep -v Available" % (Filenames.opencl_output_file,oclPlatformslocal[value2], oclPlatformslocal[value2 + 1], value + 1)
        fetch_device_extensions_command = "cat %s |  awk '/%s/&& ++n == 2,/%s/' | awk '/Device Name.*/&& ++n == %d,/Extensions.*/'| awk '/Extensions|Available/'" % (Filenames.opencl_output_file, oclPlatformslocal[value2], oclPlatformslocal[value2 + 1], value + 1)
        
        with open(Filenames.opencl_device_details_file,"w") as file:
            fetch_device_details_file_process = subprocess.Popen(fetch_device_details_file_command,shell=True,stdout=file,universal_newlines=True)
            fetch_device_details_file_process.communicate()
            fetch_device_extensions_process = subprocess.Popen(fetch_device_extensions_command,shell=True,stdout=file,universal_newlines=True)
            fetch_device_extensions_process.communicate()

        oclDeviceDetailsLHS = fetchContentsFromCommand(Filenames.fetch_device_details_lhs_command)
        oclDeviceDetailsRHS = fetchContentsFromCommand(Filenames.fetch_device_details_rhs_command)


    #    DeviceDetails_Store.remove_all()

        iter = None
        for i in range(len(oclDeviceDetailsLHS)):
            if "    " in oclDeviceDetailsLHS[i]:
                oclDeviceDetailsLHS[i] = oclDeviceDetailsLHS[i].strip("  ")
                iter = ExpandDataObject(oclDeviceDetailsLHS[i].strip('\n'), oclDeviceDetailsRHS[i].strip('\n'))
                toprow.children.append(iter)
            else:
                if "Number of devices" in oclDeviceDetailsLHS[i]:
                    oclDeviceDetailsLHS[i] = "  Number of devices"
                    oclDeviceDetailsRHS[i] = oclDeviceDetailsRHS[i][len(oclDeviceDetailsLHS[i]):].strip(' ')
                if "OpenCL" in oclDeviceDetailsLHS[i] and ("versions" in oclDeviceDetailsLHS[i] or "features" in oclDeviceDetailsLHS[i]):
                    if "versions" in oclDeviceDetailsLHS[i]:
                        toprow = ExpandDataObject(oclDeviceDetailsLHS[i].strip('\n'),"")
                        iter  = ExpandDataObject(oclDeviceDetailsRHS[i].replace(((oclDeviceDetailsRHS[i].split())[2]+" "+(oclDeviceDetailsRHS[i].split())[3]),""),(oclDeviceDetailsRHS[i].split())[2]+" "+(oclDeviceDetailsRHS[i].split())[3])
                        toprow.children.append(iter)
                    if "features" in oclDeviceDetailsLHS[i]:
                        DeviceDetails_Store.append(toprow)
                        toprow = ExpandDataObject(oclDeviceDetailsLHS[i].strip('\n'),"")
                        iter = ExpandDataObject(oclDeviceDetailsRHS[i].replace(((oclDeviceDetailsRHS[i].split())[1]+" "+(oclDeviceDetailsRHS[i].split())[2]),""), (oclDeviceDetailsRHS[i].split())[1]+" "+(oclDeviceDetailsRHS[i].split())[2])
                        toprow.children.append(iter)
                    continue
                if "0x" in oclDeviceDetailsRHS[i] and "Device" not in oclDeviceDetailsLHS[i]:
                #    toprow = ExpandDataObject(oclDeviceDetailsLHS[i].strip('\n'),"")
                    if "OpenCL" in oclDeviceDetailsRHS[i]:
                        
                        iter = ExpandDataObject(oclDeviceDetailsRHS[i].replace(((oclDeviceDetailsRHS[i].split())[2]+" "+(oclDeviceDetailsRHS[i].split())[3]),""),(oclDeviceDetailsRHS[i].split())[2]+" "+(oclDeviceDetailsRHS[i].split())[3])
                        toprow.children.append(iter)
                        continue
                    else:
                        iter = ExpandDataObject(oclDeviceDetailsRHS[i].replace(((oclDeviceDetailsRHS[i].split())[1]+" "+(oclDeviceDetailsRHS[i].split())[2]),""), (oclDeviceDetailsRHS[i].split())[1]+" "+(oclDeviceDetailsRHS[i].split())[2])
                        toprow.children.append(iter)
                        continue
                if "Extensions" in oclDeviceDetailsLHS[i]:
                    oclDeviceExtenstions = oclDeviceDetailsRHS[i].split(" ")
                    oclDeviceExtenstions = list(filter(None,oclDeviceExtenstions))
                    DeviceDetails_Store.append(toprow)
                    toprow = ExpandDataObject(oclDeviceDetailsLHS[i].strip('\n'),str(len(oclDeviceExtenstions)).strip('\n'))
                    for j in range(len(oclDeviceExtenstions)):
                        iter = ExpandDataObject(oclDeviceExtenstions[j].strip('\n'), " ")
                        toprow.children.append(iter)
                else:
                    if iter == None:
                        toprow = ExpandDataObject(oclDeviceDetailsLHS[i].strip('\n'),
                                                             oclDeviceDetailsRHS[i].strip('\n'))
                        DeviceDetails_Store.append(toprow)
                    else:
                        DeviceDetails_Store.append(toprow)
                        toprow = ExpandDataObject(oclDeviceDetailsLHS[i].strip('\n'),
                                                             oclDeviceDetailsRHS[i].strip('\n'))
        DeviceDetails_Store.append(toprow)



    def getDeviceMemoryImageDetails(value):

        value2 = platform_dropdown.props.selected

        oclPlatformslocal = []
        oclPlatformslocal = oclPlatformslocal + oclPlatforms
        oclPlatformslocal.append("BLANK")

        for i in range(len(oclPlatformslocal)):
            oclPlatformslocal[i] = [j.replace("(", "\\(") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = [j.replace(")", "\\)") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = ''.join(oclPlatformslocal[i])

        fetch_device_memory_and_image_file_command = "cat %s |  awk '/%s/&& ++n == 2,/%s/' | awk '/Device Name.*/&& ++n == %d,/Extensions.*/'| awk '/Address.*/{flag=1;print}/Queue.*/{flag=0}flag' | uniq" % (Filenames.opencl_output_file,oclPlatformslocal[value2], oclPlatformslocal[value2 + 1], value + 1)
        createMainFile(Filenames.opencl_device_memory_and_image_file,fetch_device_memory_and_image_file_command)

        oclDeviceMemoryImageDetailsLHS = fetchContentsFromCommand(Filenames.fetch_device_memory_and_image_details_lhs_command)
        oclDeviceMemoryImageDetailsRHS = fetchContentsFromCommand(Filenames.fetch_device_memory_and_image_details_rhs_command)

        oclDeviceMemoryImageDetailsLHS = [i.strip('\n') for i in oclDeviceMemoryImageDetailsLHS]
        oclDeviceMemoryImageDetailsRHS = [i.strip('\n') for i in oclDeviceMemoryImageDetailsRHS]

    #    DeviceMemoryImage_store.remove_all()
        iter = None
        for i in range(len(oclDeviceMemoryImageDetailsLHS)):
            if "    " in oclDeviceMemoryImageDetailsLHS[i]:
                if "Base address alignment for 2D image buffers" in oclDeviceMemoryImageDetailsLHS[i]:
                    oclDeviceMemoryImageDetailsLHS[i] = "    Base address alignment for 2D image buffers"
                    oclDeviceMemoryImageDetailsRHS[i] = oclDeviceMemoryImageDetailsRHS[i][
                                                        len(oclDeviceMemoryImageDetailsLHS[i]):].strip(' ')
                oclDeviceMemoryImageDetailsLHS[i] = oclDeviceMemoryImageDetailsLHS[i].strip("  ")
             #   DeviceMemoryImage_store.append(toprow)
                iter = ExpandDataObject(oclDeviceMemoryImageDetailsLHS[i].strip('\n'),oclDeviceMemoryImageDetailsRHS[i].strip('\n'))
                toprow.children.append(iter)
            else:
                if oclDeviceMemoryImageDetailsLHS[i] in oclDeviceMemoryImageDetailsRHS[i]:
                    oclDeviceMemoryImageDetailsRHS[i] = oclDeviceMemoryImageDetailsRHS[i][
                                                        len(oclDeviceMemoryImageDetailsLHS[i]):].strip(' ')
                 #   toprow = ExpandDataObject(oclDeviceMemoryImageDetailsLHS[i].strip('\n'),oclDeviceMemoryImageDetailsRHS[i].strip('\n'))
                elif "Built-in" in oclDeviceMemoryImageDetailsLHS[i]:
                    oclDeviceKernels = oclDeviceMemoryImageDetailsRHS[i].split(';')
                    toprow = ExpandDataObject(oclDeviceMemoryImageDetailsLHS[i].strip('\n'),str(len(oclDeviceKernels) - 1).strip('\n'))
                    for j in range(len(oclDeviceKernels) - 1):
                        iter = ExpandDataObject(oclDeviceKernels[j].strip('\n'), " ")
                        toprow.children.append(iter)
                else:
                    if iter == None:
                        toprow = ExpandDataObject(oclDeviceMemoryImageDetailsLHS[i].strip('\n'),oclDeviceMemoryImageDetailsRHS[i].strip('\n'))
                        DeviceMemoryImage_store.append(toprow)
                    else:
                        DeviceMemoryImage_store.append(toprow)
                        toprow = ExpandDataObject(oclDeviceMemoryImageDetailsLHS[i].strip('\n'),oclDeviceMemoryImageDetailsRHS[i].strip('\n'))
                #    DeviceMemoryImage_store.append(toprow)
        DeviceMemoryImage_store.append(toprow)

    def getDeviceVectorDetails(value):

        value2 = platform_dropdown.props.selected
        oclPlatformslocal = []
        oclPlatformslocal = oclPlatformslocal + oclPlatforms
        oclPlatformslocal.append("BLANK")

        for i in range(len(oclPlatformslocal)):
            oclPlatformslocal[i] = [j.replace("(", "\\(") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = [j.replace(")", "\\)") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = ''.join(oclPlatformslocal[i])

        fetch_device_vector_details_file_command = "cat %s | awk '/%s/&& ++n == 2,/%s/' | awk '/Device Name.*/&& ++n == %d,/Extensions.*/'| awk '/Preferred \\/.*/{flag=1;print}/Address.*/{flag=0}flag' | uniq" % (Filenames.opencl_output_file, oclPlatformslocal[value2], oclPlatformslocal[value2 + 1], value + 1)
        createMainFile(Filenames.opencl_device_vector_file,fetch_device_vector_details_file_command)

        oclDeviceVectorDetailsLHS = fetchContentsFromCommand(Filenames.fetch_device_vector_details_lhs_command)
        oclDeviceVectorDetailsRHS = fetchContentsFromCommand(Filenames.fetch_device_vector_details_rhs_command)

        oclDeviceVectorDetailsLHS = [i.strip('\n') for i in oclDeviceVectorDetailsLHS]
        oclDeviceVectorDetailsRHS = [i.strip('\n') for i in oclDeviceVectorDetailsRHS]
        DeviceVector_store.remove_all()
        iter = None
        for i in range(len(oclDeviceVectorDetailsLHS)):
            if "    " in oclDeviceVectorDetailsLHS[i]:
                if "Correctly-rounded divide and sqrt operations" in oclDeviceVectorDetailsLHS[i]:
                    oclDeviceVectorDetailsLHS[i] = "    Correctly-rounded divide and sqrt operations"
                    oclDeviceVectorDetailsRHS[i] = oclDeviceVectorDetailsRHS[i][
                                                   len(oclDeviceVectorDetailsLHS[i]):].strip(' ')
                #    oclDeviceVectorDetailsLHS[i] = oclDeviceVectorDetailsLHS[i].strip("  ")
                iter = ExpandDataObject(oclDeviceVectorDetailsLHS[i].strip('\n'), oclDeviceVectorDetailsRHS[i])
                toprow.children.append(iter)
        #            iter = ExpandDataObject(oclDeviceVectorDetailsLHS[i].strip('\n'), oclDeviceVectorDetailsRHS[i])
        #            toprow.children.append(iter)
                 #   DeviceVector_store.append(toprow)
          #      else:
         #           print(oclDeviceVectorDetailsLHS[i])
                #    DeviceVector_store.append(toprow)
        #            iter = ExpandDataObject(oclDeviceVectorDetailsLHS[i].strip('\n'), oclDeviceVectorDetailsRHS[i])
        #            toprow.children.append(iter)
        #            continue
            #    DeviceVector_store.append(toprow)
            #    continue
            else:
                if oclDeviceVectorDetailsLHS[i] in oclDeviceVectorDetailsRHS[i]:
                    oclDeviceVectorDetailsRHS[i] = oclDeviceVectorDetailsRHS[i].strip(oclDeviceVectorDetailsLHS[i])
                if iter == None:
                    toprow = ExpandDataObject(oclDeviceVectorDetailsLHS[i].strip('\n'),oclDeviceVectorDetailsRHS[i].strip('\n'))
                else:
                    DeviceVector_store.append(toprow)
                    toprow = ExpandDataObject(oclDeviceVectorDetailsLHS[i].strip('\n'),oclDeviceVectorDetailsRHS[i].strip('\n'))
        DeviceVector_store.append(toprow)
            

    def getDeviceQueueExecutionCapabilities(value):

        value2 = platform_dropdown.props.selected

        oclPlatformslocal = []
        oclPlatformslocal = oclPlatformslocal + oclPlatforms
        oclPlatformslocal.append("BLANK")

        for i in range(len(oclPlatformslocal)):
            oclPlatformslocal[i] = [j.replace("(", "\\(") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = [j.replace(")", "\\)") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = ''.join(oclPlatformslocal[i])

        fetch_device_queue_execution_file_command = "cat %s |  awk '/%s/&& ++n == 2,/%s/' | awk '/Device Name.*/&& ++n == %d,/Extensions.*/' | awk '/Queue.*/{flag=1;print}/Extensions.*/{flag=0}flag' | grep -v Available | uniq" % (Filenames.opencl_output_file,oclPlatformslocal[value2], oclPlatformslocal[value2 + 1], value + 1)
        createMainFile(Filenames.opencl_device_queue_execution_details_file,fetch_device_queue_execution_file_command)

        oclDeviceQueueExecutionDetailsLHS = fetchContentsFromCommand(Filenames.fetch_device_queue_execution_details_lhs_command)
        oclDeviceQueueExecutionDetailsRHS = fetchContentsFromCommand(Filenames.fetch_device_queue_execution_details_rhs_command)

        oclDeviceQueueExecutionDetailsLHS = [i.strip('\n') for i in oclDeviceQueueExecutionDetailsLHS]
        oclDeviceQueueExecutionDetailsRHS = [i.strip('\n') for i in oclDeviceQueueExecutionDetailsRHS]

        DeviceQueueExecution_store.remove_all()
        iter = None
        for i in range(len(oclDeviceQueueExecutionDetailsLHS)):
            if "    " in oclDeviceQueueExecutionDetailsLHS[i] and "0x" not in oclDeviceQueueExecutionDetailsRHS[i]:
                oclDeviceQueueExecutionDetailsLHS[i] = oclDeviceQueueExecutionDetailsLHS[i].strip("  ")
                iter = ExpandDataObject(oclDeviceQueueExecutionDetailsLHS[i].strip('\n'),oclDeviceQueueExecutionDetailsRHS[i].strip('\n'))
                toprow.children.append(iter)
            else:
                if "Built-in" in oclDeviceQueueExecutionDetailsLHS[i] and "version" not in oclDeviceQueueExecutionDetailsLHS[i] and "n/a" not in oclDeviceQueueExecutionDetailsRHS[i]:
                    oclDeviceKernels = oclDeviceQueueExecutionDetailsRHS[i].split(';')
                    toprow = ExpandDataObject(oclDeviceQueueExecutionDetailsLHS[i].strip('\n'),str(len(oclDeviceKernels) ).strip('\n'))
                    for j in range(len(oclDeviceKernels)):
                        iter = ExpandDataObject(oclDeviceKernels[j].strip('\n'), " ")
                        toprow.children.append(iter)
                elif "Built-in" in oclDeviceQueueExecutionDetailsLHS[i] and "version" in oclDeviceQueueExecutionDetailsLHS[i] and "n/a" not in oclDeviceQueueExecutionDetailsRHS[i]:
                    DeviceQueueExecution_store.append(toprow)
                    toprow = ExpandDataObject(oclDeviceQueueExecutionDetailsLHS[i],"")
                    iter = ExpandDataObject(oclDeviceQueueExecutionDetailsRHS[i].replace(((oclDeviceQueueExecutionDetailsRHS[i].split())[1]+" "+(oclDeviceQueueExecutionDetailsRHS[i].split())[2]),""),(oclDeviceQueueExecutionDetailsRHS[i].split())[1]+" "+(oclDeviceQueueExecutionDetailsRHS[i].split())[2])
                    toprow.children.append(iter)
                elif "0x" in oclDeviceQueueExecutionDetailsRHS[i]:
                    iter = ExpandDataObject(oclDeviceQueueExecutionDetailsRHS[i].replace(((oclDeviceQueueExecutionDetailsRHS[i].split())[1]+" "+(oclDeviceQueueExecutionDetailsRHS[i].split())[2]),""),(oclDeviceQueueExecutionDetailsRHS[i].split())[1]+" "+(oclDeviceQueueExecutionDetailsRHS[i].split())[2])
                    toprow.children.append(iter)
                    continue
                else:
                    if iter == None:
                        toprow = ExpandDataObject(oclDeviceQueueExecutionDetailsLHS[i].strip('\n'),oclDeviceQueueExecutionDetailsRHS[i].strip('\n'))
                    #    DeviceQueueExecution_store.append(toprow)
                    else:
                        DeviceQueueExecution_store.append(toprow)
                        toprow = ExpandDataObject(oclDeviceQueueExecutionDetailsLHS[i].strip('\n'),oclDeviceQueueExecutionDetailsRHS[i].strip('\n'))
        DeviceQueueExecution_store.append(toprow)

    def selectPlatform(dropdown,dummy):
        selected =dropdown.props.selected_item
        print(selected)
        value = 0
        if selected is not None:
            value = dropdown.props.selected
        getDeviceNames(value)
        getPlatfromDetails(value)

#        gpu_image = getGpuImage(gpu_list[text])
#        image_renderer.set_pixbuf(gpu_image)

    #    os.system("rm /tmp/gpu-viewer/ocl*.txt")

    split_view_container = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
    split_view_container.set_vexpand(True)
    split_view_container.set_hexpand(True)

    split_view = Adw.NavigationSplitView.new()
    split_view.set_vexpand(True)
    split_view.set_hexpand(True)

    # Create the sidebar content using a Gtk.ListBox for tabs
    sidebar_listbox = Gtk.ListBox.new()
    sidebar_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
    sidebar_listbox.set_vexpand(True)
    sidebar_listbox.add_css_class(css_class="boxed-list")
    sidebar_listbox.add_css_class(css_class="toolbar")
    sidebar_listbox.add_css_class(css_class="sidebar")
    sidebar_listbox.set_show_separators(True)

    tabs = [
        "Platform Information", "Device Information", "Device Memory  \n \t  &\nImage Information",
        "Queue Capabilities  \n \t\t &\nExecution Capabilities", "Device Vector Information"
    ]


    content_stack = Gtk.Stack.new()

    # Create the content pages for each tab and add them to the stack
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

        if tab_name == "Platform Information":

                platformColumnView = Gtk.ColumnView()
                platformColumnView.props.show_row_separators = True
                platformColumnView.props.show_column_separators = False

                factory_platform = Gtk.SignalListItemFactory()
                factory_platform.connect("setup",setup_expander)
                factory_platform.connect("bind",bind_expander)

                factory_platform_value = Gtk.SignalListItemFactory()
                factory_platform_value.connect("setup",setup)
                factory_platform_value.connect("bind",bind1)

                platformSelection = Gtk.SingleSelection()
                platformDetails_Store = Gio.ListStore.new(ExpandDataObject)

                platformModel = Gtk.TreeListModel.new(platformDetails_Store,False,True,add_tree_node)
                platformSelection.set_model(platformModel)

                platformColumnView.set_model(platformSelection)

                platformColumnLhs = Gtk.ColumnViewColumn.new("Platform Information",factory_platform)
                platformColumnLhs.set_resizable(True)
                platformColumnRhs = Gtk.ColumnViewColumn.new("Details",factory_platform_value)
                platformColumnRhs.set_expand(True)

                platformColumnView.append_column(platformColumnLhs)
                platformColumnView.append_column(platformColumnRhs)

                platformScrollbar = create_scrollbar(platformColumnView)

                content_box.append(platformScrollbar)
        elif tab_name == "Device Information":

                deviceColumnView = Gtk.ColumnView()
                deviceColumnView.props.show_row_separators = True
                deviceColumnView.props.show_column_separators = False

                factory_devices = Gtk.SignalListItemFactory()
                factory_devices.connect("setup",setup_expander)
                factory_devices.connect("bind",bind_expander)

                factory_devices_value = Gtk.SignalListItemFactory()
                factory_devices_value.connect("setup",setup)
                factory_devices_value.connect("bind",bind1)

                deviceSelection = Gtk.SingleSelection()
                DeviceDetails_Store = Gio.ListStore.new(ExpandDataObject)

                deviceModel = Gtk.TreeListModel.new(DeviceDetails_Store,False,True,add_tree_node)
                deviceSelection.set_model(deviceModel)

                deviceColumnView.set_model(deviceSelection)

                deviceColumnLhs = Gtk.ColumnViewColumn.new("Device Information",factory_devices)
                deviceColumnLhs.set_resizable(True)
                deviceColumnRhs = Gtk.ColumnViewColumn.new("Details",factory_devices_value)
                deviceColumnRhs.set_expand(True)

                deviceColumnView.append_column(deviceColumnLhs)
                deviceColumnView.append_column(deviceColumnRhs)

                DeviceDetailsScrollbar = create_scrollbar(deviceColumnView)

                content_box.append(DeviceDetailsScrollbar)
        elif tab_name == "Device Memory  \n \t  &\nImage Information":
                deviceMemoryImageColumnView = Gtk.ColumnView()
                deviceMemoryImageColumnView.props.show_row_separators = True
                deviceMemoryImageColumnView.props.show_column_separators = False

                factory_devices_memory_image = Gtk.SignalListItemFactory()
                factory_devices_memory_image.connect("setup",setup_expander)
                factory_devices_memory_image.connect("bind",bind_expander)

                factory_devices_memory_image_value = Gtk.SignalListItemFactory()
                factory_devices_memory_image_value.connect("setup",setup)
                factory_devices_memory_image_value.connect("bind",bind1)

                deviceMemoryImageSelection = Gtk.SingleSelection()
                DeviceMemoryImage_store = Gio.ListStore.new(ExpandDataObject)

                deviceMemoryImageModel = Gtk.TreeListModel.new(DeviceMemoryImage_store,False,True,add_tree_node)
                deviceMemoryImageSelection.set_model(deviceMemoryImageModel)

                deviceMemoryImageColumnView.set_model(deviceMemoryImageSelection)

                deviceMemoryImageColumnLhs = Gtk.ColumnViewColumn.new("Device Information",factory_devices_memory_image)
                deviceMemoryImageColumnLhs.set_resizable(True)
                deviceMemoryImageColumnRhs = Gtk.ColumnViewColumn.new("Details",factory_devices_memory_image_value)
                deviceMemoryImageColumnRhs.set_expand(True)

                deviceMemoryImageColumnView.append_column(deviceMemoryImageColumnLhs)
                deviceMemoryImageColumnView.append_column(deviceMemoryImageColumnRhs)

                DeviceMemoryImageScrollbar = create_scrollbar(deviceMemoryImageColumnView)

                content_box.append(DeviceMemoryImageScrollbar)
        elif tab_name == "Queue Capabilities  \n \t\t &\nExecution Capabilities":
                deviceQueueExecutionColumnView = Gtk.ColumnView()
                deviceQueueExecutionColumnView.props.show_row_separators = True
                deviceQueueExecutionColumnView.props.show_column_separators = False

                factory_devices_queue_execution = Gtk.SignalListItemFactory()
                factory_devices_queue_execution.connect("setup",setup_expander)
                factory_devices_queue_execution.connect("bind",bind_expander)

                factory_devices_queue_execution_value = Gtk.SignalListItemFactory()
                factory_devices_queue_execution_value.connect("setup",setup)
                factory_devices_queue_execution_value.connect("bind",bind1)

                deviceQueueExecutionSelection = Gtk.SingleSelection()
                DeviceQueueExecution_store = Gio.ListStore.new(ExpandDataObject)

                deviceQueueExectionModel = Gtk.TreeListModel.new(DeviceQueueExecution_store,False,True,add_tree_node)
                deviceQueueExecutionSelection.set_model(deviceQueueExectionModel)

                deviceQueueExecutionColumnView.set_model(deviceQueueExecutionSelection)

                deviceQueueExectionColumnLhs = Gtk.ColumnViewColumn.new("Device Information",factory_devices_queue_execution)
                deviceQueueExectionColumnLhs.set_resizable(True)
                deviceQueueExectionColumnRhs = Gtk.ColumnViewColumn.new("Details",factory_devices_queue_execution_value)
                deviceQueueExectionColumnRhs.set_expand(True)

                deviceQueueExecutionColumnView.append_column(deviceQueueExectionColumnLhs)
                deviceQueueExecutionColumnView.append_column(deviceQueueExectionColumnRhs)

                DeviceQueueExecutionScrollbar = create_scrollbar(deviceQueueExecutionColumnView)

                content_box.append(DeviceQueueExecutionScrollbar)
        elif tab_name == "Device Vector Information":
                deviceVectorColumnView = Gtk.ColumnView()
                deviceVectorColumnView.props.show_row_separators = True
                deviceVectorColumnView.props.show_column_separators = False

                factory_devices_vector = Gtk.SignalListItemFactory()
                factory_devices_vector.connect("setup",setup_expander)
                factory_devices_vector.connect("bind",bind_expander)

                factory_devices_vector_value = Gtk.SignalListItemFactory()
                factory_devices_vector_value.connect("setup",setup)
                factory_devices_vector_value.connect("bind",bind1)

                deviceVectorSelection = Gtk.SingleSelection()
                DeviceVector_store = Gio.ListStore.new(ExpandDataObject)

                deviceVectorModel = Gtk.TreeListModel.new(DeviceVector_store,False,True,add_tree_node)
                deviceVectorSelection.set_model(deviceVectorModel)

                deviceVectorColumnView.set_model(deviceVectorSelection)

                deviceVectorColumnLhs = Gtk.ColumnViewColumn.new("Device Information",factory_devices_vector)
                deviceVectorColumnLhs.set_resizable(True)
                deviceVectorRhs = Gtk.ColumnViewColumn.new("Details",factory_devices_vector_value)
                deviceVectorRhs.set_expand(True)

                deviceVectorColumnView.append_column(deviceVectorColumnLhs)
                deviceVectorColumnView.append_column(deviceVectorRhs)

                DeviceVectorScrollbar = create_scrollbar(deviceVectorColumnView)

                content_box.append(DeviceVectorScrollbar)



    # Add the tabs to the sidebar ListBox
        content_stack.add_titled(content_box, tab_name.replace(" ", "-").lower(), tab_name)

    sidebar_scrolled_window = Gtk.ScrolledWindow.new()
    sidebar_scrolled_window.set_child(sidebar_listbox)

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

    sidebar_page = Adw.NavigationPage.new(sidebar_scrolled_window, "Sidebar")
    content_page = Adw.NavigationPage.new(content_stack, "Content")
    
    # Set the sidebar and content for the split view using the new pages
    split_view.set_sidebar(sidebar_page)
    split_view.set_content(content_page)
    
    # Add the split view to its new container
    split_view_container.append(split_view)
    
    # The Platform Drop Down

    h_box = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    h_box.set_halign(Gtk.Align.CENTER)
    setMargin(h_box,10,10,10)

#    platformGrid = Gtk.Grid()
 #   platformGrid.set_border_width(20)
#    platformGrid.set_column_spacing(20)
#    platformGrid.set_row_spacing(10)
    #   mainGrid.set_row_spacing(10)
#    platformFrame = Gtk.Frame(hexpand=True)
#    mainGrid.attach(platformFrame,0,0,1,1)
 #   platformFrame.set_child(platformGrid)

    platformLabel = Gtk.Label()
    platformLabel.add_css_class(css_class="toolbar")
#    setMargin(platformLabel,300,10,10)
    platformLabel.set_text("Available Platform(s):")
 #   platformGrid.attach(platformLabel, 0, 1, 1, 1)

    h_box.append(platformLabel)

#    h_device_box = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
#    h_device_box.set_halign(Gtk.Align.START)
#    setMargin(h_device_box,10,10,10)
    platform_list = Gtk.StringList()

    oclPlatforms = getPlatformNames()

    for i in oclPlatforms:
        platform_list.append(i)

    platform_dropdown = Gtk.DropDown()
    platform_dropdown.add_css_class(css_class="card")
    platform_dropdown.set_model(platform_list)

    platform_dropdown.connect("notify::selected-item",selectPlatform)

    h_box.append(platform_dropdown)

    AvailableDevices = Gtk.Label()
    
    AvailableDevices.set_label("Available Device(s) :")
    setMargin(AvailableDevices,50,10,10)
    h_box.append(AvailableDevices)
#    platformGrid.attach_next_to(AvailableDevices, platformLabel, Gtk.PositionType.BOTTOM, 2, 1)

    Devices_list = Gtk.StringList()
    Devices_dropdown = Gtk.DropDown()
    Devices_dropdown.add_css_class(css_class="card")
    Devices_dropdown.set_model(Devices_list)
    setMargin(Devices_dropdown,20,10,10)
    Devices_dropdown.connect("notify::selected-item",selectDevice)
    h_box.append(Devices_dropdown)

#    platformGrid.attach_next_to(Devices_dropdown, AvailableDevices, Gtk.PositionType.RIGHT, 20, 1)

    numberOfDevicesEntry = Gtk.Entry()
    setMargin(numberOfDevicesEntry,30,10,10)

    setMargin(platform_dropdown,30,10,10)
    selectPlatform(platform_dropdown,0)


#    platformGrid.attach_next_to(platform_dropdown, platformLabel, Gtk.PositionType.RIGHT, 21, 1)

    numberOfPlatforms = Gtk.Label()
    setMargin(numberOfPlatforms,30,10,10)
    numberOfPlatforms.set_label("Number of Platforms :")
#    h_platform_box.append(numberOfPlatforms)
#    platformGrid.attach_next_to(numberOfPlatforms, platform_dropdown, Gtk.PositionType.RIGHT, 1, 1)

    numberOfPlatformsEntry = Gtk.Entry()
    setMargin(numberOfPlatformsEntry,30,10,10)
    numberOfPlatformsEntry.set_text(str(len(oclPlatforms)))
    numberOfPlatformsEntry.set_editable(False)
#    h_platform_box.append(numberOfPlatformsEntry)
#    platformGrid.attach_next_to(numberOfPlatformsEntry, numberOfPlatforms, Gtk.PositionType.RIGHT, 1, 1)

    numberOfDevices = Gtk.Label()
    setMargin(numberOfDevices,30,10,10)
    numberOfDevices.set_label("Number Of Devices :")
#    h_device_box.append(numberOfDevices)
#    platformGrid.attach_next_to(numberOfDevices, Devices_dropdown, Gtk.PositionType.RIGHT, 1, 1)

    numberOfDevicesEntry.set_max_length(2)

#    platformGrid.attach_next_to(numberOfDevicesEntry, numberOfDevices, Gtk.PositionType.RIGHT, 1, 1)
    tab.append(h_box)
    tab.append(split_view_container)
    return tab