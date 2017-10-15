import gi

FONT = "Helvetica 11"
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import os

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
InstanceTitle = ["Instance Extensions", "Version"]
LayerTitle = ["Instance Layers", "Vulkan Version", "Layer Version", "Extension Count"]
SurfaceTitle = ["Surface Capabilities", "Value"]


def Vulkan(tab2):
    # Creating Tabs for different Features

    # Creating Feature Tab
    os.system("vulkaninfo > .Temp/vulkaninfo.txt")

    def Devices(GPUname):

        for i in range(len(list)):
            if GPUname == i:
                os.system(
                    "cat .Temp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceLimits:/{flag=0}flag' | awk '/==.*/{flag=1;next}flag' | grep -v driver > VKDDeviceinfo1.txt" % i)

        os.system("cat VKDDeviceinfo1.txt | awk '{gsub(/=.*/,'True');}1' > VKDDeviceinfo.txt")
        os.system("cat VKDDeviceinfo1.txt | grep -o =.* | grep -o ' .*' > VKDDeviceinfo2.txt")

        # Storing the RHS values into a list

        with open("VKDDeviceinfo2.txt", "r") as file1:
            value = []
            for line in file1:
                value.append(line)

        # This should take care of api version from 0.0.0 to 5.9.99
        for i in range(5):
            for k in range(10):
                for j in range(RANGE1):
                    if "(%d.%d.%d)" % (i, k, j) in value[0]:
                        value[0] = " %d.%d.%d" % (i, k, j)
                        break

        for i in range(len(value)):
            if i > 0:
                if "0x" in value[i]:
                    value[i] = int(value[i], 16)
                    value[i] = str(" %d" % value[i])

        # Printing the Details into the Treeview

        DeviceTab_Store.clear()
        TreeDevice.set_model(DeviceTab_Store)

        with open("VKDDeviceinfo.txt", "r") as file1:
            file1.seek(0, 0)
            i = 0
            for line in file1:
                text = line.strip('\t')
                if i % 2 == 0:
                    background_color = "#fff"
                else:
                    background_color = "#ddd"
                DeviceTab_Store.append([text.strip('\n'), value[i].strip('\n'), background_color])
                i = i + 1

        for i in range(len(list)):
            if GPUname == i:
                os.system(
                    "cat .Temp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Extensions.*/{flag=0}flag' | awk '/VkPhysicalDeviceSparseProperties:/{flag=1;next}/Device Extensions.*/{flag=0}flag' | grep = | sort > VKDDevicesparseinfo1.txt" % i)

        os.system("cat VKDDevicesparseinfo1.txt | awk '{gsub(/=.*/,'True');}1' > VKDDevicesparseinfo.txt")

        with open("VKDDevicesparseinfo1.txt", "r") as file1:
            value = []
            fgColor = []
            for line in file1:
                if '= 1' in line:
                    value.append("true")
                    fgColor.append("GREEN")
                else:
                    value.append("false")
                    fgColor.append("RED")
        SparseTab_Store.clear()
        TreeSparse.set_model(SparseTab_Store)
        with open("VKDDevicesparseinfo.txt", "r") as file1:
            file1.seek(0, 0)
            i = 0
            for line in file1:
                text = line.strip('\t')
                if i % 2 == 0:
                    background_color = "#fff"
                else:
                    background_color = "#ddd"
                SparseTab_Store.append([text.strip('\n'), value[i].strip('\n'), background_color, fgColor[i]])
                i = i + 1

    def Features(GPUname):

        for i in range(len(list)):
            if GPUname == i:
                os.system(
                    "cat .Temp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Format Properties:/{flag=0}flag' | awk '/VkPhysicalDeviceFeatures:/{flag=1; next}/Format Properties:/{flag=0}flag' | awk '/==/{flag=1 ; next} flag' | grep = | sort > VKDFeatures1.txt" % i)

        os.system(
            "cat VKDFeatures1.txt | awk '{gsub(/= 1/,'True');print}' | awk '{gsub(/= 0/,'False');print}' > VKDFeatures.txt")

        with open("VKDFeatures1.txt", "r") as file1:
            value = []
            fgColor = []
            for line in file1:
                if '= 1' in line:
                    value.append("true")
                    fgColor.append("GREEN")
                else:
                    value.append("false")
                    fgColor.append("RED")
        FeaturesTab_Store.clear()
        TreeFeatures.set_model(FeaturesTab_Store)
        i = 0
        with open("VKDFeatures.txt", "r") as file1:
            for line in file1:
                text = line.strip('\t')
                if i % 2 == 0:
                    background_color = "#fff"
                else:
                    background_color = "#ddd"
                FeaturesTab_Store.append([text.strip('\n'), value[i].strip('\n'), background_color, fgColor[i]])
                i = i + 1

    def Limits(GPUname):

        for i in range(len(list)):
            if GPUname == i:
                os.system(
                    "cat .Temp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceSparseProperties:/{flag=0}flag'| awk '/--/{flag=1 ; next} flag' | sort > VKDlimits1.txt" % i)

        os.system("cat VKDlimits1.txt | awk '{gsub(/=.*/,'True');}1' > VKDlimits.txt")
        os.system("cat VKDlimits1.txt | grep -o '=.*' | grep -o '[ -].*' > VKDlimits2.txt")

        with open("VKDlimits2.txt", "r") as file1:
            value = []
            for line in file1:
                value.append(line)

        # finding and converting any hexadecimal value to decimal

        for i in range(len(value)):
            if "0x" in value[i]:
                value[i] = str(int(value[i], 16))

        LimitsTab_Store.clear()
        TreeLimits.set_model(LimitsTab_Store)

        with open("VKDlimits.txt", "r") as file1:
            i = 0
            for line in file1:
                text = line.strip('\t')
                if i % 2 == 0:
                    background_color = "#fff"
                else:
                    background_color = "#ddd"
                LimitsTab_Store.append([text.strip('\n'), value[i].strip('\n'), background_color])
                i = i + 1

    def Extensions(GPUname):

        for i in range(len(list)):
            if GPUname == i:
                os.system(
                    "cat .Temp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkQueueFamilyProperties/{flag=0}flag'|awk '/Device Extensions/{flag=1; next}/VkQueueFamilyProperties/{flag=0} flag' | grep VK_ | sort > VKDExtensions1.txt" % i)

        os.system("cat VKDExtensions1.txt | awk '{gsub(/:.*/,'True');print} ' > VKDExtensions.txt")

        # This should take care of further versioning till 100
        with open("VKDExtensions1.txt", "r") as file1:
            value = []
            for line in file1:
                for j in range(RANGE1):
                    if ": extension revision %2d" % j in line:
                        value.append("0.0.%d" % j)
                        break

        ExtensionTab_Store.clear()
        TreeExtension.set_model(ExtensionTab_Store)

        with open("VKDExtensions.txt", "r") as file1:
            count = len(file1.readlines())
            label = "Extensions(%d)" % count
            notebook.set_tab_label(ExtensionTab, Gtk.Label(label))
            file1.seek(0, 0)
            i = 0
            for line in file1:
                text = line.strip('\t')
                if i % 2 == 0:
                    background_color = "#fff"
                else:
                    background_color = "#ddd"
                ExtensionTab_Store.append([text.strip('\n'), value[i].strip('\n'), background_color])
                i = i + 1

    def Format(GPUname):

        for i in range(len(list)):
            if GPUname == i:
                os.system(
                    "cat .Temp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | grep ^FORMAT_ | grep -o _.* | grep -o [a-zA-Z].* > VKDFORMATS.txt" % i)
                os.system(
                    "cat .Temp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /linearTiling.*/{f=1}'> VKDFORMATSlinear.txt" % i)
                os.system(
                    "cat .Temp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /optimalTiling.*/{f=1}'> VKDFORMATSoptimal.txt" % i)
                os.system(
                    "cat .Temp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/Device Properties/{flag=0}flag'|awk '/Format Properties/{flag=1; next}/Device Properties/{flag=0} flag' | awk 'f{print;f=0} /bufferFeatures.*/{f=1}'> VKDFORMATSBuffer.txt" % i)

        linear = []
        optimal = []
        Buffer = []

        # Linear values

        with open("VKDFORMATSlinear.txt", "r") as file1:
            count = len(file1.readlines())
            file1.seek(0, 0)
            linearfg = []
            for line in file1:
                if "None" in line:
                    linear.append("false")
                    linearfg.append("RED")
                else:
                    linear.append("true")
                    linearfg.append("GREEN")

        # Optimal Values

        with open("VKDFORMATSoptimal.txt", "r") as file1:
            optimalfg = []
            for line in file1:
                if "None" in line:
                    optimal.append("false")
                    optimalfg.append("RED")
                else:
                    optimal.append("true")
                    optimalfg.append("GREEN")

        with open("VKDFORMATSBuffer.txt", "r") as file1:
            Bufferfg = []
            for line in file1:
                if "None" in line:
                    Buffer.append("false")
                    Bufferfg.append("RED")
                else:
                    Buffer.append("true")
                    Bufferfg.append("GREEN")

        # counting the number of formats supported
        Formats = 0
        for i in range(count):
            if linear[i] == "true" or optimal[i] == "true" or Buffer[i] == "true":
                Formats = Formats + 1
        FormatsTab_Store.clear()
        TreeFormats.set_model(FormatsTab_Store)
        with open("VKDFORMATS.txt", "r") as file1:
            file1.seek(0, 0)
            label = "Formats(%d)" % Formats
            notebook.set_tab_label(FormatsTab, Gtk.Label(label))
            i = 0
            for line in file1:
                if i % 2 == 0:
                    background_color = "#fff"
                else:
                    background_color = "#ddd"
                FormatsTab_Store.append(
                    [line.strip('\n'), linear[i].strip('\n'), optimal[i].strip('\n'), Buffer[i].strip('\n'),
                     background_color, linearfg[i], optimalfg[i], Bufferfg[i]])
                i = i + 1

    def MemoryTypes(GPUname):

        for i in range(len(list)):
            if GPUname == i:
                os.system(
                    "cat .Temp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceFeatures:/{flag=0}flag'|awk '/VkPhysicalDeviceMemoryProperties:/{flag=1; next}/VkPhysicalDeviceFeatures:/{flag=0} flag' > VKDMemoryType.txt" % i)

        with open("VKDMemoryType.txt", "r") as file1:
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

        with open("VKDMemoryType.txt", "r") as file1:
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
                        for i in range(len(Flags)):
                            if i == 0:
                                Lazily_Allocated.append(Flags[i])
                                if Flags[i] == "false":
                                    LAfg.append("RED")
                                else:
                                    LAfg.append("GREEN")
                            elif i == 1:
                                Host_Cached.append(Flags[i])
                                if Flags[i] == "false":
                                    HCAfg.append("RED")
                                else:
                                    HCAfg.append("GREEN")
                            elif i == 2:
                                Host_Coherent.append(Flags[i])
                                if Flags[i] == "false":
                                    HCOfg.append("RED")
                                else:
                                    HCOfg.append("GREEN")
                            elif i == 3:
                                Host_Visible.append(Flags[i])
                                if Flags[i] == "false":
                                    HVfg.append("RED")
                                else:
                                    HVfg.append("GREEN")
                            elif i == 4:
                                Device_Local.append(Flags[i])
                                if Flags[i] == "false":
                                    DLfg.append("RED")
                                else:
                                    DLfg.append("GREEN")

        MemoryTab_Store.clear()
        TreeMemory.set_model(MemoryTab_Store)
        for i in range(Mcount):
            if i % 2 == 0:
                background_color = "#fff"
            else:
                background_color = "#ddd"
            MemoryTab_Store.append([i, heapIndex[i], Device_Local[i].strip('\n'), Host_Visible[i].strip('\n'),
                                    Host_Coherent[i].strip('\n'), Host_Cached[i].strip('\n'),
                                    Lazily_Allocated[i].strip('\n'), background_color, DLfg[i], HVfg[i], HCOfg[i],
                                    HCAfg[i], LAfg[i]])

        HCount = 0
        size = []
        HEAP_DEVICE_LOCAL = []

        with open("VKDMemoryType.txt", "r") as file1:
            Heapfg = []
            for line in file1:
                if "memoryHeaps" in line:
                    HCount = HCount + 1
                if "HEAP_DEVICE_LOCAL" in line:
                    HEAP_DEVICE_LOCAL.append("true")
                    Heapfg.append("GREEN")
                if "None" in line:
                    HEAP_DEVICE_LOCAL.append("false")
                    Heapfg.append("RED")
                if "size " in line:
                    for j in range(1024):
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
            if i % 2 == 0:
                background_color = "#fff"
            else:
                background_color = "#ddd"
            HeapTab_Store.append(
                [i, size[i].strip('\n'), HEAP_DEVICE_LOCAL[i].strip('\n'), background_color, Heapfg[i]])

        label = "Memory Types(%d) & Heaps(%d)" % (Mcount, HCount)
        notebook.set_tab_label(MemoryTab, Gtk.Label(label))

    def Queues(GPUname):

        for i in range(len(list)):
            if GPUname == i:
                os.system(
                    "cat .Temp/vulkaninfo.txt | awk '/GPU%d/{flag=1;next}/VkPhysicalDeviceMemoryProperties:/{flag=0}flag'|awk '/VkQueue.*/{flag=1; next}/VkPhysicalDeviceMemoryProperties:/{flag=0} flag' > VKDQueues.txt" % i)

        os.system("cat VKDQueues.txt | grep Count | grep -o =.* | grep -o ' .*' > VKDQueuecount.txt")
        os.system("cat VKDQueues.txt | grep times | grep -o =.* | grep -o ' .*' > VKDQueuebits.txt")
        os.system("cat VKDQueues.txt | grep Flags | grep -o =.* | grep -o ' .*' > VKDQueueFlags.txt")

        qCount = []
        qBits = []
        GBit = []
        CBit = []
        TBit = []
        SBit = []
        width = []
        height = []
        depth = []
        Gfg = []
        Cfg = []
        Tfg = []
        Sfg = []

        with open("VKDQueues.txt", "r") as file1:
            for line in file1:
                for i in range(10):
                    for j in range(10):
                        for k in range(10):
                            if "(%d, %d, %d)" % (i, j, k) in line:
                                width.append("%d" % i)
                                height.append("%d" % j)
                                depth.append("%d" % k)

        # finding and storing the value for Flags
        with open("VKDQueueFlags.txt", "r") as file1:
            for line in file1:
                if "GRAPHICS" in line:
                    GBit.append("true")
                    Gfg.append("GREEN")
                else:
                    GBit.append("false")
                    Gfg.append("RED")
                if "COMPUTE" in line:
                    CBit.append("true")
                    Cfg.append("GREEN")
                else:
                    CBit.append("false")
                    Cfg.append("RED")
                if "TRANSFER" in line:
                    TBit.append("true")
                    Tfg.append("GREEN")
                else:
                    TBit.append("false")
                    Tfg.append("RED")
                if "SPARSE" in line:
                    SBit.append("true")
                    Sfg.append("GREEN")
                else:
                    SBit.append("false")
                    Sfg.append("RED")

        with open("VKDQueuecount.txt", "r") as file1:
            count = len(file1.readlines())
            file1.seek(0, 0)
            for line in file1:
                qCount.append(int(line))

        with open("VKDQueuebits.txt", "r") as file1:
            for line in file1:
                qBits.append(int(line))

        QueueTab_Store.clear()
        TreeQueue.set_model(QueueTab_Store)
        for i in range(count):
            if i % 2 == 0:
                background_color = "#fff"
            else:
                background_color = "#ddd"
            QueueTab_Store.append(
                [i, qCount[i], qBits[i], GBit[i], CBit[i], TBit[i], SBit[i], width[i], height[i], depth[i],
                 background_color, Gfg[i], Cfg[i], Tfg[i], Sfg[i]])
        label = "Queues(%d)" % count
        notebook.set_tab_label(QueueTab, Gtk.Label(label))

    def Instance():

        os.system(
            "cat .Temp/vulkaninfo.txt | awk '/Instance Extensions	count.*/{flag=1;next}/Layers: count.*/{flag=0}flag'| grep VK_ | sort > VKDInstanceExtensions1.txt")
        os.system("cat VKDInstanceExtensions1.txt | awk '{gsub(/:.*/,'True');print} ' > VKDInstanceExtensions.txt")

        # This should take care of further versioning till 100
        with open("VKDInstanceExtensions1.txt", "r") as file1:
            value = []
            for line in file1:
                for j in range(RANGE1):
                    if ": extension revision %2d" % j in line:
                        value.append("0.0.%d" % j)
                        break
        InstanceTab_Store.clear()
        TreeInstance.set_model(InstanceTab_Store)
        with open("VKDInstanceExtensions.txt", "r") as file1:
            count1 = len(file1.readlines())
            label = "Instances(%d)" % count1
            notebook.set_tab_label(InstanceTab, Gtk.Label(label))
            file1.seek(0, 0)
            i = 0
            for line in file1:
                text = line.strip('\t')
                if i % 2 == 0:
                    background_color = "#fff"
                else:
                    background_color = "#ddd"
                InstanceTab_Store.append([text.strip('\n'), value[i].strip('\n'), background_color])
                i = i + 1

        os.system(
            "cat .Temp/vulkaninfo.txt | awk '/Layers: count.*/{flag=1;next}/Presentable Surfaces.*/{flag=0}flag' > VKDLayer1.txt")
        os.system("cat VKDLayer1.txt | grep _LAYER_ | awk '{gsub(/\(.*/,'True');print} ' > VKDLayer.txt")

        Vversion = []
        with open("VKDLayer1.txt", "r") as file1:
            for line in file1:
                for j in range(RANGE1):
                    if "Vulkan version 1.0.%d," % j in line:
                        Vversion.append("1.0.%d" % j)

        LVersion = []
        with open("VKDLayer1.txt", "r") as file1:
            for line in file1:
                for j in range(RANGE1):
                    if "layer version %d" % j in line:
                        LVersion.append("0.0.%d" % j)
                        break

        ECount = []
        with open("VKDLayer1.txt", "r") as file1:
            for line in file1:
                for j in range(RANGE1):
                    if "Layer Extensions	count = %d" % j in line:
                        ECount.append("%d" % j)
                        break

        LayerTab_Store.clear()
        TreeLayer.set_model(LayerTab_Store)
        count2 = len(LVersion)
        label = "Instances(%d) & Layers(%d)" % (count1, count2)
        notebook.set_tab_label(InstanceTab, Gtk.Label(label))
        with open("VKDLayer.txt", "r") as file1:
            i = 0
            for line in file1:

                if i % 2 == 0:
                    background_color = "#fff"
                else:
                    background_color = "#ddd"
                LayerTab_Store.append(
                    [line.strip('\n'), Vversion[i].strip('\n'), LVersion[i].strip('\n'), ECount[i].strip('\n'),
                     background_color])
                i = i + 1

    def Surface(GPUname):

        for GPU in range(len(list)):
            if GPUname == GPU:
                os.system(
                    "cat .Temp/vulkaninfo.txt | awk '/Presentable Surfaces.*/{flag=1;next}/Device Properties and Extensions.*/{flag=0}flag' | awk '/GPU id       : %d.*/{flag=1;next}/GPU id       : %d.*/{flag=0}flag' | awk '/VkSurfaceCapabilities.*/{flag=1}/Device Properties.*/{flag=0}flag'> VKDsurface.txt" % (
                        GPU, GPU + 1))
                os.system(
                    "cat .Temp/vulkaninfo.txt | awk '/Presentable Surfaces.*/{flag=1;next}/Device Properties and Extensions.*/{flag=0}flag' | awk '/GPU id       : %d.*/{flag=1;next}/VkSurfaceCapabilities.*/{flag=0}flag' | awk '{gsub(/count =.*/,'True');print}' | grep -v type >> VKDsurface.txt" % GPU)

        os.system("cat VKDsurface.txt | awk '{gsub(/= .*/,'True');print} ' > VKDsurface1.txt")
        os.system("cat VKDsurface.txt | grep -o =.* | grep -o ' .*' > VKDsurface2.txt")
        temp = []

        with open("VKDsurface2.txt", "r") as file1:
            for line in file1:
                temp.append(line)

        SurfaceRHS = []
        i = 0
        with open("VKDsurface.txt", "r") as file1:
            for line in file1:
                if "= " in line:
                    SurfaceRHS.append(temp[i])
                    i = i + 1
                else:
                    SurfaceRHS.append(" ")

        Surface = []
        with open("VKDsurface1.txt", "r") as file1:
            for line in file1:
                Surface.append(line)

        Surface = [i.strip('\n ') for i in Surface]
        SurfaceTab_Store.clear()
        TreeSurface.set_model(SurfaceTab_Store)

        for i in range(len(Surface)):
            if "====" in Surface[i]:
                continue
            if "type" in Surface[i]:
                continue
            if i % 2 == 0:
                background_color = "#fff"
            else:
                background_color = "#ddd"
            if "VkSurfaceCapabilities"  in Surface[i] or "Modes" in Surface[i] or "Formats" in Surface[i] or "Extent" in Surface[i] or "supported" in Surface[i] or "current" in Surface[i]:
                background_color = "#bbb"
            text = Surface[i].strip('\t')
            SurfaceTab_Store.append([text, SurfaceRHS[i].strip('\n'), background_color])

    def radcall(combo):
        text = combo.get_active()
        for i in range(len(list)):
            if text == i:
                Devices(text)
                Features(text)
                Limits(text)
                Extensions(text)
                Format(text)
                MemoryTypes(text)
                Queues(text)
                Surface(text)
            Instance()
        os.system("rm VKD*.txt")

    grid = Gtk.Grid()
    tab2.add(grid)
    DevicesFrame = Gtk.Frame()
    grid.add(DevicesFrame)

    notebook = Gtk.Notebook()
    grid.attach(notebook, 0, 2, 1, 1)
    # ----------------Creating the Device Info Tab ------------
    DeviceTab = Gtk.VBox(spacing=10)
    DeviceTab.set_border_width(10)
    notebook.append_page(DeviceTab, Gtk.Label('Device'))
    DeviceFrame = Gtk.Frame()
    DeviceTab.add(DeviceFrame)
    DeviceGrid = Gtk.Grid()
    DeviceFrame.add(DeviceGrid)

    DeviceTab_Store = Gtk.ListStore(str, str, str)
    TreeDevice = Gtk.TreeView(DeviceTab_Store, expand=True)
    for i, column_title in enumerate(DeviceTitle):
        Devicerenderer = Gtk.CellRendererText(font=("%s" % FONT))
        column = Gtk.TreeViewColumn(column_title, Devicerenderer, text=i)
        column.add_attribute(Devicerenderer, "background", 2)
        if i == 0:
            column.set_property("min-width", 300)
        TreeDevice.append_column(column)

    DeviceScrollbar = Gtk.ScrolledWindow()
    DeviceScrollbar.set_vexpand(True)
    DeviceScrollbar.add(TreeDevice)
    DeviceGrid.add(DeviceScrollbar)

    SparseFrame = Gtk.Frame()
    DeviceTab.add(SparseFrame)
    SparseGrid = Gtk.Grid()
    SparseFrame.add(SparseGrid)

    SparseTab_Store = Gtk.ListStore(str, str, str, str)
    TreeSparse = Gtk.TreeView(SparseTab_Store, expand=True)

    for i, column_title in enumerate(SparseTitle):
        Sparserenderer = Gtk.CellRendererText(font=FONT)
        column = Gtk.TreeViewColumn(column_title, Sparserenderer, text=i)
        if i == 1:
            column.add_attribute(Sparserenderer, "foreground", 3)
        column.add_attribute(Sparserenderer, "background", 2)
        TreeSparse.append_column(column)

    SparseScrollbar = Gtk.ScrolledWindow()
    SparseScrollbar.set_vexpand(True)
    SparseScrollbar.add(TreeSparse)
    SparseGrid.add(SparseScrollbar)

    # -----------------Creating the Features Tab-----------------
    FeatureTab = Gtk.VBox(spacing=10)
    FeatureTab.set_border_width(10)
    notebook.append_page(FeatureTab, Gtk.Label('Features'))
    FeaturesFrame = Gtk.Frame()
    FeatureTab.add(FeaturesFrame)
    FeaturesGrid = Gtk.Grid()
    FeaturesFrame.add(FeaturesGrid)

    FeaturesTab_Store = Gtk.ListStore(str, str, str, str)
    TreeFeatures = Gtk.TreeView(FeaturesTab_Store, expand=True)
    for i, column_title in enumerate(FeaturesTitle):
        Featurerenderer = Gtk.CellRendererText(font=FONT)
        column = Gtk.TreeViewColumn(column_title, Featurerenderer, text=i)
        if i == 1:
            column.add_attribute(Featurerenderer, "foreground", 3)
        column.add_attribute(Featurerenderer, "background", 2)
        if i == 0:
            column.set_property("min-width", 300)
        TreeFeatures.append_column(column)

    FeatureScrollbar = Gtk.ScrolledWindow()
    FeatureScrollbar.set_vexpand(True)
    FeatureScrollbar.add(TreeFeatures)
    FeaturesGrid.add(FeatureScrollbar)

    # ------------ Creating the Limits Tab -------------------------------------------
    LimitsTab = Gtk.VBox(spacing=10)
    LimitsTab.set_border_width(10)
    notebook.append_page(LimitsTab, Gtk.Label("Limits"))
    LimitsFrame = Gtk.Frame()
    LimitsTab.add(LimitsFrame)
    LimitsGrid = Gtk.Grid()
    LimitsFrame.add(LimitsGrid)

    LimitsTab_Store = Gtk.ListStore(str, str, str)
    TreeLimits = Gtk.TreeView(LimitsTab_Store, expand=True)
    for i, column_title in enumerate(LimitsTitle):
        Limitsrenderer = Gtk.CellRendererText(font=FONT)
        column = Gtk.TreeViewColumn(column_title, Limitsrenderer, text=i)
        column.add_attribute(Limitsrenderer, "background", 2)
        if i == 0:
            column.set_property("min-width", 300)
        TreeLimits.append_column(column)

    LimitsScrollbar = Gtk.ScrolledWindow()
    LimitsScrollbar.set_vexpand(True)
    LimitsScrollbar.add(TreeLimits)
    LimitsGrid.add(LimitsScrollbar)

    # ------------ Creating the Extensions Tab-------------------------------------------

    ExtensionTab = Gtk.VBox(spacing=10)
    ExtensionTab.set_border_width(10)
    notebook.append_page(ExtensionTab, Gtk.Label("Extensions"))
    ExtensionFrame = Gtk.Frame()
    ExtensionTab.add(ExtensionFrame)
    ExtensionGrid = Gtk.Grid()
    ExtensionFrame.add(ExtensionGrid)

    ExtensionTab_Store = Gtk.ListStore(str, str, str)
    TreeExtension = Gtk.TreeView(ExtensionTab_Store, expand=True)
    for i, column_title in enumerate(ExtensionsTitle):
        Extensionrenderer = Gtk.CellRendererText(font=FONT)
        column = Gtk.TreeViewColumn(column_title, Extensionrenderer, text=i)
        column.add_attribute(Extensionrenderer, "background", 2)
        if i == 0:
            column.set_property("min-width", 300)
        TreeExtension.append_column(column)

    ExtensionScrollbar = Gtk.ScrolledWindow()
    ExtensionScrollbar.set_vexpand(True)
    ExtensionScrollbar.add(TreeExtension)
    ExtensionGrid.add(ExtensionScrollbar)
    # ------------Creating the Formats Tab --------------------------------------------------

    FormatsTab = Gtk.VBox(spacing=10)
    FormatsTab.set_border_width(10)
    notebook.append_page(FormatsTab, Gtk.Label("Formats"))
    FormatsFrame = Gtk.Frame()
    FormatsTab.add(FormatsFrame)
    FormatsGrid = Gtk.Grid()
    FormatsFrame.add(FormatsGrid)

    FormatsTab_Store = Gtk.ListStore(str, str, str, str, str, str, str, str)
    TreeFormats = Gtk.TreeView(FormatsTab_Store, expand=True)

    for i, column_title in enumerate(FormatsTitle):
        Formatsrenderer = Gtk.CellRendererText(font=FONT)
        column = Gtk.TreeViewColumn(column_title, Formatsrenderer, text=i)
        column.add_attribute(Formatsrenderer, "background", 4)
        if i == 0:
            column.set_property("min-width", 300)
        if i > 0:
            column.set_property("min-width", 100)
        if 1 <= i < 4:
            column.add_attribute(Formatsrenderer, "foreground", i + 4)
        TreeFormats.append_column(column)

    FormatsScrollbar = Gtk.ScrolledWindow()
    FormatsScrollbar.set_vexpand(True)
    FormatsScrollbar.add(TreeFormats)
    FormatsGrid.add(FormatsScrollbar)

    # ------------------------Memory Types & Heaps----------------------------------------------

    MemoryTab = Gtk.VBox(spacing=10)
    MemoryTab.set_border_width(10)
    notebook.append_page(MemoryTab, Gtk.Label("Memory Types & Heaps"))
    MemoryFrame = Gtk.Frame()
    MemoryTab.add(MemoryFrame)
    MemoryGrid = Gtk.Grid()
    MemoryFrame.add(MemoryGrid)

    MemoryTab_Store = Gtk.ListStore(int, int, str, str, str, str, str, str, str, str, str, str, str)
    TreeMemory = Gtk.TreeView(MemoryTab_Store, expand=True)

    for i, column_title in enumerate(MemoryTitle):
        Memoryrenderer = Gtk.CellRendererText(font=FONT)
        column = Gtk.TreeViewColumn(column_title, Memoryrenderer, text=i)
        column.add_attribute(Memoryrenderer, "background", 7)
        if 2 <= i < 7:
            column.set_property("min-width", 100)
            column.add_attribute(Memoryrenderer, "foreground", i + 6)
        TreeMemory.append_column(column)

    MemoryScrollbar = Gtk.ScrolledWindow()
    MemoryScrollbar.set_vexpand(True)
    MemoryScrollbar.add(TreeMemory)
    MemoryGrid.add(MemoryScrollbar)

    HeapFrame = Gtk.Frame()
    MemoryTab.add(HeapFrame)
    HeapGrid = Gtk.Grid()
    HeapFrame.add(HeapGrid)

    HeapTab_Store = Gtk.ListStore(int, str, str, str, str)
    TreeHeap = Gtk.TreeView(HeapTab_Store, expand=True)

    for i, column_title in enumerate(HeapTitle):
        Heaprenderer = Gtk.CellRendererText(font=FONT)
        column = Gtk.TreeViewColumn(column_title, Heaprenderer, text=i)
        if i == 1:
            column.set_property("min-width", 200)
        column.add_attribute(Heaprenderer, "background", 3)
        if i == 2:
            column.add_attribute(Heaprenderer, "foreground", 4)
        TreeHeap.append_column(column)

    HeapScrollbar = Gtk.ScrolledWindow()
    HeapScrollbar.set_vexpand(True)
    HeapScrollbar.add(TreeHeap)
    HeapGrid.add(HeapScrollbar)
    # -------------------------Creating the Queues Tab -----------------------------------------------------

    QueueTab = Gtk.VBox(spacing=10)
    QueueTab.set_border_width(10)
    notebook.append_page(QueueTab, Gtk.Label("Queues"))
    QueueFrame = Gtk.Frame()
    QueueTab.add(QueueFrame)
    QueueGrid = Gtk.Grid()
    QueueFrame.add(QueueGrid)

    QueueTab_Store = Gtk.ListStore(int, int, int, str, str, str, str, str, str, str, str, str, str, str, str)
    TreeQueue = Gtk.TreeView(QueueTab_Store, expand=True)

    for i, column_title in enumerate(QueueTitle):
        Queuerenderer = Gtk.CellRendererText(font=FONT)
        column = Gtk.TreeViewColumn(column_title, Queuerenderer, text=i)
        column.add_attribute(Queuerenderer, "background", 10)
        if 2 < i < 7:
            column.add_attribute(Queuerenderer, "foreground", i + 8)
        TreeQueue.append_column(column)

    QueueScrollbar = Gtk.ScrolledWindow()
    QueueScrollbar.set_vexpand(True)
    QueueScrollbar.add(TreeQueue)
    QueueGrid.add(QueueScrollbar)

    # -------------------------Creating the Instances & Layers ---------------------------------------------


    InstanceTab = Gtk.VBox(spacing=10)
    InstanceTab.set_border_width(10)
    notebook.append_page(InstanceTab, Gtk.Label("Instance Extensions & Layers"))
    InstanceFrame = Gtk.Frame()
    InstanceTab.add(InstanceFrame)
    InstanceGrid = Gtk.Grid()
    InstanceFrame.add(InstanceGrid)

    InstanceTab_Store = Gtk.ListStore(str, str, str)
    TreeInstance = Gtk.TreeView(InstanceTab_Store, expand=True)

    for i, column_title in enumerate(InstanceTitle):
        Instancerenderer = Gtk.CellRendererText(font=FONT)
        column = Gtk.TreeViewColumn(column_title, Instancerenderer, text=i)
        column.add_attribute(Instancerenderer, "background", 2)
        TreeInstance.append_column(column)

    InstanceScrollbar = Gtk.ScrolledWindow()
    InstanceScrollbar.set_vexpand(True)
    InstanceScrollbar.add(TreeInstance)
    InstanceGrid.add(InstanceScrollbar)

    LayerFrame = Gtk.Frame()
    InstanceTab.add(LayerFrame)
    LayerGrid = Gtk.Grid()
    LayerFrame.add(LayerGrid)

    LayerTab_Store = Gtk.ListStore(str, str, str, str, str)
    TreeLayer = Gtk.TreeView(LayerTab_Store, expand=True)

    for i, column_title in enumerate(LayerTitle):
        Layerrenderer = Gtk.CellRendererText(font=FONT)
        column = Gtk.TreeViewColumn(column_title, Layerrenderer, text=i)
        column.add_attribute(Layerrenderer, "background", 4)
        TreeLayer.append_column(column)

    LayerScrollbar = Gtk.ScrolledWindow()
    LayerScrollbar.set_vexpand(True)
    LayerScrollbar.add(TreeLayer)
    LayerGrid.add(LayerScrollbar)

    # ------------------ Creating the Surface Tab --------------------------------------------------
    SurfaceTab_Store = Gtk.ListStore(str, str, str)
    TreeSurface = Gtk.TreeView(SurfaceTab_Store, expand=True)
    with open(".Temp/vulkaninfo.txt", "r") as file1:
        for line in file1:
            if "VkSurfaceCapabilities" in line:
                SurfaceTab = Gtk.VBox(spacing=10)
                SurfaceTab.set_border_width(10)
                notebook.append_page(SurfaceTab, Gtk.Label("Surface"))
                SurfaceFrame = Gtk.Frame()
                SurfaceTab.add(SurfaceFrame)
                SurfaceGrid = Gtk.Grid()
                SurfaceFrame.add(SurfaceGrid)

                for i, column_title in enumerate(SurfaceTitle):
                    Surfacerenderer = Gtk.CellRendererText(font=FONT)
                    column = Gtk.TreeViewColumn(column_title, Surfacerenderer, text=i)
                    column.add_attribute(Surfacerenderer, "background", 2)
                    TreeSurface.append_column(column)

                SurfaceScrollbar = Gtk.ScrolledWindow()
                SurfaceScrollbar.set_vexpand(True)
                SurfaceScrollbar.add(TreeSurface)
                SurfaceGrid.add(SurfaceScrollbar)
                break

    DevicesGrid = Gtk.Grid()
    DevicesGrid.set_border_width(20)
    DevicesGrid.set_column_spacing(40)
    DevicesFrame.add(DevicesGrid)

    #	grid.set_column_spacing(40)
    grid.set_row_spacing(30)
    os.system("cat .Temp/vulkaninfo.txt | grep Name | grep -o  =.* | grep -o ' .*' > .Temp/GPU.txt")

    with open(".Temp/GPU.txt", "r") as file2:
        list = []
        file2.seek(0, 0)
        for line in file2:
            list.append(line)

    list = [i.strip('\n ') for i in list]

    DS = Gtk.Label()
    DS.set_text("Available Device(s) :")
    DevicesGrid.attach(DS, 0, 1, 1, 1)
    gpu_store = Gtk.ListStore(str)
    for i in list:
        #		print(i)
        gpu_store.append([i])

    gpu_combo = Gtk.ComboBox.new_with_model(gpu_store)
    gpu_combo.connect("changed", radcall)
    renderer_text = Gtk.CellRendererText()
    gpu_combo.pack_start(renderer_text, True)
    gpu_combo.add_attribute(renderer_text, "text", 0)
    gpu_combo.set_entry_text_column(0)
    gpu_combo.set_active(0)

    DevicesGrid.attach_next_to(gpu_combo, DS, Gtk.PositionType.RIGHT, 20, 1)

    tab2.show_all()
