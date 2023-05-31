import sys
import const
import gi
gi.require_version('Gtk','4.0')
from gi.repository import Gtk, Pango
from Common import create_scrollbar,setBackgroundColor,getLinkButtonImg,fetchImageFromUrl,setMargin,getScreenSize

title = ["About GPU-Viewer v2.30"]

def about(tab3):
    box = Gtk.Box(orientation=1)
    grid = Gtk.Grid()
    tab3.append(box)
    
    About_list = Gtk.ListStore(str, str)

    with open("../About_GPU_Viewer", "r") as file1:
        for i, line in enumerate(file1):
            background_color = setBackgroundColor(i)
            About_list.append([line.strip('\n'), background_color])

    TreeAbout = Gtk.TreeView.new_with_model(About_list)
 #   TreeAbout = Gtk.ColumnView()
    TreeAbout.set_model(About_list)
    TreeAbout.set_property("enable-grid-lines",1)


    screen_width, screen_height = getScreenSize()
    wrap_width = int(screen_width) * 0.50

    for i, column_title in enumerate(title):
        renderer1 = Gtk.CellRendererText()
        renderer1.set_property("wrap-width",wrap_width)
        renderer1.set_property("wrap-mode", Pango.WrapMode(0))
        column = Gtk.TreeViewColumn(column_title, renderer1, text=i)
        column.add_attribute(renderer1, "background", 1)
        column.set_alignment(0.5)
        TreeAbout.set_property("can-focus", False)
        TreeAbout.append_column(column)

    scrollable_treelist1 = create_scrollbar(TreeAbout)
    box.append(scrollable_treelist1)
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