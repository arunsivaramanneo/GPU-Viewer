mkdir_output_command = ["mkdir /tmp/gpu-viewer"]
vulkaninfo_output_command = ["vulkaninfo"]
vdpauinfo_output_command = ["vdpauinfo"]
clinfo_output_command = ["clinfo -a | awk '/Number of platforms/{flag=1;print}/NULL.*/{flag=0}flag' "]
opengl_output_command = ["glxinfo","-s"]
fetch_vulkaninfo_ouput_command = "cat /tmp/gpu-viewer/vulkaninfo.txt |"

#------------------------- Command Commands --------------------------------

remove_rhs_Command = "awk '{gsub(/[=,:].*/,'True');}1'"

# ---------------------------Vulkan Tab - Commands and Filenames -------------------------------------

vulkaninfo_output_file = "/tmp/gpu-viewer/vulkaninfo.txt"

# --------------------------- Vulkan Deviceinfo - Commands and Filenames -------------------------

vulkan_device_info_file = "/tmp/gpu-viewer/VKDDeviceinfotemp.txt"
vulkan_device_info_lhs_file = "/tmp/gpu-viewer/VKDDeviceinfotempLHS.txt"
vulkan_device_info_rhs_file = "/tmp/gpu-viewer/VKDDeviceinfotempRHS.txt"

vulkan_summary_command = "vulkaninfo --summary"

fetch_device_name_command = " | grep deviceName | grep -o  =.* | grep -o ' .*' "

#------------------- Vulkan Features Files and Commands ------------------------------------------------

vulkan_device_features_file = "/tmp/gpu-viewer/VKDDeviceFeaturesTemp.txt"
vulkan_device_features_lhs_file = "/tmp/gpu-viewer/VKDDeviceFeaturesLHS.txt"
vulkan_device_features_select_file = "/tmp/gpu-viewer/VKDDeviceFeaturesRHS.txt"

#---------------------Vulkan Extensions File and Command Name ------------------------------------

vulkan_device_extensions_file = "/tmp/gpu-viewer/VKDDeviceExtensionTemp.txt"
vulkan_device_extension_lhs_file = "/tmp/gpu-viewer/VKDDeviceExtensionLHS.txt"
vulkan_device_extension_rhs_file = "/tmp/gpu-viewer/VKDDeviceExtensionRHS.txt"

#........................ Vulkan Limits commands and File Names -------------------------------------

vulkan_device_limits_file = "/tmp/gpu-viewer/VKDDeviceLimitstemp.txt"
vulkan_device_limits_lhs_file = "/tmp/gpu-viewer/VKDDeviceLimitsLHS.txt"
vulkan_device_limits_rhs_file = "/tmp/gpu-viewer/VKDDeviceLimitsRHS.txt"











#-------------------------- OpenGL Files and Commands --------------------------------------------------------

opengl_device_info_file = "/tmp/gpu-viewer/OpenGL_Information.txt"