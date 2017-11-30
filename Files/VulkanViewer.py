import os

import gi

import Const
import time
import threading

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from Common import copyContentsFromFile, setBackgroundColor, setColumns, createSubTab, createScrollbar, createSubFrame, \
    colorTrueFalse, getDriverVersion

MWIDTH = 300

RANGE1 = 100

DeviceTitle = ["Device Information", "Details"]
SparseTitle = ["Device Sparse Properties", "Value"]
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
LayerTitle = ["Layers", "Vulkan Version", "Layer Version", "Extension Count","Description"]
SurfaceTitle = ["Surface Capabilities", "Value"]


def Vulkan(tab2):
    # Creating Tabs for different Features

    # Creating Feature Tab

    def Devices(GPUname):

        for i in range(len(list)):
            if GPUname == i:
                os.system(
                    "cat /tmp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceLimits:/{flag=0}flag' | awk '/==.*/{flag=1;next}flag' | grep -v driver > /tmp/VKDDeviceinfo1.txt" % i)
                os.system(
                    "cat /tmp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceLimits:/{flag=0}flag' | awk '/==.*/{flag=1;next}flag' | grep driverVersion | awk '{gsub(/\(.*/,'True');}1' >> /tmp/VKDDeviceinfo1.txt" % i)
                break

        os.system("cat /tmp/VKDDeviceinfo1.txt | awk '{gsub(/=.*/,'True');}1' > /tmp/VKDDeviceinfo.txt")
        os.system("cat /tmp/VKDDeviceinfo1.txt | grep -o =.* | grep -o ' .*' > /tmp/VKDDeviceinfo2.txt")

        valueLHS = copyContentsFromFile("/tmp/VKDDeviceinfo.txt")

        try:
            os.system("lsb_release -d -r -c > /tmp/VKDLsbRelease.txt")
            os.system("cat /tmp/VKDLsbRelease.txt | grep -o :.* >> /tmp/VKDDeviceinfo2.txt")
            os.system("cat /tmp/VKDLsbRelease.txt | awk '{gsub(/:.*/,'True');}1' >> /tmp/VKDLsbReleaseLHS.txt")
            os.system("uname -r >> /tmp/VKDDeviceinfo2.txt")
            valueLHS = valueLHS + copyContentsFromFile("/tmp/VKDLsbReleaseLHS.txt")
            valueLHS.append("Kernel")
        except Exception as e:
            raise e

        # Storing the RHS values into a list

        valueRHS = copyContentsFromFile("/tmp/VKDDeviceinfo2.txt")

        # This should take care of api version from 0.0.0 to 2.5.99
        for i in range(2):
            for k in range(5):
                for j in range(RANGE1):
                    if "(%d.%d.%d)" % (i, k, j) in valueRHS[0]:
                        valueRHS[0] = "%d.%d.%d" % (i, k, j)
                        break

        for i in range(len(valueRHS)):
            if i > 0:
                if "0x" in valueRHS[i]:
                    valueRHS[i] = int(valueRHS[i], 16)
                    valueRHS[i] = str("%d" % valueRHS[i])

        valueRHS[5] = getDriverVersion(valueRHS)

        valueLHS = [i.strip('\t') for i in valueLHS]
        valueRHS = [i.strip(':') for i in valueRHS]
        valueRHS = [i.strip('\t') for i in valueRHS]
        valueRHS = [i.strip(' ') for i in valueRHS]
        # Printing the Details into the Treeview

        DeviceTab_Store.clear()
        TreeDevice.set_model(DeviceTab_Store)


        for i in range(len(valueRHS)):
            background_color = setBackgroundColor(i)
            if "Description" in valueLHS[i]:
                DeviceTab_Store.append(["operatingSystem",valueRHS[i].strip('\n'),background_color])
            else:
                DeviceTab_Store.append([valueLHS[i].strip('\n'), valueRHS[i].strip('\n'), background_color])

        for i in range(len(list)):
            if GPUname == i:
                os.system(
                    "cat /tmp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Extensions.*/{flag=0}flag' | awk '/VkPhysicalDeviceSparseProperties:/{flag=1;next}/Device Extensions.*/{flag=0}flag' | grep = | sort > /tmp/VKDDevicesparseinfo1.txt" % i)

        os.system("cat /tmp/VKDDevicesparseinfo1.txt | awk '{gsub(/=.*/,'True');}1' > /tmp/VKDDevicesparseinfo.txt")

        fgColor, value = colorTrueFalse("/tmp/VKDDevicesparseinfo1.txt", "= 1")

        SparseTab_Store.clear()
        TreeSparse.set_model(SparseTab_Store)
        with open("/tmp/VKDDevicesparseinfo.txt", "r") as file1:
            for i, line in enumerate(file1):
                text = line.strip('\t')
                background_color = setBackgroundColor(i)
                SparseTab_Store.append([text.strip('\n'), value[i].strip('\n'), background_color, fgColor[i]])

    def Features(GPUname):

        for i in range(len(list)):
            if GPUname == i:
                os.system(
                    "cat /tmp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Format Properties:/{flag=0}flag' | awk '/VkPhysicalDeviceFeatures:/{flag=1; next}/Format Properties:/{flag=0}flag' | awk '/==/{flag=1 ; next} flag' | grep = | sort > /tmp/VKDFeatures1.txt" % i)
                break

        os.system(
            "cat /tmp/VKDFeatures1.txt | awk '{gsub(/= 1/,'True');print}' | awk '{gsub(/= 0/,'False');print}' > /tmp/VKDFeatures.txt")

        fgColor, value = colorTrueFalse("/tmp/VKDFeatures1.txt", "= 1")

        FeaturesTab_Store.clear()
        TreeFeatures.set_model(FeaturesTab_Store)
        with open("/tmp/VKDFeatures.txt", "r") as file1:
            for i, line in enumerate(file1):
                text = line.strip('\t')
                background_color = setBackgroundColor(i)
                FeaturesTab_Store.append([text.strip('\n'), value[i].strip('\n'), background_color, fgColor[i]])

    def Limits(GPUname):

        for i in range(len(list)):
            if GPUname == i:
                os.system(
                    "cat /tmp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceSparseProperties:/{flag=0}flag'| awk '/--/{flag=1 ; next} flag' | sort > /tmp/VKDlimits1.txt" % i)
                break
        os.system("cat /tmp/VKDlimits1.txt | awk '{gsub(/=.*/,'True');}1' > /tmp/VKDlimits.txt")
        os.system("cat /tmp/VKDlimits1.txt | grep -o '=.*' | grep -o '[ -].*' > /tmp/VKDlimits2.txt")

        value = copyContentsFromFile("/tmp/VKDlimits2.txt")

        # finding and converting any hexadecimal value to decimal

        for i in range(len(value)):
            if "0x" in value[i]:
                value[i] = str(int(value[i], 16))

        LimitsTab_Store.clear()
        TreeLimits.set_model(LimitsTab_Store)

        value = [i.strip(' ') for i in value]
        with open("/tmp/VKDlimits.txt", "r") as file1:
            for i, line in enumerate(file1):
                text = line.strip('\t')
                background_color = setBackgroundColor(i)
                LimitsTab_Store.append([text.strip('\n'), value[i].strip('\n'), background_color])

    def Extensions(GPUname):

        for i in range(len(list)):
            if GPUname == i:
                os.system(
                    "cat /tmp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkQueueFamilyProperties/{flag=0}flag'|awk '/Device Extensions/{flag=1; next}/VkQueueFamilyProperties/{flag=0} flag' | grep VK_ | sort > /tmp/VKDExtensions1.txt" % i)
                break
        os.system("cat /tmp/VKDExtensions1.txt | awk '{gsub(/:.*/,'True');print} ' > /tmp/VKDExtensions.txt")

        # This should take care of further versioning till 100
        with open("/tmp/VKDExtensions1.txt", "r") as file1:
            value = []
            for line in file1:
                for j in range(RANGE1):
                    if ": extension revision %2d" % j in line:
                        value.append("0.0.%d" % j)
                        break

        ExtensionTab_Store.clear()
        TreeExtension.set_model(ExtensionTab_Store)

        with open("/tmp/VKDExtensions.txt", "r") as file1:
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
                os.system(
                    "cat /tmp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | grep ^FORMAT_ | grep -o _.* | grep -o [a-zA-Z].* | awk '{gsub(/:.*/,'True');print} ' > /tmp/VKDFORMATS.txt" % i)
                os.system(
                    "cat /tmp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /linearTiling.*/{f=1}'> /tmp/VKDFORMATSlinear.txt" % i)
                os.system(
                    "cat /tmp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /optimalTiling.*/{f=1}'> /tmp/VKDFORMATSoptimal.txt" % i)
                os.system(
                    "cat /tmp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /bufferFeatures.*/{f=1}'> /tmp/VKDFORMATSBuffer.txt" % i)
                break

        # Linear values

        linearfg, linear = colorTrueFalse("/tmp/VKDFORMATSlinear.txt", "VK")

        # Optimal Values
        optimalfg, optimal = colorTrueFalse("/tmp/VKDFORMATSoptimal.txt", "VK")

        # Buffer Values
        Bufferfg, Buffer = colorTrueFalse("/tmp/VKDFORMATSBuffer.txt", "VK")

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
        with open("/tmp/VKDFORMATS.txt", "r") as file1:
            for line in file1:
                Format.append(line.strip('\n'))

        Format.append("BLANK")

        FormatsTab_Store.clear()
        TreeFormats.set_model(FormatsTab_Store)
        for i in range(len(Format) - 1):
            background_color = setBackgroundColor(i)
            iter = FormatsTab_Store.append(None,
                                           [Format[i], linear[i].strip('\n'), optimal[i].strip('\n'),
                                            Buffer[i].strip('\n'), background_color, linearfg[i], optimalfg[i],
                                            Bufferfg[i]])
            j = i
            if trueFormats[i]:
                os.system(
                    "cat /tmp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk '/FORMAT_%s*/{flag=1; next}/FORMAT_%s*/{flag=0} flag' | awk '/./' > /tmp/Tiling.txt" % (
                        GPUname, Format[j], Format[j + 1]))
                with open("/tmp/Tiling.txt", "r") as file1:
                    k = 0
                    z = 0
                    value = 0
                    for line in file1:
                        background_color = setBackgroundColor(k)
                        if "linear" in line:
                            value = value + 1
                        if value <= 1:
                            if ":" in line:
                                background_color = setBackgroundColor(z)
                                text = line.strip('\t')
                                iter2 = FormatsTab_Store.append(iter,
                                                                [text.strip('\n'), " ", " ", " ", background_color,
                                                                 Const.BGCOLOR1, Const.BGCOLOR1, Const.BGCOLOR1])
                                k = 1
                                z += 1
                            else:
                                text = line.strip('\t')
                                FormatsTab_Store.append(iter2, [text.strip('\n'), " ", " ", " ", background_color,
                                                                Const.BGCOLOR1, Const.BGCOLOR1, Const.BGCOLOR1])
                            k += 1

    def MemoryTypes(GPUname):

        for i in range(len(list)):
            if GPUname == i:
                os.system(
                    "cat /tmp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceFeatures:/{flag=0}flag'|awk '/VkPhysicalDeviceMemoryProperties:/{flag=1; next}/VkPhysicalDeviceFeatures:/{flag=0} flag' > /tmp/VKDMemoryType.txt" % i)
                break

        with open("/tmp/VKDMemoryType.txt", "r") as file1:
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
        Mcount = 0
        LAfg = []
        HCAfg = []
        HCOfg = []
        HVfg = []
        DLfg = []

        with open("/tmp/VKDMemoryType.txt", "r") as file1:
            for line in file1:
                if "memoryTypes" in line:
                    Mcount = Mcount + 1
                for i in range(32):
                    if " %s:" % hex(i) in line:
                        dec = int(hex(i), 16)
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
        for i in range(Mcount):
            background_color = setBackgroundColor(i)
            MemoryTab_Store.append([i, heapIndex[i], Device_Local[i].strip('\n'), Host_Visible[i].strip('\n'),
                                    Host_Coherent[i].strip('\n'), Host_Cached[i].strip('\n'),
                                    Lazily_Allocated[i].strip('\n'), background_color, DLfg[i], HVfg[i], HCOfg[i],
                                    HCAfg[i], LAfg[i]])

        HCount = 0
        size = []
        HEAP_DEVICE_LOCAL = []

        with open("/tmp/VKDMemoryType.txt", "r") as file1:
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
                if "size " in line:
                    for j in range(1025):
                        for k in range(RANGE1):
                            if "(%d.%02d GiB)" % (j, k) in line:
                                size.append("%d.%02d GB" % (j, k))
                                break
                            elif "(%d.%02d MiB)" % (j, k) in line:
                                size.append("%d.%02d MB" % (j, k))
                                break

        HeapTab_Store.clear()
        TreeHeap.set_model(HeapTab_Store)

        for i in range(HCount):
            background_color = setBackgroundColor(i)
            HeapTab_Store.append(
                [i, size[i].strip('\n'), HEAP_DEVICE_LOCAL[i].strip('\n'), background_color, Heapfg[i]])

        label = "Memory Types (%d) & Heaps (%d)" % (Mcount, HCount)
        notebook.set_tab_label(MemoryTab, Gtk.Label(label))

    def Queues(GPUname):

        for i in range(len(list)):
            if GPUname == i:
                os.system(
                    "cat /tmp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceMemoryProperties:/{flag=0}flag'|awk '/VkQueue.*/{flag=1; next}/VkPhysicalDeviceMemoryProperties:/{flag=0} flag' > /tmp/VKDQueues.txt" % i)
                break

        os.system("cat /tmp/VKDQueues.txt | grep Count | grep -o =.* | grep -o ' .*' > /tmp/VKDQueuecount.txt")
        os.system("cat /tmp/VKDQueues.txt | grep times | grep -o =.* | grep -o ' .*' > /tmp/VKDQueuebits.txt")
        os.system("cat /tmp/VKDQueues.txt | grep Flags | grep -o =.* | grep -o ' .*' > /tmp/VKDQueueFlags.txt")

        width = []
        height = []
        depth = []

        with open("/tmp/VKDQueues.txt", "r") as file1:
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
        Gfg, GBit = colorTrueFalse("/tmp/VKDQueueFlags.txt", "GRAPHICS")
        Cfg, CBit = colorTrueFalse("/tmp/VKDQueueFlags.txt", "COMPUTE")
        Tfg, TBit = colorTrueFalse("/tmp/VKDQueueFlags.txt", "TRANSFER")
        Sfg, SBit = colorTrueFalse("/tmp/VKDQueueFlags.txt", "SPARSE")

        qCount = copyContentsFromFile("/tmp/VKDQueuecount.txt")

        qBits = copyContentsFromFile("/tmp/VKDQueuebits.txt")

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
            "cat /tmp/vulkaninfo.txt | awk '/Instance Extensions	count.*/{flag=1;next}/Layers: count.*/{flag=0}flag'| grep VK_ | sort > /tmp/VKDInstanceExtensions1.txt")
        os.system(
            "cat /tmp/VKDInstanceExtensions1.txt | awk '{gsub(/:.*/,'True');print} ' > /tmp/VKDInstanceExtensions.txt")

        # This should take care of further versioning till RANGE1
        with open("/tmp/VKDInstanceExtensions1.txt", "r") as file1:
            value = []
            for line in file1:
                for j in range(RANGE1):
                    if ": extension revision %2d" % j in line:
                        value.append("0.0.%d" % j)
                        break
        InstanceTab_Store.clear()
        TreeInstance.set_model(InstanceTab_Store)
        with open("/tmp/VKDInstanceExtensions.txt", "r") as file1:
            count1 = len(file1.readlines())
            label = "Instance Extensions (%d)" % count1
            InstanceNotebook.set_tab_label(InstanceExtTab, Gtk.Label(label))
            file1.seek(0, 0)
            for i, line in enumerate(file1):
                text = line.strip('\t')
                background_color = setBackgroundColor(i)
                InstanceTab_Store.append([text.strip('\n'), value[i].strip('\n'), background_color])

        os.system(
            "cat /tmp/vulkaninfo.txt | awk '/Layers: count.*/{flag=1;next}/Presentable Surfaces.*/{flag=0}flag' > /tmp/VKDLayer1.txt")
        os.system("cat /tmp/VKDLayer1.txt | grep _LAYER_ | awk '{gsub(/\(.*/,'True');print} ' > /tmp/VKDLayer.txt")
        os.system("cat /tmp/VKDLayer1.txt | grep _LAYER_ | grep -o \(.* | awk '{gsub(/\).*/,'True');print}'| awk '{gsub(/\(/,'True');print}' > /tmp/VKDLayerDescription.txt")
        Vversion = []
        with open("/tmp/VKDLayer1.txt", "r") as file1:
            for line in file1:
                for i in range(2):
                    for j in range(5):
                        for k in range(RANGE1):
                            if "Vulkan version %d.%d.%d," % (i, j, k) in line:
                                Vversion.append("%d.%d.%d" % (i, j, k))
                                break

        LVersion = []
        with open("/tmp/VKDLayer1.txt", "r") as file1:
            for line in file1:
                for j in range(RANGE1):
                    if "layer version %d" % j in line:
                        LVersion.append("0.0.%d" % j)
                        break

        ECount = []
        with open("/tmp/VKDLayer1.txt", "r") as file1:
            for line in file1:
                for j in range(RANGE1):
                    if "Layer Extensions	count = %d" % j in line:
                        ECount.append("%d" % j)
                        break

        layerDescription = copyContentsFromFile("/tmp/VKDLayerDescription.txt")
        LayerTab_Store.clear()
        TreeLayer.set_model(LayerTab_Store)
        count2 = len(LVersion)
        label = "Instances (%d) & Layers (%d)" % (count1, count2)
        label2 = "Instance Layers (%d)"%count2
        notebook.set_tab_label(InstanceTab, Gtk.Label(label))
        InstanceNotebook.set_tab_label(InstanceLayersTab,Gtk.Label(label2))
        with open("/tmp/VKDLayer.txt", "r") as file1:
            for i, line in enumerate(file1):
                background_color = setBackgroundColor(i)
                LayerTab_Store.append(
                    [line.strip('\n'), Vversion[i].strip('\n'), LVersion[i].strip('\n'), ECount[i].strip('\n'),layerDescription[i].strip('\n'),
                     background_color])

    def Surface(GPUname):

        for GPU in range(len(list)):
            if GPUname == GPU:
                os.system(
                    "cat /tmp/vulkaninfo.txt | awk '/Presentable Surfaces.*/{flag=1;next}/Device Properties and Extensions.*/{flag=0}flag' | awk '/GPU id       : %d.*/{flag=1;next}/GPU id       : %d.*/{flag=0}flag' | awk '/VkSurfaceCapabilities.*/{flag=1}/Device Properties.*/{flag=0}flag' | awk '/./'> /tmp/VKDsurface.txt" % (
                        GPU, GPU + 1))
                os.system(
                    "cat /tmp/vulkaninfo.txt | awk '/Presentable Surfaces.*/{flag=1;next}/Device Properties and Extensions.*/{flag=0}flag' | awk '/GPU id       : %d.*/{flag=1;next}/VkSurfaceCapabilities.*/{flag=0}flag' | awk '{gsub(/count =.*/,'True');print}' | grep -v type | awk '/./'  >> /tmp/VKDsurface.txt" % GPU)

        os.system("cat /tmp/VKDsurface.txt | awk '{gsub(/= .*/,'True');print} ' > /tmp/VKDsurface1.txt")
        os.system("cat /tmp/VKDsurface.txt | grep -o =.* | grep -o ' .*' > /tmp/VKDsurface2.txt")

        temp = copyContentsFromFile("/tmp/VKDsurface2.txt")
        SurfaceRHS = []
        i = 0
        with open("/tmp/VKDsurface.txt", "r") as file1:
            for line in file1:
                if "= " in line:
                    SurfaceRHS.append(temp[i])
                    i = i + 1
                else:
                    SurfaceRHS.append(" ")

        Surface = []
        with open("/tmp/VKDsurface1.txt", "r") as file1:
            for line in file1:
                Surface.append(line)

        Surface = [i.strip('\n ') for i in Surface]
        SurfaceTab_Store.clear()
        TreeSurface.set_model(SurfaceTab_Store)
        count = 0
        for i in range(len(Surface)):
            TreeSurface.expand_all()
            if "====" in Surface[i]:
                continue
            if "type" in Surface[i]:
                continue
            background_color = setBackgroundColor(i)
            if "VkSurfaceCapabilities" in Surface[i] or "Formats" in Surface[i] or "Present" in Surface[i]:
                background_color = Const.BGCOLOR3
                text = Surface[i].strip('\t')
                count = 0
                iter1 = SurfaceTab_Store.append(None, [text, SurfaceRHS[i].strip('\n'), background_color])
            else:
                if ":" in Surface[i]:
                    count += 1
                    text = Surface[i].strip('\t')
                    iter2 = SurfaceTab_Store.append(iter1, [text, SurfaceRHS[i].strip('\n'), background_color])
                    continue
                if count > 0:
                    text = Surface[i].strip('\t')
                    SurfaceTab_Store.append(iter2, [text, SurfaceRHS[i].strip('\n'), background_color])
                else:
                    text = Surface[i].strip('\t')
                    SurfaceTab_Store.append(iter1, [text, SurfaceRHS[i].strip('\n'), background_color])

    def radcall(combo):

        text = combo.get_active()
        for i in range(len(list)):
            if text == i:
                Devices(text)
                Features(text)
                Limits(text)
                Extensions(text)
                Formats(text)
                MemoryTypes(text)
                Queues(text)
                Surface(text)
            Instance()

        os.system("rm /tmp/VKD*.txt")

    grid = Gtk.Grid()
    tab2.add(grid)
    DevicesFrame = Gtk.Frame()
    grid.add(DevicesFrame)

    notebook = Gtk.Notebook()
    notebook.set_property("scrollable", True)
    notebook.set_property("enable-popup", True)
    grid.attach(notebook, 0, 2, 1, 1)
    # ----------------Creating the Device Info Tab ------------

    DeviceTab = Gtk.VBox(spacing=10)
    DeviceGrid = createSubTab(DeviceTab, notebook, "Device")

    DeviceTab_Store = Gtk.ListStore(str, str, str)
    TreeDevice = Gtk.TreeView(DeviceTab_Store, expand=True)

    setColumns(TreeDevice, DeviceTitle, Const.MWIDTH, 0.0)

    DeviceScrollbar = createScrollbar(TreeDevice)
    DeviceGrid.add(DeviceScrollbar)

    SparseGrid = createSubFrame(DeviceTab)

    SparseTab_Store = Gtk.ListStore(str, str, str, str)
    TreeSparse = Gtk.TreeView(SparseTab_Store, expand=True)
    TreeSparse.set_enable_search(True)
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

    SparseScrollbar = createScrollbar(TreeSparse)
    SparseGrid.add(SparseScrollbar)

    # -----------------Creating the Features Tab-----------------

    FeatureTab = Gtk.VBox(spacing=10)
    FeaturesGrid = createSubTab(FeatureTab, notebook, "Features")

    FeaturesTab_Store = Gtk.ListStore(str, str, str, str)
    TreeFeatures = Gtk.TreeView(FeaturesTab_Store, expand=True)
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

    FeatureScrollbar = createScrollbar(TreeFeatures)
    FeaturesGrid.add(FeatureScrollbar)

    # ------------ Creating the Limits Tab -------------------------------------------
    LimitsTab = Gtk.VBox(spacing=10)
    LimitsGrid = createSubTab(LimitsTab, notebook, "Limits")

    LimitsTab_Store = Gtk.ListStore(str, str, str)
    TreeLimits = Gtk.TreeView(LimitsTab_Store, expand=True)
    TreeLimits.set_enable_search(True)

    setColumns(TreeLimits, LimitsTitle, Const.MWIDTH, 0.0)

    LimitsScrollbar = createScrollbar(TreeLimits)
    LimitsGrid.add(LimitsScrollbar)

    # ------------ Creating the Extensions Tab-------------------------------------------

    ExtensionTab = Gtk.VBox(spacing=10)
    ExtensionGrid = createSubTab(ExtensionTab, notebook, "Extensions")

    ExtensionTab_Store = Gtk.ListStore(str, str, str)
    TreeExtension = Gtk.TreeView(ExtensionTab_Store, expand=True)
    TreeExtension.set_enable_search(True)

    setColumns(TreeExtension, ExtensionsTitle, Const.MWIDTH, 0.0)

    ExtensionScrollbar = createScrollbar(TreeExtension)
    ExtensionGrid.add(ExtensionScrollbar)
    # ------------Creating the Formats Tab --------------------------------------------------

    FormatsTab = Gtk.VBox(spacing=10)
    FormatsGrid = createSubTab(FormatsTab, notebook, "Formats")

    FormatsTab_Store = Gtk.TreeStore(str, str, str, str, str, str, str, str)
    TreeFormats = Gtk.TreeView(FormatsTab_Store, expand=True)
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

    FormatsScrollbar = createScrollbar(TreeFormats)
    FormatsGrid.add(FormatsScrollbar)

    # ------------------------Memory Types & Heaps----------------------------------------------

    MemoryTab = Gtk.VBox(spacing=10)
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

    QueueTab = Gtk.VBox(spacing=10)
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

    InstanceTab = Gtk.VBox(spacing=10)
    InstanceGrid = createSubTab(InstanceTab, notebook, "Instances & layers")
    InstanceNotebook = Gtk.Notebook()
    InstanceGrid.add(InstanceNotebook)
    InstanceExtTab = Gtk.VBox(spacing=10)
    InstanceExtGrid = createSubTab(InstanceExtTab,InstanceNotebook,"Instance Extensions")

    InstanceTab_Store = Gtk.ListStore(str, str, str)
    TreeInstance = Gtk.TreeView(InstanceTab_Store, expand=True)
    TreeInstance.set_enable_search(True)

    setColumns(TreeInstance, InstanceTitle, 300, 0.0)

    InstanceScrollbar = createScrollbar(TreeInstance)
    InstanceExtGrid.add(InstanceScrollbar)

    InstanceLayersTab = Gtk.VBox(spacing=10)
    InstanceLayersGrid = createSubTab(InstanceLayersTab,InstanceNotebook,"Instance Layers")

    LayerTab_Store = Gtk.ListStore(str, str, str, str, str,str)
    TreeLayer = Gtk.TreeView(LayerTab_Store, expand=True)
    TreeLayer.set_enable_search(TreeLayer)

    setColumns(TreeLayer, LayerTitle, 100, 0.0)

    LayerScrollbar = createScrollbar(TreeLayer)
    InstanceLayersGrid.add(LayerScrollbar)

    # ------------------ Creating the Surface Tab --------------------------------------------------
    SurfaceTab_Store = Gtk.TreeStore(str, str, str)
    TreeSurface = Gtk.TreeView(SurfaceTab_Store, expand=True)
    TreeSurface.set_property("enable-tree-lines", True)
    with open("/tmp/vulkaninfo.txt", "r") as file1:
        for line in file1:
            if "VkSurfaceCapabilities" in line:
                SurfaceTab = Gtk.VBox(spacing=10)
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

    grid.set_row_spacing(30)
    os.system("cat /tmp/vulkaninfo.txt | grep Name | grep -o  =.* | grep -o ' .*' > /tmp/GPU.txt")

    list = copyContentsFromFile("/tmp/GPU.txt")

    list = [i.strip('\n ') for i in list]

    DS = Gtk.Label()
    DS.set_text("Available Device(s) :")
    DevicesGrid.attach(DS, 0, 1, 1, 1)
    gpu_store = Gtk.ListStore(str)
    for i in list:
        gpu_store.append([i])

    gpu_combo = Gtk.ComboBox.new_with_model(gpu_store)
    gpu_combo.connect("changed", radcall)
    renderer_text = Gtk.CellRendererText()
    gpu_combo.set_property("has-frame", False)
    gpu_combo.pack_start(renderer_text, True)
    gpu_combo.add_attribute(renderer_text, "text", 0)
    gpu_combo.set_entry_text_column(0)
    gpu_combo.set_active(0)

    DevicesGrid.attach_next_to(gpu_combo, DS, Gtk.PositionType.RIGHT, 20, 1)

    # Logos

    tab2.show_all()
