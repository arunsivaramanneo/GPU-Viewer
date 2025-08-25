import sys
import gi
import const
import Filenames
import subprocess
from FrameBuffer import FrameBuffer
gi.require_version('Gtk','4.0')
gi.require_version(namespace='Adw', version='1')


from gi.repository import Gtk,Gio,GObject,Adw

Adw.init()

from Common import getScreenSize,createMainFile,create_scrollbar,setMargin,copyContentsFromFile,getGpuImage,fetchImageFromUrl,appendLimitsRHS,create_tab

Title = [""]
Title2 = ["OpenGL Information ", " Details"]
LimitsTitle = ["OpenGL Hardware Limits", "Value"]


class ExpandDataObject(GObject.GObject):
    def __init__(self, txt: str, txt2: str):
        super(ExpandDataObject, self).__init__()
        self.data = txt
        self.data2 = txt2
        self.children = []

def add_tree_node(item):
    if not (item):
            print("no item")
            return model
    else:        
        if type(item) == Gtk.TreeListRow:
            item = item.get_item()

            print("converteu")
            print(item)  
            
        if not item.children:
            return None
        store = Gio.ListStore.new(ExpandDataObject)
        for child in item.children:
            store.append(child)
        return store

class DataObject2(GObject.GObject):
    def __init__(self, column1: str):
        super(DataObject2, self).__init__()
        self.column1 = column1

class DataObject(GObject.GObject):
    def __init__(self, column1: str,column2: str):
        super(DataObject, self).__init__()
        self.column1 = column1
        self.column2 = column2

def setup_expander(widget, item):
    """Setup the widget to show in the Gtk.Listview"""
    label = Gtk.Label()
    expander = Gtk.TreeExpander.new()
 #   expander.props.indent_for_icon = True
 #   expander.props.indent_for_depth = True
    expander.set_child(label)
    item.set_child(expander)

def setup(widget, item):
    """Setup the widget to show in the Gtk.Listview"""
    label = Gtk.Label()
    label.props.xalign = 0.0
    item.set_child(label)

def bind_column1(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_text(obj.column1)
    label.add_css_class(css_class='parent')

def bind_column2(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.column2)

def bind1(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    row = item.get_item()
    obj = row.get_item()
    if "true" in obj.data2: 
        label.add_css_class(css_class='true')
    elif "false" in obj.data2:
        label.add_css_class(css_class='false')
    else:
        label.add_css_class(css_class='nothing')
    label.set_label(obj.data2)
    

def bind_expander(widget, item):
    """bind data from the store object to the widget"""
    expander = item.get_child()
    label = expander.get_child()
    row = item.get_item()
    expander.set_list_row(row)
    obj = row.get_item()
    label.set_label(obj.data)
    label.add_css_class(css_class='parent')

def OpenGL(tab):

    def opengl_info():
        fetch_opengl_information_command = "cat %s | grep string | grep -v glx" %(Filenames.opengl_outpuf_file)
        fetch_es2_information_command = "es2_info | awk '/EGL_VERSION|VENDOR/'"
        fetch_opengl_information_lhs_command = "cat %s | awk '{gsub(/string|:.*/,'True');print}' " %(Filenames.opengl_device_info_file)
        fetch_opengl_memory_info_lhs_command = "cat %s | grep memory: | awk '{gsub(/:.*/,'True');print}' " %(Filenames.opengl_outpuf_file)
        fetch_opengl_information_rhs_command = "cat %s | grep -o :.* | grep -o ' .*' " %(Filenames.opengl_device_info_file)
        fetch_opengl_memory_info_rhs_command = "cat %s | grep memory: | grep -o :.* | grep -o ' .*' " %(Filenames.opengl_outpuf_file)

        with open(Filenames.opengl_device_info_file,"w") as file:
            fetch_opengl_information_process = subprocess.Popen(fetch_opengl_information_command,shell=True,stdout=file,universal_newlines=True)
            fetch_opengl_information_process.communicate()
            fetch_es2_information_process = subprocess.Popen(fetch_es2_information_command,shell=True,stdout=file,universal_newlines=True)
            fetch_es2_information_process.communicate()

        with open(Filenames.opengl_info_lhs_file,"w") as file:
            fetch_opengl_information_lhs_process = subprocess.Popen(fetch_opengl_information_lhs_command,shell=True,stdout=file,universal_newlines=True)
            fetch_opengl_information_lhs_process.communicate()
            fetch_opengl_memory_info_lhs_process = subprocess.Popen(fetch_opengl_memory_info_lhs_command,shell=True,stdout=file,universal_newlines=True)
            fetch_opengl_memory_info_lhs_process.communicate()

        with open(Filenames.opengl_info_rhs_file,"w") as file:
            fetch_opengl_information_rhs_process = subprocess.Popen(fetch_opengl_information_rhs_command,shell=True,stdout=file,universal_newlines=True)
            fetch_opengl_information_rhs_process.communicate()
            fetch_opengl_memory_info_rhs_process = subprocess.Popen(fetch_opengl_memory_info_rhs_command,shell=True,stdout=file,universal_newlines=True)
            fetch_opengl_memory_info_rhs_process.communicate()

        value_opengl_information_rhs = copyContentsFromFile(Filenames.opengl_info_rhs_file)
        
        with open(Filenames.opengl_info_lhs_file, "r") as file1:
            for i,line in enumerate(file1):
                text = line.strip(" ")
                opengl_info_list.append(DataObject(text.strip('\n'), value_opengl_information_rhs[i].strip('\n')))
    
    def clickme(button):

        button.set_sensitive(False)

        createMainFile(Filenames.opengl_core_limits_file,Filenames.fetch_opengl_core_limits_command)

        createMainFile(Filenames.opengl_core_limits_lhs_file,Filenames.fetch_opengl_core_limits_lhs_command)

        LimitsWin = Adw.Window()
        LimitsWin.set_title("OpenGL Hardware Limits")
        headerbar = Adw.HeaderBar.new()
        headerbar.add_css_class(css_class='compact')

        adw_toolbar_view = Adw.ToolbarView.new()
        LimitsWin.set_content(adw_toolbar_view)

        adw_toolbar_view.add_top_bar(headerbar)

        LimitsNotebook = Adw.ViewStack.new()
        limits_stack_switcher = Adw.ViewSwitcher.new()
        limits_stack_switcher.set_policy(1)
        limits_stack_switcher.set_stack(stack=LimitsNotebook)
        headerbar.set_title_widget(title_widget=limits_stack_switcher)
    #    LimitsNotebook.set_property('tab-pos',Gtk.PositionType.LEFT) 
        adw_toolbar_view.set_content(LimitsNotebook)
        LimitsCoreTab = create_tab(LimitsNotebook,"settings","Core",20,True)
    #    LimitsNotebook.append_page(LimitsCoreTab,Gtk.Label(label="\tCore\t"))
        LimitsCoreFrame = Gtk.Frame()
        limitsList = Gtk.StringList()
        limitsDropDown =Gtk.DropDown()
        limitsDropDown.set_model(limitsList)
        setMargin(limitsDropDown,2,2,2)

        # get Combo box value
        limitsList.append("Show All OpenGL Hardware Core Limits")
        with open(Filenames.opengl_core_limits_lhs_file,"r") as file1:
            for line in file1:
                if ":" in line:
                    text = line[:-2]
                    limitsList.append(text.strip(" "))

        LimitsCoreTab.append(LimitsCoreFrame)
        LimitsGrid = Gtk.Grid()
        LimitsGrid.set_row_spacing(5)
        LimitsCoreFrame.set_child(LimitsGrid)
        LimitsGrid.attach(limitsDropDown,0,0,1,1)

        limitsColumnView = Gtk.ColumnView()
        limitsColumnView.props.show_row_separators = True
        limitsColumnView.props.show_column_separators = False

        factory_limits = Gtk.SignalListItemFactory()
        factory_limits.connect("setup",setup_expander)
        factory_limits.connect("bind",bind_expander)

        factory_limits_value = Gtk.SignalListItemFactory()
        factory_limits_value.connect("setup",setup)
        factory_limits_value.connect("bind",bind1)

        limitSelection = Gtk.SingleSelection()
        LimitsCore_Store = Gio.ListStore.new(ExpandDataObject)

        limitModel = Gtk.TreeListModel.new(LimitsCore_Store,False,True,add_tree_node)
        limitSelection.set_model(limitModel)

        limitsColumnView.set_model(limitSelection)

        limitColumnLhs = Gtk.ColumnViewColumn.new("OpenGL Hardware Limits",factory_limits)
        limitColumnLhs.set_resizable(True)
        limitColumnRhs = Gtk.ColumnViewColumn.new("Value",factory_limits_value)
        limitColumnRhs.set_expand(True)

        limitsColumnView.append_column(limitColumnLhs)
        limitsColumnView.append_column(limitColumnRhs)


    #    LimitsCore_Store = Gtk.TreeStore(str, str, str)
    #    TreeCoreLimits = Gtk.TreeView.new_with_model(LimitsCore_Store)
    #    TreeCoreLimits.set_property("enable-grid-lines",1)


        showLimits(limitsDropDown,0, LimitsCore_Store, limitsColumnView,Filenames.opengl_core_limits_file)
        limitsDropDown.connect("notify::selected-item",showLimits, LimitsCore_Store, limitsColumnView,Filenames.opengl_core_limits_file)

    #    showLimits(LimitRHSValue, LimitsRHS, LimitsCore_Store, TreeCoreLimits,"/tmp/gpu-viewer/OpenGLCoreLimitsLHS.txt")

    #    setColumns(TreeCoreLimits, LimitsTitle, const.MWIDTH,0.0)
        LimitsCoreScrollbar = create_scrollbar(limitsColumnView)
        LimitsGrid.attach_next_to(LimitsCoreScrollbar,limitsDropDown,Gtk.PositionType.BOTTOM,1,1)

        createMainFile(Filenames.opengl_compat_limits_file,Filenames.fetch_opengl_compat_limits_command)

        createMainFile(Filenames.opengl_compat_limits_lhs_file,Filenames.fetch_opengl_compat_limits_lhs_command)

        LimitsCompatTab = create_tab(LimitsNotebook,"settings","Compat.",20,True)
    #    LimitsNotebook.append_page(LimitsCompatTab,Gtk.Label(label="    Compat.\t"))
        LimitsCompatFrame = Gtk.Frame()
        LimitsCompat_List = Gtk.StringList()
        limitsCompatDropDown = Gtk.DropDown()
        limitsCompatDropDown.set_model(LimitsCompat_List)
        LimitsCompat_List.append("Show All OpenGL Hardware Compatible Limits")
        with open(Filenames.opengl_compat_limits_lhs_file,"r") as file1:
            for line in file1:
                if ":" in line:
                    text = line[:-2]
                    LimitsCompat_List.append(text.strip(" "))


        LimitsCompatTab.append(LimitsCompatFrame)
        limitsCompatGrid = Gtk.Grid()
        limitsCompatGrid.set_row_spacing(5)
        LimitsCompatFrame.set_child(limitsCompatGrid)
        limitsCompatGrid.attach(limitsCompatDropDown,0,0,1,1)

    
        limitsCompatColumnView = Gtk.ColumnView()
        limitsCompatColumnView.props.show_row_separators = True
        limitsCompatColumnView.props.show_column_separators = False

        factory_compat_limits = Gtk.SignalListItemFactory()
        factory_compat_limits.connect("setup",setup_expander)
        factory_compat_limits.connect("bind",bind_expander)

        factory_compat_limits_value = Gtk.SignalListItemFactory()
        factory_compat_limits_value.connect("setup",setup)
        factory_compat_limits_value.connect("bind",bind1)

        limitCompatSelection = Gtk.SingleSelection()
        LimitsCompat_Store = Gio.ListStore.new(ExpandDataObject)

        limitCompatModel = Gtk.TreeListModel.new(LimitsCompat_Store,False,True,add_tree_node)
        limitCompatSelection.set_model(limitCompatModel)

        limitsCompatColumnView.set_model(limitCompatSelection)

        limitCompatColumnLhs = Gtk.ColumnViewColumn.new("OpenGL Hardware Limits",factory_compat_limits)
        limitCompatColumnLhs.set_resizable(True)
        limitCompatColumnRhs = Gtk.ColumnViewColumn.new("Value",factory_compat_limits_value)
        limitCompatColumnRhs.set_expand(True)

        limitsCompatColumnView.append_column(limitCompatColumnLhs)
        limitsCompatColumnView.append_column(limitCompatColumnRhs)

    #    LimitsCompat_Store = Gtk.TreeStore(str,str,str)
    #    TreeCompatLimits = Gtk.TreeView.new_with_model(LimitsCompat_Store)
    #    TreeCompatLimits.set_property("enable-grid-lines",1)

        showLimits(limitsCompatDropDown,0, LimitsCompat_Store, limitsCompatColumnView,Filenames.opengl_compat_limits_file)
        limitsCompatDropDown.connect("notify::selected-item",showLimits, LimitsCompat_Store, limitsCompatColumnView,Filenames.opengl_compat_limits_file)


     #   showLimits(LimitRHSValue2, LimitsRHS2, LimitsCompat_Store, TreeCompatLimits,"/tmp/gpu-viewer/OpenGLLimitsLHS.txt")

    #    setColumns(TreeCompatLimits, LimitsTitle, const.MWIDTH,0.0)
        LimitsCompatScrollbar = create_scrollbar(limitsCompatColumnView)
        limitsCompatGrid.attach_next_to(LimitsCompatScrollbar,limitsCompatDropDown,Gtk.PositionType.BOTTOM,1,1)

        def button_enable(win):
            button.set_sensitive(True)
        LimitsWin.connect("close-request",button_enable)
        screen_width,screen_height = getScreenSize()
        LimitsWin.set_size_request(960,640)

        LimitsWin.present()

    def showLimits(dropdown,dummy,Limits_Store, TreeLimits,openGLLimits):
        selected =dropdown.props.selected_item
        limitValue = ""
        if selected is not None:
            limitValue = selected.props.string
        
        k = 0
        count = 0
        fetch_show_opengl_limits_lhs_command = "cat %s | %s " %(openGLLimits,Filenames.remove_rhs_Command) 
        fetch_show_opengl_limits_rhs_command = "cat %s | %s " %(openGLLimits,Filenames.remove_lhs_command)
        fetch_show_select_opengl_limits_command = "cat %s | awk '/%s:/{flag=1;next}/:.*/{flag=0}flag'  "%(openGLLimits,limitValue)

        opengl_limits_lhs = []
        opengl_limits_rhs = []
        select_opengl_limits_file = " "
        if "Show All OpenGL Hardware Core Limits" in limitValue or "Show All OpenGL Hardware Compatible Limits" in limitValue:

            fetch_show_limits_lhs_process = subprocess.Popen(fetch_show_opengl_limits_lhs_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
            opengl_limits_lhs = fetch_show_limits_lhs_process.communicate()[0].splitlines()
            fetch_show_limits_rhs_process = subprocess.Popen(fetch_show_opengl_limits_rhs_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
            opengl_limits_rhs = fetch_show_limits_rhs_process.communicate()[0].splitlines()

            select_opengl_limits_file = openGLLimits
        else:
            with open(Filenames.select_opengl_limits_file,"w") as file:
                fetch_show_select_opengl_limits_process = subprocess.Popen(fetch_show_select_opengl_limits_command,shell=True,stdout=file,universal_newlines=True)
                fetch_show_select_opengl_limits_process.communicate()

            fetch_show_select_opengl_limits_lhs_command = "cat %s | %s " %(Filenames.select_opengl_limits_file,Filenames.remove_rhs_Command)
            fetch_show_select_opengl_limits_rhs_command = "cat %s | %s " %(Filenames.select_opengl_limits_file,Filenames.remove_lhs_command)
            fetch_show_select_opengl_limits_lhs_process = subprocess.Popen(fetch_show_select_opengl_limits_lhs_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
            opengl_limits_lhs = fetch_show_select_opengl_limits_lhs_process.communicate()[0].splitlines()
            fetch_show_select_opengl_limits_rhs_process = subprocess.Popen(fetch_show_select_opengl_limits_rhs_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
            opengl_limits_rhs = fetch_show_select_opengl_limits_rhs_process.communicate()[0].splitlines()
            select_opengl_limits_file = Filenames.select_opengl_limits_file

        LimitsRHS,LimitRHSValue = appendLimitsRHS(select_opengl_limits_file,opengl_limits_rhs)

        Limits_Store.remove_all()
     #   TreeLimits.set_model(Limits_Store)
        groupName = None
        with open(select_opengl_limits_file,"r") as file:
            for i, line in enumerate(file):
       #         TreeLimits.expand_all()
                text = opengl_limits_lhs[i].strip(' ')
                if ("TEXTURE_FORMATS" in line or "SHADING_LANGUAGE" in line) and LimitRHSValue[i] == True:
                    try:
                    #    iter3 = Limits_Store.append(iter2, [text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                        iter3 = ExpandDataObject(text.strip('\n'), LimitsRHS[i].strip('\n'))
                        toprow.children.append(iter3)
                    except Exception:
                    #    iter3 = Limits_Store.append(None, [text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                        toprow = ExpandDataObject(text.strip('\n'), LimitsRHS[i].strip('\n'))
            #         toprow.children.append(iter3)
                    finally:
                        pass
                elif "      " in line and LimitRHSValue[i] == False and ":" not in line:
                #    Limits_Store.append(iter3, [text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                    iter4 = ExpandDataObject(text.strip('\n'), LimitsRHS[i].strip('\n'))
                    iter3.children.append(iter4)
                else:
                    if ":" in line:
                        k = 0
                        text = opengl_limits_lhs[i]
                        count += 1
                    #    iter2 = Limits_Store.append(None,[text.strip('\n'), LimitsRHS[i].strip('\n'), const.BGCOLOR3])
                        Limits_Store.append(toprow)
                        toprow = ExpandDataObject(text.strip('\n'), LimitsRHS[i].strip('\n'))
                    #    toprow.children.append(iter2)
                        continue
                    if count > 0 and "    " in line:
                    #    Limits_Store.append(iter2, [text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                        iter2_1 = ExpandDataObject(text.strip('\n'), LimitsRHS[i].strip('\n'))
                        toprow.children.append(iter2_1)
                    else:
                    #    Limits_Store.append(None, [text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                        toprow = ExpandDataObject(text.strip('\n'), LimitsRHS[i].strip('\n'))
                        Limits_Store.append(toprow)
            Limits_Store.append(toprow)

    def radcall2(dropdown,dummy,List,filename,Store,tree,filter):
        selected =dropdown.props.selected_item
        value = 0
        if selected is not None:
            value = dropdown.props.selected
        
        GL_All = []

    #    List = copyContentsFromFile("/tmp/gpu-viewer/Vendor1.txt")
        List = [i.strip(' ') for i in List]
        List = [i.strip('\n ') for i in List]
    #    List.insert(0, " ALL")
        with open(filename, "r") as file1:
            for line in file1:
                if List[int(value)] == "Total":
                    GL_All.append(line)
                elif List[int(value)] != "Total":
                    if "_%s_" % List[int(value)] in line:
                        GL_All.append(line)

        Store.remove_all()
    #    tree.set_model(filter)

    #    for i in range(len(List)):
    #        if int(value) == i:
    #            frame4.set_label(List[i])

        count = len(GL_All)
        for i in range(count):
            text = GL_All[i].strip(' ')
            Store.append(DataObject2(text.strip('\n')))

    def getVendorList(filename):

        fetch_vendor_gl_extension_command = "cat %s | awk 'gsub(/GL_|_.*/,'true')'| uniq " %filename
        fetch_vendor_glx_extension_command = "cat %s | awk 'gsub(/GLX_|_.*/,'true')'| uniq " %filename
        fetch_vendor_gl_es_extension_command = "cat /tmp/gpu-viewer/Vendor.txt | sort | uniq | grep -v GLX | grep -v GL$"
        fetch_vendor_egl_extension_command = "cat %s | awk 'gsub(/EGL_|_.*/,'true')'| sort | uniq" %filename

        with open("/tmp/gpu-viewer/Vendor.txt","w") as file:
            fetch_vendor_gl_extension_process = subprocess.Popen(fetch_vendor_gl_extension_command,shell=True,stdout=file,universal_newlines=True)
            fetch_vendor_gl_extension_process.communicate()
            fetch_vendor_glx_extension_process = subprocess.Popen(fetch_vendor_glx_extension_command,shell=True,stdout=file,universal_newlines=True)
            fetch_vendor_glx_extension_process.communicate()

        fetch_vendor_gl_es_extension_process = subprocess.Popen(fetch_vendor_gl_es_extension_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
        vendorList = fetch_vendor_gl_es_extension_process.communicate()[0].splitlines()

        if 'egl' in filename:
            fetch_vendor_egl_extension_list_process = subprocess.Popen(fetch_vendor_egl_extension_command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
            vendorList = fetch_vendor_egl_extension_list_process.communicate()[0].splitlines()

        vCount = []

        vendorList = [i.strip(' ') for i in vendorList]
        vendorList = [i.strip('\n ') for i in vendorList]
        vendorList.insert(0, "Total")

        with open(filename, "r") as file1:
            for i in range(len(vendorList)):
                file1.seek(0, 0)
                GL_All = []
                for line in file1:
                    if vendorList[i] == "Total":
                        GL_All.append(line)
                    elif vendorList[i] != "Total":
                        if "_%s_" % vendorList[i] in line:
                            GL_All.append(line)
                vCount.append(len(GL_All))

        NewList = []
        for i in range(len(vendorList)):
            NewList.append("%s (%d)" % (vendorList[i], vCount[i]))

        return NewList, vendorList

#----------------------------------Filter -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    def _on_search_method_changed(search_entry,filterColumn):
        filterColumn.changed(Gtk.FilterChange.DIFFERENT)

    def _do_filter_opengl_extension_view(item, filter_list_model):
        search_text_widget = entry_gl.get_text()
        return search_text_widget.upper() in item.column1.upper()

    def _do_filter_opengl_es_extension_view(item, filter_list_model):
        search_text_widget = entry_es.get_text()
        return search_text_widget.upper() in item.column1.upper()

    def _do_filter_egl_extension_view(item, filter_list_model):
        search_text_widget = entry_egl.get_text()
        return search_text_widget.upper() in item.column1.upper()

# ------------------------------ Check es2_info Supported ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def es2_infoSupported():
        es2_info_check_process = subprocess.Popen("es2_info",shell=True,stdout=subprocess.PIPE)
        es2_info_check_process.communicate()
        return es2_info_check_process.returncode == 0

#--------------------------------- Creating the OpenGL Information Tab ----------------------------------------------------------------------------------------------------------------------------------------------------------------

 #   frame_opengl_info = Gtk.Frame()
    opengl_box = Gtk.Box(orientation=1,spacing=10)
#    setMargin(opengl_box,0,0,1)
    tab.append(opengl_box)
#    opengl_box.append(frame_opengl_info)

    openglColumnView = Gtk.ColumnView()
    openglColumnView.props.show_row_separators = True
    openglColumnView.props.single_click_activate = False
    openglColumnView.props.show_column_separators = False
    factoryOpenglLhs = Gtk.SignalListItemFactory()
    factoryOpenglLhs.connect("setup", setup)
    factoryOpenglLhs.connect("bind", bind_column1)
    factoryOpenglRhs = Gtk.SignalListItemFactory()
    factoryOpenglRhs.connect("setup", setup)
    factoryOpenglRhs.connect("bind", bind_column2)

    openglColumn1 = Gtk.ColumnViewColumn.new("OpenGL Information")
    openglColumn1.set_factory(factoryOpenglLhs)
    openglColumn1.set_resizable(True)
    openglColumnView.append_column(openglColumn1)

    openglColumn2 = Gtk.ColumnViewColumn.new("Details")
    openglColumn2.set_factory(factoryOpenglRhs)
    openglColumn2.set_expand(True)
    openglColumnView.append_column(openglColumn2)

    openglSelection = Gtk.SingleSelection()
    opengl_info_list = Gio.ListStore.new(DataObject)
    openglSelection.set_model(opengl_info_list)
    openglColumnView.set_model(openglSelection)

    opengl_info_scrollbar = create_scrollbar(openglColumnView)
    opengl_box.append(opengl_info_scrollbar)
    opengl_info()

#-------------------------------- Creating the show OpenGL Limits Limits------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    grid_opengl_buttons = Gtk.Grid()
    opengl_box.append(grid_opengl_buttons)

    opengl_limits_button = Gtk.Button.new_with_label("Show OpenGL Limits")
    opengl_limits_button.connect("clicked",clickme)
    setMargin(opengl_limits_button,20,10,10)
    opengl_limits_button.add_css_class(css_class = "suggested-action")
    opengl_limits_button.add_css_class(css_class = "toolbar")
    grid_opengl_buttons.attach(opengl_limits_button,0,0,1,1 )

# ---------------------------------- Creating the Logo ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    fetch_gpu_renderer_command = "cat %s | grep renderer | grep -o :.* | grep -o ' .*'" %(Filenames.opengl_device_info_file)
    fetch_gpu_renderer_process = subprocess.Popen(fetch_gpu_renderer_command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    gpu_renderer = fetch_gpu_renderer_process.communicate()[0].decode("utf-8")
    vendorImg = getGpuImage(gpu_renderer)
    vendor_pic_img = Gtk.Picture.new_for_pixbuf(vendorImg)
    setMargin(vendor_pic_img,100,10,10)
    grid_opengl_buttons.attach_next_to(vendor_pic_img,opengl_limits_button,Gtk.PositionType.RIGHT,1,1)

# ------------------------------------ Creating the show Framebuffer ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    opengl_framebuffer_button = Gtk.Button.new_with_label("Show GLX Frame Buffer Configuration")
    opengl_framebuffer_button.connect("clicked",FrameBuffer)
    opengl_framebuffer_button.add_css_class(css_class = "suggested-action")
    opengl_framebuffer_button.add_css_class(css_class = "toolbar")

    setMargin(opengl_framebuffer_button,100,10,10)
    grid_opengl_buttons.attach_next_to(opengl_framebuffer_button,vendor_pic_img,Gtk.PositionType.RIGHT,1,1)

# ------------------------------------ creating the OpenGL extension ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    frame_extension = Gtk.Frame()
    adw_toolbar_view = Adw.ToolbarView.new()
    opengl_box.append(adw_toolbar_view)
    grid_extension = Gtk.Grid()
 #   adw_toolbar_view.set_content(grid_extension)

#    extensions_notebook = Gtk.Notebook()
    extensions_notebook = Adw.ViewStack.new()
    adw_toolbar_view.set_content(extensions_notebook)
 #   grid_extension.attach(extensions_notebook,0,0,1,1)

    opengl_extension_logo = fetchImageFromUrl(const.OPEN_GL_PNG,250,50,False)
    opengl_extension_box = create_tab(extensions_notebook,"OpenGL", "OpenGL", const.ICON_HEIGHT, False)
 #   extensions_notebook.append_page(opengl_extension_box,Gtk.Picture.new_for_pixbuf(opengl_extension_logo))
 #   page1 = extensions_notebook.get_page(opengl_extension_box)
 #   page1.set_property("tab-expand",True)
    
    extensions_switcher = Adw.ViewSwitcher.new()
    extensions_switcher.set_stack(stack=extensions_notebook)
    extensions_switcher.set_policy(1)
    adw_toolbar_view.add_top_bar(extensions_switcher)

    grid_opengl_extension = Gtk.Box.new(Gtk.Orientation.VERTICAL,2)
    opengl_extension_box.append(grid_opengl_extension)

    openglExtensionColumnView = Gtk.ColumnView()
    openglExtensionColumnView.props.show_row_separators = True
    openglExtensionColumnView.props.single_click_activate = False
    openglExtensionColumnView.props.show_column_separators = True
    factoryOpenglExtensionLhs = Gtk.SignalListItemFactory()
    factoryOpenglExtensionLhs.connect("setup", setup)
    factoryOpenglExtensionLhs.connect("bind", bind_column1)

    openglExtensionsColumn1 = Gtk.ColumnViewColumn.new("")
    openglExtensionsColumn1.set_factory(factoryOpenglExtensionLhs)
    openglExtensionsColumn1.set_expand(True)
    openglExtensionColumnView.append_column(openglExtensionsColumn1)


    openglExtensionsSelection = Gtk.SingleSelection()
    opengl_extension_list = Gio.ListStore.new(DataObject2)
    filterOpenglExtensionsListStore = Gtk.FilterListModel(model=opengl_extension_list)
    filter_open_extensions = Gtk.CustomFilter.new(_do_filter_opengl_extension_view, filterOpenglExtensionsListStore)
    filterOpenglExtensionsListStore.set_filter(filter_open_extensions)
    openglExtensionsSelection.set_model(filterOpenglExtensionsListStore)
    openglExtensionColumnView.set_model(openglExtensionsSelection)

#    frame_search_gl =Gtk.Frame()
    entry_gl = Gtk.SearchEntry()
    entry_gl.set_property("placeholder-text","Type here to filter extensions.....")
    entry_gl.connect("search-changed",_on_search_method_changed,filter_open_extensions)
    entry_gl.grab_focus()
 #   frame_search_gl.set_child(entry_gl)

#---------------------------- Getting OpenGL Extensions -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    with open(Filenames.opengl_vendor_gl_extension_file,"w") as file:
        fetch_vendor_gl_extension_process = subprocess.Popen(Filenames.fetch_opengl_vendor_extensions_command,shell=True,stdout=file,universal_newlines=True)
        fetch_vendor_gl_extension_process.communicate()
        fetch_vendor_glx_extension_process = subprocess.Popen(Filenames.fetch_openglx_vendor_extensions_command,shell=True,stdout=file,universal_newlines=True)
        fetch_vendor_glx_extension_process.communicate()

    Vendor_GL, vList = getVendorList(Filenames.opengl_vendor_gl_extension_file)

    vendor_gl_list = Gtk.StringList()
    vendor_dropdown_gl = Gtk.DropDown()
    vendor_dropdown_gl.set_model(vendor_gl_list)

    for i in range(len(Vendor_GL)):
        vendor_gl_list.append(Vendor_GL[i])
    
    vendor_dropdown_gl.connect('notify::selected-item', radcall2,vList,Filenames.opengl_vendor_gl_extension_file,opengl_extension_list,openglExtensionColumnView,opengl_extension_list)
    radcall2(vendor_dropdown_gl,0,vList,Filenames.opengl_vendor_gl_extension_file,opengl_extension_list,openglExtensionColumnView,opengl_extension_list)
    setMargin(grid_opengl_extension,2,2,2)
   
    grid_opengl_extension.append(vendor_dropdown_gl)
    opengl_extension_scrollbar = create_scrollbar(openglExtensionColumnView)
    entry_gl.add_css_class(css_class = "toolbar")
    grid_opengl_extension.append(opengl_extension_scrollbar)
    grid_opengl_extension.append(entry_gl)



#--------------------------- creating OpenGL ES Extension tab -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    openglESExtensionColumnView = Gtk.ColumnView()
    openglESExtensionColumnView.props.show_row_separators = True
    openglESExtensionColumnView.props.single_click_activate = False
    openglESExtensionColumnView.props.show_column_separators = True
    factoryOpenglESExtensionLhs = Gtk.SignalListItemFactory()
    factoryOpenglESExtensionLhs.connect("setup", setup)
    factoryOpenglESExtensionLhs.connect("bind", bind_column1)

    openglESExtensionsColumn1 = Gtk.ColumnViewColumn.new("")
    openglESExtensionsColumn1.set_factory(factoryOpenglESExtensionLhs)
    openglESExtensionsColumn1.set_expand(True)
    openglESExtensionColumnView.append_column(openglESExtensionsColumn1)


    openglESExtensionsSelection = Gtk.SingleSelection()
    opengl_es_extension_list = Gio.ListStore.new(DataObject2)
    filterOpenglESExtensionsListStore = Gtk.FilterListModel(model=opengl_es_extension_list)
    filter_open_es_extensions = Gtk.CustomFilter.new(_do_filter_opengl_es_extension_view, filterOpenglESExtensionsListStore)
    filterOpenglESExtensionsListStore.set_filter(filter_open_es_extensions)
    openglESExtensionsSelection.set_model(filterOpenglESExtensionsListStore)
    openglESExtensionColumnView.set_model(openglESExtensionsSelection)

    opengl_es_extension_logo = fetchImageFromUrl(const.OPEN_GL_ES_PNG,250,50,False)
    opengl_es_extension_box = create_tab(extensions_notebook,"OpenGL_ES", "OpenGL|ES", const.ICON_HEIGHT, False)
#    extensions_notebook.append_page(opengl_es_extension_box,Gtk.Picture.new_for_pixbuf(opengl_es_extension_logo))
#    extensions_page2 = extensions_notebook.get_page(opengl_es_extension_box)
 #   extensions_page2.set_property("tab-expand",True)

    grid_opengl_es_extension = Gtk.Box.new(Gtk.Orientation.VERTICAL,2)
    opengl_es_extension_box.append(grid_opengl_es_extension)

 #   setColumns(tree_opengl_es_extension,Title,const.MWIDTH,0.0)

    with open(Filenames.opengl_vendor_es_extension_file,"w") as file:
        fetch_vendor_es_extension_process = subprocess.Popen(Filenames.fetch_opengl_es_vendor_extensions_command,shell=True,stdout=file,universal_newlines=True)
        fetch_vendor_es_extension_process.communicate()
    
    Vendor_ES,vesList = getVendorList(Filenames.opengl_vendor_es_extension_file)

    entry_es = Gtk.SearchEntry()
    entry_es.set_property("placeholder-text","Type here to filter extensions.....")
    entry_es.connect("search-changed",_on_search_method_changed,filter_open_es_extensions)
    entry_es.add_css_class(css_class = "toolbar")
    entry_es.grab_focus()

    vendor_es_list = Gtk.StringList()
    vendor_dropdown_es = Gtk.DropDown()
    vendor_dropdown_es.set_model(vendor_es_list)
    setMargin(vendor_dropdown_es,2,1,2)
    for i in range(len(Vendor_ES)):
        vendor_es_list.append(Vendor_ES[i])

    radcall2(vendor_dropdown_es,0,vesList,Filenames.opengl_vendor_es_extension_file,opengl_es_extension_list,openglESExtensionColumnView,openglESExtensionsSelection)
    vendor_dropdown_es.connect("notify::selected-item", radcall2,vesList,Filenames.opengl_vendor_es_extension_file,opengl_es_extension_list,openglESExtensionColumnView,openglESExtensionsSelection)
    grid_opengl_es_extension.append(vendor_dropdown_es)
    opengl_es_extension_scrollbar = create_scrollbar(openglESExtensionColumnView)
    grid_opengl_es_extension.append(opengl_es_extension_scrollbar)
    grid_opengl_es_extension.append(entry_es)
 #   opengl_extension_box.append(opengl_es_extension_scrollbar)


    #------------------------------------- Creating EGL Extension -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    if es2_infoSupported():
        eglExtensionColumnView = Gtk.ColumnView()
        eglExtensionColumnView.props.show_row_separators = True
        eglExtensionColumnView.props.single_click_activate = False
        eglExtensionColumnView.props.show_column_separators = True
        factoryEglExtensionLhs = Gtk.SignalListItemFactory()
        factoryEglExtensionLhs.connect("setup", setup)
        factoryEglExtensionLhs.connect("bind", bind_column1)

        eglExtensionsColumn1 = Gtk.ColumnViewColumn.new("")
        eglExtensionsColumn1.set_factory(factoryEglExtensionLhs)
        eglExtensionsColumn1.set_expand(True)
        eglExtensionColumnView.append_column(eglExtensionsColumn1)


        eglExtensionsSelection = Gtk.SingleSelection()
        egl_extension_list = Gio.ListStore.new(DataObject2)
        filterEglExtensionsListStore = Gtk.FilterListModel(model=egl_extension_list)
        filter_egl_extensions = Gtk.CustomFilter.new(_do_filter_egl_extension_view, filterEglExtensionsListStore)
        filterEglExtensionsListStore.set_filter(filter_egl_extensions)
        eglExtensionsSelection.set_model(filterEglExtensionsListStore)
        eglExtensionColumnView.set_model(eglExtensionsSelection)

    #    egl_extension_list = Gtk.ListStore(str,str)
    #    egl_extension_list_filter = egl_extension_list.filter_new()
    #    tree_egl_extension = Gtk.TreeView.new_with_model(egl_extension_list_filter)
     #   tree_egl_extension.set_property("enable-grid-lines", 1)
     #   tree_egl_extension.set_headers_visible(False)
     #   egl_extension_list_filter.set_visible_func(searchTreeExtEGL)

        egl_extension_logo = fetchImageFromUrl(const.EGL_PNG,200,50,False)
        egl_extension_box = create_tab(extensions_notebook,"Egl_logo","EGL",10,True)
   #     extensions_notebook.append_page(egl_extension_box,Gtk.Picture.new_for_pixbuf(egl_extension_logo))
    #    extensions_page3 = extensions_notebook.get_page(egl_extension_box)
    #    extensions_page3.set_property("tab-expand",True)

        grid_egl_extension = Gtk.Box.new(Gtk.Orientation.VERTICAL,2)
        egl_extension_box.append(grid_egl_extension)

     #   setColumns(tree_egl_extension,Title,const.MWIDTH,0.0)

        with open(Filenames.egl_vendor_extension_file,"w") as file:
            fetch_vendor_egl_extension_process = subprocess.Popen(Filenames.fetch_egl_vendor_extension_command,shell=True,stdout=file,universal_newlines=True)
            fetch_vendor_egl_extension_process.communicate()

        Vendor_EGL,veglList = getVendorList(Filenames.egl_vendor_extension_file)

        vendor_egl_list = Gtk.StringList()
        vendor_dropdown_egl = Gtk.DropDown()
        vendor_dropdown_egl.set_model(vendor_egl_list)
        setMargin(vendor_dropdown_egl,2,1,2)
        for i in range(len(Vendor_EGL)):
            vendor_egl_list.append(Vendor_EGL[i])
        
        vendor_dropdown_egl.set_selected(0)
        entry_egl = Gtk.SearchEntry()
        entry_egl.set_property("placeholder-text","Type here to filter extensions.....")
        entry_egl.connect("search-changed",_on_search_method_changed,filter_egl_extensions)
        entry_egl.add_css_class(css_class = "toolbar")
        entry_egl.grab_focus()

        radcall2(vendor_dropdown_egl,0,veglList,Filenames.egl_vendor_extension_file,egl_extension_list,eglExtensionColumnView,egl_extension_list)
        vendor_dropdown_egl.connect('notify::selected-item', radcall2,veglList,Filenames.egl_vendor_extension_file,egl_extension_list,eglExtensionColumnView,egl_extension_list)
        grid_egl_extension.append(vendor_dropdown_egl)
        egl_extension_scrollbar = create_scrollbar(eglExtensionColumnView)
        grid_egl_extension.append(egl_extension_scrollbar)
        grid_egl_extension.append(entry_egl)

    return tab
    # ------------------------------------------- Search Text Box GL ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------