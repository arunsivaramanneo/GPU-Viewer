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

import gi
import  const
import subprocess
import re
import Filenames

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk,Gio,Adw,GdkPixbuf

from Common import setup_expander, createSubTab, create_scrollbar, bind_expander,setMargin, setup,bind1, createMainFile, fetchContentsFromCommand,ExpandDataObject,add_tree_node,getGpuImage

platformDetailsHeader = ["Platform Information ", "Details "]
deviceDetailsHeader = ["Device Information ", "Details "]
deviceMemoryImageHeader = ["Device Information ", "Details "]


class ClinfoParser:
    def __init__(self):
        self.platforms = []
        self.fetch_data()

    def fetch_data(self):
        # Fix #3: Re-use the clinfo output file already written by
        # isOpenclSupported() in gpu_viewer.py — avoids a redundant
        # clinfo subprocess on every startup.
        try:
            with open(Filenames.opencl_output_file, "r") as f:
                output = f.read()
            if not output.strip():
                raise ValueError("clinfo output file is empty")
            self.platforms = self.parse(output)
        except Exception as e:
            print(f"Error reading clinfo output: {e}")
            # Fallback: run clinfo directly if the file is missing/empty
            try:
                output = subprocess.check_output(["clinfo"], universal_newlines=True)
                self.platforms = self.parse(output)
            except Exception as e2:
                print(f"Error running clinfo fallback: {e2}")
                self.platforms = []

    def parse(self, output):
        platforms = []
        platform_map = {}
        current_platform = None
        current_device = None
        mode = "START"
        
        lines = output.splitlines()
        for line in lines:
            if not line.strip(): continue
            indent = len(line) - len(line.lstrip())
            content = line.strip()
            
            if indent == 0:
                if "Number of platforms" in content:
                    mode = "PLATFORM"
                elif "Number of devices" in content:
                    mode = "DEVICE"
                    current_device = None
                elif "ICD loader properties" in content or "NULL platform behavior" in content:
                    mode = "STOP"
                continue

            if mode == "STOP" or mode == "START":
                continue

            # Split key and value (usually separated by multiple spaces)
            if "  " in content:
                parts = re.split(r'\s{2,}', content, maxsplit=1)
                key = parts[0].strip()
                value = parts[1].strip()
            elif " 0x" in content:
                parts = content.split(" 0x", 1)
                key = parts[0].strip()
                value = "0x" + parts[1].strip()
            else:
                key = content
                value = ""

            if indent == 2:
                if key == "Platform Name":
                    if value not in platform_map:
                        current_platform = {"name": value, "properties": [], "devices": []}
                        platforms.append(current_platform)
                        platform_map[value] = current_platform
                    else:
                        current_platform = platform_map[value]
                    continue
                
                if mode == "PLATFORM" and current_platform:
                    # Avoid duplicate properties if clinfo repeats platform block
                    if not any(p[0] == key for p in current_platform["properties"]):
                        current_platform["properties"].append((key, value, []))
                elif mode == "DEVICE" and current_platform:
                    if key == "Device Name":
                        current_device = {"name": value, "properties": []}
                        current_platform["devices"].append(current_device)
                    elif current_device:
                        current_device["properties"].append((key, value, []))
            elif indent > 2:
                # Sub-property of the last property
                if current_device and current_device["properties"]:
                    current_device["properties"][-1][2].append((key, value))
                elif current_platform and current_platform["properties"]:
                    current_platform["properties"][-1][2].append((key, value))
                    
        return platforms

def openCL(self, tab):
    gpu_index_map = []
    parser = ClinfoParser()
    oclPlatforms = parser.platforms
    platformDetails_Store = Gio.ListStore.new(ExpandDataObject)
    PlatformExtensionDetails_Store = Gio.ListStore.new(ExpandDataObject)
    DeviceDetails_Store = Gio.ListStore.new(ExpandDataObject)
    DeviceExtensionDetails_Store = Gio.ListStore.new(ExpandDataObject)
    DeviceMemoryImage_store = Gio.ListStore.new(ExpandDataObject)
    DeviceVector_store = Gio.ListStore.new(ExpandDataObject)
    DeviceQueueExecution_store = Gio.ListStore.new(ExpandDataObject)


    def getPlatformNames():
        return [p["name"] for p in oclPlatforms]

    def selectDevice(dropdown,dummy):
        selected =dropdown.props.selected_item
        DeviceDetails_Store.remove_all()
        DeviceExtensionDetails_Store.remove_all()
        PlatformExtensionDetails_Store.remove_all()
        DeviceMemoryImage_store.remove_all()
        DeviceVector_store.remove_all()
        DeviceQueueExecution_store.remove_all()
        value = 0
        if selected is not None:
            value = dropdown.props.selected
            if value == Gtk.INVALID_LIST_POSITION:
                value = 0
            real_idx = gpu_index_map[value] if len(gpu_index_map) > value else value
            getDeviceDetails(real_idx)
            refresh_extensions()
            getDeviceMemoryImageDetails(real_idx)
            getDeviceVectorDetails(real_idx)
            getDeviceQueueExecutionCapabilities(real_idx)
        
            gpu_image = getGpuImage(selected.get_string())
            image_renderer.set_pixbuf(gpu_image)


    def getDeviceNames(value):
        if value >= len(oclPlatforms): return
        
        platform = oclPlatforms[value]
        Devices_list = Gtk.StringList()
        Devices_dropdown.set_model(Devices_list)
        
        oclDeviceNames = [d["name"] for d in platform["devices"]]

        numberOfDevicesEntry.set_text(str(len(oclDeviceNames)))
        numberOfDevicesEntry.set_editable(False)

        gpu_index_map.clear()
        unique_names = []
        for i, name in enumerate(oclDeviceNames):
            # Keep unique names for dropdown but map back to original index
            if name not in unique_names:
                unique_names.append(name)
                gpu_index_map.append(i)
                Devices_list.append(name)

    def getPlatfromDetails(value):
        if value >= len(oclPlatforms): return
        
        platform = oclPlatforms[value]
        
        general_props = []
        extension_props = []

        for p in platform["properties"]:
            if "Extension" in p[0]:
                if "with Version" in p[0]:
                    extension_props.append(p)
                else:
                    general_props.append(p)
            else:
                general_props.append(p)

        populate_store(platformDetails_Store, general_props, add_children=False)
        populate_store(PlatformExtensionDetails_Store, extension_props, skip_top=True)

    def get_device_categories(platform_idx, device_idx):
        if platform_idx >= len(oclPlatforms): return None
        platform = oclPlatforms[platform_idx]
        if device_idx >= len(platform["devices"]): return None
        device = platform["devices"][device_idx]
        
        categories = {
            "Device Information": [],
            "Device Extensions": [],
            "Device Extensions with Version": [],
            "Device Memory & Image Information": [],
            "Queue & Execution Capabilities": [],
            "Device Vector Information": []
        }
        
        current_cat = "Device Information"
        for key, value, children in device["properties"]:
            # Skip redundant platform info in device section
            if key == "Platform Name" or key == "Platform Vendor":
                continue

            if "Device Extensions with Version" in key:
                categories["Device Extensions with Version"].append((key, value, children))
                continue
            if "Device Extensions" in key:
                categories["Device Extensions"].append((key, value, children))
                continue
            
            if "Preferred / native vector sizes" in key:
                current_cat = "Device Vector Information"
            elif "Address bits" in key or "Max alignment" in key:
                current_cat = "Device Memory & Image Information"
            elif "Queue properties" in key or "Execution capabilities" in key or "Device enqueue" in key:
                current_cat = "Queue & Execution Capabilities"
                
            categories[current_cat].append((key, value, children))
        return categories

    def populate_store(store, props, skip_top=False, add_children=True):
        store.remove_all()
        for key, value, children in props:
            if ("Extensions" in key or "Built-in kernels" in key or "Atomic" in key or "features" in key or "all versions" in key or "USM" in key) and "n/a" not in value.lower():
                # Handle long lists as expandable
                all_children = []
                if value:
                    if "with Version" in key or "with version" in key or "features" in key or "all versions" in key or "IL" in key:
                        if "  " in value:
                            parts = re.split(r'\s{2,}', value, maxsplit=1)
                            all_children.append(ExpandDataObject(parts[0].strip(), parts[1].strip()))
                        elif " 0x" in value:
                            parts = value.split(" 0x", 1)
                            all_children.append(ExpandDataObject(parts[0].strip(), "0x" + parts[1].strip()))
                        elif " (" in value:
                            parts = value.split(" (", 1)
                            all_children.append(ExpandDataObject(parts[0].strip(), "(" + parts[1].strip()))
                        else:
                            all_children.append(ExpandDataObject(value.strip(), ""))
                    elif "Extensions" in key:
                        for ext in value.split():
                            all_children.append(ExpandDataObject(ext, ""))
                    elif "Atomic" in key or "USM" in key:
                        for item in value.split(','):
                            all_children.append(ExpandDataObject(item.strip(), ""))
                    else:
                        for item in value.split(';'):
                            all_children.append(ExpandDataObject(item.strip(), ""))
                
                # Add versioned children if any
                for sub_key, sub_val in children:
                    all_children.append(ExpandDataObject(sub_key, sub_val))
                
                if skip_top:
                    for child in all_children:
                        store.append(child)
                else:
                    toprow = ExpandDataObject(key, str(len(all_children)))
                    if add_children:
                        toprow.children = all_children
                    store.append(toprow)
            else:
                toprow = ExpandDataObject(key, value)
                for sub_key, sub_val in children:
                    toprow.children.append(ExpandDataObject(sub_key, sub_val))
                store.append(toprow)

    def getDeviceDetails(value):
        platform_idx = platform_dropdown.props.selected
        cats = get_device_categories(platform_idx, value)
        if cats:
            populate_store(DeviceDetails_Store, cats["Device Information"])

    def getDeviceMemoryImageDetails(value):
        platform_idx = platform_dropdown.props.selected
        cats = get_device_categories(platform_idx, value)
        if cats:
            populate_store(DeviceMemoryImage_store, cats["Device Memory & Image Information"])

    def getDeviceVectorDetails(value):
        platform_idx = platform_dropdown.props.selected
        cats = get_device_categories(platform_idx, value)
        if cats:
            populate_store(DeviceVector_store, cats["Device Vector Information"])

    def getDeviceExtensionDetails(value):
        platform_idx = platform_dropdown.props.selected
        cats = get_device_categories(platform_idx, value)
        if cats:
            populate_store(DeviceExtensionDetails_Store, cats["Device Extensions with Version"], skip_top=True)

    def refresh_extensions():
        if Devices_dropdown.props.selected == Gtk.INVALID_LIST_POSITION:
            return
        real_idx = gpu_index_map[Devices_dropdown.props.selected] if len(gpu_index_map) > Devices_dropdown.props.selected else Devices_dropdown.props.selected
        getDeviceExtensionDetails(real_idx)

    def getDeviceQueueExecutionCapabilities(value):
        platform_idx = platform_dropdown.props.selected
        cats = get_device_categories(platform_idx, value)
        if cats:
            populate_store(DeviceQueueExecution_store, cats["Queue & Execution Capabilities"])

    def selectPlatform(dropdown,dummy):
        selected =dropdown.props.selected_item
        value = 0
        if selected is not None:
            value = dropdown.props.selected
        getDeviceNames(value)
        getPlatfromDetails(value)

#        gpu_image = getGpuImage(gpu_list[text])
#        image_renderer.set_pixbuf(gpu_image)

    #    os.system("rm /tmp/gpu-viewer/ocl*.txt")

    split_view_container = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
    split_view_container.set_vexpand(True)
    split_view_container.set_hexpand(True)

    split_view = Adw.NavigationSplitView.new()
    split_view.set_vexpand(True)
    split_view.set_hexpand(True)

    # Create the sidebar content using a Gtk.ListBox for tabs
    sidebar_listbox = Gtk.ListBox.new()
    sidebar_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
    sidebar_listbox.set_vexpand(True)
    sidebar_listbox.add_css_class(css_class="boxed-list")
    sidebar_listbox.add_css_class(css_class="sidebar")
    sidebar_listbox.set_show_separators(True)

    tabs = [
        "Platform Information", "Device Information", "Device Extensions", "Device Memory  \n \t    &\nImage Information",
        "Queue Capabilities\n \t\t&\nExecution Capabilities", "Device Vector Information"
    ]


    content_stack = Gtk.Stack.new()
    self.opencl_content_stack = content_stack

    # Create the content pages for each tab and add them to the stack
    for tab_name in tabs:
        row = Gtk.ListBoxRow()
        label = Gtk.Label.new(tab_name)
        # Add padding to the label inside the row
        label.set_margin_top(10)
        label.set_margin_bottom(10)
        row.set_child(label)
        sidebar_listbox.append(row)


        # Create a box for the content of this specific tab
        content_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)

        if "Platform Information" in tab_name:

                platformColumnView = Gtk.ColumnView()
                platformColumnView.props.show_row_separators = True
                platformColumnView.props.show_column_separators = False

                factory_platform = Gtk.SignalListItemFactory()
                factory_platform.connect("setup",setup_expander)
                factory_platform.connect("bind",bind_expander)

                factory_platform_value = Gtk.SignalListItemFactory()
                factory_platform_value.connect("setup",setup)
                factory_platform_value.connect("bind",bind1)

                platformSelection = Gtk.SingleSelection()
                # Store already initialized at top

                platformModel = Gtk.TreeListModel.new(platformDetails_Store,False,True,add_tree_node)
                platformSelection.set_model(platformModel)

                platformColumnView.set_model(platformSelection)

                platformColumnLhs = Gtk.ColumnViewColumn.new("Platform Information",factory_platform)
                platformColumnLhs.set_resizable(True)
                platformColumnRhs = Gtk.ColumnViewColumn.new("Details",factory_platform_value)
                platformColumnRhs.set_expand(True)

                platformColumnView.append_column(platformColumnLhs)
                platformColumnView.append_column(platformColumnRhs)

                platformScrollbar = create_scrollbar(platformColumnView)
                platformScrollbar.set_vexpand(True)

                # Platform Extensions Box
                platformExtColumnView = Gtk.ColumnView()
                platformExtColumnView.props.show_row_separators = True
                platformExtColumnView.props.show_column_separators = False

                platformExtSelection = Gtk.SingleSelection()
                
                platformExt_search_entry = Gtk.SearchEntry()
                platformExt_search_entry.set_property("placeholder-text", "Search platform extensions...")
                platformExt_search_entry.add_css_class(css_class='toolbar')
                setMargin(platformExt_search_entry, 10, 10, 10)

                def platform_ext_filter_func(item, data):
                    search_text = platformExt_search_entry.get_text().lower()
                    if not search_text:
                        return True
                    return search_text in item.data.lower() or search_text in item.data2.lower()

                platform_ext_filter_model = Gtk.FilterListModel.new(model=PlatformExtensionDetails_Store)
                platform_ext_custom_filter = Gtk.CustomFilter.new(platform_ext_filter_func, None)
                platform_ext_filter_model.set_filter(platform_ext_custom_filter)

                platformExt_search_entry.connect("search-changed", lambda w: platform_ext_custom_filter.changed(Gtk.FilterChange.DIFFERENT))

                platformExtModel = Gtk.TreeListModel.new(platform_ext_filter_model, False, True, add_tree_node)
                platformExtSelection.set_model(platformExtModel)
                platformExtColumnView.set_model(platformExtSelection)

                platformExtColumnLhs = Gtk.ColumnViewColumn.new("Platform Extensions", factory_platform)
                platformExtColumnLhs.set_resizable(True)
                platformExtColumnRhs = Gtk.ColumnViewColumn.new("Version", factory_platform_value)
                platformExtColumnRhs.set_expand(True)

                platformExtColumnView.append_column(platformExtColumnLhs)
                platformExtColumnView.append_column(platformExtColumnRhs)

                platformExtScrollbar = create_scrollbar(platformExtColumnView)
                platformExtScrollbar.set_vexpand(True)

                content_box.append(platformScrollbar)
                content_box.append(platformExtScrollbar)
                content_box.append(platformExt_search_entry)
        elif "Device Information" in tab_name:

                deviceColumnView = Gtk.ColumnView()
                deviceColumnView.props.show_row_separators = True
                deviceColumnView.props.show_column_separators = False

                factory_devices = Gtk.SignalListItemFactory()
                factory_devices.connect("setup",setup_expander)
                factory_devices.connect("bind",bind_expander)

                factory_devices_value = Gtk.SignalListItemFactory()
                factory_devices_value.connect("setup",setup)
                factory_devices_value.connect("bind",bind1)

                deviceSelection = Gtk.SingleSelection()
                # Store already initialized at top

                deviceModel = Gtk.TreeListModel.new(DeviceDetails_Store,False,True,add_tree_node)
                deviceSelection.set_model(deviceModel)

                deviceColumnView.set_model(deviceSelection)

                deviceColumnLhs = Gtk.ColumnViewColumn.new("Device Information",factory_devices)
                deviceColumnLhs.set_resizable(True)
                deviceColumnRhs = Gtk.ColumnViewColumn.new("Details",factory_devices_value)
                deviceColumnRhs.set_expand(True)

                deviceColumnView.append_column(deviceColumnLhs)
                deviceColumnView.append_column(deviceColumnRhs)

                DeviceDetailsScrollbar = create_scrollbar(deviceColumnView)

                content_box.append(DeviceDetailsScrollbar)
        elif tab_name == "Device Extensions":
                deviceExtensionColumnView = Gtk.ColumnView()
                deviceExtensionColumnView.props.show_row_separators = True
                deviceExtensionColumnView.props.show_column_separators = False

                factory_devices_extension = Gtk.SignalListItemFactory()
                factory_devices_extension.connect("setup",setup_expander)
                factory_devices_extension.connect("bind",bind_expander)

                factory_devices_extension_value = Gtk.SignalListItemFactory()
                factory_devices_extension_value.connect("setup",setup)
                factory_devices_extension_value.connect("bind",bind1)

                deviceExtensionSelection = Gtk.SingleSelection()
                # Store already initialized at top

                search_entry = Gtk.SearchEntry()
                search_entry.set_property("placeholder-text", "Search extensions...")
                search_entry.add_css_class(css_class='toolbar')
                setMargin(search_entry, 10, 10, 10)


                def filter_func(item, data):
                    search_text = search_entry.get_text().lower()
                    if not search_text:
                        return True
                    # Check both LHS (data) and RHS (data2)
                    return search_text in item.data.lower() or search_text in item.data2.lower()

                filter_model = Gtk.FilterListModel.new(model=DeviceExtensionDetails_Store)
                custom_filter = Gtk.CustomFilter.new(filter_func, None)
                filter_model.set_filter(custom_filter)

                search_entry.connect("search-changed", lambda w: custom_filter.changed(Gtk.FilterChange.DIFFERENT))

                deviceExtensionModel = Gtk.TreeListModel.new(filter_model, False, True, add_tree_node)
                deviceExtensionSelection.set_model(deviceExtensionModel)

                deviceExtensionColumnView.set_model(deviceExtensionSelection)

                deviceExtensionColumnLhs = Gtk.ColumnViewColumn.new("Device Extensions",factory_devices_extension)
                deviceExtensionColumnLhs.set_resizable(True)
                deviceExtensionColumnRhs = Gtk.ColumnViewColumn.new("Version",factory_devices_extension_value)
                deviceExtensionColumnRhs.set_expand(True)

                deviceExtensionColumnView.append_column(deviceExtensionColumnLhs)
                deviceExtensionColumnView.append_column(deviceExtensionColumnRhs)

                DeviceExtensionDetailsScrollbar = create_scrollbar(deviceExtensionColumnView)

                content_box.append(DeviceExtensionDetailsScrollbar)
                content_box.append(search_entry)
        elif "Device Memory" in tab_name:
                deviceMemoryImageColumnView = Gtk.ColumnView()
                deviceMemoryImageColumnView.props.show_row_separators = True
                deviceMemoryImageColumnView.props.show_column_separators = False

                factory_devices_memory_image = Gtk.SignalListItemFactory()
                factory_devices_memory_image.connect("setup",setup_expander)
                factory_devices_memory_image.connect("bind",bind_expander)

                factory_devices_memory_image_value = Gtk.SignalListItemFactory()
                factory_devices_memory_image_value.connect("setup",setup)
                factory_devices_memory_image_value.connect("bind",bind1)

                deviceMemoryImageSelection = Gtk.SingleSelection()
                # Store already initialized at top

                deviceMemoryImageModel = Gtk.TreeListModel.new(DeviceMemoryImage_store,False,True,add_tree_node)
                deviceMemoryImageSelection.set_model(deviceMemoryImageModel)

                deviceMemoryImageColumnView.set_model(deviceMemoryImageSelection)

                deviceMemoryImageColumnLhs = Gtk.ColumnViewColumn.new("Device Information",factory_devices_memory_image)
                deviceMemoryImageColumnLhs.set_resizable(True)
                deviceMemoryImageColumnRhs = Gtk.ColumnViewColumn.new("Details",factory_devices_memory_image_value)
                deviceMemoryImageColumnRhs.set_expand(True)

                deviceMemoryImageColumnView.append_column(deviceMemoryImageColumnLhs)
                deviceMemoryImageColumnView.append_column(deviceMemoryImageColumnRhs)

                DeviceMemoryImageScrollbar = create_scrollbar(deviceMemoryImageColumnView)

                content_box.append(DeviceMemoryImageScrollbar)
        elif "Queue Capabilities" in tab_name:
                deviceQueueExecutionColumnView = Gtk.ColumnView()
                deviceQueueExecutionColumnView.props.show_row_separators = True
                deviceQueueExecutionColumnView.props.show_column_separators = False

                factory_devices_queue_execution = Gtk.SignalListItemFactory()
                factory_devices_queue_execution.connect("setup",setup_expander)
                factory_devices_queue_execution.connect("bind",bind_expander)

                factory_devices_queue_execution_value = Gtk.SignalListItemFactory()
                factory_devices_queue_execution_value.connect("setup",setup)
                factory_devices_queue_execution_value.connect("bind",bind1)

                deviceQueueExecutionSelection = Gtk.SingleSelection()
                # Store already initialized at top

                deviceQueueExectionModel = Gtk.TreeListModel.new(DeviceQueueExecution_store,False,True,add_tree_node)
                deviceQueueExecutionSelection.set_model(deviceQueueExectionModel)

                deviceQueueExecutionColumnView.set_model(deviceQueueExecutionSelection)

                deviceQueueExectionColumnLhs = Gtk.ColumnViewColumn.new("Device Information",factory_devices_queue_execution)
                deviceQueueExectionColumnLhs.set_resizable(True)
                deviceQueueExectionColumnRhs = Gtk.ColumnViewColumn.new("Details",factory_devices_queue_execution_value)
                deviceQueueExectionColumnRhs.set_expand(True)

                deviceQueueExecutionColumnView.append_column(deviceQueueExectionColumnLhs)
                deviceQueueExecutionColumnView.append_column(deviceQueueExectionColumnRhs)

                DeviceQueueExecutionScrollbar = create_scrollbar(deviceQueueExecutionColumnView)

                content_box.append(DeviceQueueExecutionScrollbar)
        elif "Device Vector" in tab_name:
                deviceVectorColumnView = Gtk.ColumnView()
                deviceVectorColumnView.props.show_row_separators = True
                deviceVectorColumnView.props.show_column_separators = False

                factory_devices_vector = Gtk.SignalListItemFactory()
                factory_devices_vector.connect("setup",setup_expander)
                factory_devices_vector.connect("bind",bind_expander)

                factory_devices_vector_value = Gtk.SignalListItemFactory()
                factory_devices_vector_value.connect("setup",setup)
                factory_devices_vector_value.connect("bind",bind1)

                deviceVectorSelection = Gtk.SingleSelection()
                # Store already initialized at top

                deviceVectorModel = Gtk.TreeListModel.new(DeviceVector_store,False,True,add_tree_node)
                deviceVectorSelection.set_model(deviceVectorModel)

                deviceVectorColumnView.set_model(deviceVectorSelection)

                deviceVectorColumnLhs = Gtk.ColumnViewColumn.new("Device Information",factory_devices_vector)
                deviceVectorColumnLhs.set_resizable(True)
                deviceVectorRhs = Gtk.ColumnViewColumn.new("Details",factory_devices_vector_value)
                deviceVectorRhs.set_expand(True)

                deviceVectorColumnView.append_column(deviceVectorColumnLhs)
                deviceVectorColumnView.append_column(deviceVectorRhs)

                DeviceVectorScrollbar = create_scrollbar(deviceVectorColumnView)

                content_box.append(DeviceVectorScrollbar)



    # Add the tabs to the sidebar ListBox
        content_stack.add_titled(content_box, tab_name.replace(" ", "-").lower(), tab_name)

    sidebar_scrolled_window = Gtk.ScrolledWindow.new()
    sidebar_scrolled_window.set_child(sidebar_listbox)

    def on_row_activated(listbox, row):
        # Get the label from the activated row to find the tab's name
        tab_label = row.get_child()
        tab_name = tab_label.get_label()
        
        # The name for the stack child is the tab name, with spaces replaced by dashes and lowercase
        child_name = tab_name.replace(" ", "-").lower()

        # Set the visible child of the stack using its name
        content_stack.set_visible_child_name(child_name)
        
    sidebar_listbox.connect("row-activated", on_row_activated)
    sidebar_listbox.select_row(sidebar_listbox.get_row_at_index(0))

    sidebar_page = Adw.NavigationPage.new(sidebar_scrolled_window, "Sidebar")
    content_page = Adw.NavigationPage.new(content_stack, "Content")
    
    # Set the sidebar and content for the split view using the new pages
    split_view.set_sidebar(sidebar_page)
    split_view.set_content(content_page)
    
    # Add the split view to its new container
    split_view_container.append(split_view)
    
    # The Platform Drop Down

    h_box = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    h_box.set_halign(Gtk.Align.CENTER)
    setMargin(h_box,10,10,10)

#    platformGrid = Gtk.Grid()
 #   platformGrid.set_border_width(20)
#    platformGrid.set_column_spacing(20)
#    platformGrid.set_row_spacing(10)
    #   mainGrid.set_row_spacing(10)
#    platformFrame = Gtk.Frame(hexpand=True)
#    mainGrid.attach(platformFrame,0,0,1,1)
 #   platformFrame.set_child(platformGrid)

    platformLabel = Gtk.Label()
    platformLabel.add_css_class(css_class="toolbar")
#    setMargin(platformLabel,300,10,10)
    platformLabel.set_text("Available Platform(s):")
 #   platformGrid.attach(platformLabel, 0, 1, 1, 1)

    h_box.append(platformLabel)

#    h_device_box = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
#    h_device_box.set_halign(Gtk.Align.START)
#    setMargin(h_device_box,10,10,10)
    platform_list = Gtk.StringList()

    platform_names = getPlatformNames()

    for i in platform_names:
        platform_list.append(i)

    platform_dropdown = Gtk.DropDown()
    platform_dropdown.add_css_class(css_class="card")
    platform_dropdown.set_model(platform_list)

    platform_dropdown.connect("notify::selected-item",selectPlatform)

    h_box.append(platform_dropdown)

    AvailableDevices = Gtk.Label()
    
    AvailableDevices.set_label("Available Device(s) :")
    setMargin(AvailableDevices,50,10,10)
    h_box.append(AvailableDevices)
#    platformGrid.attach_next_to(AvailableDevices, platformLabel, Gtk.PositionType.BOTTOM, 2, 1)

    Devices_list = Gtk.StringList()
    Devices_dropdown = Gtk.DropDown()
    Devices_dropdown.add_css_class(css_class="card")
    Devices_dropdown.set_model(Devices_list)
    setMargin(Devices_dropdown,20,10,10)
    Devices_dropdown.connect("notify::selected-item",selectDevice)
    h_box.append(Devices_dropdown)

    gpu_image = Gtk.Image()
    gpu_image = GdkPixbuf.Pixbuf.new_from_file_at_size(const.APP_LOGO_PNG, 100, 100)
    image_renderer = Gtk.Picture.new_for_pixbuf(gpu_image)
    Devices_dropdown.set_margin_end(10)
    h_box.append(image_renderer)

#    platformGrid.attach_next_to(Devices_dropdown, AvailableDevices, Gtk.PositionType.RIGHT, 20, 1)

    numberOfDevicesEntry = Gtk.Entry()
    setMargin(numberOfDevicesEntry,30,10,10)

    setMargin(platform_dropdown,30,10,10)
    selectPlatform(platform_dropdown,0)


#    platformGrid.attach_next_to(platform_dropdown, platformLabel, Gtk.PositionType.RIGHT, 21, 1)

    numberOfPlatforms = Gtk.Label()
    setMargin(numberOfPlatforms,30,10,10)
    numberOfPlatforms.set_label("Number of Platforms :")
#    h_platform_box.append(numberOfPlatforms)
#    platformGrid.attach_next_to(numberOfPlatforms, platform_dropdown, Gtk.PositionType.RIGHT, 1, 1)

    numberOfPlatformsEntry = Gtk.Entry()
    setMargin(numberOfPlatformsEntry,30,10,10)
    numberOfPlatformsEntry.set_text(str(len(oclPlatforms)))
    numberOfPlatformsEntry.set_editable(False)
#    h_platform_box.append(numberOfPlatformsEntry)
#    platformGrid.attach_next_to(numberOfPlatformsEntry, numberOfPlatforms, Gtk.PositionType.RIGHT, 1, 1)

    numberOfDevices = Gtk.Label()
    setMargin(numberOfDevices,30,10,10)
    numberOfDevices.set_label("Number Of Devices :")
#    h_device_box.append(numberOfDevices)
#    platformGrid.attach_next_to(numberOfDevices, Devices_dropdown, Gtk.PositionType.RIGHT, 1, 1)

    numberOfDevicesEntry.set_max_length(2)

#    platformGrid.attach_next_to(numberOfDevicesEntry, numberOfDevices, Gtk.PositionType.RIGHT, 1, 1)
    tab.append(h_box)
    tab.append(split_view_container)
    return tab