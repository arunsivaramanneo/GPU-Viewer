#!/usr/bin/python3
import os
import Const
import os.path
from os import path
from Common import MyGtk, setScreenSize
from OpenGLViewer import OpenGL
from VulkanViewer import Vulkan
from About import about
from OpenCL import openCL
from VdpauViewer import vdpauinfo
import threading    
import gi
import time
    
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

if path.exists("/tmp/gpu-viewer") == True:
    message_info = Gtk.MessageDialog(flags=0,message_type=Gtk.MessageType.INFO,buttons=Gtk.ButtonsType.OK,text="gpu-viewer application is already running")
    message_info.format_secondary_text("Please run rm -r /usr/tmp/gpu-viewer if you are unable to view the application and run again")
    message_info.run()
    message_info.destroy()
else:
    def main():
    #    T1 = time.time()

        os.system("mkdir /tmp/gpu-viewer")
        gtk = MyGtk("GPU-VIEWER")
        setScreenSize(gtk, Const.WIDTH_RATIO, Const.HEIGHT_RATIO1)

        if isVulkanSupported():
            vulkanTab = gtk.createTab(Const.VULKAN_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
            t2 = threading.Thread(target=Vulkan, args=(vulkanTab,))
            t2.start()
            t2.join()

        openGlTab = gtk.createTab(Const.OPEN_GL_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
        t1 = threading.Thread(target=OpenGL, args=(openGlTab,))
        t1.start()
        t1.join()

        if isOpenclSupported():
            openclTab = gtk.createTab(Const.OPEN_CL_PNG, 130, Const. ICON_HEIGHT, False)
            t4 = threading.Thread(target=openCL, args=(openclTab,))
            t4.start()
            t4.join()

        if isVdpauinfoSupported():
            vdpauTab = gtk.createTab(Const.VDPAU_CL_PNG, 130, Const. ICON_HEIGHT, False)
            vdpauinfo(vdpauTab)

        aboutTab = gtk.createTab(Const.ABOUT_US_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, False)
        t3 = threading.Thread(target=about, args=(aboutTab,))
        t3.start()
        t3.join()

    #    print(time.time()-T1)
        gtk.connect("delete-event", quit)
        gtk.show_all()
        gtk.mainLoop()


    def isOpenclSupported():
        os.system("clinfo | awk '/Number of platforms/{flag=1;print}/NULL.*/{flag=0}flag' > /tmp/gpu-viewer/clinfo.txt")
        with open("/tmp/gpu-viewer/clinfo.txt", "r") as file:
            count = len(file.readlines())
        return count > 2


    def isVulkanSupported():
        os.system("vulkaninfo > /tmp/gpu-viewer/vulkaninfo.txt")
        with open("/tmp/gpu-viewer/vulkaninfo.txt", "r") as file1:
            count = len(file1.readlines())
        return count > 20


    def quit(instance, value):
        os.system("rm /tmp/gpu-viewer -r")
        instance.quit()

    def isVdpauinfoSupported():
        os.system("vdpauinfo > /tmp/gpu-viewer/vdpauinfo.txt")
        with open("/tmp/gpu-viewer/vdpauinfo.txt", "r") as file1:
            count = len(file1.readlines())
        return count > 20

    main()  # Program starts here
