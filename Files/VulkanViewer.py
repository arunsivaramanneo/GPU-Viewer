import sys
import gi
gi.require_version('Gtk','4.0')
gi.require_version(namespace='Adw', version='1')

from gi.repository import Gtk,GdkPixbuf,GObject,Gio,Adw

Adw.init()

import const
import Filenames
import subprocess
from Common import copyContentsFromFile, getGpuImage,setColumns,create_scrollbar,setBackgroundColor, getRamInGb,createSubTab,getDriverVersion,getDeviceSize, setMargin,fetchContentsFromCommand,getVulkanVersion,createMainFile,createSearchEntry,getLogo

DeviceTitle = ["Device Information","", "Details"]
SparseTitle = ["Device Properties", "Value"]
LimitsTitle = ["Device Limits", "Value"]
FeaturesTitle = ["Device Features", "Value"]
ExtensionsTitle = ["Device Extensions", "Extension Revision"]
FormatsTitle = ["Device Formats","linearTiling","optimalTiling","bufferFeatures"]
HeapTitle = ["Memory Heaps", "Value"]
MemoryTitle = ["Memory Types", "Value"]
QueuesLHS = ["VkQueueFamilyProperties", "QueueCount", "timestampValidBits", "queueFlags","GRAPHICS BIT", "COMPUTE BIT", "TRANSFER BIT",
              "SPARSE BINDING BIT", "minImageTransferGranularity.width", "minImageTransferGranularity.height",
              "minImageTransferGranularity.depth"]
QueueTitle = ["Queue Family","Value"]
InstanceTitle = ["Extensions", "Extension Revision"]
LayerTitle = ["Layers", "Vulkan Version", "Layer Version", "Extension Count", "Description"]
SurfaceTitle = ["Surface Capabilities", "Value"]
GroupsTitle = ["Device Groups","Value"]

class DataObject(GObject.GObject):
    def __init__(self, column1: str,column2: str):
        super(DataObject, self).__init__()
        self.column1 = column1
        self.column2 = column2

class ExpandDataObject2(GObject.GObject):
    def __init__(self, txt: str, txt2: str,txt3: str,txt4: str,txt5: str):
        super(ExpandDataObject2, self).__init__()
        self.data = txt
        self.data2 = txt2
        self.data3= txt3
        self.data4= txt4
        self.data5= txt5
        self.children = []

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


def add_tree_node2(item):
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
        store = Gio.ListStore.new(ExpandDataObject2)
        for child in item.children:
            store.append(child)
        return store
    
def setup_expander(widget, item):
    """Setup the widget to show in the Gtk.Listview"""
    label = Gtk.Label()
    expander = Gtk.TreeExpander.new()
 #   expander.props.indent_for_icon = True
 #   expander.props.indent_for_depth = True
    expander.set_child(label)
    item.set_child(expander)

def bind_expander(widget, item):
    """bind data from the store object to the widget"""
    expander = item.get_child()
    label = expander.get_child()
    row = item.get_item()
    expander.set_list_row(row)
    obj = row.get_item()
 #   print(obj.data)
    label.set_label(obj.data)

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

def bind2(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    row = item.get_item()
    obj = row.get_item()
    if "true" in obj.data3: 
        label.add_css_class(css_class='true')
    elif "false" in obj.data3:
        label.add_css_class(css_class='false')
    else:
        label.add_css_class(css_class='nothing')
    label.set_label(obj.data3)


def bind3(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    row = item.get_item()
    obj = row.get_item()
    if "true" in obj.data4: 
        label.add_css_class(css_class='true')
    elif "false" in obj.data4:
        label.add_css_class(css_class='false')
    else:
        label.add_css_class(css_class='nothing')
    label.set_label(obj.data4)


def bind4(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    row = item.get_item()
    obj = row.get_item()
    if "true" in obj.data5: 
        label.add_css_class(css_class='true')
    elif "false" in obj.data5:
        label.add_css_class(css_class='false')
    else:
        label.add_css_class(css_class='nothing')
    label.set_label(obj.data5)

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

def bind_column2(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    if "true" in obj.column2:
        label.add_css_class(css_class='true')
        label.set_label(obj.column2)
    elif "false" in obj.column2:
        label.add_css_class(css_class='false')
        label.set_label(obj.column2)
    else:
        label.set_label(obj.column2)


def Vulkan(tab2):
    # Creating Tabs for different Features

    # Creating Feature TabFalseFalse
    def Devices(GPUname):
        # noinspection PyPep8

        # --------------------------------- commands for fetching the Device Tab info --- Modify/Add Commands here -------------------------------------------------------------

        fetch_vulkan_gpu_info_command = "vulkaninfo --summary | awk '/GPU%d/{flag=1;next}/^GPU.*/{flag=0}flag' | awk '{gsub(/\([0-9].*/,'True');}1' | sort " %(GPUname)
        fetch_vulkan_gpu_pipeline_command = "cat %s | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceLimits:/{flag=0}flag' | grep pipeline" %(Filenames.vulkaninfo_output_file,GPUname)
        fetch_cpu_info_command = "LC_ALL=C lscpu | awk '/name|^CPU|^L/' | sort -r"
        fetch_cpu_core_info_command = "LC_ALL=C lscpu | awk '/ per /' |  sort"
        fetch_mem_info_command = "cat /proc/meminfo | awk '/Mem/'"
        fetch_lsb_release_info_command = "lsb_release -d -r -c"
        fetch_device_tab_rhs_command = "cat %s | grep -oE '[=,:].*'" %(Filenames.vulkan_device_info_file)
        fetch_XDG_CURRENT_DESKTOP_command = "echo $XDG_CURRENT_DESKTOP"
        fetch_kernal_version_command = "uname -r"
        fetch_windowing_system_command = "echo $XDG_SESSION_TYPE"
        fetch_vulkan_instance_version_command = "cat %s | grep Version | grep Instance" %(Filenames.vulkaninfo_output_file)

        # ------------------------------------ Writing the Output of all the Commands to a File -----------------------------------------------------------------------------------------------------
        with open(Filenames.vulkan_device_info_file,"w" ) as file:
            fetch_vulkan_gpu_info_process = subprocess.Popen(fetch_vulkan_gpu_info_command,stdout=file,universal_newlines=True,shell=True)
            fetch_vulkan_gpu_info_process.communicate()
            fetch_vulkan_gpu_pipeline_process = subprocess.Popen(fetch_vulkan_gpu_pipeline_command,stdout=file,universal_newlines=True,shell=True)
            fetch_vulkan_gpu_pipeline_process.communicate()
            fetch_vulkan_instance_version_process = subprocess.Popen(fetch_vulkan_instance_version_command,stdout=file,universal_newlines=True,shell=True)
            fetch_vulkan_instance_version_process.communicate()
            fetch_cpu_info_process = subprocess.Popen(fetch_cpu_info_command,stdout=file,universal_newlines=True,shell=True)
            fetch_cpu_info_process.communicate()
            fetch_cpu_core_info_process = subprocess.Popen(fetch_cpu_core_info_command,stdout=file,universal_newlines=True,shell=True)
            fetch_cpu_core_info_process.communicate()
            fetch_mem_info_process = subprocess.Popen(fetch_mem_info_command,stdout=file,universal_newlines=True,shell=True)
            fetch_mem_info_process.communicate()
            fetch_lsb_release_process = subprocess.Popen(fetch_lsb_release_info_command,stdout=file,universal_newlines=True,shell=True)
            fetch_lsb_release_process.communicate()


        fetch_device_tab_lhs_command = "cat %s |  %s " %(Filenames.vulkan_device_info_file,Filenames.remove_rhs_Command)


        # -------------------------------------- Seperating the LHS side of the Device Tab ----------------------------------------------------------------------------------------------
        with open(Filenames.vulkan_device_info_lhs_file,"w") as file:
            fetch_device_tab_lhs_process = subprocess.Popen(fetch_device_tab_lhs_command,stdout=file,universal_newlines=True,shell=True)
            fetch_device_tab_lhs_process.communicate()
        

        #------------------------------------- Seperating the RHS Side of the Device Tab -------------------------------------------------------------------------------------------------------------------       
        with open(Filenames.vulkan_device_info_rhs_file,"w") as file:
            fetch_device_tab_rhs_process = subprocess.Popen(fetch_device_tab_rhs_command,stdout=file,universal_newlines=True,shell=True)
            fetch_device_tab_rhs_process.communicate()
            fetch_XDG_CURRENT_DESKTOP_process = subprocess.Popen(fetch_XDG_CURRENT_DESKTOP_command,stdout=file,universal_newlines=True,shell=True)
            fetch_XDG_CURRENT_DESKTOP_process.communicate()
            fetch_kernal_version_process = subprocess.Popen(fetch_kernal_version_command,stdout=file,universal_newlines=True,shell=True)
            fetch_kernal_version_process.communicate()
            fetch_windowing_system_process = subprocess.Popen(fetch_windowing_system_command,stdout=file,universal_newlines=True,shell=True)
            fetch_windowing_system_process.communicate()

        valueLHS = copyContentsFromFile(Filenames.vulkan_device_info_lhs_file)
        valueLHS.append("Desktop")
        valueLHS.append("Kernel")
        valueLHS.append("Windowing System")
        valueRHS = copyContentsFromFile(Filenames.vulkan_device_info_rhs_file)

        valueRHS = [i.strip('=') for i in valueRHS]
        valueRHS = [i.strip(':') for i in valueRHS]
        
        for i in range(len(valueRHS)):
            if "0x" in valueRHS[i]:
                valueRHS[i] = int(valueRHS[i], 16)
                valueRHS[i] = str("%d" % valueRHS[i])


        valueLHS = [i.strip('\t') for i in valueLHS]
        valueRHS = [i.strip('\t') for i in valueRHS]
        valueRHS = [i.strip(' ') for i in valueRHS]

        DeviceTab_Store.clear()
        TreeDevice.set_model(DeviceTab_Store)


        dummy_transparent = GdkPixbuf.Pixbuf.new_from_file_at_size(const.TRANSPARENT_PIXBUF, 24, 20)
        for i in range(len(valueRHS)):
            background_color = setBackgroundColor(i)
            if "apiVersion" in valueLHS[i]:
                if '.' not in valueRHS[i]:
                    valueRHS[i] = getVulkanVersion(valueRHS[i])
                iter1 = DeviceTab_Store.append(None,["Vulkan Details...",dummy_transparent," ",const.BGCOLOR3])
            if "driverVersion" in valueLHS[i]:
                if '.' not in valueRHS[i]:
                    valueRHS[i] = getDriverVersion(valueRHS,i)
            if "deviceName" in valueLHS[i]:
                gpu_logo = getLogo(valueRHS[i])
                DeviceTab_Store.append(iter1,[valueLHS[i].strip('\n'),gpu_logo, valueRHS[i].strip('\n'),background_color])
                continue
            if "driverName" in valueLHS[i]:
                driver_logo = getLogo(valueRHS[i])
                DeviceTab_Store.append(iter1,[valueLHS[i].strip('\n'),driver_logo, valueRHS[i].strip('\n'),background_color])
                continue
            if "Model" in valueLHS[i]:
                cpu_logo = getLogo(valueRHS[i])
                iter1 = DeviceTab_Store.append(None,["Processor Details...",dummy_transparent,"",const.BGCOLOR3])
                DeviceTab_Store.append(iter1,[valueLHS[i].strip('\n'),cpu_logo, valueRHS[i].strip('\n'),background_color])
                continue
            if "Description" in valueLHS[i]:
                distro_logo = getLogo(valueRHS[i])
                iter1 = DeviceTab_Store.append(None,["Operating System Details...",dummy_transparent,"",const.BGCOLOR3])
                DeviceTab_Store.append(iter1,["Distribution",distro_logo,valueRHS[i].strip('\n'),background_color])
                continue
            if "Desktop" in valueLHS[i]:
                desktop_logo = getLogo(valueRHS[i])
                DeviceTab_Store.append(iter1,[valueLHS[i].strip('\n'),desktop_logo, valueRHS[i].strip('\n'),background_color])
                continue
            if "Windowing" in valueLHS[i]:
                windowing_system_logo = getLogo(valueRHS[i])
                DeviceTab_Store.append(iter1,[valueLHS[i].strip('\n'),windowing_system_logo, valueRHS[i].strip('\n'),background_color])
                continue
            if "MemTotal" in valueLHS[i]:
                iter1 = DeviceTab_Store.append(None,["Memory Details...",dummy_transparent," ",const.BGCOLOR3])
                DeviceTab_Store.append(iter1,[valueLHS[i].strip('\n'),dummy_transparent, getRamInGb(valueRHS[i]),background_color])
            elif "Mem" in valueLHS[i] or "Swap" in valueLHS[i] :
                DeviceTab_Store.append(iter1,[valueLHS[i].strip('\n'),dummy_transparent, getRamInGb(valueRHS[i]),background_color])
            else:
                DeviceTab_Store.append(iter1,[valueLHS[i].strip('\n'),dummy_transparent, valueRHS[i].strip('\n'),background_color])

        TreeDevice.expand_all()

        fetch_device_properties_command = "cat %s | awk '/GPU%d/{flag=1;next}/Device Extensions.*/{flag=0}flag' | awk '/VkPhysicalDeviceSparseProperties:/{flag=1}/Device Extensions.*/{flag=0}flag' | awk '/./' " %(Filenames.vulkaninfo_output_file,GPUname)
    #    os.system("cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Extensions.*/{flag=0}flag' | awk '/VkPhysicalDeviceSparseProperties:/{flag=1}/Device Extensions.*/{flag=0}flag' | awk '/./' > /tmp/gpu-viewer/VKDDevicesparseinfo1.txt" % GPUname)
        createMainFile(Filenames.vulkan_device_properties_file,fetch_device_properties_command)
        
        propertiesList = Gtk.StringList()
        propertiesDropdown.set_model(propertiesList)
        propertiesList.append("Show All Device Properties")
        with open(Filenames.vulkan_device_properties_file, "r") as file1:
            for i, line in enumerate(file1):
                if "Vk" in line:
                    text1 = ((line.strip("\t")).replace("VkPhysicalDevice",'')).replace(":","")
                    text = text1[:-1]
                    propertiesList.append(text.strip("\n"))


    def Limits(GPUname):

        fetch_vulkan_Limits_ouput_command = "awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceSparseProperties:/{flag=0}flag' | awk '/VkPhysicalDeviceLimits:/{flag=1;next}/VkPhysicalDeviceSparseProperties:/{flag=0}flag' | awk '/--/{flag=1;next}flag' | awk '/./'" %(GPUname)
        fetch_vulkan_Limits_ouput_lhs_command = "cat %s | %s " %(Filenames.vulkan_device_limits_file,Filenames.remove_rhs_Command)
        fetch_vulkan_Limits_ouput_rhs_command = "cat %s | grep -o '=.*' | grep -o '[ -].*'" %(Filenames.vulkan_device_limits_file)

        createMainFile(Filenames.vulkan_device_limits_file,Filenames.fetch_vulkaninfo_ouput_command+fetch_vulkan_Limits_ouput_command)

        vulkan_device_limits_lhs = fetchContentsFromCommand(fetch_vulkan_Limits_ouput_lhs_command)

        vulkan_device_limits_rhs = fetchContentsFromCommand(fetch_vulkan_Limits_ouput_rhs_command)

        LimitsTab_Store.remove_all()
    #    TreeLimits.set_model(LimitsTab_Store_filter)
   
    #    v1 = [ExpandDataObject("entrada 01", "other")]
    #    v2 = [ExpandDataObject("entrada 02","", v1)]
    #    LimitsTab_Store.append(ExpandDataObject("entrada 03", "else", v2)) 
        with open(Filenames.vulkan_device_limits_file, "r") as file1:
            j = 0; iter = None
            for i,line in enumerate(file1):
                background_color = setBackgroundColor(i)
                text = vulkan_device_limits_lhs[i].strip('\t')
                if not (iter == text):
                    if '=' in line and "\t\t" not in line:
                        text = vulkan_device_limits_lhs[i].strip('\t')
                        if iter == None:
                            toprow = ExpandDataObject((text.strip('\n')).replace(' count',''), vulkan_device_limits_rhs[j].strip('\n'))
                            j = j + 1
                        else:
                            LimitsTab_Store.append(toprow)
                            toprow = ExpandDataObject((text.strip('\n')).replace(' count',''), vulkan_device_limits_rhs[j].strip('\n'))
                            j = j + 1
                        iter = text
                        continue
                #    iter = [ExpandDataObject((text.strip('\n')).replace(' count',''), vulkan_device_limits_rhs[j].strip('\n'),iter2)]
                #    toprow = ExpandDataObject((text.strip('\n')).replace(' count',''), vulkan_device_limits_rhs[j].strip('\n'))
                #    j = j + 1
                if "\t\t" in line and "=" not in line:
                 #   iter2 = [ExpandDataObject(text.strip('\n')," ",iter)]
                    childrow = ExpandDataObject((text.strip('\n')).replace(' count',''), " ")
                    toprow.children.append(childrow)
                    continue
            LimitsTab_Store.append(toprow)
             #   LimitsTab_Store.append(ExpandDataObject((text.strip('\n')).replace(' count',''), " "))
                
     #       TreeLimits.expand_all()

    def Features(GPUname):
        fetch_device_features_command = "cat %s | awk '/GPU%d/{flag=1;next}/Format Properties.*/{flag=0}flag' | awk '/VkPhysicalDeviceFeatures:/{flag=1;next}/Format Properties.*/{flag=0}flag' " %(Filenames.vulkaninfo_output_file,GPUname)

        createMainFile(Filenames.vulkan_device_features_file,fetch_device_features_command)
        featureList = Gtk.StringList()
        featureDropdown.set_model(featureList)
        featureList.append("Show All Device Features")
        with open(Filenames.vulkan_device_features_file, "r") as file:
            for line in file:
                if "Vk" in line:
                    text = line[:-2]
                    featureList.append(((text.strip("\n")).replace("VkPhysicalDevice","").replace(":","")))

    def selectFeature(dropdown, _pspec):
        selected =dropdown.props.selected_item
        feature = ""
        if selected is not None:
            feature = selected.props.string

        fetch_device_features_all_command = "cat %s | awk '/==/{flag=1;next} flag' | awk '{sub(/^[ \t]+/, 'True'); print }' | grep =" %(Filenames.vulkan_device_features_file)
        fetch_device_features_selected_command = "cat %s | awk '/%s/{flag=1;next}/^Vk*/{flag=0}flag' | awk '/--/{flag=1 ; next} flag' | grep = | sort " %(Filenames.vulkan_device_features_file,feature)
        fetch_device_features_selected_lhs_command = "cat %s | awk '{sub(/^[ \t]+/, 'True'); print }' | awk '{gsub(/= true/,'True');print}' | awk '{gsub(/= false/,'False');print}' | awk '{sub(/[ \t]+$/, 'True'); print }' | awk '/./' | sort | uniq" %(Filenames.vulkan_device_features_select_file)

        if feature is None:
            feature =' '
        elif "Show All Device Features" in feature:
            createMainFile(Filenames.vulkan_device_features_select_file,fetch_device_features_all_command)
            featureColumn1.set_title(FeaturesTitle[0])
        else:
            createMainFile(Filenames.vulkan_device_features_select_file,fetch_device_features_selected_command)
            featureColumn1.set_title(feature)
        createMainFile(Filenames.vulkan_device_features_lhs_file,fetch_device_features_selected_lhs_command)

        value = []
        fgColor = []
        FeatureTab_Store.remove_all()
    #    TreeFeatures.set_model(FeaturesTab_Store_filter)
        FeaturesLHS = copyContentsFromFile(Filenames.vulkan_device_features_lhs_file,)
        count = 0
        for i,LHS in enumerate(FeaturesLHS):
            with open(Filenames.vulkan_device_features_select_file, "r") as file1:
                text = LHS.strip('\n')
                for line in file1:
                    if text in line:
                        if "= true" in line:
                            value.append('true')
                            count = count + 1
                            fgColor.append(const.COLOR1)
                            break
                        else :
                            value.append('false')
                            fgColor.append(const.COLOR2)
                            break                        
                background_color = setBackgroundColor(i)
                FeatureTab_Store.append(DataObject("  " +text.strip('\n'), value[i].strip('\n'), ))

    def Extensions(GPUname):

        fetch_device_extensions_command = "cat %s | awk '/GPU%d/{flag=1;next}/VkQueueFamilyProperties/{flag=0}flag'|awk '/Device Extensions/{flag=1; next}/VkQueueFamilyProperties/{flag=0} flag' | grep VK_ | sort" %(Filenames.vulkaninfo_output_file,GPUname)
        fetch_device_extensions_rhs_command = "cat %s | grep -o 'revision.*' | grep -o ' .*' "%Filenames.vulkan_device_extensions_file
        fetch_device_extensions_lhs_command = "cat %s | %s " %(Filenames.vulkan_device_extensions_file,Filenames.remove_rhs_Command)

        createMainFile(Filenames.vulkan_device_extensions_file,fetch_device_extensions_command)

        vulkan_device_extension_lhs = fetchContentsFromCommand(fetch_device_extensions_lhs_command)

        vulkan_device_extensions_rhs = fetchContentsFromCommand(fetch_device_extensions_rhs_command)

        ExtensionTab_Store.remove_all()
        extensionColumnView.set_model(extensionSelection)

        for i in range(len(vulkan_device_extension_lhs)):
            background_color = setBackgroundColor(i)
            ExtensionTab_Store.append(DataObject(vulkan_device_extension_lhs[i].strip('\t'),vulkan_device_extensions_rhs[i]))

        label = "Extensions (%d)" %len(vulkan_device_extensions_rhs)
        notebook.set_tab_label(ExtensionTab, Gtk.Label(label=label))

    def Formats(GPUname):
                # noinspection PyPep8
        fetch_vulkan_device_formats_command = "cat %s |  awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/Format Properties/{flag=1; next}/Unsupported Formats:*/{flag=0} flag' | awk '/./'" %(Filenames.vulkaninfo_output_file,GPUname,GPUname+1)
        fetch_vulkan_device_formats_types_command = "cat %s | grep FORMAT_  | grep -v FORMAT_FEATURE  | awk '/./'" %(Filenames.vulkan_device_formats_file)
        fetch_vulkan_device_format_types_count_command = "cat %s | grep Formats | grep -o '=.*' | grep -o ' .*' | awk '/./' " %(Filenames.vulkan_device_formats_file)
        fetch_vulkan_device_format_type_linear_count_command = "cat %s | awk '/linear*/{getline;print}' | grep -o '[N,F].*' " %(Filenames.vulkan_device_formats_file)
        fetch_vulkan_device_format_type_optimal_count_command = "cat %s | awk '/optimal*/{getline;print}' | grep -o '[N,F].*' " %(Filenames.vulkan_device_formats_file)
        fetch_vulkan_device_format_type_buffer_count_command = "cat %s | awk '/buffer*/{getline;print}' | grep -o '[N,F].*' " %(Filenames.vulkan_device_formats_file)
        
        createMainFile(Filenames.vulkan_device_formats_file,fetch_vulkan_device_formats_command)
        
        createMainFile(Filenames.vulkan_device_formats_types_file,fetch_vulkan_device_formats_types_command,)

        createMainFile(Filenames.vulkan_device_format_types_count_file,fetch_vulkan_device_format_types_count_command)

        createMainFile(Filenames.vulkan_device_format_types_linear_count_file,fetch_vulkan_device_format_type_linear_count_command)
        
        createMainFile(Filenames.vulkan_device_format_types_optimal_count_file,fetch_vulkan_device_format_type_optimal_count_command)

        createMainFile(Filenames.vulkan_device_format_types_buffer_count_file,fetch_vulkan_device_format_type_buffer_count_command)  

        FormatsList = Gtk.StringList()
        FormatsDropDown.set_model(FormatsList)
        FormatsList.append("Show All Device Formats")
        with open(Filenames.vulkan_device_formats_types_file,"r") as file:
            for line in file:
                FormatsList.append(((line.replace("FORMAT_","")).strip("\n")).strip("\t"))

    def selectFormats(dropdown,_pspec):
        selected =dropdown.props.selected_item
        selected_Format = ""
        if selected is not None:
            selected_Format = selected.props.string

        valueFormats = copyContentsFromFile(Filenames.vulkan_device_formats_types_file)
        valueFormatsCount = copyContentsFromFile(Filenames.vulkan_device_format_types_count_file)
        valueLinearCount = copyContentsFromFile(Filenames.vulkan_device_format_types_linear_count_file)
        valueOptimalCount = copyContentsFromFile(Filenames.vulkan_device_format_types_optimal_count_file)
        valueBufferCount = copyContentsFromFile(Filenames.vulkan_device_format_types_buffer_count_file)
            
        FormatsTab_Store.remove_all()
    #    TreeFormats.set_model(FormatsTab_Store_filter)
        groupName = None
        if selected_Format is None:
            pass
        elif "Show All Device Formats" in selected_Format:
            n = 0
            formatsModel.set_autoexpand(False)
            for i in range(len(valueFormatsCount)):
                for j in range(int(valueFormatsCount[i])):
                    if not (groupName == valueFormats[n]):
                        if 'None' not in valueLinearCount[i]:
                            linearStatus = "true"
                            linearColor = const.COLOR1
                        else:
                            linearStatus = "false"
                            linearColor = const.COLOR2
                        if 'None' not in valueOptimalCount[i]:
                            optimalStatus = "true"
                            optimalColor = const.COLOR1
                        else:
                            optimalStatus = "false"
                            optimalColor = const.COLOR2
                        if 'None' not in valueBufferCount[i]:
                            bufferStatus = "true"
                            bufferColor = const.COLOR1
                        else:
                            bufferStatus = "false"
                            bufferColor = const.COLOR2
                        if groupName == None:
                            toprow = ExpandDataObject2(((valueFormats[n].strip('\n')).strip('\t')).replace('FORMAT_',""),linearStatus,optimalStatus,bufferStatus,"")
                        else:
                            FormatsTab_Store.append(toprow)
                            toprow = ExpandDataObject2(((valueFormats[n].strip('\n')).strip('\t')).replace('FORMAT_',""),linearStatus,optimalStatus,bufferStatus,"")
                        groupName = valueFormats[n]

                        fetch_vulkan_device_format_linear_types_command = "cat %s | awk '/^%s$/{flag=1};flag;/Common.*/{flag=0}' | awk '/linear*/{flag=1;next}/optimal*/{flag=0}flag'" %(Filenames.vulkan_device_formats_file,valueFormats[n].strip("\n"))
                        fetch_vulkan_device_format_optimal_types_command = "cat %s | awk '/^%s$/{flag=1};flag;/Common.*/{flag=0}' | awk '/optimal*/{flag=1;next}/buffer*/{flag=0}flag'" %(Filenames.vulkan_device_formats_file,valueFormats[n].strip("\n"))
                        fetch_vulkan_device_format_buffer_types_command = "cat %s | awk '/^%s$/{flag=1};flag;/Common.*/{flag=0}' | awk '/buffer*/{flag=1;next}/Common*/{flag=0}flag'" %(Filenames.vulkan_device_formats_file,valueFormats[n].strip("\n"))

                    #    iter1 = FormatsTab_Store.append(None,[((valueFormats[n].strip('\n')).strip('\t')).replace('FORMAT_',""),linearStatus,optimalStatus,bufferStatus,setBackgroundColor(n),linearColor,optimalColor,bufferColor]) 
                    #    toprow = ExpandDataObject2(((valueFormats[n].strip('\n')).strip('\t')).replace('FORMAT_',""),linearStatus,optimalStatus,bufferStatus,"")
                        if 'None' not in valueLinearCount[i] or 'None' not in valueOptimalCount[i] or 'None' not in valueBufferCount[i]:
                        #    iter2 = FormatsTab_Store.append(iter1,["linearTiling"," "," "," ",setBackgroundColor(n+1),setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j)])
                            iter2 = ExpandDataObject2("linearTiling"," "," "," ","")
                            toprow.children.append(iter2)
                            
                            with open(Filenames.vulkan_device_format_types_linear_file,"w") as file:
                                fetch_vulkan_device_format_linear_types_process = subprocess.Popen(fetch_vulkan_device_format_linear_types_command,stdout=file,universal_newlines=True,shell=True)
                                fetch_vulkan_device_format_linear_types_process.communicate()
                                
                            with open(Filenames.vulkan_device_format_types_linear_file) as file1:
                                for k,line in enumerate(file1):
                                    iter3 = ExpandDataObject2((((line.strip('\n')).strip('\t'))).replace("FORMAT_FEATURE_2_","")," "," "," ","")
                                    iter2.children.append(iter3)
                                #    FormatsTab_Store.append(iter2,[(((line.strip('\n')).strip('\t'))).replace("FORMAT_FEATURE_2_","")," "," "," ",setBackgroundColor(k),setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j)])
                        #    iter2 = FormatsTab_Store.append(iter1,["optimalTiling"," "," "," ",setBackgroundColor(n+2),setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j)])
                            iter2 = ExpandDataObject2("optimalTiling"," "," "," ","")
                            toprow.children.append(iter2)

                            with open(Filenames.vulkan_device_format_types_optimal_file,"w") as file:
                                fetch_vulkan_device_format_optimal_types_process = subprocess.Popen(fetch_vulkan_device_format_optimal_types_command,stdout=file,universal_newlines=True,shell=True)
                                fetch_vulkan_device_format_optimal_types_process.communicate()
                        #       os.system("cat /tmp/gpu-viewer/VKDFORMATS.txt | awk '/^%s$/{flag=1};flag;/Common.*/{flag=0}' | awk '/optimal*/{flag=1;next}/buffer*/{flag=0}flag' > /tmp/gpu-viewer/VKOptimal.txt " %(valueFormats[n].strip('\n')))
                            with open(Filenames.vulkan_device_format_types_optimal_file) as file1:
                                for k,line in enumerate(file1):
                                    iter3 = ExpandDataObject2((((line.strip('\n')).strip('\t'))).replace("FORMAT_FEATURE_2_","")," "," "," ","")
                                    iter2.children.append(iter3)
                                #    FormatsTab_Store.append(iter2,[(((line.strip('\n')).strip('\t'))).replace("FORMAT_FEATURE_2_","")," "," "," ",setBackgroundColor(k),setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j)])
                        #    iter2 = FormatsTab_Store.append(iter1,["bufferFeatures"," "," "," ",setBackgroundColor(n+3),setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j)])
                            iter2 = ExpandDataObject2("bufferFeatures"," "," "," ","")
                            toprow.children.append(iter2)

                            with open(Filenames.vulkan_device_format_types_buffer_file,"w") as file:
                                fetch_vulkan_device_format_buffer_types_process = subprocess.Popen(fetch_vulkan_device_format_buffer_types_command,stdout=file,universal_newlines=True,shell=True)
                                fetch_vulkan_device_format_buffer_types_process.communicate()
                        #      os.system("cat /tmp/gpu-viewer/VKDFORMATS.txt | awk '/^%s$/{flag=1};flag;/Common.*/{flag=0}' | awk '/buffer*/{flag=1;next}/Common*/{flag=0}flag' > /tmp/gpu-viewer/VKBuffer.txt " %(valueFormats[n].strip('\n')))
                            with open(Filenames.vulkan_device_format_types_buffer_file) as file1:
                                for k,line in enumerate(file1):
                                    iter3 = ExpandDataObject2((((line.strip('\n')).strip('\t'))).replace("FORMAT_FEATURE_2_","")," "," "," ","")
                                    iter2.children.append(iter3)
                                #    FormatsTab_Store.append(iter2,[(((line.strip('\n')).strip('\t'))).replace("FORMAT_FEATURE_2_","")," "," "," ",setBackgroundColor(k),setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j)])

                        n +=1
                FormatsTab_Store.append(toprow)
        else:
                selected_value = 0
                if selected is not None:
                    selected_value = dropdown.props.selected - 1
                sum = 0
                for i in range(len(valueFormatsCount)):
                    sum = sum + int(valueFormatsCount[i])
                    if selected_value < sum:
                        value = i
                        break
                if 'None' not in valueLinearCount[value]:
                    linearStatus = "true"
                    linearColor = const.COLOR1
                else:
                    linearStatus = "false"
                    linearColor = const.COLOR2
                if 'None' not in valueOptimalCount[value]:
                    optimalStatus = "true"
                    optimalColor = const.COLOR1
                else:
                    optimalStatus = "false"
                    optimalColor = const.COLOR2
                if 'None' not in valueBufferCount[value]:
                    bufferStatus = "true"
                    bufferColor = const.COLOR1
                else:
                    bufferStatus = "false"
                    bufferColor = const.COLOR2

                fetch_vulkan_device_format_linear_types_command = "cat %s | awk '/FORMAT_%s$/{flag=1};flag;/Common.*/{flag=0}' | awk '/linear*/{flag=1;next}/optimal*/{flag=0}flag'" %(Filenames.vulkan_device_formats_file,selected_Format)
                fetch_vulkan_device_format_optimal_types_command = "cat %s | awk '/FORMAT_%s$/{flag=1};flag;/Common.*/{flag=0}' | awk '/optimal*/{flag=1;next}/buffer*/{flag=0}flag'" %(Filenames.vulkan_device_formats_file,selected_Format)
                fetch_vulkan_device_format_buffer_types_command = "cat %s | awk '/FORMAT_%s$/{flag=1};flag;/Common.*/{flag=0}' | awk '/buffer*/{flag=1;next}/Common*/{flag=0}flag'" %(Filenames.vulkan_device_formats_file,selected_Format)
            #    iter1 = FormatsTab_Store.append(None,[selected_Format,linearStatus,optimalStatus,bufferStatus,setBackgroundColor(0),linearColor,optimalColor,bufferColor]) 
                toprow = ExpandDataObject2(selected_Format,linearStatus,optimalStatus,bufferStatus,"")
                j = 1
                if 'None' not in valueLinearCount[i] or 'None' not in valueOptimalCount[i] or 'None' not in valueBufferCount[i]:
                #    iter2 = FormatsTab_Store.append(iter1,["linearTiling"," "," "," ",setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j)])
                    iter2 = ExpandDataObject2("linearTiling"," "," "," ","")
                    toprow.children.append(iter2)
                            
                    with open(Filenames.vulkan_device_format_types_linear_file,"w") as file:
                        fetch_vulkan_device_format_linear_types_process = subprocess.Popen(fetch_vulkan_device_format_linear_types_command,stdout=file,universal_newlines=True,shell=True)
                        fetch_vulkan_device_format_linear_types_process.communicate()
                        
                    with open(Filenames.vulkan_device_format_types_linear_file) as file1:
                        for k,line in enumerate(file1):
                            iter3 = ExpandDataObject2((((line.strip('\n')).strip('\t'))).replace("FORMAT_FEATURE_2_","")," "," "," ","")
                            iter2.children.append(iter3)
                        #    FormatsTab_Store.append(iter2,[(((line.strip('\n')).strip('\t'))).replace("FORMAT_FEATURE_2_","")," "," "," ",setBackgroundColor(k),setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j)])
                #    iter2 = FormatsTab_Store.append(iter1,["optimalTiling"," "," "," ",setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j)])
                    iter2 = ExpandDataObject2("optimalTiling"," "," "," ","")
                    toprow.children.append(iter2)
                            
                    with open(Filenames.vulkan_device_format_types_optimal_file,"w") as file:
                        fetch_vulkan_device_format_optimal_types_process = subprocess.Popen(fetch_vulkan_device_format_optimal_types_command,stdout=file,universal_newlines=True,shell=True)
                        fetch_vulkan_device_format_optimal_types_process.communicate()
                #       os.system("cat /tmp/gpu-viewer/VKDFORMATS.txt | awk '/^%s$/{flag=1};flag;/Common.*/{flag=0}' | awk '/optimal*/{flag=1;next}/buffer*/{flag=0}flag' > /tmp/gpu-viewer/VKOptimal.txt " %(valueFormats[n].strip('\n')))
                    with open(Filenames.vulkan_device_format_types_optimal_file) as file1:
                        for k,line in enumerate(file1):
                            iter3 = ExpandDataObject2((((line.strip('\n')).strip('\t'))).replace("FORMAT_FEATURE_2_","")," "," "," ","")
                            iter2.children.append(iter3)
                        #    FormatsTab_Store.append(iter2,[(((line.strip('\n')).strip('\t'))).replace("FORMAT_FEATURE_2_","")," "," "," ",setBackgroundColor(k),setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j)])
                #    iter2 = FormatsTab_Store.append(iter1,["bufferFeatures"," "," "," ",setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j)])
                    iter2 = ExpandDataObject2("bufferFeatures"," "," "," ","")
                    toprow.children.append(iter2)
                    
                    with open(Filenames.vulkan_device_format_types_buffer_file,"w") as file:
                        fetch_vulkan_device_format_buffer_types_process = subprocess.Popen(fetch_vulkan_device_format_buffer_types_command,stdout=file,universal_newlines=True,shell=True)
                        fetch_vulkan_device_format_buffer_types_process.communicate()
                #      os.system("cat /tmp/gpu-viewer/VKDFORMATS.txt | awk '/^%s$/{flag=1};flag;/Common.*/{flag=0}' | awk '/buffer*/{flag=1;next}/Common*/{flag=0}flag' > /tmp/gpu-viewer/VKBuffer.txt " %(valueFormats[n].strip('\n')))
                    with open(Filenames.vulkan_device_format_types_buffer_file) as file1:
                        for k,line in enumerate(file1):
                            iter3 = ExpandDataObject2((((line.strip('\n')).strip('\t'))).replace("FORMAT_FEATURE_2_","")," "," "," ","")
                            iter2.children.append(iter3)
                        #    FormatsTab_Store.append(iter2,[(((line.strip('\n')).strip('\t'))).replace("FORMAT_FEATURE_2_","")," "," "," ",setBackgroundColor(k),setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j)])
                    j +=1
                formatsModel.set_autoexpand(True)
                FormatsTab_Store.append(toprow)
                


        labe1Format = "Formats (%d)" %len(valueFormats)
        notebook.set_tab_label(FormatsTab,Gtk.Label(label = labe1Format))

    def MemoryTypes(GPUname):
        
        # -------------------------------------------- Commands --------------------------------------------------
        fetch_vulkan_device_memory_types_command = "cat %s | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceFeatures:/{flag=0}flag'|awk '/VkPhysicalDeviceMemoryProperties:/{flag=1; next}/VkPhysicalDeviceFeatures:/{flag=0} flag'| awk '/memoryTypes: */{flag=1; next}/VkPhysicalDeviceFeatures:/{flag=0} flag' "%(Filenames.vulkaninfo_output_file,GPUname)
        fetch_vulkan_device_memory_types_lhs_command = "cat %s | %s | awk '/./'" %(Filenames.vulkan_device_memory_types_file,Filenames.remove_rhs_Command)
        fetch_vulkan_device_memory_types_rhs_command = "cat %s | grep -o heapIndex.* | grep -o '= .*' " %(Filenames.vulkan_device_memory_types_file)
        fetch_vulkan_device_memory_types_property_flags_command = "cat %s | grep propertyFlags | grep -o  =.* | grep -o ' .*' |  %s " %(Filenames.vulkan_device_memory_types_file,Filenames.remove_rhs_Command)
        #os.system("cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceFeatures:/{flag=0}flag'|awk '/VkPhysicalDeviceMemoryProperties:/{flag=1; next}/VkPhysicalDeviceFeatures:/{flag=0} flag' > /tmp/gpu-viewer/VKDMemoryType.txt" % GPUname)

        createMainFile(Filenames.vulkan_device_memory_types_file,fetch_vulkan_device_memory_types_command)
    
        vulkan_memory_types_lhs = fetchContentsFromCommand(fetch_vulkan_device_memory_types_lhs_command)

        vulkan_memory_types_rhs = fetchContentsFromCommand(fetch_vulkan_device_memory_types_rhs_command)

        vulkan_memory_types_property_flags = fetchContentsFromCommand(fetch_vulkan_device_memory_types_property_flags_command)

        j = 0
        mRhs = []
        with open(Filenames.vulkan_device_memory_types_file) as file1:
            for line in file1:
                if "heapIndex" in line:
                    mRhs.append(vulkan_memory_types_rhs[j].strip('= '))
                    j = j + 1
                else:
                    mRhs.append(" ")

        propertyFlag = ["DEVICE_LOCAL","HOST_VISIBLE_BIT","HOST_COHERENT_BIT","HOST_CACHED_BIT","LAZILY_ALLOCATED_BIT","PROTECTED_BIT","DEVICE_COHERENT_BIT_AMD","DEVICE_UNCACHED_BIT_AMD","RDMA_CAPABLE_BIT_NV"]

        MemoryTab_Store.remove_all()
    #    TreeMemory.set_model(MemoryTab_Store)
        p = 0
        n = 0
        groupName = None
        for i in range(len(vulkan_memory_types_lhs)):
            background_color = setBackgroundColor(i)
            if not (vulkan_memory_types_lhs[i] == groupName):
                if "memoryTypes" in vulkan_memory_types_lhs[i]:
                    if groupName == None:
                        iter = ExpandDataObject((vulkan_memory_types_lhs[i].strip('\n')).strip("\t")," ",)
                    else:
                        MemoryTab_Store.append(iter)
                #   iter = MemoryTab_Store.append(None,[(vulkan_memory_types_lhs[i].strip('\n')).strip("\t")," ",const.BGCOLOR3,const.COLOR3])
                        iter = ExpandDataObject((vulkan_memory_types_lhs[i].strip('\n')).strip("\t")," ",)
                #    MemoryTab_Store.append(iter)
                #    groupName = vulkan_memory_types_lhs[i]
                    n = n + 1
                    continue
                if "\t\t" in vulkan_memory_types_lhs[i] and "\t\t\t" not in vulkan_memory_types_lhs[i]:
                #    iter2 = MemoryTab_Store.append(iter,[(vulkan_memory_types_lhs[i].strip('\n')).strip("\t"),mRhs[i],background_color,const.COLOR3])
                    iter2 = ExpandDataObject((vulkan_memory_types_lhs[i].strip('\n')).strip("\t"),mRhs[i])
                    iter.children.append(iter2)
                #    MemoryTab_Store.append(iter)
                #    groupName = vulkan_memory_types_lhs[i]
                    continue
                if "\t\t\t" in vulkan_memory_types_lhs[i] and "\t\t\t\t" not in vulkan_memory_types_lhs[i]:
                #    iter3 = MemoryTab_Store.append(iter2,[((vulkan_memory_types_lhs[i].strip('\n')).strip("\t")).replace("MEMORY_PROPERTY_",""),mRhs[i],background_color,const.COLOR3])
                    iter3 = ExpandDataObject((((vulkan_memory_types_lhs[i].strip('\n')).strip("\t")).replace("MEMORY_PROPERTY_","")),mRhs[i])
                    iter2.children.append(iter3)
                #    print(vulkan_memory_types_lhs[i])
                #    iter.children.append(iter2)
                    groupName = vulkan_memory_types_lhs[i]
                    continue
                else:
                #    MemoryTab_Store.append(iter3,[((vulkan_memory_types_lhs[i].strip('\n')).strip("\t")).replace("FORMAT_","")," ",background_color,const.COLOR3])
                    iter4 = ExpandDataObject(((vulkan_memory_types_lhs[i].strip('\n')).strip("\t")).replace("FORMAT_","")," ",)
                    iter3.children.append(iter4)
        MemoryTab_Store.append(iter)
       #     if "MEMORY" in vulkan_memory_types_lhs[i]:
       #         continue
        #    if "None" in vulkan_memory_types_lhs[i] and n == 0:
        #        n = n + 1
        #        continue
        #    if "heapIndex" in vulkan_memory_types_lhs[i]:
        #        iter2 = MemoryTab_Store.append(iter,[(vulkan_memory_types_lhs[i].strip('\n')).strip("\t"),mRhs[i].strip('\n'),background_color,const.COLOR3])
        #        continue
        #    if  "IMAGE" in vulkan_memory_types_lhs[i] and ("FORMAT" not in vulkan_memory_types_lhs[i] or "color" not in vulkan_memory_types_lhs[i] or "sparse" not in vulkan_memory_types_lhs[i]):
        #        iter3 = MemoryTab_Store.append(iter2,[(vulkan_memory_types_lhs[i].strip('\n')).strip("\t")," ",background_color,const.COLOR3])
        #        continue
        #    if "\t\t\t" in vulkan_memory_types_lhs[i] and "\t\t\t\t" not in vulkan_memory_types_lhs[i]:
        #        MemoryTab_Store.append(iter3,[(vulkan_memory_types_lhs[i].strip('\n')).strip("\t")," ",background_color,const.COLOR3])
        #        continue
        #    if  "IMAGE" in vulkan_memory_types_lhs[i] and ("FORMAT" not in vulkan_memory_types_lhs[i] or "color" not in vulkan_memory_types_lhs[i] or "sparse" not in vulkan_memory_types_lhs[i]):
        #        iter3 = MemoryTab_Store.append(iter2,[(vulkan_memory_types_lhs[i].strip('\n')).strip("\t")," ",background_color,const.COLOR3])
        #        continue
        #    if "\t\t\t" in vulkan_memory_types_lhs[i] and "IMAGE" not in vulkan_memory_types_lhs[i]:
        #        MemoryTab_Store.append(iter3,[(vulkan_memory_types_lhs[i].strip('\n')).strip("\t")," ",background_color,const.COLOR3])
        #        continue
        #    if "propertyFlags" in vulkan_memory_types_lhs[i]:
        #                vulkan_memory_types_property_flags[p]
         #               #text = (mRhs[i].strip('\n')).strip(": ")
         #               iter2 = MemoryTab_Store.append(iter,[(vulkan_memory_types_lhs[i].strip('\n')).strip("\t")," ",background_color,const.COLOR3])
          #              continue
        #                dec = int(vulkan_memory_types_property_flags[p], 16)
        #                if  dec == 0:
        #                   n = 0
        #                binary = bin(dec)[2:]
        #                for j in range(len(binary)):
        #                    if binary[j] == '0':
        #                        Flag.insert(j, "false")
        #                    if binary[j] == '1':
        #                        Flag.insert(j, "true")
        #                for j in range(5 - len(binary)):
        #                    Flag.insert(0, "false")
        #                Flag.reverse()
        #                for k in range(len(Flag)):
        #                    if "true" in Flag[k]:
        #                        fColor = "GREEN"
        #                    elif "false" in Flag[k]:
        #                        fColor = "RED"
        #                    else:
        #                        fColor = const.COLOR3
         #   if "MEMORY_PROPERTY" in vulkan_memory_types_lhs[i]:
         #           print(vulkan_memory_types_lhs)
         #           MemoryTab_Store.append(iter2,[(vulkan_memory_types_lhs[i].strip('\n')).strip("\t")," ",background_color,const.COLOR3])
                 #       p = p + 1
         #   else:
          #      iter2 = MemoryTab_Store.append(iter,[(vulkan_memory_types_lhs[i].strip('\n')).strip("\t")," ",background_color,const.COLOR3])
          #      continue

        labe12 = "Memory Types (%d)" %len(vulkan_memory_types_property_flags)
        notebook.set_tab_label(MemoryTypeTab,Gtk.Label(label=labe12))

    #    TreeMemory.expand_all()

        #----------------------------------------------------- Memory Heaps ----------------------------------------------------------------------------------------------------------------------------------------

        fetch_vulkan_device_memory_heaps_command = "cat %s | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceFeatures:/{flag=0}flag'|awk '/memoryHeaps:/{flag=1; next}/memoryTypes:/{flag=0} flag' " %(Filenames.vulkaninfo_output_file,GPUname)
        fetch_vulkan_device_memory_heaps_lhs_command = "cat %s | %s| awk '/./'" %(Filenames.vulkan_device_memory_heaps_file,Filenames.remove_rhs_Command)
        fetch_vulkan_device_memory_heaps_rhs_command = "cat %s | grep = | grep -v count| grep -o  =.* | grep -o ' .*' | awk '{gsub(/\(.*/,'True');print}' " %(Filenames.vulkan_device_memory_heaps_file)

        createMainFile(Filenames.vulkan_device_memory_heaps_file,fetch_vulkan_device_memory_heaps_command)

        vulkan_memory_heaps_lhs = fetchContentsFromCommand(fetch_vulkan_device_memory_heaps_lhs_command)

        vulkan_memory_heaps_rhs = fetchContentsFromCommand(fetch_vulkan_device_memory_heaps_rhs_command)
  
        HeapTab_Store.remove_all()
    #    TreeHeap.set_model(HeapTab_Store)

        vulkan_memory_heaps_lhs = [i.strip('\t') for i in vulkan_memory_heaps_lhs]
    
        j = 0
        HCount = 0;iter = None
        for i in range(len(vulkan_memory_heaps_lhs)):
                if not (iter == vulkan_memory_heaps_lhs[i]):
                    if "memoryHeaps" in vulkan_memory_heaps_lhs[i]:
                        if iter == None:
                            toprow = ExpandDataObject(vulkan_memory_heaps_lhs[i],"")
                        else:
                            HeapTab_Store.append(toprow)
                            toprow = ExpandDataObject(vulkan_memory_heaps_lhs[i],"")
                    #    iter = HeapTab_Store.append(None,[vulkan_memory_heaps_lhs[i],"",const.BGCOLOR3])
                    #    toprow = ExpandDataObject((text.strip('\n')).replace(' count',''), vulkan_device_limits_rhs[j].strip('\n')
                    #    HeapTab_Store.append(toprow)
                        HCount = HCount + 1
                        iter = vulkan_memory_heaps_lhs[i]
                        continue
                    if "None" in vulkan_memory_heaps_lhs[i] or "MEMORY_HEAP" in vulkan_memory_heaps_lhs[i] and "memoryHeaps" not in vulkan_memory_heaps_lhs[i]:
                    #    HeapTab_Store.append(iter2,[vulkan_memory_heaps_lhs[i],"",setBackgroundColor(i)])
                        childchildrow = ExpandDataObject(vulkan_memory_heaps_lhs[i], " ")
                        childrow.children.append(childchildrow)
                    #    toprow.children.append(childrow)
                    #    HeapTab_Store.append(toprow)
                        iter = vulkan_memory_heaps_lhs[i]
                        continue
                    if "size" in vulkan_memory_heaps_lhs[i] or "budget" in vulkan_memory_heaps_lhs[i] or "usage" in vulkan_memory_heaps_lhs[i]:
                    #    iter2 = HeapTab_Store.append(iter,[vulkan_memory_heaps_lhs[i],getDeviceSize(vulkan_memory_heaps_rhs[j]),setBackgroundColor(i)])
                        childrow = ExpandDataObject(vulkan_memory_heaps_lhs[i], getDeviceSize(vulkan_memory_heaps_rhs[j]))
                        toprow.children.append(childrow)
                        j = j + 1
                        iter = vulkan_memory_heaps_lhs[i]
                        continue
                    else:
                        if "None" not in vulkan_memory_heaps_lhs[i] or "MEMORY_HEAP" not in vulkan_memory_heaps_lhs[i]:
                    #    iter2 = HeapTab_Store.append(iter,[vulkan_memory_heaps_lhs[i],"",setBackgroundColor(i)])
                            childrow = ExpandDataObject(vulkan_memory_heaps_lhs[i], " ")
                            iter = vulkan_memory_heaps_lhs[i]
                            toprow.children.append(childrow)

            #    toprow.children.append(childrow)
        HeapTab_Store.append(toprow)

    #    TreeHeap.expand_all()
        labe13 = "Memory Heaps (%d)" %(HCount)
        notebook.set_tab_label(MemoryHeapTab,Gtk.Label(label=labe13))
    #    label2 = "Memory Types (%d) " %(len(vulkan_memory_types_property_flags),(HCount))
    #    notebook.set_tab_label(MemoryTab,Gtk.Label(label=label2))

    def Queues(GPUname):

        #------------------------------ commands ---------------------------------------------------------------------------------------

        fetch_vulkan_device_queues_command = "cat %s | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceMemoryProperties:/{flag=0}flag'|awk '/VkQueueFamilyProperties:*/{flag=1;next}/VkPhysicalDeviceMemoryProperties.*/{flag=0} flag' | awk '/./'" %(Filenames.vulkaninfo_output_file,GPUname)
        fetch_vulkan_device_queues_lhs_command = "cat %s | %s " %(Filenames.vulkan_device_queues_file,Filenames.remove_rhs_Command)
        fetch_vulkan_device_queues_rhs_command = "cat %s | grep -o [=,:].* | grep -o ' .*' " %(Filenames.vulkan_device_queues_file)
        fetch_vulkan_device_queue_counts_command = "cat %s | grep queueCount " %(Filenames.vulkan_device_queues_file)

        createMainFile(Filenames.vulkan_device_queues_file,fetch_vulkan_device_queues_command)
        
        vulkan_device_queues_lhs = fetchContentsFromCommand(fetch_vulkan_device_queues_lhs_command)

        vulkan_device_queues_rhs = fetchContentsFromCommand(fetch_vulkan_device_queues_rhs_command)
        
        vulkan_device_queue_counts = fetchContentsFromCommand(fetch_vulkan_device_queue_counts_command)

        QueueTab_Store.remove_all()
     #   TreeQueue.set_model(QueueTab_Store)

        j = 0
        qRHS = []
        with open(Filenames.vulkan_device_queues_file) as file1:
            for line in file1:
                if " = " in line:
                    qRHS.append(vulkan_device_queues_rhs[j])
                    j = j + 1
                else:
                    qRHS.append("")
        
        qRHS.pop(0)
    
        k = 0; groupName = None
        for i in range(len(vulkan_device_queues_lhs)):
            background_color = setBackgroundColor(i)
            if "true" in qRHS[i]:
                fColor = "GREEN"
            elif "false" in qRHS[i]:
                fColor = "RED"
            else:
                fColor = None
            if not (groupName == vulkan_device_queues_lhs[i]):
                if "Properties[" in vulkan_device_queues_lhs[i]:
                    if groupName == None:
                        toprow = ExpandDataObject((vulkan_device_queues_lhs[i].strip('\n')).strip('\t'),qRHS[i])
                    else:
                        QueueTab_Store.append(toprow)
                        toprow = ExpandDataObject((vulkan_device_queues_lhs[i].strip('\n')).strip('\t'),qRHS[i])
                #    iter1 = QueueTab_Store.append(None,[(vulkan_device_queues_lhs[i].strip('\n')).strip('\t'),qRHS[i],const.BGCOLOR3,fColor])
                #    k = 0
                    groupName = vulkan_device_queues_lhs[i]
                    continue
                if "---" in vulkan_device_queues_lhs[i]:
                    continue
                if "\t\t\t" in vulkan_device_queues_lhs[i] and "\t\t\t\t" not in vulkan_device_queues_lhs[i]:
                    iter3 = ExpandDataObject((vulkan_device_queues_lhs[i].strip('\n')).strip('\t'),(qRHS[i].strip('\n')).replace('count = ',''))
                    iter2.children.append(iter3)
                #    iter3 = QueueTab_Store.append(iter2,[(vulkan_device_queues_lhs[i].strip('\n')).strip('\t'),(qRHS[i].strip('\n')).replace('count = ',''),background_color,fColor])
                    continue
                if "\t\t\t\t" in vulkan_device_queues_lhs[i]:
                    iter4 = ExpandDataObject((vulkan_device_queues_lhs[i].strip('\n')).strip('\t'),qRHS[i].strip('\n'))
                    iter3.children.append(iter4)
                #    QueueTab_Store.append(iter3,[(vulkan_device_queues_lhs[i].strip('\n')).strip('\t'),qRHS[i].strip('\n'),background_color,fColor])
                    continue
                else :
                    if "queueFlags" in vulkan_device_queues_lhs[i] or "VkQueueFamily" in line:
                        supportedFlags = qRHS[i].split("|")
                        iter2 = ExpandDataObject((vulkan_device_queues_lhs[i].strip('\n')).strip('\t'),"")
                        toprow.children.append(iter2)
                    #    iter2 = QueueTab_Store.append(iter1,[(vulkan_device_queues_lhs[i].strip('\n')).strip('\t')," ",background_color,fColor])
                        for count,flags in enumerate(supportedFlags, start= i + 1):
                            iter2_1 = ExpandDataObject(flags.replace("QUEUE_",""),"")
                            iter2.children.append(iter2_1)
                        #    QueueTab_Store.append(iter2,[flags.replace("QUEUE_",""),"",setBackgroundColor(count),fColor])
        
                    else:
                        iter2 = ExpandDataObject((vulkan_device_queues_lhs[i].strip('\n')).strip('\t'),qRHS[i].strip('\n'))
                        toprow.children.append(iter2)
                    #    iter2 = QueueTab_Store.append(iter1,[(vulkan_device_queues_lhs[i].strip('\n')).strip('\t'),qRHS[i].strip('\n'),background_color,fColor])
        QueueTab_Store.append(toprow)           
    #    TreeQueue.expand_all()
        label = "Queues (%d)" % len(vulkan_device_queue_counts)
        notebook.set_tab_label(QueueTab, Gtk.Label(label=label))

    def Instance():

        #--------------------------------------------------Commands -----------------------------------------------------------------------------------------

        fetch_vulkan_device_instances_command = "cat %s | awk '/Instance Extensions.*/{flag=1;next}/Layers:.*/{flag=0}flag'| grep VK_ | sort " %(Filenames.vulkaninfo_output_file)
        fetch_vulkan_device_instances_lhs_command = "cat %s | %s " %(Filenames.vulkan_device_instances_file,Filenames.remove_rhs_Command)
        fetch_vulkan_device_instances_rhs_command = "cat %s | grep -o 'revision.*' | grep -o ' .*'" %(Filenames.vulkan_device_instances_file)

        createMainFile(Filenames.vulkan_device_instances_file,fetch_vulkan_device_instances_command)

        vulkan_device_instance_lhs = fetchContentsFromCommand(fetch_vulkan_device_instances_lhs_command)

        vulkan_device_instance_rhs = fetchContentsFromCommand(fetch_vulkan_device_instances_rhs_command)

        InstanceTab_Store.remove_all()

        for i in range(len(vulkan_device_instance_lhs)):
            background_color = setBackgroundColor(i)
            InstanceTab_Store.append(DataObject(vulkan_device_instance_lhs[i].strip('\t'),vulkan_device_instance_rhs[i]))

        label = "Instance Extensions (%d)" %len(vulkan_device_instance_lhs)
#        InstanceNotebook.set_tab_label(InstanceExtTab, Gtk.Label(label=label))


        #-------------------------------------------------------------Layers Commands -----------------------------------------------------------------------------------------------------------------------------------
        fetch_vulkan_device_layers_command = "cat %s  | awk '/Layers:.*/{flag=1;next}/Presentable Surfaces.*/{flag=0}flag' | awk '/./' " %(Filenames.vulkaninfo_output_file)
        fetch_vulkan_device_layer_names_command = "cat %s | grep _LAYER_ | awk '{gsub(/\(.*/,'True');print} '" %(Filenames.vulkan_device_layers_file)
        fetch_vulkan_device_layer_vulkan_version_command = "cat %s | grep ^VK | grep -o 'Vulkan.*' | awk '{gsub(/,.*/,'True');print}' | grep -o 'version.*' | grep -o ' .*' " %(Filenames.vulkan_device_layers_file)
        fetch_vulkan_device_layer_version_command = "cat %s | grep ^VK | grep -o 'layer version.*' | awk '{gsub(/:.*/,'True');print}' | grep -o version.* | grep -o ' .*' "  %(Filenames.vulkan_device_layers_file)
        fetch_vulkan_device_layer_description_command = "cat %s | grep _LAYER_ | grep -o \(.* | awk '{gsub(/\).*/,'True');print}'| awk '{gsub(/\(/,'True');print}' " %(Filenames.vulkan_device_layers_file)
        fetch_vulkan_device_layer_extension_count_command = "cat %s | grep 'Layer Extensions' | grep -o '=.*' | grep -o ' .*' " %(Filenames.vulkan_device_layers_file)

        createMainFile(Filenames.vulkan_device_layers_file,fetch_vulkan_device_layers_command,)
        
        layer_names = fetchContentsFromCommand(fetch_vulkan_device_layer_names_command)

        layer_vulkan_version = fetchContentsFromCommand(fetch_vulkan_device_layer_vulkan_version_command)

        layer_version = fetchContentsFromCommand(fetch_vulkan_device_layer_version_command)

        layer_descriptions = fetchContentsFromCommand(fetch_vulkan_device_layer_description_command)

        layer_extension_counts = fetchContentsFromCommand(fetch_vulkan_device_layer_extension_count_command)

        LayerTab_Store.remove_all()

        label = "Instance Extensions (%d)" % (len(vulkan_device_instance_lhs))
        label2 = "Instance Layers (%d)" %len(layer_names)
        notebook.set_tab_label(InstanceExtTab, Gtk.Label(label=label))
        notebook.set_tab_label(InstanceLayersTab, Gtk.Label(label=label2))
        i = 0; j =1
        groupName = None
        with open(Filenames.vulkan_device_layers_file) as file:
            for line in file:
                if '====' in line:
                    continue
                if not (groupName == line):
                    if "VK_LAYER" in line:
                        if groupName == None:
                            toprow = ExpandDataObject2(layer_names[i], layer_vulkan_version[i], layer_version[i],layer_extension_counts[i], layer_descriptions[i])
                        else:
                            LayerTab_Store.append(toprow)
                            toprow = ExpandDataObject2(layer_names[i], layer_vulkan_version[i], layer_version[i],layer_extension_counts[i], layer_descriptions[i])
                    #    iter = LayerTab_Store.append(None,[layer_names[i], layer_vulkan_version[i], layer_version[i],
                    #    layer_extension_counts[i], layer_descriptions[i],
                        groupName = line
                        i = i + 1
                        continue
                    elif "\t" in line and "\t\t" not in line:
                        iter2 = ExpandDataObject2(((line.strip('\n')).strip('\t')).replace('count =',' '),"","","","")
                        toprow.children.append(iter2)
                    #    continue
                    #    iter2 = LayerTab_Store.append(iter,[((line.strip('\n')).strip('\t')).replace('count =',' '),"","","","",setBackgroundColor(j)])
                     #   j = j + 1
                    elif "\t\t" in line and "\t\t\t" not in line and "Layer-Device" not in line:
                        iter3 = ExpandDataObject2(((line.strip('\n')).strip('\t')).replace('count =',' '),"","","","")
                        iter2.children.append(iter3)
                     #   continue
                    #    iter3 = LayerTab_Store.append(iter2,[((line.strip('\n')).strip('\t')).replace('count =',' '),"","","","",setBackgroundColor(j)])
                    #    j = j + 1
                    elif "Layer-Device" in line:
                        iter4 = ExpandDataObject2(((line.strip('\n')).strip('\t')).replace('count =',' '),"","","","")
                        iter3.children.append(iter4)
                    #    continue
                    #    iter4 = LayerTab_Store.append(iter3,[((line.strip('\n')).strip('\t')).replace('count =',' '),"","","","",setBackgroundColor(j)])
                    #    j = j + 1
                    else:
                        iter5 = ExpandDataObject2(((line.strip('\n')).strip('\t')).replace('count =',' '),"","","","")
                        iter4.children.append(iter5)
                    #    continue
                    #    LayerTab_Store.append(iter4,[((line.strip('\n')).strip('\t')).replace('count =',' '),"","","","",setBackgroundColor(j)])
                    #    j = j + 1
            LayerTab_Store.append(toprow)

    def selectProperties(dropdown, _pspec):
        selected =dropdown.props.selected_item
        property = ""
        if selected is not None:
            property = selected.props.string


        fetch_device_properties_filter_properties_command = "cat %s | awk '/./' " %(Filenames.vulkan_device_properties_file)
        fetch_device_properties_selected_filter_properties_command = "cat %s | awk '/VkPhysicalDevice%s/{flag=1;next}/Properties.*/{flag=0}flag' " %(Filenames.vulkan_device_properties_file,property)
        fetch_device_properties_filter_properties_lhs_command = "cat %s | %s " %(Filenames.vulkan_device_filter_properties_file,Filenames.remove_rhs_Command)
        fetch_device_properties_filter_properties_rhs_command = "cat %s | grep -o =.* | grep -o ' .*' " %(Filenames.vulkan_device_filter_properties_file)

        if property is None:
            property = " "
        elif "Show All Device Properties" in property:
            createMainFile(Filenames.vulkan_device_filter_properties_file,fetch_device_properties_filter_properties_command)
        else:
            createMainFile(Filenames.vulkan_device_filter_properties_file,fetch_device_properties_selected_filter_properties_command)

        createMainFile(Filenames.vulkan_device_filter_properties_lhs_file,fetch_device_properties_filter_properties_lhs_command)
     #   os.system("%s > /tmp/gpu-viewer/filterPropertiesLHS.txt"%fetch_device_properties_filter_properties_lhs_command)


        # fgColor, value = colorTrueFalse("/tmp/gpu-viewer/VKDDevicesparseinfo1.txt", "= 1")
        value = fetchContentsFromCommand(fetch_device_properties_filter_properties_rhs_command)
        value1 = []
        value2 = []
        fgColor = []
        i = 0
        with open(Filenames.vulkan_device_filter_properties_file, "r") as file1:
            for line in file1:
                if "= " in line:
                    if "Max" in line or "Min" in line or "major" in line or "minor" in line or "patch" in line:
                        value1.append(str(value[i]))
                    else:
                        value1.append(value[i])
                    i += 1
                else:
                    value1.append(" ")

        for i in value1:
            if "false" in i:
                value2.append("false")
                fgColor.append(const.COLOR2)
            elif "true" in i:
                value2.append("true")
                fgColor.append(const.COLOR1)
            else:
                value2.append(i)
                fgColor.append(const.COLOR3)

        PropertiesTab_Store.remove_all()
    #    TreeSparse.set_model(SparseTab_Store_filter)

        if "Show All Device Properties" in property:
            k = 0;
            count = 0
            groupName = None
            with open(Filenames.vulkan_device_filter_properties_lhs_file, "r") as file1:
                for i, line in enumerate(file1):
                    text = line.strip('\t')
                    if "---" in line or "====" in line:
                        continue
                    if not (groupName == text):
                        if "Vk" in line and "conformanceVersion" not in line:
                            text1 = (text.replace("VkPhysicalDevice",'').replace(":",""))
                            k = 0
                            count += 1
                            background_color = const.BGCOLOR3
                            if groupName == None:
                                toprow = ExpandDataObject((text1.strip('\n')).replace(" count",''), value2[i].strip('\n'))
                            #iter1 = SparseTab_Store.append(None, [(text1.strip('\n')).replace(" count",''), value2[i].strip('\n'), background_color, fgColor[i]])
                            else:
                                PropertiesTab_Store.append(toprow)
                                toprow = ExpandDataObject((text1.strip('\n')).replace(" count",''), value2[i].strip('\n'))
                            groupName = text
                        else:
                            background_color = setBackgroundColor(k)

                            #if "width" not in line and "height" not in line and "SUBGROUP" not in line and "RESOLVE" not in line and "SHADER_STAGE" not in line and "SAMPLE_COUNT" not in line and "\t\t" not in line:
                            if "\t\t" not in line:
                            #    iter2 = SparseTab_Store.append(iter1,
                            #                       [(text.strip('\n')).replace("count",''), value2[i].strip('\n'), background_color, fgColor[i]])
                                iter2 = ExpandDataObject((text.strip('\n')).replace("count",''), value2[i].strip('\n'))
                                toprow.children.append(iter2)
                            #if "width" in line or "height" in line or "SUBGROUP" in line or "RESOLVE" in line or "SHADER_STAGE" in line or "SAMPLE_COUNT" in line or "\t\t" in line:
                            if "\t\t" in line:
                            # SparseTab_Store.append(iter2, [(text.strip('\n')).replace(" count",''), value2[i].strip('\n'), background_color,
                            #                                fgColor[i]])
                                iter3 = ExpandDataObject((text.strip('\n')).replace(" count",''), value2[i].strip('\n'))
                                iter2.children.append(iter3)
                                k += 1
                PropertiesTab_Store.append(toprow)
            #        TreeSparse.expand_all()
        else:
            k = 0
            count = 0
   #         iter = SparseTab_Store.append(None,[property,"",setBackgroundColor(1),const.COLOR3])
            toprow = ExpandDataObject(property,"")
            with open(Filenames.vulkan_device_filter_properties_lhs_file, "r") as file1:
                for i, line in enumerate(file1):
                    text = line.strip('\t')
                    if "---" in line or "====" in line:
                        continue
                    else:
                        background_color = setBackgroundColor(k)
                        #if "width" not in line and "height" not in line and "SUBGROUP" not in line and "RESOLVE" not in line and "SHADER_STAGE" not in line:
                        if "\t\t" not in line:
                        #    iter2 = SparseTab_Store.append(iter,
                         #                      [text.strip('\n'), value2[i].strip('\n'), background_color, fgColor[i]])
                            iter2 = ExpandDataObject((text.strip('\n')).replace("count",''), value2[i].strip('\n'))
                            toprow.children.append(iter2)
                        #if "width" in line or "height" in line or "SUBGROUP" in line or "RESOLVE" in line or "SHADER_STAGE" in line:
                        if "\t\t" in line:
                                iter3 = ExpandDataObject((text.strip('\n')).replace(" count",''), value2[i].strip('\n'))
                                iter2.children.append(iter3)
                        k += 1
                PropertiesTab_Store.append(toprow)
                #    TreeSparse.expand_all()

    def Surface(GPU):

        fetch_vulkan_device_surface_command = "cat %s | awk '/Presentable Surfaces:.*/{flag=1}/Device Properties and Extensions.*/{flag=0}flag' | awk '/Presentable Surfaces:.*/{flag=1;next}/Groups.*/{flag=0}flag'  | awk '/GPU id : %d/{flag=1;next}/GPU id.*/{flag=0}flag' | awk '/./'" %(Filenames.vulkaninfo_output_file,GPU)
        fetch_vulkan_device_surface_rhs_command = "cat %s |   grep -o [:,=].* | awk '{gsub(/=/,'True');print}' | grep -o ' .*'  " %(Filenames.vulkan_device_surface_file,)
        fetch_vulkan_device_surface_lhs_command = "cat %s | awk '{gsub(/[=,:] .*/,'True');print}' | awk '{gsub(/count.*/,'True');print}'" %(Filenames.vulkan_device_surface_file)
     
        createMainFile(Filenames.vulkan_device_surface_file,fetch_vulkan_device_surface_command)

        valueRHS = fetchContentsFromCommand(fetch_vulkan_device_surface_rhs_command)
        valueLHS = fetchContentsFromCommand(fetch_vulkan_device_surface_lhs_command)

        SurfaceRHS = []
        SurfaceTab_Store.remove_all()
    #    TreeSurface.set_model(SurfaceTab_Store)
        groupName = None
        with open(Filenames.vulkan_device_surface_file, "r") as file1:
            j=0
            for i,line in enumerate(file1):
                background_color = setBackgroundColor(i)
                if '---' in line:
                    continue
                if not (valueLHS[i] == groupName):
                    if "=" in line:
                        SurfaceRHS = valueRHS[j].strip('\n')
                    #    print(SurfaceRHS)
                        j = j+1
                    else:
                        SurfaceRHS = " "
                    if "\t" in line and "\t\t" not in line:
                        if groupName == None:
                            toprow = ExpandDataObject((valueLHS[i].strip('\n')).strip('\t'),SurfaceRHS.replace('count ',''))
                        else:
                            SurfaceTab_Store.append(toprow)
                            toprow = ExpandDataObject((valueLHS[i].strip('\n')).strip('\t'),SurfaceRHS.replace('count ',''))
                    #    background_color = const.BGCOLOR3
                    #    iter1 = SurfaceTab_Store.append(None,[(valueLHS[i].strip('\n')).strip('\t'),SurfaceRHS.replace('count ',''),background_color])
                        groupName = valueLHS[i]
                        continue
                    if "\t\t" in line and "\t\t\t" not in line:
                        iter2 = ExpandDataObject((valueLHS[i].strip('\n')).strip('\t'),SurfaceRHS.replace('count ',''))
                        toprow.children.append(iter2)
                    #    iter2 = SurfaceTab_Store.append(iter1,[(valueLHS[i].strip('\n')).strip('\t'),SurfaceRHS.replace('count ',''),background_color])
                        continue
                    if "\t\t\t" in line and "\t\t\t\t" not in line:
                        iter3 = ExpandDataObject((valueLHS[i].strip('\n')).strip('\t'),SurfaceRHS.replace('count ',''))
                        iter2.children.append(iter3)
                    #    iter3 = SurfaceTab_Store.append(iter2,[(valueLHS[i].strip('\n')).strip('\t'),SurfaceRHS.replace('count ',''),background_color])
                        continue
                    if "\t\t\t\t" in line and "\t\t\t\t\t" not in line:
                        iter4 = ExpandDataObject((valueLHS[i].strip('\n')).strip('\t'),SurfaceRHS.replace('count ',''))
                        iter3.children.append(iter4)
                    #    iter4 = SurfaceTab_Store.append(iter3,[(valueLHS[i].strip('\n')).strip('\t'),SurfaceRHS.replace('count ',''),background_color]) 
                    else:
                        iter5 = ExpandDataObject((valueLHS[i].strip('\n')).strip('\t'),SurfaceRHS.replace('count ',''))
                        iter4.children.append(iter5)
                    #    SurfaceTab_Store.append(iter4,[(valueLHS[i].strip('\n')).strip('\t'),SurfaceRHS.replace('count ',''),background_color])
            SurfaceTab_Store.append(toprow)
        #    TreeSurface.expand_all()
    
    def Groups(GPU):

        fetch_vulkan_device_groups_command = "cat %s | awk '/Device Groups.*/{flag=1}/Device Properties and Extensions.*/{flag=0}flag' | awk '/Group %d:/{flag=1;next}/Group.*/{flag=0}flag' | awk '/./'" %(Filenames.vulkaninfo_output_file,GPU)
        fetch_vulkan_device_groups_lhs_command = "cat %s | awk '{gsub(/[=] .*/,'True');print}' " %(Filenames.vulkan_device_groups_file)
        fetch_vulkan_device_groups_rhs_command = "cat %s | grep -o =.* | grep -o ' .*' " %(Filenames.vulkan_device_groups_file)

        createMainFile(Filenames.vulkan_device_groups_file,fetch_vulkan_device_groups_command)
        
        groupsLHS = fetchContentsFromCommand(fetch_vulkan_device_groups_lhs_command)
        groupsRHS = fetchContentsFromCommand(fetch_vulkan_device_groups_rhs_command)
        
        Groups_Store.clear()
        TreeGroups.set_model(Groups_Store)
        j = 0
        with open(Filenames.vulkan_device_groups_file, "r") as file1:
            for i,line in enumerate(file1):
                if "=" in line:
                    groupvalueRHS = groupsRHS[j].strip('\n')
                    j = j + 1
                else:
                    groupvalueRHS = ""
                if 'Properties' in line or "Capabilities" in line:
                    iter1 = Groups_Store.append(None,[((groupsLHS[i].strip('\n')).strip('\t').replace(': count','')),groupvalueRHS,const.BGCOLOR3])
                    continue
                if '\t\t' in line and not '\t\t\t\t' in line and not '\t\t\t' in line:
                    iter2 = Groups_Store.append(iter1,[((groupsLHS[i].strip('\n')).strip('\t')).replace(': count ',''),groupvalueRHS,setBackgroundColor(i)])
                    continue
                if "\t\t\t" in line and not "\t\t\t\t" in line:
                    iter3 = Groups_Store.append(iter2,[((groupsLHS[i].strip('\n')).strip('\t')).replace(': count ',''),groupvalueRHS,setBackgroundColor(i)])
                    continue
                else:
                    Groups_Store.append(iter3,[(groupsLHS[i].strip('\n')).strip('\t'),groupvalueRHS,setBackgroundColor(i)])

        TreeGroups.expand_all()


    def _on_search_method_changed(search_entry,filterColumn):
        filterColumn.changed(Gtk.FilterChange.DIFFERENT)

    def _do_filter_extension_view(item, filter_list_model):
        search_text_widget = extensionSearchEntry.get_text()
        return search_text_widget.upper() in item.column1.upper() or search_text_widget.upper() in item.column2.upper()
    
    def _do_filter_feature_view(item, filter_list_model):
        search_text_widget = featureSearchEntry.get_text()
        return search_text_widget.upper() in item.column1.upper() or search_text_widget.upper() in item.column2.upper()

    def _do_filter_instances_view(item, filter_list_model):
        search_text_widget = instanceSearchEntry.get_text()
        return search_text_widget.upper() in item.column1.upper() or search_text_widget.upper() in item.column2.upper()

    def _do_filter_limits_view(item, filter_list_model):
        search_text_widget = limitsSearchEntry.get_text()
        return search_text_widget.upper() in item.data.upper() or search_text_widget.upper() in item.data2.upper()

    def _do_filter_properties_view(item, filter_list_model):
        search_text_widget = propertySearchEntry.get_text()
        return search_text_widget.upper() in item.data.upper() or search_text_widget.upper() in item.data2.upper()


    def _do_filter_layers_view(item, filter_list_model):
        search_text_widget = layerSearchEntry.get_text()
        return search_text_widget.upper() in item.data.upper() or search_text_widget.upper() in item.data2.upper()


    def _do_filter_formats_view(item, filter_list_model):
        search_text_widget = formatSearchEntry.get_text()
        return search_text_widget.upper() in item.data.upper() or search_text_widget.upper() in item.data2.upper()

    def searchFormatsTree(model, iter, Tree):
        search_query = formatSearchEntry.get_text().lower()
        for i in range(Tree.get_n_columns()):
            value = model.get_value(iter, i).lower()
            if search_query in value:
                return True

    def searchInstanceLayersTree(model, iter, Tree):
        search_query = layerSearchEntry.get_text().lower()
        for i in range(Tree.get_n_columns()):
            value = model.get_value(iter, i).lower()
            if search_query in value:
                return True

    def radcall(combo,dummy):
        text = combo.props.selected
        for i in range(len(gpu_list)):
            if text == i:
                Devices(text)
                Limits(text)
                Features(text)
                Extensions(text)
                Formats(text)
                MemoryTypes(text)
                Queues(text)
                Surface(text)
       #         Groups(text)
            gpu_image = getGpuImage(gpu_list[text])
            image_renderer.set_pixbuf(gpu_image)
        Instance()


    grid = Gtk.Grid()
    grid.set_row_spacing(10)
    tab2.append(grid)
    DevicesFrame = Gtk.Frame()
    grid.attach(DevicesFrame,0,1,1,1)

    notebook = Gtk.Notebook()
    notebook.set_property("scrollable", True)
    notebook.set_property("enable-popup", True)
    grid.attach(notebook, 0, 2, 1, 1)

    # ----------------Creating the Device Info Tab ------------

    DeviceTab = Gtk.Box(spacing=10)
    DeviceGrid = createSubTab(DeviceTab, notebook, "Device")
    DeviceGrid.set_row_spacing(3)

    DeviceTab_Store = Gtk.TreeStore(str,GdkPixbuf.Pixbuf, str,str)
    TreeDevice = Gtk.TreeView.new_with_model(DeviceTab_Store)
    TreeDevice.set_property("enable-grid-lines", 1)

    for i,column_title in enumerate(DeviceTitle):
        if i == 1:
            renderer_pixbuf = Gtk.CellRendererPixbuf()
            column_pixbuf = Gtk.TreeViewColumn(column_title)
            column_pixbuf.pack_start(renderer_pixbuf, False)
            column_pixbuf.add_attribute(renderer_pixbuf,"pixbuf",1)
            column_pixbuf.set_property("min-width", 20)
            column_pixbuf.add_attribute(renderer_pixbuf,"cell-background",3)
            TreeDevice.append_column(column_pixbuf)
        else:
            renderer_text = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer_text, text=i)
            column.add_attribute(renderer_text,"background",3)
            TreeDevice.append_column(column)
 #   setColumns(TreeDevice, DeviceTitle, 20, 0.0)

    DeviceScrollbar = create_scrollbar(TreeDevice)
    DeviceGrid.attach(DeviceScrollbar,0,0,1,1)

    # ------------ Creating the Limits Tab -------------------------------------------
    LimitsTab = Gtk.Box(spacing=10)
    LimitsGrid = createSubTab(LimitsTab, notebook, "Limits")
    LimitsGrid.set_row_spacing(3)

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
    LimitsTab_Store = Gio.ListStore.new(ExpandDataObject)
    filterSortLimitsStore = Gtk.FilterListModel(model=LimitsTab_Store)
    filter_limits = Gtk.CustomFilter.new(_do_filter_limits_view, filterSortLimitsStore)
    filterSortLimitsStore.set_filter(filter_limits)

    limitModel = Gtk.TreeListModel.new(filterSortLimitsStore,False,True,add_tree_node)
    limitSelection.set_model(limitModel)

    limitsColumnView.set_model(limitSelection)

    limitColumnLhs = Gtk.ColumnViewColumn.new("Device Limits",factory_limits)
    limitColumnLhs.set_resizable(True)
    limitColumnRhs = Gtk.ColumnViewColumn.new("Value",factory_limits_value)
    limitColumnRhs.set_expand(True)

    limitsColumnView.append_column(limitColumnLhs)
    limitsColumnView.append_column(limitColumnRhs)


    limitsFrameSearch = Gtk.Frame()
    limitsSearchEntry = Gtk.SearchEntry()
    limitsSearchEntry.set_property("placeholder_text","Type here to filter.....")
    limitsSearchEntry.connect("search-changed", _on_search_method_changed,filter_limits)
#    limitsSearchEntry = createSearchEntry(LimitsTab_Store_filter)
    limitsFrameSearch.set_child(limitsSearchEntry)
    LimitsGrid.attach(limitsFrameSearch,0,0,1,1)
    LimitsScrollbar = create_scrollbar(limitsColumnView)
    LimitsGrid.attach_next_to(LimitsScrollbar, limitsFrameSearch, Gtk.PositionType.BOTTOM, 1, 1)

#    LimitsTab_Store_filter.set_visible_func(searchLimitsTree, data=TreeLimits)

    propertiesColumnView = Gtk.ColumnView()
    propertiesColumnView.props.show_row_separators = True
    propertiesColumnView.props.show_column_separators = False

    factory_properties = Gtk.SignalListItemFactory()
    factory_properties.connect("setup",setup_expander)
    factory_properties.connect("bind",bind_expander)

    factory_properties_value = Gtk.SignalListItemFactory()
    factory_properties_value.connect("setup",setup)
    factory_properties_value.connect("bind",bind1)

    propertiesSelection = Gtk.SingleSelection()
    PropertiesTab_Store = Gio.ListStore.new(ExpandDataObject)
    filterSortPropertiesStore = Gtk.FilterListModel(model=PropertiesTab_Store)
    filter_properties = Gtk.CustomFilter.new(_do_filter_properties_view, filterSortPropertiesStore)
    filterSortPropertiesStore.set_filter(filter_properties)

    propertiesModel = Gtk.TreeListModel.new(filterSortPropertiesStore,False,True,add_tree_node)
    propertiesSelection.set_model(propertiesModel)

    propertiesColumnView.set_model(propertiesSelection)

    propertiesColumnLhs = Gtk.ColumnViewColumn.new("Device Limits",factory_properties)
    propertiesColumnLhs.set_resizable(True)
    propertiesColumnRhs = Gtk.ColumnViewColumn.new("Value",factory_properties_value)
    propertiesColumnRhs.set_expand(True)

    propertiesColumnView.append_column(propertiesColumnLhs)
    propertiesColumnView.append_column(propertiesColumnRhs)

    propertiesTab = Gtk.Box(spacing=10)
    propertiesGrid = createSubTab(propertiesTab, notebook, "Properties")
    propertiesGrid.set_row_spacing(5)
    propertiesList = Gtk.StringList()
    propertiesDropdown = Gtk.DropDown()
    propertiesDropdown.set_model(propertiesList)
    propertiesDropdown.connect('notify::selected-item',selectProperties)
    setMargin(propertiesDropdown,2,1,2)
#    propertiesGrid.add(propertiesCombo)



#    SparseTab_Store = Gtk.TreeStore(str, str, str, str)
#    SparseTab_Store_filter = SparseTab_Store.filter_new()
#    TreeSparse = Gtk.TreeView.new_with_model(SparseTab_Store_filter)
#    TreeSparse.set_property("enable-grid-lines", 1)
 #   TreeSparse.set_property("enable-tree-lines", True)
#    TreeSparse.set_enable_search(True)
#    TreeSparse.set_property("can-focus", False)

 #   for i, column_title in enumerate(SparseTitle):
 #       Sparserenderer = Gtk.CellRendererText()
  #      column = Gtk.TreeViewColumn(column_title, Sparserenderer, text=i)
  #      column.set_sort_column_id(i)
  #      column.set_resizable(True)
  #      column.set_reorderable(True)
  #      column.set_property("min-width", const.MWIDTH)
  #      if i == 1:
  #          column.add_attribute(Sparserenderer, "foreground", 3)
  #      column.add_attribute(Sparserenderer, "background", 2)
  #      TreeSparse.append_column(column)

    propertySearchEntry = Gtk.SearchEntry()
    propertySearchEntry.set_property("placeholder_text","Type here to filter.....")
    propertySearchEntry.connect("search-changed", _on_search_method_changed,filter_properties)
    propertiesGrid.attach(propertySearchEntry,0,0,12,1)
    propertiesGrid.attach_next_to(propertiesDropdown,propertySearchEntry,Gtk.PositionType.RIGHT,3,1)
    propertiesScrollbar = create_scrollbar(propertiesColumnView)
    propertiesGrid.attach_next_to(propertiesScrollbar, propertySearchEntry, Gtk.PositionType.BOTTOM, 15, 1)

#    SparseTab_Store_filter.set_visible_func(searchPropertiesTree, data=TreeSparse)

    # -----------------Creating the Features Tab-----------------

    FeatureTab = Gtk.Box(spacing=10)
    FeaturesGrid = createSubTab(FeatureTab, notebook, "Features")
    #   FeaturesGrid.set_row_spacing(3)

    featuresColumnView = Gtk.ColumnView()
    featuresColumnView.props.show_row_separators = True
    featuresColumnView.props.single_click_activate = False
    featuresColumnView.props.show_column_separators = False
    factoryFeaturesLhs = Gtk.SignalListItemFactory()
    factoryFeaturesLhs.connect("setup", setup)
    factoryFeaturesLhs.connect("bind", bind_column1)
    factoryFeaturesRhs = Gtk.SignalListItemFactory()
    factoryFeaturesRhs.connect("setup", setup)
    factoryFeaturesRhs.connect("bind", bind_column2)

    featureColumn1 = Gtk.ColumnViewColumn.new("Device Features")
    featureColumn1.set_factory(factoryFeaturesLhs)
    featureColumn1.set_resizable(True)
    featuresColumnView.append_column(featureColumn1)

    featureColumn2 = Gtk.ColumnViewColumn.new("Value")
    featureColumn2.set_factory(factoryFeaturesRhs)
    featureColumn2.set_expand(True)
    featuresColumnView.append_column(featureColumn2)


    featureSelection = Gtk.SingleSelection()
    FeatureTab_Store = Gio.ListStore.new(DataObject)
    filterSortFeatureListStore = Gtk.FilterListModel(model=FeatureTab_Store)
    filter_features = Gtk.CustomFilter.new(_do_filter_feature_view, filterSortFeatureListStore)
    filterSortFeatureListStore.set_filter(filter_features)
    featureSelection.set_model(filterSortFeatureListStore)
    featuresColumnView.set_model(featureSelection)
    

 #   featureList  = Gtk.StringList()
    featureDropdown = Gtk.DropDown()
 #   featureDropdown.set_model(featureList)
    featureDropdown.connect('notify::selected-item',selectFeature)
    featureSearchEntry = Gtk.SearchEntry()
    featureSearchEntry.set_property("placeholder_text","Type here to filter.....")
    featureSearchEntry.connect("search-changed",_on_search_method_changed,filter_features)
    FeaturesGrid.attach(featureSearchEntry,0,0,12,1)
    setMargin(featureDropdown,2,1,2)
    FeatureScrollbar = create_scrollbar(featuresColumnView)
    FeaturesGrid.attach_next_to(FeatureScrollbar, featureSearchEntry, Gtk.PositionType.BOTTOM, 15, 1)
    FeaturesGrid.attach_next_to(featureDropdown,featureSearchEntry,Gtk.PositionType.RIGHT,3,1)

#    FeaturesTab_Store_filter.set_visible_func(searchFeaturesTree, data=TreeFeatures)

    ExtensionTab = Gtk.Box(spacing=10)
    ExtensionGrid = createSubTab(ExtensionTab, notebook, "Extensions")
    ExtensionGrid.set_row_spacing(2)

    extensionColumnView = Gtk.ColumnView()
    extensionColumnView.props.show_row_separators = True
    extensionColumnView.props.single_click_activate = False
    extensionColumnView.props.show_column_separators = False
    factory = Gtk.SignalListItemFactory()
    factory.connect("setup", setup)
    factory.connect("bind", bind_column1)
    factory2 = Gtk.SignalListItemFactory()
    factory2.connect("setup", setup)
    factory2.connect("bind", bind_column2)
    scrollable_extension = create_scrollbar(extensionColumnView)
    ExtensionTab.append(ExtensionGrid)

    deviceExtensionColumn = Gtk.ColumnViewColumn.new("Device Extensions")
    deviceExtensionColumn.set_factory(factory)
    deviceExtensionColumn.set_resizable(True)
    extensionColumnView.append_column(deviceExtensionColumn)

    extensionRevisionColumn = Gtk.ColumnViewColumn.new("Extension Revision")
    extensionRevisionColumn.set_factory(factory2)
    extensionRevisionColumn.set_expand(True)
    extensionColumnView.append_column(extensionRevisionColumn)

    extensionSelection = Gtk.SingleSelection()
    ExtensionTab_Store = Gio.ListStore.new(DataObject)
    filterSortExtensionListStore = Gtk.FilterListModel(model=ExtensionTab_Store)
    filter_extensions = Gtk.CustomFilter.new(_do_filter_extension_view, filterSortExtensionListStore)
    filterSortExtensionListStore.set_filter(filter_extensions)
    extensionSelection.set_model(filterSortExtensionListStore)
    extensionColumnView.set_model(extensionSelection)


    extensionFrameSearch = Gtk.Frame()
    extensionSearchEntry = Gtk.SearchEntry()
    extensionFrameSearch.set_child(extensionSearchEntry)
    extensionSearchEntry.set_property("placeholder_text","Type here to filter.....")
    extensionSearchEntry.connect("search-changed", _on_search_method_changed,filter_extensions)
    ExtensionGrid.attach(extensionFrameSearch,0,0,1,1)
 #   ExtensionScrollbar = create_scrollbar(TreeExtension)
    ExtensionGrid.attach_next_to(scrollable_extension, extensionFrameSearch, Gtk.PositionType.BOTTOM, 1, 1)
  #  ExtensionTab_store_filter.set_visible_func(searchExtensionTree, data=TreeExtension)

    # ------------Creating the Formats Tab --------------------------------------------------

    FormatsList = Gtk.StringList()
    FormatsDropDown = Gtk.DropDown()
    FormatsDropDown.set_model(FormatsList)
    FormatsDropDown.connect('notify::selected-item',selectFormats)
    FormatsTab = Gtk.Box(spacing=10)
    FormatsGrid = createSubTab(FormatsTab, notebook, "Formats")
    FormatsGrid.set_row_spacing(3)


    formatsColumnView = Gtk.ColumnView()
    formatsColumnView.props.show_row_separators = True
    formatsColumnView.props.show_column_separators = False

    factory_formats = Gtk.SignalListItemFactory()
    factory_formats.connect("setup",setup_expander)
    factory_formats.connect("bind",bind_expander)

    factory_formats_value1 = Gtk.SignalListItemFactory()
    factory_formats_value1.connect("setup",setup)
    factory_formats_value1.connect("bind",bind1)


    factory_formats_value2 = Gtk.SignalListItemFactory()
    factory_formats_value2.connect("setup",setup)
    factory_formats_value2.connect("bind",bind2)


    factory_formats_value3 = Gtk.SignalListItemFactory()
    factory_formats_value3.connect("setup",setup)
    factory_formats_value3.connect("bind",bind3)

    formatsSelection = Gtk.SingleSelection()
    FormatsTab_Store = Gio.ListStore.new(ExpandDataObject2)
    filterSortFormatsStore = Gtk.FilterListModel(model=FormatsTab_Store)
    filter_formats = Gtk.CustomFilter.new(_do_filter_formats_view, filterSortFormatsStore)
    filterSortFormatsStore.set_filter(filter_formats)

    formatsModel = Gtk.TreeListModel.new(filterSortFormatsStore,False,False,add_tree_node2)
    formatsSelection.set_model(formatsModel)

    formatsColumnView.set_model(formatsSelection)

    formatColumnLhs = Gtk.ColumnViewColumn.new("Device Formats",factory_formats)
    formatColumnLhs.set_resizable(True)
    formatColumnRhs1 = Gtk.ColumnViewColumn.new("linearTiling",factory_formats_value1)
    formatColumnRhs1.set_expand(True)
    formatColumnRhs2 = Gtk.ColumnViewColumn.new("optimalTiling",factory_formats_value2)
    formatColumnRhs2.set_expand(True)
    formatColumnRhs3 = Gtk.ColumnViewColumn.new("bufferFeatures",factory_formats_value3)
    formatColumnRhs3.set_expand(True)

    formatsColumnView.append_column(formatColumnLhs)
    formatsColumnView.append_column(formatColumnRhs1)
    formatsColumnView.append_column(formatColumnRhs2)
    formatsColumnView.append_column(formatColumnRhs3)

#    FormatsTab_Store = Gtk.TreeStore(str,str,str,str,str,str,str,str)
#    FormatsTab_Store_filter = FormatsTab_Store.filter_new()
#    TreeFormats = Gtk.TreeView.new_with_model(FormatsTab_Store_filter)
 #   TreeFormats.set_property("enable-grid-lines", 1)
 #   TreeFormats.set_property("enable-tree-lines", True)
 #   TreeFormats.set_enable_search(True)
 #   TreeFormats.set_enable_search(True)
  #  for i, column_title in enumerate(FormatsTitle):
  #      Formatsrenderer = Gtk.CellRendererText()
   #     column = Gtk.TreeViewColumn(column_title, Formatsrenderer, text=i)
    #    column.add_attribute(Formatsrenderer, "background", 4)
    #    column.set_resizable(True)
    #    column.set_reorderable(True)
    #    column.set_property("min-width", MWIDTH)
    #    if i == 0:
    #        column.set_property("min-width", 400)
    #    if i > 0 :
    #        column.set_property("min-width", 200)
    #    if i > 0 and i < 4:
    #        column.add_attribute(Formatsrenderer,"foreground",i+4)

     #   TreeFormats.append_column(column)

    formatSearchFrame = Gtk.Frame()
    formatSearchEntry = Gtk.SearchEntry()
    formatSearchFrame.set_child(formatSearchEntry)
    formatSearchEntry.set_property("placeholder_text","Type here to filter.....")
    formatSearchEntry.connect("search-changed", _on_search_method_changed,filter_formats)
    FormatsGrid.attach(formatSearchFrame,0,0,12,1)
    FormatsScrollbar = create_scrollbar(formatsColumnView)
    FormatsGrid.attach_next_to(FormatsScrollbar, formatSearchFrame, Gtk.PositionType.BOTTOM, 15, 1)
 #   FormatsGrid.attach_next_to(FormatsCombo,formatSearchFrame,Gtk.PositionType.RIGHT,1,1)
    FormatsGrid.attach_next_to(FormatsDropDown,formatSearchFrame,Gtk.PositionType.RIGHT,3,1)


#    FormatsTab_Store_filter.set_visible_func(searchFormatsTree, data=TreeFormats)

        # ------------------------Memory Types & Heaps----------------------------------------------

    MemoryTab = Gtk.Box(spacing=10)
    MemoryTypeTab = Gtk.Box(spacing=10)
    MemoryTypeGrid = createSubTab(MemoryTypeTab, notebook, "Memory Types")
    MemoryTypeGrid.set_row_spacing(3)

    memoryTypesColumnView = Gtk.ColumnView()
    memoryTypesColumnView.props.show_row_separators = True
    memoryTypesColumnView.props.show_column_separators = False

    factory_memory_types = Gtk.SignalListItemFactory()
    factory_memory_types.connect("setup",setup_expander)
    factory_memory_types.connect("bind",bind_expander)

    factory_memory_types_value = Gtk.SignalListItemFactory()
    factory_memory_types_value.connect("setup",setup)
    factory_memory_types_value.connect("bind",bind1)

    memoryTypesSelection = Gtk.SingleSelection()
    MemoryTab_Store = Gio.ListStore.new(ExpandDataObject)

    memoryTypesModel = Gtk.TreeListModel.new(MemoryTab_Store,False,True,add_tree_node)
    memoryTypesSelection.set_model(memoryTypesModel)

    memoryTypesColumnView.set_model(memoryTypesSelection)

    memoryTypesColumnLhs = Gtk.ColumnViewColumn.new("Memory Types",factory_memory_types)
    memoryTypesColumnLhs.set_resizable(True)
    memoryTypesColumnRhs = Gtk.ColumnViewColumn.new("Value",factory_memory_types_value)
    memoryTypesColumnRhs.set_expand(True)

    memoryTypesColumnView.append_column(memoryTypesColumnLhs)
    memoryTypesColumnView.append_column(memoryTypesColumnRhs)

    MemoryScrollbar = create_scrollbar(memoryTypesColumnView)
    MemoryTypeGrid.attach(MemoryScrollbar,0,0,1,1)
# -----------------------------------------------------------------------------------------------------------------------------------
    MemoryHeapTab = Gtk.Box(spacing=10)
    MemoryHeapGrid = createSubTab(MemoryHeapTab, notebook, "Memory Heap")
    MemoryHeapGrid.set_row_spacing(3)
    #HeapGrid = Gtk.Box(spacing=10)

    heapsColumnView = Gtk.ColumnView()
    heapsColumnView.props.show_row_separators = True
    heapsColumnView.props.show_column_separators = False

    factory_heaps = Gtk.SignalListItemFactory()
    factory_heaps.connect("setup",setup_expander)
    factory_heaps.connect("bind",bind_expander)

    factory_heaps_value = Gtk.SignalListItemFactory()
    factory_heaps_value.connect("setup",setup)
    factory_heaps_value.connect("bind",bind1)

    heapSelection = Gtk.SingleSelection()
    HeapTab_Store = Gio.ListStore.new(ExpandDataObject)

    heapModel = Gtk.TreeListModel.new(HeapTab_Store,False,True,add_tree_node)
    heapSelection.set_model(heapModel)

    heapsColumnView.set_model(heapSelection)

    heapColumnLhs = Gtk.ColumnViewColumn.new("Memory Heaps",factory_heaps)
    heapColumnLhs.set_resizable(True)
    heapColumnRhs = Gtk.ColumnViewColumn.new("Value",factory_heaps_value)
    heapColumnRhs.set_expand(True)

    heapsColumnView.append_column(heapColumnLhs)
    heapsColumnView.append_column(heapColumnRhs)

    HeapScrollbar = create_scrollbar(heapsColumnView)
    MemoryHeapGrid.attach(HeapScrollbar,0,0,1,1)

    # -------------------------Creating the Queues Tab -----------------------------------------------------

    QueueTab = Gtk.Box(spacing=10)
    QueueGrid = createSubTab(QueueTab, notebook, "Queue")

    queuesColumnView = Gtk.ColumnView()
    queuesColumnView.props.show_row_separators = True
    queuesColumnView.props.show_column_separators = False

    factory_queues = Gtk.SignalListItemFactory()
    factory_queues.connect("setup",setup_expander)
    factory_queues.connect("bind",bind_expander)

    factory_queues_value = Gtk.SignalListItemFactory()
    factory_queues_value.connect("setup",setup)
    factory_queues_value.connect("bind",bind1)

    queueSelection = Gtk.SingleSelection()
    QueueTab_Store = Gio.ListStore.new(ExpandDataObject)

    queueModel = Gtk.TreeListModel.new(QueueTab_Store,False,True,add_tree_node)
    queueSelection.set_model(queueModel)

    queuesColumnView.set_model(queueSelection)

    queueColumnLhs = Gtk.ColumnViewColumn.new("Memory Heaps",factory_queues)
    queueColumnLhs.set_resizable(True)
    queueColumnRhs = Gtk.ColumnViewColumn.new("Value",factory_queues_value)
    queueColumnRhs.set_expand(True)

    queuesColumnView.append_column(queueColumnLhs)
    queuesColumnView.append_column(queueColumnRhs)


 #   QueueTab_Store = Gtk.TreeStore(str, str, str, str)
 #   TreeQueue = Gtk.TreeView.new_with_model(QueueTab_Store)
 #   TreeQueue.set_property("enable-grid-lines", 1)
 #   TreeQueue.set_enable_search(True)
 #   TreeQueue.set_property("enable-tree-lines", True)
 #   for i, column_title in enumerate(QueueTitle):
  #      Queuerenderer = Gtk.CellRendererText()
#        Queuerenderer.set_alignment(0.5, 0.5)
  #      column = Gtk.TreeViewColumn(column_title, Queuerenderer, text=i)
#        column.set_alignment(0.5)
  #      column.add_attribute(Queuerenderer, "background", 2)
   #     column.set_resizable(True)
   #     column.set_reorderable(True)
   #     if i > 0:
   #         column.add_attribute(Queuerenderer, "foreground", 3)
   #     TreeQueue.set_property("can-focus", False)
   #     TreeQueue.append_column(column)

    QueueScrollbar = create_scrollbar(queuesColumnView)
    QueueGrid.attach(QueueScrollbar,0,0,1,1)

    # -------------------------Creating the Instances & Layers ---------------------------------------------

#    InstanceTab = Gtk.Box(spacing=10)
#    InstanceGrid = createSubTab(InstanceTab, notebook, "Instances & layers")
#    InstanceNotebook = Gtk.Notebook()
#    InstanceGrid.attach(InstanceNotebook,0,0,1,1)
    InstanceExtTab = Gtk.Box(spacing=10)
    InstanceExtGrid = createSubTab(InstanceExtTab, notebook, "Instance Extensions")
    InstanceExtGrid.set_row_spacing(3)


    instanceExtensionColumnView = Gtk.ColumnView()
    instanceExtensionColumnView.props.show_row_separators = True
    instanceExtensionColumnView.props.single_click_activate = False
    instanceExtensionColumnView.props.show_column_separators = False
    factory = Gtk.SignalListItemFactory()
    factory.connect("setup", setup)
    factory.connect("bind", bind_column1)
    factory2 = Gtk.SignalListItemFactory()
    factory2.connect("setup", setup)
    factory2.connect("bind", bind_column2)
 #   scrollable_instanceExtension = create_scrollbar(instanceExtensionColumnView)
#    ExtensionTab.append(ExtensionGrid)

    instanceExtensionColumn = Gtk.ColumnViewColumn.new("Instance Extensions")
    instanceExtensionColumn.set_factory(factory)
    instanceExtensionColumn.set_resizable(True)
    instanceExtensionColumnView.append_column(instanceExtensionColumn)

    instanceExtensionRevisionColumn = Gtk.ColumnViewColumn.new("Extension Revision")
    instanceExtensionRevisionColumn.set_factory(factory2)
    instanceExtensionRevisionColumn.set_expand(True)
    instanceExtensionColumnView.append_column(instanceExtensionRevisionColumn)

    instanceExtensionSelection = Gtk.SingleSelection()
    InstanceTab_Store = Gio.ListStore.new(DataObject)
    filterSortInstancesListStore = Gtk.FilterListModel(model=InstanceTab_Store)
    filter_instances = Gtk.CustomFilter.new(_do_filter_instances_view, filterSortInstancesListStore)
    filterSortInstancesListStore.set_filter(filter_instances)
    instanceExtensionSelection.set_model(filterSortInstancesListStore)
    instanceExtensionColumnView.set_model(instanceExtensionSelection)

 #   InstanceTab_Store = Gtk.ListStore(str, str, str)
#    InstanceTab_Store_filter = InstanceTab_Store.filter_new()
#    TreeInstance = Gtk.TreeView.new_with_model(InstanceTab_Store_filter)
 #   TreeInstance.set_property("enable-grid-lines", 1)
#    TreeInstance.set_enable_search(True)

#    setColumns(TreeInstance, InstanceTitle, 300, 0.0)

    instanceSearchFrame = Gtk.Frame()
    instanceSearchEntry = Gtk.SearchEntry()
    instanceSearchEntry.set_property("placeholder_text","Type here to filter.....")
    instanceSearchEntry.connect("search-changed",_on_search_method_changed,filter_instances)
 #   instanceSearchEntry = createSearchEntry(InstanceTab_Store_filter)
    instanceSearchFrame.set_child(instanceSearchEntry)
    InstanceExtGrid.attach(instanceSearchFrame,0,0,1,1)
    InstanceScrollbar = create_scrollbar(instanceExtensionColumnView)
    InstanceExtGrid.attach_next_to(InstanceScrollbar, instanceSearchFrame, Gtk.PositionType.BOTTOM, 1, 1)

#    InstanceTab_Store_filter.set_visible_func(searchInstanceExtTree, data=TreeInstance)

    InstanceLayersTab = Gtk.Box(spacing=10)
    InstanceLayersGrid = createSubTab(InstanceLayersTab, notebook, "Instance Layers")
    InstanceLayersGrid.set_row_spacing(3)


    layersColumnView = Gtk.ColumnView()
    layersColumnView.props.show_row_separators = True
    layersColumnView.props.show_column_separators = False

    factory_layers = Gtk.SignalListItemFactory()
    factory_layers.connect("setup",setup_expander)
    factory_layers.connect("bind",bind_expander)

    factory_layers_value1 = Gtk.SignalListItemFactory()
    factory_layers_value1.connect("setup",setup)
    factory_layers_value1.connect("bind",bind1)


    factory_layers_value2 = Gtk.SignalListItemFactory()
    factory_layers_value2.connect("setup",setup)
    factory_layers_value2.connect("bind",bind2)


    factory_layers_value3 = Gtk.SignalListItemFactory()
    factory_layers_value3.connect("setup",setup)
    factory_layers_value3.connect("bind",bind3)


    factory_layers_value4 = Gtk.SignalListItemFactory()
    factory_layers_value4.connect("setup",setup)
    factory_layers_value4.connect("bind",bind4)

    layerSelection = Gtk.SingleSelection()
    LayerTab_Store = Gio.ListStore.new(ExpandDataObject2)
    filterSortLayersStore = Gtk.FilterListModel(model=LayerTab_Store)
    filter_layers = Gtk.CustomFilter.new(_do_filter_layers_view, filterSortLayersStore)
    filterSortLayersStore.set_filter(filter_layers)

    layersModel = Gtk.TreeListModel.new(filterSortLayersStore,False,False,add_tree_node2)
    layerSelection.set_model(layersModel)

    layersColumnView.set_model(layerSelection)

    layerColumnLhs = Gtk.ColumnViewColumn.new("Device Limits",factory_layers)
    layerColumnLhs.set_resizable(True)
    layerColumnRhs1 = Gtk.ColumnViewColumn.new("Value",factory_layers_value1)
    layerColumnRhs1.set_expand(True)
    layerColumnRhs2 = Gtk.ColumnViewColumn.new("Value",factory_layers_value2)
    layerColumnRhs2.set_expand(True)
    layerColumnRhs3 = Gtk.ColumnViewColumn.new("Value",factory_layers_value3)
    layerColumnRhs3.set_expand(True)
    layerColumnRhs4 = Gtk.ColumnViewColumn.new("Value",factory_layers_value4)
    layerColumnRhs4.set_expand(True)

    layersColumnView.append_column(layerColumnLhs)
    layersColumnView.append_column(layerColumnRhs1)
    layersColumnView.append_column(layerColumnRhs2)
    layersColumnView.append_column(layerColumnRhs3)
    layersColumnView.append_column(layerColumnRhs4)


#    LayerTab_Store = Gtk.TreeStore(str, str, str, str, str, str)
#    LayerTab_Store_filter = LayerTab_Store.filter_new()
#    TreeLayer = Gtk.TreeView.new_with_model(LayerTab_Store_filter)
#    TreeLayer.set_property("enable-grid-lines", 1)
 #   TreeLayer.set_enable_search(TreeLayer)
 #   TreeLayer.set_property("enable-tree-lines",True)

 #   setColumns(TreeLayer, LayerTitle, 100, 0.0)

    layerSearchFrame = Gtk.Frame()
    layerSearchEntry = Gtk.SearchEntry()
    layerSearchEntry.set_property("placeholder_text","Type here to filter.....")
    layerSearchEntry.connect("search-changed",_on_search_method_changed,filter_layers)
    layerSearchFrame.set_child(layerSearchEntry)
    InstanceLayersGrid.attach(layerSearchFrame,0,0,1,1)
    LayerScrollbar = create_scrollbar(layersColumnView)
    InstanceLayersGrid.attach_next_to(LayerScrollbar, layerSearchFrame, Gtk.PositionType.BOTTOM, 1, 1)

#    LayerTab_Store_filter.set_visible_func(searchInstanceLayersTree, data=TreeLayer)

    # ------------------ Creating the Surface Tab --------------------------------------------------

    SurfaceTab = Gtk.Box(spacing=10)
    SurfaceGrid = createSubTab(SurfaceTab, notebook, "Surface")

    surfaceColumnView = Gtk.ColumnView()
    surfaceColumnView.props.show_row_separators = True
    surfaceColumnView.props.show_column_separators = False

    factory_surface = Gtk.SignalListItemFactory()
    factory_surface.connect("setup",setup_expander)
    factory_surface.connect("bind",bind_expander)

    factory_surface_value = Gtk.SignalListItemFactory()
    factory_surface_value.connect("setup",setup)
    factory_surface_value.connect("bind",bind1)

    surfaceSelection = Gtk.SingleSelection()
    SurfaceTab_Store = Gio.ListStore.new(ExpandDataObject)

    surfaceModel = Gtk.TreeListModel.new(SurfaceTab_Store,False,True,add_tree_node)
    surfaceSelection.set_model(surfaceModel)

    surfaceColumnView.set_model(surfaceSelection)

    surfaceColumnLhs = Gtk.ColumnViewColumn.new("Surface Details",factory_surface)
    surfaceColumnLhs.set_resizable(True)
    surfaceColumnRhs = Gtk.ColumnViewColumn.new("Value",factory_surface_value)
    surfaceColumnRhs.set_expand(True)

    surfaceColumnView.append_column(surfaceColumnLhs)
    surfaceColumnView.append_column(surfaceColumnRhs)

    #SurfaceCombo = Gtk.ComboBoxText()
    #SurfaceCombo.connect("changed", selectSurfaceType)
    #SurfaceGrid.add(SurfaceCombo)
 #   SurfaceTab_Store = Gtk.TreeStore(str, str, str)
 #   TreeSurface = Gtk.TreeView.new_with_model(SurfaceTab_Store)
 #   TreeSurface.set_property("enable-grid-lines", 1)
 #   TreeSurface.set_property("enable-tree-lines", True)
#    with open(Filenames.vulkaninfo_output_file, "r") as file1:
 #       for line in file1:
  #          if "VkSurfaceCapabilities" in line:
   #             for i, column_title in enumerate(SurfaceTitle):
    #                Surfacerenderer = Gtk.CellRendererText()
     #               column = Gtk.TreeViewColumn(column_title, Surfacerenderer, text=i)
      #              column.add_attribute(Surfacerenderer, "background", 2)
       #             column.set_property("min-width",const.MWIDTH)
        #            TreeSurface.set_property("can-focus", False)
         #           TreeSurface.append_column(column)

    SurfaceScrollbar = create_scrollbar(surfaceColumnView)
    SurfaceGrid.attach(SurfaceScrollbar,0,0,1,1)
           #     break
    
    # ------------------------- Creating the Device Groups Tab ---------------------------------------

  #  GroupsTab = Gtk.Box(spacing=10)
  #  GroupsGrid = createSubTab(GroupsTab,notebook,"Groups")
  #  Groups_Store = Gtk.TreeStore(str,str,str)
  #  TreeGroups = Gtk.TreeView.new_with_model(Groups_Store)
  #  TreeGroups.set_property("enable-grid-lines", 1)
  #  TreeGroups.set_property("enable-tree-lines",True)
  #  setColumns(TreeGroups,GroupsTitle,const.MWIDTH,0.0)
  #  GroupsScrollbar = create_scrollbar(TreeGroups)
  #  GroupsGrid.attach(GroupsScrollbar,0,0,1,1)

    #--------------------------------------------------------- Fetching the device list ---------------------------------------------------------------------------------------------

    DevicesGrid = Gtk.Grid()
    DevicesGrid.set_row_spacing(10)
    DeviceGrid.set_column_spacing(20)
    DevicesFrame.set_child(DevicesGrid)

    gpu_list = fetchContentsFromCommand(Filenames.fetch_vulkaninfo_ouput_command+Filenames.fetch_device_name_command)

    availableDevices = Gtk.Label()
    setMargin(availableDevices,280,10,10)
    gpu_image = Gtk.Image()
    availableDevices.set_text("Available Device(s) :")
    DevicesGrid.attach(availableDevices, 10, 2, 20, 1)
    gpu_image = GdkPixbuf.Pixbuf.new_from_file_at_size(const.APP_LOGO_PNG, 100, 100)
    image_renderer = Gtk.Picture.new_for_pixbuf(gpu_image)
    gpu_DropDown = Gtk.DropDown()
    gpu_DropDown_list = Gtk.StringList()
    gpu_DropDown.set_model(gpu_DropDown_list)
    gpu_DropDown.connect('notify::selected-item',radcall)
    for i in gpu_list:
        gpu_DropDown_list.append(i)

    setMargin(gpu_DropDown,30,10,10)
    setMargin(image_renderer,30,10,10)
    DevicesGrid.attach_next_to(gpu_DropDown,availableDevices,Gtk.PositionType.RIGHT,30,1)
    DevicesGrid.attach_next_to(image_renderer,gpu_DropDown,Gtk.PositionType.RIGHT,30,1)
#    DeviceGrid.attach_next_to(spinner,image_renderer,Gtk.PositionType.RIGHT,80,1)

