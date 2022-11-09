mkdir_output_command = ["mkdir /tmp/gpu-viewer"]
vulkaninfo_output_command = ["vulkaninfo"]
vdpauinfo_output_command = ["vdpauinfo"]
clinfo_output_command = ["clinfo -a | awk '/Number of platforms/{flag=1;print}/NULL.*/{flag=0}flag' "]
opengl_output_command = ["glxinfo","-s"]

# ------------- Vulkan Tab Commands

vulkan_summary_command = "vulkaninfo --summary"

fetch_device_name_command = " | grep deviceName | grep -o  =.* | grep -o ' .*' "