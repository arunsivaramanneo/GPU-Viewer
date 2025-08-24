import sys
import gi
gi.require_version('Gtk','4.0')
gi.require_version(namespace='Adw', version='1')

from gi.repository import Gtk,GdkPixbuf,GObject,Gio,Adw,GLib
from Common import ExpandDataObject, setup_expander,bind_expander,setup,bind1,add_tree_node, ExpandDataObject2,add_tree_node2,bind2,bind3,bind4


Adw.init()

import const
import Filenames
import subprocess
from Common import copyContentsFromFile, getGpuImage,create_scrollbar, getRamInGb,createSubTab,getDriverVersion,getDeviceSize, setMargin,fetchContentsFromCommand,getVulkanVersion,createMainFile,getLogo

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil library not found. Real-time CPU/RAM stats will not be displayed.")


class DataObject(GObject.GObject):
    def __init__(self, column1: str,column2: str):
        super(DataObject, self).__init__()
        self.column1 = column1
        self.column2 = column2

class ExpandDataObject3(GObject.GObject):
    def __init__(self, txt: str, image: GdkPixbuf.Pixbuf, txt2: str):
        super(ExpandDataObject3, self).__init__()
        self.data = txt
        self.data2 = image
        self.data3 = txt2
        self.children = []

def add_tree_node3(item):
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
        store = Gio.ListStore.new(ExpandDataObject3)
        for child in item.children:
            store.append(child)
        return store

def setup_image(widget, item):
    """Setup the widget to show in the Gtk.Listview"""
    image_render = Gtk.Picture()
    item.set_child(image_render)

def bind_image(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    row = item.get_item()
    obj = row.get_item()
 #   image_render = Gtk.Image()
#    image_renderer = Gtk.Picture.new_for_pixbuf(image)
#    row = item.get_item()
#    obj = row.get_item()
    label.set_pixbuf(obj.data2)
 
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
    if "true" in obj.column2:
        label.remove_css_class(css_class='false')
        label.add_css_class(css_class='true')
        label.set_label(obj.column2)
    elif "false" in obj.column2:
        label.remove_css_class(css_class='true')
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

        fetch_vulkan_gpu_info_command = r"vulkaninfo --summary | awk '/GPU%d/{flag=1;next}/^GPU.*/{flag=0}flag' | awk '{gsub(/\([0-9].*/,'True');}1' | sort " %(GPUname)
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

        DeviceTab_Store.remove_all()
    #    TreeDevice.set_model(DeviceTab_Store)

        dummy_transparent = GdkPixbuf.Pixbuf.new_from_file_at_size(const.TRANSPARENT_PIXBUF, 24, 20)
        toprow = ExpandDataObject3("Vulkan Details...",dummy_transparent," ")
        for i in range(len(valueRHS)):
            if "apiVersion" in valueLHS[i]:
                if '.' not in valueRHS[i]:
                    valueRHS[i] = getVulkanVersion(valueRHS[i])
            if "driverVersion" in valueLHS[i]:
                if '.' not in valueRHS[i]:
                    valueRHS[i] = getDriverVersion(valueRHS,i)
            if "deviceName" in valueLHS[i]:
                gpu_logo = getLogo(valueRHS[i])
                iter1 = ExpandDataObject3(valueLHS[i].strip('\n'),gpu_logo, valueRHS[i].strip('\n'))
                toprow.children.append(iter1)
                continue
            if "driverName" in valueLHS[i]:
                driver_logo = getLogo(valueRHS[i])
                iter1 = ExpandDataObject3(valueLHS[i].strip('\n'),driver_logo, valueRHS[i].strip('\n'))
                toprow.children.append(iter1)
                continue
            if "Model" in valueLHS[i]:
                cpu_logo = getLogo(valueRHS[i])
                DeviceTab_Store.append(toprow) 
                toprow = ExpandDataObject3("Processor Details...",dummy_transparent,"")
                iter1 = ExpandDataObject3(valueLHS[i].strip('\n'),cpu_logo, valueRHS[i].strip('\n'))
                toprow.children.append(iter1)
                continue
            if "Description" in valueLHS[i]:
                distro_logo = getLogo(valueRHS[i])
                DeviceTab_Store.append(toprow) 
                toprow = ExpandDataObject3("Operating System Details...",dummy_transparent,"")
                iter1 = ExpandDataObject3(valueLHS[i].strip('\n'),distro_logo, valueRHS[i].strip('\n'))
                toprow.children.append(iter1)
                continue
            if "Desktop" in valueLHS[i]:
                desktop_logo = getLogo(valueRHS[i])
                iter1 = ExpandDataObject3(valueLHS[i].strip('\n'),desktop_logo, valueRHS[i].strip('\n'))
                toprow.children.append(iter1)
                continue
            if "Windowing" in valueLHS[i]:
                windowing_system_logo = getLogo(valueRHS[i])
                iter1 = ExpandDataObject3(valueLHS[i].strip('\n'),windowing_system_logo, valueRHS[i].strip('\n'))
                toprow.children.append(iter1)
                continue
            if "MemTotal" in valueLHS[i]:
                DeviceTab_Store.append(toprow) 
                toprow = ExpandDataObject3("Memory Details...",dummy_transparent," ")
                iter1 = ExpandDataObject3(valueLHS[i].strip('\n'),dummy_transparent, getRamInGb(valueRHS[i]))
                toprow.children.append(iter1)
            elif "Mem" in valueLHS[i] or "Swap" in valueLHS[i] :
                iter1 = ExpandDataObject3(valueLHS[i].strip('\n'),dummy_transparent, getRamInGb(valueRHS[i]))
                toprow.children.append(iter1)
            else:
                iter1 = ExpandDataObject3(valueLHS[i].strip('\n'),dummy_transparent, valueRHS[i].strip('\n'))
                toprow.children.append(iter1)
        DeviceTab_Store.append(toprow)

        fetch_device_properties_command = "cat %s | awk '/GPU%d/{flag=1;next}/Device Extensions.*/{flag=0}flag' | awk '/VkPhysicalDeviceSparseProperties:/{flag=1}/Device Extensions.*/{flag=0}flag' | awk '/./' " %(Filenames.vulkaninfo_output_file,GPUname)
    #    os.system("cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Extensions.*/{flag=0}flag' | awk '/VkPhysicalDeviceSparseProperties:/{flag=1}/Device Extensions.*/{flag=0}flag' | awk '/./' > /tmp/gpu-viewer/VKDDevicesparseinfo1.txt" % GPUname)
        createMainFile(Filenames.vulkan_device_properties_file,fetch_device_properties_command)
        
    #    propertiesList = Gtk.StringList()
    #    propertiesDropdown.set_model(propertiesList)
    #    propertiesList.remove_all()
    #    propertiesList.append(DataObject("Show All Device Properties",""))
    #    with open(Filenames.vulkan_device_properties_file, "r") as file1:
    #        for i, line in enumerate(file1):
    #            if "Vk" in line:
    #                text1 = ((line.strip("\t")).replace("VkPhysicalDevice",'')).replace(":","")
    #                text = text1[:-1]
    #                propertiesList.append(DataObject(text.strip("\n"),""))


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
        featureList.remove_all()
        featureList.append(DataObject("Show All Device Features",""))
        with open(Filenames.vulkan_device_features_file, "r") as file:
            for line in file:
                if "Vk" in line:
                    text = line[:-2]
                    featureList.append(DataObject(((text.strip("\n")).replace("VkPhysicalDevice","").replace(":","")),""))

    def selectFeature(dropdown, _pspec):
        selected =dropdown.props.selected_item
        feature = ""
        if selected is not None:
            feature = selected.column1

        fetch_device_features_all_command = "cat %s | awk '/==/{flag=1;next} flag' | awk '{sub(/^[ \t]+/, 'True'); print }' | grep =" %(Filenames.vulkan_device_features_file)
        fetch_device_features_selected_command = "cat %s | awk '/%s/{flag=1;next}/^Vk*/{flag=0}flag' | awk '/--/{flag=1 ; next} flag' | grep = | sort " %(Filenames.vulkan_device_features_file,feature)
        fetch_device_features_selected_lhs_command = "cat %s | awk '{sub(/^[ \t]+/, 'True'); print }' | awk '{gsub(/= true/,'True');print}' | awk '{gsub(/= false/,'False');print}' | awk '{sub(/[ \t]+$/, 'True'); print }' | awk '/./' | sort | uniq" %(Filenames.vulkan_device_features_select_file)

        if feature is None:
            feature =' '
        elif "Show All Device Features" in feature:
            createMainFile(Filenames.vulkan_device_features_select_file,fetch_device_features_all_command)
            featureColumn1.set_title("Device Features")
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

        FormatsList.remove_all()
        FormatsList.append(DataObject("Show All Device Formats",""))
        with open(Filenames.vulkan_device_formats_types_file,"r") as file:
            for line in file:
                FormatsList.append(DataObject(((line.replace("FORMAT_","")).strip("\n")).strip("\t"),""))

    def selectFormats(dropdown,_pspec):
        selected =dropdown.props.selected_item
        selected_Format = ""
        if selected is not None:
            selected_Format = selected.column1

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
                        else:
                            linearStatus = "false"
                        if 'None' not in valueOptimalCount[i]:
                            optimalStatus = "true"
                        else:
                            optimalStatus = "false"
                        if 'None' not in valueBufferCount[i]:
                            bufferStatus = "true"
                        else:
                            bufferStatus = "false"
                        if groupName == None:
                            toprow = ExpandDataObject2(((valueFormats[n].strip('\n')).strip('\t')).replace('FORMAT_',""),linearStatus,optimalStatus,bufferStatus,"")
                        else:
                        #    FormatsTab_Store.append(toprow)
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
                else:
                    linearStatus = "false"
                if 'None' not in valueOptimalCount[value]:
                    optimalStatus = "true"
                else:
                    optimalStatus = "false"
                if 'None' not in valueBufferCount[value]:
                    bufferStatus = "true"
                else:
                    bufferStatus = "false"

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
        groupName = None
        for i in range(len(vulkan_memory_types_lhs)):
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
        fetch_vulkan_device_memory_heaps_rhs_command = r"cat %s | grep = | grep -v count| grep -o  =.* | grep -o ' .*' | awk '{gsub(/\(.*/,'True');print}' " %(Filenames.vulkan_device_memory_heaps_file)

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
    
        groupName = None
        for i in range(len(vulkan_device_queues_lhs)):
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
                        for flags in supportedFlags:
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
            InstanceTab_Store.append(DataObject(vulkan_device_instance_lhs[i].strip('\t'),vulkan_device_instance_rhs[i]))

        label = "Instance Extensions (%d)" %len(vulkan_device_instance_lhs)
#        InstanceNotebook.set_tab_label(InstanceExtTab, Gtk.Label(label=label))


        #-------------------------------------------------------------Layers Commands -----------------------------------------------------------------------------------------------------------------------------------
        fetch_vulkan_device_layers_command = "cat %s  | awk '/Layers:.*/{flag=1;next}/Presentable Surfaces.*/{flag=0}flag' | awk '/./' " %(Filenames.vulkaninfo_output_file)
        fetch_vulkan_device_layer_names_command = r"cat %s | grep _LAYER_ | awk '{gsub(/\(.*/,'True');print} '" %(Filenames.vulkan_device_layers_file)
        fetch_vulkan_device_layer_vulkan_version_command = "cat %s | grep ^VK | grep -o 'Vulkan.*' | awk '{gsub(/,.*/,'True');print}' | grep -o 'version.*' | grep -o ' .*' " %(Filenames.vulkan_device_layers_file)
        fetch_vulkan_device_layer_version_command = "cat %s | grep ^VK | grep -o 'layer version.*' | awk '{gsub(/:.*/,'True');print}' | grep -o version.* | grep -o ' .*' "  %(Filenames.vulkan_device_layers_file)
        fetch_vulkan_device_layer_description_command = r"cat %s | grep _LAYER_ | grep -o \(.* | awk '{gsub(/\).*/,'True');print}'| awk '{gsub(/\(/,'True');print}' " %(Filenames.vulkan_device_layers_file)
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
        i = 0
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
            property = selected.column1


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
            k = 0
            groupName = None
            with open(Filenames.vulkan_device_filter_properties_lhs_file, "r") as file1:
                for i, line in enumerate(file1):
                    text = line.strip('\t')
                    if "---" in line or "====" in line:
                        continue
                    if not (groupName == text):
                        if "Vk" in line and "conformanceVersion" not in line:
                            text1 = (text.replace("VkPhysicalDevice",'').replace(":",""))
                            if groupName == None:
                                toprow = ExpandDataObject((text1.strip('\n')).replace(" count",''), value2[i].strip('\n'))
                            #iter1 = SparseTab_Store.append(None, [(text1.strip('\n')).replace(" count",''), value2[i].strip('\n'), background_color, fgColor[i]])
                            else:
                                PropertiesTab_Store.append(toprow)
                                toprow = ExpandDataObject((text1.strip('\n')).replace(" count",''), value2[i].strip('\n'))
                            groupName = text
                        else:
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
                PropertiesTab_Store.append(toprow)
            #        TreeSparse.expand_all()
        else:
   #         iter = SparseTab_Store.append(None,[property,"",setBackgroundColor(1),const.COLOR3])
            toprow = ExpandDataObject(property,"")
            with open(Filenames.vulkan_device_filter_properties_lhs_file, "r") as file1:
                for i, line in enumerate(file1):
                    text = line.strip('\t')
                    if "---" in line or "====" in line:
                        continue
                    else:
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

    def _get_search_entry_widget(dropdown):
        popover = dropdown.get_last_child()
        box = popover.get_child()
        box2 = box.get_first_child()
        search_entry = box2.get_first_child() # Gtk.SearchEntry
        return search_entry
    
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
        return search_text_widget.upper() in item.data.upper() or search_text_widget.upper() in item.data2.upper() or search_text_widget.upper() in item.data3.upper() or search_text_widget.upper() in item.data4.upper() or search_text_widget.upper() in item.data5.upper()


    def _do_filter_formats_view(item, filter_list_model):
        search_text_widget = formatSearchEntry.get_text()
        if search_text_widget.upper() in item.data.upper():
            return item.data.upper()

    def _do_filter_properties_dropdown_view(item, filter_list_model):
        search_text_widget = properties_dropdown_search.get_text()
        return search_text_widget.upper() in item.column1.upper()

    def _do_filter_features_dropdown_view(item, filter_list_model):
        search_text_widget = features_dropdown_search.get_text()
        return search_text_widget.upper() in item.column1.upper()

    def _do_filter_formats_dropdown_view(item, filter_list_model):
        search_text_widget = formats_dropdown_search.get_text()
        return search_text_widget.upper() in item.column1.upper()

    def update_system_stats():
        """
        Updates the CPU, and RAM usage labels.
        This function is called periodically by a GLib timeout.
        """
        if PSUTIL_AVAILABLE and cpu_label and ram_label:
            # CPU and RAM usage as a percentage
            cpu_percent = psutil.cpu_percent(interval=None) # Non-blocking call
            ram_percent = psutil.virtual_memory().percent
            cpu_label.set_label(f"CPU: {cpu_percent}%")
            ram_label.set_label(f"RAM: {ram_percent}%")
            
        return True # Return True to keep the timeout running

    def radcall(combo,dummy):
        text = combo.props.selected
        Devices(text)
    #    Limits(text)
    #    Features(text)
    #    Extensions(text)
    #    Formats(text)
    #    MemoryTypes(text)
    #    Queues(text)
    #    Surface(text)
       #         Groups(text)
        gpu_image = getGpuImage(gpu_list[text])
        image_renderer.set_pixbuf(gpu_image)
    #    Instance()


    grid = Gtk.Grid()
    grid.set_row_spacing(10)
    DevicesFrame = Gtk.Frame()
    grid.attach(DevicesFrame,0,1,1,1)


    sidebar_store = Gtk.StringList.new([
        "System Info", "Limits", "Properties", "Features", "Extensions", "Formats", "Memory Types", 
        "Memory Heaps", "Queues", "Instance Extensions", "Instance Layers", "Surface"
    ])

    selection_model = Gtk.SingleSelection.new(sidebar_store)
    selection_model.set_can_unselect(False)
    
    factory = Gtk.SignalListItemFactory.new()
    def on_setup(factory, list_item):
        label = Gtk.Label(xalign=0, hexpand=True)
        label.set_margin_top(10)
        label.set_margin_bottom(10)
        # Add padding to the start and end of the labels
        label.set_margin_start(10)
        label.set_margin_end(10)
        list_item.set_child(label)

    def on_bind(factory, list_item):
        label = list_item.get_child()
        label.set_label(list_item.get_item().get_string())

    # Corrected the function names in the connect calls
    factory.connect("setup", on_setup)
    factory.connect("bind", on_bind)
    
    list_view = Gtk.ListView(model=selection_model, factory=factory)

    # Wrap the list view in a scrolled window to enable scrolling
    scrolled_sidebar = Gtk.ScrolledWindow()
    scrolled_sidebar.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scrolled_sidebar.set_child(list_view)
    
    vulkan_content_stack = Gtk.Stack.new()
    vulkan_content_stack.set_vexpand(True)
    vulkan_content_stack.set_hexpand(True)

    # Connect the sidebar selection to the content stack.
    def on_sidebar_selection_changed(selection, position, items):
        selected_item = selection.get_selected_item()
        if selected_item:
            title = selected_item.get_string()
            vulkan_content_stack.set_visible_child_name(title.replace(" ", "_").lower())
            print(f"Tab '{title}' was selected.")
            
    
    selection_model.connect("selection-changed", on_sidebar_selection_changed)
    
    selection_model.set_selected(0)
    
    vulkan_split_view = Adw.NavigationSplitView.new()
    vulkan_split_view.set_vexpand(True) # Added vertical expansion
    vulkan_split_view.set_sidebar(Adw.NavigationPage.new(scrolled_sidebar, "Vulkan Sub-Tabs"))
    vulkan_split_view.set_max_sidebar_width(15)
    vulkan_split_view.set_content(Adw.NavigationPage.new(vulkan_content_stack, "Vulkan Content"))

    # ----------------Creating the Device Info Tab ------------

    DeviceTab = Gtk.Box(spacing=10)

    deviceColumnView = Gtk.ColumnView()
    deviceColumnView.props.show_row_separators = True
    deviceColumnView.props.show_column_separators = False

    factory_devices = Gtk.SignalListItemFactory()
    factory_devices.connect("setup",setup_expander)
    factory_devices.connect("bind",bind_expander)

    factory_devices_value1 = Gtk.SignalListItemFactory()
    factory_devices_value1.connect("setup",setup_image)
    factory_devices_value1.connect("bind",bind_image)

    factory_devices_value2 = Gtk.SignalListItemFactory()
    factory_devices_value2.connect("setup",setup)
    factory_devices_value2.connect("bind",bind2)

    deviceSelection = Gtk.SingleSelection()
    DeviceTab_Store = Gio.ListStore.new(ExpandDataObject3)

    deviceModel = Gtk.TreeListModel.new(DeviceTab_Store,False,True,add_tree_node3)
    deviceSelection.set_model(deviceModel)

    deviceColumnView.set_model(deviceSelection)

    deviceColumnLhs = Gtk.ColumnViewColumn.new("Device Details",factory_devices)
    deviceColumnLhs.set_resizable(True)
    deviceColumnLhs.set_fixed_width(250)
    deviceColumnRhs1 = Gtk.ColumnViewColumn.new("",factory_devices_value1)
    deviceColumnRhs1.set_resizable(True)
    deviceColumnRhs1.set_expand(False)
    deviceColumnRhs2 = Gtk.ColumnViewColumn.new("Value",factory_devices_value2)
    deviceColumnRhs2.set_expand(True)

    deviceColumnView.append_column(deviceColumnLhs)
    deviceColumnView.append_column(deviceColumnRhs1)
    deviceColumnView.append_column(deviceColumnRhs2)

    DeviceScrollbar = create_scrollbar(deviceColumnView)
#    DeviceGrid.attach(DeviceScrollbar,0,0,1,1)
    DeviceTab.append(DeviceScrollbar)

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

    propertiesColumnLhs = Gtk.ColumnViewColumn.new("Device Properties",factory_properties)
    propertiesColumnLhs.set_resizable(True)
    propertiesColumnRhs = Gtk.ColumnViewColumn.new("Value",factory_properties_value)
    propertiesColumnRhs.set_expand(True)

    propertiesColumnView.append_column(propertiesColumnLhs)
    propertiesColumnView.append_column(propertiesColumnRhs)

    factory_properties_dropdown_value = Gtk.SignalListItemFactory()
    factory_properties_dropdown_value.connect("setup",setup)
    factory_properties_dropdown_value.connect("bind",bind_column1)

    propertiesTab = Gtk.Box(spacing=10)
#    propertiesList = Gtk.StringList()

    propertiesList = Gio.ListStore.new(DataObject)
    filterPropertiesStoreDropdown = Gtk.FilterListModel(model=propertiesList)
    filter_properties_dropdown = Gtk.CustomFilter.new(_do_filter_properties_dropdown_view, filterPropertiesStoreDropdown)
    filterPropertiesStoreDropdown.set_filter(filter_properties_dropdown)
    propertiesDropdown = Gtk.DropDown(model = filterPropertiesStoreDropdown,factory=factory_properties_dropdown_value)
    propertiesDropdown.set_enable_search(True)
    properties_dropdown_search = _get_search_entry_widget(propertiesDropdown)
    properties_dropdown_search.connect('search-changed',_on_search_method_changed,filter_properties_dropdown)
 #   propertiesDropdown.set_model(propertiesList)
    propertiesDropdown.connect('notify::selected-item',selectProperties)
    setMargin(propertiesDropdown,2,1,2)
#    propertiesGrid.add(propertiesCombo)

    propertySearchEntry = Gtk.SearchEntry()
    propertySearchEntry.set_property("placeholder_text","Type here to filter.....")
    propertySearchEntry.connect("search-changed", _on_search_method_changed,filter_properties)
    propertiesScrollbar = create_scrollbar(propertiesColumnView)
    propertiesTab.append(propertiesScrollbar)



    for name in sidebar_store:
        print(name.get_string())
        if name.get_string() == "System Info":
            vulkan_content_stack.add_titled(DeviceTab, "Limits","Limits")
        if name.get_string() == "Properties":
            vulkan_content_stack.add_titled(propertiesTab,"Properties","properties")

    #--------------------------------------------------------- Fetching the device list ---------------------------------------------------------------------------------------------

    DevicesGrid = Gtk.Grid()
    DevicesGrid.set_row_spacing(10)
#    DevicesGrid.set_column_spacing(20)
    DevicesFrame.set_child(DevicesGrid)

    gpu_list = fetchContentsFromCommand(Filenames.fetch_vulkaninfo_ouput_command+Filenames.fetch_device_name_command)

    availableDevices = Gtk.Label()
    setMargin(availableDevices,350,10,10)
    gpu_image = Gtk.Image()
    gpu_image = GdkPixbuf.Pixbuf.new_from_file_at_size(const.APP_LOGO_PNG, 100, 100)
    image_renderer = Gtk.Picture.new_for_pixbuf(gpu_image)

    device_selection_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 12)
    device_selection_box.set_halign(Gtk.Align.CENTER)
    device_selection_box.set_margin_top(20)
    device_selection_box.set_margin_bottom(20)

    device_label = Gtk.Label(label="Available Device(s)")
    device_label.set_margin_start(10)
    device_label.set_margin_end(6)
    
    # --- End new code for text parsing for dropdown ---
    
    gpu_DropDown = Gtk.DropDown()
    gpu_DropDown_list = Gtk.StringList()
    gpu_DropDown.set_model(gpu_DropDown_list)
    gpu_DropDown.set_margin_start(6)
    gpu_DropDown.set_margin_end(10)
    gpu_DropDown.add_css_class("raised")

    gpu_DropDown.connect('notify::selected-item',radcall)
    for i in gpu_list:
        gpu_DropDown_list.append(i)
    
    # Add the label and dropdown to the selection box
    device_selection_box.append(device_label)
    device_selection_box.append(gpu_DropDown)

    
    # Connect the dropdown's selection change to our handler
   # device_dropdown.connect("notify::selected", on_device_selected)

    # Add real-time CPU and RAM usage labels
    cpu_label = Gtk.Label(label="CPU: N/A")
    ram_label = Gtk.Label(label="RAM: N/A")

    # Add labels to the device selection box with some spacing
    device_selection_box.append(image_renderer)
    device_selection_box.append(cpu_label)
    device_selection_box.append(ram_label)

    # Start the periodic update for system stats
    GLib.timeout_add_seconds(1, update_system_stats)
    tab2.append(device_selection_box)
    tab2.append(vulkan_split_view)


def create_limits_column(_on_search_method_changed, _do_filter_limits_view, notebook):
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
    limitsSearchBar = Gtk.SearchBar()
    limitsSearchBar.props.hexpand = True
    limitsSearchBar.props.vexpand = False
    limitsSearchBar.set_search_mode(False)
    limitsSearchBar.connect_entry(limitsSearchEntry)
    limitsSearchBar.set_child(limitsSearchEntry)
    limitsSearchBar.set_key_capture_widget(notebook)
    limitsFrameSearch.set_child(limitsSearchBar)
    LimitsGrid.attach(limitsFrameSearch,0,0,1,1)
    LimitsScrollbar = create_scrollbar(limitsColumnView)
    LimitsGrid.attach_next_to(LimitsScrollbar, limitsFrameSearch, Gtk.PositionType.BOTTOM, 1, 1)
#    DeviceGrid.attach_next_to(spinner,image_renderer,Gtk.PositionType.RIGHT,80,1)

