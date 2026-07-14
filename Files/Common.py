# Copyright (C) 2017-2026 Arun Sivaraman <arunsivaramanneo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import gi
import const
import subprocess
import Filenames
from pathlib import Path
gi.require_version('Gtk','4.0')
gi.require_version(namespace='Adw', version='1')

from gi.repository import Gtk,GdkPixbuf,Gdk,Gio,GObject,Adw,GLib,Pango
import cairo as _cairo


import os
import glob
import configparser
import math

# Removed CircularGauge - reverting to LevelBar

_intel_rc6_cache = {}

class Config:
    def __init__(self):
        self.config_dir = os.path.join(GLib.get_user_config_dir(), "gpu-viewer")
        self.config_path = os.path.join(self.config_dir, "config.ini")
        self.config = configparser.ConfigParser()
        self.load()

    def load(self):
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        if os.path.exists(self.config_path):
            self.config.read(self.config_path)
        else:
            self.config["THEME"] = {"prefer_dark": "False"}
            self.save()

    def save(self):
        with open(self.config_path, "w") as f:
            self.config.write(f)

    def get_theme_preference(self):
        return self.config.getboolean("THEME", "prefer_dark", fallback=True)

    def set_theme_preference(self, prefer_dark):
        if "THEME" not in self.config:
            self.config["THEME"] = {}
        self.config["THEME"]["prefer_dark"] = str(prefer_dark)
        self.save()

Adw.init()

def get_gpu_stats_for_index(gpu_index):
    """
    Fetches GPU stats (Memory Used, Memory Total, Temperature, Clock Current, Clock Max, Usage, Fan Speed, Power)
    by direct GPU index corresponding to /sys/class/drm/card{gpu_index}.
    """
    stats = {'mem_used': 0, 'mem_total': 0, 'temp': 0, 'clock_current': 0, 'clock_max': 0, 'usage': -1, 'fan_speed': -1, 'power_usage': -1}
    
    card_path = f"/sys/class/drm/card{gpu_index}/device"
    if not os.path.isdir(card_path):
        card_path = f"/sys/class/drm/card{gpu_index}"
        if not os.path.isdir(card_path):
            return None

    try:
        # Determine vendor first
        vendor_id = ""
        vendor_file = f"{card_path}/vendor"
        if not os.path.exists(vendor_file):
            vendor_file = f"{card_path}/device/vendor"
        if os.path.exists(vendor_file):
            try:
                with open(vendor_file, "r") as f:
                    vendor_id = f.read().strip().lower()
            except:
                pass

        if "0x10de" in vendor_id:
            # NVIDIA GPU stats using nvidia-smi
            pci_addr = ""
            try:
                real_path = os.path.realpath(card_path)
                pci_addr = os.path.basename(real_path) # e.g. "0000:01:00.0"
            except:
                pass
            
            if pci_addr:
                cmd = f"nvidia-smi -i {pci_addr} --query-gpu=memory.used,memory.total,temperature.gpu,utilization.gpu,clocks.current.graphics,clocks.max.graphics,fan.speed,power.draw --format=csv,noheader,nounits"
                lines = fetchContentsFromCommand(cmd)
                if lines:
                    parts = [p.strip() for p in lines[0].split(',')]
                    if len(parts) >= 8:
                        def parse_val(val, default=0):
                            if "[n/a]" in val.lower() or "n/a" in val.lower() or not val:
                                return default
                            try:
                                return int(float(val))
                            except:
                                return default
                        
                        stats['mem_used'] = parse_val(parts[0])
                        stats['mem_total'] = parse_val(parts[1])
                        stats['temp'] = parse_val(parts[2])
                        stats['usage'] = parse_val(parts[3], -1)
                        stats['clock_current'] = parse_val(parts[4])
                        stats['clock_max'] = parse_val(parts[5])
                        stats['fan_speed'] = parse_val(parts[6], -1)
                        stats['power_usage'] = parse_val(parts[7], -1)
                        return stats

        elif "0x8086" in vendor_id:
            # Intel GPU stats
            # 1. Clocks
            cur_freq_paths = [
                f"{card_path}/drm/card{gpu_index}/gt_cur_freq_mhz",
                f"{card_path}/drm/card{gpu_index}/gt_act_freq_mhz",
                f"{card_path}/drm/card{gpu_index}/gt/gt0/rps_cur_freq_mhz",
                f"{card_path}/drm/card{gpu_index}/gt/gt0/rps_act_freq_mhz",
                f"/sys/class/drm/card{gpu_index}/gt/gt0/rps_cur_freq_mhz",
                f"/sys/class/drm/card{gpu_index}/gt/gt0/rps_act_freq_mhz",
            ]
            max_freq_paths = [
                f"{card_path}/drm/card{gpu_index}/gt_max_freq_mhz",
                f"{card_path}/drm/card{gpu_index}/gt/gt0/rps_max_freq_mhz",
                f"/sys/class/drm/card{gpu_index}/gt/gt0/rps_max_freq_mhz",
            ]
            for p in cur_freq_paths:
                if os.path.exists(p):
                    try:
                        with open(p, 'r') as f:
                            stats['clock_current'] = int(f.read().strip())
                        break
                    except:
                        pass
            for p in max_freq_paths:
                if os.path.exists(p):
                    try:
                        with open(p, 'r') as f:
                            stats['clock_max'] = int(f.read().strip())
                        break
                    except:
                        pass

            # 2. Temperature
            hwmon_pattern = f"{card_path}/hwmon/hwmon*"
            hwmons = glob.glob(hwmon_pattern)
            if hwmons:
                for hwmon in hwmons:
                    temp_input = f"{hwmon}/temp1_input"
                    if os.path.exists(temp_input):
                        try:
                            with open(temp_input, 'r') as f:
                                stats['temp'] = int(f.read().strip()) // 1000
                            break
                        except:
                            pass
            
            # Fallback for CPU core temp (for integrated Intel GPUs)
            if stats['temp'] == 0:
                for hwmon in glob.glob("/sys/class/hwmon/hwmon*"):
                    try:
                        if os.path.exists(f"{hwmon}/name"):
                            with open(f"{hwmon}/name", "r") as f:
                                hwmon_name = f.read().strip()
                            if "coretemp" in hwmon_name or "intel" in hwmon_name:
                                temp_input = f"{hwmon}/temp1_input"
                                if os.path.exists(temp_input):
                                    with open(temp_input, 'r') as f_temp:
                                        stats['temp'] = int(f_temp.read().strip()) // 1000
                                        break
                    except:
                        pass

            # 3. Usage (active time calculation via rc6 residency)
            import time
            rc6_path = None
            for p in [
                f"{card_path}/drm/card{gpu_index}/power/rc6_residency_ms",
                f"{card_path}/drm/card{gpu_index}/gt/gt0/rc6_residency_ms",
                f"/sys/class/drm/card{gpu_index}/gt/gt0/rc6_residency_ms",
            ]:
                if os.path.exists(p):
                    rc6_path = p
                    break
            
            if rc6_path:
                try:
                    with open(rc6_path, 'r') as f:
                        curr_residency = int(f.read().strip())
                    curr_time = time.time() * 1000.0
                    
                    if gpu_index in _intel_rc6_cache:
                        prev_residency, prev_time = _intel_rc6_cache[gpu_index]
                        delta_res = curr_residency - prev_residency
                        delta_time = curr_time - prev_time
                        if delta_time > 0 and delta_res >= 0:
                            idle_percent = (delta_res / delta_time) * 100.0
                            active_percent = max(0.0, min(100.0, 100.0 - idle_percent))
                            stats['usage'] = int(active_percent)
                    
                    _intel_rc6_cache[gpu_index] = (curr_residency, curr_time)
                except:
                    pass

            # 4. Memory (for Intel discrete GPUs if local memory is exposed)
            for lmem_path in [
                f"{card_path}/tile0/memory-regions/lmem",
                f"{card_path}/memory-regions/lmem",
            ]:
                if os.path.exists(f"{lmem_path}/total_bytes") or os.path.exists(f"{lmem_path}/size"):
                    total_file = f"{lmem_path}/total_bytes" if os.path.exists(f"{lmem_path}/total_bytes") else f"{lmem_path}/size"
                    used_file = f"{lmem_path}/used_bytes"
                    avail_file = f"{lmem_path}/avail_bytes"
                    try:
                        total_val = 0
                        used_val = 0
                        with open(total_file, 'r') as f_tot:
                            total_val = int(f_tot.read().strip())
                        
                        if os.path.exists(used_file):
                            with open(used_file, 'r') as f_used:
                                used_val = int(f_used.read().strip())
                        elif os.path.exists(avail_file):
                            with open(avail_file, 'r') as f_avail:
                                avail_val = int(f_avail.read().strip())
                                used_val = total_val - avail_val
                        
                        stats['mem_total'] = total_val // (1024 * 1024)
                        stats['mem_used'] = used_val // (1024 * 1024)
                        break
                    except:
                        pass

            # 5. Generic hwmon fan/power checks if exposed
            if hwmons:
                for hwmon in hwmons:
                    pwm_input = f"{hwmon}/pwm1"
                    pwm_max_input = f"{hwmon}/pwm1_max"
                    if os.path.exists(pwm_input):
                        try:
                            with open(pwm_input, 'r') as f:
                                pwm_value = int(f.read().strip())
                            pwm_max = 255
                            if os.path.exists(pwm_max_input):
                                try:
                                    with open(pwm_max_input, 'r') as f_max:
                                        pwm_max = int(f_max.read().strip())
                                except:
                                    pass
                            stats['fan_speed'] = int((pwm_value / pwm_max) * 100)
                        except:
                            pass
                    
                    power_input = f"{hwmon}/power1_average"
                    if os.path.exists(power_input):
                        try:
                            with open(power_input, 'r') as f:
                                stats['power_usage'] = int(f.read().strip()) // 1000000
                        except:
                            pass

            if stats['mem_total'] > 0 or stats['temp'] > 0 or stats['usage'] >= 0 or stats['clock_current'] > 0:
                return stats

        else:
            # Baseline / AMD sysfs fallback
            if os.path.exists(f"{card_path}/mem_info_vram_used"):
                with open(f"{card_path}/mem_info_vram_used", 'r') as f:
                    stats['mem_used'] = int(f.read().strip()) // (1024 * 1024)
            
            if os.path.exists(f"{card_path}/mem_info_vram_total"):
                 with open(f"{card_path}/mem_info_vram_total", 'r') as f:
                    stats['mem_total'] = int(f.read().strip()) // (1024 * 1024)

            hwmon_pattern = f"{card_path}/hwmon/hwmon*"
            hwmons = glob.glob(hwmon_pattern)
            if hwmons:
                for hwmon in hwmons:
                    temp_input = f"{hwmon}/temp1_input"
                    if os.path.exists(temp_input):
                          with open(temp_input, 'r') as f:
                            stats['temp'] = int(f.read().strip()) // 1000
                    
                    pwm_input = f"{hwmon}/pwm1"
                    pwm_max_input = f"{hwmon}/pwm1_max"
                    if os.path.exists(pwm_input):
                        with open(pwm_input, 'r') as f:
                            pwm_value = int(f.read().strip())
                            pwm_max = 255
                            if os.path.exists(pwm_max_input):
                                try:
                                    with open(pwm_max_input, 'r') as f_max:
                                        pwm_max = int(f_max.read().strip())
                                except:
                                    pass
                            stats['fan_speed'] = int((pwm_value / pwm_max) * 100)
                    
                    power_input = f"{hwmon}/power1_average"
                    if os.path.exists(power_input):
                        with open(power_input, 'r') as f:
                            stats['power_usage'] = int(f.read().strip()) // 1000000
            
            if os.path.exists(f"{card_path}/gpu_busy_percent"):
                with open(f"{card_path}/gpu_busy_percent", 'r') as f:
                    stats['usage'] = int(f.read().strip())
            
            if os.path.exists(f"{card_path}/pp_dpm_sclk"):
                with open(f"{card_path}/pp_dpm_sclk", 'r') as f:
                    lines = f.readlines()
                    max_clock = 0
                    current_clock = 0
                    for line in lines:
                        parts = line.split()
                        if len(parts) >= 2:
                            clock_str = parts[1].replace('Mhz', '').replace('MHz', '')
                            try:
                                clock_val = int(clock_str)
                                if clock_val > max_clock:
                                    max_clock = clock_val
                                if '*' in line:
                                    current_clock = clock_val
                            except ValueError:
                                pass
                    stats['clock_current'] = current_clock
                    stats['clock_max'] = max_clock
            
            if stats['clock_current'] == 0 and hwmons:
                 for hwmon in hwmons:
                    freq_input = f"{hwmon}/freq1_input"
                    if os.path.exists(freq_input):
                         with open(freq_input, 'r') as f:
                            stats['clock_current'] = int(f.read().strip()) // (1000 * 1000)
                            break

            if stats['mem_total'] > 0 or stats['temp'] > 0 or stats['usage'] >= 0 or stats['clock_current'] > 0:
                return stats
    except Exception as e:
        print(f"Error reading sysfs for card {gpu_index}: {e}")
        pass

    return None


def get_gpu_stats(device_id, num_devices):
    """
    Fetches GPU stats (Memory Used, Memory Total, Temperature, Clock Current, Clock Max, Usage, Fan Speed, Power)
    by looking up matching device_id.
    """
    gpu_index = -1
    for i in range(num_devices):
        device_file_paths = [
            f"/sys/class/drm/card{i}/device/device",
            f"/sys/class/drm/card{i}/device"
        ]
        
        for device_file_path in device_file_paths:
            if os.path.exists(device_file_path):
                try:
                    with open(device_file_path, 'r') as f:
                        sys_device_id = int(f.read().strip(), 16)
                        if sys_device_id == device_id:
                            gpu_index = i
                            break
                except (ValueError, OSError):
                    continue
        
        if gpu_index != -1:
            break

    if gpu_index == -1:
        return None

    return get_gpu_stats_for_index(gpu_index)




class MyGtk(Gtk.Window):
    def __init__(self, title):
        super(MyGtk, self).__init__(title=title)
        setting = Gtk.Settings.get_default()
        # Setting Theme
   #     if Path(Filenames.Materia_gtk_theme_folder).exists(): 
   #         setting.set_property("gtk-theme-name", "Materia-dark")
   #     elif Path(Filenames.Orchis_gtk_theme_folder).exists():
   #         setting.set_property("gtk-theme-name","Orchis-Compact")
   #     else:
   #         setting.set_property("gtk-theme-name","Adwaita")

        #Setting Font
    #    if Path(Filenames.Roboto_font_folder).exists():
    #        setting.set_property("gtk-font-name","Roboto-Black 12")
    #        setting.set_property("gtk-hint-font-metrics",True)

def create_tab(notebook,icon_url,icon_width,icon_height,aspect_ratio):
    tab = Gtk.Box(orientation=1,spacing=10)
 #   tab_icon = fetchImageFromUrl(icon_url,icon_width,icon_height,aspect_ratio)
    notebook.add_titled_with_icon(child=tab, name=icon_width, title=icon_width,icon_name=icon_url)
#    notebook.append_page(tab,Gtk.Picture.new_for_pixbuf(tab_icon))
    return tab

#getting Ram Details in GB

def setMargin(widget,start,top,bottom):
    widget.set_margin_start(start)
    widget.set_margin_top(top)
    widget.set_margin_bottom(bottom)

def getRamInGb(ram):
    ram1 = ram.split()
    return str("%.2f" %(float(ram1[0])/(1024*1024))) + " GB"

# Setting the Minimum Screen Size
def getScreenSize():
    display = Gdk.Display.get_default()
    monitors = display.get_monitors()
    for m in monitors:
        g = m.get_geometry()
    return g.width,g.height


# fetching the Images/Logos from the const File
def fetchImageFromUrl(imgUrl, iconWidth, iconHeight, aspectRatio):
    return GdkPixbuf.Pixbuf.new_from_file_at_scale(
        filename=imgUrl, width=iconWidth, height=iconHeight, preserve_aspect_ratio=aspectRatio)

# Copy the Contents of the file from a File to a List
def copyContentsFromFile(fileName):
    with open(fileName, "r") as file1:
        value = []
        for line in file1:
            value.append(line)
    return value

def fetchContentsFromCommand(command):
    process = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,universal_newlines=True)
    return process.communicate()[0].splitlines()

def createMainFile(filename,command):
    with open(filename,"w") as file:
        process = subprocess.Popen(command,shell=True,stdout=file,universal_newlines=True)
        process.communicate()

def on_light_action_actived(self, action, win,param=None):
    display = Gtk.Widget.get_display(win)
    provider = Gtk.CssProvider.new()
    fname = Gio.file_new_for_path('gtk_light.css')
    provider.load_from_file(fname)
    Gtk.StyleContext.add_provider_for_display(display, provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER)
    
        
def on_dark_action_actived(self, action,win, param=None):
    display = Gtk.Widget.get_display(win)
    provider = Gtk.CssProvider.new()
    fname = Gio.file_new_for_path('gtk_dark.css')
    provider.load_from_file(fname)
    Gtk.StyleContext.add_provider_for_display(display, provider,
            Gtk.STYLE_PROVIDER_PRIORITY_USER)
        

# setting up Sub Tabs in Vulkan

def createSubTab(Tab, notebook, label):
 #   Tab.set_border_width(10)
    notebook.append_page(Tab, Gtk.Label(label=label))
    Frame = Gtk.Frame()
    Tab.append(Frame)
    notebook.set_property('tab-pos',Gtk.PositionType.LEFT) 
    page = notebook.get_page(Tab)
    page.set_property("tab-expand",False)
    Grid = Gtk.Grid()
    Frame.set_child(Grid)
    return Grid


# adding Scrollbar to the Treeview

def create_scrollbar(widget):
    scrollbar = Gtk.ScrolledWindow()
    scrollbar.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
    scrollbar.set_vexpand(True)
    scrollbar.set_hexpand(True)
    scrollbar.set_visible(True)
    scrollbar.set_child(widget)
    return scrollbar


def colorTrueFalse(filename, text):
    with open(filename, "r") as file1:
        value = []
        fgColor = []
        for line in file1:
            if text in line:
                value.append("true")
                fgColor.append(const.COLOR1)
            else:
                value.append("false")
                fgColor.append(const.COLOR2)
    return fgColor, value

def getFormatValue(filename,Format):
    loop = 0
    value = []
    fgColor = []
    with open(filename,"r") as file:
        for line in file:
            for i,f in enumerate(Format):
                if "FEATURE" in line and i >= loop:
                    value.append("true")
                    fgColor.append(const.COLOR1)
                    loop = loop + 1
                    if ":" in f:
                        break
                if "None" in line and i >= loop:
                    value.append("false")
                    fgColor.append(const.COLOR2)
                    loop = loop + 1
                    if ":" in f:
                        break
    return fgColor, value


def getLinkButtonImg(img, link, toolTip):
    Logbutton = Gtk.LinkButton.new_with_label(link)
    Logbutton.set_child(Gtk.Picture.new_for_pixbuf(img))
    Logbutton.set_tooltip_text(toolTip)
    return Logbutton


def getVulkanVersion(value):
    majorVersion = int(value) >> 22
    minorVersion = int(value) >> 12 & 1023
    patchVersion = int(value) & 4095
    return "%d.%d.%d" % (majorVersion, minorVersion, patchVersion)


def getDriverVersion(value,i):
    if '4318' in value:
        majorVersion = (int(value[i]) >> 22) & 1023
        minorVersion = (int(value[i]) >> 14) & 255
        microVersion = (int(value[i]) >> 6) & 255
        nanoVersion = int(value[i]) & 63
        return "%d.%.2d.%.2d.%d" % (majorVersion, minorVersion, microVersion, nanoVersion)
    else:
        majorVersion = int(value[i]) >> 22
        minorVersion = int(value[i]) >> 12 & 1023
        microVersion = int(value[i]) & 4095
        return "%d.%d.%d" % (majorVersion, minorVersion, microVersion)

def setup(widget, item):
    """Setup the widget to show in the Gtk.Listview"""
    label = Gtk.Label()
    label.props.xalign = 0.0
    label.set_ellipsize(Pango.EllipsizeMode.END)
    item.set_child(label)


def bind(widget, item,column):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.column)
        
def createSearchEntry(store_filter):
    entry = Gtk.SearchEntry()
    entry.set_property("placeholder_text","Type here to filter.....")
    entry.connect("search-changed", refresh_filter, store_filter)
    return entry


def getDeviceSize(size):
    sizeMB = float(size) / (1024 * 1024 * 1024)
    if sizeMB < 1.0:
        sizeMB = str(format((sizeMB * 1024), '.2f')) + " MB"
    else:
        sizeMB = str(format(sizeMB, '.2f')) + " GB"
    return sizeMB

def appendLimitsRHS(filename, temp):
    LimitsRHS = []
    LimitRHSValue = []
    i = 0
    with open(filename, "r") as file1:
        for i, line in enumerate(file1):
            if i < len(temp):
                val = temp[i].strip()
                LimitsRHS.append(val)
                LimitRHSValue.append(val != "")
            else:
                LimitsRHS.append("")
                LimitRHSValue.append(False)
    return LimitsRHS, LimitRHSValue

def getGpuImage(line):
    if "Intel" in line and "Arc" not in line:
        gpu_image = fetchImageFromUrl(const.INTEL_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "Intel" in line and "Arc" in line:
        gpu_image = fetchImageFromUrl(const.INTEL_ARC_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "GTX" in line and "GeForce" in line:
        gpu_image = fetchImageFromUrl(const.NVIDIA_GTX_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "RTX" in line and "GeForce" in line:
        gpu_image = fetchImageFromUrl(const.NVIDIA_RTX_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "NVIDIA" in line:
        gpu_image = fetchImageFromUrl(const.NVIDIA_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, True)    
    elif "GeForce" in line and ("GTX" not in line or "RTX" not in line):
        gpu_image = fetchImageFromUrl(const.GEFORCE_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "CUDA" in line and ("GTX" not in line or "RTX" not in line):
        gpu_image = fetchImageFromUrl(const.CUDA_PNG, 100, const.ICON_HEIGHT, True)
    elif "Ryzen" in line and "AMD" in line:
        gpu_image = fetchImageFromUrl(const.AMDRYZEN_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "Radeon" in line and "AMD" in line and "Pro" not in line:
        gpu_image = fetchImageFromUrl(const.AMDRADEON_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "Radeon" in line and "AMD" in line and "Pro" in line:
        gpu_image = fetchImageFromUrl(const.AMD_RADEON_Pro_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "AMD" in line or "ATI" in line and "Radeon" not in line:
        gpu_image = fetchImageFromUrl(const.AMD_LOGO_PNG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "LLVM" in line:
        gpu_image = fetchImageFromUrl(const.LLVM_LOGO_SVG, const.ICON_WIDTH, const.ICON_HEIGHT, True)
    elif "Mesa" in line or "Clover" in line:
        gpu_image = fetchImageFromUrl(const.MESA_LOGO_PNG,100,const.ICON_HEIGHT, False)
    elif "Portable Computing Language" in line:
        gpu_image = fetchImageFromUrl(const.POCL_LOGO_PNG,100,const.ICON_HEIGHT, False)
    else:
        gpu_image = fetchImageFromUrl(const.TRANSPARENT_PIXBUF,100,const.ICON_HEIGHT, False)
    return gpu_image

def getLogo(line):
    if "Ubuntu" in line and "Gnome" not in line:
        logo_pixbuf  = fetchImageFromUrl(const.Ubuntu_logo,32,28, True)
    elif "Nobara" in line:
        logo_pixbuf  = fetchImageFromUrl(const.Nobara_OS_logo,32,28, True)
    elif "AnduinOS" in line:
        logo_pixbuf  = fetchImageFromUrl(const.Anduinos_logo,32,28, True)
    elif "NixOS" in line:
        logo_pixbuf  = fetchImageFromUrl(const.NixOS_logo,32,28, True)
    elif "Fedora" in line:
        logo_pixbuf = fetchImageFromUrl(const.fedora_logo,32,28, True)
    elif "COSMIC" in line:
        logo_pixbuf  = fetchImageFromUrl(const.cosmic_logo,32,28, True)
    elif "Budgie" in line and "Ubuntu" in line:
        logo_pixbuf = fetchImageFromUrl(const.Ubuntu_Budgie_logo,32,28, True)
    elif "Studio" in line and "Ubuntu" in line:
        logo_pixbuf = fetchImageFromUrl(const.Ubuntu_Studio_logo,32,28, True)
    elif "Flatpak" in line:
        logo_pixbuf = fetchImageFromUrl(const.Flatpak_logo,32,28,True)
    elif "RebornOS" in line:
        logo_pixbuf = fetchImageFromUrl(const.RebornOS_logo,32,28,True)
    elif "Kubuntu" in line:
        logo_pixbuf = fetchImageFromUrl(const.Kubuntu_logo,32,28,True)
    elif "Lubuntu" in line:
        logo_pixbuf = fetchImageFromUrl(const.Lubuntu_logo,32,28,True)
    elif "Solus" in line:       
        logo_pixbuf = fetchImageFromUrl(const.Solus_logo,32,28,True)
    elif "Mandriva" in line:       
        logo_pixbuf = fetchImageFromUrl(const.OpenMandriva_logo,32,28,True)
    elif "CachyOS" in line:       
        logo_pixbuf = fetchImageFromUrl(const.CACHYOS_LOGO_PNG,32,28,True)
    elif "Xubuntu" in line:
        logo_pixbuf = fetchImageFromUrl(const.Xubuntu_logo,32,28,True)
    elif "Arch" in line:
        logo_pixbuf = fetchImageFromUrl(const.Arch_logo,32,28, True)
    elif "Elementary" in line:
        logo_pixbuf = fetchImageFromUrl(const.Elementary_logo,32,28,True)
    elif "Debian" in line:
        logo_pixbuf = fetchImageFromUrl(const.Debian_logo,32,28,True)
    elif "opensuse" in line:
        logo_pixbuf = fetchImageFromUrl(const.Open_Suse_logo,32,28,True)
    elif "Pop" in line:
        logo_pixbuf = fetchImageFromUrl(const.Pop_os_logo,32,28,True)
    elif "MX" in line:
        logo_pixbuf = fetchImageFromUrl(const.MX_linux_logo,32,28,True)
    elif "Zorin" in line:
        logo_pixbuf = fetchImageFromUrl(const.Zorin_os_logo,32,28,True)
    elif "Mint" in line:
        logo_pixbuf = fetchImageFromUrl(const.Mint_logo,32,28, True)
    elif "Radeon" in line and "Ryzen" not in line:
        logo_pixbuf = fetchImageFromUrl(const.AMD_LOGO_PNG,32,28, False)
    elif "Ryzen" in line:
        logo_pixbuf = fetchImageFromUrl(const.AMDRYZEN_LOGO_PNG,32,28, True)
    elif "NVIDIA" in line and "Ryzen" not in line:
        logo_pixbuf = fetchImageFromUrl(const.Nvidia_logo,32,28, True)   
    elif ("Mesa" in line or "radv" in line or "llvmpipe" in line or "dozen" in line or "venus" in line or "nvk" in line or "NVK" in line) and ("LLVM" not in line):
        logo_pixbuf = fetchImageFromUrl(const.Mesa_logo,32,28, True)
    elif "LLVM" in line :
        logo_pixbuf = fetchImageFromUrl(const.LLVM_logo,32,28, True)   
    elif "AMD" in line:
        logo_pixbuf = fetchImageFromUrl(const.AMD_logo,32,28, True)      
    elif "Intel" in line:
        logo_pixbuf = fetchImageFromUrl(const.Intel_logo,32,28, True)
    elif "Manjaro" in line:
        logo_pixbuf = fetchImageFromUrl(const.Manjaro_logo,32,28, True)
    elif "sway" in line or "Sway" in line:
        logo_pixbuf = fetchImageFromUrl(const.Sway_logo,32,28, True)
    elif "Budgie" in line:
        logo_pixbuf = fetchImageFromUrl(const.Budgie_logo,32,28, True)
    elif "Unity" in line:
        logo_pixbuf = fetchImageFromUrl(const.Unity_logo,64,64, True)
    elif "GNOME" in line:
        logo_pixbuf = fetchImageFromUrl(const.Gnome_logo,32,28, True)
    elif "Fluxbox" in line:
        logo_pixbuf = fetchImageFromUrl(const.Fluxbox_logo,32,28, True)
    elif "XFCE" in line:
        logo_pixbuf = fetchImageFromUrl(const.XFCE_logo,32,28, True)
    elif "MATE" in line:
        logo_pixbuf = fetchImageFromUrl(const.Mate_logo,32,28, True)
    elif "Cinnamon" in line:
        logo_pixbuf = fetchImageFromUrl(const.Cinnamon_logo,32,28, True)
    elif "wayland" in line:
        logo_pixbuf = fetchImageFromUrl(const.Wayland_logo,32,28, True)
    elif "x11" in line:
        logo_pixbuf = fetchImageFromUrl(const.X11_logo,32,28, True)
    elif "KDE" in line:
        logo_pixbuf = fetchImageFromUrl(const.Kde_logo,32,28, True)
    elif "Rhino" in line:
        logo_pixbuf = fetchImageFromUrl(const.Rhino_Linux_logo,32,28, True)
    elif "Steam" in line:
        logo_pixbuf = fetchImageFromUrl(const.Steam_OS_logo,32,28, True)
    else:
        logo_pixbuf = fetchImageFromUrl(const.TRANSPARENT_PIXBUF,32,28,True)
    return logo_pixbuf

class ExpandDataObject(GObject.GObject):
    def __init__(self, txt: str, txt2: str):
        super(ExpandDataObject, self).__init__()
        self.data = txt
        self.data2 = txt2
        self.children = []

def add_tree_node(item):
    if not (item):
            print("no item")
            return model
    else:        
        if type(item) == Gtk.TreeListRow:
            item = item.get_item()

            print("converteu")
            print(item)  
            
        if not item.children:
            return None
        store = Gio.ListStore.new(ExpandDataObject)
        for child in item.children:
            store.append(child)
        return store

def setup_expander(widget, item):
    """Setup the widget to show in the Gtk.Listview"""
    label = Gtk.Label()
    expander = Gtk.TreeExpander.new()
 #   expander.props.indent_for_icon = True
 #   expander.props.indent_for_depth = True
    label.set_ellipsize(Pango.EllipsizeMode.END)
    expander.set_child(label)
    item.set_child(expander)

def setup(widget, item):
    """Setup the widget to show in the Gtk.Listview"""
    label = Gtk.Label()
    label.props.xalign = 0.0
    label.set_ellipsize(Pango.EllipsizeMode.END)
    item.set_child(label)

def bind_expander(widget, item):
    """bind data from the store object to the widget"""
    expander = item.get_child()
    label = expander.get_child()
    row = item.get_item()
    expander.set_list_row(row)
    obj = row.get_item()
    label.set_label(obj.data)
    label.add_css_class(css_class='parent')

def bind1(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    row = item.get_item()
    obj = row.get_item()
    if "true" in obj.data2 or "Yes" in obj.data2: 
        label.remove_css_class(css_class='nothing')
        label.remove_css_class(css_class='error')
        label.add_css_class(css_class='success')
        label.set_label(obj.data2)
    elif "false" in obj.data2 or "No" in obj.data2 and "None" not in obj.data2:
        label.remove_css_class(css_class='nothing')
        label.remove_css_class(css_class='success')
        label.add_css_class(css_class='error')
        label.set_label(obj.data2)
    else:
        label.remove_css_class(css_class='error')
        label.remove_css_class(css_class='success')
        label.add_css_class(css_class='nothing')
        label.set_label(obj.data2)


class ExpandDataObject2(GObject.GObject):
    def __init__(self, txt: str, txt2: str,txt3: str,txt4: str,txt5: str):
        super(ExpandDataObject2, self).__init__()
        self.data = txt
        self.data2 = txt2
        self.data3= txt3
        self.data4= txt4
        self.data5= txt5
        self.children = []



def add_tree_node2(item):
    if not (item):
            print("no item")
            return model
    else:        
        if type(item) == Gtk.TreeListRow:
            item = item.get_item()

            print("converteu")
            print(item)  
            
        if not item.children:
            return None
        store = Gio.ListStore.new(ExpandDataObject2)
        for child in item.children:
            store.append(child)
        return store

def bind2(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    row = item.get_item()
    obj = row.get_item()
    if "true" in obj.data3: 
        label.add_css_class(css_class='success')
    elif "false" in obj.data3:
        label.add_css_class(css_class='error')
    else:
        label.add_css_class(css_class='nothing')
    label.set_label(obj.data3)


def bind3(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    row = item.get_item()
    obj = row.get_item()
    if "true" in obj.data4: 
        label.add_css_class(css_class='success')
    elif "false" in obj.data4:
        label.add_css_class(css_class='error')
    else:
        label.add_css_class(css_class='nothing')
    label.set_label(obj.data4)


def bind4(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    row = item.get_item()
    obj = row.get_item()
    if "true" in obj.data5: 
        label.add_css_class(css_class='success')
    elif "false" in obj.data5:
        label.add_css_class(css_class='error')
    else:
        label.add_css_class(css_class='nothing')
    label.set_label(obj.data5)
