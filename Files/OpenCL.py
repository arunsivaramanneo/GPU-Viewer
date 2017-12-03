import os
import gi
import Const

gi.require_version("Gtk","3.0")

from gi.repository import Gtk

from Common import copyContentsFromFile, createSubTab, createScrollbar, setColumns, setBackgroundColor

platformDetailsHeader = [" "," "]

def openCL(tab):

    def getPlatformNames():
        os.system("cat /tmp/clinfo.txt | grep 'Platform Name' | sort | uniq | awk '{gsub(/Platform Name/,'True');print}' > /tmp/oclPlatformNames.txt")
        oclPlatformName = copyContentsFromFile("/tmp/oclPlatformNames.txt")
        oclPlatformName = [i.strip(' ') for i in oclPlatformName]
        oclPlatformName = [i.strip('\n') for i in oclPlatformName]
        return oclPlatformName

    def setPlatfromDetails(value):

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

    def selectPlatform(combo):
        value = combo.get_active()
        setPlatfromDetails(value)

    mainGrid = Gtk.Grid()
    tab.add(mainGrid)


    oclNotebook = Gtk.Notebook()
    mainGrid.attach(oclNotebook,0,2,1,1)

    platformDetailsTab = Gtk.VBox(spacing=10)
    platformDetailsGrid = createSubTab(platformDetailsTab,oclNotebook,"Platform Details")

    platformDetails_Store = Gtk.TreeStore(str,str,str)
    platformDetailsTreeView = Gtk.TreeView(model=platformDetails_Store,expand=True)

    setColumns(platformDetailsTreeView,platformDetailsHeader,Const.MWIDTH,0.5)

    platformScrollbar = createScrollbar(platformDetailsTreeView)
    platformDetailsGrid.add(platformScrollbar)

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

    oclPlatforms = getPlatformNames()

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