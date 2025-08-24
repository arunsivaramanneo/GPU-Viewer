#!/usr/bin/env python3

# Import necessary libraries.
import sys
import gi
import subprocess

# This line is crucial for working with PyGObject.
# It ensures we are using the correct versions of the libraries.
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject,Gdk
from vulkan_viewer import create_vulkan_tab_content
import Filenames
from Common import copyContentsFromFile

# Define the main application class.
# It inherits from Adw.Application, which provides a modern application shell.

def isVulkanSupported():
    with open(Filenames.vulkaninfo_output_file,"w") as file:
        vulkan_process = subprocess.Popen(Filenames.vulkaninfo_output_command,shell=True,stdout= file,universal_newlines=True)
        vulkan_process.wait()
        vulkan_process.communicate()
    vulkaninfo_output = copyContentsFromFile(Filenames.vulkaninfo_output_file)
    return len(vulkaninfo_output) > 10 and vulkan_process.returncode == 0

class SimpleApp(Adw.Application):
    """
    A simple Libadwaita application class.
    Inherits from Adw.Application to provide the application framework.
    """
    def __init__(self, **kwargs):
        # Call the parent constructor, providing a unique application ID
        super().__init__(application_id="com.example.SimpleApp", **kwargs)
        self.connect("activate", self.on_activate)    

    def on_theme_button_clicked(self, button):
        """
        Handles the click event for the theme button to toggle between light and dark styles.
        """
        style_manager = Adw.StyleManager.get_default()
        if style_manager.get_color_scheme() == Adw.ColorScheme.PREFER_LIGHT:
            style_manager.set_color_scheme(Adw.ColorScheme.PREFER_DARK)
        else:
            style_manager.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT)
            
    def on_activate(self, app):
        """
        Callback function for the 'activate' signal.
        This is where we create and show the main window.
        """
        # Create a new Adwaita ApplicationWindow
        self.window = Adw.ApplicationWindow.new(self)
        self.window.set_title("Hello, Libadwaita!")


        # Set the application's default size to 800x800
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
                    new_height = int(screen_height * 0.85)
                
                self.window.set_default_size(new_width, new_height)

        # Create a new Adwaita view stack to hold the different pages
        self.view_stack = Adw.ViewStack.new()
        
        # Create a view switcher that will display icons
        self.switcher = Adw.ViewSwitcher.new()
        self.switcher.set_stack(self.view_stack)

        # Create a header bar
        self.header_bar = Adw.HeaderBar.new()
    #    self.header_bar.add_css_class(css_class="inline")
        # Set the view switcher as the custom title widget in the header bar
        self.header_bar.set_title_widget(self.switcher)

        theme_button = Gtk.Button.new()
        theme_button.set_icon_name("display-dark-mode-symbolic")
        theme_button.set_tooltip_text("Toggle light/dark theme")
        theme_button.connect("clicked", self.on_theme_button_clicked)
        self.header_bar.pack_end(theme_button)

        
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
            icon1 = Gtk.Image.new_from_icon_name("document-send-symbolic")

        # Add the first page to the view stack, with a title and an icon
            self.view_stack.add_titled_with_icon(vulkan_box, "page1", "Vulkan", "Vulkan")
        
        # Create the second page (tab content)
        page2_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        page2_box.set_halign(Gtk.Align.CENTER)
        page2_box.set_valign(Gtk.Align.CENTER)
        label2 = Gtk.Label.new("This is the second tab!")
        label2.set_css_classes(["title-1"])
        page2_box.append(label2)

        # Create an icon for the second tab
        icon2 = Gtk.Image.new_from_icon_name("camera-photo-symbolic")

        # Add the second page to the view stack with a title and an icon
        self.view_stack.add_titled_with_icon(page2_box, "page2", "Second Tab", icon2.get_icon_name())
        
        # Show the window and all its children
        self.window.present()


def main():
    """
    The main entry point of the application.
    """
    # Create an instance of our application class
    app = SimpleApp()
    
    # Run the application
    app.run(sys.argv)


if __name__ == "__main__":
    main()
