# GPU-Viewer
A front-end to glxinfo, vulkaninfo and clinfo. 

This project aims to capture all the required/important details of glxinfo, vulkaninfo and clinfo in a GUI. The project is being developed using python 3 PyGObjects with GTK3. All the required/Important details were extracted using glxinfo/vulkaninfo with the combination of grep, CAT , AWK commands and displayed in the front-end. There is no hard OpenGL Programming involved, until glxinfo, vulkaninfo and clinfo works the GPU-viewer will also work

![screenshot from 2017-12-13 16 55 30](https://user-images.githubusercontent.com/30646692/33936761-a3da3df4-e026-11e7-9fc2-7d38ba267a54.png)

![screenshot from 2017-12-13 16 55 37](https://user-images.githubusercontent.com/30646692/33936766-a7bcd5f8-e026-11e7-86bf-b8067eea7db3.png)

![screenshot from 2017-12-13 16 55 43](https://user-images.githubusercontent.com/30646692/33936772-ae48970e-e026-11e7-9562-0b11fa551946.png)

![screenshot from 2017-12-13 16 55 48](https://user-images.githubusercontent.com/30646692/33936775-b2a2f86c-e026-11e7-8b80-30bf3668dbd6.png)

* Please note that the above images solely depends on the Theme being used on the system.

## INSTALLATION STEPS 

1. Before Downloading the files please see the Known issues mentioned below
2. Ensure python is installed
3. **Debian based distro** users should be able to install the application by just running the .deb file https://github.com/arunsivaramanneo/GPU-Viewer/blob/master/gpu-viewer-stable-1.3.deb
4. **Arch based distro** users should be able to grab the application at https://aur.archlinux.org/packages/gpu-viewer/ or by using command yaourt -s gpu-viewer from the terminal . This should automatically should take care of the dependencies.
5. For others please follow steps 6 to 9
6. Download the file and Extract to a folder
7. Navigate to extracted folder, open terminal and enter ./install and follow on-screen instruction.
8. Once completed,Application can be accessed at menu->System/Administration/System tools->GPU Viewer
9. For **Vulkan Tab** to work Install Vulkan-Utils (sudo apt install vulkan-utils) in Ubuntu, Vulkan-extra-layers in Arch, Vulkan in Solus, also Vulkan enabled drivers should be installed.
The installer should be able to take care of this dependency in Debian based distro and Solus.
10. For **OpenCL Tab** to work install clinfo (sudo apt install clinfo) in ubuntu , clinfo in Solus (sudo eopkg install clinfo), clinfo in arch. Also, ensure you have OpenCL installed for your respective platforms, Ex. Nvidia CUDA for Nvidia hardware, beignet for Intel Graphics or pocpl for cpu or AMD openCL for AMD hardware.
11. Some distro's don't come with glxinfo installed by default, so you will need to install mesa-utils to get the OpenGL Tab displayed properly.
12. Incase of issues launching the application please see the FAQ in Wiki section

## UNINSTALL STEPS

1. Debian users should be able to uninstall in the default way i.e. sudo apt remove gpu-viewer
2. For others, Remove gpu-viewer directory in \usr\share\  or run sudo rm \usr\share\gpu-viewer -r to remove. Also you need to remove the symlink sudo rm /usr/bin/gpu-viewer

## What's developed and available?

1. OpenGL Tab - OpenGL Information, OpenGL ES Information, OpenGL hardware limits and Extensions displayed as per different Vendors, View GLX Frame Buffer Configuration
2. Vulkan Tab - Device Features, Device Limits, Device Extensions,Formats,Memory Types & Heaps, Partial Queue Families implemented, Instance and Layers,Surface Tab
3. OpenCL Tab - Platform Details, Device Details , Device Memory & Image Details, Device Queue and Execution capabilities, Device Vector Details, Total No. of Platforms, No. of Devices for the platform.
4. About Tab - About GPU Viewer Application, ability to report a bug,view license,view change log, Donate via paypal, GPU Viewer Github main page.


## UNDER DEVELOPMENT

1. General - Bug fixes, Code Optimizations (High Priority)

## PLANNED DEVELOPMENT

1. OpenGL SPIRV Support (Provided glxinfo gets updated to show SPIRV details or any other Command line)

## IMPORTANT

1. Requires Python to run this Application, works only on linux Operating system
2. For Vulkan Tab to work, nvidia, Mesa and AMD vulkan enabled drivers should be installed along with vulkan-utils
3. For OpenCL Tab to work, install clinfo along with OpenCL drivers for your respective GPU's

## KNOWN ISSUES

1. Minor UI issues.
2. The Extensions drop down menu in OpenGL tab will not render well if there are too many items, users may see a big empty space at the start. This is a GTK issue (https://github.com/arunsivaramanneo/GPU-Viewer/issues/9)
3. The Application does not render well under dark themes.

## DEVELOPMENT ENVIRONMENT

1. Operating System : Linux Mint 18.2 (Sonya)/Solus 3/Ubuntu Budgie
2. Desktop : Cinnamon 3.6/Budgie 10.4
3. Kernel : 4.14.8
4. IDE : SublimeText 3.0,IntelliJ IDEA Community Edition


## SYSTEM SETUP

1. ASUS G551JK ROG Laptop
2. Quad Core Intel Core i7-4710HQ
3. Nvidia Geforce GTX 850m (Discrete GPU) , Drivers - Nvidia (proprietary)
4. Intel Haswel Mobile (Integrated GPU) , Drivers - MESA (Open Source)
5. 8 GB RAM

If you like/use this Application and think i deserve a cup of chai, do a Paypal donation: https://www.paypal.me/ArunSivaraman
