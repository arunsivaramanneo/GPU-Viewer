#!/usr/bin/env python3

# Import necessary libraries.
import sys
import gi

# This line is crucial for working with PyGObject.
# It ensures we are using the correct versions of the libraries.
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject, Gio

# Define a custom GObject to hold our data. This is the modern,
# idiomatic way to handle list models in GTK4.
class DataItem(GObject.Object):
    def __init__(self, name, category, value):
        super().__init__()
        self.name = name
        self.category = category
        self.value = value

    # Define GObject properties for the data.
    @GObject.Property(type=str)
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @GObject.Property(type=str)
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        self._category = value

    @GObject.Property(type=int)
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

# Define the main application class.
# It inherits from Adw.Application, which provides a modern application shell.
class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        # Call the parent class's constructor.
        # Set the application ID, which is a unique identifier.
        super().__init__(application_id="com.example.SidebarApp", **kwargs)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        """
        This method is called when the application is activated.
        It's the main entry point for setting up the UI.
        """
        # Changed to Adw.ViewStack for compatibility with Adw.ViewSwitcher.
        self.content_stack = Adw.ViewStack()

        # Gtk.StackSidebar is not compatible with Adw.ViewStack, so it has been removed.
        # self.sidebar = Gtk.StackSidebar()
        # self.sidebar.set_stack(self.content_stack)

        # Create a new Adw.NavigationPage to act as the container for the sidebar.
        # This page will now be empty.
        sidebar_page = Adw.NavigationPage.new(Gtk.Box(), "Navigation")

        # Create a main navigation view.
        self.nav_view = Adw.NavigationSplitView(vexpand=True)
        self.nav_view.set_sidebar(sidebar_page)
        
        # The content also needs to be wrapped in an Adw.NavigationPage.
        content_page = Adw.NavigationPage.new(self.content_stack, "Content")
        self.nav_view.set_content(content_page)

        # Create the widgets for the new dropdown section.
        # FIX: Moved this code block to make the widgets available for the home_box.
        device_label = Gtk.Label(label="Available Device(s):")
        # Use Gtk.StringList for the dropdown's model with sample data.
        device_model = Gtk.StringList.new(["Device 1", "Device 2", "Device 3"])
        device_dropdown = Gtk.DropDown.new(device_model, None)

        # Create a Gtk.Box to hold the device selection widgets.
        device_selection_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
            margin_start=10,
            margin_end=10
        )
        device_selection_box.append(device_label)
        device_selection_box.append(device_dropdown)

        # Add all pages to the Adw.ViewStack.
        home_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            vexpand=True
        )
        # FIX: Appended the device selection box to the home_box.
        home_box.append(device_selection_box)
        home_label = Gtk.Label(label="Welcome to the Home Page!", halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        home_button = Gtk.Button(label="Go to Settings", icon_name="open-menu-symbolic", halign=Gtk.Align.CENTER)
        home_box.append(home_label)
        home_box.append(home_button)
        # Using Adw.ViewStack.add_titled_with_icon to add pages for the view switcher.
        self.content_stack.add_titled_with_icon(home_box, "home", "Home", "go-home-symbolic")

        settings_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
            spacing=10,
            vexpand=True
        )
        settings_label = Gtk.Label(label="This is the Settings Page.")
        settings_box.append(settings_label)
        self.content_stack.add_titled_with_icon(settings_box, "settings", "Settings", "preferences-system-symbolic")

        info_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
            spacing=10,
            vexpand=True
        )
        info_label = Gtk.Label(label="This is the Info Page.")
        info_box.append(info_label)
        self.content_stack.add_titled_with_icon(info_box, "info", "Info", "dialog-information-symbolic")

        logs_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
            spacing=10,
            vexpand=True
        )
        logs_label = Gtk.Label(label="This is the Logs Page.")
        logs_box.append(logs_label)
        self.content_stack.add_titled_with_icon(logs_box, "logs", "Logs", "document-symbolic")

        # Create a new page with a Gtk.ColumnView.
        data_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            vexpand=True,
            hexpand=True,
            spacing=10,
            margin_top=10,
            margin_bottom=10
        )

        # Create the search entry.
        self.search_entry = Gtk.SearchEntry(
            placeholder_text="Search data...",
            margin_start=10,
            margin_end=10
        )

        # FIX: Use a Gio.ListStore with the custom DataItem type.
        data_model = Gio.ListStore.new(item_type=DataItem)
        
        # Add some dummy data to the store.
        data_model.append(DataItem("Item 1", "Category A", 100))
        data_model.append(DataItem("Item 2", "Category B", 250))
        data_model.append(DataItem("Item 3", "Category A", 50))
        data_model.append(DataItem("Item 4", "Category C", 320))
        data_model.append(DataItem("Item 5", "Category B", 150))
        
        # FIX: The filter is now a method of the class, passed directly to Gtk.CustomFilter.
        search_filter = Gtk.CustomFilter.new(lambda item: self.filter_func(item, self.search_entry.get_text()))
        
        # Create a FilterListModel from the data model and the filter.
        filtered_model = Gtk.FilterListModel.new(data_model, search_filter)
        
        # Connect the search entry to the filter.
        # FIX: Remove the 'None' argument as Gtk.Filter.changed() does not accept it.
        self.search_entry.connect("search-changed", lambda entry: search_filter.changed())

        # Create factories for each column to display the correct property.
        name_factory = Gtk.SignalListItemFactory()
        def name_setup(factory, list_item):
            list_item.set_child(Gtk.Label())
        def name_bind(factory, list_item):
            label = list_item.get_child()
            data_item = list_item.get_item()
            if data_item:
                label.set_label(data_item.name)
        name_factory.connect("setup", name_setup)
        name_factory.connect("bind", name_bind)

        category_factory = Gtk.SignalListItemFactory()
        def category_setup(factory, list_item):
            list_item.set_child(Gtk.Label())
        def category_bind(factory, list_item):
            label = list_item.get_child()
            data_item = list_item.get_item()
            if data_item:
                label.set_label(data_item.category)
        category_factory.connect("setup", category_setup)
        category_factory.connect("bind", category_bind)

        value_factory = Gtk.SignalListItemFactory()
        def value_setup(factory, list_item):
            list_item.set_child(Gtk.Label())
        def value_bind(factory, list_item):
            label = list_item.get_child()
            data_item = list_item.get_item()
            if data_item:
                label.set_label(str(data_item.value))
        value_factory.connect("setup", value_setup)
        value_factory.connect("bind", value_bind)

        # Use the filtered model for the column view.
        column_view = Gtk.ColumnView.new(Gtk.SingleSelection.new(filtered_model))
        column_view.set_vexpand(True)
        column_view.set_hexpand(True)

        name_column = Gtk.ColumnViewColumn.new("Name", name_factory)
        category_column = Gtk.ColumnViewColumn.new("Category", category_factory)
        value_column = Gtk.ColumnViewColumn.new("Value", value_factory)

        column_view.append_column(name_column)
        column_view.append_column(category_column)
        column_view.append_column(value_column)
        
        # Add a ScrolledWindow to the column view for scrolling.
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(column_view)

        data_box.append(self.search_entry)
        data_box.append(scrolled_window)
        
        self.content_stack.add_titled_with_icon(data_box, "data", "Data", "document-edit-symbolic")

        # Create the new view switcher and its container box.
        view_switcher = Adw.ViewSwitcher(stack=self.content_stack, halign=Gtk.Align.CENTER)
        view_switcher_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.CENTER,
            margin_top=10,
            margin_bottom=10
        )
        view_switcher_box.append(view_switcher)
        
        # Create a top-level box to hold the new dropdown and the navigation view.
        main_window_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            vexpand=True,
            hexpand=True
        )
        main_window_box.append(view_switcher_box)
        # The device_selection_box is no longer appended here.
        main_window_box.append(self.nav_view)

        # Create the main application window.
        self.win = Adw.ApplicationWindow(application=app)
        self.win.set_default_size(800, 600)  # Set a default size for the window.
        self.win.set_content(main_window_box) # Set the top-level box as the content.

    def filter_func(self, item, search_text):
        """
        The callback function used by the Gtk.CustomFilter.
        Returns True if the item should be displayed, False otherwise.
        """
        # FIX: Check for item being None before accessing its properties.
        if item is None:
            return False

        if not search_text:
            return True
        
        search_text_lower = search_text.lower()
        
        # Check if the search text is in any of the item's properties.
        if search_text_lower in item.name.lower():
            return True
        if search_text_lower in item.category.lower():
            return True
        # Convert the integer value to a string for comparison.
        if search_text_lower in str(item.value).lower():
            return True
            
        return False

# Run the application.
if __name__ == "__main__":
    app = MyApp()
    app.run(sys.argv)
