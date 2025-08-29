import os.path as Path
import gi
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject,Gdk, Gio



style_manager = Adw.StyleManager.get_default()
prefer_dark_theme = style_manager.get_dark()

if prefer_dark_theme:
  AMDRADEON_LOGO_PNG = "../Images/AMD_Radeon_White.png"
  Gnome_logo = "../Images/Gnome_logo.png"
  LLVM_logo = "../Images/LLVM_Logo.png"
  LLVM_LOGO_SVG = "../Images/LLVM_Logo.png"
  AMD_LOGO_PNG = "../Images/AMD.png"
  AMDRYZEN_LOGO_PNG = "../Images/amd-ryzen.png"


else:
  AMDRADEON_LOGO_PNG = "../Images/AMDRadeon.png"
  Gnome_logo = "../Images/Gnome_Dark.png"
  LLVM_logo = "../Images/LLVM-Logo.png"
  LLVM_LOGO_SVG = "../Images/LLVM-Logo.png"
  AMDRYZEN_LOGO_PNG = "../Images/AMD_Ryzen.png"
  AMD_LOGO_PNG = "../Images/AMD_logo.png"







    

GTK_CSS = "gtk.css"

GTK_DARK_CSS = "gtk_dark.css"

ABOUT_US_PNG = "../Images/about-us.png"

VULKAN_PNG = "../Images/Vulkan.png"

OPEN_GL_PNG = "../Images/OpenGL.png"

OPEN_GL_ES_PNG = "../Images/OpenGL_ES.png"

#OPEN_CL_PNG = "../Images/OpenCL.png"

OPEN_CL_PNG = "../Images/OpenCL_Dark.png"

EGL_PNG  = "../Images/Egl_logo.png"

VDPAU_CL_PNG = "../Images/vdpauinfo.png"

NVIDIA_GTX_LOGO_PNG = "../Images/nvidia-logo.png"

NVIDIA_RTX_LOGO_PNG = "../Images/nvidia-RTX-logo.png"

NVIDIA_CUDA_LOGO_PNG = "../Images/Cuda.png"

GEFORCE_PNG = "../Images/GeForce.png"

INTEL_LOGO_PNG = "../Images/intel-logo.png"

INTEL_ARC_LOGO_PNG = "../Images/Intel_Arc_logo.png"

#AMD_LOGO_PNG = "../Images/AMD.png"


AMD_RADEON_VEGA_LOGO_PNG = "../Images/radeon-vega.png"

#AMDRADEON_LOGO_PNG = "../Images/AMD_Radeon_White.png"


AMD_Ryzen_RADEON_LOGO_PNG = "../Images/AMD_Ryzen_Radeon.png"

AMD_RADEON_Pro_LOGO_PNG = "../Images/AMD_Radeon_Pro.png"



#AMDRYZEN_LOGO_PNG = "../Images/AMD_Ryzen.png"

POCL_LOGO_PNG = "../Images/pocl.png"

CUDA_PNG = "../Images/Cuda.png"

#LLVM_LOGO_SVG = "../Images/LLVM_Logo.png"

MESA_LOGO_PNG = "../Images/mesa-logo.png"

INTEL_BANNER = "../Images/Intel_Banner.png"

NVIDIA_BANNER = "../Images/nvidia-banner.jpg"

TWITTER_LOGO_PNG = "../Images/twitter-icon.png"

VULKAN_VIDEO_PNG = "../Images/Vulkan-Video.png"

DONATE_LOGO_PNG = "../Images/Donate.png"

GITHUB_LOGO_PNG = "../Images/github.png"

FAQ_LOGO_PNG = "../Images/faq-icon.png"

LICENSE_LOGO_PNG = "../Images/GPL3.png"

BUG_LOGO_PNG = "../Images/Bug.svg"

LOG_LOGO_PNG = "../Images/Changelog.png"

APP_LOGO_PNG = "../Images/GPU_Viewer.png"

NVIDIA_LOGO_PNG = "../Images/Nvidia_logo.png"

CONTACT_LOGO_PNG = "../Images/Contact.png"

DISCORD_LOGO_PNG = "../Images/Discord.png"

TOOLTIP_LICENSE = "View License"

TOOLTIP_CHANGE_LOG = "View Change Log"

LICENSE_HTML_LINK = "https://www.gnu.org/licenses/gpl-3.0-standalone.html"

CHANGE_LOG_LINK = "https://github.com/arunsivaramanneo/GPU-Viewer/releases"

TOOLTIP_FAQ = "View Frequently Asked Questions"

FAQ_LINK = "https://github.com/arunsivaramanneo/GPU-Viewer/wiki/FAQ----GPU-Viewer"

TOOLTIP_BUG = "Click here to report a bug"

ISSUE_LINK = "https://github.com/arunsivaramanneo/GPU-Viewer/issues"

EMAIL_LINK = "mailto:arunsivaramanneo@gmail.com?Subject=GPU Viewer - <Enter Description here>"

TOOLTIP_DONATE = "Donate PayPal "

PAYPAL_LINK = "https://www.paypal.com/donate/?hosted_button_id=7M3PMM78FBR4Q"

TOOLTIP_TWITTER = "Follow me on Twitter"

TWITTER_LINK = "https://twitter.com/arunsivaraman"

TOOLTIP_GITHUB = "Arun Sivaraman's Github"

GITHUB_LINK = "https://github.com/arunsivaramanneo/GPU-Viewer"

DISCORD_LINK = "https://discord.gg/S7YbaWWM"

DUMMY_PIXBUF = "../Images/8e8e8e.png"

TRANSPARENT_PIXBUF = "../Images/2c2c2c.png"


# ----------------- Distro logos --------------------------------------

Ubuntu_logo = "../Images/Ubuntu.png"
Mint_logo = "../Images/linux_mint.png"
Manjaro_logo = "../Images/Manjaro-log.png"
Open_Suse_logo = "../Images/open_suse.png"
fedora_logo = "../Images/Fedora_icon.png"
Pop_os_logo = "../Images/pop_os.png"
Flatpak_logo = "../Images/Flatpak.png"
Elementary_logo = "../Images/elementaryOS.png"
Debian_logo = "../Images/debian.png"
Arch_logo = "../Images/arch.png"
Solus_logo = "../Images/Solus.svg"
Xubuntu_logo = "../Images/xubuntu.png"
Lubuntu_logo = "../Images/Lubuntu_logo.svg"
Kubuntu_logo = "../Images/Kubuntu_logo.png"
MX_linux_logo = "../Images/MX_Linux_logo.svg"
Zorin_os_logo = "../Images/Zorin_Logo.svg"
Linux_Lite_logo = "../Images/Linux-Lite-Logo.png"
OpenMandriva_logo = "../Images/Mandriva.png"
Ubuntu_Budgie_logo = "../Images/Ubuntu_Budgie.png"
Ubuntu_Studio_logo = "../Images/Ubuntu_Studio.png"
RebornOS_logo = "../Images/RebornOS_Icon.png"
NixOS_logo = "../Images/NixOS.png"
Rhino_Linux_logo = "../Images/Rhino_Linux.png"
Steam_OS_logo = "../Images/Steam_icon_logo.png"
Nobara_OS_logo = "../Images/nobara.png"

#AMD_logo = "../Images/AMD_logo.png"
#Radeon_logo = "../Images/AMD_Radeon.svg"
Radeon_logo = "../Images/AMD_Radeon_graphics_logo.png"
Nvidia_logo = "../Images/nvidia_logo.png"
#LLVM_logo = "../Images/LLVM-Logo.png"
Intel_logo = "../Images/Intel_logo.png"
Mesa_logo = "../Images/mesa.png"
#Ryzen_logo = "../Images/Ryzen.png"
Intel_core_i7_logo = "../Images/intel-logo-core-i7.png"

Ryzen_logo = "../Images/Ryzen_Dark.svg"


#------------------- Desktop logo--------------------------------------

#Gnome_logo = "../Images/Gnome_logo.png"
Unity_logo = "../Images/Unity_logo.png"
Cinnamon_logo = "../Images/Cinnamon-logo.png"
Kde_logo = "../Images/kde-logo.png"
Budgie_logo = "../Images/Budgie.png"
Mate_logo = "../Images/Mate-logo.svg"
XFCE_logo = "../Images/xfce-logo.svg"
Fluxbox_logo = "../Images/Fluxbox-logo.svg"
Sway_logo = "../Images/Sway_Tree.svg"
Wayland_logo = "../Images/Wayland_Logo.svg"
X11_logo = "../Images/X11_Logo.png"
cosmic_logo = "../Images/cosmic.png"

#Gnome_logo = "../Images/Gnome_Dark.png"

TOOLTIP_CONTACT = "Contact us"

FRAMEBUFFERLIST = ["vid", "vdep", "vt", "xsp", "bfsz", "lvl", "rt", "db", "st", "rsz", "gsz", "bsz", "asz", "flt",
                   "srgb", "aux", "depth", "stcl",
                   "acr", "acg", "acb", "aca", "msnum", "msbufs", "Swap", "caveats"]

ICON_WIDTH = 350

ICON_HEIGHT = 50

ICON_HEIGHT2 = 50

WIDTH_RATIO = 0.78

WIDTH_RATIO2 = 0.70

HEIGHT_RATIO1 = 0.90    

HEIGHT_RATIO2 = 0.65

MWIDTH = 350


# .------------- Colors ---------------------

#BGCOLOR1 = "#e9edf6"
BGCOLOR1 = "#353839"

#BGCOLOR2 = "#eeeeee"
BGCOLOR2 = "#2D2E36"

#BGCOLOR3 = "#ccc"
#BGCOLOR3 = "#9FA3AC"
BGCOLOR3 = "#171717"


COLOR1 = "GREEN"

COLOR2 = "RED"

COLOR3 = "#FFFFFF"
#COLOR3  = "#333333"

FONT = "Noto Sans Regular"

# ------------------------ theme Menu -----------------------------------------

MENU_XML="""
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <menu id="app-menu">
    <section>
      <item>
        <attribute name="action">win.about</attribute>
        <attribute name="label" translatable="yes">_Light theme</attribute>
      </item>
      <item>
        <attribute name="action">win.quit</attribute>
        <attribute name="label" translatable="yes">_Dark theme</attribute>
    </item>
    </section>
  </menu>
</interface>"""
