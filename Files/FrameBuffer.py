import gi
import os
BGCOLOR1 ="#fff"
BGCOLOR2 = "#ddd"
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

FrameBufferList = ["vid","vdep", "vt", "xsp", "bfsz", "lvl", "rt", "db", "stereo", "rsz", "gsz", "bsz", "asz", "flt", "srgb", "aux", "depth", "stcl",
                   "acr", "acg", "acb", "aca", "msnum", "msbufs","caveats"]

def FrameBuffer(button):

    def GLXFB(button, value):
        FB_Store.clear()
        TreeFB.set_model(FB_Store)
        if value == 1:
            os.system(
                "glxinfo | awk '/GLX Visuals.*/{flag=1;next}/GLXFBConfigs.*/{flag=0}flag' | awk '/----.*/{flag=1;next}flag' > /tmp/FrameBufferGLXVisual.txt")

            list = []
            with open("/tmp/FrameBufferGLXVisual.txt", "r") as file1:
                for line in file1:
                    list.append(line.split())

            for i in range(len(list)-1):
                if i % 2 == 0:
                    background_color = BGCOLOR1
                else:
                    background_color = BGCOLOR2
                FB_Store.append(list[i]+[background_color])
            label = "%d GLX Visuals"%(len(list)-1)
            button.set_label(label)

        if value == 2:

            os.system(
                "glxinfo | awk '/GLXFBConfigs.*/{flag=1;next}flag' | awk '/----.*/{flag=1;next}flag' > /tmp/FrameBufferGLXFBconfigs.txt")

            list = []
            with open("/tmp/FrameBufferGLXFBconfigs.txt", "r") as file1:
                for line in file1:
                    list.append(line.split())

            for i in range(len(list)-1):
                if i % 2 == 0:
                    background_color = BGCOLOR1
                else:
                    background_color = BGCOLOR2
                if list[i][6] == "r" or list[i][6] == "c":
                    pass
                else:
                    list[i].insert(6," ")
                FB_Store.append(list[i]+[background_color])
            label = "%d  GLXFBConfigs"%(len(list)-1)
            button.set_label(label)

    FBWin = Gtk.Window()
    FBWin.set_title("GLX Frame Buffer Configuration")
    FBWin.set_size_request(1050, 500)
    FBGrid = Gtk.Grid()
    FBWin.add(FBGrid)
    FBGrid.set_border_width(20)
    FBGrid.set_row_spacing(30)
    FBGLXButton = Gtk.RadioButton("GLX Visuals")
    FBGLXButton.connect("toggled", GLXFB, 1)
    FBGrid.add(FBGLXButton)
    FBConfigButton = Gtk.RadioButton.new_from_widget(FBGLXButton)
    FBConfigButton.set_label("GLXFBConfigs")
    FBConfigButton.connect("toggled",GLXFB,2)
    FBGrid.attach_next_to(FBConfigButton, FBGLXButton, Gtk.PositionType.RIGHT, 1, 1)
    FBFrame = Gtk.Frame()

    FB_Store = Gtk.ListStore(str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str,str)
    TreeFB = Gtk.TreeView(FB_Store, expand=True)
    TreeFB.set_property("enable-grid-lines",3)

    FBConfigButton.set_active(True)
    FBGLXButton.set_active(True)

    for i, column_title in enumerate(FrameBufferList):
        FBrenderer = Gtk.CellRendererText(font="Helvetica 11")
        column = Gtk.TreeViewColumn(column_title, FBrenderer, text=i)
        column.add_attribute(FBrenderer,"background",25)
        if i < len(FrameBufferList) - 1:
            FBrenderer.set_alignment(0.5, 0.5)
            column.set_alignment(0.5)
        column.set_property("min-width", 35)
        TreeFB.append_column(column)

    FBScrollbar = Gtk.ScrolledWindow()
    FBScrollbar.set_vexpand(True)
    FBScrollbar.add(TreeFB)
    FBFrame.add(FBScrollbar)
    FBGrid.attach_next_to(FBFrame, FBGLXButton, Gtk.PositionType.BOTTOM, 25, 1)

    FBWin.show_all()

    #Gtk.main()
