# GPU-Viewer



![image](https://user-images.githubusercontent.com/30646692/209199473-a51dbd6c-d7f2-4bfe-a392-0abf20cbc4ec.png)
## Testimonials

### Softpedia

#### "GPU-Viewer can potentially be a very useful application in the right hands. There's no denying the fact that it's not the most beginner-friendly application out there, but the fact that it manages to bundle three very complex CLI tools into one functional GUI is definitely something I appreciate." - Review by Vladimir Ciobica

### Linux Magazine USA (Issue 254)

#### "GPU-Viewer is a clever combination of pre-existing tools, including glxinfo, vulkaninfo and clinfo" - BY GRAHAM MORRISON

### A front-end to glxinfo, vulkaninfo, clinfo and es2_info.


![image](https://repology.org/badge/vertical-allrepos/gpu-viewer.svg)


This project aims to capture all the important details of glxinfo, vulkaninfo
and clinfo in a GUI. The project is being developed using python 3 pygobject
with GTK4. All the important details are extracted using
glxinfo/vulkaninfo/clinfo with the combination of grep, CAT , AWK commands and
displayed in the front-end. There is no hard OpenGL Programming involved, until
glxinfo, vulkaninfo and clinfo works the GPU-viewer will also work

Light Theme
![Screenshot From 2026-02-27 17-49-05](https://github.com/user-attachments/assets/2c8145dd-1e93-4c53-b69b-aecff3ada902)

Dark theme
![Screenshot From 2026-02-27 17-49-14](https://github.com/user-attachments/assets/ee41b8b3-d3be-4a05-bf18-e1f4e3d78dd7)


## INSTALLATION

**Arch based distro**

```
sudo pacman -S gpu-viewer
```
**Debian & Ubuntu based distro**

```
sudo apt install gpu-viewer
```


## Make and install from the source

### Install dependencies

**Arch based distro**

```
sudo pacman -S appstream-glib clinfo gtk4 libadwaita lsb-release mesa-utils meson pkgconf python-gobject vdpauinfo vulkan-tools xorg-xdpyinfo
```
**Debian & Ubuntu based distro**

```
sudo apt install clinfo gawk gir1.2-adw-1 gir1.2-gtk-4.0 libadwaita-1-dev libgtk-4-dev lsb-release mesa-opencl-icd mesa-utils pkgconf python3-cairo python3-click python3-gi python3-gi-cairo vdpauinfo vulkan-tools x11-util
```
**Fedora based distro**

```
sudo dnf install clinfo egl-utils mesa-demos mesa-vulkan-drivers meson python3-gobject vdpauinfo vulkan-tools
```
**openSUSE based distro**

```
sudo zypper install clinfo mesa-demo mesa-vulkan-device-select libvulkan_intel libvulkan_lvp libvulkan_radeon python3 libvdpau1 vulkan-tools xdpyinfo xev xlsatoms xlsclients xlsfonts xprop xvinfo xwininfo
```

### Make & install GPU-viewer

1.  Download the latest tag.
2.  Extract it and go in to it.
3.  Open terminal and enter below commands

```
meson _build
cd _build
DESTDIR=/usr/local ninja install
```


## UNINSTALL

**Arch based distro**

```
sudo pacman -R gpu-viewer
```
**Debian & Ubuntu based distro**

```
sudo apt remove gpu-viewer
```


## What's developed and available?

1.  OpenGL Tab - OpenGL Information, OpenGL ES Information, OpenGL hardware
    limits and Extensions displayed as per different Vendors, View GLX Frame
    Buffer Configuration and EGL information, EGL Information
2.  Vulkan Tab - Device Features, Device Limits, Device
    Extensions,Formats,Memory Types & Heaps, Partial Queue Families
    implemented, Instance and Layers,Surface Tab
3.  OpenCL Tab - Platform Details, Device Details , Device Memory & Image
    Details, Device Queue and Execution capabilities, Device Vector Details,
    Total No. of Platforms, No. of Devices for the platform.
4.  About Tab - About GPU Viewer Application, ability to report a bug,view
    license,view change log, Donate via paypal, GPU Viewer Github main page.


## UNDER DEVELOPMENT

1.  General - Bug fixes, Code Optimizations (High Priority)


## IMPORTANT

1.  For Vulkan Tab to work, nvidia, Mesa and AMD vulkan enabled drivers should
    be installed along with vulkan-utils
2.  For OpenCL Tab to work, install clinfo along with OpenCL drivers for your
    respective GPU's


## DEVELOPMENT/TEST ENVIRONMENT

1.  Operating System : Fedora 42
2.  Desktop : Gnome 48
3.  Kernel : 6.14.x-xx
4.  IDE : VSCode


## SYSTEM SETUP

1.  MSI PE62 Laptop, Huawei Matebook 13 AMD
2.  Quad Core Intel Core i7-4710HQ, AMD Ryzen 3500 U
3.  Nvidia Gefore GTX 1050Ti (Discrete GPU) , Drivers - Nvidia
    (proprietary)/Mesa drivers
4.  Intel HD(R) Graphics 630, Drivers - MESA (Open Source)
5.  8 GB RAM

**If you find the project interesting enough, please consider making a donation.
Even a small one would mean the world to me. More than a mere financial act,
donate means that you simply believe in this project and want it to be better.**



![image](https://user-images.githubusercontent.com/30646692/209199473-a51dbd6c-d7f2-4bfe-a392-0abf20cbc4ec.png)
