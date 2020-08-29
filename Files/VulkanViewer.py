import os

import gi

import Const

import threading


gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf
# noinspection PyPep8
from Common import copyContentsFromFile, setBackgroundColor, setColumns, createSubTab, createScrollbar, createSubFrame, \
    colorTrueFalse, getDriverVersion, getVulkanVersion, getDeviceSize, refresh_filter, getRamInGb, fetchImageFromUrl, getFormatValue

MWIDTH = 300

RANGE1 = 100

DeviceTitle = ["Device Information", "Details"]
SparseTitle = ["Device Properties", "Value"]
FeaturesTitle = ["Device Features", "Value"]
LimitsTitle = ["Device Limits", "Value"]
ExtensionsTitle = ["Device Extensions", "Version"]
FormatsTitle = ["Device Formats","linearTiling","optimalTiling","bufferFeatures"]
MemoryTitle = ["Memory Types", "Value"]
HeapTitle = ["Memory Heaps", "Device Size","Budget", "Usage", "HEAP DEVICE LOCAL"]
QueuesLHS = ["VkQueueFamilyProperties", "QueueCount", "timestampValidBits", "queueFlags","GRAPHICS BIT", "COMPUTE BIT", "TRANSFER BIT",
              "SPARSE BINDING BIT", "minImageTransferGranularity.width", "minImageTransferGranularity.height",
              "minImageTransferGranularity.depth"]
QueueTitle = ["Queue Family","Value"]
InstanceTitle = ["Extensions", "Version"]
LayerTitle = ["Layers", "Vulkan Version", "Layer Version", "Extension Count", "Description"]
SurfaceTitle = ["Surface Capabilities", "Value"]

def Vulkan(tab2):
    # Creating Tabs for different Features

    # Creating Feature Tab
    def Devices(GPUname):
        # noinspection PyPep8
        os.system(
            "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceLimits:/{flag=0}flag' | grep '=' | grep -v Version > /tmp/gpu-viewer/VKDDeviceinfo1.txt" % GPUname)
        # noinspection PyPep8
        os.system(
            "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceLimits:/{flag=0}flag' | awk '/--.*/{flag=1;next}flag' | grep Version | awk '{gsub(/\(.*/,'True');}1' >> /tmp/gpu-viewer/VKDDeviceinfo1.txt" % GPUname)

        # noinspection PyPep8
        os.system(
            "cat /tmp/gpu-viewer/VKDDeviceinfo1.txt | sort | awk '{gsub(/=.*/,'True');}1' > /tmp/gpu-viewer/VKDDeviceinfo.txt")
        # noinspection PyPep8
        os.system(
            "cat /tmp/gpu-viewer/VKDDeviceinfo1.txt | sort | grep -o =.* | grep -o ' .*' > /tmp/gpu-viewer/VKDDeviceinfo2.txt")
        os.system(
            "lscpu | awk '/name|^CPU/' | sort -r | awk '{gsub(/:.*/,'True');}1' >> /tmp/gpu-viewer/VKDDeviceinfo.txt")
        os.system(
            "lscpu | awk '/name|^CPU/'| sort -r | grep -o :.* | grep -o '  .*' >> /tmp/gpu-viewer/VKDDeviceinfo2.txt")
        os.system("cat /proc/meminfo | grep Mem | awk '{gsub(/:.*/,'True')l}1' >> /tmp/gpu-viewer/VKDDeviceinfo.txt")
        os.system("cat /proc/meminfo | grep Mem | grep -o :.* | grep -o ' .*' >> /tmp/gpu-viewer/VKDDeviceinfo2.txt")
        valueLHS = copyContentsFromFile("/tmp/gpu-viewer/VKDDeviceinfo.txt")

        try:
            os.system("lsb_release -d -r -c > /tmp/gpu-viewer/VKDLsbRelease.txt")
            os.system("cat /tmp/gpu-viewer/VKDLsbRelease.txt | grep -o :.* >> /tmp/gpu-viewer/VKDDeviceinfo2.txt")
            # noinspection PyPep8
            os.system(
                "cat /tmp/gpu-viewer/VKDLsbRelease.txt | awk '{gsub(/:.*/,'True');}1' > /tmp/gpu-viewer/VKDLsbReleaseLHS.txt")
            os.system("echo $DESKTOP_SESSION >> /tmp/gpu-viewer/VKDDeviceinfo2.txt")
            os.system("uname -r >> /tmp/gpu-viewer/VKDDeviceinfo2.txt")
            valueLHS = valueLHS + copyContentsFromFile("/tmp/gpu-viewer/VKDLsbReleaseLHS.txt")
            valueLHS.append("Desktop")
            valueLHS.append("Kernel")
        except Exception as e:
            raise e
        # Storing the RHS values into a list

        valueRHS = copyContentsFromFile("/tmp/gpu-viewer/VKDDeviceinfo2.txt")

        for i in range(len(valueRHS)):
            if "0x" in valueRHS[i]:
                valueRHS[i] = int(valueRHS[i], 16)
                valueRHS[i] = str("%d" % valueRHS[i])

        #valueRHS[0] = getVulkanVersion(valueRHS[0])
        #valueRHS[4] = getDriverVersion(valueRHS)


        valueLHS = [i.strip('\t') for i in valueLHS]
        valueRHS = [i.strip(':') for i in valueRHS]
        valueRHS = [i.strip('\t') for i in valueRHS]
        valueRHS = [i.strip(' ') for i in valueRHS]
        # Printing the Details into the Treeview

        DeviceTab_Store.clear()
        TreeDevice.set_model(DeviceTab_Store)

        deviceHardwareInfo = ["GPU","CPU","MEMORY","OS INFO."]

        for i in range(len(valueRHS)):
            background_color = setBackgroundColor(i)
            if "apiVersion" in valueLHS[i]:
                valueRHS[i] = getVulkanVersion(valueRHS[i])
                iter1 = DeviceTab_Store.append(None,["Vulkan Details..."," ",Const.BGCOLOR3])
            if "driverVersion" in valueLHS[i]:
                valueRHS[i] = getDriverVersion(valueRHS)
            if "Model" in valueLHS[i]:
                iter1 = DeviceTab_Store.append(None,["Processor Details..."," ",Const.BGCOLOR3])
            if "Description" in valueLHS[i]:
                iter1 = DeviceTab_Store.append(None,["Operating System Details..."," ",Const.BGCOLOR3])
                DeviceTab_Store.append(iter1,["Distribution", valueRHS[i].strip('\n'), background_color])
                continue
            if "Total" in valueLHS[i]:
                iter1 = DeviceTab_Store.append(None,["Memory Details..."," ",Const.BGCOLOR3])
                DeviceTab_Store.append(iter1,[valueLHS[i].strip('\n'), getRamInGb(valueRHS[i]), background_color])
            elif "Mem" in valueLHS[i]:
                DeviceTab_Store.append(iter1,[valueLHS[i].strip('\n'), getRamInGb(valueRHS[i]), background_color])
            else:
                DeviceTab_Store.append(iter1,[valueLHS[i].strip('\n'), valueRHS[i].strip('\n'), background_color])

        TreeDevice.expand_all()

        os.system("cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Extensions.*/{flag=0}flag' | awk '/VkPhysicalDeviceSparseProperties:/{flag=1}/Device Extensions.*/{flag=0}flag' | awk '/./' > /tmp/gpu-viewer/VKDDevicesparseinfo1.txt" % GPUname)

        propertiesCombo.remove_all()
        with open("/tmp/gpu-viewer/VKDDevicesparseinfo1.txt", "r") as file1:
            for i, line in enumerate(file1):
                if "Vk" in line:
                    text1 = line.strip("\t")
                    text = text1[:-1]
                    propertiesCombo.append_text(text.strip("\n"))

        propertiesCombo.insert_text(0, "Show All Properties")
        propertiesCombo.set_active(0)

    #    notebook.set_tab_label(propertiesTab,Gtk.Label(label))

    def Features(GPUname):

    #    for i in range(len(list)):
    #        if
        i = GPUname
                # noinspection PyPep8
        os.system(
            "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/VkPhysicalDeviceFeatures:/{flag=1;next}/GPU*/{flag=0}flag' | awk '/==/{flag=1 ; next} flag' | grep = > /tmp/gpu-viewer/VKDFeatures1.txt" %(i,i+1))
        # noinspection PyPep8
        os.system(
            "cat /tmp/gpu-viewer/vulkaninfo.txt |  awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/VkPhysicalDeviceFeatures:/{flag=1;next}/GPU*/{flag=0}flag' > /tmp/gpu-viewer/VKDeviceFeatures.txt" %(i,i+1))
    #    break
        featureCombo.remove_all()
        with open("/tmp/gpu-viewer/VKDeviceFeatures.txt", "r") as file:
            for line in file:
                if "Vk" in line:
                    text = line[:-2]
                    featureCombo.append_text(text.strip("\n"))

        featureCombo.insert_text(0, "Show All Features")
        featureCombo.set_active(0)

    def Limits(GPUname):


        os.system(
            "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceSparseProperties:/{flag=0}flag' | awk '/VkPhysicalDeviceLimits:/{flag=1;next}/VkPhysicalDeviceSparseProperties:/{flag=0}flag' | awk '/--/{flag=1;next}flag' | awk '/./' > /tmp/gpu-viewer/VKDlimits1.txt" % GPUname)
        os.system("cat /tmp/gpu-viewer/VKDlimits1.txt | awk '{gsub(/=.*/,'True');}1' > /tmp/gpu-viewer/VKDlimits.txt")
        os.system(
            "cat /tmp/gpu-viewer/VKDlimits1.txt | grep -o '=.*' | grep -o '[ -].*' > /tmp/gpu-viewer/VKDlimits2.txt")

        valueLHS = copyContentsFromFile("/tmp/gpu-viewer/VKDlimits.txt")
        valueRHS = copyContentsFromFile("/tmp/gpu-viewer/VKDlimits2.txt")

        # finding and converting any hexadecimal value to decimal

        LimitsTab_Store.clear()
        TreeLimits.set_model(LimitsTab_Store_filter)


        with open("/tmp/gpu-viewer/VKDlimits1.txt", "r") as file1:
            j = 0
            for i,line in enumerate(file1):
                background_color = setBackgroundColor(i)
                if '=' in line:
                    text = valueLHS[i].strip('\t')
                    iter = LimitsTab_Store.append(None,[(text.strip('\n')).replace(' count',''), valueRHS[j].strip('\n'), background_color])
                    j = j + 1
                else:
                    text = valueLHS[i].strip('\t')
                    if "\t" in line :
                        iter2 = LimitsTab_Store.append(iter,[text.strip('\n')," ", background_color])
                    else:
                        LimitsTab_Store.append(iter2,[text.strip('\n')," ", background_color])
            TreeLimits.expand_all()

    def Extensions(GPUname):

        for i in range(len(list)):
            if GPUname == i:
                # noinspection PyPep8
                os.system(
                    "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkQueueFamilyProperties/{flag=0}flag'|awk '/Device Extensions/{flag=1; next}/VkQueueFamilyProperties/{flag=0} flag' | grep VK_ | sort > /tmp/gpu-viewer/VKDExtensions1.txt" % i)
                break
        # noinspection PyPep8
        os.system(
            "cat /tmp/gpu-viewer/VKDExtensions1.txt | grep -o 'revision.*' | grep -o ' .*' > /tmp/gpu-viewer/VKDExtensionsRHS.txt")
        # noinspection PyPep8
        os.system(
            "cat /tmp/gpu-viewer/VKDExtensions1.txt | awk '{gsub(/:.*/,'True');print} ' > /tmp/gpu-viewer/VKDExtensions.txt")

        # This should take care of future versioning
        with open("/tmp/gpu-viewer/VKDExtensionsRHS.txt", "r") as file1:
            value = []
            for line in file1:
                text = line.strip('\n')
                value.append(getVulkanVersion(text))

        ExtensionTab_Store.clear()
        TreeExtension.set_model(ExtensionTab_store_filter)

        with open("/tmp/gpu-viewer/VKDExtensions.txt", "r") as file1:
            count = len(file1.readlines())
            label = "Extensions (%d)" % count
            notebook.set_tab_label(ExtensionTab, Gtk.Label(label))
            file1.seek(0, 0)
            for i, line in enumerate(file1):
                text = line.strip('\t')
                background_color = setBackgroundColor(i)
                ExtensionTab_Store.append([text.strip('\n'), value[i].strip('\n'), background_color])

    def Formats(GPUname):
                # noinspection PyPep8

        os.system(
            "vulkaninfo --show-formats | awk '/GPU%d/{flag=1;next}/GPU%d/{flag=0}flag' | awk '/Format Properties/{flag=1; next}/Unsupported Formats:*/{flag=0} flag' | awk '/./' > /tmp/gpu-viewer/VKDFORMATS.txt" % (GPUname,GPUname+1))
        # noinspection PyPep8
        os.system(
            "cat /tmp/gpu-viewer/VKDFORMATS.txt | grep FORMAT_  | grep -v FORMAT_FEATURE > /tmp/gpu-viewer/VKFORMATS.txt" )

        os.system(
            "cat /tmp/gpu-viewer/VKDFORMATS.txt | grep Formats | grep -o '=.*' | grep -o ' .*' | awk '/./' > /tmp/gpu-viewer/VKFORMATSCount.txt")

        os.system(
            "cat /tmp/gpu-viewer/VKDFORMATS.txt | grep linear | grep -o '=.*' | grep -o ' .*' | awk '/./' > /tmp/gpu-viewer/VKLinearCount.txt")
        

        os.system(
            "cat /tmp/gpu-viewer/VKDFORMATS.txt | grep optimal | grep -o '=.*' | grep -o ' .*' | awk '/./' > /tmp/gpu-viewer/VKOptimalCount.txt")
        

        os.system(
            "cat /tmp/gpu-viewer/VKDFORMATS.txt | grep buffer | grep -o '=.*' | grep -o ' .*' | awk '/./' > /tmp/gpu-viewer/VKBufferCount.txt")
        

        valueFormats = copyContentsFromFile("/tmp/gpu-viewer/VKFORMATS.txt")
        valueFormatsCount = copyContentsFromFile("/tmp/gpu-viewer/VKFORMATSCount.txt")
        valueLinearCount = copyContentsFromFile("/tmp/gpu-viewer/VKLinearCount.txt")
        valueOptimalCount = copyContentsFromFile("/tmp/gpu-viewer/VKOptimalCount.txt")
        valueBufferCount = copyContentsFromFile("/tmp/gpu-viewer/VKBufferCount.txt")
        

   
        FormatsTab_Store.clear()
        TreeFormats.set_model(FormatsTab_Store_filter)
        n = 0;p = 0; t = 0;s = 0
        for i in range(len(valueFormatsCount)):
            for j in range(int(valueFormatsCount[i])):
                if int(valueLinearCount[i]) != 0:
                    linearStatus = "true"
                    linearColor = Const.COLOR1
                else:
                    linearStatus = "false"
                    linearColor = Const.COLOR2
                if int(valueOptimalCount[i]) != 0:
                    optimalStatus = "true"
                    optimalColor = Const.COLOR1
                else:
                    optimalStatus = "false"
                    optimalColor = Const.COLOR2
                if int(valueBufferCount[i]) != 0:
                    bufferStatus = "true"
                    bufferColor = Const.COLOR1
                else:
                    bufferStatus = "false"
                    bufferColor = Const.COLOR2
                iter1 = FormatsTab_Store.append(None,[((valueFormats[n].strip('\n')).strip('\t')).replace('FORMAT_',""),linearStatus,optimalStatus,bufferStatus,setBackgroundColor(n),linearColor,optimalColor,bufferColor]) 
                if int(valueLinearCount[i]) != 0 or int(valueOptimalCount[i]) != 0 or int(valueBufferCount[i]) != 0:
                    iter2 = FormatsTab_Store.append(iter1,["linearTiling"," "," "," ",setBackgroundColor(n+1),setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j)])
                    os.system("cat /tmp/gpu-viewer/VKDFORMATS.txt | awk '/^%s$/{flag=1};flag;/Common.*/{flag=0}' | awk '/linear*/{flag=1;next}/optimal*/{flag=0}flag' > /tmp/gpu-viewer/VKLinear.txt " %(valueFormats[n].strip('\n')))
                    with open("/tmp/gpu-viewer/VKLinear.txt") as file1:
                        for k,line in enumerate(file1):
                            FormatsTab_Store.append(iter2,[((line.strip('\n')).strip('\t')).replace("FORMAT_FEATURE_","")," "," "," ",setBackgroundColor(k),setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j)])
                    iter2 = FormatsTab_Store.append(iter1,["optimalTiling"," "," "," ",setBackgroundColor(n+2),setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j)])
                    os.system("cat /tmp/gpu-viewer/VKDFORMATS.txt | awk '/^%s$/{flag=1};flag;/Common.*/{flag=0}' | awk '/optimal*/{flag=1;next}/buffer*/{flag=0}flag' > /tmp/gpu-viewer/VKOptimal.txt " %(valueFormats[n].strip('\n')))
                    with open("/tmp/gpu-viewer/VKOptimal.txt") as file1:
                        for k,line in enumerate(file1):
                            FormatsTab_Store.append(iter2,[((line.strip('\n')).strip('\t')).replace("FORMAT_FEATURE_","")," "," "," ",setBackgroundColor(k),setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j)])
                    iter2 = FormatsTab_Store.append(iter1,["bufferFeatures"," "," "," ",setBackgroundColor(n+3),setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j)])
                    os.system("cat /tmp/gpu-viewer/VKDFORMATS.txt | awk '/^%s$/{flag=1};flag;/Common.*/{flag=0}' | awk '/buffer*/{flag=1;next}/Common*/{flag=0}flag' > /tmp/gpu-viewer/VKBuffer.txt " %(valueFormats[n].strip('\n')))
                    with open("/tmp/gpu-viewer/VKBuffer.txt") as file1:
                        for k,line in enumerate(file1):
                            FormatsTab_Store.append(iter2,[((line.strip('\n')).strip('\t')).replace("FORMAT_FEATURE_","")," "," "," ",setBackgroundColor(k),setBackgroundColor(j),setBackgroundColor(j),setBackgroundColor(j)])

                n +=1



                
        labe1Format = "Formats(%d)" %len(valueFormats)
        notebook.set_tab_label(FormatsTab,Gtk.Label(labe1Format))

    def MemoryTypes(GPUname):
        # propertiesGrid.add(propertiesCombo)ame):
        os.system("cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceFeatures:/{flag=0}flag'|awk '/VkPhysicalDeviceMemoryProperties:/{flag=1; next}/VkPhysicalDeviceFeatures:/{flag=0} flag' > /tmp/gpu-viewer/VKDMemoryType.txt" % GPUname)

        # New One
        os.system("cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceFeatures:/{flag=0}flag'|awk '/VkPhysicalDeviceMemoryProperties:/{flag=1; next}/VkPhysicalDeviceFeatures:/{flag=0} flag'| awk '/memoryTypes: */{flag=1; next}/VkPhysicalDeviceFeatures:/{flag=0} flag' > /tmp/gpu-viewer/VKDMemoryTypes.txt" %GPUname)


        # MemoryType LHS
        os.system("cat /tmp/gpu-viewer/VKDMemoryTypes.txt | awk '{gsub(/[=:].*/,'True')l}1' | awk '/./' > /tmp/gpu-viewer/VKDMemoryTypesLHS.txt")

        #MemoryType qRHS
        os.system("cat /tmp/gpu-viewer/VKDMemoryTypes.txt | grep -o heapIndex.* | grep -o '= .*' > /tmp/gpu-viewer/VKDMemoryTypesRHS.txt")

        mLhs = copyContentsFromFile("/tmp/gpu-viewer/VKDMemoryTypesLHS.txt")
        mRHS = copyContentsFromFile("/tmp/gpu-viewer/VKDMemoryTypesRHS.txt")
        #Copying Values to RHS as per LHS
        j = 0
        mRhs = []
        with open("/tmp/gpu-viewer/VKDMemoryTypes.txt") as file1:
            for line in file1:
                if "heapIndex" in line:
                    mRhs.append(mRHS[j].strip('= '))
                    j = j + 1
                else:
                    mRhs.append(" ")

        propertyFlag = ["DEVICE_LOCAL","HOST_VISIBLE_BIT","HOST_COHERENT_BIT","HOST_CACHED_BIT","LAZILY_ALLOCATED_BIT","PROTECTED_BIT","DEVICE_COHERENT_BIT_AMD","DEVICE_UNCACHED_BIT_AMD"]

        # noinspection PyPep8
        os.system(
            "cat /tmp/gpu-viewer/VKDMemoryType.txt | grep propertyFlags | grep -o  =.* | grep -o ' .*' | awk '{gsub(/:.*/,'True');print}' > /tmp/gpu-viewer/VKDMemoryPropertyFlags.txt")
        propertyFlags = copyContentsFromFile("/tmp/gpu-viewer/VKDMemoryPropertyFlags.txt")


        MemoryTab_Store.clear()
        TreeMemory.set_model(MemoryTab_Store)
        p = 0
        n = 0
        for i in range(len(mLhs)):
            background_color = setBackgroundColor(i)
            if "memoryTypes" in mLhs[i]:
                iter = MemoryTab_Store.append(None,[(mLhs[i].strip('\n')).strip("\t")," ",Const.BGCOLOR3,"BLACK"])
                continue
            if "MEMORY" in mLhs[i]:
                continue
            if "None" in mLhs[i] and n == 0:
                n = n + 1
                continue
            if "heapIndex" in mLhs[i]:
                iter2 = MemoryTab_Store.append(iter,[(mLhs[i].strip('\n')).strip("\t"),mRhs[i].strip('\n'),background_color,"BLACK"])
                continue
            if  "IMAGE" in mLhs[i] and ("FORMAT" not in mLhs[i] or "color" not in mLhs[i] or "sparse" not in mLhs[i]):
                iter3 = MemoryTab_Store.append(iter2,[(mLhs[i].strip('\n')).strip("\t")," ",background_color,"BLACK"])
                continue
            if "\t\t\t" in mLhs[i] and "IMAGE" not in mLhs[i]:
                MemoryTab_Store.append(iter3,[(mLhs[i].strip('\n')).strip("\t")," ",background_color,"BLACK"])
                continue
            if  "IMAGE" in mLhs[i] and ("FORMAT" not in mLhs[i] or "color" not in mLhs[i] or "sparse" not in mLhs[i]):
                iter3 = MemoryTab_Store.append(iter2,[(mLhs[i].strip('\n')).strip("\t")," ",background_color,"BLACK"])
                continue
            if "\t\t\t" in mLhs[i] and "IMAGE" not in mLhs[i]:
                MemoryTab_Store.append(iter3,[(mLhs[i].strip('\n')).strip("\t")," ",background_color,"BLACK"])
                continue
            else:
                Flag = []
                if "propertyFlags" in mLhs[i]:
                        propertyFlags[p]
                        #text = (mRhs[i].strip('\n')).strip(": ")
                        iter2 = MemoryTab_Store.append(iter,[(mLhs[i].strip('\n')).strip("\t")," ",background_color,"BLACK"])
                        dec = int(propertyFlags[p], 16)
                        if  dec == 0:
                            n = 0
                        binary = bin(dec)[2:]
                        for j in range(len(binary)):
                            if binary[j] == '0':
                                Flag.insert(j, "false")
                            if binary[j] == '1':
                                Flag.insert(j, "true")
                        for j in range(5 - len(binary)):
                            Flag.insert(0, "false")
                        Flag.reverse()
                        for k in range(len(Flag)):
                            if "true" in Flag[k]:
                                fColor = "GREEN"
                            elif "false" in Flag[k]:
                                fColor = "RED"
                            else:
                                fColor = "BLACK"
                            MemoryTab_Store.append(iter2,[propertyFlag[k],Flag[k],setBackgroundColor(k),fColor])
                        p = p + 1
                else:
                    iter2 = MemoryTab_Store.append(iter,[(mLhs[i].strip('\n')).strip("\t")," ",background_color,"BLACK"])
                    continue

        labe12 = "Memory Types (%d)" %len(propertyFlags)
        MemoryNotebook.set_tab_label(MemoryTypeTab,Gtk.Label(labe12))

        TreeMemory.expand_all()

        os.system("cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceFeatures:/{flag=0}flag'|awk '/VkPhysicalDeviceMemoryProperties:/{flag=1; next}/VkPhysicalDeviceFeatures:/{flag=0} flag' > /tmp/gpu-viewer/VKDMemoryHeap.txt" % GPUname)
        HCount = 0
        HEAP_DEVICE_LOCAL = []

        with open("/tmp/gpu-viewer/VKDMemoryHeap.txt", "r") as file1:
            Heapfg = []
            for line in file1:
                if "memoryHeaps" in line:
                    HCount = HCount + 1
                if "HEAP_DEVICE_LOCAL" in line:
                    HEAP_DEVICE_LOCAL.append("true")
                    Heapfg.append(Const.COLOR1)
                if "None" in line:
                    HEAP_DEVICE_LOCAL.append("false")
                    Heapfg.append(Const.COLOR2)

        os.system(
            "cat /tmp/gpu-viewer/VKDMemoryHeap.txt | grep size | grep -o  =.* | grep -o ' .*' | awk '{gsub(/\(.*/,'True');print}' > /tmp/gpu-viewer/VKDDeviceSize.txt")
        size = copyContentsFromFile("/tmp/gpu-viewer/VKDDeviceSize.txt")

        os.system(
            "cat /tmp/gpu-viewer/VKDMemoryHeap.txt | grep budget | grep -o  =.* | grep -o ' .*' | awk '{gsub(/\(.*/,'True');print}' > /tmp/gpu-viewer/VKDDeviceBudgetSize.txt")
        budget = copyContentsFromFile("/tmp/gpu-viewer/VKDDeviceBudgetSize.txt")

        os.system(
            "cat /tmp/gpu-viewer/VKDMemoryHeap.txt | grep usage | grep -o  =.* | grep -o ' .*' | awk '{gsub(/\(.*/,'True');print}' > /tmp/gpu-viewer/VKDDeviceUsageSize.txt")
        usage = copyContentsFromFile("/tmp/gpu-viewer/VKDDeviceUsageSize.txt")

        HeapTab_Store.clear()
        TreeHeap.set_model(HeapTab_Store)
        for i in range(HCount-1):
            background_color = setBackgroundColor(i)
            HeapTab_Store.append(
                [i, getDeviceSize(size[i]),getDeviceSize(budget[i]),getDeviceSize(usage[i]), HEAP_DEVICE_LOCAL[i].strip('\n'), background_color, Heapfg[i]])

        labe13 = "Memory Heaps (%d)" %(HCount-1)
        MemoryNotebook.set_tab_label(MemoryHeapTab,Gtk.Label(labe13))
        label2 = "Memory Types (%d) & Memory Heaps (%d)" %(len(propertyFlags),(HCount-1))
        notebook.set_tab_label(MemoryTab,Gtk.Label(label2))


    def Queues(GPUname):

        #with open("/tmp/gpu-viewer/vulkaninfo.txt") as file1:
        #    for line in file1:
        #        if "VkQueueFamilyProperties[" in line:
        #            os.system(
        #                    "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceMemoryProperties:/{flag=0}flag'|awk '/VkQueue.*/{flag=1;}/VkPhysicalDeviceMemoryProperties:/{flag=0} flag' | awk '/./'> /tmp/gpu-viewer/VKDQueues.txt" % GPUname)
        #            break
        #        else:
        os.system(
                    "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceMemoryProperties:/{flag=0}flag'|awk '/VkQueue.*/{flag=1;next}/VkPhysicalDeviceMemoryProperties:/{flag=0} flag' | awk '/./'> /tmp/gpu-viewer/VKDQueues.txt" % GPUname)

        os.system(
            "cat /tmp/gpu-viewer/VKDQueues.txt | grep -o [=,:].* | grep -o ' .*' > /tmp/gpu-viewer/VKDQueueRHS.txt")
        os.system(
            "cat /tmp/gpu-viewer/VKDQueues.txt | awk '{gsub(/[=,:].*/,'True')l}1' | awk '/./' > /tmp/gpu-viewer/VKDQueueLHS.txt")
        os.system(
            "cat /tmp/gpu-viewer/VKDQueues.txt | grep Count | grep -o =.* | grep -o ' .*' > /tmp/gpu-viewer/VKDQueuecount.txt")

        # finding and storing the value for Flags


        qCount = copyContentsFromFile("/tmp/gpu-viewer/VKDQueuecount.txt")
        qLhs = copyContentsFromFile("/tmp/gpu-viewer/VKDQueueLHS.txt")
        qRhs = copyContentsFromFile("/tmp/gpu-viewer/VKDQueueRHS.txt")

        QueueTab_Store.clear()
        TreeQueue.set_model(QueueTab_Store)

        j = 0
        qRHS = []
        with open("/tmp/gpu-viewer/VKDQueues.txt") as file1:
            for line in file1:
                if " = " in line:
                    qRHS.append(qRhs[j])
                    j = j + 1
                if ":" in line or "---" in line:
                    qRHS.append(" ")
        k = 0
        for i in range(len(qLhs)):
            background_color = setBackgroundColor(k)
            if "true" in qRHS[i]:
                fColor = "GREEN"
            elif "false" in qRHS[i]:
                fColor = "RED"
            else:
                fColor = "BLACK"
            if "Properties" in qLhs[i]:
                iter1 = QueueTab_Store.append(None,[(qLhs[i].strip('\n')).strip('\t'),qRHS[i],Const.BGCOLOR3,fColor])
                k = 0
                continue
            if "---" in qLhs[i]:
                continue
            if "VK_" in qLhs[i] and "Properties" not in qLhs[i]:
                QueueTab_Store.append(iter2,[(qLhs[i].strip('\n')).strip('\t'),qRHS[i].strip('\n'),background_color,fColor])

            else :
                if "queueFlags" in qLhs[i]:
                    iter2 = QueueTab_Store.append(iter1,[(qLhs[i].strip('\n')).strip('\t')," ",setBackgroundColor(2),fColor])

                    if "GRAPHICS" in qRHS[i]:
                        QueueTab_Store.append(iter2,["GRAPHICS_BIT","true",setBackgroundColor(1),Const.COLOR1])
                    else:
                        QueueTab_Store.append(iter2,["GRAPHICS_BIT","false",setBackgroundColor(1),Const.COLOR2])
                    if "COMPUTE" in qRHS[i]:
                        QueueTab_Store.append(iter2,["COMPUTE_BIT","true",setBackgroundColor(2),Const.COLOR1])
                    else:
                        QueueTab_Store.append(iter2,["COMPUTE_BIT","false",setBackgroundColor(2),Const.COLOR2])
                    if "TRANSFER" in qRHS[i]:
                        QueueTab_Store.append(iter2,["TRANSFER_BIT","true",setBackgroundColor(1),Const.COLOR1])
                    else:
                        QueueTab_Store.append(iter2,["TRANSFER_BIT","false",setBackgroundColor(1),Const.COLOR2])
                    if "SPARSE" in qRHS[i]:
                        QueueTab_Store.append(iter2,["SPARSE_BINDING_BIT","true",setBackgroundColor(2),Const.COLOR1])
                    else:
                        QueueTab_Store.append(iter2,["SPARSE_BINDING_BIT","false",setBackgroundColor(2),Const.COLOR2])
                    if "PROTECTED" in qRHS[i]:
                        QueueTab_Store.append(iter2,["PROTECTED_BIT","true",setBackgroundColor(1),Const.COLOR1])
                    else:
                        QueueTab_Store.append(iter2,["PROTECTED_BIT","false",setBackgroundColor(1),Const.COLOR2])
                else:
                    k = k + 1
                    iter2 = QueueTab_Store.append(iter1,[(qLhs[i].strip('\n')).strip('\t'),qRHS[i].strip('\n'),background_color,fColor])
                    
            TreeQueue.expand_all()
        label = "Queues (%d)" % len(qCount)
        notebook.set_tab_label(QueueTab, Gtk.Label(label))

    def Instance():

        os.system(
            "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/Instance Extensions.*/{flag=1;next}/Layers:.*/{flag=0}flag'| grep VK_ | sort > /tmp/gpu-viewer/VKDInstanceExtensions1.txt")
        os.system(
            "cat /tmp/gpu-viewer/VKDInstanceExtensions1.txt | awk '{gsub(/:.*/,'True');print} ' > /tmp/gpu-viewer/VKDInstanceExtensions.txt")
        os.system(
            "cat /tmp/gpu-viewer/VKDInstanceExtensions1.txt | grep -o 'revision.*' | grep -o ' .*' > /tmp/gpu-viewer/VKDInstanceExtensionsRHS.txt")

        # This should take care of further versioning till RANGE1
        with open("/tmp/gpu-viewer/VKDInstanceExtensionsRHS.txt", "r") as file1:
            value = []
            for line in file1:
                text = line.strip('\n')
                value.append(getVulkanVersion(text))

        InstanceTab_Store.clear()

        with open("/tmp/gpu-viewer/VKDInstanceExtensions.txt", "r") as file1:
            count1 = len(file1.readlines())
            label = "Instance Extensions (%d)" % count1
            InstanceNotebook.set_tab_label(InstanceExtTab, Gtk.Label(label))
            file1.seek(0, 0)
            for i, line in enumerate(file1):
                text = line.strip('\t')
                background_color = setBackgroundColor(i)
                InstanceTab_Store.append([text.strip('\n'), value[i].strip('\n'), background_color])

        os.system(
            "cat /tmp/gpu-viewer/vulkaninfo.txt  | awk '/Layers:.*/{flag=1;next}/Presentable Surfaces.*/{flag=0}flag' > /tmp/gpu-viewer/VKDLayer1.txt")
        os.system(
            "cat /tmp/gpu-viewer/vulkaninfo.txt  | grep _LAYER_ | awk '{gsub(/\(.*/,'True');print} ' > /tmp/gpu-viewer/VKDLayer.txt")
        os.system(
            "cat /tmp/gpu-viewer/vulkaninfo.txt  | grep _LAYER_ | grep -o \(.* | awk '{gsub(/\).*/,'True');print}'| awk '{gsub(/\(/,'True');print}' > /tmp/gpu-viewer/VKDLayerDescription.txt")
        os.system(
            "cat /tmp/gpu-viewer/VKDLayer1.txt | grep ^VK | grep -o Vulkan.* | awk '{gsub(/,.*/,'True');print}' | grep -o version.* | grep -o ' .*' > /tmp/gpu-viewer/VKDVulkanVersion.txt")
        os.system(
            "cat /tmp/gpu-viewer/VKDLayer1.txt | grep ^VK | grep -o 'layer version.*' | awk '{gsub(/:.*/,'True');print}' | grep -o version.* | grep -o ' .*' > /tmp/gpu-viewer/VKDLayerVersion.txt")

        Vversion = copyContentsFromFile("/tmp/gpu-viewer/VKDVulkanVersion.txt")

        LVersion = copyContentsFromFile("/tmp/gpu-viewer/VKDLayerVersion.txt")


        ECount = []
        with open("/tmp/gpu-viewer/VKDLayer1.txt", "r") as file1:
            for line in file1:
                for j in range(RANGE1):
                    if "Layer Extensions: count = %d" % j in line:
                        ECount.append("%d" % j)
                        break

        layerDescription = copyContentsFromFile("/tmp/gpu-viewer/VKDLayerDescription.txt")
        LayerTab_Store.clear()

        count2 = len(LVersion)
        label = "Instances (%d) & Layers (%d)" % (count1, count2)
        label2 = "Instance Layers (%d)" % count2
        notebook.set_tab_label(InstanceTab, Gtk.Label(label))
        InstanceNotebook.set_tab_label(InstanceLayersTab, Gtk.Label(label2))
        with open("/tmp/gpu-viewer/VKDLayer.txt", "r") as file1:
            for i, line in enumerate(file1):
                background_color = setBackgroundColor(i)
                LayerTab_Store.append(
                    [line.strip('\n'), Vversion[i].strip('\n'), getVulkanVersion(LVersion[i]).strip('\n'),
                     ECount[i].strip('\n'), layerDescription[i].strip('\n'),
                     background_color])

    def Surface(GPU):

        os.system("cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/Presentable Surfaces:.*/{flag=1}/Device Properties and Extensions.*/{flag=0}flag' | awk '/Presentable Surfaces:.*/{flag=1;next}/Groups.*/{flag=0}flag'  | awk '/GPU id : %d/{flag=1;next}/GPU id : %d/{flag=0}flag' | awk '/./' > /tmp/gpu-viewer/VKDsurfaceType1.txt"%(GPU,GPU+1))
        

        os.system(
                "cat /tmp/gpu-viewer/VKDsurfaceType1.txt | grep -o [:,=].* | awk '{gsub(/=/,'True');print}' | grep -o ' .*' > /tmp/gpu-viewer/VKDsurface2.txt")

        os.system(
            "cat /tmp/gpu-viewer/VKDsurfaceType1.txt | awk '{gsub(/[=,:] .*/,'True');print}' | awk '{gsub(/count.*/,'True');print}' > /tmp/gpu-viewer/VKDsurface1.txt")

        valueRHS = copyContentsFromFile("/tmp/gpu-viewer/VKDsurface2.txt")
        valueLHS = copyContentsFromFile("/tmp/gpu-viewer/VKDsurface1.txt")
        SurfaceRHS = []
        i = 0

        Surface = []
        SurfaceTab_Store.clear()
        with open("/tmp/gpu-viewer/VKDsurfaceType1.txt", "r") as file1:
            j=0
            for i,line in enumerate(file1):
                background_color = setBackgroundColor(i)
                if "=" in line:
                    SurfaceRHS = valueRHS[j].strip('\n')
                    j = j+1
                else:
                    SurfaceRHS = " "
                if '---' in line:
                    continue
                if "types" in line or "Formats" in line or "Modes" in line or "VkSurface" in line :
                    background_color = Const.BGCOLOR3
                    iter1 = SurfaceTab_Store.append(None,[(valueLHS[i].strip('\n')).strip('\t'),SurfaceRHS.replace('count ',''),background_color])
                    continue
                if ':' in line and ("types" not in line or "Formats" not in line or "Modes" not in line or "VkSurface" not in line) :
                    iter2 = SurfaceTab_Store.append(iter1,[(valueLHS[i].strip('\n')).strip('\t'),SurfaceRHS.replace('count ',''),background_color])
                    continue
                if "VK_KHR" in line or "PRESENT_MODE" in line or "min" in line or "max" in line or "Transform" in line or "Protected" in line:
                    SurfaceTab_Store.append(iter1,[(valueLHS[i].strip('\n')).strip('\t'),SurfaceRHS.replace('count ',''),background_color])
                    continue
                else:
                    SurfaceTab_Store.append(iter2,[(valueLHS[i].strip('\n')).strip('\t'),SurfaceRHS.replace('count ',''),background_color])

            TreeSurface.expand_all()

    def searchFeaturesTree(model, iter, Tree):
        search_query = featureSearchEntry.get_text().lower()
        for i in range(Tree.get_n_columns()):
            value = model.get_value(iter, i).lower()
            if search_query in value:
                return True

    def searchExtensionTree(model, iter, Tree):
        search_query = extensionSearchEntry.get_text().lower()
        for i in range(Tree.get_n_columns()):
            value = model.get_value(iter, i).lower()
            if search_query in value:
                return True

    def searchLimitsTree(model, iter, Tree):
        search_query = limitsSearchEntry.get_text().lower()
        for i in range(Tree.get_n_columns()):
            value = model.get_value(iter, i).lower()
            if search_query in value:
                return True

    def searchFormatsTree(model, iter, Tree):
        search_query = formatSearchEntry.get_text().lower()
        for i in range(Tree.get_n_columns()):
            value = model.get_value(iter, i).lower()
            if search_query in value:
                return True

    def searchInstanceExtTree(model, iter, Tree):
        search_query = instanceSearchEntry.get_text().lower()
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

    def radcall(combo):

        text = combo.get_active()

        for i in range(len(list)):
            if text == i:
                Devices(text)
                Features(text)
                Limits(text)
                Extensions(text)
                Formats(text)
            #    t5 = threading.Thread(target=Formats, args=(text,))
            #    t5.start()
            #    t5.join()
                MemoryTypes(text)
            #    Heap(text)
                Queues(text)
                Surface(text)

                with open("/tmp/gpu-viewer/VKDDeviceinfo1.txt", "r") as file1:

                    for line in file1:
                        if "Intel" in line:
                            gpu_image = fetchImageFromUrl(Const.INTEL_LOGO_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
                            image_renderer.set_from_pixbuf(gpu_image)
                            break
                        elif "NVIDIA" in line or "GeForce" in line:
                            gpu_image = fetchImageFromUrl(Const.GTX_LOGO_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
                            image_renderer.set_from_pixbuf(gpu_image)
                            break
                        elif "AMD" in line or "ATI" in line:
                            gpu_image = fetchImageFromUrl(Const.AMD_LOGO_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
                            image_renderer.set_from_pixbuf(gpu_image)
                            break
                        elif "LLVM" in line:
                            image_renderer.clear()
                            gpu_image = fetchImageFromUrl(Const.LLVM_LOGO_SVG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
                            image_renderer.set_from_pixbuf(gpu_image)
                            break


            Instance()
        DevicesGrid.attach(image_renderer,50,1,1,1)
    #    os.system("rm /tmp/gpu-viewer/VKD*.txt")

    def selectProperties(Combo):
        property = Combo.get_active_text()

        if property is None:
            property = " "
        elif "Show All Properties" in property:
            os.system("cat /tmp/gpu-viewer/VKDDevicesparseinfo1.txt | awk '/./' > /tmp/gpu-viewer/filterProperties.txt")
        else:
            os.system(
                "cat /tmp/gpu-viewer/VKDDevicesparseinfo1.txt | awk '/^%s$/{flag=1;next}/Properties.*/{flag=0}flag' > /tmp/gpu-viewer/filterProperties.txt" % property)

        os.system(
            "cat /tmp/gpu-viewer/filterProperties.txt | awk '{gsub(/ =.*/,'True');}1' > /tmp/gpu-viewer/filterPropertiesLHS.txt")
        os.system(
            "cat /tmp/gpu-viewer/filterProperties.txt | grep -o =.* | grep -o ' .*' > /tmp/gpu-viewer/filterPropertiesRHS.txt")

        # fgColor, value = colorTrueFalse("/tmp/gpu-viewer/VKDDevicesparseinfo1.txt", "= 1")
        value = copyContentsFromFile("/tmp/gpu-viewer/filterPropertiesRHS.txt")

        value1 = []
        value2 = []
        fgColor = []
        i = 0
        with open("/tmp/gpu-viewer/filterProperties.txt", "r") as file1:
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
            if i == " false\n":
                value2.append("false")
                fgColor.append(Const.COLOR2)
            elif i == " true\n":
                value2.append("true")
                fgColor.append(Const.COLOR1)
            elif i == " false\n":
                value2.append(i)
                fgColor.append(Const.COLOR2)
            else:
                value2.append(i)
                fgColor.append("BLACK")

        SparseTab_Store.clear()
        TreeSparse.set_model(SparseTab_Store)

        if "Show All Properties" in property:
            k = 0;
            count = 0
            with open("/tmp/gpu-viewer/filterPropertiesLHS.txt", "r") as file1:
                for i, line in enumerate(file1):
                    text = line.strip('\t')
                    if "---" in line or "====" in line:
                        continue
                    if "Vk" in line and "conformanceVersion" not in line:
                        text1 = text
                        k = 0
                        count += 1
                        background_color = Const.BGCOLOR3
                        iter1 = SparseTab_Store.append(None, [(text1.strip('\n')).replace(" count",''), value2[i].strip('\n'), background_color,
                                                              fgColor[i]])
                    else:
                        background_color = setBackgroundColor(k)

                        #if "width" not in line and "height" not in line and "SUBGROUP" not in line and "RESOLVE" not in line and "SHADER_STAGE" not in line and "SAMPLE_COUNT" not in line and "\t\t" not in line:
                        if "\t\t" not in line:
                            iter2 = SparseTab_Store.append(iter1,
                                               [(text.strip('\n')).replace("count",''), value2[i].strip('\n'), background_color, fgColor[i]])
                        #if "width" in line or "height" in line or "SUBGROUP" in line or "RESOLVE" in line or "SHADER_STAGE" in line or "SAMPLE_COUNT" in line or "\t\t" in line:
                        if "\t\t" in line:
                            SparseTab_Store.append(iter2, [(text.strip('\n')).replace(" count",''), value2[i].strip('\n'), background_color,
                                                           fgColor[i]])
                        k += 1
                    TreeSparse.expand_all()
        else:
            k = 0;
            count = 0
            with open("/tmp/gpu-viewer/filterPropertiesLHS.txt", "r") as file1:
                for i, line in enumerate(file1):
                    text = line.strip('\t')
                    if "---" in line or "====" in line:
                        continue
                    else:
                        background_color = setBackgroundColor(k)
                        #if "width" not in line and "height" not in line and "SUBGROUP" not in line and "RESOLVE" not in line and "SHADER_STAGE" not in line:
                        if "\t\t" not in line:
                            iter2 = SparseTab_Store.append(None,
                                               [text.strip('\n'), value2[i].strip('\n'), background_color, fgColor[i]])
                        #if "width" in line or "height" in line or "SUBGROUP" in line or "RESOLVE" in line or "SHADER_STAGE" in line:
                        if "\t\t" in line:
                            SparseTab_Store.append(iter2, [text.strip('\n'), value2[i].strip('\n'), background_color,
                                                           fgColor[i]])
                        k += 1
                    TreeSparse.expand_all()

    def selectFeature(Combo):
        feature = Combo.get_active_text()
        if feature is None:
            feature = " "
        elif "Show All Features" in feature:
            os.system(
                "cat /tmp/gpu-viewer/VKDeviceFeatures.txt | awk '/==/{flag=1;next} flag' | awk '{sub(/^[ \t]+/, 'True'); print }' | grep = > /tmp/gpu-viewer/VKDFeatures1.txt")

        else:
            os.system(
                "cat /tmp/gpu-viewer/VKDeviceFeatures.txt | awk '/%s/{flag=1;next}/Vk*/{flag=0}flag' | awk '/--/{flag=1 ; next} flag' | grep = | sort > /tmp/gpu-viewer/VKDFeatures1.txt" % feature)

        os.system(
            "cat /tmp/gpu-viewer/VKDFeatures1.txt | awk '{sub(/^[ \t]+/, 'True'); print }' | awk '{gsub(/= true/,'True');print}' | awk '{gsub(/= false/,'False');print}' | awk '{sub(/[ \t]+$/, 'True'); print }' | awk '/./' | sort | uniq > /tmp/gpu-viewer/VKDFeatures.txt")

        value = []
        fgColor = []
        FeaturesTab_Store.clear()
        TreeFeatures.set_model(FeaturesTab_Store_filter)
        #fgColor, value = colorTrueFalse("/tmp/gpu-viewer/VKDFeatures1.txt", "= true")
        FeaturesLHS = copyContentsFromFile("/tmp/gpu-viewer/VKDFeatures.txt",)

        for i,LHS in enumerate(FeaturesLHS):
            with open("/tmp/gpu-viewer/VKDFeatures1.txt", "r") as file1:
                text = LHS.strip('\n')
                for line in file1:
                    if text in line:
                        if "= true" in line:
                            value.append('true')
                            fgColor.append(Const.COLOR1)
                            break
                        else :
                            value.append('false')
                            fgColor.append(Const.COLOR2)
                            break                        
                background_color = setBackgroundColor(i)
                FeaturesTab_Store.append([text.strip('\n'), value[i].strip('\n'), background_color, fgColor[i]])

    grid = Gtk.Grid()
    tab2.add(grid)
    DevicesFrame = Gtk.Frame()
    grid.add(DevicesFrame)

    notebook = Gtk.Notebook()
    notebook.set_property("scrollable", True)
    notebook.set_property("enable-popup", True)
    grid.attach(notebook, 0, 2, 1, 1)

    # ----------------Creating the Device Info Tab ------------

    DeviceTab = Gtk.Box(spacing=10)
    DeviceGrid = createSubTab(DeviceTab, notebook, "Device")

    DeviceTab_Store = Gtk.TreeStore(str, str, str)
    TreeDevice = Gtk.TreeView(DeviceTab_Store, expand=True)

    setColumns(TreeDevice, DeviceTitle, Const.MWIDTH, 0.0)

    DeviceScrollbar = createScrollbar(TreeDevice)
    DeviceGrid.add(DeviceScrollbar)

    propertiesTab = Gtk.Box(spacing=10)
    propertiesGrid = createSubTab(propertiesTab, notebook, "Properties")
    propertiesGrid.set_row_spacing(5)
    propertiesStore = Gtk.ListStore(str)
    propertiesCombo = Gtk.ComboBoxText()
    propertiesCombo.connect("changed", selectProperties)
    propertiesGrid.add(propertiesCombo)
    SparseTab_Store = Gtk.TreeStore(str, str, str, str)
    TreeSparse = Gtk.TreeView(SparseTab_Store, expand=True)
    TreeSparse.set_property("enable-tree-lines", True)
    TreeSparse.set_enable_search(True)
    TreeSparse.set_property("can-focus", False)
    for i, column_title in enumerate(SparseTitle):
        Sparserenderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(column_title, Sparserenderer, text=i)
        column.set_sort_column_id(i)
        column.set_resizable(True)
        column.set_reorderable(True)
        column.set_property("min-width", Const.MWIDTH)
        if i == 1:
            column.add_attribute(Sparserenderer, "foreground", 3)
        column.add_attribute(Sparserenderer, "background", 2)
        TreeSparse.append_column(column)

    propertiesScrollbar = createScrollbar(TreeSparse)
    propertiesGrid.attach_next_to(propertiesScrollbar, propertiesCombo, Gtk.PositionType.BOTTOM, 1, 1)

    # -----------------Creating the Features Tab-----------------

    FeatureTab = Gtk.Box(spacing=10)
    FeaturesGrid = createSubTab(FeatureTab, notebook, "Features")
    #   FeaturesGrid.set_row_spacing(3)

    FeaturesTab_Store = Gtk.ListStore(str, str, str, str)
    FeaturesTab_Store_filter = FeaturesTab_Store.filter_new()
    TreeFeatures = Gtk.TreeView(FeaturesTab_Store_filter, expand=True)
    TreeFeatures.set_enable_search(True)
    for i, column_title in enumerate(FeaturesTitle):
        Featurerenderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(column_title, Featurerenderer, text=i)
        column.set_sort_column_id(i)
        column.set_resizable(True)
        column.set_reorderable(True)
        if i == 1:
            column.add_attribute(Featurerenderer, "foreground", 3)
        column.add_attribute(Featurerenderer, "background", 2)
        column.set_property("min-width", MWIDTH)
        TreeFeatures.set_property("can-focus", False)
        TreeFeatures.append_column(column)

    featureCombo = Gtk.ComboBoxText()
    featureCombo.connect("changed", selectFeature)
    FeaturesGrid.add(featureCombo)
    featureFrameSearch = Gtk.Frame()
    featureSearchEntry = createSearchEntry(FeaturesTab_Store_filter)
    featureFrameSearch.add(featureSearchEntry)
    FeaturesGrid.attach_next_to(featureFrameSearch, featureCombo, Gtk.PositionType.BOTTOM, 1, 1)
    # FeaturesGrid.add(featureFrameSearch)
    FeatureScrollbar = createScrollbar(TreeFeatures)
    FeaturesGrid.attach_next_to(FeatureScrollbar, featureFrameSearch, Gtk.PositionType.BOTTOM, 1, 1)

    FeaturesTab_Store_filter.set_visible_func(searchFeaturesTree, data=TreeFeatures)

    # ------------ Creating the Limits Tab -------------------------------------------
    LimitsTab = Gtk.Box(spacing=10)
    LimitsGrid = createSubTab(LimitsTab, notebook, "Limits")
    LimitsGrid.set_row_spacing(3)

    LimitsTab_Store = Gtk.TreeStore(str, str, str)
    LimitsTab_Store_filter = LimitsTab_Store.filter_new()
    TreeLimits = Gtk.TreeView(LimitsTab_Store_filter, expand=True)
    TreeLimits.set_property("enable-tree-lines", True)
    TreeLimits.set_enable_search(True)

    setColumns(TreeLimits, LimitsTitle, Const.MWIDTH, 0.0)

    limitsFrameSearch = Gtk.Frame()
    limitsSearchEntry = createSearchEntry(LimitsTab_Store_filter)
    limitsFrameSearch.add(limitsSearchEntry)
    LimitsGrid.add(limitsFrameSearch)
    LimitsScrollbar = createScrollbar(TreeLimits)
    LimitsGrid.attach_next_to(LimitsScrollbar, limitsFrameSearch, Gtk.PositionType.BOTTOM, 1, 1)

    LimitsTab_Store_filter.set_visible_func(searchLimitsTree, data=TreeLimits)

    # ------------ Creating the Extensions Tab-------------------------------------------

    ExtensionTab = Gtk.Box(spacing=10)
    ExtensionGrid = createSubTab(ExtensionTab, notebook, "Extensions")
    ExtensionGrid.set_row_spacing(2)

    ExtensionTab_Store = Gtk.ListStore(str, str, str)
    ExtensionTab_store_filter = ExtensionTab_Store.filter_new()
    TreeExtension = Gtk.TreeView(ExtensionTab_store_filter, expand=True)

    setColumns(TreeExtension, ExtensionsTitle, Const.MWIDTH, 0.0)

    extensionFrameSearch = Gtk.Frame()
    extensionSearchEntry = createSearchEntry(ExtensionTab_store_filter)
    extensionFrameSearch.add(extensionSearchEntry)
    ExtensionGrid.add(extensionFrameSearch)
    ExtensionScrollbar = createScrollbar(TreeExtension)
    ExtensionGrid.attach_next_to(ExtensionScrollbar, extensionFrameSearch, Gtk.PositionType.BOTTOM, 1, 1)
    ExtensionTab_store_filter.set_visible_func(searchExtensionTree, data=TreeExtension)

    # ------------Creating the Formats Tab --------------------------------------------------

    FormatsTab = Gtk.Box(spacing=10)
    FormatsGrid = createSubTab(FormatsTab, notebook, "Formats")
    FormatsGrid.set_row_spacing(3)

    FormatsTab_Store = Gtk.TreeStore(str,str,str,str,str,str,str,str)
    FormatsTab_Store_filter = FormatsTab_Store.filter_new()
    TreeFormats = Gtk.TreeView(FormatsTab_Store_filter, expand=True)
    TreeFormats.set_property("enable-tree-lines", True)
    TreeFormats.set_enable_search(True)
    for i, column_title in enumerate(FormatsTitle):
        Formatsrenderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(column_title, Formatsrenderer, text=i)
        column.add_attribute(Formatsrenderer, "background", 4)
        column.set_resizable(True)
        column.set_reorderable(True)
    #    column.set_property("min-width", MWIDTH)
        if i == 0:
            column.set_property("min-width", 400)
        if i > 0 :
            column.set_property("min-width", 200)
        if i > 0 and i < 4:
            column.add_attribute(Formatsrenderer,"foreground",i+4)

        TreeFormats.append_column(column)

    formatSearchFrame = Gtk.Frame()
    formatSearchEntry = createSearchEntry(FormatsTab_Store_filter)
    formatSearchFrame.add(formatSearchEntry)
    FormatsGrid.add(formatSearchFrame)
    FormatsScrollbar = createScrollbar(TreeFormats)
    FormatsGrid.attach_next_to(FormatsScrollbar, formatSearchFrame, Gtk.PositionType.BOTTOM, 1, 1)

    FormatsTab_Store_filter.set_visible_func(searchFormatsTree, data=TreeFormats)

    # ------------------------Memory Types & Heaps----------------------------------------------

    MemoryTab = Gtk.Box(spacing=10)
    MemoryTab.set_orientation(1)
    MemoryGrid = createSubTab(MemoryTab, notebook, "Memory Types & Heaps")
    MemoryNotebook = Gtk.Notebook()
    MemoryGrid.add(MemoryNotebook)
    MemoryTypeTab = Gtk.Box(spacing=10)
    MemoryTypeGrid = createSubTab(MemoryTypeTab, MemoryNotebook, "Memory Types")
    MemoryTypeGrid.set_row_spacing(3)

    MemoryTab_Store = Gtk.TreeStore(str, str, str,str)
    TreeMemory = Gtk.TreeView(MemoryTab_Store, expand=True)
    TreeMemory.set_enable_search(True)
    TreeMemory.set_property("enable-tree-lines",True)

    for i, column_title in enumerate(MemoryTitle):
        Memoryrenderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(column_title, Memoryrenderer, text=i)
        column.add_attribute(Memoryrenderer, "background", 2)
        if i > 0:
            column.add_attribute(Memoryrenderer,"foreground",3)
        column.set_sort_column_id(i)
        column.set_resizable(True)
        column.set_reorderable(True)
        TreeMemory.set_property("can-focus", False)
        TreeMemory.append_column(column)

    MemoryScrollbar = createScrollbar(TreeMemory)
    MemoryTypeGrid.add(MemoryScrollbar)

    MemoryHeapTab = Gtk.Box(spacing=10)
    MemoryHeapGrid = createSubTab(MemoryHeapTab, MemoryNotebook, "Memory Heap")
    MemoryHeapGrid.set_row_spacing(3)
    #HeapGrid = Gtk.Box(spacing=10)

    HeapTab_Store = Gtk.ListStore(int, str, str, str, str,str,str)
    TreeHeap = Gtk.TreeView(HeapTab_Store, expand=True)
    TreeHeap.set_enable_search(True)
    for i, column_title in enumerate(HeapTitle):
        Heaprenderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(column_title, Heaprenderer, text=i)
        column.set_resizable(True)
        column.set_reorderable(True)
        column.set_sort_column_id(i)
        if i > 0 and i < 4:
            column.set_property("min-width", 150)
        column.add_attribute(Heaprenderer, "background", 5)
        if i == 4:
            column.add_attribute(Heaprenderer, "foreground", 6)
        TreeHeap.set_property("can-focus", False)
        TreeHeap.append_column(column)

    HeapScrollbar = createScrollbar(TreeHeap)
    MemoryHeapGrid.add(HeapScrollbar)

    # -------------------------Creating the Queues Tab -----------------------------------------------------

    QueueTab = Gtk.Box(spacing=10)
    QueueGrid = createSubTab(QueueTab, notebook, "Queue")

    QueueTab_Store = Gtk.TreeStore(str, str, str, str)
    TreeQueue = Gtk.TreeView(QueueTab_Store, expand=True)
    TreeQueue.set_enable_search(True)
    TreeQueue.set_property("enable-tree-lines", True)
    for i, column_title in enumerate(QueueTitle):
        Queuerenderer = Gtk.CellRendererText()
#        Queuerenderer.set_alignment(0.5, 0.5)
        column = Gtk.TreeViewColumn(column_title, Queuerenderer, text=i)
#        column.set_alignment(0.5)
        column.add_attribute(Queuerenderer, "background", 2)
        column.set_sort_column_id(i)
        column.set_resizable(True)
        column.set_reorderable(True)
        if i > 0:
            column.add_attribute(Queuerenderer, "foreground", 3)
        TreeQueue.set_property("can-focus", False)
        TreeQueue.append_column(column)

    QueueScrollbar = createScrollbar(TreeQueue)
    QueueGrid.add(QueueScrollbar)

    # -------------------------Creating the Instances & Layers ---------------------------------------------

    InstanceTab = Gtk.Box(spacing=10)
    InstanceGrid = createSubTab(InstanceTab, notebook, "Instances & layers")
    InstanceNotebook = Gtk.Notebook()
    InstanceGrid.add(InstanceNotebook)
    InstanceExtTab = Gtk.Box(spacing=10)
    InstanceExtGrid = createSubTab(InstanceExtTab, InstanceNotebook, "Instance Extensions")
    InstanceExtGrid.set_row_spacing(3)

    InstanceTab_Store = Gtk.ListStore(str, str, str)
    InstanceTab_Store_filter = InstanceTab_Store.filter_new()
    TreeInstance = Gtk.TreeView(InstanceTab_Store_filter, expand=True)
    TreeInstance.set_enable_search(True)

    setColumns(TreeInstance, InstanceTitle, 300, 0.0)

    instanceSearchFrame = Gtk.Frame()
    instanceSearchEntry = createSearchEntry(InstanceTab_Store_filter)
    instanceSearchFrame.add(instanceSearchEntry)
    InstanceExtGrid.add(instanceSearchFrame)
    InstanceScrollbar = createScrollbar(TreeInstance)
    InstanceExtGrid.attach_next_to(InstanceScrollbar, instanceSearchFrame, Gtk.PositionType.BOTTOM, 1, 1)

    InstanceTab_Store_filter.set_visible_func(searchInstanceExtTree, data=TreeInstance)

    InstanceLayersTab = Gtk.Box(spacing=10)
    InstanceLayersGrid = createSubTab(InstanceLayersTab, InstanceNotebook, "Instance Layers")
    InstanceLayersGrid.set_row_spacing(3)

    LayerTab_Store = Gtk.ListStore(str, str, str, str, str, str)
    LayerTab_Store_filter = LayerTab_Store.filter_new()
    TreeLayer = Gtk.TreeView(LayerTab_Store_filter, expand=True)
    TreeLayer.set_enable_search(TreeLayer)

    setColumns(TreeLayer, LayerTitle, 100, 0.0)

    layerSearchFrame = Gtk.Frame()
    layerSearchEntry = createSearchEntry(LayerTab_Store_filter)
    layerSearchFrame.add(layerSearchEntry)
    InstanceLayersGrid.add(layerSearchFrame)
    LayerScrollbar = createScrollbar(TreeLayer)
    InstanceLayersGrid.attach_next_to(LayerScrollbar, layerSearchFrame, Gtk.PositionType.BOTTOM, 1, 1)

    LayerTab_Store_filter.set_visible_func(searchInstanceLayersTree, data=TreeLayer)

    # ------------------ Creating the Surface Tab --------------------------------------------------

    SurfaceTab = Gtk.Box(spacing=10)
    SurfaceGrid = createSubTab(SurfaceTab, notebook, "Surface")
    #SurfaceCombo = Gtk.ComboBoxText()
    SurfaceTypeList = Gtk.ListStore(str)
    #SurfaceCombo.connect("changed", selectSurfaceType)
    #SurfaceGrid.add(SurfaceCombo)
    SurfaceTab_Store = Gtk.TreeStore(str, str, str)
    TreeSurface = Gtk.TreeView(SurfaceTab_Store, expand=True)
    TreeSurface.set_property("enable-tree-lines", True)
    with open("/tmp/gpu-viewer/vulkaninfo.txt", "r") as file1:
        for line in file1:
            if "VkSurfaceCapabilities" in line:

                for i, column_title in enumerate(SurfaceTitle):
                    Surfacerenderer = Gtk.CellRendererText()
                    column = Gtk.TreeViewColumn(column_title, Surfacerenderer, text=i)
                    column.add_attribute(Surfacerenderer, "background", 2)
                    column.set_property("min-width", MWIDTH)
                    TreeSurface.set_property("can-focus", False)
                    TreeSurface.append_column(column)

                SurfaceScrollbar = createScrollbar(TreeSurface)
                SurfaceGrid.add(SurfaceScrollbar)
                break

    DevicesGrid = Gtk.Grid()
    DevicesGrid.set_border_width(20)
    DevicesGrid.set_column_spacing(40)
    DevicesFrame.add(DevicesGrid)

    #    grid.set_row_spacing(10)
    os.system("cat /tmp/gpu-viewer/vulkaninfo.txt | grep deviceName | grep -o  =.* | grep -o ' .*' > /tmp/gpu-viewer/GPU.txt")

    list = copyContentsFromFile("/tmp/gpu-viewer/GPU.txt")

    list = [i.strip('\n ') for i in list]

    DS = Gtk.Label()
    gpu_image = Gtk.Image()
    DS.set_text("Available Device(s) :")
    DevicesGrid.attach(DS, 0, 1, 1, 1)
    gpu_image = GdkPixbuf.Pixbuf.new_from_file_at_size(Const.APP_LOGO_PNG, 50, 50)
    image_renderer = Gtk.Image.new_from_pixbuf(gpu_image)
    gpu_store = Gtk.ListStore(str)
    for i in list:
        gpu_store.append([i])

    gpu_combo = Gtk.ComboBox.new_with_model(gpu_store)
    gpu_combo.connect("changed", radcall)
    renderer_text = Gtk.CellRendererText(font="BOLD")
    #   gpu_combo.set_property("has-frame", False)
    gpu_combo.pack_start(renderer_text, True)
    gpu_combo.add_attribute(renderer_text, "text", 0)
    gpu_combo.set_entry_text_column(0)
    gpu_combo.set_active(0)




    DevicesGrid.attach_next_to(gpu_combo, DS, Gtk.PositionType.RIGHT, 20, 1)

    # Logos

    tab2.show_all()

def createSearchEntry(ExtensionTab_store_filter):
    Extensionentry = Gtk.SearchEntry()
    Extensionentry.set_placeholder_text("Type here to filter.....")
    Extensionentry.connect("search-changed", refresh_filter, ExtensionTab_store_filter)
    return Extensionentry

