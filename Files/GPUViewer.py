import gi
import os
import Const

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gdk
from OpenGLViewer import OpenGL
from VulkanViewer import Vulkan
from About import about


def createMainWindow():
    gtk = Gtk.Window(title="GPU Viewer v1.1")

    setScreenSize(gtk)

    notebook = Gtk.Notebook()
    gtk.add(notebook)

    openGlTab = createTab(notebook, Const.OPEN_GL_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT)
    OpenGL(openGlTab)

    if isVulkanSupported():
        vulkanTab = createTab(notebook, Const.VULKAN_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT)
        Vulkan(vulkanTab)

    aboutTab = createTab(notebook, Const.ABOUT_US_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT)
    about(aboutTab)

    return gtk


def isVulkanSupported():
    os.system("vulkaninfo > /tmp/vulkaninfo.txt")
    with open("/tmp/vulkaninfo.txt", "r") as file1:
        count = len(file1.readlines())
    return count > 0


def createTab(notebook, iconUrl, iconWidth, iconHeight):
    tab = Gtk.VBox(spacing=10)
    tab.set_border_width(20)
    openGlIcon = fetchImageFromUrl(iconUrl, iconWidth, iconHeight)
    notebook.append_page(tab, Gtk.Image.new_from_pixbuf(openGlIcon))
    return tab


def fetchImageFromUrl(imgUrl, iconWidth, iconHeight):
    return GdkPixbuf.Pixbuf.new_from_file_at_scale(
        filename=imgUrl, width=iconWidth, height=iconHeight, preserve_aspect_ratio=True)


def setScreenSize(gtk):
    Screen = Gdk.Screen.get_default()
    if Screen.get_height() > 950:
        gtk.set_size_request(1000, 950)
    else:
        gtk.set_size_request(1000, 720)


win = createMainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
