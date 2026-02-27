import gi
import const
gi.require_version("Adw","1")
gi.require_version("Gtk","4.0")

from gi.repository import Adw, Gio, GObject, Gtk, Pango,Adw
from Common import create_scrollbar,fetchImageFromUrl,getLinkButtonImg,setMargin

Adw.init()

title = "About GPU-Viewer v3.29"

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

class AboutPage(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.grid = Gtk.Grid()
        
        title = "About GPU-Viewer v3.30"
        self.column_view = Gtk.ColumnView()
        self.column_view.props.show_row_separators = True
        self.column_view.props.single_click_activate = False
        self.column_view.props.show_column_separators = True
        
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", setup)
        factory.connect("bind", bind)
        
        scrollable_treelist1 = create_scrollbar(self.column_view)
        self.append(scrollable_treelist1)
        
        aboutColumn = Gtk.ColumnViewColumn.new(title)
        aboutColumn.set_resizable(True)
        aboutColumn.set_expand(True)
        aboutColumn.set_factory(factory)
        self.column_view.append_column(aboutColumn)
        
        selection = Gtk.SingleSelection()
        self.store = Gio.ListStore.new(DataObject)
        selection.set_model(self.store)
        self.column_view.set_model(selection)
        
        with open("../About_GPU_Viewer", "r") as file1:
            for i, line in enumerate(file1):
                self.store.append(DataObject(line.strip('\n')))
        
        self.append(self.grid)
        
        # Buttons with icons
        self.log_button = Gtk.LinkButton.new_with_label(const.CHANGE_LOG_LINK)
        self.log_button.set_tooltip_text(const.TOOLTIP_CHANGE_LOG)
        setMargin(self.log_button, 10, 5, 5)
        self.grid.attach(self.log_button, 0, 0, 1, 1)

        self.license_button = Gtk.LinkButton.new_with_label(const.LICENSE_HTML_LINK)
        self.license_button.set_tooltip_text(const.TOOLTIP_LICENSE)
        setMargin(self.license_button, 100, 5, 5)
        self.grid.attach_next_to(self.license_button, self.log_button, Gtk.PositionType.RIGHT, 1, 1)

        self.faq_button = Gtk.LinkButton.new_with_label(const.FAQ_LINK)
        self.faq_button.set_tooltip_text(const.TOOLTIP_FAQ)
        setMargin(self.faq_button, 100, 5, 5)
        self.grid.attach_next_to(self.faq_button, self.license_button, Gtk.PositionType.RIGHT, 1, 1)

        self.report_button = Gtk.LinkButton.new_with_label(const.ISSUE_LINK)
        self.report_button.set_tooltip_text(const.TOOLTIP_BUG)
        setMargin(self.report_button, 100, 5, 5)
        self.grid.attach_next_to(self.report_button, self.faq_button, Gtk.PositionType.RIGHT, 1, 1)

        self.donate_button = Gtk.LinkButton.new_with_label(const.PAYPAL_LINK)
        self.donate_button.set_tooltip_text(const.TOOLTIP_DONATE)
        setMargin(self.donate_button, 100, 5, 5)
        self.grid.attach_next_to(self.donate_button, self.report_button, Gtk.PositionType.RIGHT, 1, 1)

        self.github_button = Gtk.LinkButton.new_with_label(const.GITHUB_LINK)
        self.github_button.set_tooltip_text(const.TOOLTIP_GITHUB)
        setMargin(self.github_button, 100, 5, 5)
        self.grid.attach_next_to(self.github_button, self.donate_button, Gtk.PositionType.RIGHT, 1, 1)

        self.contact_button = Gtk.LinkButton.new_with_label(const.EMAIL_LINK)
        self.contact_button.set_tooltip_text(const.TOOLTIP_CONTACT)
        setMargin(self.contact_button, 100, 5, 5)
        self.grid.attach_next_to(self.contact_button, self.github_button, Gtk.PositionType.RIGHT, 1, 1)
        
        self.refresh_icons()

    def refresh_icons(self):
        self.log_button.set_child(Gtk.Picture.new_for_pixbuf(fetchImageFromUrl(const.LOG_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT2, True)))
        self.license_button.set_child(Gtk.Picture.new_for_pixbuf(fetchImageFromUrl(const.LICENSE_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT2, True)))
        self.faq_button.set_child(Gtk.Picture.new_for_pixbuf(fetchImageFromUrl(const.FAQ_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT2, True)))
        self.report_button.set_child(Gtk.Picture.new_for_pixbuf(fetchImageFromUrl(const.BUG_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT2, True)))
        self.donate_button.set_child(Gtk.Picture.new_for_pixbuf(fetchImageFromUrl(const.DONATE_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT2, True)))
        self.github_button.set_child(Gtk.Picture.new_for_pixbuf(fetchImageFromUrl(const.GITHUB_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT2, True)))
        self.contact_button.set_child(Gtk.Picture.new_for_pixbuf(fetchImageFromUrl(const.CONTACT_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT2, True)))

def about_page(tab3):
    page = AboutPage()
    tab3.append(page)
    return page