import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk","3.0")

from gi.repository import Gdk, Gtk, GdkPixbuf


class MyGtk(Gtk.Window):
    def __init__(self, title):
        super(MyGtk, self).__init__(title=title)
        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

    def setScreenSize(self):
        Screen = Gdk.Screen.get_default()
        self.set_size_request(Screen.get_width() * 0.50, Screen.get_height() * 0.85)


    def createTab(self, iconUrl, iconWidth, iconHeight, aspectRatio):
        tab = Gtk.VBox(spacing=10)
        tab.set_border_width(20)
        openGlIcon = fetchImageFromUrl(iconUrl, iconWidth, iconHeight, aspectRatio)
        self.notebook.append_page(tab, Gtk.Image.new_from_pixbuf(openGlIcon))
        return tab

    def mainLoop(self):
        Gtk.main()

    def quit(self):
        Gtk.main_quit()


def fetchImageFromUrl(imgUrl, iconWidth, iconHeight, aspectRatio):
    return GdkPixbuf.Pixbuf.new_from_file_at_scale(
        filename=imgUrl, width=iconWidth, height=iconHeight, preserve_aspect_ratio=aspectRatio)
