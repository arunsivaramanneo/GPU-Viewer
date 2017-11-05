import gi
import Const
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from Common import setBackgroundColor, createScrollbar, setColumns

Title1 = ["About GPU Viewer v1.1"]
Title2 = ["Change Log"]


def about(tab3):
    grid = Gtk.Grid()
    tab3.add(grid)
    frame1 = Gtk.Frame(label="")
    grid.attach(frame1,0,1,12,1)
    grid.set_row_spacing(10)
    grid.set_column_spacing(20)
    screen = Gdk.Screen.get_default()
    About_list = Gtk.ListStore(str, str)
    i = 0
    with open("../About GPU Viewer", "r") as file1:
        for line in file1:
            background_color = setBackgroundColor(i)
            About_list.append([line.strip('\n'), background_color])
            i = i + 1

    TreeAbout = Gtk.TreeView(About_list, expand=True)
    wrapWidth = screen.get_width() * 0.50

    for i, column_title in enumerate(Title1):
        renderer1 = Gtk.CellRendererText(font=Const.FONT)
        renderer1.set_property("wrap-width", wrapWidth)
        column = Gtk.TreeViewColumn(column_title, renderer1, text=i)
        column.add_attribute(renderer1, "background", 1)
        column.set_alignment(0.5)
        TreeAbout.append_column(column)

    scrollable_treelist1 = createScrollbar(TreeAbout)
    frame1.add(scrollable_treelist1)

    Logframe = Gtk.Frame()
    Logbutton = Gtk.LinkButton("https://github.com/arunsivaramanneo/GPU-Viewer/blob/master/Change%20Log","View Change Log")
    Logframe.add(Logbutton)
    grid.attach_next_to(Logframe,frame1,Gtk.PositionType.BOTTOM,2,1)

    Licenseframe = Gtk.Frame()
    Licensebutton = Gtk.LinkButton("https://www.gnu.org/licenses/gpl-3.0-standalone.html","View License")
    Licenseframe.add(Licensebutton)
    grid.attach_next_to(Licenseframe,Logframe,Gtk.PositionType.RIGHT,2,1)

    Faqframe = Gtk.Frame()
    Faqbutton = Gtk.LinkButton("https://github.com/arunsivaramanneo/GPU-Viewer/wiki/FAQ----GPU-Viewer","FAQ")
    Faqframe.add(Faqbutton)
    grid.attach_next_to(Faqframe,Licenseframe,Gtk.PositionType.RIGHT,2,1)


    DonateFrame = Gtk.Frame()
    Donatebutton = Gtk.LinkButton("https://www.paypal.me/ArunSivaraman","Donate")
    DonateFrame.add(Donatebutton)
    grid.attach_next_to(DonateFrame,Faqframe,Gtk.PositionType.RIGHT,2,1)
