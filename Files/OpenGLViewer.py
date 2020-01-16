import os
import gi
import Const

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from FrameBuffer import FrameBuffer
from Common import setScreenSize, fetchImageFromUrl, copyContentsFromFile, setBackgroundColor, setColumns, \
    createScrollbar, refresh_filter, appendLimitsRHS

WH = 70
switchCount = 0

Title1 = [" "]
Title2 = ["OpenGL Information ", " Details"]
LimitsTitle = ["OpenGL Hardware Limits", "Value"]


def OpenGL(tab1):
    grid = Gtk.Grid()
    grid.set_row_spacing(10)
    grid.set_column_spacing(10)
    tab1.add(grid)
    grid4 = Gtk.Grid()
#    grid4.set_row_spacing(5)
    frame1 = Gtk.Frame(label="", expand=True)
    grid.attach(frame1, 0, 0, 12, 1)
    frame1.add(grid4)
    OpenGLInfo_list = Gtk.ListStore(str, str, str)
    os.system("glxinfo -s > /tmp/gpu-viewer/glxinfo.txt")
    os.system("cat /tmp/gpu-viewer/glxinfo.txt | grep string | grep -v glx > /tmp/gpu-viewer/OpenGL_Information.txt")
    os.system("es2_info | awk '/EGL_VERSION|VENDOR/' >> /tmp/gpu-viewer/OpenGL_Information.txt")
    os.system("cat /tmp/gpu-viewer/OpenGL_Information.txt | grep -o :.* | grep -o ' .*' > /tmp/gpu-viewer/OpenGLRHS.txt")
    os.system("cat /tmp/gpu-viewer/glxinfo.txt | grep memory: | grep -o :.* | grep -o ' .*' >> /tmp/gpu-viewer/OpenGLRHS.txt")
    os.system("cat /tmp/gpu-viewer/OpenGL_Information.txt | awk '{gsub(/string|:.*/,'True');print}' > /tmp/gpu-viewer/OpenGLLHS.txt")
    os.system("cat /tmp/gpu-viewer/glxinfo.txt | grep memory: | awk '{gsub(/:.*/,'True');print}' >> /tmp/gpu-viewer/OpenGLLHS.txt")
    value = copyContentsFromFile("/tmp/gpu-viewer/OpenGLRHS.txt")

    with open("/tmp/gpu-viewer/OpenGLLHS.txt", "r") as file1:
        for i,line in enumerate(file1):
            text = line.strip(" ")
            background_color = setBackgroundColor(i)
            OpenGLInfo_list.append([text.strip('\n'), value[i].strip('\n'), background_color])


    TreeGL = Gtk.TreeView(OpenGLInfo_list, expand=True)
    # TreeGL.set_enable_search(True)
    setColumns(TreeGL, Title2, Const.MWIDTH,0.0)

    scrollable_treelist = createScrollbar(TreeGL)
    grid4.add(scrollable_treelist)


    def clickme(button):

        button.set_sensitive(False)
        os.system(
            "glxinfo -l | awk '/OpenGL core profile limits:/{flag=1}/GLX Visuals.*/{flag=0} flag' | awk '/OpenGL core profile limits:/{flag=1;next}/OpenGL version string.*/{flag=0} flag' | awk '/./'  > /tmp/gpu-viewer/OpenGL_Core_Limits.txt")
        os.system("cat /tmp/gpu-viewer/OpenGL_Core_Limits.txt | awk '{gsub(/=.*/,'True');print}' > /tmp/gpu-viewer/OpenGLCoreLimitsLHS.txt")
        LimitsWin = Gtk.Window()
        LimitsWin.set_title("OpenGL Hardware Limits")
        #    LimitsWin.set_size_request(1000, 500)
        setScreenSize(LimitsWin, Const.WIDTH_RATIO, Const.HEIGHT_RATIO2)
        LimitsWin.set_border_width(10)
        LimitsNotebook = Gtk.Notebook()
        LimitsWin.add(LimitsNotebook)
        LimitsCoreTab = Gtk.Box("spacing=10")
        LimitsNotebook.add(LimitsCoreTab)
        LimitsNotebook.set_tab_label(LimitsCoreTab,Gtk.Label("\tCore\t"))
        LimitsCoreFrame = Gtk.Frame()
        limitsCombo = Gtk.ComboBoxText()


        # get Combo box value

        limitsCombo.remove_all()
        with open("/tmp/gpu-viewer/OpenGLCoreLimitsLHS.txt","r") as file1:
            for line in file1:
                if ":" in line:
                    text = line[:-2]
                    limitsCombo.append_text(text.strip(" "))

        limitsCombo.insert_text(0,"Show All OpenGL Hardware Core Limits")



        LimitsCoreTab.add(LimitsCoreFrame)
        LimitsGrid = Gtk.Grid()
        LimitsGrid.set_row_spacing(5)
        LimitsCoreFrame.add(LimitsGrid)
        LimitsGrid.add(limitsCombo)
        LimitsCore_Store = Gtk.TreeStore(str, str, str)
        TreeCoreLimits = Gtk.TreeView(LimitsCore_Store, expand=True)
        TreeCoreLimits.set_property("enable-tree-lines",True)


        limitsCombo.connect("changed",showLimits, LimitsCore_Store, TreeCoreLimits,"/tmp/gpu-viewer/OpenGL_Core_Limits.txt")
        limitsCombo.set_active(0)

    #    showLimits(LimitRHSValue, LimitsRHS, LimitsCore_Store, TreeCoreLimits,"/tmp/gpu-viewer/OpenGLCoreLimitsLHS.txt")

        setColumns(TreeCoreLimits, LimitsTitle, Const.MWIDTH,0.0)
        LimitsCoreScrollbar = createScrollbar(TreeCoreLimits)
        LimitsGrid.attach_next_to(LimitsCoreScrollbar,limitsCombo,Gtk.PositionType.BOTTOM,1,1)

        os.system(
            "glxinfo -l | awk '/OpenGL limits:/{flag=1}/GLX Visuals.*/{flag=0} flag' | awk '/OpenGL limits:/{flag=1;next}/OpenGL ES profile/{flag=0} flag' | awk '/./'  > /tmp/gpu-viewer/OpenGL_Limits.txt")
        os.system("cat /tmp/gpu-viewer/OpenGL_Limits.txt | awk '{gsub(/=.*/,'True');print}' > /tmp/gpu-viewer/OpenGLLimitsLHS.txt")
        LimitsCompatTab = Gtk.Box("spacing=10")
        LimitsNotebook.add(LimitsCompatTab)
        LimitsNotebook.set_tab_label(LimitsCompatTab,Gtk.Label("    Compat.\t"))
        LimitsCompatFrame = Gtk.Frame()
        limitsCompatCombo = Gtk.ComboBoxText()

        limitsCompatCombo.remove_all()
        with open("/tmp/gpu-viewer/OpenGLLimitsLHS.txt","r") as file1:
            for line in file1:
                if ":" in line:
                    text = line[:-2]
                    limitsCompatCombo.append_text(text.strip(" "))

        limitsCompatCombo.insert_text(0,"Show All OpenGL Hardware Compatible Limits")

        LimitsCompatTab.add(LimitsCompatFrame)
        limitsCompatGrid = Gtk.Grid()
        limitsCompatGrid.set_row_spacing(5)
        LimitsCompatFrame.add(limitsCompatGrid)
        limitsCompatGrid.add(limitsCompatCombo)
        LimitsCompat_Store = Gtk.TreeStore(str,str,str)
        TreeCompatLimits = Gtk.TreeView(LimitsCompat_Store,expand=True)
        TreeCompatLimits.set_property("enable-tree-lines",True)

        limitsCompatCombo.connect("changed",showLimits, LimitsCompat_Store, TreeCompatLimits,"/tmp/gpu-viewer/OpenGL_Limits.txt")
        limitsCompatCombo.set_active(0)


     #   showLimits(LimitRHSValue2, LimitsRHS2, LimitsCompat_Store, TreeCompatLimits,"/tmp/gpu-viewer/OpenGLLimitsLHS.txt")

        setColumns(TreeCompatLimits, LimitsTitle, Const.MWIDTH,0.0)
        LimitsCompatScrollbar = createScrollbar(TreeCompatLimits)
        limitsCompatGrid.attach_next_to(LimitsCompatScrollbar,limitsCompatCombo,Gtk.PositionType.BOTTOM,1,1)

        def button_enable(win,value):
            button.set_sensitive(True)
        LimitsWin.connect("delete-event",button_enable)

        LimitsWin.show_all()

    def showLimits(Combo, Limits_Store, TreeLimits,openGLLimits):
        k = 0
        count = 0
        limitValue = Combo.get_active_text()
        if "Show All OpenGL Hardware Core Limits" in limitValue or "Show All OpenGL Hardware Compatible Limits" in limitValue:
            os.system(
                "cat %s > /tmp/gpu-viewer/selectOpenglLimits.txt"%openGLLimits)

            os.system("cat /tmp/gpu-viewer/selectOpenglLimits.txt | awk '{gsub(/=.*/,'True');print}' > /tmp/gpu-viewer/OpenGLLimitsLHS.txt")
            os.system("cat /tmp/gpu-viewer/selectOpenglLimits.txt | grep -o =.* | grep -o ' .*' > /tmp/gpu-viewer/OpenGLLimitsRHS.txt")

        else:
            with open(openGLLimits,"r") as file1:
                for line in file1:
                    if limitValue in line:
                        os.system("cat %s | awk '/%s:/{flag=1;next}/:.*/{flag=0}flag' > /tmp/gpu-viewer/selectOpenglLimits.txt"%(openGLLimits,limitValue))
                        os.system("cat /tmp/gpu-viewer/selectOpenglLimits.txt | awk '{gsub(/=.*/,'True');print}' > /tmp/gpu-viewer/OpenGLLimitsLHS.txt")
                        os.system("cat /tmp/gpu-viewer/selectOpenglLimits.txt | grep -o =.* | grep -o ' .*' > /tmp/gpu-viewer/OpenGLLimitsRHS.txt")


        with open("/tmp/gpu-viewer/OpenGLLimitsLHS.txt", "r") as file1:
            temp = copyContentsFromFile("/tmp/gpu-viewer/OpenGLLimitsRHS.txt")
            LimitsRHS,LimitRHSValue = appendLimitsRHS("/tmp/gpu-viewer/selectOpenglLimits.txt",temp)

            Limits_Store.clear()
            TreeLimits.set_model(Limits_Store)
            for i, line in enumerate(file1):
                background_color = setBackgroundColor(k)
                k += 1
                TreeLimits.expand_all()
                text = line.strip(' ')
                if ("TEXTURE_FORMATS" in line or "SHADING_LANGUAGE" in line) and LimitRHSValue[i] == True:
                    try:
                        iter3 = Limits_Store.append(iter2, [text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                    except Exception:
                        iter3 = Limits_Store.append(None, [text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                    finally:
                        pass
                elif "      " in line and LimitRHSValue[i] == False and ":" not in line:
                    Limits_Store.append(iter3, [text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                else:
                    if ":" in line:
                        k = 0
                        text = line[:-2]
                        count += 1
                        iter2 = Limits_Store.append(None,
                                                    [text.strip('\n'), LimitsRHS[i].strip('\n'), Const.BGCOLOR3])
                        continue
                    if count > 0 and "    " in line:
                        Limits_Store.append(iter2, [text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                    else:
                        Limits_Store.append(None, [text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])

  #  LimitsFrame = Gtk.Frame()
  #  grid.attach(LimitsFrame, 0, 1, 2, 1)
    Button_Limits = Gtk.Button("Show OpenGL Limits")
    Button_Limits.connect("clicked", clickme)
    grid.attach(Button_Limits,0,1,2,1)
  #  LimitsFrame.add(Button_Limits)
    # grid4.attach(Button_Limits, 0, 1, 2, 1)

    # vendorFrame = Gtk.Frame()
    # grid.attach_next_to(vendorFrame,LimitsFrame,Gtk.PositionType.RIGHT,1,1)

  #  FBFrame = Gtk.Frame()
    Button_FB = Gtk.Button.new_with_label("Show GLX Frame Buffer Configuration")
    Button_FB.connect("clicked", FrameBuffer)
  #  FBFrame.add(Button_FB)

    with open("/tmp/gpu-viewer/OpenGLRHS.txt", "r") as file1:
        for line in file1:
            if "Intel" in line:
                vendorImg = fetchImageFromUrl(Const.INTEL_LOGO_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
                grid.attach_next_to(Gtk.Image.new_from_pixbuf(vendorImg), Button_Limits, Gtk.PositionType.RIGHT, 1, 1)
                break
            elif "NVIDIA" in line:
                vendorImg = fetchImageFromUrl(Const.GTX_LOGO_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
                grid.attach_next_to(Gtk.Image.new_from_pixbuf(vendorImg), Button_Limits, Gtk.PositionType.RIGHT, 1, 1)
                break
            elif "AMD" in line or "ATI" in line:
                vendorImg = fetchImageFromUrl(Const.AMD_LOGO_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
                grid.attach_next_to(Gtk.Image.new_from_pixbuf(vendorImg), Button_Limits, Gtk.PositionType.RIGHT, 1, 1)
                break

        # vendorFrame.add(Gtk.Image.new_from_pixbuf(vendorImg))
        grid.attach(Button_FB, 3, 1, 2, 1)

    # End of Frame 1
    OpenGLExt_list = Gtk.ListStore(str, str)
    OpenGLExt_list_filter = OpenGLExt_list.filter_new()
    TreeGLExt = Gtk.TreeView(OpenGLExt_list_filter, expand=True)
    TreeGLExt.set_headers_visible(False)
    frame4 = Gtk.Frame(label=" ")

    def radcall2(button):
        value = button.get_active()

        GL_All = []

        List = copyContentsFromFile("/tmp/gpu-viewer/Vendor1.txt")

        List = [i.strip(' ') for i in List]
        List = [i.strip('\n ') for i in List]
        List.insert(0, " ALL")

        with open("/tmp/gpu-viewer/extensions.txt", "r") as file1:
            for line in file1:
                if List[int(value)] == " ALL":
                    GL_All.append(line)
                elif List[int(value)] != " ALL":
                    if "_%s_" % List[int(value)] in line:
                        GL_All.append(line)

        OpenGLExt_list.clear()
        TreeGLExt.set_model(OpenGLExt_list_filter)

        for i in range(len(List)):
            if int(value) == i:
                frame4.set_label(List[i])

        count = len(GL_All)
        for i in range(count):
            background_color = setBackgroundColor(i)
            text = GL_All[i].strip(' ')
            OpenGLExt_list.append([text.strip('\n'), background_color])

    VendorExt_list = Gtk.ListStore(str, bool, str)
    TreeVendor = Gtk.TreeView(VendorExt_list, expand=True)

    Vendor_Store = Gtk.ListStore(str)
    Vendor_Combo = Gtk.ComboBox.new_with_model(Vendor_Store)

    def Radio(value):

        if 1 <= value <= 2:
            os.system("cat /tmp/gpu-viewer/extensions.txt | awk 'gsub(/GL_|_.*/,'true')'| uniq > /tmp/gpu-viewer/Vendor.txt")
            os.system("cat /tmp/gpu-viewer/extensions.txt | awk 'gsub(/GLX_|_.*/,'true')'| uniq >> /tmp/gpu-viewer/Vendor.txt")
            os.system("cat /tmp/gpu-viewer/Vendor.txt | sort | uniq | grep -v GLX | grep -v GL$  > /tmp/gpu-viewer/Vendor1.txt")

        if value == 3:
            os.system("cat /tmp/gpu-viewer/extensions.txt | awk 'gsub(/EGL_|_.*/,'true')'| sort | uniq > /tmp/gpu-viewer/Vendor1.txt")

        vCount = []
        vendorList = []
        with open("/tmp/gpu-viewer/Vendor1.txt", "r") as file1:
            for line in file1:
                vendorList.append(line)

        vendorList = [i.strip(' ') for i in vendorList]
        vendorList = [i.strip('\n ') for i in vendorList]
        vendorList.insert(0, "Total")

        with open("/tmp/gpu-viewer/extensions.txt", "r") as file1:
            for i in range(len(vendorList)):
                file1.seek(0, 0)
                GL_All = []
                for line in file1:
                    if vendorList[i] == "Total":
                        GL_All.append(line)
                    elif vendorList[i] != "Total":
                        if "_%s_" % vendorList[i] in line:
                            GL_All.append(line)
                vCount.append(len(GL_All))

        NewList = []
        for i in range(len(vendorList)):
            NewList.append("%s (%d)" % (vendorList[i], vCount[i]))

        VendorExt_list.clear()
        TreeVendor.set_model(VendorExt_list)
        Toggle = []
        for i in range(len(NewList) - 1):
            Toggle.append(False)
        Vendor_Store.clear()
        Vendor_Combo.set_model(Vendor_Store)
        Toggle.insert(True, 0)
        for i in range(len(NewList)):
            background_color = setBackgroundColor(i)
            VendorExt_list.append([NewList[i], Toggle[i], background_color])
            Vendor_Store.append([NewList[i]])

    def radcall(button, value):
        if value == 1:
            try:
                switch.set_active(True)
                switch.set_sensitive(True)
            except:
                pass
            os.system(
                "cat /tmp/gpu-viewer/glxinfo.txt | awk '/OpenGL extensions/{flag=1;next}/OpenGL ES profile/{flag=0} flag' | grep GL_ | sort > /tmp/gpu-viewer/extensions.txt")
            os.system(
                "cat /tmp/gpu-viewer/glxinfo.txt  | awk '/client glx extensions/{flag=1; next}/GLX version/{flag=0} flag' | grep GLX_ | sort >> /tmp/gpu-viewer/extensions.txt")

        elif value == 2:
            switch.set_active(True)
            switch.set_sensitive(False)
            os.system(
                "cat /tmp/gpu-viewer/glxinfo.txt  | awk '/OpenGL ES profile/{flag=1;next}/80 GLX Visuals/{flag=0} flag' | grep GL_ | sort > /tmp/gpu-viewer/extensions.txt")

        elif value == 3:
            switch.set_active(True)
            switch.set_sensitive(False)
            os.system("es2_info | awk '/EGL_EXTENSIONS.*/{flag=1;next}/EGL_CLIENT.*/{flag=0}flag'| awk '{n=split($0,a,/,/);{for (i=1;i<=n;i++) print a[i]}}' | grep -o EGL.* > /tmp/gpu-viewer/extensions.txt")

        Radio(value)
        Vendor_Combo.set_active(0)

    frame2 = Gtk.Frame(label="Extensions\t")
    grid.attach(frame2, 0, 2, 12, 1)
    grid1 = Gtk.Grid()
    #grid1.set_row_spacing(5)
    grid1.set_border_width(5)
    frame2.add(grid1)

    OpenGLRad = Gtk.RadioButton()
    RadioImg1 = fetchImageFromUrl(Const.OPEN_GL_PNG, 90,70, True)
    OpenGLRad.set_image(Gtk.Image.new_from_pixbuf(RadioImg1))
    OpenGLRad.connect("clicked", radcall, 1)
    grid1.add(OpenGLRad)
    OpenGLRadES = Gtk.RadioButton.new_from_widget(OpenGLRad)
    RadioImg2 = fetchImageFromUrl(Const.OPEN_GL_ES_PNG, 100,70, True)
    OpenGLRadES.set_image(Gtk.Image.new_from_pixbuf(RadioImg2))
    OpenGLRadES.connect("clicked", radcall, 2)
    eglRad = Gtk.RadioButton.new_from_widget(OpenGLRadES)
    eglRad.connect("clicked",radcall, 3)
    RadioImg3 = fetchImageFromUrl(Const.EGL_PNG,70,70,True)
    eglRad.set_image(Gtk.Image.new_from_pixbuf(RadioImg3))
    with open("/tmp/gpu-viewer/OpenGLLHS.txt", "r") as file1:
        for line in file1:
            if "OpenGL ES" in line:
                grid1.attach_next_to(OpenGLRadES, OpenGLRad, Gtk.PositionType.RIGHT, 1, 1)
                continue
            elif "EGL_VERSION" in line:
                grid1.attach_next_to(eglRad,OpenGLRadES,Gtk.PositionType.RIGHT,1,1)
                break
            else:
                OpenGLRadES.set_visible(False)
                eglRad.set_visible(False)

    OpenGLRad.set_active(False)
   # OpenGLRadES.set_active(True)
    # os.system("rm /tmp/gpu-viewer/OpenGL*.txt")
    # End of Frame 2 and grid 1
    # Start of Frame 3

    def searchTree(model,iter,data=None):
        search_query = entry.get_text().lower()
        for i in range(TreeGLExt.get_n_columns()):
            value = model.get_value(iter,i).lower()
            if search_query in value:
                return True

    def switchCall(self, value):
        if switch.get_active():
            os.system(
                "cat /tmp/gpu-viewer/glxinfo.txt | awk '/OpenGL extensions/{flag=1;next}/OpenGL ES profile/{flag=0} flag' | grep GL_ | sort > /tmp/gpu-viewer/extensions.txt")
            os.system(
                "cat /tmp/gpu-viewer/glxinfo.txt  | awk '/client glx extensions/{flag=1; next}/GLX version/{flag=0} flag' | grep GLX_ | sort >> /tmp/gpu-viewer/extensions.txt")
        else:
            os.system(
                "cat /tmp/gpu-viewer/glxinfo.txt | awk '/OpenGL core profile extensions:/{flag=1;next}/OpenGL version*/{flag=0} flag' | grep GL_ | sort > /tmp/gpu-viewer/extensions.txt")
            os.system(
                "cat /tmp/gpu-viewer/glxinfo.txt  | awk '/client glx extensions/{flag=1; next}/GLX version/{flag=0} flag' | grep GLX_ | sort >> /tmp/gpu-viewer/extensions.txt")
        Radio(1)
        Vendor_Combo.set_active(0)

    Vendor_Combo = Gtk.ComboBox.new_with_model(Vendor_Store)
    Vendor_Combo.connect("changed", radcall2)
    Vendor_renderer = Gtk.CellRendererText()
    Vendor_Combo.pack_start(Vendor_renderer, True)
    Vendor_Combo.add_attribute(Vendor_renderer, "text", 0)
   # Vendor_Combo.set_entry_text_column(0)
    Vendor_Combo.set_active(0)
    grid1.attach_next_to(Vendor_Combo, OpenGLRad, Gtk.PositionType.BOTTOM, 1, 1)

    switch = Gtk.Switch()
    switch.connect("notify::active",switchCall)
    switch.set_active(True)

    coreLabel = Gtk.Label("Core")
    comptLabel = Gtk.Label("\t\tCompat.")


    grid1.attach_next_to(coreLabel, Vendor_Combo, Gtk.PositionType.RIGHT, 1, 1)

    grid1.attach_next_to(switch, coreLabel, Gtk.PositionType.RIGHT,1,1)
    grid1.attach_next_to(comptLabel, switch, Gtk.PositionType.RIGHT, 4, 1)
    TreeGLExt.set_enable_search(True)
    TreeGLExt.set_headers_visible(True)
    setColumns(TreeGLExt, Title1, Const.MWIDTH,0.0)

    grid.attach(frame4, 0, 3, 12, 1)
    grid3 = Gtk.Grid()
    #grid3.set_row_spacing(2)
    frame4.add(grid3)
    frameSearch = Gtk.Frame()
    entry = Gtk.SearchEntry()
    entry.set_placeholder_text("Type here to filter extensions.....")
    entry.connect("search-changed",refresh_filter,OpenGLExt_list_filter)
    entry.grab_focus()
    frameSearch.add(entry)
    scrollable_treelist2 = createScrollbar(TreeGLExt)
    grid3.attach(frameSearch,0,0,1,1)
    grid3.attach_next_to(scrollable_treelist2,frameSearch,Gtk.PositionType.BOTTOM, 1, 1)

    OpenGLExt_list_filter.set_visible_func(searchTree)

    tab1.show_all()
