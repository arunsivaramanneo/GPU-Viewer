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

# Data model for the ColumnView
# Each row in the ColumnView will be a DataRow object.
class DataRow(GObject.Object):
    def __init__(self, key, value):
        super().__init__()
        self.key = key
        self.value = value

    @GObject.Property(type=str)
    def key_text(self):
        return self.key

    @GObject.Property(type=str)
    def value_text(self):
        return self.value

# A specialized data model for the Instance Layers tab
class InstanceLayerDataRow(GObject.Object):
    def __init__(self, layer_name, spec_version, impl_version, description, extension_count):
        super().__init__()
        self.layer_name = layer_name
        self.spec_version = spec_version
        self.impl_version = impl_version
        self.description = description
        self.extension_count = extension_count

    @GObject.Property(type=str)
    def layer_name_text(self):
        return self.layer_name

    @GObject.Property(type=str)
    def spec_version_text(self):
        return self.spec_version

    @GObject.Property(type=str)
    def impl_version_text(self):
        return self.impl_version

    @GObject.Property(type=str)
    def description_text(self):
        return self.description

    @GObject.Property(type=str)
    def extension_count_text(self):
        return str(self.extension_count)


class GPUInfoApp(Adw.Application):
    """
    Main application class for the GPU Info Viewer.
    """
    def __init__(self, **kwargs):
        super().__init__(application_id="com.example.gpuviewer", **kwargs)
        self.connect('activate', self.on_activate)
        self.vulkan_data = {}
        # Define the path for the configuration file
        self.config_dir = os.path.join(GLib.get_user_config_dir(), 'gpu-viewer')
        self.config_file = os.path.join(self.config_dir, 'config.json')
        self.cpu_label = None
        self.ram_label = None

    def run_command(self, command):
        """
        Executes a shell command and returns its output.
        If the command fails, returns a formatted error string.
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                shell=True,
                timeout=20
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error: Command '{command}' failed with:\n{e.stderr}"
        except FileNotFoundError:
            return f"Error: Command '{command}' not found. Please ensure it's installed."
        except subprocess.TimeoutExpired:
            return f"Error: Command '{command}' timed out."

    def create_column_view(self, data):
        """
        Creates a new Gtk.ColumnView populated with key-value data,
        including a search bar for filtering at the bottom.
        """
        # Create a vertical box to hold the list view and the search bar
        view_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 6)
        
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        # Enable horizontal scrolling
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        list_store = Gio.ListStore.new(DataRow.__gtype__)
        for key, value in data:
            list_store.append(DataRow(str(key), str(value)))

        # Create the search entry
        search_entry = Gtk.SearchEntry()
        search_entry.set_placeholder_text("Search...")
        
        # Create a custom filter that will search both columns.
        # We pass the search entry as user_data so the filter can access its text.
        custom_filter = Gtk.CustomFilter.new(lambda item, user_data: (
            user_data.get_text().lower() in item.key_text.lower() or
            user_data.get_text().lower() in item.value_text.lower()
        ), search_entry)
        
        # Create a FilterListModel to apply the filter
        filter_model = Gtk.FilterListModel.new(list_store, custom_filter)
        
        selection_model = Gtk.NoSelection.new(filter_model)
        column_view = Gtk.ColumnView.new(selection_model)
        column_view.set_vexpand(True)
        column_view.set_hexpand(True)
        
        # Enable gridlines for the rows and columns
        column_view.set_show_row_separators(True)

        property_factory = Gtk.SignalListItemFactory.new()
        def property_setup(factory, list_item):
            list_item.set_child(Gtk.Label(xalign=0))
        def property_bind(factory, list_item):
            label = list_item.get_child()
            label.set_label(list_item.get_item().key_text)
        property_factory.connect("setup", property_setup)
        property_factory.connect("bind", property_bind)
        
        value_factory = Gtk.SignalListItemFactory.new()
        def value_setup(factory, list_item):
            # To enable horizontal scrolling, the label should not wrap text.
            label = Gtk.Label(xalign=0)
            list_item.set_child(label)
        def value_bind(factory, list_item):
            label = list_item.get_child()
            label.set_label(list_item.get_item().value_text)
        value_factory.connect("setup", value_setup)
        value_factory.connect("bind", value_bind)

        property_column = Gtk.ColumnViewColumn.new("Property", property_factory)
        # Change to set_expand(True) to make the columns equally spaced
        property_column.set_expand(True)
        property_column.set_resizable(True)

        value_column = Gtk.ColumnViewColumn.new("Value", value_factory)
        value_column.set_expand(True)
        value_column.set_resizable(True)

        column_view.append_column(property_column)
        column_view.append_column(value_column)
        
        scrolled_window.set_child(column_view)
        
        # Place the search entry at the top, before the main view.
        view_box.append(search_entry)
        
        view_box.append(scrolled_window)
        
        # Define a separate function to handle the signal.
        # Using *args is a robust way to handle potential extra arguments from the signal.
        def on_search_entry_changed(search_entry, *args):
            custom_filter.changed()
        
        # Connect the search entry's 'search-changed' signal to our new function.
        search_entry.connect('search-changed', on_search_entry_changed)
        
        return view_box
    
    def create_instance_layers_view(self, instance_layers_data):
        """
        Creates a new Gtk.ColumnView with 5 columns for instance layers,
        including a search bar for filtering.
        """
        view_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 6)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        list_store = Gio.ListStore.new(InstanceLayerDataRow.__gtype__)
        for layer in instance_layers_data:
            # Safely get properties and handle missing keys
            layer_name = layer.get("layerName", "N/A")
            spec_version = layer.get("specVersion", "N/A")
            impl_version = str(layer.get("implementationVersion", "N/A"))
            description = layer.get("description", "N/A")
            
            # Count extensions if they exist
            extension_count = 0
            if 'deviceExtensions' in layer and layer['deviceExtensions'] is not None:
                extension_count += len(layer['deviceExtensions'])
            if 'instanceExtensions' in layer and layer['instanceExtensions'] is not None:
                extension_count += len(layer['instanceExtensions'])
            
            list_store.append(InstanceLayerDataRow(layer_name, spec_version, impl_version, description, extension_count))

        search_entry = Gtk.SearchEntry()
        search_entry.set_placeholder_text("Search...")

        custom_filter = Gtk.CustomFilter.new(lambda item, user_data: (
            user_data.get_text().lower() in item.layer_name_text.lower() or
            user_data.get_text().lower() in item.spec_version_text.lower() or
            user_data.get_text().lower() in item.impl_version_text.lower() or
            user_data.get_text().lower() in item.description_text.lower() or
            user_data.get_text().lower() in item.extension_count_text.lower()
        ), search_entry)

        filter_model = Gtk.FilterListModel.new(list_store, custom_filter)
        selection_model = Gtk.NoSelection.new(filter_model)
        column_view = Gtk.ColumnView.new(selection_model)
        column_view.set_vexpand(True)
        column_view.set_hexpand(True)
        column_view.set_show_row_separators(True)
        column_view.set_show_column_separators(True)

        def create_column(title, property_name):
            factory = Gtk.SignalListItemFactory.new()
            def setup(factory, list_item):
                list_item.set_child(Gtk.Label(xalign=0, ellipsize=Gtk.EllipsizeMode.END))
            def bind(factory, list_item):
                label = list_item.get_child()
                label.set_label(getattr(list_item.get_item(), f"{property_name}_text"))
            factory.connect("setup", setup)
            factory.connect("bind", bind)
            column = Gtk.ColumnViewColumn.new(title, factory)
            column.set_resizable(True)
            # Make sure all columns expand equally
            column.set_expand(True)
            return column

        column_view.append_column(create_column("Layer Name", "layer_name"))
        column_view.append_column(create_column("Spec Version", "spec_version"))
        column_view.append_column(create_column("Impl Version", "impl_version"))
        column_view.append_column(create_column("Description", "description"))
        column_view.append_column(create_column("Extension Count", "extension_count"))

        scrolled_window.set_child(column_view)
        view_box.append(search_entry)
        view_box.append(scrolled_window)

        def on_search_entry_changed(search_entry, *args):
            custom_filter.changed()
        search_entry.connect('search-changed', on_search_entry_changed)

        return view_box
    
    def _populate_vulkan_stack(self, vulkan_content_stack, device_index):
        """
        Populates the Gtk.Stack for the Vulkan content with data for the given device index.
        """
        # Clear existing pages from the stack by iterating over the pages and removing them.
        for page in list(vulkan_content_stack.get_pages()):
            vulkan_content_stack.remove(page.get_child())
        
        # Get the selected physical device info.
        device = self.vulkan_data['devices'][device_index] if len(self.vulkan_data['devices']) > device_index else {'properties': {'limits': {}}, 'features': {}, 'memoryProperties': {'memoryTypes': [], 'memoryHeaps': []}, 'queueProperties': [], 'extensions': [], 'formats': [], 'surface': {}}

        # Prepare data for all tabs based on the selected device.
        # This dictionary is what drives the content for the sub-tabs.
        tabs = {
            "System Info": [
                ("Vulkan Instance Version", self.vulkan_data.get('vulkanInstanceVersion', 'N/A')),
                ("Total Instance Extensions", len(self.vulkan_data.get('instanceExtensions', []))),
                ("Total Instance Layers", len(self.vulkan_data.get('instanceLayers', []))),
                ("Device Name", device.get('deviceName', 'N/A')),
                ("Device Type", device['properties'].get('deviceType', 'N/A'))
            ],
            "Limits": [(key, value) for key, value in device['properties']['limits'].items()],
            "Properties": [(key, value) for key, value in device['properties'].items() if key != 'limits'],
            "Features": [(key, value) for key, value in device['features'].items()],
            "Extensions": [(ext['extensionName'], f"Version: {ext['specVersion']}") for ext in device.get('extensions', [])],
            "Formats": [(f['format'], f'Flags: {f.get("formatFlags", "N/A")}, Properties: {f.get("formatProperties", "N/A")}') for f in device.get('formats', [])],
            "Memory Types": [(f"Memory Type {i}", m) for i, m in enumerate(device['memoryProperties']['memoryTypes'])],
            "Memory Heaps": [(f"Memory Heap {i}", m) for i, m in enumerate(device['memoryProperties']['memoryHeaps'])],
            "Queues": [(f"Queue Family {i}", q) for i, q in enumerate(device['queueProperties'])],
            "Instance Extensions": [(ext['extensionName'], f"Version: {ext['specVersion']}") for ext in self.vulkan_data['instanceExtensions']],
            "Instance Layers": self.vulkan_data['instanceLayers'], # This is the raw data now
            # Added a new key for the Surface tab
            "Surface": []
        }
        
        # Add surface formats and present modes to the Surface tab data
        surface_data = []
        if 'surface' in device and device['surface'] is not None:
            if 'formats' in device['surface'] and device['surface']['formats'] is not None:
                surface_data.append(("--- Surface Formats ---", ""))
                for fmt in device['surface']['formats']:
                    surface_data.append((fmt.get('format', 'N/A'), fmt.get('colorSpace', 'N/A')))
            if 'presentModes' in device['surface'] and device['surface']['presentModes'] is not None:
                surface_data.append(("--- Present Modes ---", ""))
                for mode in device['surface']['presentModes']:
                    surface_data.append((mode, ""))
        tabs["Surface"] = surface_data

        # Populate the content stack with the views
        for name, data in tabs.items():
            if name == "Instance Layers":
                view = self.create_instance_layers_view(data)
            else:
                view = self.create_column_view(data)
            vulkan_content_stack.add_titled(view, name.replace(" ", "_").lower(), name)

    def create_vulkan_sidebar(self, vulkan_data):
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
    
    def on_stack_page_changed(self, stack, prop):
        """
        Handles the visibility of the sidebar toggle button based on the active tab
        and updates the active button in our custom tab bar.
        """
        current_child_name = stack.get_visible_child_name()
        
        # Update the visual state of our custom buttons
        for button, name in self.custom_tabs.items():
            if name == current_child_name:
                button.add_css_class("selected")
            else:
                button.remove_css_class("selected")

    def create_tab_button(self, text, icon_name):
        """
        Helper function to create a button with an icon and text.
        """
        button = Gtk.Button.new()
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        image = Gtk.Image.new_from_icon_name(icon_name)
        label = Gtk.Label(label=text)
        box.append(image)
        box.append(label)
        button.set_child(box)
        return button
    
    def on_device_selected(self, dropdown, param):
        """
        Callback for the device dropdown selection change.
        Updates the Vulkan content based on the selected device.
        """
        selected_index = dropdown.get_selected()
        print(f"Device at index {selected_index} selected.")
        self._populate_vulkan_stack(self.vulkan_content_stack, selected_index)

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

    def create_about_page(self):
        """
        Creates the 'About' page content with information from the provided file.
        """
        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 12)
        box.set_halign(Gtk.Align.START)
        box.set_valign(Gtk.Align.START)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        # Get the path to the images folder relative to the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_dir = os.path.join(script_dir, "images")
        
        # The content from the provided file
        about_content_markdown = """
**Copyright © 2017-2025 Arun Sivaraman** (<a href="mailto:arunsivaramanneo@gmail.com">arunsivaramanneo@gmail.com</a>)

**GPU Viewer is a FREE SOFTWARE: This program comes with ABSOLUTELY NO WARRANTY.**
You can redistribute it and/or modify it under the terms of the GNU General Public license as published by the free software Foundation, either version 3 of the license, or (at your Option) any later version.
Click on the GPLv3 Icon below to view the License

This project is developed as a basic front-end UI for the command-line outputs of glxinfo, vulkaninfo, clinfo,es2_info and vdpauinfo.
The application helps in viewing/navigating the OpenGL, Vulkan, OpenCL, EGL and VDPAU Information in ease over command-line.

Please do note that this project does not use any OpenGL,Vulkan or OpenCL programming languages. The entire application works as a wrapper on the glxinfo, vulkaninfo, clinfo, es2_info and vdpauinfo output.

The latest source code of this program can be found at
<a href="https://github.com/arunsivaramanneo/GPU-Viewer">**https://github.com/arunsivaramanneo/GPU-Viewer**</a>

This program uses:
    - python 3 or higher
    - GTK4+ and libadwaita for the graphical user interface
    - The below commands are used to fetch the report
        - glxinfo(OpenGL Information)
        - vulkaninfo(Vulkan Information)
        - clinfo(OpenCL Information)
        - es2_info(EGL Information)
        - vdpauinfo(VDPAU Information) (Note : Supported only on x11/Xwayland)
        - lscpu (CPU information)
        - lsb_release (Distro Information)
        - XDG_CURRENT_DESKTOP (Desktop Information)
        - XDG_SESSION_TYPE (Windowing System Information)
        - cat /proc/meminfo | awk '/Mem/' (Memory information)
        - uname -r (Kernel Information)

If you find the project interesting enough, please consider making a <a href="https://www.paypal.com/donate/?hosted_button_id=7M3PMM78FBR4Q">**DONATION**</a>.
Even a small one would mean the world to me. More than a mere financial act, donate means that you simply believe in this project and want it to be better.

Trademarks
    - OpenGL® and the oval logo are trademarks or registered trademarks of Hewlett Packard Enterprise in the United States and/or other countries worldwide.
    - OpenGL is a registered trademark and the OpenGL ES logo is a trademark of Hewlett Packard Enterprise used by permission by Khronos.
    - EGL and the EGL logo are trademarks of the Khronos Group Inc.
    - Vulkan and the Vulkan logo are registered trademarks of the Khronos Group Inc.
    - OpenCL and the OpenCL logo are trademarks of Apple Inc. used by permission by Khronos.
    - Intel and the Intel logo are trademarks of Intel Corporation or its subsidiaries in the U.S. and/or other countries.
    - NVIDIA and NVIDIA logo are trademarks and/or registered trademarks of NVIDIA Corporation in the U.S. and/or other countries.
    - AMD and AMD logo are trademarks or registered trademark of AMD
    - GITHUB®, the GITHUB® logo design, OCTOCAT® and the OCTOCAT® logo design are exclusive trademarks registered in the United States by GitHub, Inc.
    - Fedora®, the Fedora word design, the Infinity design logo, Fedora Remix, and the Fedora Remix word design, either separately or in combination, are hereinafter referred to as "Fedora Trademarks" and are trademarks of Red Hat, Inc.
        """
        
        # Use Gtk.Label to display the text
        title_label = Gtk.Label(label="<b>About GPU-VIEWER 4.0</b>", use_markup=True)
        title_label.add_css_class("title-1") # Use Adwaita title style
        title_label.set_halign(Gtk.Align.CENTER) # Center the heading
        
        # Use a single Gtk.Label for the entire content from the file
        info_label = Gtk.Label()
        # The file content contains HTML tags and links, so we'll use use_markup=True
        info_label.set_markup(about_content_markdown)
        info_label.set_wrap(True)
        info_label.set_justify(Gtk.Justification.LEFT) # Left-justify the body text
        
        # Create a horizontal box to hold the link buttons
        link_button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 12)
        link_button_box.set_halign(Gtk.Align.START) # Align the button box to the left
        link_button_box.set_margin_top(20)

        # Create each of the link buttons with a URI and icon
        changelog_button = Gtk.LinkButton.new_with_label("https://github.com/arunsivaramanneo/GPU-Viewer/releases", "Change Log")
        changelog_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        changelog_box.append(Gtk.Image.new_from_file(os.path.join(image_dir, "Changelog.png")))
        changelog_box.append(Gtk.Label(label="Change Log"))
        changelog_button.set_child(changelog_box)
        
        gpl_button = Gtk.LinkButton.new_with_label("https://www.gnu.org/licenses/gpl-3.0-standalone.html", "GPLv3")
        gpl_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        gpl_box.append(Gtk.Image.new_from_file(os.path.join(image_dir, "gpl.png")))
        gpl_box.append(Gtk.Label(label="GPLv3"))
        gpl_button.set_child(gpl_box)

        faq_button = Gtk.LinkButton.new_with_label("https://github.com/arun-v-nair/GPU-Viewer/blob/master/FAQ.md", "FAQ")
        faq_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        faq_box.append(Gtk.Image.new_from_file(os.path.join(image_dir, "faq.png")))
        faq_box.append(Gtk.Label(label="FAQ"))
        faq_button.set_child(faq_box)

        bug_button = Gtk.LinkButton.new_with_label("https://github.com/arun-v-nair/GPU-Viewer/issues", "Bug")
        bug_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        bug_box.append(Gtk.Image.new_from_file(os.path.join(image_dir, "bug.png")))
        bug_box.append(Gtk.Label(label="Bug"))
        bug_button.set_child(bug_box)

        # CORRECTED LINE: new_from_from_file -> new_from_file
        donate_button = Gtk.LinkButton.new_with_label("https://www.paypal.com/donate/?hosted_button_id=7M3PMM78FBR4Q", "Donate")
        donate_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        donate_box.append(Gtk.Image.new_from_file(os.path.join(image_dir, "Donate.png")))
        donate_box.append(Gtk.Label(label="Donate"))
        donate_button.set_child(donate_box)

        github_button = Gtk.LinkButton.new_with_label("https://github.com/arunsivaramanneo/GPU-Viewer", "GitHub")
        github_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        github_box.append(Gtk.Image.new_from_file(os.path.join(image_dir, "github.png")))
        github_box.append(Gtk.Label(label="GitHub"))
        github_button.set_child(github_box)
        
        email_button = Gtk.LinkButton.new_with_label("mailto:arun.v.nair@icloud.com", "Email Us")
        email_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        email_box.append(Gtk.Image.new_from_file(os.path.join(image_dir, "email.png")))
        email_box.append(Gtk.Label(label="Email Us"))
        email_button.set_child(email_box)

        # Add all the buttons to the horizontal box
        link_button_box.append(changelog_button)
        link_button_box.append(gpl_button)
        link_button_box.append(faq_button)
        link_button_box.append(bug_button)
        link_button_box.append(donate_button)
        link_button_box.append(github_button)
        link_button_box.append(email_button)

        box.append(title_label)
        box.append(Gtk.Separator())
        box.append(info_label)
        box.append(link_button_box) # Add the button box to the main content box
        
        return box
        
    def on_activate(self, app):
        """
        Callback for the 'activate' signal. This is where the UI is built.
        """
        # Create a standard Gtk.ApplicationWindow and Adw.HeaderBar for better compatibility.
        self.win = Gtk.ApplicationWindow(application=app)
        
        # Get the screen dimensions and set the window size based on resolution.
        display = Gdk.Display.get_default()
        if display:
            monitor = display.get_primary_monitor()
            if monitor:
                geometry = monitor.get_geometry()
                screen_width = geometry.width
                screen_height = geometry.height
                
                # Check for 4K resolution
                if screen_width == 3840 and screen_height == 2160:
                    new_width = int(screen_width * 0.4)
                    new_height = int(screen_height * 0.6)
                else:
                    # Default size for other resolutions
                    new_width = int(screen_width * 0.6)
                    new_height = int(screen_height * 0.8)
                
                self.win.set_default_size(new_width, new_height)
        else:
            # Fallback to a default size if unable to get screen dimensions
            self.win.set_default_size(800, 600)
            
        # Set the application window icon
        self.win.set_icon_name("computer-symbolic")

        # Create the header bar and set it on the window.
        self.header_bar = Adw.HeaderBar.new()
        self.win.set_titlebar(self.header_bar)
        
        # Add the computer icon to the header bar
        icon_image = Gtk.Image.new_from_icon_name("computer-symbolic")
        # To make it appear on the left side, we need to pack it at the start.
        self.header_bar.pack_start(icon_image)

        # Main stack for top-level tabs
        self.main_stack = Gtk.Stack.new()
        self.main_stack.set_vexpand(True)
        self.main_stack.set_hexpand(True)
        
        # Create a custom tab bar as the title widget
        # The second argument now provides padding between the buttons
        tab_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 18)
        tab_box.set_halign(Gtk.Align.CENTER)
        self.header_bar.set_title_widget(tab_box)
        
        self.custom_tabs = {} # Dictionary to hold our custom buttons

        # Connect the stack's visible-child property to our handler
        self.main_stack.connect('notify::visible-child', self.on_stack_page_changed)

        # --- Begin dynamic data fetching ---
        # Attempt to get the full JSON output for the content tables
        vulkaninfo_output_json = self.run_command('vulkaninfo --json')
        try:
            self.vulkan_data = json.loads(vulkaninfo_output_json)
        except (json.JSONDecodeError, FileNotFoundError):
            print("Failed to get Vulkan info. Using empty data.")
            # Set to an empty dictionary instead of mock data
            self.vulkan_data = {
                'vulkanInstanceVersion': 'N/A',
                'instanceExtensions': [],
                'instanceLayers': [],
                'devices': []
            }

        self.vulkan_split_view, self.vulkan_content_stack, self.sidebar_selection_model = self.create_vulkan_sidebar(self.vulkan_data)
        
        # New UI elements: label and dropdown for device selection
        device_selection_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 12)
        device_selection_box.set_halign(Gtk.Align.CENTER)
        device_selection_box.set_margin_top(20)
        device_selection_box.set_margin_bottom(20)

        device_label = Gtk.Label(label="Available Device(s)")
        device_label.set_margin_start(10)
        device_label.set_margin_end(6)

        # --- Begin new code for text parsing for dropdown ---
        device_names = []
        vulkaninfo_output_text = self.run_command('vulkaninfo')
        if not "Error" in vulkaninfo_output_text:
            # Use regex to find all deviceName entries from the text output
            matches = re.findall(r'deviceName\s*=\s*(.*)', vulkaninfo_output_text)
            # Remove leading/trailing whitespace and quotes
            device_names = [name.strip().strip('"') for name in matches]
        
        # If text parsing fails, use names from the JSON data as a fallback
        if not device_names:
             device_names = [d.get('deviceName', 'Unknown Device') for d in self.vulkan_data.get('devices', [])]
        
        device_list_store = Gtk.StringList.new(device_names)
        # --- End new code for text parsing for dropdown ---
        
        device_dropdown = Gtk.DropDown.new(device_list_store, None)
        device_dropdown.set_margin_start(6)
        device_dropdown.set_margin_end(10)
        
        # Add the label and dropdown to the selection box
        device_selection_box.append(device_label)
        device_selection_box.append(device_dropdown)
        
        # Connect the dropdown's selection change to our handler
        device_dropdown.connect("notify::selected", self.on_device_selected)

        # Add real-time CPU and RAM usage labels
        self.cpu_label = Gtk.Label(label="CPU: N/A")
        self.ram_label = Gtk.Label(label="RAM: N/A")

        # Add labels to the device selection box with some spacing
        device_selection_box.append(self.cpu_label)
        device_selection_box.append(self.ram_label)

        # Start the periodic update for system stats
        GLib.timeout_add_seconds(1, self.update_system_stats)

        # Main content box to hold the new device selection and the main view
        main_content_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        # Set the main content box to expand vertically to fill the window
        main_content_box.set_vexpand(True) 
        main_content_box.append(device_selection_box)
        main_content_box.append(self.vulkan_split_view)
        
        # Initially populate the content stack with data from the first device
        self._populate_vulkan_stack(self.vulkan_content_stack, 0)
        
        # Add the Vulkan page to the stack
        self.main_stack.add_titled(main_content_box, "vulkan", "Vulkan")

        # Add the new "About" page
        about_page = self.create_about_page()
        self.main_stack.add_titled(about_page, "about", "About")

        # Create and add the custom button for the Vulkan tab
        vulkan_button = self.create_tab_button("Vulkan", "video-display-symbolic")
        vulkan_button.connect("clicked", lambda b: self.main_stack.set_visible_child_name("vulkan"))
        tab_box.append(vulkan_button)
        self.custom_tabs[vulkan_button] = "vulkan"

        # Create and add the custom button for the About tab
        about_button = self.create_tab_button("About", "help-info-symbolic")
        about_button.connect("clicked", lambda b: self.main_stack.set_visible_child_name("about"))
        tab_box.append(about_button)
        self.custom_tabs[about_button] = "about"
        
        self.win.set_child(self.main_stack)
        
        # Initially set the sidebar button visibility
        self.on_stack_page_changed(self.main_stack, None)

        self.win.present()
        
if __name__ == "__main__":
    app = GPUInfoApp()
    app.run(None)
