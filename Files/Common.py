import gi
import Const
import os

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

from gi.repository import Gdk, Gtk, GdkPixbuf


class MyGtk(Gtk.Window):
    def __init__(self, title):
        super(MyGtk, self).__init__(title=title)
        self.set_icon_from_file(Const.APP_LOGO_PNG)
        self.notebook = Gtk.Notebook()
        self.add(self.notebook)
        setting = Gtk.Settings.get_default()

        if Gtk.get_minor_version() >= 22:
            #print(Gtk.get_minor_version())
            theme = Gtk.CssProvider()
            theme.load_from_path("gtk.css")
            screen = Gdk.Screen.get_default()
            setting.set_property("gtk-theme-name", "Qogir")
            style_context = self.get_style_context()
            style_context.add_provider_for_screen(screen, theme, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        elif Const.THEME1:
            setting.set_property("gtk-theme-name", "Adwaita")
        elif Const.THEME2:
            setting.set_property("gtk-theme-name", "Adapta")

    def createTab(self, iconUrl, iconWidth, iconHeight, aspectRatio):
        tab = Gtk.Box(spacing=5)
        openGlIcon = fetchImageFromUrl(iconUrl, iconWidth, iconHeight, aspectRatio)
        self.notebook.append_page(tab, Gtk.Image.new_from_pixbuf(openGlIcon))
        return tab

    def mainLoop(self):
        Gtk.main()

    def quit(self):
        Gtk.main_quit()

#getting Ram Details in GB

def getRamInGb(ram):
    ram1 = ram.split()
    return str("%.2f" %(float(ram1[0])/(1024*1024))) + " GB"

# Setting the Minimum Screen Size
def setScreenSize(self, widthRatio, heightRatio):
    Screen = Gdk.Screen.get_default()
    if Screen.get_height() == 2160:
        self.set_default_size(Screen.get_width() * 0.50, Screen.get_height() * 0.65)
    else:
        self.set_default_size(Screen.get_width() * widthRatio, Screen.get_height() * heightRatio)

    self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)


# fetching the Images/Logos from the Const File
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


# Setting the background color for rows
def setBackgroundColor(i):
    if i % 2 == 0:
        background_color = Const.BGCOLOR1
    else:
        background_color = Const.BGCOLOR2
    return background_color


# setting up Sub Tabs in Vulkan

def createSubTab(Tab, notebook, label):
    Tab.set_border_width(10)
    notebook.append_page(Tab, Gtk.Label(label))
    Frame = Gtk.Frame()
    Tab.add(Frame)
    Grid = Gtk.Grid()
    Frame.add(Grid)
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

def createScrollbar(Treeview):
    Scrollbar = Gtk.ScrolledWindow()
    Scrollbar.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    Scrollbar.set_vexpand(True)
    Scrollbar.add(Treeview)
    return Scrollbar


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
                fgColor.append(Const.COLOR1)
            else:
                value.append("false")
                fgColor.append(Const.COLOR2)
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
                    fgColor.append(Const.COLOR1)
                    loop = loop + 1
                    if ":" in f:
                        break
                if "None" in line and i >= loop:
                    value.append("false")
                    fgColor.append(Const.COLOR2)
                    loop = loop + 1
                    if ":" in f:
                        break
    return fgColor, value




def getLinkButtonImg(img, link, toolTip):
    Logbutton = Gtk.LinkButton(link)
    Logbutton.add(Gtk.Image.new_from_pixbuf(img))
    Logbutton.set_tooltip_text(toolTip)
    return Logbutton


def getVulkanVersion(value):
    majorVersion = int(value) >> 22
    minorVersion = int(value) >> 12 & 1023
    patchVersion = int(value) & 4095
    return "%d.%d.%d" % (majorVersion, minorVersion, patchVersion)


def getDriverVersion(value):
    if '4318' in value[6]:
        majorVersion = (int(value[4]) >> 22) & 1023
        minorVersion = (int(value[4]) >> 14) & 255
        microVersion = (int(value[4]) >> 6) & 255
        nanoVersion = int(value[4]) & 63
        return "%d.%.2d.%.2d.%d" % (majorVersion, minorVersion, microVersion, nanoVersion)
    else:
        majorVersion = int(value[4]) >> 22
        minorVersion = int(value[4]) >> 12 & 1023
        microVersion = int(value[4]) & 4095
        return "%d.%d.%d" % (majorVersion, minorVersion, microVersion)


def setColumnFrameBuffer(TreeFB, Title):
    for i, column_title in enumerate(Title):

        FBrenderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(column_title, FBrenderer, text=i)
        column.add_attribute(FBrenderer, "background", 25)
        if i < len(Title) - 1:
            FBrenderer.set_alignment(0.5, 0.5)
            column.set_alignment(0.5)
        column.set_property("min-width", 40)
        TreeFB.set_property("can-focus", False)
        TreeFB.append_column(column)


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
