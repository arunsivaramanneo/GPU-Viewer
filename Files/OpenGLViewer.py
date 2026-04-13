# Copyright (C) 2017-2026 Arun Sivaraman <arunsivaramanneo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import os
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

def OpenGL(self, tab):

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

# ------------------------------ Check es2_info Supported ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def es2_infoSupported():
        es2_info_check_process = subprocess.Popen("es2_info",shell=True,stdout=subprocess.PIPE)
        es2_info_check_process.communicate()
        return es2_info_check_process.returncode == 0

    def create_sidebar_row(label_text, sensitive=True, css_class=None):
        row = Gtk.ListBoxRow()
        label = Gtk.Label.new(label_text)
        label.set_xalign(0)
        label.set_margin_start(12)
        label.set_margin_end(12)
        label.set_margin_top(8)
        label.set_margin_bottom(8)
        if css_class:
            label.add_css_class(css_class=css_class)
        row.set_child(label)
        row.set_sensitive(sensitive)
        return row

    def create_limits_page(core_file, core_lhs_file, compat_file, compat_lhs_file,
                              core_label, compat_label,
                              core_command, core_lhs_command,
                              compat_command, compat_lhs_command):
        if not os.path.exists(core_file) or not os.path.exists(core_lhs_file):
            createMainFile(core_file, core_command)
            createMainFile(core_lhs_file, core_lhs_command)

        if not os.path.exists(compat_file) or not os.path.exists(compat_lhs_file):
            createMainFile(compat_file, compat_command)
            createMainFile(compat_lhs_file, compat_lhs_command)

        limits_page = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        limits_page.add_css_class('toolbar')

        limitsList = Gtk.StringList()
        limitsDropDown = Gtk.DropDown()
        limitsDropDown.set_model(limitsList)

        profile_group = Adw.ToggleGroup.new()
        core_toggle = Adw.Toggle.new()
        core_toggle.set_name("core")
        profile_group.add(core_toggle)
        compat_toggle = Adw.Toggle.new()
        compat_toggle.set_name("compat")
        profile_group.add(compat_toggle)

        core_button = Gtk.ToggleButton.new_with_label("Core")
        compat_button = Gtk.ToggleButton.new_with_label("Compatibility")
        core_button.set_active(True)
        core_button.set_valign(Gtk.Align.CENTER)
        compat_button.set_valign(Gtk.Align.CENTER)

        toggle_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        toggle_box.set_valign(Gtk.Align.CENTER)
        toggle_box.append(core_button)
        toggle_box.append(compat_button)

        top_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)
        top_box.set_hexpand(True)
        top_box.append(limitsDropDown)
        top_box.append(toggle_box)
        limits_page.append(top_box)

        limitsColumnView = Gtk.ColumnView()
        limitsColumnView.props.show_row_separators = True
        limitsColumnView.props.show_column_separators = False

        factory_limits = Gtk.SignalListItemFactory()
        factory_limits.connect("setup", setup_expander)
        factory_limits.connect("bind", bind_expander)

        factory_limits_value = Gtk.SignalListItemFactory()
        factory_limits_value.connect("setup", setup)
        factory_limits_value.connect("bind", bind1)

        limitSelection = Gtk.SingleSelection()
        limits_store = Gio.ListStore.new(ExpandDataObject)
        limitModel = Gtk.TreeListModel.new(limits_store, False, True, add_tree_node)
        limitSelection.set_model(limitModel)

        limitsColumnView.set_model(limitSelection)
        limitColumnLhs = Gtk.ColumnViewColumn.new("OpenGL Hardware Limits", factory_limits)
        limitColumnLhs.set_resizable(True)
        limitColumnRhs = Gtk.ColumnViewColumn.new("Value", factory_limits_value)
        limitColumnRhs.set_expand(True)
        limitsColumnView.append_column(limitColumnLhs)
        limitsColumnView.append_column(limitColumnRhs)

        current_mode = {"profile": "core", "file": core_file, "lhs": core_lhs_file, "label": core_label}

        def load_limits_profile(profile):
            if profile == "core":
                createMainFile(core_file, core_command)
                createMainFile(core_lhs_file, core_lhs_command)
                current_mode["file"] = core_file
                current_mode["lhs"] = core_lhs_file
                current_mode["label"] = core_label
            else:
                createMainFile(compat_file, compat_command)
                createMainFile(compat_lhs_file, compat_lhs_command)
                current_mode["file"] = compat_file
                current_mode["lhs"] = compat_lhs_file
                current_mode["label"] = compat_label

            new_model = Gtk.StringList()
            new_model.append(current_mode["label"])
            with open(current_mode["lhs"], "r") as file1:
                for line in file1:
                    if ":" in line:
                        text = line[:-2]
                        new_model.append(text.strip(" "))
            limitsDropDown.set_model(new_model)
            limitsDropDown.set_selected(0)
            showLimits(limitsDropDown, 0, limits_store, limitsColumnView, current_mode["file"])

        def sync_toggle_buttons(profile):
            core_button.handler_block_by_func(on_core_toggled)
            compat_button.handler_block_by_func(on_compat_toggled)
            core_button.set_active(profile == "core")
            compat_button.set_active(profile == "compat")
            core_button.handler_unblock_by_func(on_core_toggled)
            compat_button.handler_unblock_by_func(on_compat_toggled)

        def on_profile_group_changed(group, pspec):
            profile = group.get_active_name()
            if not profile:
                return
            sync_toggle_buttons(profile)
            load_limits_profile(profile)

        def on_core_toggled(button):
            if button.get_active():
                profile_group.set_active_name("core")

        def on_compat_toggled(button):
            if button.get_active():
                profile_group.set_active_name("compat")

        core_button.connect("toggled", on_core_toggled)
        compat_button.connect("toggled", on_compat_toggled)
        profile_group.connect("notify::active-name", on_profile_group_changed)

        load_limits_profile("core")

        limitsDropDown.connect("notify::selected-item", showLimits, limits_store, limitsColumnView, current_mode["file"])
        limits_page.append(create_scrollbar(limitsColumnView))
        return limits_page

    def create_framebuffer_page(visuals_command, fbconfig_command):
        page = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        page.add_css_class('toolbar')

        def fetch_lines(command):
            fetch_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
            return [line for line in fetch_process.communicate()[0].splitlines() if line.strip()]

        visuals_lines = fetch_lines(visuals_command)
        fbconfig_lines = fetch_lines(fbconfig_command)

        visuals_count = len(visuals_lines)
        fbconfig_count = len(fbconfig_lines)

        profile_group = Adw.ToggleGroup.new()
        visuals_toggle = Adw.Toggle.new()
        visuals_toggle.set_name("glx-visuals")
        profile_group.add(visuals_toggle)
        fbconfig_toggle = Adw.Toggle.new()
        fbconfig_toggle.set_name("glx-fbconfig")
        profile_group.add(fbconfig_toggle)

        visuals_button = Gtk.ToggleButton.new_with_label(f"GLX Visuals ({visuals_count})")
        fbconfig_button = Gtk.ToggleButton.new_with_label(f"GLX FBConfig ({fbconfig_count})")
        visuals_button.set_active(True)
        visuals_button.set_valign(Gtk.Align.CENTER)
        fbconfig_button.set_valign(Gtk.Align.CENTER)

        toggle_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        toggle_box.set_valign(Gtk.Align.CENTER)
        toggle_box.append(visuals_button)
        toggle_box.append(fbconfig_button)

        page.append(toggle_box)

        frameBufferColumnView = Gtk.ColumnView()
        frameBufferColumnView.props.show_row_separators = True
        frameBufferColumnView.props.show_column_separators = True
        frameBufferColumnView.set_vexpand(True)
        frameBufferColumnView.set_hexpand(True)

        all_lines = visuals_lines + fbconfig_lines
        max_columns = 0
        for line in all_lines:
            tokens = line.strip().split()
            if len(tokens) > max_columns:
                max_columns = len(tokens)

        class FramebufferRow(GObject.GObject):
            def __init__(self, values):
                super(FramebufferRow, self).__init__()
                for index, value in enumerate(values, start=1):
                    setattr(self, f"data{index}", value)
                for index in range(len(values) + 1, max_columns + 1):
                    setattr(self, f"data{index}", "")

        def make_bind(column_index):
            def bind(widget, item):
                label = item.get_child()
                obj = item.get_item()
                label.set_text(getattr(obj, f"data{column_index}", ""))
            return bind

        headings = const.FRAMEBUFFERLIST
        if max_columns == 0:
            factory_fb = Gtk.SignalListItemFactory()
            factory_fb.connect("setup", setup)
            factory_fb.connect("bind", bind_column1)
            fbColumn = Gtk.ColumnViewColumn.new("Framebuffer Data", factory_fb)
            fbColumn.set_expand(True)
            frameBufferColumnView.append_column(fbColumn)

            fb_selection = Gtk.SingleSelection()
            fb_store = Gio.ListStore.new(DataObject2)
            fb_selection.set_model(fb_store)
            frameBufferColumnView.set_model(fb_selection)
        else:
            fb_selection = Gtk.SingleSelection()
            fb_store = Gio.ListStore.new(FramebufferRow)
            fb_selection.set_model(fb_store)
            frameBufferColumnView.set_model(fb_selection)

            for index in range(1, max_columns + 1):
                factory = Gtk.SignalListItemFactory()
                factory.connect("setup", setup)
                factory.connect("bind", make_bind(index))
                column_name = headings[index - 1] if index <= len(headings) else f"Column {index}"
                column = Gtk.ColumnViewColumn.new(column_name, factory)
                column.set_resizable(True)
                if index == max_columns:
                    column.set_expand(True)
                frameBufferColumnView.append_column(column)

        def populate_lines(lines):
            fb_store.remove_all()
            if max_columns == 0:
                for line in lines:
                    fb_store.append(DataObject2(line))
            else:
                for line in lines:
                    tokens = line.strip().split()
                    fb_store.append(FramebufferRow(tokens))

        def set_active_profile(profile):
            if profile == "glx-visuals":
                populate_lines(visuals_lines)
            else:
                populate_lines(fbconfig_lines)

        def sync_toggle_buttons(profile):
            visuals_button.handler_block_by_func(on_visuals_toggled)
            fbconfig_button.handler_block_by_func(on_fbconfig_toggled)
            visuals_button.set_active(profile == "glx-visuals")
            fbconfig_button.set_active(profile == "glx-fbconfig")
            visuals_button.handler_unblock_by_func(on_visuals_toggled)
            fbconfig_button.handler_unblock_by_func(on_fbconfig_toggled)

        def on_group_changed(group, pspec):
            profile = group.get_active_name()
            if not profile:
                return
            sync_toggle_buttons(profile)
            set_active_profile(profile)

        def on_visuals_toggled(button):
            if button.get_active():
                profile_group.set_active_name("glx-visuals")

        def on_fbconfig_toggled(button):
            if button.get_active():
                profile_group.set_active_name("glx-fbconfig")

        visuals_button.connect("toggled", on_visuals_toggled)
        fbconfig_button.connect("toggled", on_fbconfig_toggled)
        profile_group.connect("notify::active-name", on_group_changed)

        set_active_profile("glx-visuals")

        page.append(create_scrollbar(frameBufferColumnView))
        return page

    def create_extensions_page():
        page = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        page.add_css_class('toolbar')

        extensionColumnView = Gtk.ColumnView()
        extensionColumnView.props.show_row_separators = True
        extensionColumnView.props.single_click_activate = False
        extensionColumnView.props.show_column_separators = False

        factory_extension = Gtk.SignalListItemFactory()
        factory_extension.connect("setup", setup)
        factory_extension.connect("bind", bind_column1)

        extensionColumn = Gtk.ColumnViewColumn.new("Extensions", factory_extension)
        extensionColumn.set_expand(True)
        extensionColumnView.append_column(extensionColumn)

        extensionSelection = Gtk.SingleSelection()
        extension_list = Gio.ListStore.new(DataObject2)

        search_entry = Gtk.SearchEntry()
        search_entry.set_property("placeholder-text", "Type here to filter extensions.....")
        search_entry.add_css_class(css_class='toolbar')

        def filter_func(item, filter_list_model):
            search_text_widget = search_entry.get_text()
            return search_text_widget.upper() in item.column1.upper()

        filterExtensionListStore = Gtk.FilterListModel(model=extension_list)
        filterExtensions = Gtk.CustomFilter.new(filter_func, filterExtensionListStore)
        filterExtensionListStore.set_filter(filterExtensions)
        extensionSelection.set_model(filterExtensionListStore)
        extensionColumnView.set_model(extensionSelection)

        vendor_list = Gtk.StringList()
        vendor_dropdown = Gtk.DropDown()
        vendor_dropdown.set_model(vendor_list)
        setMargin(vendor_dropdown, 2, 1, 2)

        current_type = {"name": "OpenGL", "file": Filenames.opengl_vendor_gl_extension_file}
        opengl_profile = {"mode": "core"}

        type_group = Adw.ToggleGroup.new()
        opengl_type_toggle = Adw.Toggle.new()
        opengl_type_toggle.set_name("OpenGL")
        type_group.add(opengl_type_toggle)
        opengles_type_toggle = Adw.Toggle.new()
        opengles_type_toggle.set_name("OpenGL ES")
        type_group.add(opengles_type_toggle)
        egl_type_toggle = Adw.Toggle.new()
        egl_type_toggle.set_name("EGL")
        type_group.add(egl_type_toggle)

        opengl_button = Gtk.ToggleButton.new_with_label("OpenGL")
        opengles_button = Gtk.ToggleButton.new_with_label("OpenGL ES")
        egl_button = Gtk.ToggleButton.new_with_label("EGL")
        opengl_button.set_active(True)
        opengl_button.set_valign(Gtk.Align.CENTER)
        opengles_button.set_valign(Gtk.Align.CENTER)
        egl_button.set_valign(Gtk.Align.CENTER)

        type_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        type_box.set_valign(Gtk.Align.CENTER)
        type_box.append(opengl_button)
        type_box.append(opengles_button)
        type_box.append(egl_button)
        page.append(type_box)

        profile_group = Adw.ToggleGroup.new()
        core_profile_toggle = Adw.Toggle.new()
        core_profile_toggle.set_name("core")
        profile_group.add(core_profile_toggle)
        compat_profile_toggle = Adw.Toggle.new()
        compat_profile_toggle.set_name("compat")
        profile_group.add(compat_profile_toggle)

        core_button = Gtk.ToggleButton.new_with_label("Core")
        compat_button = Gtk.ToggleButton.new_with_label("Compatibility")
        core_button.set_active(True)
        core_button.set_valign(Gtk.Align.CENTER)
        compat_button.set_valign(Gtk.Align.CENTER)

        profile_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        profile_box.set_valign(Gtk.Align.CENTER)
        profile_box.append(core_button)
        profile_box.append(compat_button)

        vendor_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)
        vendor_box.set_hexpand(True)
        vendor_box.set_halign(Gtk.Align.START)
        vendor_box.append(vendor_dropdown)
        vendor_box.append(profile_box)

        def prepare_opengl_extension_file(profile):
            def write_lines(lines):
                with open(Filenames.opengl_vendor_gl_extension_file, "w") as file:
                    file.write("\n".join(lines))

            def collect_section(start_marker, stop_markers):
                lines = []
                writing = False
                with open(Filenames.opengl_outpuf_file, "r") as src:
                    for raw_line in src:
                        line = raw_line.strip()
                        if writing and any(line.startswith(stop) for stop in stop_markers):
                            break
                        if writing:
                            if line.startswith("GL_"):
                                lines.append(line)
                        elif line.startswith(start_marker):
                            writing = True
                return lines

            if profile == "core":
                lines = collect_section(
                    "OpenGL core profile extensions:",
                    ["OpenGL compatibility profile extensions:", "OpenGL extensions:", "OpenGL ES profile"]
                )
            else:
                lines = collect_section(
                    "OpenGL compatibility profile extensions:",
                    ["OpenGL ES profile", "OpenGL core profile extensions:", "OpenGL extensions:"]
                )
                if not lines:
                    lines = collect_section(
                        "OpenGL extensions:",
                        ["OpenGL ES profile"]
                    )

            write_lines(sorted(lines))

        def prepare_type_file(type_name):
            current_type["name"] = type_name
            if type_name == "OpenGL":
                current_type["file"] = Filenames.opengl_vendor_gl_extension_file
                prepare_opengl_extension_file(opengl_profile["mode"])
            elif type_name == "OpenGL ES":
                current_type["file"] = Filenames.opengl_vendor_es_extension_file
                with open(current_type["file"], "w") as file:
                    fetch_process = subprocess.Popen(Filenames.fetch_opengl_es_vendor_extensions_command, shell=True, stdout=file, universal_newlines=True)
                    fetch_process.communicate()
            else:
                current_type["file"] = Filenames.egl_vendor_extension_file
                with open(current_type["file"], "w") as file:
                    fetch_process = subprocess.Popen(Filenames.fetch_egl_vendor_extension_command, shell=True, stdout=file, universal_newlines=True)
                    fetch_process.communicate()

        def refresh_vendors():
            VendorList, vendor_names = getVendorList(current_type["file"])
            new_vendor_model = Gtk.StringList()
            for item in VendorList:
                new_vendor_model.append(item)
            vendor_dropdown.set_model(new_vendor_model)
            vendor_dropdown.set_selected(0)
            return VendorList, vendor_names

        current_vendors = {"names": []}

        def update_extension_list():
            VendorList, vendor_names = refresh_vendors()
            current_vendors["names"] = vendor_names
            radcall2(vendor_dropdown, 0, vendor_names, current_type["file"], extension_list, extensionColumnView, extension_list)
            return VendorList, vendor_names

        def set_profile_visibility(type_name):
            profile_box.set_visible(type_name == "OpenGL")

        def sync_type_buttons(type_name):
            opengl_button.handler_block_by_func(on_opengl_toggled)
            opengles_button.handler_block_by_func(on_opengles_toggled)
            egl_button.handler_block_by_func(on_egl_toggled)
            opengl_button.set_active(type_name == "OpenGL")
            opengles_button.set_active(type_name == "OpenGL ES")
            egl_button.set_active(type_name == "EGL")
            opengl_button.handler_unblock_by_func(on_opengl_toggled)
            opengles_button.handler_unblock_by_func(on_opengles_toggled)
            egl_button.handler_unblock_by_func(on_egl_toggled)

        def on_type_group_changed(group, pspec):
            type_name = group.get_active_name()
            if not type_name:
                return
            sync_type_buttons(type_name)
            set_profile_visibility(type_name)
            prepare_type_file(type_name)
            update_extension_list()

        def on_opengl_toggled(button):
            if button.get_active():
                type_group.set_active_name("OpenGL")

        def on_opengles_toggled(button):
            if button.get_active():
                type_group.set_active_name("OpenGL ES")

        def on_egl_toggled(button):
            if button.get_active():
                type_group.set_active_name("EGL")

        def sync_profile_buttons(profile):
            core_button.handler_block_by_func(on_core_toggled)
            compat_button.handler_block_by_func(on_compat_toggled)
            core_button.set_active(profile == "core")
            compat_button.set_active(profile == "compat")
            core_button.handler_unblock_by_func(on_core_toggled)
            compat_button.handler_unblock_by_func(on_compat_toggled)

        def on_profile_group_changed(group, pspec):
            profile = group.get_active_name()
            if not profile:
                return
            sync_profile_buttons(profile)
            opengl_profile["mode"] = profile
            if current_type["name"] == "OpenGL":
                prepare_type_file("OpenGL")
                update_extension_list()

        def on_core_toggled(button):
            if button.get_active():
                profile_group.set_active_name("core")

        def on_compat_toggled(button):
            if button.get_active():
                profile_group.set_active_name("compat")

        opengl_button.connect("toggled", on_opengl_toggled)
        opengles_button.connect("toggled", on_opengles_toggled)
        egl_button.connect("toggled", on_egl_toggled)
        type_group.connect("notify::active-name", on_type_group_changed)
        type_group.set_active_name("OpenGL")

        core_button.connect("toggled", on_core_toggled)
        compat_button.connect("toggled", on_compat_toggled)
        profile_group.connect("notify::active-name", on_profile_group_changed)
        profile_group.set_active_name("core")

        vendor_dropdown.connect('notify::selected-item', lambda dropdown, *_: radcall2(dropdown, 0, current_vendors["names"], current_type["file"], extension_list, extensionColumnView, extension_list))

        prepare_type_file("OpenGL")
        current_type["name"] = "OpenGL"
        set_profile_visibility("OpenGL")
        update_extension_list()

        search_entry.connect("search-changed", _on_search_method_changed, filterExtensions)

        page.append(vendor_box)
        page.append(create_scrollbar(extensionColumnView))
        page.append(search_entry)
        return page

    def on_row_activated(listbox, row):
        tab_label = row.get_child()
        tab_name = tab_label.get_label()
        if not row.get_sensitive():
            return
        sidebar_target_names = {
            "OpenGL Information": "opengl-information",
            "OpenGL Limits": "opengl-limits",
            "Framebuffer Configuration": "framebuffer-configuration",
            "Extensions": "extensions",
        }
        child_name = sidebar_target_names.get(tab_name)
        if child_name is not None:
            content_stack.set_visible_child_name(child_name)

    opengl_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
    opengl_box.set_vexpand(True)
    opengl_box.set_hexpand(True)
    tab.append(opengl_box)

    split_view = Adw.NavigationSplitView.new()
    split_view.set_vexpand(True)
    split_view.set_hexpand(True)

    sidebar_listbox = Gtk.ListBox.new()
    sidebar_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
    sidebar_listbox.set_vexpand(True)
    sidebar_listbox.add_css_class(css_class="boxed-list")
    sidebar_listbox.add_css_class(css_class="card")
    sidebar_listbox.add_css_class(css_class="sidebar")
    sidebar_listbox.set_show_separators(True)

    content_stack = Gtk.Stack.new()
    content_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
    content_stack.set_vexpand(True)
    content_stack.set_hexpand(True)

    info_page = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
    info_page.set_vexpand(True)
    info_page.set_hexpand(True)
    info_page.set_halign(Gtk.Align.FILL)
    info_page.set_valign(Gtk.Align.FILL)

    openglColumnView = Gtk.ColumnView()
    openglColumnView.props.show_row_separators = True
    openglColumnView.props.single_click_activate = False
    openglColumnView.props.show_column_separators = False
    openglColumnView.set_vexpand(True)
    openglColumnView.set_hexpand(True)

    factoryOpenglLhs = Gtk.SignalListItemFactory()
    factoryOpenglLhs.connect("setup", setup)
    factoryOpenglLhs.connect("bind", bind_column1)
    factoryOpenglRhs = Gtk.SignalListItemFactory()
    factoryOpenglRhs.connect("setup", setup)
    factoryOpenglRhs.connect("bind", bind_column2)

    openglColumn1 = Gtk.ColumnViewColumn.new("OpenGL Information")
    openglColumn1.set_factory(factoryOpenglLhs)
    openglColumn1.set_expand(True)
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
    opengl_info_scrollbar.set_vexpand(True)
    opengl_info_scrollbar.set_hexpand(True)
    opengl_info_scrollbar.set_valign(Gtk.Align.FILL)
    opengl_info_scrollbar.set_min_content_height(440)
    opengl_info_scrollbar.set_min_content_width(520)

    info_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)
    info_box.set_hexpand(True)
    info_box.set_vexpand(True)
    info_box.append(opengl_info_scrollbar)
    info_page.append(info_box)

    opengl_info()

    limits_page = create_limits_page(
        Filenames.opengl_core_limits_file,
        Filenames.opengl_core_limits_lhs_file,
        Filenames.opengl_compat_limits_file,
        Filenames.opengl_compat_limits_lhs_file,
        "Show All OpenGL Hardware Core Limits",
        "Show All OpenGL Hardware Compatible Limits",
        Filenames.fetch_opengl_core_limits_command,
        Filenames.fetch_opengl_core_limits_lhs_command,
        Filenames.fetch_opengl_compat_limits_command,
        Filenames.fetch_opengl_compat_limits_lhs_command,
    )

    glx_visuals_command = "cat %s  | awk '/GLX Visuals.*/{flag=1;next}/GLXFBConfigs.*/{flag=0}flag' | awk '/----.*/{flag=1;next}flag' " %(Filenames.opengl_outpuf_file)
    glx_fbconfig_command = "cat %s | awk '/GLXFBConfigs.*/{flag=1;next}flag' | awk '/----.*/{flag=1;next}flag' " %(Filenames.opengl_outpuf_file)

    framebuffer_page = create_framebuffer_page(glx_visuals_command, glx_fbconfig_command)

    extensions_page = create_extensions_page()

    content_stack.add_titled(info_page, "opengl-information", "OpenGL Information")
    content_stack.add_titled(limits_page, "opengl-limits", "OpenGL Limits")
    content_stack.add_titled(framebuffer_page, "framebuffer-configuration", "Framebuffer Configuration")
    content_stack.add_titled(extensions_page, "extensions", "Extensions")

    sidebar_listbox.append(create_sidebar_row("OpenGL Information", True))
    sidebar_listbox.append(create_sidebar_row("OpenGL Limits", True))
    sidebar_listbox.append(create_sidebar_row("Framebuffer Configuration", True))
    sidebar_listbox.append(create_sidebar_row("Extensions", True))

    sidebar_scrolled_window = Gtk.ScrolledWindow.new()
    sidebar_scrolled_window.set_vexpand(True)
    sidebar_scrolled_window.set_hexpand(True)
    sidebar_scrolled_window.set_child(sidebar_listbox)

    sidebar_page = Adw.NavigationPage.new(sidebar_scrolled_window, "Sidebar")
    content_page = Adw.NavigationPage.new(content_stack, "Content")
    sidebar_page.set_vexpand(True)
    sidebar_page.set_hexpand(True)
    content_page.set_vexpand(True)
    content_page.set_hexpand(True)
    split_view.set_sidebar(sidebar_page)
    split_view.set_content(content_page)

    opengl_box.append(split_view)

    sidebar_listbox.connect("row-activated", on_row_activated)
    sidebar_listbox.select_row(sidebar_listbox.get_row_at_index(0))
    content_stack.set_visible_child_name("opengl-information")

    return tab
