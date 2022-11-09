#!/usr/bin/python3
import os
import subprocess
import Const
import Commands
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
    message_info = Gtk.MessageDialog(flags=0,message_type=Gtk.MessageType.INFO,buttons=Gtk.ButtonsType.OK,text="gpu-viewer  application is already running")
    message_info.format_secondary_text("If you are unable to view the application, please run rm -r /tmp/gpu-viewer and run the application again")
    message_info.run()
    message_info.destroy()
else:
    def main():
    #    T1 = time.time()

        mkdir_process = subprocess.Popen(Commands.mkdir_output_command,stdout=subprocess.PIPE,shell=True)
        mkdir_process.communicate()
        gtk = MyGtk("GPU-VIEWER")
        setScreenSize(gtk, Const.WIDTH_RATIO, Const.HEIGHT_RATIO1)
        
        if isVulkanSupported():
            vulkanTab = gtk.createTab(Const.VULKAN_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
            t2 = threading.Thread(target=Vulkan, args=(vulkanTab,))
            t2.start()
            t2.join()

        if isOpenglSupported():
            openGlTab = gtk.createTab(Const.OPEN_GL_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
            t1 = threading.Thread(target=OpenGL, args=(openGlTab,))
            t1.start()
            t1.join()

        if isOpenclSupported():
            openclTab = gtk.createTab(Const.OPEN_CL_PNG, Const.ICON_WIDTH, Const. ICON_HEIGHT, False)
            t4 = threading.Thread(target=openCL, args=(openclTab,))
            t4.start()
            t4.join()

        if isVdpauinfoSupported():
            vdpauTab = gtk.createTab(Const.VDPAU_CL_PNG, Const.ICON_WIDTH, Const. ICON_HEIGHT, False)
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
        with open("/tmp/gpu-viewer/clinfo.txt", "w") as file:
            clinfo_process = subprocess.Popen(Commands.clinfo_output_command,shell=True,stdout= file,universal_newlines=True)
            clinfo_process.wait()
            clinfo_process.communicate()
        return clinfo_process.returncode == 0

    def isOpenglSupported():
        with open("/tmp/gpu-viewer/glxinfo.txt", "w") as file:
            opengl_process = subprocess.Popen(Commands.opengl_output_command,shell=False,stdout= file,universal_newlines=True)
            opengl_process.wait()
            opengl_process.communicate()
        return opengl_process.returncode == 1


    def isVulkanSupported():
        with open("/tmp/gpu-viewer/vulkaninfo.txt","w") as file:
            vulkan_process = subprocess.Popen(Commands.vulkaninfo_output_command,shell=False,stdout= file,universal_newlines=True)
            vulkan_process.wait()
            vulkan_process.communicate()
        return vulkan_process.returncode == 0


    def quit(instance, value):
        os.system("unset LC_ALL")
        os.system("rm /tmp/gpu-viewer -r")
        instance.quit()

    def isVdpauinfoSupported():
        with open("/tmp/gpu-viewer/vdpauinfo.txt", "w") as file:
            vdpauinfo_process = subprocess.Popen(Commands.vdpauinfo_output_command,shell=False,stdout= file,universal_newlines=True)
            vdpauinfo_process.wait()
            vdpauinfo_process.communicate()
        return vdpauinfo_process.returncode == 0

    main()  # Program starts here
