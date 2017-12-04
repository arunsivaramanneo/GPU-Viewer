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
        os.system("clinfo -l | grep Platform | grep -o :.* | grep -o ' .*' > /tmp/oclPlatformNames.txt")
        os.system("clinfo -l | grep Device | grep -o :.* | grep -o ' .*' > /tmp/oclDeviceNames.txt")
        oclPlatformName = copyContentsFromFile("/tmp/oclPlatformNames.txt")
        oclPlatformName = [i.strip(' ') for i in oclPlatformName]
        oclPlatformName = [i.strip('\n') for i in oclPlatformName]
        oclDeviceNames = copyContentsFromFile("/tmp/oclDeviceNames.txt")
        oclDeviceNames = [i.strip(' ') for i in oclDeviceNames]
        oclDeviceNames = [i.strip('\n') for i in oclDeviceNames]

        os.system("clinfo > /tmp/clinfo.txt")
        return oclPlatformName,oclDeviceNames

    def getPlatfromDetails(value):

        os.system("cat /tmp/clinfo.txt | awk '/Number of platforms.*/{flag=1;next}/Number of devices/{flag=0}flag' | awk '/%s/{flag=1;next}/Platform Name/{flag=0}flag' | awk /./> /tmp/oclPlatformDetails.txt"%oclPlatforms[value])
        os.system("cat /tmp/oclPlatformDetails.txt | grep -o Platform.* | awk '{gsub(/  .*/,'True');print}' > /tmp/oclPlatformDetailsLHS.txt")
        os.system("cat /tmp/oclPlatformDetails.txt | grep -o Platform.* | awk '{gsub(/Platform.*  /,'True');print}' > /tmp/oclPlatformDetailsRHS.txt")

        oclPlatformDetailsLHS = copyContentsFromFile("/tmp/oclPlatformDetailsLHS.txt")
        oclPlatformDetailsRHS = copyContentsFromFile('/tmp/oclPlatformDetailsRHS.txt')
        platformDetails_Store.clear()
        platformDetailsTreeView.set_model(platformDetails_Store)
        oclPlatformExtensions = oclPlatformDetailsRHS[3].split(' ')

        for i in range(len(oclPlatformDetailsLHS)):
            platformDetailsTreeView.expand_all()
            background_color = setBackgroundColor(i)
            if i == 3:
                iter = platformDetails_Store.append(None,[oclPlatformDetailsLHS[i].strip('\n'),str(len(oclPlatformExtensions)),background_color])
                for j in range(len(oclPlatformExtensions)):
                    background_color = setBackgroundColor(j)
                    platformDetails_Store.append(iter,[oclPlatformExtensions[j].strip('\n')," ",background_color])
            else:
                platformDetails_Store.append(None,[oclPlatformDetailsLHS[i].strip('\n'),oclPlatformDetailsRHS[i].strip('\n'),background_color])

    def getDeviceDetails(value):

        os.system("cat /tmp/clinfo.txt | awk '/%s/{flag=1}/Preferred \/.*/{flag=0}flag'  > /tmp/oclDeviceDetails.txt"%oclDevices[value].strip('Intel(R)'))
        os.system("cat /tmp/clinfo.txt | awk '/%s/{flag=1}/Platform.*/{flag=0}flag'| awk '/Extensions/' >> /tmp/oclDeviceDetails.txt"%oclDevices[value].strip('Intel(R)'))
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
                if "Extensions" in oclDeviceDetailsLHS[i]:
                    oclDeviceExtenstions = oclDeviceDetailsRHS[i].split(' ')
                    iter = DeviceDetails_Store.append(None,[oclDeviceDetailsLHS[i].strip('\n'),str(len(oclDeviceExtenstions)).strip('\n'),setBackgroundColor(i),fgcolor[i]])
                    for j in range(len(oclDeviceExtenstions)):
                        DeviceDetailsTreeView.expand_all()
                        DeviceDetails_Store.append(iter,[oclDeviceExtenstions[j].strip('\n')," ",setBackgroundColor(j),'#fff'])
                else:
                    iter = DeviceDetails_Store.append(None,[oclDeviceDetailsLHS[i].strip('\n'),oclDeviceDetailsRHS[i].strip('\n'),setBackgroundColor(i),fgcolor[i]])

    def getDeviceMemoryImageDetails(value):

        os.system("cat /tmp/clinfo.txt | awk '/%s/{flag=1}/Platform.*/{flag=0}flag' | awk '/Address.*/{flag=1;print}/Extensions.*/{flag=0}flag' | uniq > /tmp/oclDeviceMemoryImageDetails.txt"%oclDevices[value].strip('Intel(R)'))
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
            DeviceDetailsTreeView.expand_all()
            if "    " in oclDeviceMemoryImageDetailsLHS[i]:
                if "Base address alignment for 2D image buffers" in oclDeviceMemoryImageDetailsLHS[i]:
                    oclDeviceMemoryImageDetailsLHS[i] = "    Base address alignment for 2D image buffers"
                    oclDeviceMemoryImageDetailsRHS[i] = oclDeviceMemoryImageDetailsRHS[i][len(oclDeviceMemoryImageDetailsLHS[i]):].strip(' ')
                DeviceMemoryImageTreeview.expand_all()
                DeviceMemoryImage_store.append(iter,[oclDeviceMemoryImageDetailsLHS[i].strip('\n'),oclDeviceMemoryImageDetailsRHS[i].strip('\n'),setBackgroundColor(i),fgcolor[i]])
            else:
                if oclDeviceMemoryImageDetailsLHS[i] in oclDeviceMemoryImageDetailsRHS[i]:
                    oclDeviceMemoryImageDetailsRHS[i] = oclDeviceMemoryImageDetailsRHS[i].strip(oclDeviceMemoryImageDetailsLHS[i])
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

        os.system("cat /tmp/clinfo.txt | awk '/%s/{flag=1}/Platform.*/{flag=0}flag' | awk '/Preferred \/.*/{flag=1;print}/Address.*/{flag=0}flag' | uniq > /tmp/oclDeviceVectorDetails.txt"%oclDevices[value].strip('Intel(R)'))
        os.system("cat /tmp/oclDeviceVectorDetails.txt | awk '{gsub(/     .*/,'True');print}' > /tmp/oclDeviceVectorDetailsLHS.txt")
        os.system("cat /tmp/oclDeviceVectorDetails.txt | awk '{gsub(/^ .*        /,'True');print}' > /tmp/oclDeviceVectorDetailsRHS.txt")

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
            DeviceDetailsTreeView.expand_all()
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

    def selectPlatform(combo):
        value = combo.get_active()
        getPlatfromDetails(value)
        getDeviceDetails(value)
        getDeviceMemoryImageDetails(value)
        getDeviceVectorDetails(value)
        os.system("rm /tmp/ocl*.txt")

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
    platformGrid.set_column_spacing(30)
    mainGrid.set_row_spacing(30)
    platformFrame = Gtk.Frame(hexpand=True)
    mainGrid.add(platformFrame)
    platformFrame.add(platformGrid)

    platformLabel = Gtk.Label()
    platformLabel.set_text("Platform Name :")
    platformGrid.attach(platformLabel,0,1,1,1)

    platform_store = Gtk.ListStore(str)

    oclPlatforms,oclDevices = getPlatformNames()

    for i in oclPlatforms:
        platform_store.append([i])

    platform_combo = Gtk.ComboBox.new_with_model(platform_store)
    platform_combo.connect("changed",selectPlatform)
    platform_renderer = Gtk.CellRendererText()
    platform_combo.pack_start(platform_renderer, True)
    platform_combo.add_attribute(platform_renderer, "text", 0)
    platform_combo.set_active(0)

    platformGrid.attach_next_to(platform_combo,platformLabel,Gtk.PositionType.RIGHT,25,1)



    tab.show_all()


def setOclColumns(Treeview,Title):
    for i, column_title in enumerate(Title):
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(column_title, renderer, text=i)
        column.add_attribute(renderer, "background", len(Title))
        if i == 1:
            column.add_attribute(renderer, "foreground", len(Title) + 1)
        Treeview.set_property("can-focus", False)
        Treeview.append_column(column)