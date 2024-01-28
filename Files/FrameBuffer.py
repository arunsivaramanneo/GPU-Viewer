import gi
import const
import Filenames
import subprocess

gi.require_version("Gtk", "4.0")
gi.require_version(namespace='Adw', version='1')
from gi.repository import Gtk,GObject,Gio,Adw
from Common import  setBackgroundColor, create_scrollbar, createSubTab,getScreenSize,setup,create_tab

FrameBufferToolTip = ["Visual ID", "Visual Depth", "Visual Type", "Transparency", "Buffer Size", "level", "Render Type",
                      "Double Buffer", "Stereo", "Red Colorbuffer Size", "Green Colorbuffer Size",
                      "Blue Colorbuffer Size", "Alpha Colorbuffer Size"
                                               "float", "SRGB", "Auxillary Buffer", "Depth", "Stencil",
                      "Accumbuffer Red", "Accumbuffer Green", "Accumbuffer Blue", "Accumbuffer Alpha", "msnum",
                      "msbufs", "Swap", "Caveats"]

class DataObject(GObject.GObject):
    def __init__(self, data1: str,data2: str,data3: str,data4: str,data5: str, data6: str, data7: str, data8: str, data9: str, data10: str,data11: str,data12: str, data13: str,data14: str,data15: str,data16: str,data17: str, data18: str,data19: str,data20: str,data21: str,data22: str,data23: str,data24: str,data25: str,data26: str):
        super(DataObject, self).__init__()
        self.data1 = data1
        self.data2 = data2
        self.data3 = data3
        self.data4 = data4
        self.data5 = data5
        self.data6 = data6
        self.data7 = data7
        self.data8 = data8
        self.data9 = data9
        self.data10 = data10
        self.data11 = data11
        self.data12 = data12
        self.data13 = data13
        self.data14 = data14
        self.data15 = data15
        self.data16 = data16
        self.data17 = data17
        self.data18 = data18
        self.data19 = data19
        self.data20 = data20
        self.data21 = data21
        self.data22 = data22
        self.data23 = data23
        self.data24 = data24
        self.data25 = data25
        self.data26 = data26

def bind1(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data1)

def bind2(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data2)

def bind3(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data3)

def bind4(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data4)

def bind5(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data5)

def bind6(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data6)

def bind7(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data7)

def bind8(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data8)

def bind9(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data9)

def bind10(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data10)

def bind11(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data11)

def bind12(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data12)

def bind13(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data13)

def bind14(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data14)

def bind15(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data15)

def bind16(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data16)

def bind17(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data17)

def bind18(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data18)

def bind19(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data19)

def bind20(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data20)

def bind21(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data22)

def bind22(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data22)

def bind23(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data23)

def bind24(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data24)

def bind25(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data25)

def bind26(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.data26)

def FrameBuffer(button):
    FBWin = Adw.Window()
    FBWin.set_title("GLX Frame Buffer Configuration")
    headerbar = Adw.HeaderBar.new()
    headerbar.add_css_class(css_class='compact')

    adw_toolbar_view = Adw.ToolbarView.new()
    FBWin.set_content(adw_toolbar_view)

    adw_toolbar_view.add_top_bar(headerbar)
    #   FBWin.set_size_request(1000, 500)
 #   setScreenSize(FBWin, const.WIDTH_RATIO, const.HEIGHT_RATIO2)

    FBNotebook = Adw.ViewStack.new()
    FBNotebook_stack_switcher = Adw.ViewSwitcher.new()
    FBNotebook_stack_switcher.set_stack(stack=FBNotebook)
    FBNotebook_stack_switcher.set_policy(1)
    adw_toolbar_view.set_content(FBNotebook)
    headerbar.set_title_widget(title_widget=FBNotebook_stack_switcher)

#    FBGLX_Store = Gtk.ListStore(str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str,
#                                str,
#                                str, str, str, str, str, str, str, str, str)
#    TreeFBGLX = Gtk.TreeView.new_with_model(FBGLX_Store)
#    TreeFBGLX.set_enable_search(True)
#    TreeFBGLX.set_property("enable-grid-lines", 3)

    FBGLXTab = create_tab(FBNotebook,"settings","GLX Visuals",20,True)
    FBGLXGrid = Gtk.Grid()
    FBGLXTab.append(FBGLXGrid)
    FBConfigTab = create_tab(FBNotebook,"settings","GLX FBConfigs",20,True)
    FBConfigGrid = Gtk.Grid()
    FBConfigTab.append(FBConfigGrid)

    button.set_sensitive(False)

    fetch_framebuffer_glx_visual_command = "cat %s  | awk '/GLX Visuals.*/{flag=1;next}/GLXFBConfigs.*/{flag=0}flag' | awk '/----.*/{flag=1;next}flag' " %(Filenames.opengl_outpuf_file)

    fetch_framebuffer_glx_visual_process = subprocess.Popen(fetch_framebuffer_glx_visual_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    list_glx_visuals= fetch_framebuffer_glx_visual_process.communicate()[0].splitlines()

    list_glx_visuals = [i.split() for i in list_glx_visuals]

    fetch_framebuffer_glx_fbconfigs_command = "cat %s | awk '/GLXFBConfigs.*/{flag=1;next}flag' | awk '/----.*/{flag=1;next}flag' " %(Filenames.opengl_outpuf_file)

    fetch_framebuffer_glx_fbconfigs_process= subprocess.Popen(fetch_framebuffer_glx_fbconfigs_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    list_fb_configs = fetch_framebuffer_glx_fbconfigs_process.communicate()[0].splitlines()
    
    list_fb_configs = [i.split() for i in list_fb_configs]    

    frameBufferColumnView = Gtk.ColumnView()
    frameBufferColumnView.props.show_row_separators = True
    frameBufferColumnView.props.show_column_separators = True

    factory_fbglx_value1 = Gtk.SignalListItemFactory()
    factory_fbglx_value1.connect("setup",setup)
    factory_fbglx_value1.connect("bind",bind1)

    fbglxColumn1 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[0],factory_fbglx_value1)
    fbglxColumn1.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn1)

    factory_fbglx_value2 = Gtk.SignalListItemFactory()
    factory_fbglx_value2.connect("setup",setup)
    factory_fbglx_value2.connect("bind",bind2)

    fbglxColumn2 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[1],factory_fbglx_value2)
    fbglxColumn2.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn2)

    factory_fbglx_value3 = Gtk.SignalListItemFactory()
    factory_fbglx_value3.connect("setup",setup)
    factory_fbglx_value3.connect("bind",bind3)

    fbglxColumn3 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[2],factory_fbglx_value3)
    fbglxColumn3.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn3)

    factory_fbglx_value4 = Gtk.SignalListItemFactory()
    factory_fbglx_value4.connect("setup",setup)
    factory_fbglx_value4.connect("bind",bind4)

    fbglxColumn4 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[3],factory_fbglx_value4)
    fbglxColumn4.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn4)

    factory_fbglx_value5 = Gtk.SignalListItemFactory()
    factory_fbglx_value5.connect("setup",setup)
    factory_fbglx_value5.connect("bind",bind5)

    fbglxColumn5 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[4],factory_fbglx_value5)
    fbglxColumn5.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn5)

    factory_fbglx_value6 = Gtk.SignalListItemFactory()
    factory_fbglx_value6.connect("setup",setup)
    factory_fbglx_value6.connect("bind",bind6)

    fbglxColumn6 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[5],factory_fbglx_value6)
    fbglxColumn6.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn6)

    factory_fbglx_value7 = Gtk.SignalListItemFactory()
    factory_fbglx_value7.connect("setup",setup)
    factory_fbglx_value7.connect("bind",bind7)

    fbglxColumn7 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[6],factory_fbglx_value7)
    fbglxColumn7.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn7)

    factory_fbglx_value8 = Gtk.SignalListItemFactory()
    factory_fbglx_value8.connect("setup",setup)
    factory_fbglx_value8.connect("bind",bind8)

    fbglxColumn8 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[7],factory_fbglx_value8)
    fbglxColumn8.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn8)

    factory_fbglx_value9 = Gtk.SignalListItemFactory()
    factory_fbglx_value9.connect("setup",setup)
    factory_fbglx_value9.connect("bind",bind9)

    fbglxColumn9 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[8],factory_fbglx_value9)
    fbglxColumn9.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn9)

    factory_fbglx_value10 = Gtk.SignalListItemFactory()
    factory_fbglx_value10.connect("setup",setup)
    factory_fbglx_value10.connect("bind",bind10)

    fbglxColumn10 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[9],factory_fbglx_value10)
    fbglxColumn10.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn10)

    factory_fbglx_value11 = Gtk.SignalListItemFactory()
    factory_fbglx_value11.connect("setup",setup)
    factory_fbglx_value11.connect("bind",bind11)

    fbglxColumn11 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[10],factory_fbglx_value11)
    fbglxColumn11.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn11)

    factory_fbglx_value12 = Gtk.SignalListItemFactory()
    factory_fbglx_value12.connect("setup",setup)
    factory_fbglx_value12.connect("bind",bind12)

    fbglxColumn12 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[11],factory_fbglx_value12)
    fbglxColumn12.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn12)

    factory_fbglx_value13 = Gtk.SignalListItemFactory()
    factory_fbglx_value13.connect("setup",setup)
    factory_fbglx_value13.connect("bind",bind13)

    fbglxColumn13 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[12],factory_fbglx_value13)
    fbglxColumn13.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn13)

    factory_fbglx_value14 = Gtk.SignalListItemFactory()
    factory_fbglx_value14.connect("setup",setup)
    factory_fbglx_value14.connect("bind",bind14)

    fbglxColumn14 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[13],factory_fbglx_value14)
    fbglxColumn14.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn14)

    factory_fbglx_value15 = Gtk.SignalListItemFactory()
    factory_fbglx_value15.connect("setup",setup)
    factory_fbglx_value15.connect("bind",bind15)

    fbglxColumn15 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[14],factory_fbglx_value15)
    fbglxColumn15.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn15)

    factory_fbglx_value16 = Gtk.SignalListItemFactory()
    factory_fbglx_value16.connect("setup",setup)
    factory_fbglx_value16.connect("bind",bind16)

    fbglxColumn16 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[15],factory_fbglx_value16)
    fbglxColumn16.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn16)

    factory_fbglx_value17 = Gtk.SignalListItemFactory()
    factory_fbglx_value17.connect("setup",setup)
    factory_fbglx_value17.connect("bind",bind17)

    fbglxColumn17 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[16],factory_fbglx_value17)
    fbglxColumn17.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn17)

    factory_fbglx_value18 = Gtk.SignalListItemFactory()
    factory_fbglx_value18.connect("setup",setup)
    factory_fbglx_value18.connect("bind",bind18)

    fbglxColumn18 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[17],factory_fbglx_value18)
    fbglxColumn18.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn18)

    factory_fbglx_value19 = Gtk.SignalListItemFactory()
    factory_fbglx_value19.connect("setup",setup)
    factory_fbglx_value19.connect("bind",bind19)

    fbglxColumn19 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[18],factory_fbglx_value19)
    fbglxColumn19.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn19)

    factory_fbglx_value20 = Gtk.SignalListItemFactory()
    factory_fbglx_value20.connect("setup",setup)
    factory_fbglx_value20.connect("bind",bind20)

    fbglxColumn20 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[19],factory_fbglx_value20)
    fbglxColumn20.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn20)

    factory_fbglx_value21 = Gtk.SignalListItemFactory()
    factory_fbglx_value21.connect("setup",setup)
    factory_fbglx_value21.connect("bind",bind21)

    fbglxColumn21 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[20],factory_fbglx_value21)
    fbglxColumn21.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn21)

    factory_fbglx_value22 = Gtk.SignalListItemFactory()
    factory_fbglx_value22.connect("setup",setup)
    factory_fbglx_value22.connect("bind",bind22)

    fbglxColumn22 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[21],factory_fbglx_value22)
    fbglxColumn22.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn22)

    factory_fbglx_value23 = Gtk.SignalListItemFactory()
    factory_fbglx_value23.connect("setup",setup)
    factory_fbglx_value23.connect("bind",bind23)

    fbglxColumn23 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[22],factory_fbglx_value23)
    fbglxColumn23.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn23)

    factory_fbglx_value24 = Gtk.SignalListItemFactory()
    factory_fbglx_value24.connect("setup",setup)
    factory_fbglx_value24.connect("bind",bind24)

    fbglxColumn24 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[23],factory_fbglx_value24)
    fbglxColumn24.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn24)

    factory_fbglx_value25 = Gtk.SignalListItemFactory()
    factory_fbglx_value25.connect("setup",setup)
    factory_fbglx_value25.connect("bind",bind25)

    fbglxColumn25 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[24],factory_fbglx_value25)
    fbglxColumn25.set_resizable(True)
    frameBufferColumnView.append_column(fbglxColumn25)

    factory_fbglx_value26 = Gtk.SignalListItemFactory()
    factory_fbglx_value26.connect("setup",setup)
    factory_fbglx_value26.connect("bind",bind26)

    fbglxColumn26 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[25],factory_fbglx_value26)
    fbglxColumn26.set_resizable(True)
    fbglxColumn26.set_expand(True)
    frameBufferColumnView.append_column(fbglxColumn26)

    frameBufferSelection = Gtk.SingleSelection()
    FBGLX_Store = Gio.ListStore.new(DataObject)
    frameBufferSelection.set_model(FBGLX_Store)
    frameBufferColumnView.set_model(frameBufferSelection)
    
    for i in range(len(list_glx_visuals) - 1):
        background_color = setBackgroundColor(i)
        FBGLX_Store.append(DataObject(list_glx_visuals[i][0],list_glx_visuals[i][1],list_glx_visuals[i][2],list_glx_visuals[i][3],list_glx_visuals[i][4],list_glx_visuals[i][5],list_glx_visuals[i][6],list_glx_visuals[i][7],list_glx_visuals[i][8],list_glx_visuals[i][9],list_glx_visuals[i][10],list_glx_visuals[i][11],list_glx_visuals[i][12],list_glx_visuals[i][13],list_glx_visuals[i][14],list_glx_visuals[i][15],list_glx_visuals[i][16],list_glx_visuals[i][17],list_glx_visuals[i][18],list_glx_visuals[i][19],list_glx_visuals[i][20],list_glx_visuals[i][21],list_glx_visuals[i][22],list_glx_visuals[i][23],list_glx_visuals[i][24],list_glx_visuals[i][25]))
    label1 = "%d GLX Visuals" % (len(list_glx_visuals) - 1)
#    FBNotebook.set_tab_label(FBGLXTab, Gtk.Label(label=label1))

#    setColumnFrameBuffer(TreeFBGLX, const.FRAMEBUFFERLIST)

    FBGLXScrollbar = create_scrollbar(frameBufferColumnView)
    FBGLXGrid.attach(FBGLXScrollbar,0,0,1,1)


    frameBufferConfigColumnView = Gtk.ColumnView()
    frameBufferConfigColumnView.props.show_row_separators = True
    frameBufferConfigColumnView.props.show_column_separators = True


    factory_fbconfig_value1 = Gtk.SignalListItemFactory()
    factory_fbconfig_value1.connect("setup",setup)
    factory_fbconfig_value1.connect("bind",bind1)

    fbconfigColumn1 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[0],factory_fbconfig_value1)
    fbconfigColumn1.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn1)

    factory_fbconfig_value2 = Gtk.SignalListItemFactory()
    factory_fbconfig_value2.connect("setup",setup)
    factory_fbconfig_value2.connect("bind",bind2)

    fbconfigColumn2 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[1],factory_fbconfig_value2)
    fbconfigColumn2.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn2)

    factory_fbconfig_value3 = Gtk.SignalListItemFactory()
    factory_fbconfig_value3.connect("setup",setup)
    factory_fbconfig_value3.connect("bind",bind3)

    fbconfigColumn3 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[2],factory_fbconfig_value3)
    fbconfigColumn3.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn3)

    factory_fbconfig_value4 = Gtk.SignalListItemFactory()
    factory_fbconfig_value4.connect("setup",setup)
    factory_fbconfig_value4.connect("bind",bind4)

    fbconfigColumn4 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[3],factory_fbconfig_value4)
    fbconfigColumn4.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn4)

    factory_fbconfig_value5 = Gtk.SignalListItemFactory()
    factory_fbconfig_value5.connect("setup",setup)
    factory_fbconfig_value5.connect("bind",bind5)

    fbconfigColumn5 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[4],factory_fbconfig_value5)
    fbconfigColumn5.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn5)

    factory_fbconfig_value6 = Gtk.SignalListItemFactory()
    factory_fbconfig_value6.connect("setup",setup)
    factory_fbconfig_value6.connect("bind",bind6)

    fbconfigColumn6 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[5],factory_fbconfig_value6)
    fbconfigColumn6.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn6)

    factory_fbconfig_value7 = Gtk.SignalListItemFactory()
    factory_fbconfig_value7.connect("setup",setup)
    factory_fbconfig_value7.connect("bind",bind7)

    fbconfigColumn7 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[6],factory_fbconfig_value7)
    fbconfigColumn7.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn7)

    factory_fbconfig_value8 = Gtk.SignalListItemFactory()
    factory_fbconfig_value8.connect("setup",setup)
    factory_fbconfig_value8.connect("bind",bind8)

    fbconfigColumn8 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[7],factory_fbconfig_value8)
    fbconfigColumn8.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn8)

    factory_fbconfig_value9 = Gtk.SignalListItemFactory()
    factory_fbconfig_value9.connect("setup",setup)
    factory_fbconfig_value9.connect("bind",bind9)

    fbconfigColumn9 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[8],factory_fbconfig_value9)
    fbconfigColumn9.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn9)

    factory_fbconfig_value10 = Gtk.SignalListItemFactory()
    factory_fbconfig_value10.connect("setup",setup)
    factory_fbconfig_value10.connect("bind",bind10)

    fbconfigColumn10 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[9],factory_fbconfig_value10)
    fbconfigColumn10.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn10)

    factory_fbconfig_value11 = Gtk.SignalListItemFactory()
    factory_fbconfig_value11.connect("setup",setup)
    factory_fbconfig_value11.connect("bind",bind11)

    fbconfigColumn11 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[10],factory_fbconfig_value11)
    fbconfigColumn11.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn11)

    factory_fbconfig_value12 = Gtk.SignalListItemFactory()
    factory_fbconfig_value12.connect("setup",setup)
    factory_fbconfig_value12.connect("bind",bind12)

    fbconfigColumn12 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[11],factory_fbconfig_value12)
    fbconfigColumn12.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn12)

    factory_fbconfig_value13 = Gtk.SignalListItemFactory()
    factory_fbconfig_value13.connect("setup",setup)
    factory_fbconfig_value13.connect("bind",bind13)

    fbconfigColumn13 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[12],factory_fbconfig_value13)
    fbconfigColumn13.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn13)

    factory_fbconfig_value14 = Gtk.SignalListItemFactory()
    factory_fbconfig_value14.connect("setup",setup)
    factory_fbconfig_value14.connect("bind",bind14)

    fbconfigColumn14 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[13],factory_fbconfig_value14)
    fbconfigColumn14.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn14)

    factory_fbconfig_value15 = Gtk.SignalListItemFactory()
    factory_fbconfig_value15.connect("setup",setup)
    factory_fbconfig_value15.connect("bind",bind15)

    fbconfigColumn15 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[14],factory_fbconfig_value15)
    fbconfigColumn15.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn15)

    factory_fbconfig_value16 = Gtk.SignalListItemFactory()
    factory_fbconfig_value16.connect("setup",setup)
    factory_fbconfig_value16.connect("bind",bind16)

    fbconfigColumn16 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[15],factory_fbconfig_value16)
    fbconfigColumn16.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn16)

    factory_fbconfig_value17 = Gtk.SignalListItemFactory()
    factory_fbconfig_value17.connect("setup",setup)
    factory_fbconfig_value17.connect("bind",bind17)

    fbconfigColumn17 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[16],factory_fbconfig_value17)
    fbconfigColumn17.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn17)

    factory_fbconfig_value18 = Gtk.SignalListItemFactory()
    factory_fbconfig_value18.connect("setup",setup)
    factory_fbconfig_value18.connect("bind",bind18)

    fbconfigColumn18 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[17],factory_fbconfig_value18)
    fbconfigColumn18.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn18)

    factory_fbconfig_value19 = Gtk.SignalListItemFactory()
    factory_fbconfig_value19.connect("setup",setup)
    factory_fbconfig_value19.connect("bind",bind19)

    fbconfigColumn19 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[18],factory_fbconfig_value19)
    fbconfigColumn19.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn19)

    factory_fbconfig_value20 = Gtk.SignalListItemFactory()
    factory_fbconfig_value20.connect("setup",setup)
    factory_fbconfig_value20.connect("bind",bind20)

    fbconfigColumn20 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[19],factory_fbconfig_value20)
    fbconfigColumn20.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn20)

    factory_fbconfig_value21 = Gtk.SignalListItemFactory()
    factory_fbconfig_value21.connect("setup",setup)
    factory_fbconfig_value21.connect("bind",bind21)

    fbconfigColumn21 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[20],factory_fbconfig_value21)
    fbconfigColumn21.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn21)

    factory_fbconfig_value22 = Gtk.SignalListItemFactory()
    factory_fbconfig_value22.connect("setup",setup)
    factory_fbconfig_value22.connect("bind",bind22)

    fbconfigColumn22 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[21],factory_fbconfig_value22)
    fbconfigColumn22.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn22)

    factory_fbconfig_value23 = Gtk.SignalListItemFactory()
    factory_fbconfig_value23.connect("setup",setup)
    factory_fbconfig_value23.connect("bind",bind23)

    fbconfigColumn23 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[22],factory_fbconfig_value23)
    fbconfigColumn23.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn23)

    factory_fbconfig_value24 = Gtk.SignalListItemFactory()
    factory_fbconfig_value24.connect("setup",setup)
    factory_fbconfig_value24.connect("bind",bind24)

    fbconfigColumn24 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[23],factory_fbconfig_value24)
    fbconfigColumn24.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn24)

    factory_fbconfig_value25 = Gtk.SignalListItemFactory()
    factory_fbconfig_value25.connect("setup",setup)
    factory_fbconfig_value25.connect("bind",bind25)

    fbconfigColumn25 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[24],factory_fbconfig_value25)
    fbconfigColumn25.set_resizable(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn25)

    factory_fbconfig_value26 = Gtk.SignalListItemFactory()
    factory_fbconfig_value26.connect("setup",setup)
    factory_fbconfig_value26.connect("bind",bind26)

    fbconfigColumn26 = Gtk.ColumnViewColumn.new(const.FRAMEBUFFERLIST[25],factory_fbconfig_value26)
    fbconfigColumn26.set_resizable(True)
    fbconfigColumn26.set_expand(True)
    frameBufferConfigColumnView.append_column(fbconfigColumn26)

    frameBufferConfigSelection = Gtk.SingleSelection()
    FBConfig_Store = Gio.ListStore.new(DataObject)
    frameBufferConfigSelection.set_model(FBConfig_Store)
    frameBufferConfigColumnView.set_model(frameBufferConfigSelection)

    for i in range(len(list_fb_configs) - 1):
        background_color = setBackgroundColor(i)
        if list_fb_configs[i][6] == "r" or list_fb_configs[i][6] == "c":
            pass
        else:
            list_fb_configs[i].insert(6, ".")
        FBConfig_Store.append(DataObject(list_fb_configs[i][0],list_fb_configs[i][1],list_fb_configs[i][2],list_fb_configs[i][3],list_fb_configs[i][4],list_fb_configs[i][5],list_fb_configs[i][6],list_fb_configs[i][7],list_fb_configs[i][8],list_fb_configs[i][9],list_fb_configs[i][10],list_fb_configs[i][11],list_fb_configs[i][12],list_fb_configs[i][13],list_fb_configs[i][14],list_fb_configs[i][15],list_fb_configs[i][16],list_fb_configs[i][17],list_fb_configs[i][18],list_fb_configs[i][19],list_fb_configs[i][20],list_fb_configs[i][21],list_fb_configs[i][22],list_fb_configs[i][23],list_fb_configs[i][24],list_fb_configs[i][25]))
    label2 = "%d  GLX FBConfigs" % (len(list_fb_configs) - 1)
#    FBNotebook.set_tab_label(FBConfigTab, Gtk.Label(label=label2))

#    setColumnFrameBuffer(TreeFBConfig, const.FRAMEBUFFERLIST)

    FBConfigScrollbar = create_scrollbar(frameBufferConfigColumnView)
    FBConfigGrid.attach(FBConfigScrollbar,0,0,1,1)

    def button_enable(win):
        button.set_sensitive(True)

    FBWin.connect("close-request", button_enable)
    screen_width,screen_height = getScreenSize()
    FBWin.set_size_request(int(screen_width) * const.WIDTH_RATIO2 ,640)
    FBWin.present()

    # Gtk.main()
