import gi
import Const
import os

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Pango
from Common import setBackgroundColor, createScrollbar, setColumns, fetchImageFromUrl, getLinkButtonImg

Title1 = ["About GPU Viewer v1.1"]
Title2 = ["Change Log"]


def about(tab3):
    grid = Gtk.Grid()
    tab3.add(grid)
    frame1 = Gtk.Frame(label="")
    grid.attach(frame1,0,1,12,1)
    grid.set_row_spacing(20)
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
        renderer1 = Gtk.CellRendererText()
        renderer1.set_property("wrap-width", wrapWidth)
        renderer1.set_property("wrap-mode",Pango.WrapMode(0))
        column = Gtk.TreeViewColumn(column_title, renderer1, text=i)
        column.add_attribute(renderer1, "background", 1)
        column.set_alignment(0.5)
        TreeAbout.set_property("can-focus",False)
        TreeAbout.append_column(column)

    scrollable_treelist1 = createScrollbar(TreeAbout)
    frame1.add(scrollable_treelist1)

    Logimg = fetchImageFromUrl(Const.LOG_LOGO_PNG,Const.ICON_WIDTH,Const.ICON_HEIGHT,True)
    Logbutton = getLinkButtonImg(Logimg,Const.CHANGE_LOG_LINK,Const.TOOLTIP_CHANGE_LOG)
    grid.attach_next_to(Logbutton,frame1,Gtk.PositionType.BOTTOM,1,1)

    Licenseimg = fetchImageFromUrl(Const.LICENSE_LOGO_PNG,Const.ICON_WIDTH,Const.ICON_HEIGHT,True)
    Licensebutton = getLinkButtonImg(Licenseimg,Const.LICENSE_HTML_LINK,Const.TOOLTIP_LICENSE)
    grid.attach_next_to(Licensebutton,Logbutton,Gtk.PositionType.RIGHT,1,1)

    Faqimg = fetchImageFromUrl(Const.FAQ_LOGO_PNG,Const.ICON_WIDTH,Const.ICON_HEIGHT,True)
    Faqbutton = getLinkButtonImg(Faqimg,Const.FAQ_LINK,Const.TOOLTIP_FAQ)
    grid.attach_next_to(Faqbutton,Licensebutton,Gtk.PositionType.RIGHT,1,1)

    Reportimg = fetchImageFromUrl(Const.BUG_LOGO_PNG,Const.ICON_WIDTH,Const.ICON_HEIGHT,True)
    Reportbutton = getLinkButtonImg(Reportimg,Const.EMAIL_LINK,Const.TOOLTIP_BUG)
    grid.attach_next_to(Reportbutton,Faqbutton,Gtk.PositionType.RIGHT,1,1)

    Donateimg = fetchImageFromUrl(Const.DONATE_LOGO_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, False)
    Donatebutton = getLinkButtonImg(Donateimg,Const.PAYPAL_LINK,Const.TOOLTIP_DONATE)
    grid.attach_next_to(Donatebutton,Reportbutton,Gtk.PositionType.RIGHT,1,1)

    Twitterimg = fetchImageFromUrl(Const.TWITTER_LOGO_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
    Twitterbutton = getLinkButtonImg(Twitterimg,Const.TWITTER_LINK,Const.TOOLTIP_TWITTER)
    grid.attach_next_to(Twitterbutton, Donatebutton, Gtk.PositionType.RIGHT, 1, 1)

    Githubimg = fetchImageFromUrl(Const.GITHUB_LOGO_PNG,Const.ICON_WIDTH,Const.ICON_HEIGHT,True)
    Githubbutton = getLinkButtonImg(Githubimg,Const.GITHUB_LINK,Const.TOOLTIP_GITHUB)
    grid.attach_next_to(Githubbutton,Twitterbutton,Gtk.PositionType.RIGHT,1,1)


