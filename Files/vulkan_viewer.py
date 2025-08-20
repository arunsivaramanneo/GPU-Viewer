#
# A Gtk4 Libadwaita application to display Vulkan, OpenGL, and OpenCL information.
# This application is inspired by the functionality of GPU-Viewer.
#
# To run this, you will need:
# 1. Python 3.x
# 2. PyGObject (Gtk4 bindings)
# 3. Libadwaita 1.4 or newer
# 4. The `vulkaninfo` tool installed on your system.
# 5. psutil (for CPU/RAM stats): pip install psutil
# 6. An `images` folder containing `changelog.png`, `gpl.png`, `faq.png`, `bug.png`, `donate.png`, `github.png`, and `email.png`
#
# On Debian/Ubuntu/Fedora/etc., you can install the necessary packages with:
# sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1 vulkan-tools
#
# Run the application from your terminal:
# python3 your_script_name.py
#

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, GObject, Gio, Gdk
import subprocess
import os
import re
import json
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil library not found. Real-time CPU/RAM stats will not be displayed.")

def update_system_stats(self):
    """
    Updates the CPU, and RAM usage labels.
    This function is called periodically by a GLib timeout.
    """
    if PSUTIL_AVAILABLE and self.cpu_label and self.ram_label:
        # CPU and RAM usage as a percentage
        cpu_percent = psutil.cpu_percent(interval=None) # Non-blocking call
        ram_percent = psutil.virtual_memory().percent
        self.cpu_label.set_label(f"CPU: {cpu_percent}%")
        self.ram_label.set_label(f"RAM: {ram_percent}%")
        
    return True # Return True to keep the timeout running

def create_vulkan_sidebar(self):
    """
    Creates the sidebar for the Vulkan view with tabs based on JSON data.
    Returns the sidebar, content stack, and selection model.
    """
    # Updated the list of tabs to include "Surface" at the end
    sidebar_store = Gtk.StringList.new([
        "System Info", "Limits", "Properties", "Features", "Extensions", "Formats", "Memory Types", 
        "Memory Heaps", "Queues", "Instance Extensions", "Instance Layers", "Surface"
    ])

    selection_model = Gtk.SingleSelection.new(sidebar_store)
    selection_model.set_can_unselect(False)
    
    factory = Gtk.SignalListItemFactory.new()
    def on_setup(factory, list_item):
        label = Gtk.Label(xalign=0, hexpand=True)
        label.set_margin_top(10)
        label.set_margin_bottom(10)
        # Add padding to the start and end of the labels
        label.set_margin_start(10)
        label.set_margin_end(10)
        list_item.set_child(label)

    def on_bind(factory, list_item):
        label = list_item.get_child()
        label.set_label(list_item.get_item().get_string())

    # Corrected the function names in the connect calls
    factory.connect("setup", on_setup)
    factory.connect("bind", on_bind)
    
    list_view = Gtk.ListView(model=selection_model, factory=factory)

    # Wrap the list view in a scrolled window to enable scrolling
    scrolled_sidebar = Gtk.ScrolledWindow()
    scrolled_sidebar.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled_sidebar.set_child(list_view)
    
    vulkan_content_stack = Gtk.Stack.new()
    vulkan_content_stack.set_vexpand(True)
    vulkan_content_stack.set_hexpand(True)

    # Connect the sidebar selection to the content stack.
    def on_sidebar_selection_changed(selection, position, items):
        selected_item = selection.get_selected_item()
        if selected_item:
            title = selected_item.get_string()
            vulkan_content_stack.set_visible_child_name(title.replace(" ", "_").lower())
            print(f"Tab '{title}' was selected.")
    
    selection_model.connect("selection-changed", on_sidebar_selection_changed)
    
    selection_model.set_selected(0)
    
    vulkan_split_view = Adw.NavigationSplitView.new()
    vulkan_split_view.set_vexpand(True) # Added vertical expansion
    vulkan_split_view.set_sidebar(Adw.NavigationPage.new(scrolled_sidebar, "Vulkan Sub-Tabs"))
    vulkan_split_view.set_content(Adw.NavigationPage.new(vulkan_content_stack, "Vulkan Content"))

    return vulkan_split_view, vulkan_content_stack, selection_model

def on_device_selected(self, dropdown):
    """
    Callback for the device dropdown selection change.
    Updates the Vulkan content based on the selected device.
    """
    selected_index = dropdown.get_selected()
    print(f"Device at index {selected_index} selected.")
#    self._populate_vulkan_stack(self.vulkan_content_stack, selected_index)