import gi
from gi.repository import Gtk

gi.require_version("Gtk", "3.0")

Title1 = ["About GPU Viewer v1.1"]
Title2 = ["Change Log"]


def about(tab3):
    grid = Gtk.Grid()
    grid.set_row_spacing(10)
    tab3.add(grid)
    frame1 = Gtk.Frame(label="")
    grid.add(frame1)
    frame2 = Gtk.Frame(label="")
    grid.attach_next_to(frame2, frame1, Gtk.PositionType.BOTTOM, 1, 1)

    About_list = Gtk.ListStore(str, str)
    i = 0
    with open("../About GPU Viewer", "r") as file1:
        for line in file1:
            if i % 2 == 0:
                background_color = "#fff"
            else:
                background_color = "#ddd"
            About_list.append([line.strip('\n'), background_color])
            i = i + 1

    TreeAbout = Gtk.TreeView(About_list, expand=True)

    for i, column_title in enumerate(Title1):
        renderer1 = Gtk.CellRendererText(font="Helvetica 11")
        renderer1.set_property("wrap-width", 900)
    #  renderer1.set_property("wrap-mode",True)
        column = Gtk.TreeViewColumn(column_title, renderer1, text=i)
        column.add_attribute(renderer1, "background", 1)
        column.set_alignment(0.5)
        TreeAbout.append_column(column)

    scrollable_treelist1 = Gtk.ScrolledWindow()
    scrollable_treelist1.set_vexpand(True)
    scrollable_treelist1.add(TreeAbout)

    frame1.add(scrollable_treelist1)

    ChangeLog_list = Gtk.ListStore(str, str)

    with open("../Change Log", "r") as file1:
        i = 0
        for line in file1:
            if i % 2 == 0:
                background_color = "#fff"
            else:
                background_color = "#ddd"
            ChangeLog_list.append([line.strip('\n'), background_color])
            i = i + 1

    TreeChangeLog = Gtk.TreeView(ChangeLog_list, expand=True)

    for i, column_title in enumerate(Title2):
        renderer2 = Gtk.CellRendererText(font="Helvetica 11")
        renderer2.set_property("wrap-width", 990)
        renderer2.set_property("wrap-mode", True)
        column = Gtk.TreeViewColumn(column_title, renderer2, text=i)
        column.add_attribute(renderer2, "background", 1)
        column.set_alignment(0.5)
        TreeChangeLog.append_column(column)

    scrollable_treelist2 = Gtk.ScrolledWindow()
    scrollable_treelist2.set_vexpand(True)
    scrollable_treelist2.add(TreeChangeLog)

    frame2.add(scrollable_treelist2)
