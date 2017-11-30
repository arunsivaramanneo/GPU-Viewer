#!/usr/bin/python

import os
import Const
from Common import MyGtk, fetchImageFromUrl, setScreenSize
from OpenGLViewer import OpenGL
from VulkanViewer import Vulkan
from About import about
import threading
import time


def main():
    a = time.time()
    gtk = MyGtk("GPU-Viewer v1.2")
    setScreenSize(gtk, Const.WIDTH_RATIO, Const.HEIGHT_RATIO1)

    openGlTab = gtk.createTab(Const.OPEN_GL_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
    t1=threading.Thread(target=OpenGL,args=(openGlTab,))
    t1.start()

    if isVulkanSupported():
        vulkanTab = gtk.createTab(Const.VULKAN_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
        t2=threading.Thread(target=Vulkan,args=(vulkanTab,))
        t2.start()

    aboutTab = gtk.createTab(Const.ABOUT_US_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, False)
    t3=threading.Thread(target=about,args=(aboutTab,))
    t3.start()

    t1.join()
    t2.join()
    t3.join()
    print(time.time()-a)
    gtk.connect("delete-event", quit)
    gtk.show_all()
    gtk.mainLoop()


def isVulkanSupported():
    os.system("vulkaninfo > /tmp/vulkaninfo.txt")
    with open("/tmp/vulkaninfo.txt", "r") as file1:
        count = len(file1.readlines())
    return count > 0


def quit(instance, value):
    os.system("rm -rf *.pyc")
    instance.quit()


main()  # Program starts here
