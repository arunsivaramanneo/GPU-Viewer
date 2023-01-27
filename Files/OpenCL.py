import gi
import  const
import subprocess
import Filenames

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from Common import copyContentsFromFile, createSubTab, create_scrollbar, setColumns, setBackgroundColor,setMargin, createSearchEntry, createMainFile, fetchContentsFromCommand

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

    def selectDevice(combo):
        value = combo.get_active()
        getDeviceDetails(value)
        getDeviceMemoryImageDetails(value)
        getDeviceVectorDetails(value)
        getDeviceQueueExecutionCapabilities(value)

    def getDeviceNames(value):

        oclPlatformslocal = []
        oclPlatformslocal = oclPlatformslocal + oclPlatforms
        oclPlatformslocal.append("BLANK")

        for i in range(len(oclPlatformslocal)):
            oclPlatformslocal[i] = [j.replace("(", "\(") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = [j.replace(")", "\)") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = ''.join(oclPlatformslocal[i])

        fetch_device_names_command = "cat %s | awk '/%s.*/{flag=1;next}/Platform.*/{flag=0}flag'| grep -o :.* | grep -o ' .*' | awk /./"%(Filenames.opencl_plaform_and_device_names_file,oclPlatforms[value])
        Devices_store.clear()
        Devices_combo.set_model(Devices_store)
        oclDeviceNames = fetchContentsFromCommand(fetch_device_names_command)
        oclDeviceNames = [i.strip(' ') for i in oclDeviceNames]
        oclDeviceNames = [i.strip('\n') for i in oclDeviceNames]

        numberOfDevicesEntry.set_text(str(len(oclDeviceNames)))
        numberOfDevicesEntry.set_editable(False)

        for i in oclDeviceNames:
            Devices_store.append([i])

        Devices_combo.set_active(0)

    def getPlatfromDetails(value):

        oclPlatformslocal = []
        oclPlatformslocal = oclPlatformslocal + oclPlatforms
        oclPlatformslocal.append("BLANK")

        for i in range(len(oclPlatformslocal)):
            oclPlatformslocal[i] = [j.replace("(", "\(") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = [j.replace(")", "\)") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = ''.join(oclPlatformslocal[i])

        fetch_platform_details_file_command = "cat %s | awk '/Number of platforms.*/{flag=1;next}/Number of devices/{flag=0}flag' | awk '/%s/{flag=1;next}/Platform Name/{flag=0}flag' | awk /./ " %(Filenames.opencl_output_file,oclPlatformslocal[value])
        createMainFile(Filenames.opencl_platform_details_file,fetch_platform_details_file_command)

        oclPlatformDetailsLHS = fetchContentsFromCommand(Filenames.fetch_platform_details_lhs_command)
        oclPlatformDetailsRHS = fetchContentsFromCommand(Filenames.fetch_platform_details_rhs_command)
        platformDetails_Store.clear()
        platformDetailsTreeView.set_model(platformDetails_Store)

        for i in range(len(oclPlatformDetailsLHS)):
            platformDetailsTreeView.expand_all()
            background_color = setBackgroundColor(i)
            if "Extensions" in oclPlatformDetailsLHS[i] and "suffix" not in oclPlatformDetailsLHS[i]:
                if "Version" in oclPlatformDetailsLHS[i]:
                    continue
                oclPlatformExtensions = oclPlatformDetailsRHS[i].split(' ')
                oclPlatformExtensions = list(filter(None,oclPlatformExtensions))
                iter = platformDetails_Store.append(None, [oclPlatformDetailsLHS[i].strip('\n'),
                                                           str(len(oclPlatformExtensions)), const.BGCOLOR3])
                for j in range(len(oclPlatformExtensions)):
                    background_color = setBackgroundColor(j)
                    platformDetails_Store.append(iter, [oclPlatformExtensions[j].strip('\n'), " ", background_color])
            else:
                platformDetails_Store.append(None, [oclPlatformDetailsLHS[i].strip('\n'),
                                                    oclPlatformDetailsRHS[i].strip('\n'), background_color])

    def getDeviceDetails(value):

        value2 = platform_combo.get_active()

        oclPlatformslocal = []
        oclPlatformslocal = oclPlatformslocal + oclPlatforms
        oclPlatformslocal.append("BLANK")

        for i in range(len(oclPlatformslocal)):
            oclPlatformslocal[i] = [j.replace("(", "\(") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = [j.replace(")", "\)") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = ''.join(oclPlatformslocal[i])

        fetch_device_details_file_command = "cat %s | awk '/%s/&& ++n == 2,/%s*/' | awk '/Device Name.*/&& ++n == %d,/Preferred \/.*/' | grep -v Preferred | grep -v Available" % (Filenames.opencl_output_file,oclPlatformslocal[value2], oclPlatformslocal[value2 + 1], value + 1)
        fetch_device_extensions_command = "cat %s |  awk '/%s/&& ++n == 2,/%s/' | awk '/Device Name.*/&& ++n == %d,/Extensions.*/'| awk '/Extensions|Available/'" % (Filenames.opencl_output_file, oclPlatformslocal[value2], oclPlatformslocal[value2 + 1], value + 1)
        
        with open(Filenames.opencl_device_details_file,"w") as file:
            fetch_device_details_file_process = subprocess.Popen(fetch_device_details_file_command,shell=True,stdout=file,universal_newlines=True)
            fetch_device_details_file_process.communicate()
            fetch_device_extensions_process = subprocess.Popen(fetch_device_extensions_command,shell=True,stdout=file,universal_newlines=True)
            fetch_device_extensions_process.communicate()

        oclDeviceDetailsLHS = fetchContentsFromCommand(Filenames.fetch_device_details_lhs_command)
        oclDeviceDetailsRHS = fetchContentsFromCommand(Filenames.fetch_device_details_rhs_command)

        DeviceDetails_Store.clear()
        DeviceDetailsTreeView.set_model(DeviceDetails_Store)
        fgcolor = []

        for i in range(len(oclDeviceDetailsRHS)):
            if "Yes" in oclDeviceDetailsRHS[i]:
                fgcolor.append("GREEN")
            elif "No" in oclDeviceDetailsRHS[i] and "None" not in oclDeviceDetailsRHS[i]:
                fgcolor.append("RED")
            else:
                fgcolor.append(const.COLOR3)

        for i in range(len(oclDeviceDetailsLHS)):
            DeviceDetailsTreeView.expand_all()
            if "    " in oclDeviceDetailsLHS[i]:
                oclDeviceDetailsLHS[i] = oclDeviceDetailsLHS[i].strip("  ")
                DeviceDetails_Store.append(iter,
                                           [oclDeviceDetailsLHS[i].strip('\n'), oclDeviceDetailsRHS[i].strip('\n'),
                                            setBackgroundColor(i), fgcolor[i]])
            else:
                if "Number of devices" in oclDeviceDetailsLHS[i]:
                    oclDeviceDetailsLHS[i] = "  Number of devices"
                    oclDeviceDetailsRHS[i] = oclDeviceDetailsRHS[i][len(oclDeviceDetailsLHS[i]):].strip(' ')
                if "OpenCL" in oclDeviceDetailsLHS[i] and ("versions" in oclDeviceDetailsLHS[i] or "features" in oclDeviceDetailsLHS[i]):
                    iter = DeviceDetails_Store.append(None, [oclDeviceDetailsLHS[i].strip('\n'),
                                                             "", setBackgroundColor(i),
                                                             fgcolor[i]])
                    if "versions" in oclDeviceDetailsLHS[i]:
                        DeviceDetails_Store.append(iter,
                                                   [oclDeviceDetailsRHS[i].replace(((oclDeviceDetailsRHS[i].split())[2]+" "+(oclDeviceDetailsRHS[i].split())[3]),""),(oclDeviceDetailsRHS[i].split())[3], setBackgroundColor(i),
                                                    const.COLOR3])
                    if "features" in oclDeviceDetailsLHS[i]:
                        DeviceDetails_Store.append(iter,
                                                   [oclDeviceDetailsRHS[i].replace(((oclDeviceDetailsRHS[i].split())[1]+" "+(oclDeviceDetailsRHS[i].split())[2]),""), (oclDeviceDetailsRHS[i].split())[2], setBackgroundColor(i),
                                                    const.COLOR3])
                    continue
                if "0x" in oclDeviceDetailsRHS[i] and "Device" not in oclDeviceDetailsLHS[i]:
                    if "OpenCL" in oclDeviceDetailsRHS[i]:
                        DeviceDetails_Store.append(iter,
                                                   [oclDeviceDetailsRHS[i].replace(((oclDeviceDetailsRHS[i].split())[2]+" "+(oclDeviceDetailsRHS[i].split())[3]),""),(oclDeviceDetailsRHS[i].split())[3], setBackgroundColor(i),
                                                    const.COLOR3])
                    else:
                        DeviceDetails_Store.append(iter,
                                                   [oclDeviceDetailsRHS[i].replace(((oclDeviceDetailsRHS[i].split())[1]+" "+(oclDeviceDetailsRHS[i].split())[2]),""), (oclDeviceDetailsRHS[i].split())[2], setBackgroundColor(i),
                                                    const.COLOR3])
                    continue
                if "Extensions" in oclDeviceDetailsLHS[i]:
                    oclDeviceExtenstions = oclDeviceDetailsRHS[i].split(" ")
                    oclDeviceExtenstions = list(filter(None,oclDeviceExtenstions))
                    iter = DeviceDetails_Store.append(None, [oclDeviceDetailsLHS[i].strip('\n'),
                                                             str(len(oclDeviceExtenstions)).strip('\n'),
                                                             const.BGCOLOR3, fgcolor[i]])
                    for j in range(len(oclDeviceExtenstions)):
                        DeviceDetailsTreeView.expand_all()
                        DeviceDetails_Store.append(iter,
                                                   [oclDeviceExtenstions[j].strip('\n'), " ", setBackgroundColor(j),
                                                    '#fff'])
                else:
                    iter = DeviceDetails_Store.append(None, [oclDeviceDetailsLHS[i].strip('\n'),
                                                             oclDeviceDetailsRHS[i].strip('\n'), setBackgroundColor(i),
                                                             fgcolor[i]])


    def getDeviceMemoryImageDetails(value):

        value2 = platform_combo.get_active()

        oclPlatformslocal = []
        oclPlatformslocal = oclPlatformslocal + oclPlatforms
        oclPlatformslocal.append("BLANK")

        for i in range(len(oclPlatformslocal)):
            oclPlatformslocal[i] = [j.replace("(", "\(") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = [j.replace(")", "\)") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = ''.join(oclPlatformslocal[i])

        fetch_device_memory_and_image_file_command = "cat %s |  awk '/%s/&& ++n == 2,/%s/' | awk '/Device Name.*/&& ++n == %d,/Extensions.*/'| awk '/Address.*/{flag=1;print}/Queue.*/{flag=0}flag' | uniq" % (Filenames.opencl_output_file,oclPlatformslocal[value2], oclPlatformslocal[value2 + 1], value + 1)
        createMainFile(Filenames.opencl_device_memory_and_image_file,fetch_device_memory_and_image_file_command)

        oclDeviceMemoryImageDetailsLHS = fetchContentsFromCommand(Filenames.fetch_device_memory_and_image_details_lhs_command)
        oclDeviceMemoryImageDetailsRHS = fetchContentsFromCommand(Filenames.fetch_device_memory_and_image_details_rhs_command)

        oclDeviceMemoryImageDetailsLHS = [i.strip('\n') for i in oclDeviceMemoryImageDetailsLHS]
        oclDeviceMemoryImageDetailsRHS = [i.strip('\n') for i in oclDeviceMemoryImageDetailsRHS]

        DeviceMemoryImage_store.clear()
        DeviceMemoryImageTreeview.set_model(DeviceMemoryImage_store)
        fgcolor = []

        for i in range(len(oclDeviceMemoryImageDetailsRHS)):
            if "Yes" in oclDeviceMemoryImageDetailsRHS[i]:
                fgcolor.append("GREEN")
            elif "No" in oclDeviceMemoryImageDetailsRHS[i] and "None" not in oclDeviceMemoryImageDetailsRHS[i]:
                fgcolor.append("RED")
            else:
                fgcolor.append(const.COLOR3)

        for i in range(len(oclDeviceMemoryImageDetailsLHS)):
            DeviceMemoryImageTreeview.expand_all()
            if "    " in oclDeviceMemoryImageDetailsLHS[i]:
                if "Base address alignment for 2D image buffers" in oclDeviceMemoryImageDetailsLHS[i]:
                    oclDeviceMemoryImageDetailsLHS[i] = "    Base address alignment for 2D image buffers"
                    oclDeviceMemoryImageDetailsRHS[i] = oclDeviceMemoryImageDetailsRHS[i][
                                                        len(oclDeviceMemoryImageDetailsLHS[i]):].strip(' ')
                DeviceMemoryImageTreeview.expand_all()
                oclDeviceMemoryImageDetailsLHS[i] = oclDeviceMemoryImageDetailsLHS[i].strip("  ")
                DeviceMemoryImage_store.append(iter, [oclDeviceMemoryImageDetailsLHS[i].strip('\n'),
                                                      oclDeviceMemoryImageDetailsRHS[i].strip('\n'),
                                                      setBackgroundColor(i), fgcolor[i]])
            else:
                if oclDeviceMemoryImageDetailsLHS[i] in oclDeviceMemoryImageDetailsRHS[i]:
                    oclDeviceMemoryImageDetailsRHS[i] = oclDeviceMemoryImageDetailsRHS[i][
                                                        len(oclDeviceMemoryImageDetailsLHS[i]):].strip(' ')
                    iter = DeviceMemoryImage_store.append(None, [oclDeviceMemoryImageDetailsLHS[i].strip('\n'),
                                                                 oclDeviceMemoryImageDetailsRHS[i].strip('\n'),
                                                                 const.BGCOLOR3, fgcolor[i]])
                elif "Built-in" in oclDeviceMemoryImageDetailsLHS[i]:
                    oclDeviceKernels = oclDeviceMemoryImageDetailsRHS[i].split(';')
                    iter = DeviceMemoryImage_store.append(None, [oclDeviceMemoryImageDetailsLHS[i].strip('\n'),
                                                                 str(len(oclDeviceKernels) - 1).strip('\n'),
                                                                 setBackgroundColor(i), fgcolor[i]])
                    for j in range(len(oclDeviceKernels) - 1):
                        DeviceMemoryImageTreeview.expand_all()
                        DeviceMemoryImage_store.append(iter,
                                                       [oclDeviceKernels[j].strip('\n'), " ", setBackgroundColor(j),
                                                        '#fff'])
                else:
                    iter = DeviceMemoryImage_store.append(None, [oclDeviceMemoryImageDetailsLHS[i].strip('\n'),
                                                                 oclDeviceMemoryImageDetailsRHS[i].strip('\n'),
                                                                 setBackgroundColor(i), fgcolor[i]])


    def getDeviceVectorDetails(value):

        value2 = platform_combo.get_active()

        oclPlatformslocal = []
        oclPlatformslocal = oclPlatformslocal + oclPlatforms
        oclPlatformslocal.append("BLANK")

        for i in range(len(oclPlatformslocal)):
            oclPlatformslocal[i] = [j.replace("(", "\(") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = [j.replace(")", "\)") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = ''.join(oclPlatformslocal[i])

        fetch_device_vector_details_file_command = "cat %s | awk '/%s/&& ++n == 2,/%s/' | awk '/Device Name.*/&& ++n == %d,/Extensions.*/'| awk '/Preferred \/.*/{flag=1;print}/Address.*/{flag=0}flag' | uniq" % (Filenames.opencl_output_file, oclPlatformslocal[value2], oclPlatformslocal[value2 + 1], value + 1)
        createMainFile(Filenames.opencl_device_vector_file,fetch_device_vector_details_file_command)

        oclDeviceVectorDetailsLHS = fetchContentsFromCommand(Filenames.fetch_device_vector_details_lhs_command)
        oclDeviceVectorDetailsRHS = fetchContentsFromCommand(Filenames.fetch_device_vector_details_rhs_command)

        oclDeviceVectorDetailsLHS = [i.strip('\n') for i in oclDeviceVectorDetailsLHS]
        oclDeviceVectorDetailsRHS = [i.strip('\n') for i in oclDeviceVectorDetailsRHS]
        DeviceVector_store.clear()
        DeviceVectorTreeview.set_model(DeviceVector_store)
        fgcolor = []

        for i in range(len(oclDeviceVectorDetailsRHS)):
            if "Yes" in oclDeviceVectorDetailsRHS[i]:
                fgcolor.append("GREEN")
            elif "No" in oclDeviceVectorDetailsRHS[i] and "None" not in oclDeviceVectorDetailsRHS[i]:
                fgcolor.append("RED")
            else:
                fgcolor.append(const.COLOR3)

        for i in range(len(oclDeviceVectorDetailsLHS)):
            DeviceVectorTreeview.expand_all()
            if "    " in oclDeviceVectorDetailsLHS[i]:
                DeviceVectorTreeview.expand_all()
                if "Correctly-rounded divide and sqrt operations" in oclDeviceVectorDetailsLHS[i]:
                    oclDeviceVectorDetailsLHS[i] = "    Correctly-rounded divide and sqrt operations"
                    oclDeviceVectorDetailsRHS[i] = oclDeviceVectorDetailsRHS[i][
                                                   len(oclDeviceVectorDetailsLHS[i]):].strip(' ')
                oclDeviceVectorDetailsLHS[i] = oclDeviceVectorDetailsLHS[i].strip("  ")
                DeviceVector_store.append(iter, [oclDeviceVectorDetailsLHS[i].strip('\n'), oclDeviceVectorDetailsRHS[i],
                                                 setBackgroundColor(i), fgcolor[i]])
            else:
                if oclDeviceVectorDetailsLHS[i] in oclDeviceVectorDetailsRHS[i]:
                    oclDeviceVectorDetailsRHS[i] = oclDeviceVectorDetailsRHS[i].strip(oclDeviceVectorDetailsLHS[i])
                iter = DeviceVector_store.append(None, [oclDeviceVectorDetailsLHS[i].strip('\n'),
                                                        oclDeviceVectorDetailsRHS[i].strip('\n'), const.BGCOLOR3,
                                                        fgcolor[i]])

    def getDeviceQueueExecutionCapabilities(value):

        value2 = platform_combo.get_active()

        oclPlatformslocal = []
        oclPlatformslocal = oclPlatformslocal + oclPlatforms
        oclPlatformslocal.append("BLANK")

        for i in range(len(oclPlatformslocal)):
            oclPlatformslocal[i] = [j.replace("(", "\(") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = [j.replace(")", "\)") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = ''.join(oclPlatformslocal[i])

        fetch_device_queue_execution_file_command = "cat %s |  awk '/%s/&& ++n == 2,/%s/' | awk '/Device Name.*/&& ++n == %d,/Extensions.*/' | awk '/Queue.*/{flag=1;print}/Extensions.*/{flag=0}flag' | grep -v Available | uniq" % (Filenames.opencl_output_file,oclPlatformslocal[value2], oclPlatformslocal[value2 + 1], value + 1)
        createMainFile(Filenames.opencl_device_queue_execution_details_file,fetch_device_queue_execution_file_command)

        oclDeviceQueueExecutionDetailsLHS = fetchContentsFromCommand(Filenames.fetch_device_queue_execution_details_lhs_command)
        oclDeviceQueueExecutionDetailsRHS = fetchContentsFromCommand(Filenames.fetch_device_queue_execution_details_rhs_command)

        oclDeviceQueueExecutionDetailsLHS = [i.strip('\n') for i in oclDeviceQueueExecutionDetailsLHS]
        oclDeviceQueueExecutionDetailsRHS = [i.strip('\n') for i in oclDeviceQueueExecutionDetailsRHS]

        DeviceQueueExecution_store.clear()
        DeviceQueueExecutionTreeView.set_model(DeviceQueueExecution_store)
        fgcolor = []

        for i in range(len(oclDeviceQueueExecutionDetailsRHS)):
            if "Yes" in oclDeviceQueueExecutionDetailsRHS[i]:
                fgcolor.append("GREEN")
            elif "No" in oclDeviceQueueExecutionDetailsRHS[i] and "None" not in oclDeviceQueueExecutionDetailsRHS[i]:
                fgcolor.append("RED")
            else:
                fgcolor.append(const.COLOR3)

        for i in range(len(oclDeviceQueueExecutionDetailsLHS)):
            DeviceQueueExecutionTreeView.expand_all()
            if "    " in oclDeviceQueueExecutionDetailsLHS[i] and "0x" not in oclDeviceQueueExecutionDetailsRHS[i]:
                oclDeviceQueueExecutionDetailsLHS[i] = oclDeviceQueueExecutionDetailsLHS[i].strip("  ")
                DeviceQueueExecution_store.append(iter, [oclDeviceQueueExecutionDetailsLHS[i].strip('\n'),
                                                         oclDeviceQueueExecutionDetailsRHS[i].strip('\n'),
                                                         setBackgroundColor(i), fgcolor[i]])
            else:
                if "Built-in" in oclDeviceQueueExecutionDetailsLHS[i] and "version" not in oclDeviceQueueExecutionDetailsLHS[i] and "n/a" not in oclDeviceQueueExecutionDetailsRHS[i]:
                    oclDeviceKernels = oclDeviceQueueExecutionDetailsRHS[i].split(';')
                    iter = DeviceQueueExecution_store.append(None, [oclDeviceQueueExecutionDetailsLHS[i].strip('\n'),
                                                                    str(len(oclDeviceKernels) ).strip('\n'),
                                                                    setBackgroundColor(i), fgcolor[i]])
                    for j in range(len(oclDeviceKernels)):
                        DeviceQueueExecutionTreeView.expand_all()
                        DeviceQueueExecution_store.append(iter,
                                                          [oclDeviceKernels[j].strip('\n'), " ", setBackgroundColor(j),
                                                           '#fff'])
                elif "Built-in" in oclDeviceQueueExecutionDetailsLHS[i] and "version" in oclDeviceQueueExecutionDetailsLHS[i] and "n/a" not in oclDeviceQueueExecutionDetailsRHS[i]:
                    iter = DeviceQueueExecution_store.append(None,[oclDeviceQueueExecutionDetailsLHS[i],"",setBackgroundColor(i),fgcolor[i]])
                    DeviceQueueExecution_store.append(iter,[oclDeviceQueueExecutionDetailsRHS[i].replace(((oclDeviceQueueExecutionDetailsRHS[i].split())[1]+" "+(oclDeviceQueueExecutionDetailsRHS[i].split())[2]),""),(oclDeviceQueueExecutionDetailsRHS[i].split())[2],setBackgroundColor(i),fgcolor[i]])
                elif "0x" in oclDeviceQueueExecutionDetailsRHS[i]:
                    DeviceQueueExecution_store.append(iter,[oclDeviceQueueExecutionDetailsRHS[i].replace(((oclDeviceQueueExecutionDetailsRHS[i].split())[1]+" "+(oclDeviceQueueExecutionDetailsRHS[i].split())[2]),""),(oclDeviceQueueExecutionDetailsRHS[i].split())[2],setBackgroundColor(i),fgcolor[i]])
                    continue
                else:
                    iter = DeviceQueueExecution_store.append(None, [oclDeviceQueueExecutionDetailsLHS[i].strip('\n'),
                                                                    oclDeviceQueueExecutionDetailsRHS[i].strip('\n'),
                                                                    setBackgroundColor(i), fgcolor[i]])

    def selectPlatform(combo):
        value = combo.get_active()
        getDeviceNames(value)
        getPlatfromDetails(value)

    #    os.system("rm /tmp/gpu-viewer/ocl*.txt")

    def searchTreeEntry(model,iter,Tree):
        search_query = searchEntry.get_text().lower()
        for i in range(Tree.get_n_columns()):
            value = model.get_value(iter, i).lower()
        if search_query in value:
                return True

    mainGrid = Gtk.Grid()
    mainGrid.set_row_spacing(10)
    tab.append(mainGrid)

    oclNotebook = Gtk.Notebook()
    mainGrid.attach(oclNotebook, 0, 2, 1, 1)

    platformDetailsTab = Gtk.Box(spacing=10)
    platformDetailsGrid = createSubTab(platformDetailsTab, oclNotebook, "Platform Details")

    platformDetails_Store = Gtk.TreeStore(str, str, str)
    platformDetailsTreeView = Gtk.TreeView.new_with_model(platformDetails_Store)
    platformDetailsTreeView.set_property("enable-grid-lines", 1)
#    platformDetailsTreeView.set_property("enable-tree-lines", True)

    setColumns(platformDetailsTreeView, platformDetailsHeader, const.MWIDTH, 0.0)

    platformScrollbar = create_scrollbar(platformDetailsTreeView)
    platformDetailsGrid.attach(platformScrollbar,0,0,1,1)

    DeviceDetailsTab = Gtk.Box(spacing=10)
    DeviceDetailsGrid = createSubTab(DeviceDetailsTab, oclNotebook, "Device Details")

    DeviceDetails_Store = Gtk.TreeStore(str, str, str, str)
    DeviceDetailsTreeView = Gtk.TreeView.new_with_model(DeviceDetails_Store)
    DeviceDetailsTreeView.set_property("enable-grid-lines", 1)
#    DeviceDetailsTreeView.set_property("enable-tree-lines", True)

    setOclColumns(DeviceDetailsTreeView, deviceDetailsHeader)

    DeviceDetailsScrollbar = create_scrollbar(DeviceDetailsTreeView)

    DeviceDetailsGrid.attach(DeviceDetailsScrollbar,0,0,1,1)

    # Device Memory Details ...

    DeviceMemoryImageTab = Gtk.Box(spacing=10)
    DeviceMemoryImageGrid = createSubTab(DeviceMemoryImageTab, oclNotebook, "Device Memory & Image Details")

    DeviceMemoryImage_store = Gtk.TreeStore(str, str, str, str)
    DeviceMemoryImage_filter = DeviceMemoryImage_store.filter_new()
    DeviceMemoryImageTreeview = Gtk.TreeView.new_with_model(DeviceMemoryImage_store)
    DeviceMemoryImageTreeview.set_property("enable-grid-lines", 1)

 #   DeviceMemoryImageTreeview.set_property("enable-tree-lines", True)

    setOclColumns(DeviceMemoryImageTreeview, deviceMemoryImageHeader)

 #   searchEntry = createSearchEntry(DeviceMemoryImage_filter)
 #   DeviceMemoryImageGrid.attach(searchEntry,0,0,1,1)
    DeviceMemoryImageScrollbar = create_scrollbar(DeviceMemoryImageTreeview)
    DeviceMemoryImageGrid.attach(DeviceMemoryImageScrollbar,0,0,1,1)

 #   DeviceMemoryImage_filter.set_visible_func(searchTreeEntry, data=DeviceMemoryImageTreeview)

    # Device Queue & Execution capabilities

    DeviceQueueExecutionTab = Gtk.Box(spacing=10)
    DeviceQueueExecutionGrid = createSubTab(DeviceQueueExecutionTab, oclNotebook,
                                            "Device Queue & Execution Capabilities")

    DeviceQueueExecution_store = Gtk.TreeStore(str, str, str, str)
    DeviceQueueExecutionTreeView = Gtk.TreeView.new_with_model(DeviceQueueExecution_store)
    DeviceQueueExecutionTreeView.set_property("enable-grid-lines", 1)
 #   DeviceQueueExecutionTreeView.set_property("enable-tree-lines", True)

    setOclColumns(DeviceQueueExecutionTreeView, deviceMemoryImageHeader)

    DeviceQueueExecutionScrollbar = create_scrollbar(DeviceQueueExecutionTreeView)
    DeviceQueueExecutionGrid.attach(DeviceQueueExecutionScrollbar,0,0,1,1)

    # Device Vector Details

    DeviceVectorTab = Gtk.Box(spacing=10)
    DeviceVectorGrid = createSubTab(DeviceVectorTab, oclNotebook, "Device Vector Details")

    DeviceVector_store = Gtk.TreeStore(str, str, str, str)
    DeviceVectorTreeview = Gtk.TreeView.new_with_model(DeviceVector_store)
    DeviceVectorTreeview.set_property("enable-grid-lines", 1)
#    DeviceVectorTreeview.set_property("enable-tree-lines", True)

    setOclColumns(DeviceVectorTreeview, deviceMemoryImageHeader)

    DeviceVectorScrollbar = create_scrollbar(DeviceVectorTreeview)
    DeviceVectorGrid.attach(DeviceVectorScrollbar,0,0,1,1)

    # The Platform Drop Down

    platformGrid = Gtk.Grid()
 #   platformGrid.set_border_width(20)
    platformGrid.set_column_spacing(20)
    platformGrid.set_row_spacing(10)
    #   mainGrid.set_row_spacing(10)
    platformFrame = Gtk.Frame(hexpand=True)
    mainGrid.attach(platformFrame,0,0,1,1)
    platformFrame.set_child(platformGrid)

    platformLabel = Gtk.Label()
    setMargin(platformLabel,30,10,10)
    platformLabel.set_text("Platform Name :")
    platformGrid.attach(platformLabel, 0, 1, 1, 1)

    platform_store = Gtk.ListStore(str)

    oclPlatforms = getPlatformNames()

    AvailableDevices = Gtk.Label()
    
    AvailableDevices.set_label("Available Device(s) :")
    setMargin(AvailableDevices,20,10,10)
    platformGrid.attach_next_to(AvailableDevices, platformLabel, Gtk.PositionType.BOTTOM, 2, 1)

    Devices_store = Gtk.ListStore(str)
    Devices_combo = Gtk.ComboBox.new_with_model(Devices_store)
    setMargin(Devices_combo,30,10,10)
    Devices_combo.connect("changed", selectDevice)
    Devices_renderer = Gtk.CellRendererText(font="BOLD")
    Devices_combo.pack_start(Devices_renderer, True)
    Devices_combo.add_attribute(Devices_renderer, "text", 0)

    platformGrid.attach_next_to(Devices_combo, AvailableDevices, Gtk.PositionType.RIGHT, 20, 1)

    numberOfDevicesEntry = Gtk.Entry()
    setMargin(numberOfDevicesEntry,30,10,10)

    for i in oclPlatforms:
        platform_store.append([i])

    platform_combo = Gtk.ComboBox.new_with_model(platform_store)
    setMargin(platform_combo,30,10,10)
    platform_combo.connect("changed", selectPlatform)
    platform_renderer = Gtk.CellRendererText(font="BOLD")
    platform_combo.pack_start(platform_renderer, True)
    platform_combo.add_attribute(platform_renderer, "text", 0)
    platform_combo.set_active(0)

    platformGrid.attach_next_to(platform_combo, platformLabel, Gtk.PositionType.RIGHT, 21, 1)

    numberOfPlatforms = Gtk.Label()
    setMargin(numberOfPlatforms,30,10,10)
    numberOfPlatforms.set_label("No. of Platforms :")
    platformGrid.attach_next_to(numberOfPlatforms, platform_combo, Gtk.PositionType.RIGHT, 1, 1)

    numberOfPlatformsEntry = Gtk.Entry()
    setMargin(numberOfPlatformsEntry,30,10,10)
    numberOfPlatformsEntry.set_text(str(len(oclPlatforms)))
    numberOfPlatformsEntry.set_editable(False)
    platformGrid.attach_next_to(numberOfPlatformsEntry, numberOfPlatforms, Gtk.PositionType.RIGHT, 1, 1)

    numberOfDevices = Gtk.Label()
    setMargin(numberOfDevices,30,10,10)
    numberOfDevices.set_label("No. Of Devices :")
    platformGrid.attach_next_to(numberOfDevices, Devices_combo, Gtk.PositionType.RIGHT, 1, 1)

    numberOfDevicesEntry.set_max_length(2)
    platformGrid.attach_next_to(numberOfDevicesEntry, numberOfDevices, Gtk.PositionType.RIGHT, 1, 1)



def setOclColumns(Treeview, Title):
    for i, column_title in enumerate(Title):
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(column_title, renderer, text=i)
        column.add_attribute(renderer, "background", len(Title))
        if i == 1:
            column.add_attribute(renderer, "foreground", len(Title) + 1)
        column.set_property("min-width", const.MWIDTH)
        Treeview.set_property("can-focus", False)
        Treeview.append_column(column)
