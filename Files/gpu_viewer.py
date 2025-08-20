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
from vulkan_viewer import create_vulkan_sidebar, on_device_selected, update_system_stats
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

        self.vulkan_split_view, self.vulkan_content_stack, self.sidebar_selection_model = create_vulkan_sidebar(self)
        
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
        device_dropdown.connect("notify::selected",on_device_selected,self, device_dropdown)

        # Add real-time CPU and RAM usage labels
        self.cpu_label = Gtk.Label(label="CPU: N/A")
        self.ram_label = Gtk.Label(label="RAM: N/A")

        # Add labels to the device selection box with some spacing
        device_selection_box.append(self.cpu_label)
        device_selection_box.append(self.ram_label)

        # Start the periodic update for system stats
        GLib.timeout_add_seconds(1, update_system_stats,self)

        # Main content box to hold the new device selection and the main view
        main_content_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        # Set the main content box to expand vertically to fill the window
        main_content_box.set_vexpand(True) 
        main_content_box.append(device_selection_box)
        main_content_box.append(self.vulkan_split_view)
        
        # Initially populate the content stack with data from the first device
    #    self._populate_vulkan_stack(self.vulkan_content_stack, 0)
        
        # Add the Vulkan page to the stack
        self.main_stack.add_titled(main_content_box, "vulkan", "Vulkan")

        # Add the new "About" page
    #    about_page = self.create_about_page()
    #    self.main_stack.add_titled(about_page, "about", "About")

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
