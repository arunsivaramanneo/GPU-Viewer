[![Build Status](https://travis-ci.org/flyingarg/GPU-Viewer.svg?branch=master)](https://travis-ci.org/flyingarg/GPU-Viewer)

# GPU-Viewer
A front-end to glxinfo and Vulkaninfo. 

This project aims to capture all the required/important details of glxinfo and vulkaninfo in a GUI. The project is being developed using python 3 PyGObjects with GTK3. All the required/Important details were extracted using glxinfo/vulkaninfo with the combination of grep, CAT , AWK commands and displayed in the front-end. There is no hard OpenGL Programming involved, until glxinfo and vulkaninfo works the GPU-viewer will also work

![gpu viewer v1 1_006](https://user-images.githubusercontent.com/30646692/31825959-5d71f2fa-b5d1-11e7-95d5-59139108c0ab.png)

![gpu viewer v1 1_004](https://user-images.githubusercontent.com/30646692/31717602-469b1b2c-b42a-11e7-94c0-1de3f0ca40ea.png)

* Please note that the above Images solely depends on the Theme being used on the system.

## INSTALLATION STEP

1. Before Downloading the files please see the Known issues below
2. Ensure python is installed
3. Download the file and Extract to a folder
4. Double click GPUViewer to launch the Application or You can go to Files and then open terminal and run/type python GPUViewer.py
5. For Vulkan Tab to work Install Vulkan-Utils (Sudo apt-get install vulkan-utils) in Ubuntu, Vulkan-extra-layers in Arch, Vulkan in Solus, also Vulkan enabled drivers should be installed.

6. Incase of issues launching the application please see the FAQ in Wiki section

## What's developed and available?

1. OpenGL Tab - OpenGL Information, OpenGL ES Information, OpenGL hardware limits and Extensions displayed as per different Vendors, View GLX Frame Buffer Configuration
2. Vulkan Tab - Device Features, Device Limits, Device Extensions,Formats,Memory Types & Heaps, Partial Queue Families implemented, Instance and Layers,Surface Tab
3. About Tab - About GPU Viewer Application, Change Log


## UNDERDEVELOPMENT

1. OpenGL - OpenGL SPIRV support (low priority - this feature is not available in glxinfo yet,it will be done once implemented by MESA team)
2. General - Bug fixes, Code Optimizations (High Priority)

## IMPORTANT

1. Requires Python to run this Application, works only on linux Operating system
2. For Vulkaninfo to work, nvidia, Mesa and AMD vulkan enabled drivers should be installed along with vulkan-utils

## KNOWN ISSUES

1. Minor UI issues.
2. Not tested on hardware other than Intel and Nvidia

## DEVELOPMENT ENVIRONMENT

1. Operating System : Linux Mint 18.2 (Sonya)
2. Desktop : Cinnamon 3.4.6
3. Kernel : 4.10.0-33
4. IDE : SublimeText 3.0,IntelliJ IDEA Community Edition


## SYSTEM SETUP

1. ASUS G551JK ROG Laptop
2. Quad Core Intel Core i7-4710HQ
3. Nvidia Geforce GTX 850m (Discrete GPU) , Drivers - Nvidia (proprietary)
4. Intel Haswel Mobile (Integrated GPU) , Drivers - MESA (Open Source)
5. 8 GB RAM

If you like/use this Application and think i deserve a cup of chai, do a Paypal donation: https://www.paypal.me/ArunSivaraman
