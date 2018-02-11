import os
import gi
import Const

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from FrameBuffer import FrameBuffer
from Common import setScreenSize, fetchImageFromUrl, copyContentsFromFile, setBackgroundColor, setColumns, \
    createScrollbar, refresh_filter

WH = 70

Title1 = [" "]
Title2 = ["OpenGL Information ", " Details"]
LimitsTitle = ["OpenGL Hardware Limits", "Value"]


def OpenGL(tab1):
    grid = Gtk.Grid()
    grid.set_row_spacing(10)
    grid.set_column_spacing(20)
    tab1.add(grid)
    grid4 = Gtk.Grid()
#    grid4.set_row_spacing(5)
    frame1 = Gtk.Frame(label="", expand=True)
    grid.attach(frame1, 0, 0, 12, 1)
    frame1.add(grid4)
    OpenGLInfo_list = Gtk.ListStore(str, str, str)
    os.system("glxinfo -s > /tmp/glxinfo.txt")
    os.system("cat /tmp/glxinfo.txt | grep string | grep -v glx > /tmp/OpenGL_Information.txt")
    os.system("cat /tmp/OpenGL_Information.txt | grep -o :.* | grep -o ' .*' > /tmp/OpenGLRHS.txt")
    os.system("cat /tmp/OpenGL_Information.txt | awk '{gsub(/string.*/,'True');print}' > /tmp/OpenGLLHS.txt")

    value = copyContentsFromFile("/tmp/OpenGLRHS.txt")

    with open("/tmp/OpenGLLHS.txt", "r") as file1:
        for i,line in enumerate(file1):
            background_color = setBackgroundColor(i)
            OpenGLInfo_list.append([line.strip('\n'), value[i].strip('\n'), background_color])


    TreeGL = Gtk.TreeView(OpenGLInfo_list, expand=True)
    # TreeGL.set_enable_search(True)
    setColumns(TreeGL, Title2, Const.MWIDTH,0.0)

    scrollable_treelist = createScrollbar(TreeGL)
    grid4.add(scrollable_treelist)

    def clickme(button):

        button.set_sensitive(False)
        os.system(
            "glxinfo -l | awk '/OpenGL limits:/{flag=1}/GLX Visuals.*/{flag=0} flag' | awk '/OpenGL limits:/{flag=1;next}/OpenGL ES profile/{flag=0} flag' | awk '/./'  > /tmp/OpenGL_Limits.txt")
        os.system("cat /tmp/OpenGL_Limits.txt | awk '{gsub(/=.*/,'True');print}' > /tmp/OpenGLLimitsLHS.txt")
        os.system("cat /tmp/OpenGL_Limits.txt | grep -o =.* | grep -o ' .*' > /tmp/OpenGLLimitsRHS.txt")
        LimitsWin = Gtk.Window()
        LimitsWin.set_title("OpenGL Hardware Limits")
        #    LimitsWin.set_size_request(1000, 500)
        setScreenSize(LimitsWin, Const.WIDTH_RATIO, Const.HEIGHT_RATIO2)
        LimitsWin.set_border_width(10)
        LimitsFrame = Gtk.Frame()
        LimitsWin.add(LimitsFrame)
        Limits_Store = Gtk.TreeStore(str, str, str)
        TreeLimits = Gtk.TreeView(Limits_Store, expand=True)
        TreeLimits.set_property("enable-tree-lines",True)

        LimitsRHS = []
        LimitRHSValue = []
        temp = copyContentsFromFile("/tmp/OpenGLLimitsRHS.txt")

        i = 0
        with open("/tmp/OpenGL_Limits.txt", "r") as file1:
            for line in file1:
                if "= " in line:
                    LimitsRHS.append(temp[i])
                    LimitRHSValue.append(True)
                    i = i + 1
                else:
                    LimitsRHS.append("")
                    LimitRHSValue.append(False)

        k = 0;count=0
        with open("/tmp/OpenGLLimitsLHS.txt", "r") as file1:
            for i,line in enumerate(file1):
                background_color = setBackgroundColor(i)
                TreeLimits.expand_all()
                text = line.strip(' ')
                if "TEXTURE_FORMATS" in line and LimitRHSValue[i] == True:
                    iter2 = Limits_Store.append(None,[text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                elif ":" not in line and LimitRHSValue[i] == False:
                    Limits_Store.append(iter2,[text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                    k += 1
                else:
                    if ":" in line:
                        count += 1
                        iter2 = Limits_Store.append(None,[text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                        continue
                    if count > 0 :
                        Limits_Store.append(iter2,[text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                    else:
                        Limits_Store.append(None,[text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])

        setColumns(TreeLimits, LimitsTitle, Const.MWIDTH,0.0)
        LimitsScrollbar = createScrollbar(TreeLimits)
        LimitsFrame.add(LimitsScrollbar)

        def button_enable(win,value):
            button.set_sensitive(True)
        LimitsWin.connect("delete-event",button_enable)

        LimitsWin.show_all()

    LimitsFrame = Gtk.Frame()
    grid.attach(LimitsFrame, 0, 1, 2, 1)
    Button_Limits = Gtk.Button("Show OpenGL Limits")
    Button_Limits.connect("clicked", clickme)
    LimitsFrame.add(Button_Limits)
    # grid4.attach(Button_Limits, 0, 1, 2, 1)

    # vendorFrame = Gtk.Frame()
    # grid.attach_next_to(vendorFrame,LimitsFrame,Gtk.PositionType.RIGHT,1,1)

    FBFrame = Gtk.Frame()
    Button_FB = Gtk.Button.new_with_label("Show GLX Frame Buffer Configuration")
    Button_FB.connect("clicked", FrameBuffer)
    FBFrame.add(Button_FB)

    with open("/tmp/OpenGLRHS.txt", "r") as file1:
        for line in file1:
            if "Intel" in line:
                vendorImg = fetchImageFromUrl(Const.INTEL_LOGO_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
                grid.attach_next_to(Gtk.Image.new_from_pixbuf(vendorImg), LimitsFrame, Gtk.PositionType.RIGHT, 1, 1)
                break
            elif "NVIDIA" in line:
                vendorImg = fetchImageFromUrl(Const.NVIDIA_LOGO_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
                grid.attach_next_to(Gtk.Image.new_from_pixbuf(vendorImg), LimitsFrame, Gtk.PositionType.RIGHT, 1, 1)
                break
            elif "AMD" in line or "ATI" in line:
                vendorImg = fetchImageFromUrl(Const.AMD_LOGO_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
                grid.attach_next_to(Gtk.Image.new_from_pixbuf(vendorImg), LimitsFrame, Gtk.PositionType.RIGHT, 1, 1)
                break

        # vendorFrame.add(Gtk.Image.new_from_pixbuf(vendorImg))
        grid.attach(FBFrame, 3, 1, 2, 1)

    # End of Frame 1
    OpenGLExt_list = Gtk.ListStore(str, str)
    OpenGLExt_list_filter = OpenGLExt_list.filter_new()
    TreeGLExt = Gtk.TreeView(OpenGLExt_list_filter, expand=True)
    TreeGLExt.set_headers_visible(False)
    frame4 = Gtk.Frame(label=" ")

    def radcall2(button):
        value = button.get_active()

        GL_All = []

        List = copyContentsFromFile("/tmp/Vendor1.txt")

        List = [i.strip(' ') for i in List]
        List = [i.strip('\n ') for i in List]
        List.insert(0, " ALL")

        with open("/tmp/extensions.txt", "r") as file1:
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

        os.system("cat /tmp/extensions.txt | awk 'gsub(/GL_|_.*/,'true')'| uniq > /tmp/Vendor.txt")
        os.system("cat /tmp/extensions.txt | awk 'gsub(/GLX_|_.*/,'true')'| uniq >> /tmp/Vendor.txt")
        os.system("cat /tmp/Vendor.txt | sort | uniq | grep -v GLX | grep -v GL$  > /tmp/Vendor1.txt")

        vCount = []
        vendorList = []
        with open("/tmp/Vendor1.txt", "r") as file1:
            for line in file1:
                vendorList.append(line)

        vendorList = [i.strip(' ') for i in vendorList]
        vendorList = [i.strip('\n ') for i in vendorList]
        vendorList.insert(0, "Total")

        with open("/tmp/extensions.txt", "r") as file1:
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
            os.system(
                "cat /tmp/glxinfo.txt | awk '/OpenGL extensions/{flag=1;next}/OpenGL ES profile/{flag=0} flag' | grep GL_ | sort > /tmp/extensions.txt")
            os.system(
                "cat /tmp/glxinfo.txt  | awk '/client glx extensions/{flag=1; next}/GLX version/{flag=0} flag' | grep GLX_ | sort >> /tmp/extensions.txt")

        elif value == 2:
            os.system(
                "cat /tmp/glxinfo.txt  | awk '/OpenGL ES profile/{flag=1;next}/80 GLX Visuals/{flag=0} flag' | grep GL_ | sort > /tmp/extensions.txt")

        Radio(value)
        Vendor_Combo.set_active(0)

    frame2 = Gtk.Frame(label="Extensions")
    grid.attach(frame2, 0, 2, 12, 1)
    grid1 = Gtk.Grid()
    grid1.set_row_spacing(5)
    grid1.set_border_width(5)
    frame2.add(grid1)

    OpenGLRad = Gtk.RadioButton("OpenGL")
    OpenGLRad.connect("clicked", radcall, 1)
    grid1.add(OpenGLRad)
    OpenGLRadES = Gtk.RadioButton.new_with_label_from_widget(OpenGLRad, "OpenGL ES")
    OpenGLRadES.connect("clicked", radcall, 2)
    with open("/tmp/OpenGLLHS.txt", "r") as file1:
        for line in file1:
            if "OpenGL ES" in line:
                grid1.attach_next_to(OpenGLRadES, OpenGLRad, Gtk.PositionType.RIGHT, 1, 1)
                break
            else:
                OpenGLRadES.set_visible(False)

    OpenGLRad.set_active(False)
    # os.system("rm /tmp/OpenGL*.txt")
    # End of Frame 2 and grid 1
    # Start of Frame 3

    def searchTree(model,iter,data=None):
        search_query = entry.get_text().lower()
        for i in range(TreeGLExt.get_n_columns()):
            value = model.get_value(iter,i).lower()
            if search_query in value:
                return True


    Vendor_Combo = Gtk.ComboBox.new_with_model(Vendor_Store)
    Vendor_Combo.connect("changed", radcall2)
    Vendor_renderer = Gtk.CellRendererText()
    Vendor_Combo.pack_start(Vendor_renderer, True)
    Vendor_Combo.add_attribute(Vendor_renderer, "text", 0)
   # Vendor_Combo.set_entry_text_column(0)
    Vendor_Combo.set_active(0)

    grid1.attach_next_to(Vendor_Combo, OpenGLRad, Gtk.PositionType.BOTTOM, 5, 1)
    TreeGLExt.set_enable_search(True)
    TreeGLExt.set_headers_visible(True)
    setColumns(TreeGLExt, Title1, Const.MWIDTH,0.0)

    grid.attach(frame4, 0, 3, 12, 1)
    grid3 = Gtk.Grid()
    grid3.set_row_spacing(2)
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
