
#!/usr/bin/env python3

# This is a simple Libadwaita application written in Python.
# To run this, you will need to have PyGObject and libadwaita installed.
# On a Debian-based system (like Ubuntu), you can install them with:
# sudo apt install python3-gi python3-gi-cairo libadwaita-1-dev

import sys
import gi
import subprocess, const
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib, GObject, Gio, GdkPixbuf
from Common import fetchContentsFromCommand, create_scrollbar,setup_expander,bind_expander,bind2,copyContentsFromFile,getVulkanVersion,getDriverVersion,getRamInGb,getLogo,bind1,add_tree_node,add_tree_node2,ExpandDataObject,createMainFile, getGpuImage, setMargin,getDeviceSize,bind3,ExpandDataObject2,bind,bind4
import Filenames

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
    label.add_css_class(css_class='body')


def bind_column2(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    if "true" in obj.column2:
        label.remove_css_class(css_class='false')
        label.add_css_class(css_class='success')
        label.set_label(obj.column2)
    elif "false" in obj.column2:
        label.remove_css_class(css_class='true')
        label.add_css_class(css_class='error')
        label.set_label(obj.column2)
    else:
        label.set_label(obj.column2)



def create_vulkan_tab_content(self):


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
        propertiesList.remove_all()
        propertiesList.append(DataObject("Show All Device Properties",""))
        with open(Filenames.vulkan_device_properties_file, "r") as file1:
            for i, line in enumerate(file1):
                if "Vk" in line:
                    text1 = ((line.strip("\t")).replace("VkPhysicalDevice",'')).replace(":","")
                    text = text1[:-1]
                    propertiesList.append(DataObject(text.strip("\n"),""))
                    
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
                            iter2 = ExpandDataObject((text.strip('\n')).replace("count",''), value2[i].strip('\n'))
                            toprow.children.append(iter2)
                        #if "width" in line or "height" in line or "SUBGROUP" in line or "RESOLVE" in line or "SHADER_STAGE" in line:
                        if "\t\t" in line:
                                iter3 = ExpandDataObject((text.strip('\n')).replace(" count",''), value2[i].strip('\n'))
                                iter2.children.append(iter3)
                PropertiesTab_Store.append(toprow)
                #    TreeSparse.expand_all()
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

            label = "Device Extensions (%d)" %len(vulkan_device_extensions_rhs)
            deviceExtensionColumn.set_title(label)
        #    notebook.set_tab_label(ExtensionTab, Gtk.Label(label=label))

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
                


        labe1Format = "Device Formats (%d)" %len(valueFormats)
        formatColumnLhs.set_title(labe1Format)
    #    notebook.set_tab_label(FormatsTab,Gtk.Label(label = labe1Format))



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
        heapColumnLhs.set_title(labe13)
     #   notebook.set_tab_label(MemoryHeapTab,Gtk.Label(label=labe13))
        label2 = "Memory Types (%d) " %(len(vulkan_memory_types_property_flags))
        memoryTypesColumnLhs.set_title(label2)
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
        queueColumnLhs.set_title(label)
    #    notebook.set_tab_label(QueueTab, Gtk.Label(label=label))

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

        label = Gtk.Label.new("Instance Extensions (%d)" %len(vulkan_device_instance_lhs))
#        InstanceNotebook.set_tab_label(InstanceExtTab, Gtk.Label(label=label))
     #   row.set_header(label)



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
        instanceExtensionColumn.set_title(label)
        layerColumnLhs.set_title(label2)
    #    notebook.set_tab_label(InstanceExtTab, Gtk.Label(label=label))
    #    notebook.set_tab_label(InstanceLayersTab, Gtk.Label(label=label2))
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
        current_count = filter_list_model.get_n_items()
        if search_text_widget == "":
            deviceExtensionColumn.set_title("Device Extensions (%d)" %(current_count + 1))
        else:
            deviceExtensionColumn.set_title("Device Extensions (%d)" % current_count)
        return search_text_widget.upper() in item.column1.upper() or search_text_widget.upper() in item.column2.upper()
    
    def _do_filter_feature_view(item, filter_list_model):
        search_text_widget = featureSearchEntry.get_text()
        current_count = filter_list_model.get_n_items()
        if search_text_widget == "":
            featureColumn1.set_title("Device Features")
        else:
            featureColumn1.set_title("Device Featres (%d)" % current_count)
        return search_text_widget.upper() in item.column1.upper() or search_text_widget.upper() in item.column2.upper()

    def _do_filter_instances_view(item, filter_list_model):
        search_text_widget = instanceSearchEntry.get_text()
        current_count = filter_list_model.get_n_items()
        if search_text_widget == "":
            instanceExtensionColumn.set_title("Instance Extensions (%d)" %(current_count + 1))
        else:
            instanceExtensionColumn.set_title("Instance Extensions (%d)" % current_count)
        return search_text_widget.upper() in item.column1.upper() or search_text_widget.upper() in item.column2.upper()

    def _do_filter_limits_view(item, filter_list_model):
        search_text_widget = limitsSearchEntry.get_text()
        current_count = filter_list_model.get_n_items()
        if search_text_widget == "":
            limitColumnLhs.set_title("Device Limits")
        else:
            limitColumnLhs.set_title("Device Limits (%d)" % current_count)
        return search_text_widget.upper() in item.data.upper() or search_text_widget.upper() in item.data2.upper()

    def _do_filter_properties_view(item, filter_list_model):
        search_text_widget = propertySearchEntry.get_text()
        return search_text_widget.upper() in item.data.upper() or search_text_widget.upper() in item.data2.upper()


    def _do_filter_layers_view(item, filter_list_model):
        search_text_widget = layerSearchEntry.get_text()
        current_count = filter_list_model.get_n_items()
        if search_text_widget == "":
            layerColumnLhs.set_title("Instance Layers (%d)" %(current_count + 1))
        else:
            layerColumnLhs.set_title("Instance Layers (%d)" % current_count)
        return search_text_widget.upper() in item.data.upper() or search_text_widget.upper() in item.data2.upper() or search_text_widget.upper() in item.data3.upper() or search_text_widget.upper() in item.data4.upper() or search_text_widget.upper() in item.data5.upper()


    def _do_filter_formats_view(item, filter_list_model):
        search_text_widget = formatSearchEntry.get_text()
        current_count = filter_list_model.get_n_items()
        if search_text_widget == "":
            formatColumnLhs.set_title("Device Formats (%d)" %(current_count + 1))
        else:
            formatColumnLhs.set_title("Device Formats (%d)" % current_count)
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


    def on_gpu_dropdown_changed(gpu_dropdown,dummy):
        text = gpu_dropdown.props.selected
        Devices(text)
        Limits(text)
        Features(text)
        Extensions(text)
        Formats(text)
        MemoryTypes(text)
        Queues(text)
        Instance()
        Surface(text)

        gpu_image = getGpuImage(gpu_list[text])
        image_renderer.set_pixbuf(gpu_image)

    """
    Creates the content for the first tab, featuring a label and a
    gpu_dropdown for selecting Vulkan devices, now with a NavigationSplitView.
    """
    # Create a vertical box to hold the widgets
    box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
    
    # Create a horizontal box to place the label and gpu_dropdown side-by-side
    h_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)
    h_box.set_halign(Gtk.Align.CENTER)
    
    # Add a top margin to create space between the header bar and the content
    h_box.set_margin_top(10)
    h_box.set_margin_bottom(10)
    h_box.set_margin_start(10)

    # Create the label for the devices
    label = Gtk.Label.new("Available Device(s) :")
    h_box.append(label)

    # Create a list with some dummy device names
    gpu_list = fetchContentsFromCommand(Filenames.fetch_vulkaninfo_ouput_command+Filenames.fetch_device_name_command)
    
    # Create the gpu_dropdown, populated from the list of strings
    gpu_Dropdown = Gtk.DropDown()
    gpu_Dropdown.add_css_class(css_class="card")
    gpu_Dropdown_list = Gtk.StringList()
    gpu_Dropdown.set_model(gpu_Dropdown_list)
    gpu_Dropdown.set_margin_start(10)
    h_box.append(gpu_Dropdown)
    
    for i in gpu_list:
        gpu_Dropdown_list.append(i)
    # Add the horizontal box to the main vertical box
    box.append(h_box)
    
    # Create a new NavigationSplitView container
    split_view_container = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
    split_view_container.set_vexpand(True)
    split_view_container.set_hexpand(True)
    
    # Create a new NavigationSplitView
    split_view = Adw.NavigationSplitView.new()
    split_view.set_vexpand(True)
    split_view.set_hexpand(True)

    # Create the sidebar content using a Gtk.ListBox for tabs
    sidebar_listbox = Gtk.ListBox.new()
    sidebar_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
    sidebar_listbox.set_vexpand(True)
    sidebar_listbox.add_css_class(css_class="boxed-list")
    sidebar_listbox.add_css_class(css_class="toolbar")


#    sidebar_listbox.add_css_class(css_class="frame")
    # Set the show-separators property to False
    sidebar_listbox.set_show_separators(True)
    
    # Add the tabs to the sidebar ListBox
    tabs = [
        "System Information", "Limits", "Properties", "Extensions",
        "Features", "Formats", "Memory Types", "Memory Heaps", "Queues",
        "Instance Extensions", "Instance Layers", "Surface"
    ]
    
    # Create the content view using a Gtk.Stack to switch pages
    content_stack = Gtk.Stack.new()

    # Create the content pages for each tab and add them to the stack
    for tab_name in tabs:
        row = Gtk.ListBoxRow()
        label = Gtk.Label.new(tab_name)
        # Add padding to the label inside the row
        label.set_margin_top(10)
        label.set_margin_bottom(10)
        row.set_child(label)
        sidebar_listbox.append(row)


        # Create a box for the content of this specific tab
        content_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        
        if tab_name == "System Information":
            # Create a selection model from the new Gio.ListStore
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
            deviceColumnView.add_css_class(css_class="toolbar")

            DeviceScrollbar = create_scrollbar(deviceColumnView)


            # Append the scrolled window to the content box
            content_box.append(DeviceScrollbar)
        
        elif tab_name == "Properties":


            propertiesContentBox = Gtk.Box.new(Gtk.Orientation.VERTICAL,2)
            propertiesSearchDropdownBox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL,10)
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
            propertiesColumnView.add_css_class(css_class="toolbar")
            propertiesColumnView.add_css_class(css_class="property")


            propertiesColumnLhs = Gtk.ColumnViewColumn.new("Device Properties",factory_properties)
            propertiesColumnLhs.set_resizable(True)
            propertiesColumnRhs = Gtk.ColumnViewColumn.new("Value",factory_properties_value)
            propertiesColumnRhs.set_expand(True)

            propertiesColumnView.append_column(propertiesColumnLhs)
            propertiesColumnView.append_column(propertiesColumnRhs)

            factory_properties_dropdown_value = Gtk.SignalListItemFactory()
            factory_properties_dropdown_value.connect("setup",setup)
            factory_properties_dropdown_value.connect("bind",bind_column1)

        #    propertiesList = Gtk.StringList()

            propertiesList = Gio.ListStore.new(DataObject)
            filterPropertiesStoreDropdown = Gtk.FilterListModel(model=propertiesList)
            filter_properties_dropdown = Gtk.CustomFilter.new(_do_filter_properties_dropdown_view, filterPropertiesStoreDropdown)
            filterPropertiesStoreDropdown.set_filter(filter_properties_dropdown)
            propertiesDropdown = Gtk.DropDown(model = filterPropertiesStoreDropdown,factory=factory_properties_dropdown_value)
            propertiesDropdown.set_enable_search(True)
            propertiesDropdown.add_css_class(css_class="menu")
            properties_dropdown_search = _get_search_entry_widget(propertiesDropdown)
            properties_dropdown_search.connect('search-changed',_on_search_method_changed,filter_properties_dropdown)
        #   propertiesDropdown.set_model(propertiesList)
            propertiesDropdown.connect('notify::selected-item',selectProperties)
            setMargin(propertiesDropdown,2,1,2)
        #    propertiesGrid.add(propertiesCombo)

            propertySearchEntry = Gtk.SearchEntry()
            propertySearchEntry.add_css_class(css_class="toolbar")
            propertySearchEntry.add_css_class(css_class="inline")
            propertySearchEntry.set_property("placeholder_text","Type here to filter.....")
            propertySearchEntry.connect("search-changed", _on_search_method_changed,filter_properties)
            propertiesScrollbar = create_scrollbar(propertiesColumnView)

            propertiesContentBox.append(propertiesDropdown)
            propertiesContentBox.append(propertiesScrollbar)
            propertiesContentBox.append(propertySearchEntry)
            content_box.append(propertiesContentBox)
        

        elif tab_name == "Limits":

            limitsContentBox = Gtk.Box.new(Gtk.Orientation.VERTICAL,2)
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
            limitsColumnView.add_css_class(css_class="toolbar")



            limitsFrameSearch = Gtk.Frame()
            limitsSearchEntry = Gtk.SearchEntry()
            limitsSearchEntry.set_property("placeholder_text","Type here to filter.....")
            limitsSearchEntry.connect("search-changed", _on_search_method_changed,filter_limits)
            limitsFrameSearch.set_child(limitsSearchEntry)
            limitsSearchEntry.add_css_class(css_class="toolbar")
            limitsSearchEntry.add_css_class(css_class="inline")
            LimitsScrollbar = create_scrollbar(limitsColumnView)
            limitsContentBox.append(limitsSearchEntry)
            limitsContentBox.append(LimitsScrollbar)
            limitsContentBox.append(limitsFrameSearch)
            # Set up the signal handler for the gpu_dropdown to update the table
            
            # Update the table initially with the first selected item
#            self.update_system_info_tab(devices[0])
            content_box.append(limitsContentBox)

        elif tab_name == "Features":
        
            featureContentBox = Gtk.Box.new(Gtk.Orientation.VERTICAL,1)
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
            featuresColumnView.add_css_class(css_class="toolbar")


            factory_features_dropdown_value = Gtk.SignalListItemFactory()
            factory_features_dropdown_value.connect("setup",setup)
            factory_features_dropdown_value.connect("bind",bind_column1)
            
            featureList = Gio.ListStore.new(DataObject)
            filterFeaturesStoreDropdown = Gtk.FilterListModel(model=featureList)
            filter_features_dropdown = Gtk.CustomFilter.new(_do_filter_features_dropdown_view, filterFeaturesStoreDropdown)
            filterFeaturesStoreDropdown.set_filter(filter_features_dropdown)
        #   featureList  = Gtk.StringList()
            featureDropdown = Gtk.DropDown(model=filterFeaturesStoreDropdown,factory=factory_features_dropdown_value)
            featureDropdown.set_enable_search(True)
            features_dropdown_search = _get_search_entry_widget(featureDropdown)
            features_dropdown_search.connect('search-changed',_on_search_method_changed,filter_features_dropdown)
        #   featureDropdown.set_model(featureList)
            featureDropdown.connect('notify::selected-item',selectFeature)
            
            featureFrameSearch = Gtk.Frame()
            featureSearchEntry = Gtk.SearchEntry()
            featureSearchEntry.add_css_class(css_class="toolbar")
            featureSearchEntry.add_css_class(css_class="inline")
            featureFrameSearch.set_child(featureSearchEntry)
            featureSearchEntry.set_property("placeholder_text","Type here to filter.....")
            featureSearchEntry.connect("search-changed",_on_search_method_changed,filter_features)
            setMargin(featureDropdown,2,1,2)
            FeatureScrollbar = create_scrollbar(featuresColumnView)
            featureContentBox.append(featureDropdown)
            featureContentBox.append(FeatureScrollbar)
            featureContentBox.append(featureFrameSearch)

            content_box.append(featureContentBox)

        elif tab_name == "Extensions":

            extensionContentBox = Gtk.Box.new(Gtk.Orientation.VERTICAL,1)
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

            deviceExtensionColumn = Gtk.ColumnViewColumn.new("Device Extensions")
            deviceExtensionColumn.set_factory(factory)
            deviceExtensionColumn.set_resizable(True)
            extensionColumnView.append_column(deviceExtensionColumn)

            extensionRevisionColumn = Gtk.ColumnViewColumn.new("Revision")
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
            extensionColumnView.add_css_class(css_class="toolbar")


            extensionFrameSearch = Gtk.Frame()
            extensionSearchEntry = Gtk.SearchEntry()
            extensionSearchEntry.add_css_class(css_class="toolbar")
            extensionSearchEntry.add_css_class(css_class="toolbar")
            extensionFrameSearch.set_child(extensionSearchEntry)
            extensionSearchEntry.set_property("placeholder_text","Type here to filter.....")
            extensionSearchEntry.connect("search-changed", _on_search_method_changed,filter_extensions)
            extensionContentBox.append(scrollable_extension)
            extensionContentBox.append(extensionFrameSearch)
            content_box.append(extensionContentBox)
        
        elif tab_name == "Formats":

            factory_formats_dropdown_value = Gtk.SignalListItemFactory()
            factory_formats_dropdown_value.connect("setup",setup)
            factory_formats_dropdown_value.connect("bind",bind_column1)

            FormatsList = Gio.ListStore.new(DataObject)
            filterFormatStoreDropdown = Gtk.FilterListModel(model=FormatsList)
            filter_formats_dropdown = Gtk.CustomFilter.new(_do_filter_formats_dropdown_view, filterFormatStoreDropdown)
            filterFormatStoreDropdown.set_filter(filter_formats_dropdown)
            FormatsDropDown = Gtk.DropDown(model=filterFormatStoreDropdown,factory=factory_formats_dropdown_value)
            FormatsDropDown.set_model(filterFormatStoreDropdown)
            FormatsDropDown.connect('notify::selected-item',selectFormats)
            FormatsDropDown.set_enable_search(True)
            formats_dropdown_search = _get_search_entry_widget(FormatsDropDown)
            formats_dropdown_search.connect('search-changed',_on_search_method_changed,filter_formats_dropdown)
            formatsContentBox = Gtk.Box.new(Gtk.Orientation.VERTICAL,2)

            formatsColumnView = Gtk.ColumnView()
            formatsColumnView.props.show_row_separators = True
            formatsColumnView.props.show_column_separators = False
            formatsColumnView.props.single_click_activate - True

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
            formatsColumnView.add_css_class(css_class="toolbar")


            formatColumnLhs = Gtk.ColumnViewColumn.new("Device Formats",factory_formats)
            formatColumnLhs.set_resizable(True)
            formatColumnLhs.set_expand(True)
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

            formatSearchFrame = Gtk.Frame()
            formatSearchEntry = Gtk.SearchEntry()
            formatSearchEntry.add_css_class(css_class="toolbar")
            formatSearchEntry.add_css_class(css_class="inline")
            formatSearchFrame.set_child(formatSearchEntry)
            formatSearchEntry.set_property("placeholder_text","Type here to filter.....")
            formatSearchEntry.connect("search-changed", _on_search_method_changed,filter_formats)
            formatsScrollbar = create_scrollbar(formatsColumnView)
    #        formatsSearchDropdownBox.append(FormatsDropDown)
    #        formatsSearchDropdownBox.append(formatSearchFrame)
            formatsContentBox.append(FormatsDropDown)
            formatsContentBox.append(formatsScrollbar)
            formatsContentBox.append(formatSearchFrame)

            content_box.append(formatsContentBox)

        elif tab_name == "Memory Types":

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

            memoryTypesColumnView.add_css_class(css_class="toolbar")


            MemoryScrollbar = create_scrollbar(memoryTypesColumnView)

            content_box.append(MemoryScrollbar)
        # -----------------------------------------------------------------------------------------------------------------------------------
        elif tab_name == "Memory Heaps":

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

            heapsColumnView.add_css_class(css_class="toolbar")


            HeapScrollbar = create_scrollbar(heapsColumnView)

            content_box.append(HeapScrollbar)


        elif tab_name == "Queues":

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

            queueColumnLhs = Gtk.ColumnViewColumn.new("Queue Properties",factory_queues)
            queueColumnLhs.set_resizable(True)
            queueColumnRhs = Gtk.ColumnViewColumn.new("Value",factory_queues_value)
            queueColumnRhs.set_expand(True)

            queuesColumnView.append_column(queueColumnLhs)
            queuesColumnView.append_column(queueColumnRhs)

            queuesColumnView.add_css_class(css_class="toolbar")


            QueueScrollbar = create_scrollbar(queuesColumnView)

            content_box.append(QueueScrollbar)

        elif tab_name == "Instance Extensions":

            instanceContentBox = Gtk.Box.new(Gtk.Orientation.VERTICAL,2)

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

            instanceExtensionColumn = Gtk.ColumnViewColumn.new("Instance Extensions")
            instanceExtensionColumn.set_factory(factory)
            instanceExtensionColumn.set_resizable(True)
            instanceExtensionColumnView.append_column(instanceExtensionColumn)

            instanceExtensionRevisionColumn = Gtk.ColumnViewColumn.new("Revision")
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

            instanceExtensionColumnView.add_css_class(css_class="toolbar")


            instanceSearchFrame = Gtk.Frame()
            instanceSearchEntry = Gtk.SearchEntry()
            instanceSearchEntry.add_css_class(css_class="toolbar")
            instanceSearchEntry.add_css_class(css_class="inline")
            instanceSearchEntry.set_property("placeholder_text","Type here to filter.....")
            instanceSearchEntry.connect("search-changed",_on_search_method_changed,filter_instances)
        #   instanceSearchEntry = createSearchEntry(InstanceTab_Store_filter)
            instanceSearchFrame.set_child(instanceSearchEntry)
            instanceScrollbar = create_scrollbar(instanceExtensionColumnView)

            instanceContentBox.append(instanceScrollbar)

            instanceContentBox.append(instanceSearchFrame)
            content_box.append(instanceContentBox)

        #    InstanceTab_Store_filter.set_visible_func(searchInstanceExtTree, data=TreeInstance)
        elif tab_name == "Instance Layers":

            instanceLayersContentBox = Gtk.Box.new(Gtk.Orientation.VERTICAL,2)

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
            layersColumnView.add_css_class(css_class="toolbar")


            layerColumnLhs = Gtk.ColumnViewColumn.new("Layers",factory_layers)
            layerColumnLhs.set_resizable(True)
            layerColumnLhs.set_expand(True)
            layerColumnRhs1 = Gtk.ColumnViewColumn.new("Vulkan Version",factory_layers_value1)
            layerColumnRhs1.set_expand(True)
            layerColumnRhs2 = Gtk.ColumnViewColumn.new("Layer Version",factory_layers_value2)
            layerColumnRhs2.set_expand(True)
            layerColumnRhs3 = Gtk.ColumnViewColumn.new("Extension Count",factory_layers_value3)
            layerColumnRhs3.set_expand(True)
            layerColumnRhs4 = Gtk.ColumnViewColumn.new("Description",factory_layers_value4)
            layerColumnRhs4.set_expand(True)

            layersColumnView.append_column(layerColumnLhs)
            layersColumnView.append_column(layerColumnRhs1)
            layersColumnView.append_column(layerColumnRhs2)
            layersColumnView.append_column(layerColumnRhs3)
            layersColumnView.append_column(layerColumnRhs4)

            layerSearchFrame = Gtk.Frame()
            layerSearchEntry = Gtk.SearchEntry()
            layerSearchEntry.add_css_class(css_class="toolbar")
            layerSearchEntry.add_css_class(css_class="inline")
            layerSearchEntry.set_property("placeholder_text","Type here to filter.....")
            layerSearchEntry.connect("search-changed",_on_search_method_changed,filter_layers)
            layerSearchFrame.set_child(layerSearchEntry)
            layerScrollbar = create_scrollbar(layersColumnView)

            instanceLayersContentBox.append(layerScrollbar)

            instanceLayersContentBox.append(layerSearchFrame)

            content_box.append(instanceLayersContentBox)

        elif tab_name == "Surface":

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
            surfaceColumnView.add_css_class(css_class="toolbar")


            SurfaceScrollbar = create_scrollbar(surfaceColumnView)

            content_box.append(SurfaceScrollbar)
            
        else:
            # For all other tabs, create a simple label
            content_label = Gtk.Label.new(f"Content for {tab_name}")
            content_label.set_css_classes(["title-1"])
            content_box.set_halign(Gtk.Align.CENTER)
            content_box.set_valign(Gtk.Align.CENTER)
            content_box.append(content_label)
        
        # Add the content box to the stack
        content_stack.add_titled(content_box, tab_name.replace(" ", "-").lower(), tab_name)

    gpu_Dropdown.connect("notify::selected-item", on_gpu_dropdown_changed)

    gpu_image = Gtk.Image()
    gpu_image = GdkPixbuf.Pixbuf.new_from_file_at_size(const.APP_LOGO_PNG, 100, 100)
    image_renderer = Gtk.Picture.new_for_pixbuf(gpu_image)
    gpu_Dropdown.set_margin_end(10)
    h_box.append(image_renderer)

    on_gpu_dropdown_changed(gpu_Dropdown,dummy=0)
    # Create a scrolled window for the sidebar list
    sidebar_scrolled_window = Gtk.ScrolledWindow.new()
    sidebar_scrolled_window.set_child(sidebar_listbox)

    # Connect the listbox signal to change the stack page
    def on_row_activated(listbox, row):
        # Get the label from the activated row to find the tab's name
        tab_label = row.get_child()
        tab_name = tab_label.get_label()
        
        # The name for the stack child is the tab name, with spaces replaced by dashes and lowercase
        child_name = tab_name.replace(" ", "-").lower()

        # Set the visible child of the stack using its name
        content_stack.set_visible_child_name(child_name)
        
    sidebar_listbox.connect("row-activated", on_row_activated)
    sidebar_listbox.select_row(sidebar_listbox.get_row_at_index(0))
#    content_stack.set_visible_child_name("System Information")
    # Set a minimum width for the sidebar


    # Create the Adw.NavigationPage wrappers for the sidebar and content
    sidebar_page = Adw.NavigationPage.new(sidebar_scrolled_window, "Sidebar")
    content_page = Adw.NavigationPage.new(content_stack, "Content")
    
    # Set the sidebar and content for the split view using the new pages
    split_view.set_sidebar(sidebar_page)
    split_view.set_content(content_page)
    
    # Add the split view to its new container
    split_view_container.append(split_view)
    
    # Add the split view container to the main vertical box
    box.append(split_view_container)
    
    return box