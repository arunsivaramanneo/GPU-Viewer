import os
import gi
import Const

gi.require_version("Gtk","3.0")

from gi.repository import Gtk

from Common import copyContentsFromFile, createSubTab, createScrollbar, setColumns, setBackgroundColor

platformDetailsHeader = [" "," "]
deviceDetailsHeader = [" "," "]
deviceMemoryImageHeader = [" "," "]

def openCL(tab):

    def getPlatformNames():

        os.system("clinfo -l > /tmp/PlatnDev.txt")
        os.system("cat /tmp/PlatnDev.txt | grep Platform | grep -o :.* | grep -o ' .*' > /tmp/oclPlatformNames.txt")
        oclPlatformName = copyContentsFromFile("/tmp/oclPlatformNames.txt")
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
            oclPlatformslocal[i] = [j.replace("(","\(") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = [j.replace(")","\)") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = ''.join(oclPlatformslocal[i])

        os.system("cat /tmp/PlatnDev.txt | awk '/%s.*/{flag=1;next}/Platform.*/{flag=0}flag'| grep -o :.* | grep -o ' .*' | awk /./ > /tmp/oclDeviceNames.txt"%oclPlatformslocal[value])
        Devices_store.clear()
        Devices_combo.set_model(Devices_store)
        oclDeviceNames = copyContentsFromFile("/tmp/oclDeviceNames.txt")
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
            oclPlatformslocal[i] = [j.replace("(","\(") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = [j.replace(")","\)") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = ''.join(oclPlatformslocal[i])

        os.system("cat /tmp/clinfo.txt | awk '/Number of platforms.*/{flag=1;next}/Number of devices/{flag=0}flag' | awk '/%s/{flag=1;next}/Platform Name/{flag=0}flag' | awk /./> /tmp/oclPlatformDetails.txt"%oclPlatformslocal[value])
        os.system("cat /tmp/oclPlatformDetails.txt | grep -o Platform.* | awk '{gsub(/  .*/,'True');print}' > /tmp/oclPlatformDetailsLHS.txt")
        os.system("cat /tmp/oclPlatformDetails.txt | grep -o Platform.* | awk '{gsub(/Platform.*  /,'True');print}' > /tmp/oclPlatformDetailsRHS.txt")

        oclPlatformDetailsLHS = copyContentsFromFile("/tmp/oclPlatformDetailsLHS.txt")
        oclPlatformDetailsRHS = copyContentsFromFile('/tmp/oclPlatformDetailsRHS.txt')
        platformDetails_Store.clear()
        platformDetailsTreeView.set_model(platformDetails_Store)

        for i in range(len(oclPlatformDetailsLHS)):
            platformDetailsTreeView.expand_all()
            background_color = setBackgroundColor(i)
            if "Extensions" in oclPlatformDetailsLHS[i] and "suffix" not in oclPlatformDetailsLHS[i]:
                oclPlatformExtensions = oclPlatformDetailsRHS[i].split(' ')
                iter = platformDetails_Store.append(None,[oclPlatformDetailsLHS[i].strip('\n'),str(len(oclPlatformExtensions)),background_color])
                for j in range(len(oclPlatformExtensions)):
                    background_color = setBackgroundColor(j)
                    platformDetails_Store.append(iter,[oclPlatformExtensions[j].strip('\n')," ",background_color])
            else:
                platformDetails_Store.append(None,[oclPlatformDetailsLHS[i].strip('\n'),oclPlatformDetailsRHS[i].strip('\n'),background_color])

    def getDeviceDetails(value):

        value2 = platform_combo.get_active()

        oclPlatformslocal = []
        oclPlatformslocal = oclPlatformslocal + oclPlatforms
        oclPlatformslocal.append("BLANK")

        for i in range(len(oclPlatformslocal)):
            oclPlatformslocal[i] = [j.replace("(","\(") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = [j.replace(")","\)") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = ''.join(oclPlatformslocal[i])

        print oclPlatformslocal
        os.system("cat /tmp/clinfo.txt | awk '/%s/&& ++n == 2,/%s*/' | awk '/Device Name.*/&& ++n == %d,/Preferred \/.*/' | grep -v Preferred > /tmp/oclDeviceDetails.txt"%(oclPlatformslocal[value2],oclPlatformslocal[value2+1],value+1))
        os.system("cat /tmp/clinfo.txt |  awk '/%s/&& ++n == 2,/%s/' | awk '/Device Name.*/&& ++n == %d,/Extensions.*/'| awk '/Extensions/' >> /tmp/oclDeviceDetails.txt"%(oclPlatformslocal[value2],oclPlatformslocal[value2+1],value+1))
        os.system("cat /tmp/oclDeviceDetails.txt | awk '{gsub(/     .*/,'True');print}' > /tmp/oclDeviceDetailsLHS.txt")
        os.system("cat /tmp/oclDeviceDetails.txt | awk '{gsub(/^ .*        /,'True');print}' > /tmp/oclDeviceDetailsRHS.txt")

        oclDeviceDetailsLHS = copyContentsFromFile("/tmp/oclDeviceDetailsLHS.txt")
        oclDeviceDetailsRHS = copyContentsFromFile("/tmp/oclDeviceDetailsRHS.txt")

        DeviceDetails_Store.clear()
        DeviceDetailsTreeView.set_model(DeviceDetails_Store)
        fgcolor = []

        for i in range(len(oclDeviceDetailsRHS)):
            if "Yes" in oclDeviceDetailsRHS[i]:
                fgcolor.append("GREEN")
            elif "No" in oclDeviceDetailsRHS[i] and "None" not in oclDeviceDetailsRHS[i]:
                fgcolor.append("RED")
            else:
                fgcolor.append("BLACK")

        for i in range(len(oclDeviceDetailsLHS)):
            DeviceDetailsTreeView.expand_all()
            if "    " in oclDeviceDetailsLHS[i]:
                DeviceDetails_Store.append(iter,[oclDeviceDetailsLHS[i].strip('\n'),oclDeviceDetailsRHS[i].strip('\n'),setBackgroundColor(i),fgcolor[i]])
            else:
                if "Number of devices" in oclDeviceDetailsLHS[i]:
                    oclDeviceDetailsLHS[i] = "  Number of devices"
                    oclDeviceDetailsRHS[i] = oclDeviceDetailsRHS[i][len(oclDeviceDetailsLHS[i]):].strip(' ')
                if "Extensions" in oclDeviceDetailsLHS[i]:
                    oclDeviceExtenstions = oclDeviceDetailsRHS[i].split(' ')
                    iter = DeviceDetails_Store.append(None,[oclDeviceDetailsLHS[i].strip('\n'),str(len(oclDeviceExtenstions)).strip('\n'),setBackgroundColor(i),fgcolor[i]])
                    for j in range(len(oclDeviceExtenstions)):
                        DeviceDetailsTreeView.expand_all()
                        DeviceDetails_Store.append(iter,[oclDeviceExtenstions[j].strip('\n')," ",setBackgroundColor(j),'#fff'])
                else:
                    iter = DeviceDetails_Store.append(None,[oclDeviceDetailsLHS[i].strip('\n'),oclDeviceDetailsRHS[i].strip('\n'),setBackgroundColor(i),fgcolor[i]])

    def getDeviceMemoryImageDetails(value):

        value2 = platform_combo.get_active()

        oclPlatformslocal = []
        oclPlatformslocal = oclPlatformslocal + oclPlatforms
        oclPlatformslocal.append("BLANK")

        for i in range(len(oclPlatformslocal)):
            oclPlatformslocal[i] = [j.replace("(","\(") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = [j.replace(")","\)") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = ''.join(oclPlatformslocal[i])


        os.system("cat /tmp/clinfo.txt |  awk '/%s/&& ++n == 2,/%s/' | awk '/Device Name.*/&& ++n == %d,/Extensions.*/'| awk '/Address.*/{flag=1;print}/Queue.*/{flag=0}flag' | uniq > /tmp/oclDeviceMemoryImageDetails.txt"%(oclPlatformslocal[value2],oclPlatformslocal[value2+1],value+1))
        os.system("cat /tmp/oclDeviceMemoryImageDetails.txt | awk '{gsub(/     .*/,'True');print}' > /tmp/oclDeviceMemoryImageDetailsLHS.txt")
        os.system("cat /tmp/oclDeviceMemoryImageDetails.txt | awk '{gsub(/^ .*        /,'True');print}' > /tmp/oclDeviceMemoryImageDetailsRHS.txt")

        oclDeviceMemoryImageDetailsLHS = copyContentsFromFile("/tmp/oclDeviceMemoryImageDetailsLHS.txt")
        oclDeviceMemoryImageDetailsRHS = copyContentsFromFile("/tmp/oclDeviceMemoryImageDetailsRHS.txt")

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
                fgcolor.append("BLACK")


        for i in range(len(oclDeviceMemoryImageDetailsLHS)):
            DeviceMemoryImageTreeview.expand_all()
            if "    " in oclDeviceMemoryImageDetailsLHS[i]:
                if "Base address alignment for 2D image buffers" in oclDeviceMemoryImageDetailsLHS[i]:
                    oclDeviceMemoryImageDetailsLHS[i] = "    Base address alignment for 2D image buffers"
                    oclDeviceMemoryImageDetailsRHS[i] = oclDeviceMemoryImageDetailsRHS[i][len(oclDeviceMemoryImageDetailsLHS[i]):].strip(' ')
                DeviceMemoryImageTreeview.expand_all()
                DeviceMemoryImage_store.append(iter,[oclDeviceMemoryImageDetailsLHS[i].strip('\n'),oclDeviceMemoryImageDetailsRHS[i].strip('\n'),setBackgroundColor(i),fgcolor[i]])
            else:
                if oclDeviceMemoryImageDetailsLHS[i] in oclDeviceMemoryImageDetailsRHS[i]:
                    oclDeviceMemoryImageDetailsRHS[i] = oclDeviceMemoryImageDetailsRHS[i][len(oclDeviceMemoryImageDetailsLHS[i]):].strip(' ')
                    iter = DeviceMemoryImage_store.append(None,[oclDeviceMemoryImageDetailsLHS[i].strip('\n'),oclDeviceMemoryImageDetailsRHS[i].strip('\n'),setBackgroundColor(i),fgcolor[i]])
                elif "Built-in" in oclDeviceMemoryImageDetailsLHS[i]:
                    oclDeviceKernels = oclDeviceMemoryImageDetailsRHS[i].split(';')
                    iter = DeviceMemoryImage_store.append(None,[oclDeviceMemoryImageDetailsLHS[i].strip('\n'),str(len(oclDeviceKernels)-1).strip('\n'),setBackgroundColor(i),fgcolor[i]])
                    for j in range(len(oclDeviceKernels)-1):
                        DeviceMemoryImageTreeview.expand_all()
                        DeviceMemoryImage_store.append(iter,[oclDeviceKernels[j].strip('\n')," ",setBackgroundColor(j),'#fff'])
                else:
                    iter = DeviceMemoryImage_store.append(None,[oclDeviceMemoryImageDetailsLHS[i].strip('\n'),oclDeviceMemoryImageDetailsRHS[i].strip('\n'),setBackgroundColor(i),fgcolor[i]])

    def getDeviceVectorDetails(value):

        value2 = platform_combo.get_active()

        oclPlatformslocal = []
        oclPlatformslocal = oclPlatformslocal + oclPlatforms
        oclPlatformslocal.append("BLANK")

        for i in range(len(oclPlatformslocal)):
            oclPlatformslocal[i] = [j.replace("(","\(") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = [j.replace(")","\)") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = ''.join(oclPlatformslocal[i])


        os.system("cat /tmp/clinfo.txt | awk '/%s/&& ++n == 2,/%s/' | awk '/Device Name.*/&& ++n == %d,/Extensions.*/'| awk '/Preferred \/.*/{flag=1;print}/Address.*/{flag=0}flag' | uniq > /tmp/oclDeviceVectorDetails.txt"%(oclPlatformslocal[value2],oclPlatformslocal[value2+1],value+1))
        os.system("cat /tmp/oclDeviceVectorDetails.txt | awk '{gsub(/     .*/,'True');print}' > /tmp/oclDeviceVectorDetailsLHS.txt")
        os.system("cat /tmp/oclDeviceVectorDetails.txt | awk '{gsub(/.*          /,'True');print}' > /tmp/oclDeviceVectorDetailsRHS.txt")

        oclDeviceVectorDetailsLHS = copyContentsFromFile("/tmp/oclDeviceVectorDetailsLHS.txt")
        oclDeviceVectorDetailsRHS = copyContentsFromFile("/tmp/oclDeviceVectorDetailsRHS.txt")

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
                fgcolor.append("BLACK")


        for i in range(len(oclDeviceVectorDetailsLHS)):
            DeviceVectorTreeview.expand_all()
            if "    " in oclDeviceVectorDetailsLHS[i]:
                DeviceVectorTreeview.expand_all()
                if "Correctly-rounded divide and sqrt operations" in oclDeviceVectorDetailsLHS[i]:
                    oclDeviceVectorDetailsLHS[i] = "    Correctly-rounded divide and sqrt operations"
                    oclDeviceVectorDetailsRHS[i] = oclDeviceVectorDetailsRHS[i][len(oclDeviceVectorDetailsLHS[i]):].strip(' ')
                DeviceVector_store.append(iter,[oclDeviceVectorDetailsLHS[i].strip('\n'),oclDeviceVectorDetailsRHS[i],setBackgroundColor(i),fgcolor[i]])
            else:
                if oclDeviceVectorDetailsLHS[i] in oclDeviceVectorDetailsRHS[i]:
                    print(oclDeviceVectorDetailsLHS[i])
                    oclDeviceVectorDetailsRHS[i] = oclDeviceVectorDetailsRHS[i].strip(oclDeviceVectorDetailsLHS[i])
                iter = DeviceVector_store.append(None,[oclDeviceVectorDetailsLHS[i].strip('\n'),oclDeviceVectorDetailsRHS[i].strip('\n'),setBackgroundColor(i),fgcolor[i]])

    def getDeviceQueueExecutionCapabilities(value):

        value2 = platform_combo.get_active()

        oclPlatformslocal = []
        oclPlatformslocal = oclPlatformslocal + oclPlatforms
        oclPlatformslocal.append("BLANK")

        for i in range(len(oclPlatformslocal)):
            oclPlatformslocal[i] = [j.replace("(","\(") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = [j.replace(")","\)") for j in oclPlatformslocal[i]]
            oclPlatformslocal[i] = ''.join(oclPlatformslocal[i])

        os.system("cat /tmp/clinfo.txt |  awk '/%s/&& ++n == 2,/%s/' | awk '/Device Name.*/&& ++n == %d,/Extensions.*/' | awk '/Queue.*/{flag=1;print}/Extensions.*/{flag=0}flag' | uniq > /tmp/oclDeviceQueueExecutionDetails.txt"%(oclPlatformslocal[value2],oclPlatformslocal[value2+1],value+1))
        os.system("cat /tmp/oclDeviceQueueExecutionDetails.txt | awk '{gsub(/     .*/,'True');print}' > /tmp/oclDeviceQueueExecutionDetailsLHS.txt")
        os.system("cat /tmp/oclDeviceQueueExecutionDetails.txt | awk '{gsub(/^ .*        /,'True');print}' > /tmp/oclDeviceQueueExecutionDetailsRHS.txt")

        oclDeviceQueueExecutionDetailsLHS = copyContentsFromFile("/tmp/oclDeviceQueueExecutionDetailsLHS.txt")
        oclDeviceQueueExecutionDetailsRHS = copyContentsFromFile("/tmp/oclDeviceQueueExecutionDetailsRHS.txt")

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
                fgcolor.append("BLACK")


        for i in range(len(oclDeviceQueueExecutionDetailsLHS)):
            DeviceQueueExecutionTreeView.expand_all()
            if "    " in oclDeviceQueueExecutionDetailsLHS[i]:
                DeviceQueueExecution_store.append(iter,[oclDeviceQueueExecutionDetailsLHS[i].strip('\n'),oclDeviceQueueExecutionDetailsRHS[i].strip('\n'),setBackgroundColor(i),fgcolor[i]])
            else:
                if oclDeviceQueueExecutionDetailsLHS[i] in oclDeviceQueueExecutionDetailsRHS[i]:
                    oclDeviceQueueExecutionDetailsRHS[i] = oclDeviceQueueExecutionDetailsRHS[i][len(oclDeviceQueueExecutionDetailsLHS[i]):].strip(' ')
                    iter = DeviceQueueExecution_store.append(None,[oclDeviceQueueExecutionDetailsLHS[i].strip('\n'),oclDeviceQueueExecutionDetailsRHS[i].strip('\n'),setBackgroundColor(i),fgcolor[i]])
                elif "Built-in" in oclDeviceQueueExecutionDetailsLHS[i]:
                    oclDeviceKernels = oclDeviceQueueExecutionDetailsRHS[i].split(';')
                    iter = DeviceQueueExecution_store.append(None,[oclDeviceQueueExecutionDetailsLHS[i].strip('\n'),str(len(oclDeviceKernels)-1).strip('\n'),setBackgroundColor(i),fgcolor[i]])
                    for j in range(len(oclDeviceKernels)-1):
                        DeviceQueueExecutionTreeView.expand_all()
                        DeviceQueueExecution_store.append(iter,[oclDeviceKernels[j].strip('\n')," ",setBackgroundColor(j),'#fff'])
                else:
                    iter = DeviceQueueExecution_store.append(None,[oclDeviceQueueExecutionDetailsLHS[i].strip('\n'),oclDeviceQueueExecutionDetailsRHS[i].strip('\n'),setBackgroundColor(i),fgcolor[i]])

    def selectPlatform(combo):
        value = combo.get_active()
        getDeviceNames(value)
        getPlatfromDetails(value)


    #    os.system("rm /tmp/ocl*.txt")

    mainGrid = Gtk.Grid()
    tab.add(mainGrid)


    oclNotebook = Gtk.Notebook()
    mainGrid.attach(oclNotebook,0,2,1,1)

    platformDetailsTab = Gtk.VBox(spacing=10)
    platformDetailsGrid = createSubTab(platformDetailsTab,oclNotebook,"Platform Details")

    platformDetails_Store = Gtk.TreeStore(str,str,str)
    platformDetailsTreeView = Gtk.TreeView(model=platformDetails_Store,expand=True)
    platformDetailsTreeView.set_property("enable-tree-lines",True)

    setColumns(platformDetailsTreeView,platformDetailsHeader,Const.MWIDTH,0.5)

    platformScrollbar = createScrollbar(platformDetailsTreeView)
    platformDetailsGrid.add(platformScrollbar)

    DeviceDetailsTab = Gtk.VBox(spacing=10)
    DeviceDetailsGrid = createSubTab(DeviceDetailsTab,oclNotebook,"Device Details")


    DeviceDetails_Store = Gtk.TreeStore(str,str,str,str)
    DeviceDetailsTreeView = Gtk.TreeView(model=DeviceDetails_Store,expand=True)
    DeviceDetailsTreeView.set_property("enable-tree-lines",True)

    setOclColumns(DeviceDetailsTreeView,deviceDetailsHeader)

    DeviceDetailsScrollbar = createScrollbar(DeviceDetailsTreeView)

    DeviceDetailsGrid.add(DeviceDetailsScrollbar)

# Device Memory Details ...

    DeviceMemoryImageTab = Gtk.VBox(spacing=10)
    DeviceMemoryImageGrid = createSubTab(DeviceMemoryImageTab,oclNotebook,"Device Memory & Image Details")

    DeviceMemoryImage_store = Gtk.TreeStore(str,str,str,str)
    DeviceMemoryImageTreeview = Gtk.TreeView(model=DeviceMemoryImage_store,expand=True)
    DeviceMemoryImageTreeview.set_property("enable-tree-lines",True)

    setOclColumns(DeviceMemoryImageTreeview,deviceMemoryImageHeader)


    DeviceMemoryImageScrollbar = createScrollbar(DeviceMemoryImageTreeview)
    DeviceMemoryImageGrid.add(DeviceMemoryImageScrollbar)

# Device Queue & Execution capabilities

    DeviceQueueExecutionTab = Gtk.VBox(spacing=10)
    DeviceQueueExecutionGrid = createSubTab(DeviceQueueExecutionTab,oclNotebook,"Device Queue & Execution Capabilities")

    DeviceQueueExecution_store = Gtk.TreeStore(str,str,str,str)
    DeviceQueueExecutionTreeView = Gtk.TreeView(model=DeviceQueueExecution_store,expand=True)
    DeviceQueueExecutionTreeView.set_property("enable-tree-lines",True)

    setOclColumns(DeviceQueueExecutionTreeView,deviceMemoryImageHeader)

    DeviceQueueExecutionScrollbar = createScrollbar(DeviceQueueExecutionTreeView)
    DeviceQueueExecutionGrid.add(DeviceQueueExecutionScrollbar)

# Device Vector Details

    DeviceVectorTab = Gtk.VBox(spacing=10)
    DeviceVectorGrid = createSubTab(DeviceVectorTab,oclNotebook,"Device Vector Details")

    DeviceVector_store = Gtk.TreeStore(str,str,str,str)
    DeviceVectorTreeview = Gtk.TreeView(model=DeviceVector_store,expand=True)
    DeviceVectorTreeview.set_property("enable-tree-lines",True)

    setOclColumns(DeviceVectorTreeview,deviceMemoryImageHeader)


    DeviceVectorScrollbar = createScrollbar(DeviceVectorTreeview)
    DeviceVectorGrid.add(DeviceVectorScrollbar)

# The Platform Drop Down

    platformGrid = Gtk.Grid()
    platformGrid.set_border_width(20)
    platformGrid.set_column_spacing(20)
    platformGrid.set_row_spacing(20)
    mainGrid.set_row_spacing(30)
    platformFrame = Gtk.Frame(hexpand=True)
    mainGrid.add(platformFrame)
    platformFrame.add(platformGrid)

    platformLabel = Gtk.Label()
    platformLabel.set_text("Platform Name :")
    platformGrid.attach(platformLabel,0,1,1,1)

    platform_store = Gtk.ListStore(str)

    oclPlatforms = getPlatformNames()

    AvailableDevices = Gtk.Label()
    AvailableDevices.set_label("Available Device(s) :")
    platformGrid.attach_next_to(AvailableDevices,platformLabel,Gtk.PositionType.BOTTOM,2,1)

    Devices_store = Gtk.ListStore(str)
    Devices_combo = Gtk.ComboBox.new_with_model(Devices_store)
    Devices_combo.connect("changed",selectDevice)
    Devices_renderer = Gtk.CellRendererText(font="BOLD")
    Devices_combo.pack_start(Devices_renderer, True)
    Devices_combo.add_attribute(Devices_renderer, "text", 0)


    platformGrid.attach_next_to(Devices_combo,AvailableDevices,Gtk.PositionType.RIGHT,20,1)

    numberOfDevicesEntry = Gtk.Entry()

    for i in oclPlatforms:
        platform_store.append([i])

    platform_combo = Gtk.ComboBox.new_with_model(platform_store)
    platform_combo.connect("changed",selectPlatform)
    platform_renderer = Gtk.CellRendererText(font="BOLD")
    platform_combo.pack_start(platform_renderer, True)
    platform_combo.add_attribute(platform_renderer, "text", 0)
    platform_combo.set_active(0)

    platformGrid.attach_next_to(platform_combo,platformLabel,Gtk.PositionType.RIGHT,21,1)

    numberOfPlatforms = Gtk.Label()
    numberOfPlatforms.set_label("No. of Platforms :")
    platformGrid.attach_next_to(numberOfPlatforms,platform_combo,Gtk.PositionType.RIGHT,10,1)

    numberOfPlatformsEntry = Gtk.Entry()
    numberOfPlatformsEntry.set_text(str(len(oclPlatforms)))
    numberOfPlatformsEntry.set_editable(False)
    platformGrid.attach_next_to(numberOfPlatformsEntry,numberOfPlatforms,Gtk.PositionType.RIGHT,1,1)

    numberOfDevices = Gtk.Label()
    numberOfDevices.set_label("No. Of Devices :")
    platformGrid.attach_next_to(numberOfDevices,Devices_combo,Gtk.PositionType.RIGHT,10,1)


    numberOfDevicesEntry.set_max_length(2)
    platformGrid.attach_next_to(numberOfDevicesEntry,numberOfDevices,Gtk.PositionType.RIGHT,1,1)


    tab.show_all()


def setOclColumns(Treeview,Title):
    for i, column_title in enumerate(Title):
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(column_title, renderer, text=i)
        column.add_attribute(renderer, "background", len(Title))
        if i == 1:
            column.add_attribute(renderer, "foreground", len(Title) + 1)
        column.set_property("min-width", Const.MWIDTH)
        Treeview.set_property("can-focus", False)
        Treeview.append_column(column)
