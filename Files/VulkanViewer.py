import os

import gi

import Const

import threading

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf
# noinspection PyPep8
from Common import copyContentsFromFile, setBackgroundColor, setColumns, createSubTab, createScrollbar, createSubFrame, \
    colorTrueFalse, getDriverVersion, getVulkanVersion, getDeviceSize, refresh_filter, getRamInGb, fetchImageFromUrl

MWIDTH = 300

RANGE1 = 100

DeviceTitle = ["Device Information", "Details"]
SparseTitle = ["Device Properties", "Value"]
FeaturesTitle = ["Device Features", "Value"]
LimitsTitle = ["Device Limits", "Value"]
ExtensionsTitle = ["Device Extensions", "Version"]
FormatsTitle = ["Device Formats", "Linear", "Optimal", "Buffer"]
MemoryTitle = ["Memory Types", "Heap Index", "Device Local", "Host Visible", "Host Coherent", "Host Cached",
               "Lazily Allocated"]
HeapTitle = ["Memory Heaps", "Device Size", "HEAP DEVICE LOCAL"]
QueueTitle = ["Queue Family", "Queue Count", "timestampValidBits", "GRAPHICS BIT", "COMPUTE BIT", "TRANSFER BIT",
              "SPARSE BINDING BIT", "minImageTransferGranularity.width", "minImageTransferGranularity.height",
              "minImageTransferGranularity.depth"]
InstanceTitle = ["Extensions", "Version"]
LayerTitle = ["Layers", "Vulkan Version", "Layer Version", "Extension Count", "Description"]
SurfaceTitle = ["Surface Capabilities", "Value"]

def Vulkan(tab2):
    # Creating Tabs for different Features

    # Creating Feature Tab
    def Devices(GPUname):

        for i in range(len(list)):
            if GPUname == i:
                # noinspection PyPep8
                os.system(
                    "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceLimits:/{flag=0}flag' | awk '/==.*/{flag=1;next}flag' | grep -v Version > /tmp/gpu-viewer/VKDDeviceinfo1.txt" % i)
                # noinspection PyPep8
                os.system(
                    "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceLimits:/{flag=0}flag' | awk '/==.*/{flag=1;next}flag' | grep Version | awk '{gsub(/\(.*/,'True');}1' >> /tmp/gpu-viewer/VKDDeviceinfo1.txt" % i)
                break

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
        headValues = ['GPU','CPU','MEMORY']


        try:
            os.system("lsb_release -d -r -c > /tmp/gpu-viewer/VKDLsbRelease.txt")
            os.system("cat /tmp/gpu-viewer/VKDLsbRelease.txt | grep -o :.* >> /tmp/gpu-viewer/VKDDeviceinfo2.txt")
            # noinspection PyPep8
            os.system(
                "cat /tmp/gpu-viewer/VKDLsbRelease.txt | awk '{gsub(/:.*/,'True');}1' > /tmp/gpu-viewer/VKDLsbReleaseLHS.txt")
            os.system("uname -r >> /tmp/gpu-viewer/VKDDeviceinfo2.txt")
            valueLHS = valueLHS + copyContentsFromFile("/tmp/gpu-viewer/VKDLsbReleaseLHS.txt")
            valueLHS.append("Kernel")
            headValues.append("DISTRIBUTION")
        except Exception as e:
            raise e
        # Storing the RHS values into a list

        valueRHS = copyContentsFromFile("/tmp/gpu-viewer/VKDDeviceinfo2.txt")

        for i in range(len(valueRHS)):
            if "0x" in valueRHS[i]:
                valueRHS[i] = int(valueRHS[i], 16)
                valueRHS[i] = str("%d" % valueRHS[i])

        valueRHS[0] = getVulkanVersion(valueRHS[0])
        valueRHS[4] = getDriverVersion(valueRHS)


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
            if "Description" in valueLHS[i]:
                DeviceTab_Store.append(["operatingSystem", valueRHS[i].strip('\n'), background_color])
            elif "Mem" in valueLHS[i]:
                DeviceTab_Store.append([valueLHS[i].strip('\n'), getRamInGb(valueRHS[i]), background_color])
            else:
                DeviceTab_Store.append([valueLHS[i].strip('\n'), valueRHS[i].strip('\n'), background_color])

        for i in range(len(list)):
            if GPUname == i:
                # noinspection PyPep8
                os.system(
                    "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Extensions.*/{flag=0}flag' | awk '/VkPhysicalDeviceSparseProperties:/{flag=1}/Device Extensions.*/{flag=0}flag' | awk '/./' > /tmp/gpu-viewer/VKDDevicesparseinfo1.txt" % i)

        propertiesCombo.remove_all()
        with open("/tmp/gpu-viewer/VKDDevicesparseinfo1.txt", "r") as file1:
            for i, line in enumerate(file1):
                if "Vk" in line:
                    text1 = line.strip("\t")
                    text = text1[:-2]
                    propertiesCombo.append_text(text.strip("\n"))

        propertiesCombo.insert_text(0, "Show All Properties")
        propertiesCombo.set_active(0)

    #    notebook.set_tab_label(propertiesTab,Gtk.Label(label))

    def Features(GPUname):

        for i in range(len(list)):
            if GPUname == i:
                # noinspection PyPep8
                os.system(
                    "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Format Properties:/{flag=0}flag' | awk '/VkPhysicalDeviceFeatures:/{flag=1; next}/Format Properties:/{flag=0}flag' | awk '/==/{flag=1 ; next} flag' | grep = | sort > /tmp/gpu-viewer/VKDFeatures1.txt" % i)
                # noinspection PyPep8
                os.system(
                    "cat /tmp/gpu-viewer/vulkaninfo.txt |  awk '/GPU%d/{flag=1;next}/Format Properties:/{flag=0}flag' | awk '/VkPhysicalDeviceFeatures:/{flag=1}/Format Properties:/{flag=0}flag' > /tmp/gpu-viewer/VKDeviceFeatures.txt" % i)
                break
        featureCombo.remove_all()
        with open("/tmp/gpu-viewer/VKDeviceFeatures.txt", "r") as file:
            for line in file:
                if "Vk" in line:
                    text = line[:-2]
                    featureCombo.append_text(text.strip("\n"))

        featureCombo.insert_text(0, "Show All Features")
        featureCombo.set_active(0)

    def Limits(GPUname):

        for i in range(len(list)):
            if GPUname == i:
                # noinspection PyPep8
                os.system(
                    "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceSparseProperties:/{flag=0}flag'| awk '/--/{flag=1 ; next} flag' | sort > /tmp/gpu-viewer/VKDlimits1.txt" % i)
                break
        os.system("cat /tmp/gpu-viewer/VKDlimits1.txt | awk '{gsub(/=.*/,'True');}1' > /tmp/gpu-viewer/VKDlimits.txt")
        os.system(
            "cat /tmp/gpu-viewer/VKDlimits1.txt | grep -o '=.*' | grep -o '[ -].*' > /tmp/gpu-viewer/VKDlimits2.txt")

        value = copyContentsFromFile("/tmp/gpu-viewer/VKDlimits2.txt")

        # finding and converting any hexadecimal value to decimal

        for i in range(len(value)):
            if "0x" in value[i]:
                value[i] = str(int(value[i], 16))

        LimitsTab_Store.clear()
        TreeLimits.set_model(LimitsTab_Store_filter)

        value = [i.strip(' ') for i in value]
        with open("/tmp/gpu-viewer/VKDlimits.txt", "r") as file1:
            for i, line in enumerate(file1):
                text = line.strip('\t')
                background_color = setBackgroundColor(i)
                LimitsTab_Store.append([text.strip('\n'), value[i].strip('\n'), background_color])

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

        for i in range(len(list)):
            if GPUname == i:
                # noinspection PyPep8
                os.system(
                    "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | grep ^FORMAT_ | grep -o _.* | grep -o [a-zA-Z].* | awk '{gsub(/:.*/,'True');print} ' > /tmp/gpu-viewer/VKDFORMATS.txt" % i)
                # noinspection PyPep8
                os.system(
                    "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /linearTiling.*/{f=1}'> /tmp/gpu-viewer/VKDFORMATSlinear.txt" % i)
                # noinspection PyPep8
                os.system(
                    "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /optimalTiling.*/{f=1}'> /tmp/gpu-viewer/VKDFORMATSoptimal.txt" % i)
                # noinspection PyPep8
                os.system(
                    "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /bufferFeatures.*/{f=1}'> /tmp/gpu-viewer/VKDFORMATSBuffer.txt" % i)
                break

        # Linear values

        linearfg, linear = colorTrueFalse("/tmp/gpu-viewer/VKDFORMATSlinear.txt", "VK")

        # Optimal Values
        optimalfg, optimal = colorTrueFalse("/tmp/gpu-viewer/VKDFORMATSoptimal.txt", "VK")

        # Buffer Values
        Bufferfg, Buffer = colorTrueFalse("/tmp/gpu-viewer/VKDFORMATSBuffer.txt", "VK")

        count = len(linear)
        trueFormats = []
        # counting the number of formats supported
        Formats = 0
        for i in range(count):
            if linear[i] == "true" or optimal[i] == "true" or Buffer[i] == "true":
                Formats = Formats + 1
                trueFormats.append(True)
            else:
                trueFormats.append(False)

        label = "Formats (%d)" % Formats
        notebook.set_tab_label(FormatsTab, Gtk.Label(label))

        Format = []
        with open("/tmp/gpu-viewer/VKDFORMATS.txt", "r") as file1:
            for line in file1:
                Format.append(line.strip('\n'))

        Format.append("BLANK")

        FormatsTab_Store.clear()

        for i in range(len(Format) - 1):
            background_color = setBackgroundColor(i)
            iter = FormatsTab_Store.append(None,
                                           [Format[i], linear[i].strip('\n'), optimal[i].strip('\n'),
                                            Buffer[i].strip('\n'), background_color, linearfg[i], optimalfg[i],
                                            Bufferfg[i]])
            j = i
            if trueFormats[i]:
                # noinspection PyPep8
                os.system(
                    "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk '/FORMAT_%s*/{flag=1; next}/FORMAT_%s*/{flag=0} flag' | awk '/./' > /tmp/gpu-viewer/VKDTiling.txt" % (
                        GPUname, Format[j], Format[j + 1]))
                with open("/tmp/gpu-viewer/VKDTiling.txt", "r") as file1:
                    k = 0
                    z = 0
                    j = 1
                    value = 0
                    for line in file1:
                        background_color = setBackgroundColor(k)
                        if "linear" in line:
                            value = value + 1
                        if value <= 1:
                            if ":" in line:
                                text1 = line[:-2]
                                background_color = setBackgroundColor(z)
                                text = text1.strip('\t')
                                iter2 = FormatsTab_Store.append(iter,
                                                                [text.strip('\n'), " ", " ", " ", background_color,
                                                                 Const.BGCOLOR1, Const.BGCOLOR1, Const.BGCOLOR1])
                                k = 1
                                z += 1
                            else:
                                background_color = setBackgroundColor(j)
                                text = line.strip('\t')
                                FormatsTab_Store.append(iter2, [text.strip('\n'), " ", " ", " ", background_color,
                                                                Const.BGCOLOR1, Const.BGCOLOR1, Const.BGCOLOR1])
                                j += 1
                            k += 1

    def MemoryTypes(GPUname):
        # propertiesGrid.add(propertiesCombo)ame):

        for i in range(len(list)):
            if GPUname == i:
                # noinspection PyPep8
                os.system(
                    "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceFeatures:/{flag=0}flag'|awk '/VkPhysicalDeviceMemoryProperties:/{flag=1; next}/VkPhysicalDeviceFeatures:/{flag=0} flag' > /tmp/gpu-viewer/VKDMemoryType.txt" % i)
                break

        with open("/tmp/gpu-viewer/VKDMemoryType.txt", "r") as file1:
            heapIndex = []
            for line in file1:
                for j in range(RANGE1):
                    if "heapIndex" in line:
                        if "= %d" % j in line:
                            heapIndex.append(j)
                            break

        Device_Local = []
        Host_Visible = []
        Host_Coherent = []
        Host_Cached = []
        Lazily_Allocated = []
        Flags = []
        LAfg = []
        HCAfg = []
        HCOfg = []
        HVfg = []
        DLfg = []

        # noinspection PyPep8
        os.system(
            "cat /tmp/gpu-viewer/VKDMemoryType.txt | grep propertyFlags | grep -o  =.* | grep -o ' .*' | awk '{gsub(/:.*/,'True');print}' > /tmp/gpu-viewer/VKDMemoryPropertyFlags.txt")
        propertyFlags = copyContentsFromFile("/tmp/gpu-viewer/VKDMemoryPropertyFlags.txt")

        for i in propertyFlags:
            dec = int(i, 16)
            binary = bin(dec)[2:]
            for j in range(len(binary)):
                if binary[j] == '0':
                    Flags.insert(j, "false")
                if binary[j] == '1':
                    Flags.insert(j, "true")
            for j in range(5 - len(binary)):
                Flags.insert(0, "false")
            for k in range(len(Flags)):
                if k == 0:
                    Lazily_Allocated.append(Flags[k])
                    if Flags[k] == "false":
                        LAfg.append(Const.COLOR2)
                    else:
                        LAfg.append(Const.COLOR1)
                elif k == 1:
                    Host_Cached.append(Flags[k])
                    if Flags[k] == "false":
                        HCAfg.append(Const.COLOR2)
                    else:
                        HCAfg.append(Const.COLOR1)
                elif k == 2:
                    Host_Coherent.append(Flags[k])
                    if Flags[k] == "false":
                        HCOfg.append(Const.COLOR2)
                    else:
                        HCOfg.append(Const.COLOR1)
                elif k == 3:
                    Host_Visible.append(Flags[k])
                    if Flags[k] == "false":
                        HVfg.append(Const.COLOR2)
                    else:
                        HVfg.append(Const.COLOR1)
                elif k == 4:
                    Device_Local.append(Flags[k])
                    if Flags[k] == "false":
                        DLfg.append(Const.COLOR2)
                    else:
                        DLfg.append(Const.COLOR1)

        MemoryTab_Store.clear()
        TreeMemory.set_model(MemoryTab_Store)
        for i in range(len(propertyFlags)):
            background_color = setBackgroundColor(i)
            MemoryTab_Store.append([i, heapIndex[i], Device_Local[i].strip('\n'), Host_Visible[i].strip('\n'),
                                    Host_Coherent[i].strip('\n'), Host_Cached[i].strip('\n'),
                                    Lazily_Allocated[i].strip('\n'), background_color, DLfg[i], HVfg[i], HCOfg[i],
                                    HCAfg[i], LAfg[i]])

        HCount = 0
        HEAP_DEVICE_LOCAL = []

        with open("/tmp/gpu-viewer/VKDMemoryType.txt", "r") as file1:
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
            "cat /tmp/gpu-viewer/VKDMemoryType.txt | grep size | grep -o  =.* | grep -o ' .*' | awk '{gsub(/\(.*/,'True');print}' > /tmp/gpu-viewer/VKDDeviceSize.txt")
        size = copyContentsFromFile("/tmp/gpu-viewer/VKDDeviceSize.txt")

        HeapTab_Store.clear()
        TreeHeap.set_model(HeapTab_Store)

        for i in range(HCount):
            background_color = setBackgroundColor(i)
            HeapTab_Store.append(
                [i, getDeviceSize(size[i]), HEAP_DEVICE_LOCAL[i].strip('\n'), background_color, Heapfg[i]])

        label = "Memory Types (%d) & Heaps (%d)" % (len(propertyFlags), HCount)
        notebook.set_tab_label(MemoryTab, Gtk.Label(label))

    def Queues(GPUname):

        for i in range(len(list)):
            if GPUname == i:
                os.system(
                    "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceMemoryProperties:/{flag=0}flag'|awk '/VkQueue.*/{flag=1; next}/VkPhysicalDeviceMemoryProperties:/{flag=0} flag' > /tmp/gpu-viewer/VKDQueues.txt" % i)
                break

        os.system(
            "cat /tmp/gpu-viewer/VKDQueues.txt | grep Count | grep -o =.* | grep -o ' .*' > /tmp/gpu-viewer/VKDQueuecount.txt")
        os.system(
            "cat /tmp/gpu-viewer/VKDQueues.txt | grep times | grep -o =.* | grep -o ' .*' > /tmp/gpu-viewer/VKDQueuebits.txt")
        os.system(
            "cat /tmp/gpu-viewer/VKDQueues.txt | grep Flags | grep -o =.* | grep -o ' .*' > /tmp/gpu-viewer/VKDQueueFlags.txt")

        width = []
        height = []
        depth = []

        with open("/tmp/gpu-viewer/VKDQueues.txt", "r") as file1:
            for line in file1:
                for i in range(10):
                    for j in range(10):
                        for k in range(10):
                            if "(%d, %d, %d)" % (i, j, k) in line:
                                width.append("%d" % i)
                                height.append("%d" % j)
                                depth.append("%d" % k)
                                break

        # finding and storing the value for Flags
        Gfg, GBit = colorTrueFalse("/tmp/gpu-viewer/VKDQueueFlags.txt", "GRAPHICS")
        Cfg, CBit = colorTrueFalse("/tmp/gpu-viewer/VKDQueueFlags.txt", "COMPUTE")
        Tfg, TBit = colorTrueFalse("/tmp/gpu-viewer/VKDQueueFlags.txt", "TRANSFER")
        Sfg, SBit = colorTrueFalse("/tmp/gpu-viewer/VKDQueueFlags.txt", "SPARSE")

        qCount = copyContentsFromFile("/tmp/gpu-viewer/VKDQueuecount.txt")

        qBits = copyContentsFromFile("/tmp/gpu-viewer/VKDQueuebits.txt")

        QueueTab_Store.clear()
        TreeQueue.set_model(QueueTab_Store)
        for i in range(len(qCount)):
            background_color = setBackgroundColor(i)
            QueueTab_Store.append(
                [i, int(qCount[i]), int(qBits[i]), GBit[i], CBit[i], TBit[i], SBit[i], width[i], height[i], depth[i],
                 background_color, Gfg[i], Cfg[i], Tfg[i], Sfg[i]])
        label = "Queues (%d)" % len(qCount)
        notebook.set_tab_label(QueueTab, Gtk.Label(label))

    def Instance():

        os.system(
            "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/Instance Extensions	count.*/{flag=1;next}/Layers: count.*/{flag=0}flag'| grep VK_ | sort > /tmp/gpu-viewer/VKDInstanceExtensions1.txt")
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
            "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/Layers: count.*/{flag=1;next}/Presentable Surfaces.*/{flag=0}flag' > /tmp/gpu-viewer/VKDLayer1.txt")
        os.system(
            "cat /tmp/gpu-viewer/VKDLayer1.txt | grep _LAYER_ | awk '{gsub(/\(.*/,'True');print} ' > /tmp/gpu-viewer/VKDLayer.txt")
        os.system(
            "cat /tmp/gpu-viewer/VKDLayer1.txt | grep _LAYER_ | grep -o \(.* | awk '{gsub(/\).*/,'True');print}'| awk '{gsub(/\(/,'True');print}' > /tmp/gpu-viewer/VKDLayerDescription.txt")
        os.system(
            "cat /tmp/gpu-viewer/VKDLayer1.txt | grep ^VK | grep -o Vulkan.* | awk '{gsub(/,.*/,'True');print}' | grep -o version.* | grep -o ' .*' > /tmp/gpu-viewer/VKDVulkanVersion.txt")
        os.system(
            "cat /tmp/gpu-viewer/VKDLayer1.txt | grep ^VK | grep -o layer.* | awk '{gsub(/,.*/,'True');print}' | grep -o version.* | grep -o ' .*' > /tmp/gpu-viewer/VKDLayerVersion.txt")

        Vversion = copyContentsFromFile("/tmp/gpu-viewer/VKDVulkanVersion.txt")

        LVersion = copyContentsFromFile("/tmp/gpu-viewer/VKDLayerVersion.txt")

        ECount = []
        with open("/tmp/gpu-viewer/VKDLayer1.txt", "r") as file1:
            for line in file1:
                for j in range(RANGE1):
                    if "Layer Extensions	count = %d" % j in line:
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

    def Surface(GPUname):

        for GPU in range(len(list)):
            if GPUname == GPU:
                os.system(
                    "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/Presentable Surfaces.*/{flag=1}/Device Properties and Extensions.*/{flag=0}flag' | awk '/Presentable Surfaces.*/{flag=1;next}/Groups.*/{flag=0}flag'  | awk '/GPU id       : %d.*/{flag=1;next}/GPU id */{flag=0}flag'| awk '/./'> /tmp/gpu-viewer/VKDsurface.txt" % (
                        GPU))
            #    os.system(
            #        "cat /tmp/gpu-viewer/vulkaninfo.txt | awk '/Presentable Surfaces.*/{flag=1;next}/Device Properties and Extensions.*/{flag=0}flag' | awk '/GPU id       : %d.*/{flag=1;next}/VkSurfaceCapabilities.*/{flag=0}flag' | awk '{gsub(/count/,'True');print}' | awk '/./'  >> /tmp/gpu-viewer/VKDsurface.txt" % GPU)

        os.system(
            "cat /tmp/gpu-viewer/VKDsurface.txt | awk '{gsub(/[=,:] .*/,'True');print} ' > /tmp/gpu-viewer/VKDsurface1.txt")
        os.system("cat /tmp/gpu-viewer/VKDsurface.txt | grep -o [:,=].* | awk '{gsub(/=/,'True');print}' | grep -o ' .*' > /tmp/gpu-viewer/VKDsurface2.txt")

        temp = copyContentsFromFile("/tmp/gpu-viewer/VKDsurface2.txt")
        SurfaceRHS = []
        i = 0
        with open("/tmp/gpu-viewer/VKDsurface.txt", "r") as file1:
            for line in file1:
                if "= " in line or "type" in line:
                    SurfaceRHS.append(temp[i])
                    i = i + 1
                else:
                    SurfaceRHS.append(" ")

        Surface = []
        with open("/tmp/gpu-viewer/VKDsurface1.txt", "r") as file1:
            for line in file1:
                Surface.append(line)

        Surface = [i.strip('\n ') for i in Surface]
        SurfaceTab_Store.clear()
        count = 0
        TreeSurface.set_model(SurfaceTab_Store)
        for i in range(len(Surface)):
            TreeSurface.expand_all()
            if "====" in Surface[i]:
                continue
            background_color = setBackgroundColor(i)
            if "VkSurfaceCapabilities" in Surface[i] or "Formats" in Surface[i] or "Present" in Surface[i] or "type" in Surface[i]:
                background_color = Const.BGCOLOR3
                if "type" in Surface[i]:
                    background_color = setBackgroundColor(i)
                text1 = Surface[i].strip('\t')
                text = text1.strip(":")
                count = 0
                iter1 = SurfaceTab_Store.append(None, [text, SurfaceRHS[i].strip('\n'), background_color])
            else:
                if ":" in Surface[i] or "ArrayLayers" in Surface[i]:
                    count += 1
                    text1 = Surface[i].strip('\t')
                    text = text1.strip(":")
                    iter2 = SurfaceTab_Store.append(iter1, [text, SurfaceRHS[i].strip('\n'), background_color])
                    continue
                if count > 0:
                    text = Surface[i].strip('\t')
                    SurfaceTab_Store.append(iter2, [text, SurfaceRHS[i].strip('\n'), background_color])
                else:
                    text = Surface[i].strip('\t')
                    SurfaceTab_Store.append(iter1, [text, SurfaceRHS[i].strip('\n'), background_color])
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
                t5 = threading.Thread(target=Formats, args=(text,))
                t5.start()
                t5.join()
                MemoryTypes(text)
                Queues(text)
                Surface(text)

                with open("/tmp/gpu-viewer/VKDDeviceinfo1.txt", "r") as file1:

                    for line in file1:
                        if "Intel" in line:
                            gpu_image = fetchImageFromUrl(Const.INTEL_LOGO_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
                            image_renderer.set_from_pixbuf(gpu_image)
                            break
                        elif "NVIDIA" in line or "GeForce" in line:
                            gpu_image = fetchImageFromUrl(Const.NVIDIA_LOGO_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
                            image_renderer.set_from_pixbuf(gpu_image)
                            break
                        elif "AMD" in line or "ATI" in line:
                            gpu_image = fetchImageFromUrl(Const.AMD_LOGO_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
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
                "cat /tmp/gpu-viewer/VKDDevicesparseinfo1.txt | awk '/%s/{flag=1;next}/Properties.*/{flag=0}flag' > /tmp/gpu-viewer/filterProperties.txt" % property)

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
                        value1.append(str(float(value[i])))
                    else:
                        value1.append(value[i])
                    i += 1
                else:
                    value1.append(" ")

        for i in value1:
            if i == " 0\n":
                value2.append("false")
                fgColor.append(Const.COLOR2)
            elif i == " 1\n":
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
                        text1 = text[:-2]
                        k = 0
                        count += 1
                        background_color = Const.BGCOLOR3
                        iter1 = SparseTab_Store.append(None, [text1.strip('\n'), value2[i].strip('\n'), background_color,
                                                              fgColor[i]])

                    else:
                        background_color = setBackgroundColor(k)
                        SparseTab_Store.append(iter1,
                                               [text.strip('\n'), value2[i].strip('\n'), background_color, fgColor[i]])
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
                        SparseTab_Store.append(None,
                                               [text.strip('\n'), value2[i].strip('\n'), background_color, fgColor[i]])
                        k += 1
                    TreeSparse.expand_all()

    def selectFeature(Combo):
        feature = Combo.get_active_text()
        if feature is None:
            feature = " "
        elif "Show All Features" in feature:
            os.system(
                "cat /tmp/gpu-viewer/VKDeviceFeatures.txt | awk '/==/{flag=1 ; next} flag' | grep = | sort > /tmp/gpu-viewer/VKDFeatures1.txt")

        else:
            os.system(
                "cat /tmp/gpu-viewer/VKDeviceFeatures.txt | awk '/%s/{flag=1;next}/Features*/{flag=0}flag' | awk '/==/{flag=1 ; next} flag' | grep = | sort > /tmp/gpu-viewer/VKDFeatures1.txt" % feature)

        os.system(
            "cat /tmp/gpu-viewer/VKDFeatures1.txt | awk '{gsub(/= 1/,'True');print}' | awk '{gsub(/= 0/,'False');print}' > /tmp/gpu-viewer/VKDFeatures.txt")

        FeaturesTab_Store.clear()
        TreeFeatures.set_model(FeaturesTab_Store_filter)
        fgColor, value = colorTrueFalse("/tmp/gpu-viewer/VKDFeatures1.txt", "= 1")

        with open("/tmp/gpu-viewer/VKDFeatures.txt", "r") as file1:
            for i, line in enumerate(file1):
                text = line.strip('\t')
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

    DeviceTab_Store = Gtk.ListStore(str, str, str)
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

    LimitsTab_Store = Gtk.ListStore(str, str, str)
    LimitsTab_Store_filter = LimitsTab_Store.filter_new()
    TreeLimits = Gtk.TreeView(LimitsTab_Store_filter, expand=True)
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

    FormatsTab_Store = Gtk.TreeStore(str, str, str, str, str, str, str, str)
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
        column.set_property("min-width", MWIDTH)
        column.set_property("min-width", 100)
        if 1 <= i < 5:
            column.add_attribute(Formatsrenderer, "foreground", i + 4)
        TreeFormats.set_property("can-focus", False)
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

    MemoryTab_Store = Gtk.ListStore(int, int, str, str, str, str, str, str, str, str, str, str, str)
    TreeMemory = Gtk.TreeView(MemoryTab_Store, expand=True)
    TreeMemory.set_enable_search(True)

    for i, column_title in enumerate(MemoryTitle):
        Memoryrenderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(column_title, Memoryrenderer, text=i)
        column.add_attribute(Memoryrenderer, "background", 7)
        column.set_sort_column_id(i)
        column.set_resizable(True)
        column.set_reorderable(True)
        if 2 <= i < 7:
            column.set_property("min-width", 100)
            column.add_attribute(Memoryrenderer, "foreground", i + 6)
        TreeMemory.set_property("can-focus", False)
        TreeMemory.append_column(column)

    MemoryScrollbar = createScrollbar(TreeMemory)
    MemoryGrid.add(MemoryScrollbar)

    HeapGrid = createSubFrame(MemoryTab)

    HeapTab_Store = Gtk.ListStore(int, str, str, str, str)
    TreeHeap = Gtk.TreeView(HeapTab_Store, expand=True)
    TreeHeap.set_enable_search(True)
    for i, column_title in enumerate(HeapTitle):
        Heaprenderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(column_title, Heaprenderer, text=i)
        column.set_resizable(True)
        column.set_reorderable(True)
        column.set_sort_column_id(i)
        if i == 1:
            column.set_property("min-width", 200)
        column.add_attribute(Heaprenderer, "background", 3)
        if i == 2:
            column.add_attribute(Heaprenderer, "foreground", 4)
        TreeHeap.set_property("can-focus", False)
        TreeHeap.append_column(column)

    HeapScrollbar = createScrollbar(TreeHeap)
    HeapGrid.add(HeapScrollbar)
    # -------------------------Creating the Queues Tab -----------------------------------------------------

    QueueTab = Gtk.Box(spacing=10)
    QueueGrid = createSubTab(QueueTab, notebook, "Queue")

    QueueTab_Store = Gtk.ListStore(int, int, int, str, str, str, str, str, str, str, str, str, str, str, str)
    TreeQueue = Gtk.TreeView(QueueTab_Store, expand=True)
    TreeQueue.set_enable_search(True)

    for i, column_title in enumerate(QueueTitle):
        Queuerenderer = Gtk.CellRendererText()
        Queuerenderer.set_alignment(0.5, 0.5)
        column = Gtk.TreeViewColumn(column_title, Queuerenderer, text=i)
        column.set_alignment(0.5)
        column.add_attribute(Queuerenderer, "background", 10)
        column.set_sort_column_id(i)
        column.set_resizable(True)
        column.set_reorderable(True)
        if 2 < i < 7:
            column.add_attribute(Queuerenderer, "foreground", i + 8)
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
    SurfaceTab_Store = Gtk.TreeStore(str, str, str)
    TreeSurface = Gtk.TreeView(SurfaceTab_Store, expand=True)
    TreeSurface.set_property("enable-tree-lines", True)
    with open("/tmp/gpu-viewer/vulkaninfo.txt", "r") as file1:
        for line in file1:
            if "VkSurfaceCapabilities" in line:
                SurfaceTab = Gtk.Box(spacing=10)
                SurfaceGrid = createSubTab(SurfaceTab, notebook, "Surface")

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

def setGpuIcon(self,gpu_image,image_renderer):

    with open("/tmp/gpu-viewer/VKDDeviceinfo1.txt", "r") as file1:

        self.gpu_image = fetchImageFromUrl(Const.AMD_LOGO_PNG,Const.ICON_WIDTH,Const.ICON_HEIGHT, True)
        self.image_renderer = Gtk.Image.new_from_pixbuf(gpu_image)
        for line in file1:
            if "Intel" in line:
                self.gpu_image = GdkPixbuf.Pixbuf.new_from_file_at_size(Const.INTEL_LOGO_PNG, 70, 70)
                self.image_renderer.set_from_pixbuf(gpu_image)
                break
            elif "NVIDIA" in line or "GeForce" in line :
                image_renderer.clear()
                gpu_image = GdkPixbuf.Pixbuf.new_from_file_at_size(Const.NVIDIA_LOGO_PNG,50,50)
                image_renderer.set_from_pixbuf(gpu_image)
                break
            elif "AMD" in line or "ATI" in line:
                gpu_image = fetchImageFromUrl(Const.AMD_LOGO_PNG, Const.ICON_WIDTH, Const.ICON_HEIGHT, True)
                image_renderer.set_from_pixbuf(gpu_image)
                break
