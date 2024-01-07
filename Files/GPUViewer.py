#!/usr/bin/python3
#define PING_TIMEOUT_DELAY 8000

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
gi.require_version(namespace='Adw', version='1')
from gi.repository import Gtk, Pango, Gdk,Gio,GLib,Adw

Adw.init()

from Common import getScreenSize,create_tab,MyGtk,setMargin, copyContentsFromFile,on_light_action_actived,on_dark_action_actived
from VulkanViewer import Vulkan
from OpenCL import openCL
from OpenGLViewer import OpenGL
from VdpauViewer import vdpauinfo
from aboutPage import about_page

Title1 = "About GPU-Viewer v2.0"

if Path(Filenames.gpu_viewer_folder_path).exists():
    
    def show_message(app):
        message_window = Gtk.ApplicationWindow(application=app)
        message_grid = Gtk.Grid()
        message_window.set_title("gpu-viewer application is already running")
        message_window.set_default_size(480,120)
        message_window.set_resizable(False)
        message_window.present()
        message_window_frame = Gtk.Frame()
        setMargin(message_window_frame,5,5,10)
        label = Gtk.Label(label="If you are unable to view the application, please run rm -r /tmp/gpu-viewer and run the application again")
        message_window.set_child(message_window_frame)
        message_window_frame.set_child(message_grid)
        setMargin(label,5,10,0)
        message_grid.attach(label,0,0,20,1)
        
        message_button_OK = Gtk.Button.new_with_label("OK")
        message_button_OK.connect("clicked",quit)
    #    message_button_CANCEL = Gtk.Button.new_with_label("No")
        setMargin(message_button_OK,500,50,10)
        message_grid.attach_next_to(message_button_OK,label,Gtk.PositionType.BOTTOM,5,1)
     #   message_grid.attach_next_to(message_button_CANCEL,message_button_OK,Gtk.PositionType.RIGHT,10,1)
    #    setMargin(message_button_CANCEL,50,50,10)
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
        win.set_content(notebook)

        if isVulkanSupported():
            vulkanTab = create_tab(notebook,const.VULKAN_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, False)
            page = notebook.get_page(vulkanTab)
            page.set_property("tab-expand",True)
            vulkanTab.add_css_class(css_class='compact')
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
        t3 = threading.Thread(target=about_page, args=(aboutTab,))
        t3.start()
        t3.join()   

        print(time.time()-T1)
    #    win.connect("close-request",quit)
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
        unset_lc_all_process = subprocess.Popen(Filenames.unset_LC_ALL_conmand,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        unset_lc_all_process.communicate()
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
        win = Adw.ApplicationWindow(application=app)
        headerbar = Adw.HeaderBar.new()
        headerbar.add_css_class(css_class='compact')

        adw_toolbar_view = Adw.ToolbarView.new()
        win.set_content(adw_toolbar_view)

        adw_toolbar_view.add_top_bar(headerbar)
    #    win.set_titlebar(headerbar)
        win.set_title("GPU-Viewer v2.3")

        light_action = Gio.SimpleAction.new("about", None) # look at MENU_XML win.quit
        light_action.connect("activate", on_light_action_actived,win)
        win.add_action(light_action) # (self window) == win in MENU_XML
        
        dark_action = Gio.SimpleAction.new("quit", None) # look at MENU_XML win.about
        dark_action.connect("activate", on_dark_action_actived,win)
        win.add_action(dark_action) # (self window) == win in MENU_XML

        menubutton = Gtk.MenuButton.new()
        menubutton.set_icon_name("open-menu-symbolic") 
        menu = Gtk.Builder.new_from_string(const.MENU_XML, -1).get_object("app-menu")
        menubutton.set_menu_model(menu)
        headerbar.pack_end(menubutton)

        width,height = getScreenSize()
        if int(width) > 2160 and int(height) < 1440:
            win.set_size_request(2160 * const.WIDTH_RATIO ,int(height) * const.HEIGHT_RATIO1)
        elif int(width) > 2160 and int(height) > 1440:
            win.set_size_request(2160 * const.WIDTH_RATIO ,1440 * const.HEIGHT_RATIO1)
        else:
            win.set_size_request(int(width) * const.WIDTH_RATIO ,int(height) * const.HEIGHT_RATIO1)
        display = Gtk.Widget.get_display(win)
        provider = Gtk.CssProvider.new()
        fname = Gio.file_new_for_path('gtk_test.css')
        provider.load_from_file(fname)
        Gtk.StyleContext.add_provider_for_display(display, provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        win.present()
        win.connect("close-request",quit)
        main(adw_toolbar_view)  # Program starts here

    app = Adw.Application(application_id='io.github.arunsivaramanneo.GPUViewer')
    app.connect('activate', on_activate)

    app.run(None)   

