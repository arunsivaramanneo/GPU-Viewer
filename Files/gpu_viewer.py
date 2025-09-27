#!/usr/bin/env python3

# Import necessary libraries.
import sys, os
import gi
import subprocess

# This line is crucial for working with PyGObject.
# It ensures we are using the correct versions of the libraries.
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject,Gdk, Gio
from vulkan_viewer import create_vulkan_tab_content
import Filenames, const
from Common import copyContentsFromFile,getScreenSize,fetchContentsFromCommand,setMargin
from aboutPage import about_page
from OpenGLViewer import OpenGL
from OpenCL import openCL
from VdpauViewer import vdpauinfo
from VulkanVideoViewer import VulkanVideo
from pathlib import Path

# Define the main application class.
# It inherits from Adw.Application, which provides a modern application shell.

def isVulkanSupported():
    with open(Filenames.vulkaninfo_output_file,"w") as file:
        vulkan_process = subprocess.Popen(Filenames.vulkaninfo_output_command,shell=True,stdout= file,universal_newlines=True)
        vulkan_process.wait()
        vulkan_process.communicate()
    vulkaninfo_output = copyContentsFromFile(Filenames.vulkaninfo_output_file)
    return len(vulkaninfo_output) > 10 and vulkan_process.returncode == 0

def isOpenglSupported():
    with open(Filenames.opengl_outpuf_file, "w") as file:
        opengl_process = subprocess.Popen(Filenames.opengl_output_command,shell=True,stdout= file,universal_newlines=True)
        opengl_process.wait()
        opengl_process.communicate()
    opengl_output = copyContentsFromFile(Filenames.opengl_outpuf_file)
    return len(opengl_output) > 10 and opengl_process.returncode == 0

def isOpenclSupported():
    with open(Filenames.opencl_output_file, "w") as file:
        clinfo_process = subprocess.Popen(Filenames.clinfo_output_command,shell=True,stdout= file,universal_newlines=True)
        clinfo_process.wait()
        clinfo_process.communicate()
    clinfo_output = copyContentsFromFile(Filenames.opencl_output_file)
    return len(clinfo_output) > 10 and clinfo_process.returncode == 0

def isVdpauinfoSupported():
    with open(Filenames.vdpauinfo_output_file, "w") as file:
        vdpauinfo_process = subprocess.Popen(Filenames.vdpauinfo_output_command,shell=True,stdout= file,universal_newlines=True)
        vdpauinfo_process.wait()
        vdpauinfo_process.communicate()
    vdpauinfo_output = copyContentsFromFile(Filenames.vdpauinfo_output_file)
    return len(vdpauinfo_output) > 10 and vdpauinfo_process.returncode == 0

def isVulkanVideoSupported():
    return  len(fetchContentsFromCommand("vulkaninfo | grep 'Video Profiles'")) > 0

def quit(instance):
    unset_lc_all_process = subprocess.Popen(Filenames.unset_LC_ALL_conmand,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    unset_lc_all_process.communicate()
    rmdir_process =subprocess.Popen(Filenames.rmdir_output_command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    rmdir_process.communicate()
    instance.destroy()

if Path(Filenames.gpu_viewer_folder_path).exists():
    
    def show_message(app):
        dialog = Gtk.AlertDialog()
        dialog.set_modal(False)
        dialog.set_message('gpu-viewer is already running')
        dialog.set_detail('If you are unable to view the application, please run rm -r /tmp/gpu-viewer and run the application again')
    #    dialog.set_default_button(0)
        dialog.set_cancel_button(1)
        dialog.choose(None,None,None,None)
    #    dialog.show()
        message_window = Gtk.ApplicationWindow(application=app)
        message_grid = Gtk.Grid()
        message_window.set_title("gpu-viewer application is already running")
        message_window.set_default_size(480,120)
        message_window.set_resizable(False)
    #    message_window.present()
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
    class GPUViewerApp(Adw.Application):
        """
        A simple Libadwaita application class.
        Inherits from Adw.Application to provide the application framework.
        """
        def __init__(self, **kwargs):
            # Call the parent constructor, providing a unique application ID
            super().__init__(application_id="io.github.arunsivaramanneo.GPUViewer", **kwargs)
            self.connect("activate", self.on_activate)    

        def _on_theme_toggled(self, switch, state):
            """
            Callback to handle the theme switch state change.
            It updates the Adw.StyleManager's color scheme based on the switch state.
            """
            style_manager = Adw.StyleManager.get_default()
            if state:
                # Set to dark theme
                style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)

            else:
                # Set to light theme
                style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)


        def on_activate(self, app):
            """
            Callback function for the 'activate' signal.
            This is where we create and show the main window.
            """
            # Create a new Adwaita ApplicationWindow
            self.window = Adw.ApplicationWindow.new(self)
            self.window.add_css_class(css_class="compact")
            self.window.set_title("GPU-Viewer v3.2")
            self.window.add_css_class(css_class="view")

            # Set the application's default size to 800x800

            width,height = getScreenSize()

            if int(width) > 2160 and int(height) < 1440:
                self.window.set_size_request(2160 * const.WIDTH_RATIO ,int(height) * const.HEIGHT_RATIO1)
            elif int(width) > 2160 and int(height) > 1440:
                self.window.set_size_request(2160 * const.WIDTH_RATIO ,1440 * const.HEIGHT_RATIO1)
            else:
                self.window.set_size_request(int(width) * const.WIDTH_RATIO ,int(height) * const.HEIGHT_RATIO1)
    
            provider = Gtk.CssProvider.new()
            try:
                p = subprocess.Popen(Filenames.fetch_theme_preference,stdout= subprocess.PIPE,stderr = subprocess.PIPE,shell=True,text=True)
                prefer_theme = p.communicate()[0]
            except NameError:
                print("Command not found")
            if "prefer-dark"  in prefer_theme:
                fname = Gio.file_new_for_path('gtk_dark.css')
            elif "default" in prefer_theme:
                fname = Gio.file_new_for_path('gtk_light.css')
            else:
                fname = Gio.file_new_for_path('gtk-dark.css')

            display = Gtk.Widget.get_display(self.window)
            provider.load_from_file(fname)
            Gtk.StyleContext.add_provider_for_display(display, provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            # Create a new Adwaita view stack to hold the different pages
            self.view_stack = Adw.ViewStack.new()

            # Create a view switcher that will display icons
            self.switcher = Adw.ViewSwitcher.new()
            self.switcher.set_stack(self.view_stack)
            self.switcher.set_policy(1)
            # Create a header bar
            self.header_bar = Adw.HeaderBar.new()
        #    self.header_bar.add_css_class(css_class="inline")
            # Set the view switcher as the custom title widget in the header bar
            self.header_bar.add_css_class(css_class="view")
            theme_switch = Gtk.Switch.new()
            theme_switch.set_valign(Gtk.Align.CENTER)

            icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
            icon_theme.add_search_path(os.path.abspath("../Images"))

            # Get the current theme preference from Adw.StyleManager
            style_manager = Adw.StyleManager.get_default()
            prefer_dark_theme = style_manager.get_dark()
            theme_switch.set_active(prefer_dark_theme)

            # Connect the switch's 'state-set' signal to a handler
            theme_switch.connect("state-set", self._on_theme_toggled)

            # Create an icon for the theme switch
            theme_icon = Gtk.Image.new_from_icon_name("theme")

            # Create a box to hold the icon and the switch
            theme_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
            theme_box.set_halign(Gtk.Align.END)
            theme_box.set_valign(Gtk.Align.CENTER)
     #       theme_box.append(theme_icon)
      #      theme_box.append(theme_switch)
       #     self.header_bar.pack_end(theme_box)
            self.header_bar.set_title_widget(title_widget=self.switcher)

            # Create a main box to hold the header bar and the view stack
            main_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
            main_box.append(self.header_bar)
            main_box.append(self.view_stack)



            # Set the main box as the content of the window
            self.window.set_content(main_box)

            mkdir_process = subprocess.Popen(Filenames.mkdir_output_command,stdout=subprocess.PIPE,shell=True)
            mkdir_process.communicate()

            # Create the first page (tab content) by calling the new function
            if isVulkanSupported():
                vulkan_box = create_vulkan_tab_content(self)

            # Create an icon for the first tab
            # Add the first page to the view stack, with a title and an icon
                self.view_stack.add_titled_with_icon(vulkan_box, "page1", "Vulkan", "Vulkan")
            # Create the second page (tab content)
        #    page2_box.set_halign(Gtk.Align.CENTER)
        #    page2_box.set_valign(Gtk.Align.CENTER)
       #     label2 = Gtk.Label.new("This is the second tab!")
        #    label2.set_css_classes(["title-1"])
        #    page2_box.append(label2)
            page2_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)

            # Create an icon for the second tab
            if isOpenglSupported():
                opengl_box = OpenGL(page2_box)
                self.view_stack.add_titled_with_icon(opengl_box, "page2", "OpenGL", "OpenGL")


            opencl_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)

            if isOpenclSupported():
                opencl_content = openCL(opencl_box)
                self.view_stack.add_titled_with_icon(opencl_content,"opencl_page","OpenCL","OpenCL")

            vulkan_video_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
            if isVulkanVideoSupported():
                vulkan_video_content = VulkanVideo(vulkan_video_box)
        #        page_vdpau = notebook.get_page(vdpauTab)
        #        page_vdpau.set_property("tab-expand",True)
                self.view_stack.add_titled_with_icon(vulkan_video_content,"vulkan_video_page","Vulkan Video","Vulkan-Video")

            vdpau_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
            if isVdpauinfoSupported():
                vdpau_content = vdpauinfo(vdpau_box)
                self.view_stack.add_titled_with_icon(vdpau_content,"vdpau_page","VDPAU","vdpauinfo")



            page3_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)

            # Add the second page to the view stack with a title and an icon
            about_box = about_page(page3_box)
            self.view_stack.add_titled_with_icon(about_box, "page3", "About Us", "about-us")
            self.window.connect("close-request",quit)

            # Show the window and all its children
            self.window.present()


    def main():
        """
        The main entry point of the application.
        """
        # Create an instance of our application class
        app = GPUViewerApp()

        # Run the application
        app.run(sys.argv)


    if __name__ == "__main__":
        main()
