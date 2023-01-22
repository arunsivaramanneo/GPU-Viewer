import sys
import gi
import const
import subprocess
import Filenames
from pathlib import Path
gi.require_version('Gtk','4.0')
from gi.repository import Gtk,GdkPixbuf,Gdk


class MyGtk(Gtk.Window):
    def __init__(self, title):
        super(MyGtk, self).__init__(title=title)
        setting = Gtk.Settings.get_default()
        # Setting Theme
   #     if Path(Filenames.Materia_gtk_theme_folder).exists(): 
   #         setting.set_property("gtk-theme-name", "Materia-dark")
   #     elif Path(Filenames.Orchis_gtk_theme_folder).exists():
   #         setting.set_property("gtk-theme-name","Orchis-Compact")
   #     else:
   #         setting.set_property("gtk-theme-name","Adwaita")

        #Setting Font
    #    if Path(Filenames.Roboto_font_folder).exists():
    #        setting.set_property("gtk-font-name","Roboto-Black 12")
    #        setting.set_property("gtk-hint-font-metrics",True)

def create_tab(notebook,icon_url,icon_width,icon_height,aspect_ratio):
    tab = Gtk.Box(orientation=1,spacing=10)
    tab_icon = fetchImageFromUrl(icon_url,icon_width,icon_height,aspect_ratio)
    notebook.append_page(tab,Gtk.Picture.new_for_pixbuf(tab_icon))
    return tab

#getting Ram Details in GB

def setMargin(widget,start,top,bottom):
    widget.set_margin_start(start)
    widget.set_margin_top(top)
    widget.set_margin_bottom(bottom)

def getRamInGb(ram):
    ram1 = ram.split()
    return str("%.2f" %(float(ram1[0])/(1024*1024))) + " GB"

# Setting the Minimum Screen Size
def getScreenSize():
    display = Gdk.Display.get_default()
    monitors = display.get_monitors()
    for m in monitors:
        g = m.get_geometry()
    return g.width,g.height


# fetching the Images/Logos from the const File
def fetchImageFromUrl(imgUrl, iconWidth, iconHeight, aspectRatio):
    return GdkPixbuf.Pixbuf.new_from_file_at_scale(
        filename=imgUrl, width=iconWidth, height=iconHeight, preserve_aspect_ratio=aspectRatio)

# Copy the Contents of the file from a File to a List
def copyContentsFromFile(fileName):
    with open(fileName, "r") as file1:
        value = []
        for line in file1:
            value.append(line)
    return value

def fetchContentsFromCommand(command):
    process = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    return process.communicate()[0].splitlines()

def createMainFile(filename,command):
    with open(filename,"w") as file:
        process = subprocess.Popen(command,shell=True,stdout=file,universal_newlines=True)
        process.communicate()

# Setting the background color for rows
def setBackgroundColor(i):
    if i % 2 == 0:
        background_color = const.BGCOLOR1
    else:
        background_color = const.BGCOLOR2
    return background_color


# setting up Sub Tabs in Vulkan

def createSubTab(Tab, notebook, label):
 #   Tab.set_border_width(10)
    notebook.append_page(Tab, Gtk.Label(label=label))
    Frame = Gtk.Frame()
    Tab.append(Frame)
    Grid = Gtk.Grid()
    Frame.set_child(Grid)
    return Grid


# Setting Columns in TreeView
def setColumns(Treeview, Title, MWIDTH, align):
    for i, column_title in enumerate(Title):
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(column_title, renderer, text=i)
        column.set_alignment(align)
        column.add_attribute(renderer, "background", len(Title))
        column.set_property("min-width", MWIDTH)
        Treeview.set_property("can-focus", False)
        Treeview.append_column(column)


# adding Scrollbar to the Treeview

def create_scrollbar(widget):
    scrollbar = Gtk.ScrolledWindow()
    scrollbar.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
    scrollbar.set_vexpand(True)
    scrollbar.set_hexpand(True)
    scrollbar.set_visible(True)
    scrollbar.set_child(widget)
    return scrollbar


# creating subFrame in Vulkan Tab

def createSubFrame(Tab):
    Frame = Gtk.Frame()
    Tab.add(Frame)
    grid = Gtk.Grid()
    Frame.add(grid)
    return grid


def colorTrueFalse(filename, text):
    with open(filename, "r") as file1:
        value = []
        fgColor = []
        for line in file1:
            if text in line:
                value.append("true")
                fgColor.append(const.COLOR1)
            else:
                value.append("false")
                fgColor.append(const.COLOR2)
    return fgColor, value

def getFormatValue(filename,Format):
    loop = 0
    value = []
    fgColor = []
    with open(filename,"r") as file:
        for line in file:
            for i,f in enumerate(Format):
                if "FEATURE" in line and i >= loop:
                    value.append("true")
                    fgColor.append(const.COLOR1)
                    loop = loop + 1
                    if ":" in f:
                        break
                if "None" in line and i >= loop:
                    value.append("false")
                    fgColor.append(const.COLOR2)
                    loop = loop + 1
                    if ":" in f:
                        break
    return fgColor, value


def getLinkButtonImg(img, link, toolTip):
    Logbutton = Gtk.LinkButton.new_with_label(link)
    Logbutton.set_child(Gtk.Picture.new_for_pixbuf(img))
    Logbutton.set_tooltip_text(toolTip)
    return Logbutton


def getVulkanVersion(value):
    majorVersion = int(value) >> 22
    minorVersion = int(value) >> 12 & 1023
    patchVersion = int(value) & 4095
    return "%d.%d.%d" % (majorVersion, minorVersion, patchVersion)


def getDriverVersion(value,i):
    if '4318' in value:
        majorVersion = (int(value[i]) >> 22) & 1023
        minorVersion = (int(value[i]) >> 14) & 255
        microVersion = (int(value[i]) >> 6) & 255
        nanoVersion = int(value[i]) & 63
        return "%d.%.2d.%.2d.%d" % (majorVersion, minorVersion, microVersion, nanoVersion)
    else:
        majorVersion = int(value[i]) >> 22
        minorVersion = int(value[i]) >> 12 & 1023
        microVersion = int(value[i]) & 4095
        return "%d.%d.%d" % (majorVersion, minorVersion, microVersion)


def setColumnFrameBuffer(TreeFB, Title):
    for i, column_title in enumerate(Title):

        FBrenderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(column_title, FBrenderer, text=i)
        column.add_attribute(FBrenderer, "background", len(Title))
        if i < len(Title) - 1:
            FBrenderer.set_alignment(0.5, 0.5)
            column.set_alignment(0.5)
        column.set_property("min-width", 40)
        TreeFB.set_property("can-focus", False)
        TreeFB.append_column(column)
        
def createSearchEntry(store_filter):
    entry = Gtk.SearchEntry()
    entry.set_property("placeholder_text","Type here to filter.....")
    entry.connect("search-changed", refresh_filter, store_filter)
    return entry


def getDeviceSize(size):
    sizeMB = float(size) / (1024 * 1024 * 1024)
    if sizeMB < 1.0:
        sizeMB = str(format((sizeMB * 1024), '.2f')) + " MB"
    else:
        sizeMB = str(format(sizeMB, '.2f')) + " GB"
    return sizeMB


def searchStore(TreeGLExt, grid3, refresh_filter):
    frameSearch = Gtk.Frame()
    entry = Gtk.SearchEntry()
    entry.set_placeholder_text("Type here to filter extensions.....")
    entry.connect("search-changed", refresh_filter)
    frameSearch.add(entry)
    scrollable_treelist2 = createScrollbar(TreeGLExt)
    grid3.attach(frameSearch, 0, 0, 1, 1)
    grid3.attach_next_to(scrollable_treelist2, frameSearch, Gtk.PositionType.BOTTOM, 1, 1)


def refresh_filter(self, store_filter):
    store_filter.refilter()



def appendLimitsRHS(filename, temp):
    LimitsRHS = []
    LimitRHSValue = []
    i = 0
    with open(filename, "r") as file1:
        for line in file1:
            if "= " in line:
                LimitsRHS.append(temp[i])
                LimitRHSValue.append(True)
                i = i + 1
            else:
                LimitsRHS.append("")
                LimitRHSValue.append(False)
    return LimitsRHS, LimitRHSValue

def getGpuImage(line):
    if "Intel" in line and "Arc" not in line:
        gpu_image = fetchImageFromUrl(const.INTEL_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "Intel" in line and "Arc" in line:
        gpu_image = fetchImageFromUrl(const.INTEL_ARC_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "GTX" in line and "GeForce" in line:
        gpu_image = fetchImageFromUrl(const.NVIDIA_GTX_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "RTX" in line and "GeForce" in line:
        gpu_image = fetchImageFromUrl(const.NVIDIA_RTX_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "GeForce" in line and ("GTX" not in line or "RTX" not in line):
        gpu_image = fetchImageFromUrl(const.GEFORCE_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "CUDA" in line and ("GTX" not in line or "RTX" not in line):
        gpu_image = fetchImageFromUrl(const.CUDA_PNG, 100, const.ICON_HEIGHT, True)
    elif "Ryzen" in line and "AMD" in line:
        gpu_image = fetchImageFromUrl(const.AMDRYZEN_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "Radeon" in line and "AMD" in line and "Pro" not in line:
        gpu_image = fetchImageFromUrl(const.AMDRADEON_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "Radeon" in line and "AMD" in line and "Pro" in line:
        gpu_image = fetchImageFromUrl(const.AMD_RADEON_Pro_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "AMD" in line or "ATI" in line and "Radeon" not in line:
        gpu_image = fetchImageFromUrl(const.AMD_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "LLVM" in line:
        gpu_image = fetchImageFromUrl(const.LLVM_LOGO_SVG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "Mesa" in line or "Clover" in line:
        gpu_image = fetchImageFromUrl(const.MESA_LOGO_PNG,100,const.ICON_HEIGHT, False)
    elif "Portable Computing Language" in line:
        gpu_image = fetchImageFromUrl(const.POCL_LOGO_PNG,100,const.ICON_HEIGHT, False)
    return gpu_image

def getLogo(line):
    if "Ubuntu" in line and "Gnome" not in line:
        logo_pixbuf  = fetchImageFromUrl(const.Ubuntu_logo,32,20, True)
    elif "Flatpak" in line:
        logo_pixbuf = fetchImageFromUrl(const.Flatpak_logo,32,20)
    elif "Kubuntu" in line:
        logo_pixbuf = fetchImageFromUrl(const.Kubuntu_logo,32,20)
    elif "Lubuntu" in line:
        logo_pixbuf = fetchImageFromUrl(const.Lubuntu_logo,32,20)
    elif "Solus" in line:       
        logo_pixbuf = fetchImageFromUrl(const.Solus_logo,32,20)
    elif "Xubuntu" in line:
        logo_pixbuf = fetchImageFromUrl(const.Xubuntu_logo,32,20)
    elif "Elementary" in line:
        logo_pixbuf = fetchImageFromUrl(const.Elementary_logo,32,20)
    elif "Debian" in line:
        logo_pixbuf = fetchImageFromUrl(const.Debian_logo,32,20)
    elif "opensuse" in line:
        logo_pixbuf = fetchImageFromUrl(const.Open_Suse_logo,32,20)
    elif "Pop" in line:
        logo_pixbuf = fetchImageFromUrl(const.Pop_os_logo,32,20)
    elif "MX" in line:
        logo_pixbuf = fetchImageFromUrl(const.MX_linux_logo,32,20)
    elif "Zorin" in line:
        logo_pixbuf = fetchImageFromUrl(const.Zorin_os_logo,32,20)
    elif "Mint" in line:
        logo_pixbuf = fetchImageFromUrl(const.Mint_logo,32,20, True)
    elif "Radeon" in line and "Ryzen" not in line:
        logo_pixbuf = fetchImageFromUrl(const.Radeon_logo,32,20, True)
    elif "Ryzen" in line:
        logo_pixbuf = fetchImageFromUrl(const.Ryzen_logo,32,20, True)
    elif "Mesa" in line or "radv" in line or "llvmpipe" in line and "LLVM" not in line:
        logo_pixbuf = fetchImageFromUrl(const.Mesa_logo,32,20, True)
    elif "LLVM" in line :
        logo_pixbuf = fetchImageFromUrl(const.LLVM_logo,32,20, True)
    elif "NVIDIA" in line and "Ryzen" not in line:
        logo_pixbuf = fetchImageFromUrl(const.Nvidia_logo,32,20, True)      
    elif "AMD" in line:
        logo_pixbuf = fetchImageFromUrl(const.AMD_logo,32,20, True)      
    elif "Intel" in line:
        logo_pixbuf = fetchImageFromUrl(const.Intel_logo,32,20, True)
    elif "Fedora" in line:
        logo_pixbuf = fetchImageFromUrl(const.fedora_logo,32,20, True)
    elif "Manjaro" in line:
        logo_pixbuf = fetchImageFromUrl(const.Manjaro_logo,32,20, True)
    elif "Budgie" in line:
        logo_pixbuf = fetchImageFromUrl(const.Budgie_logo,32,20, True)
    elif "GNOME" in line:
        logo_pixbuf = fetchImageFromUrl(const.Gnome_logo,32,20, True)
    elif "Unity" in line:
        logo_pixbuf = fetchImageFromUrl(const.Unity_logo,32,20, True)
    elif "Fluxbox" in line:
        logo_pixbuf = fetchImageFromUrl(const.Fluxbox_logo,32,20, True)
    elif "XFCE" in line:
        logo_pixbuf = fetchImageFromUrl(const.XFCE_logo,32,20, True)
    elif "MATE" in line:
        logo_pixbuf = fetchImageFromUrl(const.Mate_logo,32,20, True)
    elif "Cinnamon" in line:
        logo_pixbuf = fetchImageFromUrl(const.Cinnamon_logo,32,20, True)
    elif "wayland" in line:
        logo_pixbuf = fetchImageFromUrl(const.Wayland_logo,32,20, True)
    elif "x11" in line:
        logo_pixbuf = fetchImageFromUrl(const.X11_logo,32,20, True)
    elif "KDE" in line:
        logo_pixbuf = fetchImageFromUrl(const.Kde_logo,32,20, True)
    else:
        logo_pixbuf = fetchImageFromUrl(const.TRANSPARENT_PIXBUF,32,20,True)
    return logo_pixbuf