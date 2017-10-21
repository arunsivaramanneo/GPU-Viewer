import os
import Const
from Common import MyGtk, fetchImageFromUrl
from OpenGLViewer import OpenGL
from VulkanViewer import Vulkan
from About import about


def main():
    gtk = MyGtk("GPU Viewer")

    gtk.setScreenSize()

    openGlTab = gtk.createTab(Const.OPEN_GL_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
    OpenGL(openGlTab)

    if isVulkanSupported():
        vulkanTab = gtk.createTab(Const.VULKAN_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
        Vulkan(vulkanTab)

    aboutTab = gtk.createTab(Const.ABOUT_US_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, False)
    about(aboutTab)

    gtk.connect("delete-event", quit)
    gtk.show_all()
    gtk.mainLoop()


def isVulkanSupported():
    os.system("vulkaninfo > /tmp/vulkaninfo.txt")
    with open("/tmp/vulkaninfo.txt", "r") as file1:
        count = len(file1.readlines())
    return count > 0


def quit(instance, value):
    instance.quit()


main()  # Program starts here
