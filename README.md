# GPU-Viewer

### A front-end to glxinfo, vulkaninfo, clinfo and es2_info.


This project aims to capture all the important details of glxinfo, vulkaninfo and clinfo in a GUI. The project is being developed using python 3 pygobject with GTK3. All the important details are extracted using glxinfo/vulkaninfo/clinfo with the combination of grep, CAT , AWK commands and displayed in the front-end. There is no hard OpenGL Programming involved, until glxinfo, vulkaninfo and clinfo works the GPU-viewer will also work


![Screenshot from 2022-04-24 19-37-53](https://user-images.githubusercontent.com/30646692/164991416-b647a045-8f8f-4b98-9ea4-791ef262647c.png)


![Screenshot from 2022-04-24 19-38-07](https://user-images.githubusercontent.com/30646692/164991422-11aa9671-3ee3-4450-b0b9-e73fb6c80fe0.png)


![Screenshot from 2022-04-24 19-38-13](https://user-images.githubusercontent.com/30646692/164991428-0cca0696-018e-4154-b646-ddf08e00f768.png)


![Screenshot from 2022-04-24 19-38-18](https://user-images.githubusercontent.com/30646692/164991433-c44da2fa-4cf2-40be-aa9c-0a44c57b09df.png)


![Screenshot from 2022-04-24 19-38-28](https://user-images.githubusercontent.com/30646692/164991440-f17e9a18-44ee-43c1-96f9-6a64d044fd2e.png)



## INSTALLATION STEPS

**Those who are cloning and installing the application through install file, please note the application will work with vulkan tools 1.2.141 or higher, for anything below please use the PPA to install the latest stable version. Working on Integrating the latest vulkan tools to the installation**

1. Before Downloading the files please see the Known issues mentioned below
2. Ensure python is installed
3. **Ubuntu 22.04 (Jammy)/Ubuntu 21.10(Impish)/Ubuntu 21.04(Hirsute)/Ubuntu 20.04(Focal)/Ubuntu 18.04 (Bionic)/Linux Mint 20.x/Linux Mint 19.x** users should be able to install this application using the below PPA

    * sudo add-apt-repository ppa:arunsivaraman/gpuviewer
    * sudo apt-get update
    * sudo apt-get install gpu-viewer

    Please note all the dependencies python, vulkan-tools,clinfo, es2_info will be installed, if not installed before.

4. **Debian based distro** users should be able to install the application by just running the .deb file attached in the Release notes
5. **Arch based distro** - 	[![Packaging status](https://repology.org/badge/vertical-allrepos/gpu-viewer.svg)](https://repology.org/project/gpu-viewer/versions) - users should be able to grab the application at https://aur.archlinux.org/packages/gpu-viewer/ or by running command **yay -S gpu-viewer** from the terminal . This should automatically take care of the dependencies. Thanks to **Dan Johnson (strit)** for maintaining the AUR Package
6. **Fedora (RPM) based distro** run the command **sudo dnf -y install clinfo egl-utils mesa-demos mesa-vulkan-drivers python3 vdpauinfo vulkan-tools** from the terminal, then complete steps 7 to 10.
7. For others please follow steps 7 to 10
8. Download the file  and Extract to a folder
9. Navigate to extracted folder, open terminal and enter below commands
    - meson _build
    - cd _build
    - ninja install
10. Once completed,Application can be accessed at menu->System/Administration/System tools->GPU Viewer
11. For **Vulkan Tab** to work Install vulkan-tools (sudo apt-get install vulkan-tools) in Ubuntu, vulkan-tools in Arch, Vulkan in Solus, also Vulkan enabled drivers should be installed.
The installer should be able to take care of this dependency in Debian based distro and Solus.
12. For **OpenCL Tab** to work install clinfo (sudo apt install clinfo) in ubuntu , clinfo in Solus (sudo eopkg install clinfo), clinfo in arch. Also, ensure you have OpenCL installed for your respective platforms, Ex. Nvidia CUDA for Nvidia hardware, beignet for Intel Graphics or pocpl for cpu or AMD openCL for AMD hardware.
13. For **EGL** information to be displayed in OpenGL tab, users should install mesa-utils-extra package in Debian based systems. On Arch, Please install latest version of mesa-demos
14. For **VDPAU** information to be displayed, please install vdpauinfo.
15. Incase of issues launching the application please see the FAQ in Wiki section

## UNINSTALL STEPS

1. Debian users should be able to uninstall in the default way i.e. sudo apt remove gpu-viewer
2. For others, Remove gpu-viewer directory in \usr\share\  or run sudo rm \usr\share\gpu-viewer -r to remove. Also you need to remove the symlink by running sudo rm \usr\bin\gpu-viewer

## What's developed and available?

1. OpenGL Tab - OpenGL Information, OpenGL ES Information, OpenGL hardware limits and Extensions displayed as per different Vendors, View GLX Frame Buffer Configuration and EGL information, EGL Information
2. Vulkan Tab - Device Features, Device Limits, Device Extensions,Formats,Memory Types & Heaps, Partial Queue Families implemented, Instance and Layers,Surface Tab
3. OpenCL Tab - Platform Details, Device Details , Device Memory & Image Details, Device Queue and Execution capabilities, Device Vector Details, Total No. of Platforms, No. of Devices for the platform.
4. About Tab - About GPU Viewer Application, ability to report a bug,view license,view change log, Donate via paypal, GPU Viewer Github main page.


## UNDER DEVELOPMENT

1. General - Bug fixes, Code Optimizations (High Priority)


## IMPORTANT

1. Requires Python3 to run this Application, works only on linux Operating system
2. For Vulkan Tab to work, nvidia, Mesa and AMD vulkan enabled drivers should be installed along with vulkan-utils
3. For OpenCL Tab to work, install clinfo along with OpenCL drivers for your respective GPU's

## KNOWN ISSUES

1. Minor UI issues.
2. The Extensions drop down menu in OpenGL tab will not render well if there are too many items, users may see a big empty space at the start. This is a GTK issue (https://github.com/arunsivaramanneo/GPU-Viewer/issues/9)
3. The Application does not render well under dark themes.

## DEVELOPMENT/TEST ENVIRONMENT

1. Operating System : Ubuntu 22.04
2. Desktop : Gnome 42
3. Kernel : 5.15.x-xx
4. IDE : VSCode


## SYSTEM SETUP

1. MSI PE62 Laptop, Huawei Matebook 13 AMD
2. Quad Core Intel Core i7-4710HQ, AMD Ryzen 3500 U
3. Nvidia Gefore GTX 1050Ti (Discrete GPU) , Drivers - Nvidia (proprietary)/Mesa drivers
4. Intel HD(R) Graphics 630, Drivers - MESA (Open Source)
5. 8 GB RAM

**If you like/use this Application,consider supporing us by DONATING at PayPal https://www.paypal.me/ArunSivaraman.**
