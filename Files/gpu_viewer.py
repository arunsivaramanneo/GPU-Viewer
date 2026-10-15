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
from SummaryViewer import create_summary_page
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
    return len(clinfo_output) > 10 and clinfo_process.returncode == 0 and "Device Name" in clinfo_output

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
    
    def on_response(dialog, result, app):
        app.release()

    def show_message(app):
        app.hold()
        dialog = Gtk.AlertDialog()
        dialog.set_message('gpu-viewer is already running')
        dialog.set_detail('If you are unable to view the application, please run rm -r /tmp/gpu-viewer and run the application again')
        dialog.choose(None,None,on_response,app)

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
                    props = None
                    if hasattr(self, 'opencl_platforms') and self.opencl_platforms:
                        platform_idx = self.opencl_platform_dropdown.props.selected if hasattr(self, 'opencl_platform_dropdown') else 0
                        if platform_idx == Gtk.INVALID_LIST_POSITION:
                            platform_idx = 0
                        device_selected = self.opencl_devices_dropdown.props.selected if hasattr(self, 'opencl_devices_dropdown') else 0
                        if device_selected != Gtk.INVALID_LIST_POSITION:
                            device_idx = self.opencl_gpu_index_map[device_selected] if (hasattr(self, 'opencl_gpu_index_map') and len(self.opencl_gpu_index_map) > device_selected) else device_selected
                        else:
                            device_idx = 0
                        if opencl_tab == "platform-information":
                            if platform_idx < len(self.opencl_platforms):
                                props = self.opencl_platforms[platform_idx]["properties"]
                                default_name = "platform_details.txt"
                        elif hasattr(self, 'opencl_get_device_categories'):
                            cats = self.opencl_get_device_categories(platform_idx, device_idx)
                            if cats:
                                if opencl_tab == "device-information":
                                    props = cats["Device Information"]
                                    default_name = "device_details.txt"
                                elif opencl_tab == "device-extensions":
                                    props = cats["Device Extensions with Version"]
                                    default_name = "device_extensions.txt"
                                elif opencl_tab and (opencl_tab.startswith("device-memory") or "image" in opencl_tab):
                                    props = cats["Device Memory & Image Information"]
                                    default_name = "memory_and_image_details.txt"
                                elif opencl_tab and (opencl_tab.startswith("queue-capabilities") or "queue" in opencl_tab):
                                    props = cats["Queue & Execution Capabilities"]
                                    default_name = "queue_execution_details.txt"
                                elif opencl_tab == "device-vector-information":
                                    props = cats["Device Vector Information"]
                                    default_name = "vector_details.txt"
                    if props is not None:
                        temp_file = "/tmp/gpu-viewer/opencl_tab_output.txt"
                        try:
                            with open(temp_file, "w") as f:
                                for key, value, children in props:
                                    if value:
                                        f.write(f"{key}: {value}\n")
                                    else:
                                        f.write(f"{key}\n")
                                    for sub_key, sub_val in children:
                                        f.write(f"    {sub_key}: {sub_val}\n")
                            source_file = temp_file
                        except Exception as e:
                            print(f"Error writing temporary OpenCL file: {e}")

            elif visible_child_name == "vdpau_page":
                source_file = Filenames.vdpauinfo_output_file
                default_name = "vdpauinfo.txt"
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
            self.theme_button.set_sensitive(False)
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

            # Reload CSS cleanly by removing previous provider
            display = Gtk.Widget.get_display(self.window) if hasattr(self, 'window') and self.window else Gdk.Display.get_default()
            if hasattr(self, '_css_provider') and self._css_provider:
                try:
                    Gtk.StyleContext.remove_provider_for_display(display, self._css_provider)
                except Exception:
                    pass

            self._css_provider = Gtk.CssProvider.new()
            self._css_provider.load_from_file(fname)
            Gtk.StyleContext.add_provider_for_display(display, self._css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_USER)

            # Update constants
            const.update_theme_constants(state)

            # Update button icon
            if hasattr(self, 'theme_icon'):
                self._update_theme_button_icon(state)
            
            # Refresh UI by re-creating tabs
            if hasattr(self, 'view_stack'):
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

            # Set the application's default and minimum size
            width, height = getScreenSize()

            target_w = int(width * const.WIDTH_RATIO)
            target_h = int(height * const.HEIGHT_RATIO1)

            if int(width) > 2160 and int(height) < 1440:
                target_w = int(2160 * const.WIDTH_RATIO)
                target_h = int(height * const.HEIGHT_RATIO1)
            elif int(width) > 2160 and int(height) > 1440:
                target_w = int(2160 * const.WIDTH_RATIO)
                target_h = int(1440 * const.HEIGHT_RATIO1)

            target_w = max(target_w, 900)
            target_h = max(target_h, 650)

            self.window.set_default_size(target_w, target_h)
            self.window.set_size_request(750, 500)
    
            style_manager = Adw.StyleManager.get_default()
            prefer_dark_theme = self.config.get_theme_preference()
            
            if prefer_dark_theme:
                style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
                fname = Gio.file_new_for_path('gtk_dark.css')
            else:
                style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
                fname = Gio.file_new_for_path('gtk_light.css')

            display = Gtk.Widget.get_display(self.window)
            self._css_provider = Gtk.CssProvider.new()
            self._css_provider.load_from_file(fname)
            Gtk.StyleContext.add_provider_for_display(display, self._css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_USER)
            
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
            self.theme_button.set_sensitive(False)
            
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
            self.save_button.set_sensitive(False)
            self.save_button.connect("clicked", self._on_save_button_clicked)

            # Create the close-tab button (disabled for Summary and About Us)
            self.close_tab_button = Gtk.Button.new()
            self.close_tab_button.add_css_class("flat")
            self.close_tab_button.set_valign(Gtk.Align.CENTER)
            self.close_tab_button.set_icon_name("window-close-symbolic")
            self.close_tab_button.set_sensitive(False)
            def _on_close_tab_clicked(btn):
                visible = self.view_stack.get_visible_child_name()
                if not visible or visible in ("summary", "page3"):
                    return

                # Remove the currently visible child and return to summary.
                current = self.view_stack.get_visible_child()
                if current is not None:
                    self.view_stack.remove(current)

                # Allow the tab to be rebuilt later if reopened.
                if visible in self._inner_stacks:
                    del self._inner_stacks[visible]
                if visible in self._tab_built:
                    self._tab_built[visible] = False

                self.view_stack.set_visible_child_name("summary")
                if hasattr(self, 'close_tab_button') and self.close_tab_button:
                    self.close_tab_button.set_sensitive(False)
            self.close_tab_button.connect("clicked", _on_close_tab_clicked)

            self.summary_reorder_button = Gtk.Button.new()
            self.summary_reorder_button.add_css_class("flat")
            self.summary_reorder_button.set_valign(Gtk.Align.CENTER)
            self.summary_reorder_button.set_icon_name("view-list-symbolic")
            self.summary_reorder_button.set_tooltip_text("Reorder summary cards")
            self.summary_reorder_button.set_sensitive(False)

            def _show_summary_reorder_popover(button):
                flow_box = getattr(self, "summary_flow_box", None)
                if flow_box is None:
                    return
                registry = list(getattr(flow_box, "_summary_card_registry", []))
                if not registry:
                    return

                popover = Gtk.Popover.new()
                popover.set_parent(button)
                popover.set_position(Gtk.PositionType.BOTTOM)
                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
                box.set_margin_top(8)
                box.set_margin_bottom(8)
                box.set_margin_start(8)
                box.set_margin_end(8)

                header = Gtk.Label(label="Reorder cards")
                header.add_css_class("title-4")
                header.set_halign(Gtk.Align.START)
                box.append(header)

                list_box = Gtk.ListBox()
                list_box.set_selection_mode(Gtk.SelectionMode.NONE)

                def _refresh_summary_order_list():
                    child = list_box.get_first_child()
                    while child is not None:
                        next_child = child.get_next_sibling()
                        list_box.remove(child)
                        child = next_child

                    registry = list(getattr(flow_box, "_summary_card_registry", []))
                    for entry_card_id, widget in registry:
                        title = getattr(widget, "_summary_card_title", entry_card_id)
                        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                        row.set_margin_top(4)
                        row.set_margin_bottom(4)
                        row.set_margin_start(4)
                        row.set_margin_end(4)

                        label = Gtk.Label(label=title)
                        label.set_halign(Gtk.Align.START)
                        label.set_hexpand(True)
                        row.append(label)

                        up_button = Gtk.Button(icon_name="go-up-symbolic")
                        up_button.add_css_class("flat")
                        up_button.set_tooltip_text("Move up")
                        up_button.connect("clicked", lambda *_ , card_id=entry_card_id: _move_summary_card(card_id, -1, flow_box))
                        row.append(up_button)

                        down_button = Gtk.Button(icon_name="go-down-symbolic")
                        down_button.add_css_class("flat")
                        down_button.set_tooltip_text("Move down")
                        down_button.connect("clicked", lambda *_ , card_id=entry_card_id: _move_summary_card(card_id, 1, flow_box))
                        row.append(down_button)

                        list_box.append(row)

                def _move_summary_card(card_id, direction, flow_box):
                    registry = list(getattr(flow_box, "_summary_card_registry", []))
                    if not registry:
                        return
                    order = [entry_card_id for entry_card_id, _ in registry]
                    if card_id not in order:
                        return
                    index = order.index(card_id)
                    target = index + direction
                    if target < 0 or target >= len(order):
                        return
                    order[index], order[target] = order[target], order[index]
                    widget_map = {entry_card_id: widget for entry_card_id, widget in registry}
                    reordered = [(entry_card_id, widget_map[entry_card_id]) for entry_card_id in order]
                    flow_box.remove_all()
                    for _, widget in reordered:
                        flow_box.append(widget)
                    flow_box._summary_card_registry = reordered
                    if hasattr(self, "config"):
                        self.config.set_summary_card_order(order)
                    _refresh_summary_order_list()

                _refresh_summary_order_list()
                box.append(list_box)
                popover.set_child(box)
                popover.popup()

            self.summary_reorder_button.connect("clicked", _show_summary_reorder_popover)

            # Create a box to hold the buttons
            header_buttons_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
            header_buttons_box.set_halign(Gtk.Align.END)
            header_buttons_box.set_valign(Gtk.Align.CENTER)
            header_buttons_box.append(self.save_button)
            header_buttons_box.append(self.summary_reorder_button)

            # Refresh interval selector popover
            _interval_options = ["250 ms", "500 ms", "1 s", "2 s", "5 s"]
            self._refresh_interval_values = [250, 500, 1000, 2000, 5000]
            current_interval = self.config.get_refresh_interval()
            try:
                _current_idx = self._refresh_interval_values.index(current_interval)
            except ValueError:
                _current_idx = 2
            self._current_refresh_interval_ms = current_interval

            interval_string_list = Gtk.StringList.new(_interval_options)
            self._interval_dropdown = Gtk.DropDown.new(interval_string_list, None)
            self._interval_dropdown.set_selected(_current_idx)

            interval_pop_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            interval_pop_box.set_margin_top(10)
            interval_pop_box.set_margin_bottom(10)
            interval_pop_box.set_margin_start(12)
            interval_pop_box.set_margin_end(12)
            interval_lbl = Gtk.Label(label="Stats Refresh Interval")
            interval_lbl.add_css_class("caption-heading")
            interval_lbl.set_halign(Gtk.Align.START)
            interval_pop_box.append(interval_lbl)
            interval_pop_box.append(self._interval_dropdown)

            interval_popover = Gtk.Popover()
            interval_popover.set_child(interval_pop_box)

            self.refresh_menu_button = Gtk.MenuButton()
            self.refresh_menu_button.set_icon_name("media-playlist-repeat-symbolic")
            self.refresh_menu_button.add_css_class("flat")
            self.refresh_menu_button.set_valign(Gtk.Align.CENTER)
            self.refresh_menu_button.set_tooltip_text("Set stats refresh interval")
            self.refresh_menu_button.set_popover(interval_popover)
            self.refresh_menu_button.set_sensitive(False)

            def _on_interval_selected(dropdown, _pspec):
                idx = dropdown.get_selected()
                if 0 <= idx < len(self._refresh_interval_values):
                    ms = self._refresh_interval_values[idx]
                    self.config.set_refresh_interval(ms)
                    self._current_refresh_interval_ms = ms
            self._interval_dropdown.connect("notify::selected", _on_interval_selected)

            # Search toggle button
            self.search_toggle = Gtk.ToggleButton()
            self.search_toggle.set_icon_name("system-search-symbolic")
            self.search_toggle.add_css_class("flat")
            self.search_toggle.set_valign(Gtk.Align.CENTER)
            self.search_toggle.set_tooltip_text("Search summary properties (Ctrl+F)")
            self.search_toggle.set_sensitive(False)

            header_buttons_box.append(self.refresh_menu_button)
            header_buttons_box.append(self.search_toggle)
            header_buttons_box.append(self.theme_button)
            self.header_bar.pack_end(header_buttons_box)
            self.header_bar.set_title_widget(title_widget=self.switcher)

            # Search bar
            self.search_entry = Gtk.SearchEntry()
            self.search_entry.set_placeholder_text("Filter summary properties…")
            self.search_entry.set_hexpand(True)

            self.search_bar = Gtk.SearchBar()
            self.search_bar.set_child(self.search_entry)
            self.search_bar.set_show_close_button(True)
            self.search_bar.connect_entry(self.search_entry)

            def _on_search_toggle(btn):
                self.search_bar.set_search_mode(btn.get_active())
                if not btn.get_active():
                    self.search_entry.set_text("")
                    self._apply_summary_search("")
            self.search_toggle.connect("toggled", _on_search_toggle)

            def _on_search_bar_mode_changed(bar, _pspec):
                self.search_toggle.set_active(bar.get_search_mode())
            self.search_bar.connect("notify::search-mode-enabled", _on_search_bar_mode_changed)

            def _on_search_changed(entry):
                visible = self.view_stack.get_visible_child_name()
                if visible == "summary":
                    self._apply_summary_search(entry.get_text())
            self.search_entry.connect("search-changed", _on_search_changed)

            # Keyboard shortcut Ctrl+F
            key_ctrl = Gtk.EventControllerKey.new()
            def _on_key_pressed(controller, keyval, keycode, state):
                if keyval == Gdk.KEY_f and (state & Gdk.ModifierType.CONTROL_MASK):
                    visible = self.view_stack.get_visible_child_name()
                    if visible == "summary":
                        self.search_bar.set_search_mode(True)
                        self.search_entry.grab_focus()
                        return True
                if keyval == Gdk.KEY_Escape and self.search_bar.get_search_mode():
                    self.search_bar.set_search_mode(False)
                    return True
                return False
            key_ctrl.connect("key-pressed", _on_key_pressed)
            self.window.add_controller(key_ctrl)

            # Create a main box to hold the header bar and the view stack
            main_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
            main_box.append(self.header_bar)
            main_box.append(self.search_bar)
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

            # If the parallel probe missed OpenCL but a clinfo output file
            # exists with device information, treat OpenCL as available so
            # the OpenCL tab can be registered and opened from Summary.
            try:
                if not results.get("opencl"):
                    clout_lines = copyContentsFromFile(Filenames.opencl_output_file)
                    clout = "\n".join(clout_lines) if isinstance(clout_lines, (list, tuple)) else str(clout_lines)
                    if len(clout) > 10 and "Device Name" in clout:
                        results["opencl"] = True
            except Exception:
                pass

            # Fix #1 & #6: vulkan-video check reuses the file written by isVulkanSupported
            results["vulkan_video"] = isVulkanVideoSupported() if results.get("vulkan") else False

            # Schedule the actual GTK widget construction back on the main thread
            GLib.idle_add(self._build_tabs_on_main_thread, results)

        def _build_tabs_on_main_thread(self, results):
            """Called on the GLib main thread — safe to create/modify GTK widgets.

            Each tab is immediately added to the outer ViewStack with a fixed inner
            Gtk.Stack that starts on its "spinner" child.  When the real content is
            ready the inner stack simply switches to its "content" child — the outer
            ViewStack page never moves, so tabs never jump or reorder.
            """
            # Debug: print probe results for troubleshooting OpenCL tab
            pass

            # Remove the global loading spinner page
            if hasattr(self, '_loading_box') and self._loading_box:
                self.view_stack.remove(self._loading_box)
                self._loading_box = None

            self._tab_built = {}          # page_name → bool
            self._inner_stacks = {}       # page_name → inner Gtk.Stack
            self._available_tab_builders = {}

            def _make_placeholder(label_text):
                """Centred spinner displayed until the real content arrives."""
                box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 12)
                box.set_valign(Gtk.Align.CENTER)
                box.set_halign(Gtk.Align.CENTER)
                box.set_vexpand(True)
                sp = Gtk.Spinner()
                sp.set_size_request(36, 36)
                sp.start()
                lbl = Gtk.Label(label=f"Loading {label_text}…")
                lbl.add_css_class("dim-label")
                box.append(sp)
                box.append(lbl)
                return box, sp  # return spinner ref so we can stop it later

            def _register_tab(page_name, title, icon, builder):
                """Add a stable ViewStack page with an inner stack (spinner + content)."""
                inner = Gtk.Stack()
                inner.set_vexpand(True)
                inner.set_hexpand(True)
                # Disable transition animation inside the inner stack
                inner.set_transition_type(Gtk.StackTransitionType.NONE)

                placeholder, spinner_widget = _make_placeholder(title)
                inner.add_named(placeholder, "spinner")
                # "content" child is added later by _reveal_content

                # The outer ViewStack page wraps the inner stack — it never moves
                self.view_stack.add_titled_with_icon(inner, page_name, title, icon)
                self._inner_stacks[page_name] = (inner, spinner_widget)
                self._tab_built[page_name] = False

            def _build_tab_async(page_name):
                """Build tab widgets on the main thread to avoid GTK thread issues."""
                builder = self._tab_builders[page_name]
                def _build_on_main():
                    real_widget = builder()
                    return _reveal_content(page_name, real_widget)
                GLib.idle_add(_build_on_main)

            def _reveal_content(page_name, real_widget):
                """Swap spinner → real content inside the inner stack (main thread)."""
                entry = self._inner_stacks.get(page_name)
                if entry is None:
                    return False
                inner, spinner_widget = entry
                inner.add_named(real_widget, "content")
                inner.set_visible_child_name("content")
                # Stop the spinner to free resources
                spinner_widget.stop()
                self._tab_built[page_name] = True
                return False  # Don't repeat

            # Keep builder callables in a separate dict (needed by _build_tab_async)
            self._tab_builders = {}

            def _register(page_name, title, icon, builder):
                self._tab_builders[page_name] = builder
                _register_tab(page_name, title, icon, builder)

            def _register_available(page_name, title, icon, builder):
                self._tab_builders[page_name] = builder
                self._available_tab_builders[page_name] = (title, icon, builder)

            def _register_summary():
                def _build_summary():
                    return create_summary_page(self, results)
                _register("summary", "Summary", "view-list-symbolic", _build_summary)

            _register_summary()

            # Register all supported tabs immediately so they appear in the header bar.
            if results.get("vulkan"):
                _register("page1", "Vulkan", "Vulkan",
                          lambda: create_vulkan_tab_content(self))

            if results.get("vulkan_video"):
                def _build_vulkan_video():
                    box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
                    return VulkanVideo(box)
                _register("vulkan_video_page", "Vulkan Video", "Vulkan-Video", _build_vulkan_video)

            if results.get("opengl"):
                def _build_opengl():
                    box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
                    return OpenGL(self, box)
                _register("page2", "OpenGL", "OpenGL", _build_opengl)

            if results.get("opencl"):
                def _build_opencl():
                    box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
                    return openCL(self, box)
                _register("opencl_page", "OpenCL", "OpenCL", _build_opencl)

            if results.get("vdpau"):
                def _build_vdpau():
                    box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
                    return vdpauinfo(box)
                _register("vdpau_page", "VDPAU", "vdpauinfo", _build_vdpau)

            # About page has no subprocesses — build immediately
            page3_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
            self.about_page_ui = about_page(page3_box)
            self._about_page_box = page3_box  # keep reference for tab reordering
            self.view_stack.add_titled_with_icon(page3_box, "page3", "About Us", "about-us")

            # ---- Trigger a lazy build whenever the visible tab changes ----
            def _on_visible_child_changed(stack, _pspec):
                name = stack.get_visible_child_name()
                if name and not self._tab_built.get(name, True) and name in self._tab_builders:
                    self._tab_built[name] = True   # prevent double-build
                    _build_tab_async(name)

                # Enable save button only for API detail tabs (not Summary or About)
                if hasattr(self, 'save_button') and self.save_button:
                    self.save_button.set_sensitive(name not in ("summary", "page3"))

                if hasattr(self, 'summary_reorder_button'):
                    self.summary_reorder_button.set_sensitive(name == "summary")

                if hasattr(self, 'refresh_menu_button'):
                    self.refresh_menu_button.set_sensitive(name == "summary")

                if hasattr(self, 'search_toggle'):
                    self.search_toggle.set_sensitive(name == "summary")

                # Hide search bar when not on summary tab
                if hasattr(self, 'search_bar') and name != "summary":
                    self.search_bar.set_search_mode(False)
                    if hasattr(self, 'search_entry'):
                        self.search_entry.set_text("")
                    self._apply_summary_search("")

            self.view_stack.connect("notify::visible-child", _on_visible_child_changed)

            # Manually trigger the button state update for the initial visible child (Summary)
            # since the signal may not fire when the view_stack is initially configured
            GLib.idle_add(lambda: _on_visible_child_changed(self.view_stack, None))

            def open_tab(page_name, gpu_index=None):
                # Store GPU pre-selection request for Vulkan/OpenCL viewers to read
                self._pending_gpu_index = gpu_index
                # All tabs are already in the view_stack — just switch to the requested one.
                if page_name in self._inner_stacks:
                    self.view_stack.set_visible_child_name(page_name)

            self.open_tab = open_tab

            # Build the first tab automatically if it is registered
            first = self.view_stack.get_visible_child_name()
            if first and not self._tab_built.get(first, True):
                self._tab_built[first] = True
                _build_tab_async(first)

            if hasattr(self, 'theme_button') and self.theme_button:
                self.theme_button.set_sensitive(True)
            if hasattr(self, 'search_toggle') and self.search_toggle:
                self.search_toggle.set_sensitive(True)
            if hasattr(self, 'refresh_menu_button') and self.refresh_menu_button:
                self.refresh_menu_button.set_sensitive(True)

            return False  # Do not repeat GLib.idle_add

        def _apply_summary_search(self, query: str):
            """Show/hide property rows in summary cards based on search query."""
            flow_box = getattr(self, "summary_flow_box", None)
            if flow_box is None:
                return
            query_lower = query.strip().lower()

            fb_child = flow_box.get_first_child()
            while fb_child is not None:
                card_frame = fb_child.get_child() if hasattr(fb_child, "get_child") else fb_child.get_first_child()
                if card_frame is not None:
                    card_title = getattr(card_frame, "_summary_card_title", "").lower()
                    if query_lower and query_lower in card_title:
                        self._set_widget_tree_visible(card_frame)
                        fb_child.set_visible(True)
                    else:
                        any_visible = self._search_card(card_frame, query_lower)
                        fb_child.set_visible(not query_lower or any_visible)
                fb_child = fb_child.get_next_sibling()

        def _search_card(self, card_widget, query_lower: str) -> bool:
            """Walk card widget tree, show/hide action rows. Return True if any row matched."""
            if not query_lower:
                self._set_widget_tree_visible(card_widget)
                return True
            card_box = card_widget.get_child() if hasattr(card_widget, "get_child") else None
            if card_box is None:
                return True
            any_match = False
            child = card_box.get_first_child()
            while child is not None:
                if self._search_widget(child, query_lower):
                    any_match = True
                child = child.get_next_sibling()
            return any_match

        def _search_widget(self, widget, query_lower: str) -> bool:
            """Recursively find _make_action_row boxes matching query."""
            if isinstance(widget, Gtk.Box) and hasattr(widget, "subtitle_labels"):
                title_text = ""
                inner = widget.get_first_child()
                if inner is not None and isinstance(inner, Gtk.Box):
                    t_lbl = inner.get_first_child()
                    if t_lbl and hasattr(t_lbl, "get_label"):
                        title_text = t_lbl.get_label().lower()
                elif inner is not None and hasattr(inner, "get_label"):
                    title_text = inner.get_label().lower()

                value_texts = " ".join(
                    lbl.get_label().lower() for lbl in widget.subtitle_labels
                    if hasattr(lbl, "get_label")
                )
                matched = query_lower in title_text or query_lower in value_texts
                widget.set_visible(matched)
                return matched

            any_match = False
            child = widget.get_first_child()
            while child is not None:
                if self._search_widget(child, query_lower):
                    any_match = True
                child = child.get_next_sibling()
            return any_match

        def _set_widget_tree_visible(self, widget):
            """Recursively restore visibility of all action row boxes."""
            if isinstance(widget, Gtk.Box) and hasattr(widget, "subtitle_labels"):
                widget.set_visible(True)
                return
            child = widget.get_first_child()
            while child is not None:
                self._set_widget_tree_visible(child)
                child = child.get_next_sibling()

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
