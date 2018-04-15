import gi
import os
import Const

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from Common import setScreenSize, setBackgroundColor, createScrollbar, createSubTab, setColumnFrameBuffer


FrameBufferToolTip = ["Visual ID","Visual Depth","Visual Type","Transparency","Buffer Size","level","Render Type","Double Buffer","Stereo","Red Colorbuffer Size","Green Colorbuffer Size","Blue Colorbuffer Size","Alpha Colorbuffer Size"
                      "float","SRGB","Auxillary Buffer","Depth","Stencil","Accumbuffer Red","Accumbuffer Green","Accumbuffer Blue","Accumbuffer Alpha","msnum","msbufs","Caveats"]

def FrameBuffer(button):

    FBWin = Gtk.Window()
    FBWin.set_border_width(10)
    FBWin.set_title("GLX Frame Buffer Configuration")
    #   FBWin.set_size_request(1000, 500)
    setScreenSize(FBWin, Const.WIDTH_RATIO, Const.HEIGHT_RATIO2)

    FBNotebook = Gtk.Notebook()
    FBWin.add(FBNotebook)

    FBGLX_Store = Gtk.ListStore(str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str,
                             str, str, str, str, str, str, str, str)
    TreeFBGLX = Gtk.TreeView(FBGLX_Store, expand=True)
    TreeFBGLX.set_enable_search(True)
    TreeFBGLX.set_property("enable-grid-lines", 3)

    FBGLXTab = Gtk.Box(spacing=10)
    FBGLXGrid = createSubTab(FBGLXTab,FBNotebook,"GLX Visuals")
    FBConfigTab = Gtk.Box(spacing=10)
    FBConfigGrid = createSubTab(FBConfigTab,FBNotebook,"GLX FBConfigs")

    button.set_sensitive(False)

    os.system(
        "cat /tmp/glxinfo.txt  | awk '/GLX Visuals.*/{flag=1;next}/GLXFBConfigs.*/{flag=0}flag' | awk '/----.*/{flag=1;next}flag' > /tmp/FrameBufferGLXVisual.txt")

    list = []
    with open("/tmp/FrameBufferGLXVisual.txt", "r") as file1:
        for line in file1:
            list.append(line.split())

    for i in range(len(list) - 1):
        background_color = setBackgroundColor(i)
        FBGLX_Store.append(list[i] + [background_color])
    label1 = "%d GLX Visuals" % (len(list) - 1)
    FBNotebook.set_tab_label(FBGLXTab,Gtk.Label(label1))

    FBConfig_Store = Gtk.ListStore(str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str,
                                str, str, str, str, str, str, str, str)
    TreeFBConfig = Gtk.TreeView(FBConfig_Store, expand=True)
    TreeFBConfig.set_enable_search(True)
    TreeFBConfig.set_property("enable-grid-lines", 3)

    os.system(
        "cat /tmp/glxinfo.txt | awk '/GLXFBConfigs.*/{flag=1;next}flag' | awk '/----.*/{flag=1;next}flag' > /tmp/FrameBufferGLXFBconfigs.txt")

    list = []
    with open("/tmp/FrameBufferGLXFBconfigs.txt", "r") as file1:
        for line in file1:
            list.append(line.split())

    for i in range(len(list) - 1):
        background_color = setBackgroundColor(i)
        if list[i][6] == "r" or list[i][6] == "c":
            pass
        else:
            list[i].insert(6, ".")
        FBConfig_Store.append(list[i] + [background_color])
    label2 = "%d  GLX FBConfigs" % (len(list) - 1)
    FBNotebook.set_tab_label(FBConfigTab,Gtk.Label(label2))



    setColumnFrameBuffer(TreeFBGLX,Const.FRAMEBUFFERLIST)

    FBGLXScrollbar = createScrollbar(TreeFBGLX)
    FBGLXGrid.add(FBGLXScrollbar)

    setColumnFrameBuffer(TreeFBConfig,Const.FRAMEBUFFERLIST)

    FBConfigScrollbar = createScrollbar(TreeFBConfig)
    FBConfigGrid.add(FBConfigScrollbar)

    def button_enable(win,value):
        button.set_sensitive(True)
    FBWin.connect("delete-event",button_enable)

    FBWin.show_all()

    # Gtk.main()
