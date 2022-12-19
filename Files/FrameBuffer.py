import gi
import const
import Filenames
import subprocess

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from Common import  setBackgroundColor, create_scrollbar, createSubTab, setColumnFrameBuffer,getScreenSize

FrameBufferToolTip = ["Visual ID", "Visual Depth", "Visual Type", "Transparency", "Buffer Size", "level", "Render Type",
                      "Double Buffer", "Stereo", "Red Colorbuffer Size", "Green Colorbuffer Size",
                      "Blue Colorbuffer Size", "Alpha Colorbuffer Size"
                                               "float", "SRGB", "Auxillary Buffer", "Depth", "Stencil",
                      "Accumbuffer Red", "Accumbuffer Green", "Accumbuffer Blue", "Accumbuffer Alpha", "msnum",
                      "msbufs", "Swap", "Caveats"]


def FrameBuffer(button):
    FBWin = Gtk.Window()
    FBWin.set_title("GLX Frame Buffer Configuration")
    #   FBWin.set_size_request(1000, 500)
 #   setScreenSize(FBWin, const.WIDTH_RATIO, const.HEIGHT_RATIO2)

    FBNotebook = Gtk.Notebook()
    FBWin.set_child(FBNotebook)

    FBGLX_Store = Gtk.ListStore(str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str,
                                str,
                                str, str, str, str, str, str, str, str, str)
    TreeFBGLX = Gtk.TreeView.new_with_model(FBGLX_Store)
    TreeFBGLX.set_enable_search(True)
    TreeFBGLX.set_property("enable-grid-lines", 3)

    FBGLXTab = Gtk.Box(spacing=10)
    FBGLXGrid = createSubTab(FBGLXTab, FBNotebook, "GLX Visuals")
    FBConfigTab = Gtk.Box(spacing=10)
    FBConfigGrid = createSubTab(FBConfigTab, FBNotebook, "GLX FBConfigs")

    button.set_sensitive(False)

    fetch_framebuffer_glx_visual_command = "cat %s  | awk '/GLX Visuals.*/{flag=1;next}/GLXFBConfigs.*/{flag=0}flag' | awk '/----.*/{flag=1;next}flag' " %(Filenames.opengl_outpuf_file)

    fetch_framebuffer_glx_visual_process = subprocess.Popen(fetch_framebuffer_glx_visual_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    list_glx_visuals= fetch_framebuffer_glx_visual_process.communicate()[0].splitlines()

    list_glx_visuals = [i.split() for i in list_glx_visuals]

    for i in range(len(list_glx_visuals) - 1):
        background_color = setBackgroundColor(i)
        FBGLX_Store.append(list_glx_visuals[i] + [background_color])
    label1 = "%d GLX Visuals" % (len(list_glx_visuals) - 1)
    FBNotebook.set_tab_label(FBGLXTab, Gtk.Label(label=label1))

    FBConfig_Store = Gtk.ListStore(str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str,
                                   str,
                                   str, str, str, str, str, str, str, str, str)
    TreeFBConfig = Gtk.TreeView.new_with_model(FBConfig_Store)
    TreeFBConfig.set_enable_search(True)
    TreeFBConfig.set_property("enable-grid-lines", 3)

    fetch_framebuffer_glx_fbconfigs_command = "cat %s | awk '/GLXFBConfigs.*/{flag=1;next}flag' | awk '/----.*/{flag=1;next}flag' " %(Filenames.opengl_outpuf_file)

    fetch_framebuffer_glx_fbconfigs_process= subprocess.Popen(fetch_framebuffer_glx_fbconfigs_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    list_fb_configs = fetch_framebuffer_glx_fbconfigs_process.communicate()[0].splitlines()
    
    list_fb_configs = [i.split() for i in list_fb_configs]    

    for i in range(len(list_fb_configs) - 1):
        background_color = setBackgroundColor(i)
        if list_fb_configs[i][6] == "r" or list_fb_configs[i][6] == "c":
            pass
        else:
            list_fb_configs[i].insert(6, ".")
        FBConfig_Store.append(list_fb_configs[i] + [background_color])
    label2 = "%d  GLX FBConfigs" % (len(list_fb_configs) - 1)
    FBNotebook.set_tab_label(FBConfigTab, Gtk.Label(label=label2))

    setColumnFrameBuffer(TreeFBGLX, const.FRAMEBUFFERLIST)

    FBGLXScrollbar = create_scrollbar(TreeFBGLX)
    FBGLXGrid.attach(FBGLXScrollbar,0,0,1,1)

    setColumnFrameBuffer(TreeFBConfig, const.FRAMEBUFFERLIST)

    FBConfigScrollbar = create_scrollbar(TreeFBConfig)
    FBConfigGrid.attach(FBConfigScrollbar,0,0,1,1)

    def button_enable(win):
        button.set_sensitive(True)

    FBWin.connect("close-request", button_enable)
    screen_width,screen_height = getScreenSize()
    FBWin.set_size_request(int(screen_width) * const.WIDTH_RATIO2 ,540)
    FBWin.present()

    # Gtk.main()
