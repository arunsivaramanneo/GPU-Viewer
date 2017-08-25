# GPU-Viewer
A front-end to glxinfo and Vulkaninfo. 

This project aims to capture all the required/important details of glxinfo and vulkaninfo in a GUI. The project is being developed using python 3 with tkinter (python-tk). All the required/Important details were extracted using glxinfo/vulkaninfo with the combination of grep, CAT , AWK commands and displayed in the front-end. There is no hard OpenGL Programming involved, until glxinfo and vulkaninfo works the GPU-viewer will also work

What's developed and available?

1. OpenGL Information, OpenGL ES Information, OpenGL hardware limits and Extensions displayed as per different Vendors.
2. Vulkan - Device Features, Device Limits, Device Extensions have been fully developed and available to the end users,Memory Types


UNDERDEVELOPMENT

1. OpenGL - Frame Buffer configuration is underdevelopment
2. Vulkan - Vulkan Formats, Memory Heap, Queue Family

IMPORTANT

1. Need Python 3 and python tkinter to run this Application
2. Tested on Intel and Nvidia hardware
3. Vulkan should be installed for Vulkaninfo to work

KNOWN ISSUES

1. Currently Vulkaninfo works for 2 GPU setup, 3 Way SLI/Crossfire and 4 Way SLI/crossfire will not work
2. Minor UI issues.
