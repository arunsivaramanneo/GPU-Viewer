import gi
import Const
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from Common import setBackgroundColor, createScrollbar, setColumns

Title1 = ["About GPU Viewer v1.1"]
Title2 = ["Change Log"]


def about(tab3):
    frame1 = Gtk.Frame(label="")
    tab3.add(frame1)
    frame2 = Gtk.Frame(label="")
    tab3.add(frame2)
    screen = Gdk.Screen.get_default()
    About_list = Gtk.ListStore(str, str)
    i = 0
    with open("../About GPU Viewer", "r") as file1:
        for line in file1:
            background_color = setBackgroundColor(i)
            About_list.append([line.strip('\n'), background_color])
            i = i + 1

    TreeAbout = Gtk.TreeView(About_list, expand=True)
    wrapWidth = screen.get_width() * 0.58

    for i, column_title in enumerate(Title1):
        renderer1 = Gtk.CellRendererText(font=Const.FONT)
        renderer1.set_property("wrap-width", wrapWidth)
        column = Gtk.TreeViewColumn(column_title, renderer1, text=i)
        column.add_attribute(renderer1, "background", 1)
        column.set_alignment(0.5)
        TreeAbout.append_column(column)

    scrollable_treelist1 = createScrollbar(TreeAbout)
    frame1.add(scrollable_treelist1)

    ChangeLog_list = Gtk.ListStore(str, str)

    with open("../Change Log", "r") as file1:
        i = 0
        for line in file1:
            background_color = setBackgroundColor(i)
            ChangeLog_list.append([line.strip('\n'), background_color])
            i = i + 1

    TreeChangeLog = Gtk.TreeView(ChangeLog_list, expand=True)

    for i, column_title in enumerate(Title2):
        renderer2 = Gtk.CellRendererText(font=Const.FONT)
        renderer2.set_property("wrap-width", wrapWidth)
        renderer2.set_property("wrap-mode", True)
        column = Gtk.TreeViewColumn(column_title, renderer2, text=i)
        column.add_attribute(renderer2, "background", 1)
        column.set_alignment(0.5)
        TreeChangeLog.append_column(column)

    scrollable_treelist2 = createScrollbar(TreeChangeLog)
    frame2.add(scrollable_treelist2)
