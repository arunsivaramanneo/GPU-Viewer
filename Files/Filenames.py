mkdir_output_command = ["mkdir /tmp/gpu-viewer"]
rmdir_output_command = ["rm /tmp/gpu-viewer -r"]
vulkaninfo_output_command = ["vulkaninfo --show-formats"]
vdpauinfo_output_command = ["vdpauinfo"]
clinfo_output_command = ["clinfo -a | awk '/Number of platforms/{flag=1;print}/NULL.*/{flag=0}flag' "]
opengl_output_command = ["glxinfo -s"]
fetch_vulkaninfo_ouput_command = "cat /tmp/gpu-viewer/vulkaninfo.txt |"

fetch_screen_resolution_command = "xdpyinfo | awk '/dimensions/{print $2}'"
#------------------------- Command Commands --------------------------------

remove_rhs_Command = "awk '{gsub(/[=,:].*/,'True')l}1' | awk '/./' "
remove_lhs_command = "grep -o [=,:].* | grep -o ' .*' "



# ---------------------------Vulkan Tab - Commands and Filenames -------------------------------------

gpu_viewer_folder_path = "/tmp/gpu-viewer"

vulkaninfo_output_file = "/tmp/gpu-viewer/vulkaninfo.txt"

# --------------------------- Vulkan Deviceinfo - Commands and Filenames -------------------------

vulkan_device_info_file = "/tmp/gpu-viewer/VKDDeviceinfotemp.txt"
vulkan_device_info_lhs_file = "/tmp/gpu-viewer/VKDDeviceinfotempLHS.txt"
vulkan_device_info_rhs_file = "/tmp/gpu-viewer/VKDDeviceinfotempRHS.txt"

vulkan_summary_command = "vulkaninfo --summary"

fetch_device_name_command = " grep deviceName | grep -o  =.* | grep -o ' .*' "

#---------------------------- Vulkan Properties and Commands -----------------------------------------------

vulkan_device_properties_file = "/tmp/gpu-viewer/VKDDevicePropertiesTemp.txt"
vulkan_device_filter_properties_file = "/tmp/gpu-viewer/VKDDevicePropertiesFilterTemp.txt"
vulkan_device_filter_properties_lhs_file = "/tmp/gpu-viewer/VKDDevicePropertiesFilterLHSTemp.txt"

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


#-------------------vulkan Device Surface Filenames -------------------------------------------------------------------------------

vulkan_device_surface_file = "/tmp/gpu-viewer/VKDDeviceSurfaceTemp.txt"

#-------------------vulkan Device Groups Filenames -------------------------------------------------------------------------------

vulkan_device_groups_file = "/tmp/gpu-viewer/VKDDeviceGroupsTemp.txt"


#-------------------------- OpenGL Files and Commands --------------------------------------------------------

opengl_outpuf_file = "/tmp/gpu-viewer/glxinfo.txt"
opengl_device_info_file = "/tmp/gpu-viewer/opengl_information.txt"
opengl_info_lhs_file = "/tmp/gpu-viewer/opengl_information_lhs.txt"
opengl_info_rhs_file = "/tmp/gpu-viewer/opengl_information_rhs.txt"
opengl_vendor_gl_extension_file = "/tmp/gpu-viewer/opengl_vendor_gl_extension.txt"
opengl_vendor_es_extension_file = "/tmp/gpu-viewer/opengl_vendor_es_extension.txt"
egl_vendor_extension_file = "/tmp/gpu-viewer/egl_vendor_extension.txt"


fetch_opengl_vendor_extensions_command = "cat %s | awk '/OpenGL extensions/{flag=1;next}/OpenGL ES profile/{flag=0} flag' | grep GL_ | sort" %(opengl_outpuf_file)
fetch_openglx_vendor_extensions_command ="cat %s  | awk '/client glx extensions/{flag=1; next}/GLX version/{flag=0} flag' | grep GLX_ | sort" %(opengl_outpuf_file)

fetch_opengl_es_vendor_extensions_command = "cat %s  | awk '/OpenGL ES profile/{flag=1;next}/80 GLX Visuals/{flag=0} flag' | grep GL_ | sort" %(opengl_outpuf_file)

fetch_egl_vendor_extension_command = "es2_info | awk '/EGL_EXTENSIONS.*/{flag=1;next}/EGL_CLIENT.*/{flag=0}flag'| awk '{n=split($0,a,/,/);{for (i=1;i<=n;i++) print a[i]}}' | grep -o EGL.* "

#----------------------- OpenGL Limits ------------------------------------------------------------------------------------------------------------------

opengl_core_limits_lhs_file = "/tmp/gpu-viewer/opengl_core_limits_lhs.txt"
opengl_core_limits_file = "/tmp/gpu-viewer/opengl_core_limits.txt"

fetch_opengl_core_limits_command = "glxinfo -l | awk '/OpenGL core profile limits:/{flag=1}/GLX Visuals.*/{flag=0} flag' | awk '/OpenGL core profile limits:/{flag=1;next}/OpenGL version string.*/{flag=0} flag' | awk '/./' "
fetch_opengl_core_limits_lhs_command = "cat %s | awk '{gsub(/=.*/,'True');print}' " %(opengl_core_limits_file)

opengl_compat_limits_file = "/tmp/gpu-viewer/opengl_compat_limits.txt"

opengl_compat_limits_lhs_file = "/tmp/gpu-viewer/opengl_compat_limits_lhs.txt"

fetch_opengl_compat_limits_command = "glxinfo -l | awk '/OpenGL limits:/{flag=1}/GLX Visuals.*/{flag=0} flag' | awk '/OpenGL limits:/{flag=1;next}/OpenGL ES profile/{flag=0} flag' | awk '/./' "

fetch_opengl_compat_limits_lhs_command = "cat %s | awk '{gsub(/=.*/,'True');print}'" %(opengl_compat_limits_file)

select_opengl_limits_file = "/tmp/gpu-viewer/selectOpenglLimits.txt"


#-------------------------------------------- Clinfo filenames and Commands -------------------------------------------------------------------

opencl_output_file = "/tmp/gpu-viewer/clinfo.txt"

opencl_plaform_and_device_names_file = "/tmp/gpu-viewer/PlatnDev.txt"


fetch_platform_and_device_names_command = "clinfo -l"

fetch_platform_names_command = "cat %s | grep Platform | grep -o :.* | grep -o ' .*' " %(opencl_plaform_and_device_names_file)

opencl_platform_details_file = "/tmp/gpu-viewer/oclPlatformDetails.txt"

fetch_platform_details_lhs_command = "cat %s | grep -o Platform.* | awk '{gsub(/  .*/,'True');print}' " %(opencl_platform_details_file)

fetch_platform_details_rhs_command = "cat %s | grep -o Platform.* | awk '{gsub(/Platform.*  /,'True');print}'" %(opencl_platform_details_file)

opencl_device_details_file = "/tmp/gpu-viewer/oclDeviceDetails.txt"

fetch_device_details_lhs_command = "cat %s | awk '{gsub(/     .*/,'True');print}'" %(opencl_device_details_file)
fetch_device_details_rhs_command = "cat %s | awk '{gsub(/^ .*        /,'True');print}'" %(opencl_device_details_file)

opencl_device_memory_and_image_file = "/tmp/gpu-viewer/oclDeviceMemoryImageDetails.txt"

fetch_device_memory_and_image_details_lhs_command = "cat %s | awk '{gsub(/     .*/,'True');print}'" %(opencl_device_memory_and_image_file)
fetch_device_memory_and_image_details_rhs_command = "cat %s | awk '{gsub(/^ .*        /,'True');print}'" %(opencl_device_memory_and_image_file)

opencl_device_vector_file = "/tmp/gpu-viewer/oclDeviceVectorDetails.txt"

fetch_device_vector_details_lhs_command = "cat %s | awk '{gsub(/     .*/,'True');print}'" %(opencl_device_vector_file)
fetch_device_vector_details_rhs_command = "cat %s | awk '{gsub(/^ .*        /,'True');print}'" %(opencl_device_vector_file)

opencl_device_queue_execution_details_file = "/tmp/gpu-viewer/oclDeviceQueueExecutionDetails.txt"

fetch_device_queue_execution_details_lhs_command = "cat %s | awk '{gsub(/     .*/,'True');print}'" %(opencl_device_queue_execution_details_file)
fetch_device_queue_execution_details_rhs_command = "cat %s | awk '{gsub(/^ .*        /,'True');print}'" %(opencl_device_queue_execution_details_file)

# ------------------------------------------- VDPAUINFO filenames and Commands ------------------------------------------------------------

vdpauinfo_output_file = "/tmp/gpu-viewer/vdpauinfo.txt"

#---------------------------------------------- Themes Folder ----------------------------------------------------------------------------------------------------

Orchis_gtk_theme_folder = "/usr/share/themes/Orchis"
Materia_gtk_theme_folder = "/usr/share/themes/Materia"
Roboto_font_folder = "/usr/share/fonts/truetype/roboto"