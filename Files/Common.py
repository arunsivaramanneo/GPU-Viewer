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
import re

# Custom Cairo Circular Gauge / Speedometer for GPU Stats
class CircularGauge(Gtk.DrawingArea):
    """
    Custom GTK4 Cairo-rendered speedometer / circular gauge widget for GPU statistics.
    """
    def __init__(self, size=118, title="", unit="%", min_value=0.0, max_value=100.0, gauge_type="usage"):
        super().__init__()
        self.size = size
        self.title = title
        self.unit = unit
        self.min_value = float(min_value)
        self.max_value = float(max_value)
        self.value = float(min_value)
        self.subtitle = ""
        self.gauge_type = gauge_type
        self.value_label = None

        self.set_content_width(size)
        self.set_content_height(int(size * 0.96) if size > 0 else size)
        self.set_draw_func(self._on_draw)

    def set_value(self, value, subtitle=None, max_value=None):
        if max_value is not None and max_value > 0:
            self.max_value = float(max_value)
        if value is None:
            self.value = None
        else:
            try:
                self.value = float(value)
            except (ValueError, TypeError):
                self.value = None
        if subtitle is not None:
            self.subtitle = str(subtitle)
        self.queue_draw()

    def set_max_value(self, max_value):
        if max_value > 0:
            self.max_value = float(max_value)
            self.queue_draw()

    def _get_colors(self, percentage, is_dark_bg=True):
        """Return RGB tuple optimized for light or dark backgrounds."""
        if self.gauge_type in ("temp", "temp_hotspot", "cpu_temp"):
            if self.value is None or self.value <= 0:
                return (0.1, 0.6, 0.8) if not is_dark_bg else (0.2, 0.75, 0.95)
            if self.value < 55:
                return (0.05, 0.55, 0.85) if not is_dark_bg else (0.2, 0.75, 0.95)  # Cool Cyan
            elif self.value < 75:
                return (0.85, 0.50, 0.0) if not is_dark_bg else (0.95, 0.7, 0.1)   # Warm Amber
            else:
                return (0.85, 0.15, 0.15) if not is_dark_bg else (0.95, 0.3, 0.25) # Crimson Red
        elif self.gauge_type in ("clock", "vram_clock"):
            return (0.50, 0.15, 0.80) if not is_dark_bg else (0.65, 0.35, 0.95)  # Purple / violet
        elif self.gauge_type in ("power", "voltage"):
            return (0.85, 0.45, 0.0) if not is_dark_bg else (0.98, 0.60, 0.10)   # Vivid Amber
        elif self.gauge_type == "fan":
            return (0.05, 0.55, 0.55) if not is_dark_bg else (0.15, 0.80, 0.75)  # Deep Teal
        elif self.gauge_type in ("vram", "gtt", "mem_busy"):
            return (0.05, 0.45, 0.85) if not is_dark_bg else (0.25, 0.70, 1.0)   # Royal Blue
        elif self.gauge_type == "cpu":
            return (0.05, 0.60, 0.30) if not is_dark_bg else (0.25, 0.80, 0.45)  # Emerald Green
        elif self.gauge_type in ("ram", "swap"):
            return (0.80, 0.15, 0.50) if not is_dark_bg else (0.95, 0.40, 0.70)  # Magenta Pink
        elif self.gauge_type == "net_down":
            return (0.00, 0.60, 0.40) if not is_dark_bg else (0.10, 0.85, 0.55)  # Teal Green (download)
        elif self.gauge_type == "net_up":
            return (0.70, 0.30, 0.00) if not is_dark_bg else (0.95, 0.50, 0.10)  # Deep Orange (upload)
        else:
            return (0.10, 0.40, 0.85) if not is_dark_bg else (0.30, 0.65, 1.0)   # Cobalt Blue

    def _on_draw(self, area, cr, width, height):
        cx = width / 2.0
        width_ref = min(width, self.size) if (hasattr(self, 'size') and self.size > 0) else width
        radius = width_ref * 0.34
        line_width = max(5.0, radius * 0.16)
        cy = radius + line_width + 2

        # Dynamic theme color extraction
        try:
            fg_rgba = self.get_color()
            fg_r, fg_g, fg_b = fg_rgba.red, fg_rgba.green, fg_rgba.blue
            is_dark_bg = (fg_r * 0.299 + fg_g * 0.587 + fg_b * 0.114) > 0.5
        except Exception:
            is_dark_bg = True
            fg_r, fg_g, fg_b = (0.9, 0.9, 0.95)

        # 240-degree arc: from 135 deg to 405 deg (3/4 pi to 9/4 pi)
        start_angle = math.pi * 0.75
        total_angle = math.pi * 1.5
        end_angle = start_angle + total_angle

        # 1. Background Arc Track
        cr.save()
        cr.set_line_width(line_width)
        cr.set_line_cap(_cairo.LINE_CAP_ROUND)
        track_alpha = 0.15 if is_dark_bg else 0.16
        cr.set_source_rgba(fg_r, fg_g, fg_b, track_alpha)
        cr.arc(cx, cy, radius, start_angle, end_angle)
        cr.stroke()
        cr.restore()

        # 2. Tick Marks
        cr.save()
        num_ticks = 9
        tick_r_inner = radius - line_width * 0.8
        tick_r_outer = radius - line_width * 0.5
        cr.set_line_width(1.2)
        tick_alpha = 0.30 if is_dark_bg else 0.40
        cr.set_source_rgba(fg_r, fg_g, fg_b, tick_alpha)
        for i in range(num_ticks):
            t_angle = start_angle + (total_angle / (num_ticks - 1)) * i
            x1 = cx + math.cos(t_angle) * tick_r_inner
            y1 = cy + math.sin(t_angle) * tick_r_inner
            x2 = cx + math.cos(t_angle) * tick_r_outer
            y2 = cy + math.sin(t_angle) * tick_r_outer
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
            cr.stroke()
        cr.restore()

        # 3. Active Value Arc
        if self.value is not None and self.max_value > self.min_value:
            val_clamped = max(self.min_value, min(self.max_value, self.value))
            pct = (val_clamped - self.min_value) / (self.max_value - self.min_value)
            if pct > 0:
                active_end_angle = start_angle + total_angle * pct
                r, g, b = self._get_colors(pct, is_dark_bg=is_dark_bg)

                cr.save()
                cr.set_line_width(line_width)
                cr.set_line_cap(_cairo.LINE_CAP_ROUND)
                cr.set_source_rgb(r, g, b)
                cr.arc(cx, cy, radius, start_angle, active_end_angle)
                cr.stroke()
                cr.restore()

        # 4. Center Readout (%) inside Speedometer Arc (Omega Symbol)
        cr.save()
        if self.value is not None:
            if self.unit == "%":
                val_text = f"{int(self.value)}%"
            elif self.unit in ("°C", "C"):
                val_text = f"{int(self.value)}°C"
            elif self.unit == "V":
                val_text = f"{self.value:.2f}V" if isinstance(self.value, float) else f"{self.value}V"
            elif self.unit in ("W", "MHz", "RPM"):
                val_text = f"{int(self.value)}{self.unit}"
            else:
                val_text = f"{int(self.value)}{self.unit}"
        else:
            val_text = "—"

        cr.set_source_rgba(fg_r, fg_g, fg_b, 1.0)
        font_size = max(13, int(radius * 0.44))
        cr.select_font_face("Sans", _cairo.FONT_SLANT_NORMAL, _cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(font_size)

        extents = cr.text_extents(val_text)
        cr.move_to(cx - extents.width / 2.0 - extents.x_bearing, cy - extents.height / 2.0 - extents.y_bearing)
        cr.show_text(val_text)
        cr.restore()

        # 5. Divider Line completely below Speedometer Arc
        cr.save()
        line_y = cy + radius * 0.92
        cr.set_line_width(1.0)
        cr.set_source_rgba(fg_r, fg_g, fg_b, 0.22)
        cr.move_to(cx - radius * 0.70, line_y)
        cr.line_to(cx + radius * 0.70, line_y)
        cr.stroke()
        cr.restore()

        # 6. Title Text below Divider Line (e.g. VRAM, GPU Usage)
        cr.save()
        if self.title:
            title_font_size = max(10, int(radius * 0.27))
            cr.set_font_size(title_font_size)
            cr.set_source_rgba(fg_r, fg_g, fg_b, 0.92)
            cr.select_font_face("Sans", _cairo.FONT_SLANT_NORMAL, _cairo.FONT_WEIGHT_BOLD)
            t_extents = cr.text_extents(self.title)
            cr.move_to(cx - t_extents.width / 2.0 - t_extents.x_bearing, line_y + 14)
            cr.show_text(self.title)

        # 7. Subtitle Text below Title (e.g. used/total)
        if self.subtitle:
            sub_font_size = max(9, int(radius * 0.21))
            cr.set_font_size(sub_font_size)
            cr.set_source_rgba(fg_r, fg_g, fg_b, 0.72)
            cr.select_font_face("Sans", _cairo.FONT_SLANT_NORMAL, _cairo.FONT_WEIGHT_NORMAL)
            s_extents = cr.text_extents(self.subtitle)
            cr.move_to(cx - s_extents.width / 2.0 - s_extents.x_bearing, line_y + 26)
            cr.show_text(self.subtitle)

        cr.restore()


class SparklineWidget(Gtk.DrawingArea):
    """
    A small Cairo-rendered sparkline that shows the recent history of a metric.
    Stores up to MAX_POINTS readings in a ring buffer.
    """
    MAX_POINTS = 60

    def __init__(self, width=138, height=28, gauge_type="usage"):
        super().__init__()
        self.spark_width = width
        self.spark_height = height
        self.gauge_type = gauge_type
        self._values = []
        self.set_content_width(width)
        self.set_content_height(height)
        self.set_draw_func(self._on_draw)

    def push_value(self, value):
        """Add a new normalised (0-100) value to the history."""
        if value is None or value < 0:
            value = 0.0
        self._values.append(float(value))
        if len(self._values) > self.MAX_POINTS:
            self._values.pop(0)
        self.queue_draw()

    def _get_color(self, is_dark_bg):
        """Match colors from CircularGauge for consistency."""
        if self.gauge_type in ("temp", "temp_hotspot", "cpu_temp"):
            return (0.2, 0.75, 0.95) if is_dark_bg else (0.1, 0.6, 0.8)
        elif self.gauge_type in ("clock", "vram_clock"):
            return (0.65, 0.35, 0.95) if is_dark_bg else (0.50, 0.15, 0.80)
        elif self.gauge_type in ("power", "voltage"):
            return (0.98, 0.60, 0.10) if is_dark_bg else (0.85, 0.45, 0.0)
        elif self.gauge_type == "fan":
            return (0.15, 0.80, 0.75) if is_dark_bg else (0.05, 0.55, 0.55)
        elif self.gauge_type in ("vram", "gtt", "mem_busy"):
            return (0.25, 0.70, 1.0) if is_dark_bg else (0.05, 0.45, 0.85)
        elif self.gauge_type == "cpu":
            return (0.25, 0.80, 0.45) if is_dark_bg else (0.05, 0.60, 0.30)
        elif self.gauge_type in ("ram", "swap"):
            return (0.95, 0.40, 0.70) if is_dark_bg else (0.80, 0.15, 0.50)
        elif self.gauge_type == "net_down":
            return (0.10, 0.85, 0.55) if is_dark_bg else (0.00, 0.60, 0.40)  # Teal Green (download)
        elif self.gauge_type == "net_up":
            return (0.95, 0.50, 0.10) if is_dark_bg else (0.70, 0.30, 0.00)  # Deep Orange (upload)
        else:
            return (0.30, 0.65, 1.0) if is_dark_bg else (0.10, 0.40, 0.85)

    def _on_draw(self, area, cr, width, height):
        import cairo as _cairo
        import math
        try:
            fg_rgba = self.get_color()
            fg_r, fg_g, fg_b = fg_rgba.red, fg_rgba.green, fg_rgba.blue
            is_dark_bg = (fg_r * 0.299 + fg_g * 0.587 + fg_b * 0.114) > 0.5
        except Exception:
            is_dark_bg = True
            fg_r, fg_g, fg_b = 0.9, 0.9, 0.95
        r, g, b = self._get_color(is_dark_bg)
        vals = self._values
        n = len(vals)
        if n >= 2:
            pad = 2
            effective_w = width - 2 * pad
            effective_h = height - 2 * pad
            # Filled area
            cr.save()
            cr.set_source_rgba(r, g, b, 0.15)
            cr.move_to(pad, height - pad)
            for i, v in enumerate(vals):
                x = pad + (i / (n - 1)) * effective_w
                y = (height - pad) - (v / 100.0) * effective_h
                cr.line_to(x, y)
            cr.line_to(pad + effective_w, height - pad)
            cr.close_path()
            cr.fill()
            cr.restore()
            # Line
            cr.save()
            cr.set_source_rgba(r, g, b, 0.85)
            cr.set_line_width(1.5)
            cr.set_line_cap(_cairo.LINE_CAP_ROUND)
            cr.set_line_join(_cairo.LINE_JOIN_ROUND)
            first = True
            for i, v in enumerate(vals):
                x = pad + (i / (n - 1)) * effective_w
                y = (height - pad) - (v / 100.0) * effective_h
                if first:
                    cr.move_to(x, y)
                    first = False
                else:
                    cr.line_to(x, y)
            cr.stroke()
            cr.restore()
            # Dot at last point
            cr.save()
            last_x = pad + effective_w
            last_y = (height - pad) - (vals[-1] / 100.0) * effective_h
            cr.set_source_rgba(r, g, b, 1.0)
            cr.arc(last_x, last_y, 2.5, 0, 2 * math.pi)
            cr.fill()
            cr.restore()
        else:
            # Baseline
            cr.save()
            cr.set_source_rgba(fg_r, fg_g, fg_b, 0.08)
            cr.set_line_width(1.0)
            cr.move_to(0, height / 2)
            cr.line_to(width, height / 2)
            cr.stroke()
            cr.restore()





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

    def get_summary_card_order(self):
        raw_order = self.config.get("SUMMARY", "card_order", fallback="")
        if not raw_order:
            return []
        return [item.strip() for item in raw_order.split(",") if item.strip()]

    def set_summary_card_order(self, order):
        if "SUMMARY" not in self.config:
            self.config["SUMMARY"] = {}
        normalized = [str(item).strip() for item in order if str(item).strip()]
        self.config["SUMMARY"]["card_order"] = ",".join(normalized)
        self.save()

    def get_refresh_interval(self):
        return self.config.getint("PERFORMANCE", "refresh_interval_ms", fallback=1000)

    def set_refresh_interval(self, interval_ms: int):
        if "PERFORMANCE" not in self.config:
            self.config["PERFORMANCE"] = {}
        self.config["PERFORMANCE"]["refresh_interval_ms"] = str(interval_ms)
        self.save()

    def get_view_mode(self):
        return self.config.get("GENERAL", "view_mode", fallback="dashboard")

    def set_view_mode(self, mode: str):
        if "GENERAL" not in self.config:
            self.config["GENERAL"] = {}
        self.config["GENERAL"]["view_mode"] = str(mode)
        self.save()

Adw.init()

def get_gpu_stats_for_index(gpu_index):
    """
    Fetches GPU stats (VRAM, GTT/Shared Memory, Temperature, Hotspot, Clocks, Usage, Memory Bus, Fan Speed/RPM, Power, Voltage)
    by direct GPU index corresponding to /sys/class/drm/card{gpu_index}.
    """
    stats = {
        'mem_used': 0, 'mem_total': 0,
        'gtt_used': 0, 'gtt_total': 0,
        'temp': 0, 'temp_hotspot': 0,
        'clock_current': 0, 'clock_max': 0,
        'vram_clock': 0, 'vram_clock_max': 0,
        'usage': -1, 'mem_busy': -1,
        'fan_speed': -1, 'fan_rpm': -1,
        'power_usage': -1,
        'voltage': 0.0,
        'vram_type': '', 'compute_units': '', 'rop_count': '', 'instruction_set': ''
    }
    
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
                cmd = f"nvidia-smi -i {pci_addr} --query-gpu=memory.used,memory.total,temperature.gpu,utilization.gpu,clocks.current.graphics,clocks.max.graphics,clocks.current.memory,clocks.max.memory,fan.speed,power.draw,utilization.memory --format=csv,noheader,nounits"
                lines = fetchContentsFromCommand(cmd)
                if lines:
                    parts = [p.strip() for p in lines[0].split(',')]
                    if len(parts) >= 10:
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
                        stats['vram_clock'] = parse_val(parts[6])
                        stats['vram_clock_max'] = parse_val(parts[7])
                        stats['vram_type'] = 'GDDR'
                        stats['fan_speed'] = parse_val(parts[8], -1)
                        stats['power_usage'] = parse_val(parts[9], -1)
                        if len(parts) >= 11:
                            stats['mem_busy'] = parse_val(parts[10], -1)
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

            # 5. GTT / Shared Memory
            if os.path.exists(f"{card_path}/mem_info_gtt_used"):
                try:
                    with open(f"{card_path}/mem_info_gtt_used", 'r') as f:
                        stats['gtt_used'] = int(f.read().strip()) // (1024 * 1024)
                except: pass
            if os.path.exists(f"{card_path}/mem_info_gtt_total"):
                try:
                    with open(f"{card_path}/mem_info_gtt_total", 'r') as f:
                        stats['gtt_total'] = int(f.read().strip()) // (1024 * 1024)
                except: pass

            # 6. Generic hwmon fan/power/voltage checks if exposed
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
                    
                    fan_input = f"{hwmon}/fan1_input"
                    if os.path.exists(fan_input):
                        try:
                            with open(fan_input, 'r') as f:
                                stats['fan_rpm'] = int(f.read().strip())
                        except:
                            pass

                    power_input = f"{hwmon}/power1_average"
                    if not os.path.exists(power_input):
                        power_input = f"{hwmon}/power1_input"
                    if os.path.exists(power_input):
                        try:
                            with open(power_input, 'r') as f:
                                stats['power_usage'] = int(f.read().strip()) // 1000000
                        except:
                            pass

                    for vf in [f"{hwmon}/in0_input", f"{hwmon}/in1_input"]:
                        if os.path.exists(vf):
                            try:
                                with open(vf, 'r') as f:
                                    v_mv = int(f.read().strip())
                                if v_mv > 0:
                                    stats['voltage'] = v_mv / 1000.0
                                    break
                            except:
                                pass

            if stats['mem_total'] > 0 or stats['temp'] > 0 or stats['usage'] >= 0 or stats['clock_current'] > 0:
                return stats

        else:
            # Baseline / AMD sysfs fallback
            if os.path.exists(f"{card_path}/mem_info_vram_used"):
                try:
                    with open(f"{card_path}/mem_info_vram_used", 'r') as f:
                        stats['mem_used'] = int(f.read().strip()) // (1024 * 1024)
                except: pass
            
            if os.path.exists(f"{card_path}/mem_info_vram_total"):
                try:
                    with open(f"{card_path}/mem_info_vram_total", 'r') as f:
                        stats['mem_total'] = int(f.read().strip()) // (1024 * 1024)
                except: pass

            if os.path.exists(f"{card_path}/mem_info_gtt_used"):
                try:
                    with open(f"{card_path}/mem_info_gtt_used", 'r') as f:
                        stats['gtt_used'] = int(f.read().strip()) // (1024 * 1024)
                except: pass
            
            if os.path.exists(f"{card_path}/mem_info_gtt_total"):
                try:
                    with open(f"{card_path}/mem_info_gtt_total", 'r') as f:
                        stats['gtt_total'] = int(f.read().strip()) // (1024 * 1024)
                except: pass

            if os.path.exists(f"{card_path}/mem_busy_percent"):
                try:
                    with open(f"{card_path}/mem_busy_percent", 'r') as f:
                        stats['mem_busy'] = int(f.read().strip())
                except: pass

            hwmon_pattern = f"{card_path}/hwmon/hwmon*"
            hwmons = glob.glob(hwmon_pattern)
            if hwmons:
                for hwmon in hwmons:
                    temp_input = f"{hwmon}/temp1_input"
                    if os.path.exists(temp_input):
                        try:
                            with open(temp_input, 'r') as f:
                                stats['temp'] = int(f.read().strip()) // 1000
                        except: pass
                    
                    for tf in [f"{hwmon}/temp2_input", f"{hwmon}/temp3_input"]:
                        if os.path.exists(tf):
                            try:
                                with open(tf, 'r') as f:
                                    t_val = int(f.read().strip()) // 1000
                                if t_val > 0:
                                    stats['temp_hotspot'] = t_val
                                    break
                            except: pass

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
                        except: pass
                    
                    fan_input = f"{hwmon}/fan1_input"
                    if os.path.exists(fan_input):
                        try:
                            with open(fan_input, 'r') as f:
                                stats['fan_rpm'] = int(f.read().strip())
                        except: pass

                    power_input = f"{hwmon}/power1_average"
                    if not os.path.exists(power_input):
                        power_input = f"{hwmon}/power1_input"
                    if os.path.exists(power_input):
                        try:
                            with open(power_input, 'r') as f:
                                stats['power_usage'] = int(f.read().strip()) // 1000000
                        except: pass

                    for vf in [f"{hwmon}/in0_input", f"{hwmon}/in1_input"]:
                        if os.path.exists(vf):
                            try:
                                with open(vf, 'r') as f:
                                    v_mv = int(f.read().strip())
                                if v_mv > 0:
                                    stats['voltage'] = v_mv / 1000.0
                                    break
                            except: pass
            
            if os.path.exists(f"{card_path}/gpu_busy_percent"):
                try:
                    with open(f"{card_path}/gpu_busy_percent", 'r') as f:
                        stats['usage'] = int(f.read().strip())
                except: pass
            
            if os.path.exists(f"{card_path}/pp_dpm_sclk"):
                try:
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
                except: pass
            
            if os.path.exists(f"{card_path}/pp_dpm_mclk"):
                try:
                    with open(f"{card_path}/pp_dpm_mclk", 'r') as f:
                        max_mclk = 0
                        cur_mclk = 0
                        for line in f:
                            parts = line.split()
                            if len(parts) >= 2:
                                clk_s = parts[1].replace('Mhz', '').replace('MHz', '')
                                try:
                                    c_val = int(clk_s)
                                    if c_val > max_mclk: max_mclk = c_val
                                    if '*' in line: cur_mclk = c_val
                                except ValueError: pass
                        stats['vram_clock'] = cur_mclk
                        stats['vram_clock_max'] = max_mclk
                except: pass

            if stats['clock_current'] == 0 and hwmons:
                for hwmon in hwmons:
                    freq_input = f"{hwmon}/freq1_input"
                    if os.path.exists(freq_input):
                        try:
                            with open(freq_input, 'r') as f:
                                stats['clock_current'] = int(f.read().strip()) // (1000 * 1000)
                                break
                        except: pass

            if stats['mem_total'] > 0 or stats['gtt_total'] > 0 or stats['temp'] > 0 or stats['usage'] >= 0 or stats['clock_current'] > 0:
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
    if not display:
        return 1280, 800
    monitors = display.get_monitors()
    if not monitors or monitors.get_n_items() == 0:
        return 1280, 800
    max_w, max_h = 0, 0
    for i in range(monitors.get_n_items()):
        m = monitors.get_item(i)
        if m and m.is_valid():
            g = m.get_geometry()
            if g.width * g.height > max_w * max_h:
                max_w, max_h = g.width, g.height
    if max_w == 0 or max_h == 0:
        return 1280, 800
    return max_w, max_h



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

def parse_vulkan_devices(content):
    """
    Parse vulkaninfo GPU blocks and remove duplicate Flatpak/multi-ICD views.

    Physical and software devices are both retained. deviceUUID is the strongest
    identity and prevents identical PCI hardware, including separate cards of
    the same model, from being merged when UUIDs are available. For older output
    without UUIDs, only software-device identities are safely deduplicated.
    """
    if not content:
        return []

    blocks = re.split(r"(?m)(?=^GPU\s*\d+\s*:)", content)
    devices = []
    for block in blocks:
        match = re.match(r"(?m)^GPU\s*(\d+)\s*:\s*(.*)$", block)
        if not match:
            continue

        gpu_index = int(match.group(1))
        name = ""
        vendor_id = ""
        device_id = ""
        device_uuid = ""
        driver_name = ""
        driver_uuid = ""
        device_type = ""

        for line in block.splitlines():
            stripped = line.strip()
            if "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key == "deviceName":
                name = value
            elif key in ("vendorID", "vendorId"):
                vendor_id = value
            elif key in ("deviceID", "deviceId"):
                device_id = value
            elif key == "deviceUUID":
                device_uuid = value
            elif key == "driverName":
                driver_name = value
            elif key == "driverUUID":
                driver_uuid = value
            elif key == "deviceType":
                device_type = value

        if not name:
            name = match.group(2).strip() or f"GPU {gpu_index}"

        duplicate = False
        for previous in devices:
            previous_uuid = previous["device_uuid"]

            if device_uuid and previous_uuid:
                if device_uuid.upper() == previous_uuid.upper():
                    duplicate = True
                    break
                continue

            name_lower = name.lower()
            previous_name = previous["name"].lower()
            is_software = (
                "llvmpipe" in name_lower
                or "lavapipe" in name_lower
                or "swiftshader" in name_lower
                or "software" in device_type.lower()
            )
            previous_is_software = (
                "llvmpipe" in previous_name
                or "lavapipe" in previous_name
                or "swiftshader" in previous_name
                or "software" in previous["device_type"].lower()
            )
            if is_software and previous_is_software:
                if (name_lower == previous_name
                        and driver_name.lower() == previous["driver_name"].lower()):
                    duplicate = True
                    break

        if duplicate:
            continue

        devices.append({
            "index": gpu_index,
            "name": name,
            "vendor_id": vendor_id,
            "device_id": device_id,
            "device_uuid": device_uuid,
            "driver_name": driver_name,
            "driver_uuid": driver_uuid,
            "device_type": device_type,
            "block": block,
        })

    return devices

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
