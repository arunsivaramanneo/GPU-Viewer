import os
import gi

BGCOLOR1 = "#fff"
BGCOLOR2 = "#ddd"
from gi.repository import Gtk, GdkPixbuf
from FrameBuffer import FrameBuffer
WH = 60
gi.require_version("Gtk", "3.0")

Title1 = [" ", " "]
LimitsTitle = ["OpenGL Hardware Limits", "Value"]


def OpenGL(tab1):
    grid = Gtk.Grid()
    grid.set_row_spacing(10)
    grid.set_column_spacing(20)
    tab1.add(grid)
    grid4 = Gtk.Grid()
    grid4.set_row_spacing(10)
    frame1 = Gtk.Frame(label="OpenGL_Information", expand=True)
    grid.attach(frame1, 0, 0, 12, 1)
    frame1.add(grid4)
    OpenGLInfo_list = Gtk.ListStore(str, str, str)

    os.system("glxinfo | grep string | grep -v glx > .Temp/OpenGL_Information.txt")
    # os.system("glxinfo | grep string | grep glx >> OpenGL_Information.txt")
    os.system("cat .Temp/OpenGL_Information.txt | grep -o :.* | grep -o ' .*' > .Temp/OpenGLRHS.txt")
    os.system("cat .Temp/OpenGL_Information.txt | awk '{gsub(/string.*/,'True');print}' > .Temp/OpenGLLHS.txt")

    with open(".Temp/OpenGLRHS.txt", "r") as file1:
        value = []
        for line in file1:
            value.append(line)
    i = 0
    with open(".Temp/OpenGLLHS.txt", "r") as file1:
        for line in file1:
            if i % 2 == 0:
                background_color = BGCOLOR1
            else:
                background_color = BGCOLOR2
            OpenGLInfo_list.append([line.strip('\n'), value[i].strip('\n'), background_color])
            i = i + 1

    TreeGL = Gtk.TreeView(OpenGLInfo_list, expand=True)

    for i, column_title in enumerate([" ", " "]):
        renderer = Gtk.CellRendererText(font="Helvetica 11")
        column = Gtk.TreeViewColumn(column_title, renderer, text=i)
        column.add_attribute(renderer, "background", 2)
        TreeGL.append_column(column)

    scrollable_treelist = Gtk.ScrolledWindow()
    scrollable_treelist.set_vexpand(True)
    scrollable_treelist.add(TreeGL)
    grid4.add(scrollable_treelist)

    def clickme(button):

        os.system(
            "glxinfo -l | awk '/OpenGL limits:/{flag=1}/GLX Visuals.*/{flag=0} flag' | awk '/OpenGL limits:/{flag=1;next}/OpenGL ES profile/{flag=0} flag'  > .Temp/OpenGL_Limits.txt")
        os.system("cat .Temp/OpenGL_Limits.txt | awk '{gsub(/=.*/,'True');print}' > .Temp/OpenGLLimitsLHS.txt")
        os.system("cat .Temp/OpenGL_Limits.txt | grep -o =.* | grep -o ' .*' > .Temp/OpenGLLimitsRHS.txt")
        LimitsWin = Gtk.Window()
        LimitsWin.set_title("OpenGL Hardware Limits")
        LimitsWin.set_size_request(1000, 500)
        LimitsWin.set_border_width(20)
        LimitsFrame = Gtk.Frame()
        LimitsWin.add(LimitsFrame)
        Limits_Store = Gtk.ListStore(str, str, str)
        TreeLimits = Gtk.TreeView(Limits_Store, expand=True)

        temp = []
        LimitsRHS = []

        with open(".Temp/OpenGLLimitsRHS.txt", "r") as file1:
            for line in file1:
                temp.append(line)

        i = 0
        with open(".Temp/OpenGL_Limits.txt", "r") as file1:
            for line in file1:
                if "= " in line:
                    LimitsRHS.append(temp[i])
                    i = i + 1
                else:
                    LimitsRHS.append(" ")

        i = 0
        with open(".Temp/OpenGLLimitsLHS.txt", "r") as file1:
            for line in file1:
                if i % 2 == 0:
                    background_color = BGCOLOR1
                else:
                    background_color = BGCOLOR2
                Limits_Store.append([line.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                i = i + 1

        for i, column_title in enumerate(LimitsTitle):
            Limitsrenderer = Gtk.CellRendererText(font="Helvetica 11")
            column = Gtk.TreeViewColumn(column_title, Limitsrenderer, text=i)
            column.add_attribute(Limitsrenderer, "background", 2)
            TreeLimits.append_column(column)

        LimitsScrollbar = Gtk.ScrolledWindow()
        LimitsScrollbar.set_vexpand(True)
        LimitsScrollbar.add(TreeLimits)
        LimitsFrame.add(LimitsScrollbar)

        os.system("rm .Temp/OpenGL*.txt")
        LimitsWin.show_all()

    LimitsFrame = Gtk.Frame()
    grid.attach(LimitsFrame, 0, 1, 2, 1)
    Button_Limits = Gtk.Button.new_with_label("Show OpenGL Limits")
    Button_Limits.connect("clicked", clickme)
    LimitsFrame.add(Button_Limits)
    # grid4.attach(Button_Limits, 0, 1, 2, 1)

    #vendorFrame = Gtk.Frame()
    #grid.attach_next_to(vendorFrame,LimitsFrame,Gtk.PositionType.RIGHT,1,1)

    FBFrame = Gtk.Frame()
    Button_FB = Gtk.Button.new_with_label("Show GLX Frame Buffer Configuration")
    Button_FB.connect("clicked", FrameBuffer)
    FBFrame.add(Button_FB)

    with open(".Temp/OpenGLRHS.txt","r") as file1:
        for line in file1:
            if "Intel" in line :
                vendorImg = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename="../Images/intel-logo.png", width=WH, height=WH,
                                                                    preserve_aspect_ratio=True)
                grid.attach_next_to(Gtk.Image.new_from_pixbuf(vendorImg),LimitsFrame,Gtk.PositionType.RIGHT,1,1)
                break
            elif "NVIDIA" in line:
                vendorImg = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename="../Images/nvidia-logo.png", width=WH, height=WH,
                                                                    preserve_aspect_ratio=True)
                grid.attach_next_to(Gtk.Image.new_from_pixbuf(vendorImg),LimitsFrame,Gtk.PositionType.RIGHT,1,1)
                break
            elif "AMD" in  line or "ATI" in line:
                vendorImg = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename="../Images/AMD.png", width=WH, height=WH,
                                                                    preserve_aspect_ratio=True)
                grid.attach_next_to(Gtk.Image.new_from_pixbuf(vendorImg),LimitsFrame,Gtk.PositionType.RIGHT,1,1)
                break

        #vendorFrame.add(Gtk.Image.new_from_pixbuf(vendorImg))
        grid.attach(FBFrame,3,1,2,1)

    # End of Frame 1
    OpenGLExt_list = Gtk.ListStore(str, str)
    TreeGLExt = Gtk.TreeView(OpenGLExt_list, expand=True)
    frame4 = Gtk.Frame(label=" ")

    def radcall2(button):
        value = button.get_active()

        GL_All = []
        List = []

        with open(".Temp/Vendor1.txt", "r") as file1:
            for line in file1:
                List.append(line)

        List = [i.strip(' ') for i in List]
        List = [i.strip('\n ') for i in List]
        List.insert(0, " ALL")

        with open(".Temp/extensions.txt", "r") as file1:
            for line in file1:
                if List[int(value)] == " ALL":
                    GL_All.append(line)
                elif List[int(value)] != " ALL":
                    if "_%s_" % List[int(value)] in line:
                        GL_All.append(line)

        OpenGLExt_list.clear()
        TreeGLExt.set_model(OpenGLExt_list)

        for i in range(len(List)):
            if int(value) == i:
                frame4.set_label(List[i])


        count = len(GL_All)
        for i in range(count):
            if i % 2 == 0:
                background_color = BGCOLOR1
            else:
                background_color = BGCOLOR2
            text = GL_All[i].strip(' ')
            OpenGLExt_list.append([text.strip('\n'), background_color])

    VendorExt_list = Gtk.ListStore(str, bool, str)
    TreeVendor = Gtk.TreeView(VendorExt_list, expand=True)

    Vendor_Store = Gtk.ListStore(str)
    Vendor_Combo = Gtk.ComboBox.new_with_model(Vendor_Store)

    def Radio(value):

        os.system("cat .Temp/extensions.txt | awk 'gsub(/GL_|_.*/,'true')'| uniq > .Temp/Vendor.txt")
        os.system("cat .Temp/extensions.txt | awk 'gsub(/GLX_|_.*/,'true')'| uniq >> .Temp/Vendor.txt")
        os.system("cat .Temp/Vendor.txt | sort | uniq | grep -v GLX | grep -v GL  > .Temp/Vendor1.txt")

        vCount = []
        vendorList = []
        with open(".Temp/Vendor1.txt", "r") as file1:
            for line in file1:
                vendorList.append(line)

        vendorList = [i.strip(' ') for i in vendorList]
        vendorList = [i.strip('\n ') for i in vendorList]
        vendorList.insert(0, "Total")

        with open(".Temp/extensions.txt", "r") as file1:
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
            if i % 2 == 0:
                background_color = BGCOLOR1
            else:
                background_color = BGCOLOR2
            VendorExt_list.append([NewList[i], Toggle[i], background_color])
            Vendor_Store.append([NewList[i]])

    def radcall(button, value):
        if value == 1:
            os.system(
                "glxinfo -s | awk '/OpenGL extensions/{flag=1;next}/OpenGL ES profile/{flag=0} flag' | grep GL_ | sort > .Temp/extensions.txt")
            os.system(
                "glxinfo -s | awk '/client glx extensions/{flag=1; next}/GLX version/{flag=0} flag' | grep GLX_ | sort >> .Temp/extensions.txt")

        elif value == 2:
            os.system(
                "glxinfo -s | awk '/OpenGL ES profile/{flag=1;next}/80 GLX Visuals/{flag=0} flag' | grep GL_ | sort > .Temp/extensions.txt")

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
    with open(".Temp/OpenGLLHS.txt", "r") as file1:
        for line in file1:
            if "OpenGL ES" in line:
                grid1.attach_next_to(OpenGLRadES, OpenGLRad, Gtk.PositionType.RIGHT, 1, 1)
                break
            else:
                OpenGLRadES.set_visible(False)

    OpenGLRad.set_active(False)
    #os.system("rm .Temp/OpenGL*.txt")
    # End of Frame 2 and grid 1
    # Start of Frame 3

    Vendor_Combo = Gtk.ComboBox.new_with_model(Vendor_Store)
    Vendor_Combo.connect("changed", radcall2)
    Vendor_renderer = Gtk.CellRendererText(font="Helvetica 10")
    Vendor_Combo.pack_start(Vendor_renderer, True)
    Vendor_Combo.add_attribute(Vendor_renderer, "text", 0)
    Vendor_Combo.set_entry_text_column(0)
    Vendor_Combo.set_active(0)

    grid1.attach_next_to(Vendor_Combo, OpenGLRad, Gtk.PositionType.BOTTOM, 5, 1)

    for i, column_title in enumerate([" "]):
        renderer = Gtk.CellRendererText(font="Helvetica 11")
        column = Gtk.TreeViewColumn(column_title, renderer, text=i)
        column.add_attribute(renderer, "background", 1)
        TreeGLExt.append_column(column)

    grid.attach(frame4, 0, 3, 12, 1)
    grid3 = Gtk.Grid()
    frame4.add(grid3)
    scrollable_treelist2 = Gtk.ScrolledWindow()
    scrollable_treelist2.set_vexpand(True)
    scrollable_treelist2.add(TreeGLExt)
    grid3.attach(scrollable_treelist2, 0, 0, 1, 1)

    tab1.show_all()
