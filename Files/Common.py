import gi
import Const

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

from gi.repository import Gdk, Gtk, GdkPixbuf


class MyGtk(Gtk.Window):
    def __init__(self, title):
        super(MyGtk, self).__init__(title=title)
        self.set_icon_from_file(Const.APP_LOGO_PNG)
        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

    def createTab(self, iconUrl, iconWidth, iconHeight, aspectRatio):
        tab = Gtk.VBox(spacing=10)
        tab.set_border_width(20)
        openGlIcon = fetchImageFromUrl(iconUrl, iconWidth, iconHeight, aspectRatio)
        self.notebook.append_page(tab, Gtk.Image.new_from_pixbuf(openGlIcon))
        return tab

    def mainLoop(self):
        Gtk.main()

    def quit(self):
        Gtk.main_quit()


# Setting the Minimum Screen Size
def setScreenSize(self, widthRatio, heightRatio):
    Screen = Gdk.Screen.get_default()
    self.set_size_request(Screen.get_width() * widthRatio, Screen.get_height() * heightRatio)


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
def setColumns(Treeview, Title, MWIDTH,align):
    for i, column_title in enumerate(Title):
        renderer = Gtk.CellRendererText(font=Const.FONT)
        column = Gtk.TreeViewColumn(column_title, renderer, text=i)
        column.set_sort_column_id(i)
        column.set_alignment(align)
        column.add_attribute(renderer, "background", len(Title))
        column.set_property("min-width", MWIDTH)
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
