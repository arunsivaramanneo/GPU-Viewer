#!/usr/bin/python

import os
import Const
from Common import MyGtk, fetchImageFromUrl, setScreenSize
from OpenGLViewer import OpenGL
from VulkanViewer import Vulkan
from About import about
from OpenCL import openCL
import threading


def main():

    gtk = MyGtk("GPU-Viewer v1.2")
    setScreenSize(gtk, Const.WIDTH_RATIO, Const.HEIGHT_RATIO1)

    openGlTab = gtk.createTab(Const.OPEN_GL_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
    t1=threading.Thread(target=OpenGL,args=(openGlTab,))
    t1.start()

    if isVulkanSupported():
        vulkanTab = gtk.createTab(Const.VULKAN_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
        t2=threading.Thread(target=Vulkan,args=(vulkanTab,))
        t2.start()
        t2.join()

    if isOpenclSupported():
        openclTab = gtk.createTab(Const.OPEN_CL_PNG, 100, Const.ICON_HEIGHT,False)
        openCL(openclTab)


    aboutTab = gtk.createTab(Const.ABOUT_US_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, False)
    t3=threading.Thread(target=about,args=(aboutTab,))
    t3.start()

    t1.join()
    t3.join()

    gtk.connect("delete-event", quit)
    gtk.show_all()
    gtk.mainLoop()

def isOpenclSupported():
    os.system("clinfo > /tmp/clinfo.txt")
    with open("/tmp/clinfo.txt","r") as file:
        count = len(file.readlines())
    return count > 1

def isVulkanSupported():
    os.system("vulkaninfo > /tmp/vulkaninfo.txt")
    with open("/tmp/vulkaninfo.txt", "r") as file1:
        count = len(file1.readlines())
    return count


def quit(instance, value):
    os.system("rm -rf *.pyc")
    instance.quit()


main()  # Program starts here
