mkdir_output_command = ["mkdir /tmp/gpu-viewer"]
rmdir_output_command = ["rm /tmp/gpu-viewer -r"]
vulkaninfo_output_command = ["vulkaninfo --show-formats"]
vdpauinfo_output_command = ["vdpauinfo"]
clinfo_output_command = ["clinfo -a | awk '/Number of platforms/{flag=1;print}/NULL.*/{flag=0}flag' "]
opengl_output_command = ["glxinfo","-s"]
fetch_vulkaninfo_ouput_command = "cat /tmp/gpu-viewer/vulkaninfo.txt |"

#------------------------- Command Commands --------------------------------

remove_rhs_Command = "awk '{gsub(/[=,:].*/,'True')l}1' | awk '/./' "
remove_lhs_command = "grep -o [=,:].* | grep -o ' .*' "

# ---------------------------Vulkan Tab - Commands and Filenames -------------------------------------

vulkaninfo_output_file = "/tmp/gpu-viewer/vulkaninfo.txt"

# --------------------------- Vulkan Deviceinfo - Commands and Filenames -------------------------

vulkan_device_info_file = "/tmp/gpu-viewer/VKDDeviceinfotemp.txt"
vulkan_device_info_lhs_file = "/tmp/gpu-viewer/VKDDeviceinfotempLHS.txt"
vulkan_device_info_rhs_file = "/tmp/gpu-viewer/VKDDeviceinfotempRHS.txt"

vulkan_summary_command = "vulkaninfo --summary"

fetch_device_name_command = " grep deviceName | grep -o  =.* | grep -o ' .*' "

#------------------- Vulkan Features Files and Commands ------------------------------------------------

vulkan_device_features_file = "/tmp/gpu-viewer/VKDDeviceFeaturesTemp.txt"
vulkan_device_features_lhs_file = "/tmp/gpu-viewer/VKDDeviceFeaturesLHS.txt"
vulkan_device_features_select_file = "/tmp/gpu-viewer/VKDDeviceFeaturesRHS.txt"

#---------------------Vulkan Extensions File and Command Name ------------------------------------

vulkan_device_extensions_file = "/tmp/gpu-viewer/VKDDeviceExtensionTemp.txt"
vulkan_device_extension_lhs_file = "/tmp/gpu-viewer/VKDDeviceExtensionLHS.txt"
vulkan_device_extension_rhs_file = "/tmp/gpu-viewer/VKDDeviceExtensionRHS.txt"

#........................ Vulkan Limits commands and File Names -------------------------------------

vulkan_device_limits_file = "/tmp/gpu-viewer/VKDDeviceLimitsTemp.txt"
vulkan_device_limits_lhs_file = "/tmp/gpu-viewer/VKDDeviceLimitsLHS.txt"
vulkan_device_limits_rhs_file = "/tmp/gpu-viewer/VKDDeviceLimitsRHS.txt"

#.........................Vulkan Formats Commands and File Names ----------------------------------

vulkan_device_formats_file = "/tmp/gpu-viewer/VKDDeviceFormatsTemp.txt"
vulkan_device_formats_types_file = "/tmp/gpu-viewer/VKDDeviceFormatsTypesTemp.txt"
vulkan_device_format_types_count_file = "/tmp/gpu-viewer/VKDDeviceFormatTypesCountTemp.txt"
vulkan_device_format_types_linear_count_file = "/tmp/gpu-viewer/VKDDeviceFormatTypesLinearCountTemp.txt"
vulkan_device_format_types_optimal_count_file = "/tmp/gpu-viewer/VKDDeviceFormatTypesOptimalCountTemp.txt"
vulkan_device_format_types_buffer_count_file = "/tmp/gpu-viewer/VKDDeviceFormatTypesBufferCountTemp.txt"
vulkan_device_format_types_linear_file = "/tmp/gpu-viewer/VKDDeviceFormatTypesLinearTypesTemp.txt"
vulkan_device_format_types_optimal_file = "/tmp/gpu-viewer/VKDDeviceFormatTypesOptimalTypesTemp.txt"
vulkan_device_format_types_buffer_file = "/tmp/gpu-viewer/VKDDeviceFormatTypesBufferTypesTemp.txt"

#----------------------Vulkan Device Memory Types Commands and File Names ----------------------------------

vulkan_device_memory_types_file = "/tmp/gpu-viewer/VKDDeviceMemoryTypesTemp.txt"
vulkan_device_memory_types_lhs_file = "/tmp/gpu-viewer/VKDDeviceMemoryTypesLHS.txt"
vulkan_device_memory_types_rhs_file = "/tmp/gpu-viewer/VKDDeviceMemoryTypesRHS.txt"
vulkan_device_memory_types_property_flags_file = "/tmp/gpu-viewer/VKDDeviceMemoryTypesPropertyFlagsTemp.txt"

#-----------------------Vulkan Device Memory Heaps Commands and File Names --------------------------------

vulkan_device_memory_heaps_file = "/tmp/gpu-viewer/VKDDeviceMemoryHeapsTemp.txt"
vulkan_device_memory_heaps_lhs_file = "/tmp/gpu-viewer/VKDDeviceMemoryHeapsLHSTemp.txt"
vulkan_device_memory_heaps_rhs_file = "/tmp/gpu-viewer/VKDDeviceMemoryHeapsRHSTemp.txt"


#---------------------- Vulkan Device Queues  Filenames --------------------------------------------------------------------------

vulkan_device_queues_file = "/tmp/gpu-viewer/VKDDeviceQueuesTemp.txt"
vulkan_device_queues_lhs_file = "/tmp/gpu-viewer/VKDDeviceQueuesLHSTemp.txt"
vulkan_device_queues_rhs_file = "/tmp/gpu-viewer/VKDDeviceQueuesRHSTemp.txt"
vulkan_device_queue_counts_file = "/tmp/gpu-viewer/VKDDeviceQueueCountTemp.txtS"

#------------------- vulkan Device instances Filenames -----------------------------------------------------------------------------

vulkan_device_instances_file = "/tmp/gpu-viewer/VKDDeviceInstancesTemp.txt"
vulkan_device_instances_lhs_file = "/tmp/gpu-viewer/VKDDeviceInstancesLHSTemp.txt"
vulkan_device_instances_rhs_file = "/tmp/gpu-viewer/VKDDeviceInstancesRHSTemp.txt"

#--------------------vulkan Device layers Filenames -----------------------------------------------------------------------------------

vulkan_device_layers_file = "/tmp/gpu-viewer/VKDDeviceLayersTemp.txt"
vulkan_device_layers_name_file = "/tmp/gpu-viewer/VKDDeviceLayerNames.txt"

#-------------------------- OpenGL Files and Commands --------------------------------------------------------

opengl_device_info_file = "/tmp/gpu-viewer/OpenGL_Information.txt"