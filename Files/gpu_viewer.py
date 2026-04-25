#!/usr/bin/env python3

# Copyright (C) 2017-2026 Arun Sivaraman <arunsivaramanneo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Import necessary libraries.
import sys, os

os.environ["PYTHONSAFEPATH"] = "1"
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
os.chdir(script_dir)

import gi
import subprocess
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# This line is crucial for working with PyGObject.
# It ensures we are using the correct versions of the libraries.
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject, Gdk, Gio, GLib
from vulkan_viewer import create_vulkan_tab_content
import Filenames, const
from Common import copyContentsFromFile,getScreenSize,fetchContentsFromCommand,setMargin,Config
from aboutPage import about_page
from OpenGLViewer import OpenGL
from OpenCL import openCL
from VdpauViewer import vdpauinfo
from VulkanVideoViewer import VulkanVideo
from pathlib import Path

# Define the main application class.
# It inherits from Adw.Application, which provides a modern application shell.

def isVulkanSupported():
    # Runs inside ThreadPoolExecutor (parallel with glxinfo/clinfo/vdpauinfo),
    # so --show-formats completes fully before _build_tabs_on_main_thread is
    # called — no race condition against create_vulkan_tab_content().
    with open(Filenames.vulkaninfo_output_file, "w") as file:
        vulkan_process = subprocess.Popen(
            Filenames.vulkaninfo_output_command,
            shell=True, stdout=file, universal_newlines=True
        )
        vulkan_process.wait()
        vulkan_process.communicate()
    vulkaninfo_output = copyContentsFromFile(Filenames.vulkaninfo_output_file)
    return len(vulkaninfo_output) > 10 and vulkan_process.returncode == 0

def isOpenglSupported():
    with open(Filenames.opengl_outpuf_file, "w") as file:
        opengl_process = subprocess.Popen(
            Filenames.opengl_output_command,
            shell=True, stdout=file, universal_newlines=True
        )
        opengl_process.wait()
        opengl_process.communicate()
    opengl_output = copyContentsFromFile(Filenames.opengl_outpuf_file)
    return len(opengl_output) > 10 and opengl_process.returncode == 0

def isOpenclSupported():
    # Fix #3 (part 1): Write clinfo output to the shared file so OpenCL.py
    # can reuse it without spawning a second clinfo process.
    with open(Filenames.opencl_output_file, "w") as file:
        clinfo_process = subprocess.Popen(
            "clinfo",
            shell=True, stdout=file, universal_newlines=True
        )
        clinfo_process.wait()
        clinfo_process.communicate()
    clinfo_output = copyContentsFromFile(Filenames.opencl_output_file)
    return len(clinfo_output) > 10 and clinfo_process.returncode == 0

def isVdpauinfoSupported():
    with open(Filenames.vdpauinfo_output_file, "w") as file:
        vdpauinfo_process = subprocess.Popen(
            Filenames.vdpauinfo_output_command,
            shell=True, stdout=file, universal_newlines=True
        )
        vdpauinfo_process.wait()
        vdpauinfo_process.communicate()
    vdpauinfo_output = copyContentsFromFile(Filenames.vdpauinfo_output_file)
    return len(vdpauinfo_output) > 10 and vdpauinfo_process.returncode == 0

def isVulkanVideoSupported():
    # Fix #1 & #6: Grep the file already written by isVulkanSupported() —
    # no need to spawn a second vulkaninfo process.
    try:
        return len(fetchContentsFromCommand(
            f"grep 'Video Profiles' {Filenames.vulkaninfo_output_file}"
        )) > 0
    except Exception:
        return False

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
            self.config = Config()
            self.connect("activate", self.on_activate)    

        def _on_save_button_clicked(self, button):
            visible_child_name = self.view_stack.get_visible_child_name()
            
            source_file = None
            default_name = "output.txt"
            
            if visible_child_name == "page1":
                source_file = Filenames.vulkaninfo_output_file
                default_name = "vulkaninfo.txt"
                if hasattr(self, 'vulkan_content_stack'):
                    vulkan_tab = self.vulkan_content_stack.get_visible_child_name()
                    if vulkan_tab == "system-information":
                        source_file = Filenames.vulkaninfo_output_file
                        default_name = "vulkaninfo.txt"
                    elif vulkan_tab == "device":
                        source_file = Filenames.vulkan_device_info_file
                        default_name = "deviceinfo.txt"
                    elif vulkan_tab == "properties":
                        source_file = Filenames.vulkan_device_properties_file
                        default_name = "properties.txt"
                    elif vulkan_tab == "limits":
                        source_file = Filenames.vulkan_device_limits_file
                        default_name = "limits.txt"
                    elif vulkan_tab == "features":
                        source_file = Filenames.vulkan_device_features_file
                        default_name = "features.txt"
                    elif vulkan_tab == "formats":
                        source_file = Filenames.vulkan_device_formats_file
                        default_name = "formats.txt"
                    elif vulkan_tab == "memory-types":
                        source_file = Filenames.vulkan_device_memory_types_file
                        default_name = "memory_types.txt"
                    elif vulkan_tab == "memory-heaps":
                        source_file = Filenames.vulkan_device_memory_heaps_file
                        default_name = "memory_heaps.txt"
                    elif vulkan_tab == "queues":
                        source_file = Filenames.vulkan_device_queues_file
                        default_name = "queues.txt"
                    elif vulkan_tab == "instance-extensions":
                        source_file = Filenames.vulkan_device_extensions_file
                        default_name = "extensions.txt"
                    elif vulkan_tab == "instance-layers":
                        source_file = Filenames.vulkan_device_layers_file
                        default_name = "layers.txt"
                    elif vulkan_tab == "surface":
                        source_file = Filenames.vulkan_device_surface_file
                        default_name = "surface.txt"

            elif visible_child_name == "page2":
                source_file = Filenames.opengl_outpuf_file
                default_name = "glxinfo.txt"
                if hasattr(self, 'opengl_extensions_notebook'):
                    opengl_tab = self.opengl_extensions_notebook.get_visible_child_name()
                    if opengl_tab == "opengl":
                        pass
                    elif opengl_tab == "opengl_es":
                        source_file = Filenames.opengl_vendor_es_extension_file
                        default_name = "opengl_es_extensions.txt"
                    elif opengl_tab == "egl_logo":
                        source_file = Filenames.egl_vendor_extension_file
                        default_name = "egl_extensions.txt"

            elif visible_child_name == "opencl_page":
                source_file = Filenames.opencl_output_file
                default_name = "clinfo.txt"
                if hasattr(self, 'opencl_content_stack'):
                    opencl_tab = self.opencl_content_stack.get_visible_child_name()
                    if opencl_tab == "platform-information":
                        source_file = Filenames.opencl_platform_details_file
                        default_name = "platform_details.txt"
                    elif opencl_tab == "device-information":
                        source_file = Filenames.opencl_device_details_file
                        default_name = "device_details.txt"
                    elif opencl_tab and opencl_tab.startswith("device-memory"):
                        source_file = Filenames.opencl_device_memory_and_image_file
                        default_name = "memory_and_image_details.txt"
                    elif opencl_tab and opencl_tab.startswith("queue-capabilities"):
                        source_file = Filenames.opencl_device_queue_execution_details_file
                        default_name = "queue_execution_details.txt"
                    elif opencl_tab == "device-vector-information":
                        source_file = Filenames.opencl_device_vector_file
                        default_name = "vector_details.txt"

            elif visible_child_name == "vdpau_page":
                source_file = Filenames.vdpauinfo_output_file
                default_name = "vdpauinfo.txt"
            elif visible_child_name == "vulkan_video_page":
                source_file = "/tmp/gpu-viewer/vulkan_video_info.txt"
                default_name = "vulkan_video_info.txt"
                with open(source_file, "w") as f:
                    subprocess.run(["vulkaninfo", "--show-video-props"], stdout=f, universal_newlines=True)
            else:
                return
            
            if not source_file or not os.path.exists(source_file):
                return

            dialog = Gtk.FileChooserNative.new("Save Tab Output",
                                               self.window,
                                               Gtk.FileChooserAction.SAVE,
                                               "Save",
                                               "Cancel")
            dialog.set_current_name(default_name)
            
            def on_response(native, response):
                if response == Gtk.ResponseType.ACCEPT:
                    file_out = native.get_file()
                    if file_out:
                        dest_path = file_out.get_path()
                        if dest_path:
                            shutil.copyfile(source_file, dest_path)
                            
            dialog.connect("response", on_response)
            dialog.show()

        def _on_theme_button_clicked(self, button):
            """
            Callback to handle the theme button click.
            It toggles the Adw.StyleManager's color scheme.
            """
            prefer_dark_theme = not self.config.get_theme_preference()
            self._apply_theme(prefer_dark_theme)

        def _apply_theme(self, state):
            """
            Applies the theme based on the state (True for dark, False for light).
            """
            style_manager = Adw.StyleManager.get_default()
            self.config.set_theme_preference(state)
            
            if state:
                # Set to dark theme
                style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
                fname = Gio.file_new_for_path('gtk_dark.css')
            else:
                # Set to light theme
                style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
                fname = Gio.file_new_for_path('gtk_light.css')

            # Reload CSS
            display = Gtk.Widget.get_display(self.window)
            provider = Gtk.CssProvider.new()
            provider.load_from_file(fname)
            Gtk.StyleContext.add_provider_for_display(display, provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

            # Update constants
            const.update_theme_constants(state)

            # Update button icon
            self._update_theme_button_icon(state)
            
            # Refresh UI by re-creating tabs
            self.refresh_tabs()

        def _update_theme_button_icon(self, is_dark):
            """Updates the icon of the theme toggle button."""
            if is_dark:
                self.theme_icon.set_from_icon_name("display-brightness-symbolic")
            else:
                self.theme_icon.set_from_icon_name("weather-clear-night-symbolic")


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
            style_manager = Adw.StyleManager.get_default()
            prefer_dark_theme = self.config.get_theme_preference()
            
            if prefer_dark_theme:
                style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
                fname = Gio.file_new_for_path('gtk_dark.css')
            else:
                style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
                fname = Gio.file_new_for_path('gtk_light.css')

            display = Gtk.Widget.get_display(self.window)
            provider.load_from_file(fname)
            Gtk.StyleContext.add_provider_for_display(display, provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            
            # Synchronize constants with the loaded preference
            const.update_theme_constants(prefer_dark_theme)
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

            icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
            icon_theme.add_search_path(os.path.abspath("../Images"))

            # Create the theme toggle button
            self.theme_button = Gtk.Button.new()
            self.theme_button.add_css_class("flat")
            self.theme_button.set_valign(Gtk.Align.CENTER)
            
            self.theme_icon = Gtk.Image.new()
            self._update_theme_button_icon(prefer_dark_theme)
            self.theme_button.set_child(self.theme_icon)
            
            # Connect the button's 'clicked' signal
            self.theme_button.connect("clicked", self._on_theme_button_clicked)

            # Create the save button
            self.save_button = Gtk.Button.new()
            self.save_button.add_css_class("flat")
            self.save_button.set_valign(Gtk.Align.CENTER)
            self.save_button.set_icon_name("document-save-symbolic")
            self.save_button.connect("clicked", self._on_save_button_clicked)

            # Create a box to hold the buttons
            header_buttons_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
            header_buttons_box.set_halign(Gtk.Align.END)
            header_buttons_box.set_valign(Gtk.Align.CENTER)
            header_buttons_box.append(self.save_button)
            header_buttons_box.append(self.theme_button)
            self.header_bar.pack_end(header_buttons_box)
            self.header_bar.set_title_widget(title_widget=self.switcher)

            # Create a main box to hold the header bar and the view stack
            main_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
            main_box.append(self.header_bar)
            main_box.append(self.view_stack)



            # Set the main box as the content of the window
            self.window.set_content(main_box)
            self.window.connect("close-request", quit)

            # Fix #4: Show the window immediately so the user sees it right
            # away, then kick off tab-building asynchronously.
            self.show_window()
            GLib.idle_add(self._start_loading_tabs)

        def refresh_tabs(self):
            """Clears and re-creates all tabs in the view stack."""
            # Remove all current children
            child = self.view_stack.get_first_child()
            while child:
                next_child = child.get_next_sibling()
                self.view_stack.remove(child)
                child = next_child
            # Re-show spinner and re-trigger async load
            self._start_loading_tabs()

        def _start_loading_tabs(self):
            """Show a loading spinner immediately, then build tabs in a background thread."""
            # Show a spinner page so the user sees *something* right away
            self._loading_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 12)
            self._loading_box.set_valign(Gtk.Align.CENTER)
            self._loading_box.set_halign(Gtk.Align.CENTER)
            self._loading_box.set_vexpand(True)

            spinner = Gtk.Spinner()
            spinner.set_size_request(48, 48)
            spinner.start()

            loading_label = Gtk.Label(label="Loading GPU information…")
            loading_label.add_css_class("dim-label")

            self._loading_box.append(spinner)
            self._loading_box.append(loading_label)
            self.view_stack.add_titled_with_icon(self._loading_box, "loading", "Loading", "system-run-symbolic")

            # Ensure the /tmp/gpu-viewer directory exists before threads start
            subprocess.Popen(Filenames.mkdir_output_command, stdout=subprocess.PIPE, shell=True).communicate()

            # Fix #2: Run all support checks in parallel, then build UI on main thread
            thread = threading.Thread(target=self._probe_and_build_tabs, daemon=True)
            thread.start()
            return False  # Do not repeat GLib.idle_add

        def _probe_and_build_tabs(self):
            """Run support checks in parallel (background thread), then schedule UI build."""
            # Fix #2: parallel support checks via ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    executor.submit(isVulkanSupported):   "vulkan",
                    executor.submit(isOpenglSupported):   "opengl",
                    executor.submit(isOpenclSupported):   "opencl",
                    executor.submit(isVdpauinfoSupported): "vdpau",
                }
                results = {}
                for future in as_completed(futures):
                    key = futures[future]
                    try:
                        results[key] = future.result()
                    except Exception as e:
                        print(f"Support check failed for {key}: {e}")
                        results[key] = False

            # Fix #1 & #6: vulkan-video check reuses the file written by isVulkanSupported
            results["vulkan_video"] = isVulkanVideoSupported() if results.get("vulkan") else False

            # Schedule the actual GTK widget construction back on the main thread
            GLib.idle_add(self._build_tabs_on_main_thread, results)

        def _build_tabs_on_main_thread(self, results):
            """Called on the GLib main thread — safe to create/modify GTK widgets."""
            # Remove the loading spinner page
            if hasattr(self, '_loading_box') and self._loading_box:
                self.view_stack.remove(self._loading_box)
                self._loading_box = None

            if results.get("vulkan"):
                vulkan_box = create_vulkan_tab_content(self)
                self.view_stack.add_titled_with_icon(vulkan_box, "page1", "Vulkan", "Vulkan")

            if results.get("opengl"):
                page2_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
                opengl_box = OpenGL(self, page2_box)
                self.view_stack.add_titled_with_icon(opengl_box, "page2", "OpenGL", "OpenGL")

            if results.get("opencl"):
                opencl_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
                opencl_content = openCL(self, opencl_box)
                self.view_stack.add_titled_with_icon(opencl_content, "opencl_page", "OpenCL", "OpenCL")

            if results.get("vulkan_video"):
                vulkan_video_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
                vulkan_video_content = VulkanVideo(vulkan_video_box)
                self.view_stack.add_titled_with_icon(vulkan_video_content, "vulkan_video_page", "Vulkan Video", "Vulkan-Video")

            if results.get("vdpau"):
                vdpau_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
                vdpau_content = vdpauinfo(vdpau_box)
                self.view_stack.add_titled_with_icon(vdpau_content, "vdpau_page", "VDPAU", "vdpauinfo")

            page3_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
            self.about_page_ui = about_page(page3_box)
            self.view_stack.add_titled_with_icon(page3_box, "page3", "About Us", "about-us")

            return False  # Do not repeat GLib.idle_add

        def show_window(self):
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
