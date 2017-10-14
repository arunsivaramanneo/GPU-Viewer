# GPU-Viewer
A front-end to glxinfo and Vulkaninfo. 

This project aims to capture all the required/important details of glxinfo and vulkaninfo in a GUI. The project is being developed using python 3 PyGObjects with GTK3. All the required/Important details were extracted using glxinfo/vulkaninfo with the combination of grep, CAT , AWK commands and displayed in the front-end. There is no hard OpenGL Programming involved, until glxinfo and vulkaninfo works the GPU-viewer will also work

![gpu viewer v1 1_008](https://user-images.githubusercontent.com/30646692/31576187-97a6ffdc-b113-11e7-8195-bfcfe3a3a4a3.png)
![gpu viewer v1 1_010](https://user-images.githubusercontent.com/30646692/31576204-cab6826c-b113-11e7-8d38-ded1934c08dc.png)

## INSTALLATION STEPS

#### Ubuntu

1. Before Downloading the files please see the Known issues below
2. Ensure python3 or higher is installed.
3. Download the file and Extract to a folder
4. Double click GPU Viewer to launch the Application or You can go to Files and then open terminal and run/type python GPU_Viewer.py
5. For Vulkan Tab to work Install Vulkan-Utils(Ubuntu)/(Sudo apt-get install vulkan-utils),also Vulkan enabled drivers should be installed.

#### Arch 

1. Before Downloading the files please see the Known issues below
2. Ensure python 3 is installed
3. Download the file and Extract to a folder
4. Double click GPU Viewer to launch the Application or You can go to Files and then open terminal and run/type python3 GPU_Viewer.py
5. For Vulkan Tab to work Install vulkan-extra-layers(Arch),also Vulkan enabled drivers should be installed.


## What's developed and available?

1. OpenGL Tab - OpenGL Information, OpenGL ES Information, OpenGL hardware limits and Extensions displayed as per different Vendors
2. Vulkan Tab - Device Features, Device Limits, Device Extensions,Formats,Memory Types & Heaps, Partial Queue Families implemented, Instance and Layers,Surface Tab
3. About Tab - About GPU Viewer Application, Change Log


## UNDERDEVELOPMENT

1. OpenGL - GLX Frame Buffer Configuration, OpenGL SPIRV support (low priority - this feature is not available in glxinfo yet,it will be done once implemented by MESA team)
2. General - Bug fixes, Code Optimizations (High Priority)

## IMPORTANT

1. Requires Python 3 pyGObjects to run this Application, works only on linux Operating system
2. Tested on Intel and Nvidia hardware
3. For Vulkaninfo to work, nvidia, Mesa and AMD vulkan enabled drivers should be installed along with vulkan-utils
4. Vulkan Tab should work fine for multi-gpu setup.

## KNOWN ISSUES

1. Minor UI issues.
2. Not tested on hardware other than Intel and Nvidia
3. GLX Frame Buffer Configuration should work almost fine If there are any Blank values in the report the alignment   goes out(mainly in GLXFBConfigs). Yet to figure out a fix.

## DEVELOPMENT ENVIRONMENT

1. Operating System : Linux Mint 18.2 (Sonya)
2. Desktop : Cinnamon 3.4.6
3. Kernel : 4.10.0-33
4. IDE : SublimeText 3.0

## SYSTEM SETUP

1. ASUS G551JK ROG Laptop
2. Quad Core Intel Core i7-4710HQ
3. Nvidia Geforce GTX 850m (Discrete GPU) , Drivers - Nvidia (proprietary)
4. Intel Haswel Mobile (Integrated GPU) , Drivers - MESA (Open Source)
5. 8 GB RAM

If you like/use this Application and think i deserve a cup of chai, do a Paypal donation: https://www.paypal.me/ArunSivaraman
