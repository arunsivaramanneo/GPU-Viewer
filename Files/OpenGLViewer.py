import sys
import gi
import const
import Filenames
import subprocess
from FrameBuffer import FrameBuffer
gi.require_version('Gtk','4.0')

from gi.repository import Gtk

from Common import getScreenSize,createMainFile,create_scrollbar,setColumns,setMargin,copyContentsFromFile,setBackgroundColor,getGpuImage,fetchImageFromUrl,refresh_filter,appendLimitsRHS

Title = [""]
Title2 = ["OpenGL Information ", " Details"]
LimitsTitle = ["OpenGL Hardware Limits", "Value"]

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
                background_color = setBackgroundColor(i)
                opengl_info_list.append([text.strip('\n'), value_opengl_information_rhs[i].strip('\n'), background_color])
    
    def clickme(button):

        button.set_sensitive(False)

        createMainFile(Filenames.opengl_core_limits_file,Filenames.fetch_opengl_core_limits_command)

        createMainFile(Filenames.opengl_core_limits_lhs_file,Filenames.fetch_opengl_core_limits_lhs_command)

        LimitsWin = Gtk.Window()
        LimitsWin.set_title("OpenGL Hardware Limits")
        LimitsNotebook = Gtk.Notebook()
        LimitsWin.set_child(LimitsNotebook)
        LimitsCoreTab = Gtk.Box(spacing=10)
        LimitsNotebook.append_page(LimitsCoreTab,Gtk.Label(label="\tCore\t"))
        LimitsCoreFrame = Gtk.Frame()
        limitsCombo = Gtk.ComboBoxText()
        setMargin(limitsCombo,2,2,2)

        # get Combo box value

        limitsCombo.remove_all()
        with open(Filenames.opengl_core_limits_lhs_file,"r") as file1:
            for line in file1:
                if ":" in line:
                    text = line[:-2]
                    limitsCombo.append_text(text.strip(" "))

        limitsCombo.insert_text(0,"Show All OpenGL Hardware Core Limits")

        LimitsCoreTab.append(LimitsCoreFrame)
        LimitsGrid = Gtk.Grid()
        LimitsGrid.set_row_spacing(5)
        LimitsCoreFrame.set_child(LimitsGrid)
        LimitsGrid.attach(limitsCombo,0,0,1,1)
        LimitsCore_Store = Gtk.TreeStore(str, str, str)
        TreeCoreLimits = Gtk.TreeView.new_with_model(LimitsCore_Store)
        TreeCoreLimits.set_property("enable-grid-lines",1)


        limitsCombo.connect("changed",showLimits, LimitsCore_Store, TreeCoreLimits,Filenames.opengl_core_limits_file)
        limitsCombo.set_active(0)

    #    showLimits(LimitRHSValue, LimitsRHS, LimitsCore_Store, TreeCoreLimits,"/tmp/gpu-viewer/OpenGLCoreLimitsLHS.txt")

        setColumns(TreeCoreLimits, LimitsTitle, const.MWIDTH,0.0)
        LimitsCoreScrollbar = create_scrollbar(TreeCoreLimits)
        LimitsGrid.attach_next_to(LimitsCoreScrollbar,limitsCombo,Gtk.PositionType.BOTTOM,1,1)

        createMainFile(Filenames.opengl_compat_limits_file,Filenames.fetch_opengl_compat_limits_command)

        createMainFile(Filenames.opengl_compat_limits_lhs_file,Filenames.fetch_opengl_compat_limits_lhs_command)

        LimitsCompatTab = Gtk.Box(spacing=10)
        LimitsNotebook.append_page(LimitsCompatTab,Gtk.Label(label="    Compat.\t"))
        LimitsCompatFrame = Gtk.Frame()
        limitsCompatCombo = Gtk.ComboBoxText()

        limitsCompatCombo.remove_all()
        with open(Filenames.opengl_compat_limits_lhs_file,"r") as file1:
            for line in file1:
                if ":" in line:
                    text = line[:-2]
                    limitsCompatCombo.append_text(text.strip(" "))

        limitsCompatCombo.insert_text(0,"Show All OpenGL Hardware Compatible Limits")

        LimitsCompatTab.append(LimitsCompatFrame)
        limitsCompatGrid = Gtk.Grid()
        limitsCompatGrid.set_row_spacing(5)
        LimitsCompatFrame.set_child(limitsCompatGrid)
        limitsCompatGrid.attach(limitsCompatCombo,0,0,1,1)
        LimitsCompat_Store = Gtk.TreeStore(str,str,str)
        TreeCompatLimits = Gtk.TreeView.new_with_model(LimitsCompat_Store)
        TreeCompatLimits.set_property("enable-grid-lines",1)

        limitsCompatCombo.connect("changed",showLimits, LimitsCompat_Store, TreeCompatLimits,Filenames.opengl_compat_limits_file)
        limitsCompatCombo.set_active(0)


     #   showLimits(LimitRHSValue2, LimitsRHS2, LimitsCompat_Store, TreeCompatLimits,"/tmp/gpu-viewer/OpenGLLimitsLHS.txt")

        setColumns(TreeCompatLimits, LimitsTitle, const.MWIDTH,0.0)
        LimitsCompatScrollbar = create_scrollbar(TreeCompatLimits)
        limitsCompatGrid.attach_next_to(LimitsCompatScrollbar,limitsCompatCombo,Gtk.PositionType.BOTTOM,1,1)

        def button_enable(win):
            button.set_sensitive(True)
        LimitsWin.connect("close-request",button_enable)
        screen_width,screen_height = getScreenSize()
        LimitsWin.set_size_request(int(screen_width) * const.WIDTH_RATIO2,640)

        LimitsWin.present()

    def showLimits(Combo, Limits_Store, TreeLimits,openGLLimits):
        k = 0
        count = 0
        limitValue = Combo.get_active_text()
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

        Limits_Store.clear()
        TreeLimits.set_model(Limits_Store)

        with open(select_opengl_limits_file,"r") as file:
            for i, line in enumerate(file):
                background_color = setBackgroundColor(k)
                k += 1
                TreeLimits.expand_all()
                text = opengl_limits_lhs[i].strip(' ')
                if ("TEXTURE_FORMATS" in line or "SHADING_LANGUAGE" in line) and LimitRHSValue[i] == True:
                    try:
                        iter3 = Limits_Store.append(iter2, [text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                    except Exception:
                        iter3 = Limits_Store.append(None, [text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                    finally:
                        pass
                elif "      " in line and LimitRHSValue[i] == False and ":" not in line:
                    Limits_Store.append(iter3, [text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                else:
                    if ":" in line:
                        k = 0
                        text = opengl_limits_lhs[i]
                        count += 1
                        iter2 = Limits_Store.append(None,
                                                    [text.strip('\n'), LimitsRHS[i].strip('\n'), const.BGCOLOR3])
                        continue
                    if count > 0 and "    " in line:
                        Limits_Store.append(iter2, [text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                    else:
                        Limits_Store.append(None, [text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])


    def radcall2(button,List,filename,Store,tree,filter):
        value = button.get_active()

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

        Store.clear()
        tree.set_model(filter)

    #    for i in range(len(List)):
    #        if int(value) == i:
    #            frame4.set_label(List[i])

        count = len(GL_All)
        for i in range(count):
            background_color = setBackgroundColor(i)
            text = GL_All[i].strip(' ')
            Store.append([text.strip('\n'), background_color])

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

    def searchTreeExtGL(model,iter,data=None):
        search_query = entry_gl.get_text().lower()
        for i in range(tree_opengl_extension.get_n_columns()):
            value = model.get_value(iter,i).lower()
            if search_query in value:
                return True

    def searchTreeExtES(model,iter,data=None):
        search_query = entry_es.get_text().lower()
        for i in range(tree_opengl_es_extension.get_n_columns()):
            value = model.get_value(iter,i).lower()
            if search_query in value:
                return True

    def searchTreeExtEGL(model,iter,data=None):
        search_query = entry_egl.get_text().lower()
        for i in range(tree_egl_extension.get_n_columns()):
            value = model.get_value(iter,i).lower()
            if search_query in value:
                return True
# ------------------------------ Check es2_info Supported ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def es2_infoSupported():
        es2_info_check_process = subprocess.Popen("es2_info",shell=True,stdout=subprocess.PIPE)
        es2_info_check_process.communicate()
        return es2_info_check_process.returncode == 0

#--------------------------------- Creating the OpenGL Information Tab ----------------------------------------------------------------------------------------------------------------------------------------------------------------

    frame_opengl_info = Gtk.Frame()
    opengl_box = Gtk.Box(orientation=1,spacing=10)
    setMargin(opengl_box,0,5,10)
    tab.append(opengl_box)
    opengl_box.append(frame_opengl_info)
    opengl_info_list = Gtk.ListStore(str,str,str)
    Tree_opengl_info = Gtk.TreeView.new_with_model(opengl_info_list)
    Tree_opengl_info.set_property("enable-grid-lines", 1)

    setColumns(Tree_opengl_info,Title2,const.MWIDTH,0.0)

    opengl_info_scrollbar = create_scrollbar(Tree_opengl_info)
    frame_opengl_info.set_child(opengl_info_scrollbar)
    opengl_info()

#-------------------------------- Creating the show OpenGL Limits Limits------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    frame_opengl_buttons = Gtk.Frame()
    opengl_box.append(frame_opengl_buttons)
    grid_opengl_buttons = Gtk.Grid()
    frame_opengl_buttons.set_child(grid_opengl_buttons)

    opengl_limits_button = Gtk.Button.new_with_label("Show OpenGL Limits")
    opengl_limits_button.connect("clicked",clickme)
    setMargin(opengl_limits_button,20,10,10)
    grid_opengl_buttons.attach(opengl_limits_button,0,0,1,1)

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

    setMargin(opengl_framebuffer_button,100,10,10)
    grid_opengl_buttons.attach_next_to(opengl_framebuffer_button,vendor_pic_img,Gtk.PositionType.RIGHT,1,1)

# ------------------------------------ creating the OpenGL extension ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    frame_extension = Gtk.Frame()
    opengl_box.append(frame_extension)
    grid_extension = Gtk.Grid()
    frame_extension.set_child(grid_extension)
    extensions_notebook = Gtk.Notebook()
    grid_extension.attach(extensions_notebook,0,0,1,1)

    opengl_extension_logo = fetchImageFromUrl(const.OPEN_GL_PNG,250,50,False)
    opengl_extension_box = Gtk.Box()
    extensions_notebook.append_page(opengl_extension_box,Gtk.Picture.new_for_pixbuf(opengl_extension_logo))
    page1 = extensions_notebook.get_page(opengl_extension_box)
    page1.set_property("tab-expand",True)

    grid_opengl_extension = Gtk.Grid()
    opengl_extension_box.append(grid_opengl_extension)

    opengl_extension_list = Gtk.ListStore(str,str)
    opengl_extension_list_filter = opengl_extension_list.filter_new()
    tree_opengl_extension = Gtk.TreeView.new_with_model(opengl_extension_list_filter)
    tree_opengl_extension.set_property("enable-grid-lines", 1)
    tree_opengl_extension.set_headers_visible(False)
    opengl_extension_list_filter.set_visible_func(searchTreeExtGL)

    setColumns(tree_opengl_extension,Title,const.MWIDTH,0.0)

    frame_search_gl =Gtk.Frame()
    entry_gl = Gtk.SearchEntry()
    entry_gl.set_property("placeholder-text","Type here to filter extensions.....")
    entry_gl.connect("search-changed",refresh_filter,opengl_extension_list_filter)
    entry_gl.grab_focus()
    frame_search_gl.set_child(entry_gl)

#---------------------------- Getting OpenGL Extensions -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    with open(Filenames.opengl_vendor_gl_extension_file,"w") as file:
        fetch_vendor_gl_extension_process = subprocess.Popen(Filenames.fetch_opengl_vendor_extensions_command,shell=True,stdout=file,universal_newlines=True)
        fetch_vendor_gl_extension_process.communicate()
        fetch_vendor_glx_extension_process = subprocess.Popen(Filenames.fetch_openglx_vendor_extensions_command,shell=True,stdout=file,universal_newlines=True)
        fetch_vendor_glx_extension_process.communicate()

    Vendor_GL, vList = getVendorList(Filenames.opengl_vendor_gl_extension_file)

    vendor_gl_store = Gtk.ListStore(str)
    vendor_combo_gl = Gtk.ComboBox.new_with_model(vendor_gl_store)

    for i in range(len(Vendor_GL)):
        vendor_gl_store.append([Vendor_GL[i]])

    vendor_combo_gl.connect("changed", radcall2,vList,Filenames.opengl_vendor_gl_extension_file,opengl_extension_list,tree_opengl_extension,opengl_extension_list_filter)
    Vendor_renderer = Gtk.CellRendererText()
    setMargin(vendor_combo_gl,2,1,2)
    vendor_combo_gl.pack_start(Vendor_renderer, True)
    vendor_combo_gl.add_attribute(Vendor_renderer, "text", 0)
   # vendor_combo_gl.set_entry_text_column(0)
    vendor_combo_gl.set_active(0)
    grid_opengl_extension.attach(vendor_combo_gl,0,0,1,1)
    grid_opengl_extension.attach_next_to(frame_search_gl,vendor_combo_gl,Gtk.PositionType.LEFT,150,1)
    opengl_extension_scrollbar = create_scrollbar(tree_opengl_extension)
    grid_opengl_extension.attach_next_to(opengl_extension_scrollbar,frame_search_gl,Gtk.PositionType.BOTTOM,151,1)


#--------------------------- creating OpenGL ES Extension tab -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    opengl_es_extension_list = Gtk.ListStore(str,str)
    opengl_es_extension_list_filter = opengl_es_extension_list.filter_new()
    tree_opengl_es_extension = Gtk.TreeView.new_with_model(opengl_es_extension_list_filter)
    tree_opengl_es_extension.set_property("enable-grid-lines", 1)
    tree_opengl_es_extension.set_headers_visible(False)
    opengl_es_extension_list_filter.set_visible_func(searchTreeExtES)


    opengl_es_extension_logo = fetchImageFromUrl(const.OPEN_GL_ES_PNG,250,50,False)
    opengl_es_extension_box = Gtk.Box()
    extensions_notebook.append_page(opengl_es_extension_box,Gtk.Picture.new_for_pixbuf(opengl_es_extension_logo))
    extensions_page2 = extensions_notebook.get_page(opengl_es_extension_box)
    extensions_page2.set_property("tab-expand",True)

    grid_opengl_es_extension = Gtk.Grid()
    opengl_es_extension_box.append(grid_opengl_es_extension)

    setColumns(tree_opengl_es_extension,Title,const.MWIDTH,0.0)

    with open(Filenames.opengl_vendor_es_extension_file,"w") as file:
        fetch_vendor_es_extension_process = subprocess.Popen(Filenames.fetch_opengl_es_vendor_extensions_command,shell=True,stdout=file,universal_newlines=True)
        fetch_vendor_es_extension_process.communicate()
    
    Vendor_ES,vesList = getVendorList(Filenames.opengl_vendor_es_extension_file)

    frame_search_es =Gtk.Frame()
    entry_es = Gtk.SearchEntry()
    entry_es.set_property("placeholder-text","Type here to filter extensions.....")
    entry_es.connect("search-changed",refresh_filter,opengl_es_extension_list_filter)
    entry_es.grab_focus()
    frame_search_es.set_child(entry_es)

    vendor_es_store = Gtk.ListStore(str)
    vendor_combo_es = Gtk.ComboBox.new_with_model(vendor_es_store)
    setMargin(vendor_combo_es,2,1,2)
    for i in range(len(Vendor_ES)):
        vendor_es_store.append([Vendor_ES[i]])

    vendor_combo_es.connect("changed", radcall2,vesList,Filenames.opengl_vendor_es_extension_file,opengl_es_extension_list,tree_opengl_es_extension,opengl_es_extension_list_filter)
    Vendor_renderer_es = Gtk.CellRendererText()
    vendor_combo_es.pack_start(Vendor_renderer_es, True)
    vendor_combo_es.add_attribute(Vendor_renderer_es, "text", 0)
   # vendor_combo_gl.set_entry_text_column(0)
    vendor_combo_es.set_active(0)
    grid_opengl_es_extension.attach(vendor_combo_es,0,0,1,1)
    grid_opengl_es_extension.attach_next_to(frame_search_es,vendor_combo_es,Gtk.PositionType.LEFT,150,1)
    opengl_es_extension_scrollbar = create_scrollbar(tree_opengl_es_extension)
    grid_opengl_es_extension.attach_next_to(opengl_es_extension_scrollbar,frame_search_es,Gtk.PositionType.BOTTOM,151,1)
 #   opengl_extension_box.append(opengl_es_extension_scrollbar)


    #------------------------------------- Creating EGL Extension -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    if es2_infoSupported():

        egl_extension_list = Gtk.ListStore(str,str)
        egl_extension_list_filter = egl_extension_list.filter_new()
        tree_egl_extension = Gtk.TreeView.new_with_model(egl_extension_list_filter)
        tree_egl_extension.set_property("enable-grid-lines", 1)
        tree_egl_extension.set_headers_visible(False)
        egl_extension_list_filter.set_visible_func(searchTreeExtEGL)

        egl_extension_logo = fetchImageFromUrl(const.EGL_PNG,200,50,False)
        egl_extension_box = Gtk.Box()
        extensions_notebook.append_page(egl_extension_box,Gtk.Picture.new_for_pixbuf(egl_extension_logo))
        extensions_page3 = extensions_notebook.get_page(egl_extension_box)
        extensions_page3.set_property("tab-expand",True)

        grid_egl_extension = Gtk.Grid()
        egl_extension_box.append(grid_egl_extension)

        setColumns(tree_egl_extension,Title,const.MWIDTH,0.0)

        with open(Filenames.egl_vendor_extension_file,"w") as file:
            fetch_vendor_egl_extension_process = subprocess.Popen(Filenames.fetch_egl_vendor_extension_command,shell=True,stdout=file,universal_newlines=True)
            fetch_vendor_egl_extension_process.communicate()

        Vendor_EGL,veglList = getVendorList(Filenames.egl_vendor_extension_file)

        vendor_egl_store = Gtk.ListStore(str)
        vendor_combo_egl = Gtk.ComboBox.new_with_model(vendor_egl_store)
        setMargin(vendor_combo_egl,2,1,2)
        for i in range(len(Vendor_EGL)):
            vendor_egl_store.append([Vendor_EGL[i]])
        
        frame_search_egl =Gtk.Frame()
        entry_egl = Gtk.SearchEntry()
        entry_egl.set_property("placeholder-text","Type here to filter extensions.....")
        entry_egl.connect("search-changed",refresh_filter,egl_extension_list_filter)
        entry_egl.grab_focus()
        frame_search_egl.set_child(entry_egl)

        vendor_combo_egl.connect("changed", radcall2,veglList,Filenames.egl_vendor_extension_file,egl_extension_list,tree_egl_extension,egl_extension_list_filter)
        Vendor_renderer_egl = Gtk.CellRendererText()
        vendor_combo_egl.pack_start(Vendor_renderer_egl, True)
        vendor_combo_egl.add_attribute(Vendor_renderer_egl, "text", 0)
        vendor_combo_egl.set_active(0)
        grid_egl_extension.attach(vendor_combo_egl,0,0,1,1)
        grid_egl_extension.attach_next_to(frame_search_egl,vendor_combo_egl,Gtk.PositionType.LEFT,150,1)
        egl_extension_scrollbar = create_scrollbar(tree_egl_extension)
        grid_egl_extension.attach_next_to(egl_extension_scrollbar,frame_search_egl,Gtk.PositionType.BOTTOM,151,1)


    # ------------------------------------------- Search Text Box GL ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------