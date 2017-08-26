# GPU-Viewer
A front-end to glxinfo and Vulkaninfo. 

This project aims to capture all the required/important details of glxinfo and vulkaninfo in a GUI. The project is being developed using python 3 with tkinter (python3-tk). All the required/Important details were extracted using glxinfo/vulkaninfo with the combination of grep, CAT , AWK commands and displayed in the front-end. There is no hard OpenGL Programming involved, until glxinfo and vulkaninfo works the GPU-viewer will also work



What's developed and available?

1. OpenGL Information, OpenGL ES Information, OpenGL hardware limits and Extensions displayed as per different Vendors.
2. Vulkan - Device Features, Device Limits, Device Extensions have been fully developed and available to the end users,Formats,Memory Types


UNDERDEVELOPMENT

1. OpenGL - Frame Buffer configuration is underdevelopment
2. Vulkan - Memory Heap, Queue Family

IMPORTANT

1. Need Python 3 and python3-tk to run this Application, works only on linux Operating system
2. Tested on Intel and Nvidia hardware
3. For Vulkaninfo to work, nvidia, Mesa and nvidia vulkan enabled drivers should be installed
4. Vulkaninfo should work fine on 2 way and 3 way SLI/crossfire.

KNOWN ISSUES

1. Currentl 4 Way SLI/crossfire will not work
2. Minor UI issues.
3. Not tested on hardware other than Intel and Nvidia
