import gi
import const
gi.require_version("Adw","1")
gi.require_version("Gtk","4.0")

from gi.repository import Adw, Gio, GObject, Gtk, Pango,Adw
from Common import create_scrollbar,fetchImageFromUrl,getLinkButtonImg,setMargin

Adw.init()

title = "About GPU-Viewer v3.25"

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GObject  # noqa


class DataObject(GObject.GObject):
    def __init__(self, column: str):
        super(DataObject, self).__init__()
        self.column = column

def setup(widget, item):
    """Setup the widget to show in the Gtk.Listview"""
    label = Gtk.Label()
    label.props.use_markup = True
    label.props.xalign = 0.0
    item.set_child(label)


def bind(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.column)

def about_page(tab3):
    box = Gtk.Box(orientation=1)
    grid = Gtk.Grid()
    tab3.append(box)

    column_view = Gtk.ColumnView()
    column_view.props.show_row_separators = True
    column_view.props.single_click_activate = False
    column_view.props.show_column_separators = True
    factory = Gtk.SignalListItemFactory()
    factory.connect("setup", setup)
    factory.connect("bind", bind)
    scrollable_treelist1 = create_scrollbar(column_view)
    box.append(scrollable_treelist1)
 #   box.append(sw)
 #   sw.set_child(column_view)

    aboutColumn = Gtk.ColumnViewColumn.new(title)
    aboutColumn.set_resizable(True)
#    aboutColumn.set_fixed_width(5)
    aboutColumn.set_expand(True)
    aboutColumn.set_factory(factory)
    column_view.append_column(aboutColumn)

    selection = Gtk.SingleSelection()
    
    store = Gio.ListStore.new(DataObject)
    
    selection.set_model(store)
    
    column_view.set_model(selection)

    with open("../About_GPU_Viewer", "r") as file1:
        for i, line in enumerate(file1):
            store.append(DataObject(line.strip('\n')))

    box.append(grid)


    Logimg = fetchImageFromUrl(const.LOG_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT2, True)
    Logbutton = getLinkButtonImg(Logimg, const.CHANGE_LOG_LINK, const.TOOLTIP_CHANGE_LOG)
    setMargin(Logbutton,10,5,5)
    grid.attach(Logbutton, 0, 0,1,1)

    Licenseimg = fetchImageFromUrl(const.LICENSE_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT2, True)
    Licensebutton = getLinkButtonImg(Licenseimg, const.LICENSE_HTML_LINK, const.TOOLTIP_LICENSE)
    setMargin(Licensebutton,100,5,5)
    grid.attach_next_to(Licensebutton, Logbutton, Gtk.PositionType.RIGHT, 1, 1)

    Faqimg = fetchImageFromUrl(const.FAQ_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT2, True)
    Faqbutton = getLinkButtonImg(Faqimg, const.FAQ_LINK, const.TOOLTIP_FAQ)
    setMargin(Faqbutton,100,5,5)
    grid.attach_next_to(Faqbutton, Licensebutton, Gtk.PositionType.RIGHT, 1, 1)

    Reportimg = fetchImageFromUrl(const.BUG_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT2, True)
    Reportbutton = getLinkButtonImg(Reportimg, const.ISSUE_LINK, const.TOOLTIP_BUG)
    setMargin(Reportbutton,100,5,5)
    grid.attach_next_to(Reportbutton, Faqbutton, Gtk.PositionType.RIGHT, 1, 1)

    Donateimg = fetchImageFromUrl(const.DONATE_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT2, True)
    Donatebutton = getLinkButtonImg(Donateimg, const.PAYPAL_LINK, const.TOOLTIP_DONATE)
    setMargin(Donatebutton,100,5,5)
    grid.attach_next_to(Donatebutton, Reportbutton, Gtk.PositionType.RIGHT, 1, 1)

    Githubimg = fetchImageFromUrl(const.GITHUB_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT2, True)
    Githubbutton = getLinkButtonImg(Githubimg, const.GITHUB_LINK, const.TOOLTIP_GITHUB)
    setMargin(Githubbutton,100,5,5)
    grid.attach_next_to(Githubbutton, Donatebutton, Gtk.PositionType.RIGHT, 1, 1)

    Contactimg = fetchImageFromUrl(const.CONTACT_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT2, True)
    Contactbutton = getLinkButtonImg(Contactimg, const.EMAIL_LINK, const.TOOLTIP_CONTACT)
    setMargin(Contactbutton,100,5,5)
    grid.attach_next_to(Contactbutton, Githubbutton, Gtk.PositionType.RIGHT, 1, 1)

    return tab3