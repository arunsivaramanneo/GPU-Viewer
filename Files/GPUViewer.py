#!/usr/bin/python3
import sys
import gi
import const
import Common
import subprocess
import Filenames
import threading
import time
import os
from pathlib import Path

gi.require_version('Gtk','4.0')
gi.require_version('Gdk','4.0')
from gi.repository import Gtk, Pango, Gdk,Gio

from Common import getScreenSize,create_tab,MyGtk,setMargin, copyContentsFromFile
from VulkanViewer import Vulkan
from OpenCL import openCL
from OpenGLViewer import OpenGL
from VdpauViewer import vdpauinfo
from About import about

Title1 = "About GPU-Viewer v2.0"

if Path(Filenames.gpu_viewer_folder_path).exists():

    def show_message(app):
        message_window = Gtk.ApplicationWindow(application=app)
        message_window.set_title("gpu-viewer application is already running")
        message_window.set_default_size(480,120)
        message_window.set_resizable(False)
        message_window.present()
        message_window_frame = Gtk.Frame()
        setMargin(message_window_frame,5,5,10)
        label = Gtk.Label(label="If you are unable to view the application, please run rm -r /tmp/gpu-viewer and run the application again")
        message_window.set_child(message_window_frame)
        message_window_frame.set_child(label)
        setMargin(message_window,5,5,10)

    app = Gtk.Application()
    app.connect("activate",show_message)
    app.run(None)

else:
    def main(win):
        T1 = time.time()

        mkdir_process = subprocess.Popen(Filenames.mkdir_output_command,stdout=subprocess.PIPE,shell=True)
        mkdir_process.communicate()
        gtk = MyGtk("GPU-VIEWER")
    #    setScreenSize(gtk, const.WIDTH_RATIO, const.HEIGHT_RATIO1)
        
        notebook = Gtk.Notebook()
        win.set_child(notebook)

        if isVulkanSupported():
            vulkanTab = create_tab(notebook,const.VULKAN_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, False)
            page = notebook.get_page(vulkanTab)
            page.set_property("tab-expand",True)
            t2 = threading.Thread(target=Vulkan, args=(vulkanTab,))
            t2.start()
            t2.join()

        if isOpenglSupported():
            openGlTab = create_tab(notebook,const.OPEN_GL_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, False)
            page = notebook.get_page(openGlTab)
            page.set_property("tab-expand",True)
            t1 = threading.Thread(target=OpenGL, args=(openGlTab,))
            t1.start()
            t1.join()

        if isOpenclSupported():
            openclTab = create_tab(notebook,const.OPEN_CL_PNG, const.ICON_WIDTH, const. ICON_HEIGHT, False)
            page = notebook.get_page(openclTab)
            page.set_property("tab-fill",True)
            page.set_property("tab-expand",True)
            t4 = threading.Thread(target=openCL, args=(openclTab,))
            t4.start()
            t4.join()

        if isVdpauinfoSupported():
            vdpauTab = create_tab(notebook,const.VDPAU_CL_PNG, const.ICON_WIDTH, const. ICON_HEIGHT, False)
            page_vdpau = notebook.get_page(vdpauTab)
            page_vdpau.set_property("tab-expand",True)
            vdpauinfo(vdpauTab)

        aboutTab = create_tab(notebook,const.ABOUT_US_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, False)
        page = notebook.get_page(aboutTab)
        page.set_property("tab-expand",True)
        t3 = threading.Thread(target=about, args=(aboutTab,))
        t3.start()
        t3.join()   

        print(time.time()-T1)
        win.connect("close-request",quit)
    #    gtk.mainLoop()


    def isOpenclSupported():
        with open(Filenames.opencl_output_file, "w") as file:
            clinfo_process = subprocess.Popen(Filenames.clinfo_output_command,shell=True,stdout= file,universal_newlines=True)
            clinfo_process.wait()
            clinfo_process.communicate()
        clinfo_output = copyContentsFromFile(Filenames.opencl_output_file)
        return len(clinfo_output) > 10 and clinfo_process.returncode == 0

    def isOpenglSupported():
        with open(Filenames.opengl_outpuf_file, "w") as file:
            opengl_process = subprocess.Popen(Filenames.opengl_output_command,shell=True,stdout= file,universal_newlines=True)
            opengl_process.wait()
            opengl_process.communicate()
        opengl_output = copyContentsFromFile(Filenames.opengl_outpuf_file)
        return len(opengl_output) > 10 and opengl_process.returncode == 0


    def isVulkanSupported():
        with open(Filenames.vulkaninfo_output_file,"w") as file:
            vulkan_process = subprocess.Popen(Filenames.vulkaninfo_output_command,shell=True,stdout= file,universal_newlines=True)
            vulkan_process.wait()
            vulkan_process.communicate()
        vulkaninfo_output = copyContentsFromFile(Filenames.vulkaninfo_output_file)
        return len(vulkaninfo_output) > 10 and vulkan_process.returncode == 0


    def quit(instance):
        os.system("unset LC_ALL")
        rmdir_process =subprocess.Popen(Filenames.rmdir_output_command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        rmdir_process.communicate()
        instance.destroy()

    def isVdpauinfoSupported():
        with open(Filenames.vdpauinfo_output_file, "w") as file:
            vdpauinfo_process = subprocess.Popen(Filenames.vdpauinfo_output_command,shell=True,stdout= file,universal_newlines=True)
            vdpauinfo_process.wait()
            vdpauinfo_process.communicate()
        vdpauinfo_output = copyContentsFromFile(Filenames.vdpauinfo_output_file)
        return len(vdpauinfo_output) > 10 and vdpauinfo_process.returncode == 0

    def on_activate(app):
        win = Gtk.ApplicationWindow(application=app)
        win.present()
        win.set_title("GPU-Viewer v2.0")
        width,height = getScreenSize()
        win.set_size_request(int(width) * const.WIDTH_RATIO ,int(height) * const.HEIGHT_RATIO1)
        display = Gtk.Widget.get_display(win)
        provider = Gtk.CssProvider.new()
        fname = Gio.file_new_for_path('gtk.css')
        provider.load_from_file(fname)
        Gtk.StyleContext.add_provider_for_display(display, provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        main(win)  # Program starts here

    app = Gtk.Application(application_id='io.github.arunsivaramanneo.GPUViewer')
    app.connect('activate', on_activate)

    app.run(None)   

