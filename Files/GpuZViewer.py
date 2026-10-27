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

"""
GpuZViewer.py
-------------
Implements a TechPowerUp GPU-Z style presentation mode for GPU-Viewer.
Provides:
  - Graphics Card Tab: High-density specification sheet (Architecture, BIOS,
    IDs, Bus, Shaders, Memory, Clocks, Computing Checkboxes).
  - Sensors Tab: Real-time telemetry monitoring with sparkline graphs.
  - Advanced Tab: Subsystem capability inspector (Vulkan, OpenGL, OpenCL, etc.).
  - Bottom Bar: Multi-GPU switcher dropdown.
"""

import os
import re
import glob
import threading
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib, GdkPixbuf, Pango, Gdk

import const
import Filenames
from Common import (
    get_gpu_stats_for_index,
    SparklineWidget,
)
from SummaryViewer import (
    get_realtime_cpu_usage,
    get_realtime_cpu_temp,
    get_realtime_ram_usage,
)



# ---------------------------------------------------------------------------
# GPU-Z CSS Styling
# ---------------------------------------------------------------------------

GPUZ_CSS = """
.gpuz-container {
    background-color: @view_bg_color;
    padding: 6px;
}

.gpuz-card-frame {
    border: 1px solid rgba(128, 128, 128, 0.25);
    border-radius: 8px;
    background-color: @card_bg_color;
    padding: 6px 8px;
    margin-bottom: 6px;
}

.gpuz-header-title {
    font-size: 13pt;
    font-weight: 700;
}

.gpuz-field-label {
    font-size: 8.5pt;
    color: alpha(@window_fg_color, 0.7);
    font-weight: 600;
}

.gpuz-field-value {
    font-size: 9pt;
    font-weight: 600;
}

.gpuz-field-box {
    border: 1px solid rgba(128, 128, 128, 0.18);
    border-radius: 4px;
    padding: 3px 8px;
    min-height: 22px;
    background-color: alpha(@window_fg_color, 0.04);
}

.gpuz-tech-badge {
    border: 1px solid rgba(128, 128, 128, 0.25);
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 8.5pt;
    font-weight: 600;
}

.gpuz-tech-supported {
    background-color: alpha(#2ec27e, 0.15);
    color: #2ec27e;
    border-color: alpha(#2ec27e, 0.4);
}

.gpuz-tech-unsupported {
    background-color: alpha(@window_fg_color, 0.04);
    color: alpha(@window_fg_color, 0.4);
    border-color: alpha(@window_fg_color, 0.1);
}

.gpuz-sensor-row {
    padding: 4px 6px;
    border-bottom: 1px solid rgba(128, 128, 128, 0.12);
}

.gpuz-sensor-title {
    font-size: 9.5pt;
    font-weight: 500;
}

.gpuz-sensor-val {
    font-size: 9.5pt;
    font-weight: 700;
    font-family: monospace;
}

.gpuz-bottom-bar {
    border-top: 1px solid rgba(128, 128, 128, 0.2);
    padding: 6px 10px;
    background-color: alpha(@window_fg_color, 0.03);
}
"""


def _clean_device_type(raw_type: str) -> str:
    """Format Vulkan/OpenCL device types like PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU into Integrated GPU."""
    if not raw_type:
        return "—"
    t = str(raw_type).strip()
    for prefix in ("VK_PHYSICAL_DEVICE_TYPE_", "PHYSICAL_DEVICE_TYPE_"):
        if t.startswith(prefix):
            t = t[len(prefix):]
            break
    t = t.replace("_", " ").title()
    t = re.sub(r'\bGpu\b', 'GPU', t)
    t = re.sub(r'\bCpu\b', 'CPU', t)
    return t.strip() or "—"


def _clean_version(ver_str: str) -> str:
    """Strip redundant packed integers like (4211051) and trailing whitespace."""
    if not ver_str:
        return "—"
    s = str(ver_str).strip()
    s = re.sub(r'\s*\(\d+\)$', '', s).strip()
    return s if s else "—"


class GpuZView(Gtk.Box):
    """
    Main GPU-Z Style container widget.
    Integrates Graphics Card, Sensors, and Advanced tabs with a GPU switcher bottom bar.
    """

    def __init__(self, app, results: dict, summary_data: dict = None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.app = app
        self.results = results or {}
        self.summary_data = summary_data or {}
        self.selected_gpu_idx = 0
        self.sensor_timer_id = 0

        # Inject GPU-Z CSS provider
        css_prov = Gtk.CssProvider()
        css_prov.load_from_data(GPUZ_CSS.encode("utf-8"))
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display,
                css_prov,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )

        self.set_vexpand(True)
        self.set_hexpand(True)

        # Build view stack and tab switcher
        self.view_stack = Adw.ViewStack()
        self.view_stack.set_vexpand(True)

        self.tab_switcher = Adw.ViewSwitcher()
        self.tab_switcher.set_stack(self.view_stack)
        self.tab_switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)

        # Header bar for GPU-Z View
        self.header_bar = Adw.HeaderBar()
        self.header_bar.set_title_widget(self.tab_switcher)

        # Back / Dashboard Mode button on top left
        self.dashboard_button = Gtk.Button()
        self.dashboard_button.set_icon_name("view-grid-symbolic")
        self.dashboard_button.add_css_class("flat")
        self.dashboard_button.set_tooltip_text("Switch to Dashboard View (Ctrl+Z)")
        self.dashboard_button.connect("clicked", lambda _: self.app.set_view_mode("dashboard"))
        self.header_bar.pack_start(self.dashboard_button)

        # Theme toggle on top right
        if hasattr(self.app, "_on_theme_button_clicked"):
            theme_btn = Gtk.Button()
            theme_btn.set_icon_name("weather-clear-night-symbolic")
            theme_btn.add_css_class("flat")
            theme_btn.set_tooltip_text("Toggle Dark / Light Theme")
            theme_btn.connect("clicked", self.app._on_theme_button_clicked)
            self.header_bar.pack_end(theme_btn)

        self.append(self.header_bar)

        # Extract GPUs
        self.gpus = self._extract_gpu_list()

        # Build Tab 1: Graphics Card
        self.card_page = self._build_graphics_card_tab()
        self.view_stack.add_titled_with_icon(
            self.card_page, "card", "Graphics Card", "video-display-symbolic"
        )

        # Build Tab 2: Sensors
        self.sensors_page = self._build_sensors_tab()
        self.view_stack.add_titled_with_icon(
            self.sensors_page, "sensors", "Sensors", "utilities-system-monitor-symbolic"
        )

        # Build Tab 3: Advanced
        self.advanced_page = self._build_advanced_tab()
        self.view_stack.add_titled_with_icon(
            self.advanced_page, "advanced", "Advanced", "emblem-system-symbolic"
        )

        self.append(self.view_stack)

        # Bottom Bar: Multi-GPU selector
        self.bottom_bar = self._build_bottom_bar()
        self.append(self.bottom_bar)

        # Connect cleanup on destroy
        self.connect("destroy", self._on_destroy)

        # Start sensor polling
        self._start_sensor_polling()

    # -----------------------------------------------------------------------
    # Multi-GPU List & Data Helpers
    # -----------------------------------------------------------------------

    def _extract_gpu_list(self) -> list:
        """Extract available GPU list from summary_data or /sys/class/drm."""
        raw_gpus = self.summary_data.get("gpui_stats", [])
        valid_gpus = [
            g for g in raw_gpus
            if (g.get("vendor_id") or g.get("device_id"))
            and re.fullmatch(r'card\d+', g.get("card_name", ""))
        ]
        if valid_gpus:
            return valid_gpus

        # Fallback probe if summary_data was not yet gathered
        gpus = []
        card_dirs = sorted(glob.glob("/sys/class/drm/card[0-9]*"))
        for card_dir in card_dirs:
            card_name = os.path.basename(card_dir)
            if not re.fullmatch(r'card\d+', card_name):
                continue
            device_path = f"{card_dir}/device"
            if not os.path.isdir(device_path):
                continue

            vendor_id = ""
            device_id = ""
            if os.path.exists(f"{device_path}/vendor"):
                try:
                    with open(f"{device_path}/vendor", "r") as f:
                        vendor_id = f.read().strip()
                except Exception:
                    pass
            if os.path.exists(f"{device_path}/device"):
                try:
                    with open(f"{device_path}/device", "r") as f:
                        device_id = f.read().strip()
                except Exception:
                    pass

            if not vendor_id and not device_id:
                continue

            m = re.search(r'\d+', card_name)
            idx = int(m.group(0)) if m else 0
            gpus.append({
                "card_index": idx,
                "card_name": card_name,
                "vendor_id": vendor_id,
                "device_id": device_id,
                "stats": get_gpu_stats_for_index(idx) or {},
            })

        if gpus:
            return gpus

        # Fallback to Vulkan physical devices (filtering out CPU software renderers like llvmpipe)
        vk_devices = self.summary_data.get("vulkan", {}).get("devices", [])
        phys_devs = [
            d for d in vk_devices
            if "CPU" not in d.get("device_type", "").upper() and "LLVMPIPE" not in d.get("name", "").upper()
        ]
        if not phys_devs and vk_devices:
            phys_devs = vk_devices

        for i, dev in enumerate(phys_devs):
            gpus.append({
                "card_index": i,
                "card_name": f"vulkan{i}",
                "vendor_id": dev.get("vendor_id", ""),
                "device_id": dev.get("device_id", ""),
                "stats": {},
            })

        return gpus

    def _get_current_gpu(self) -> dict:
        """Return the dictionary for the currently selected GPU."""
        if 0 <= self.selected_gpu_idx < len(self.gpus):
            return self.gpus[self.selected_gpu_idx]
        return self.gpus[0] if self.gpus else {}

    def _get_vulkan_device(self, vendor_id, device_id) -> dict | None:
        """Find matching Vulkan device entry. Returns None if no device matches."""
        vk_devices = self.summary_data.get("vulkan", {}).get("devices", [])
        if not vk_devices:
            return None
        if not vendor_id and not device_id:
            idx = getattr(self, "selected_gpu_idx", 0)
            if 0 <= idx < len(vk_devices):
                return vk_devices[idx]
            return vk_devices[0]
        try:
            v_int = int(vendor_id, 16) if vendor_id else None
            d_int = int(device_id, 16) if device_id else None
        except ValueError:
            v_int = None
            d_int = None

        for dev in vk_devices:
            vk_v = dev.get("vendor_id")
            vk_d = dev.get("device_id")
            if vk_v and vk_d:
                try:
                    if int(vk_v, 16) == v_int and int(vk_d, 16) == d_int:
                        return dev
                except ValueError:
                    pass
        return None

    def _get_gpu_display_name(self, gpu: dict) -> str:
        """Resolve clean display name for the GPU."""
        v_id = gpu.get("vendor_id", "")
        d_id = gpu.get("device_id", "")
        vk_dev = self._get_vulkan_device(v_id, d_id)
        if vk_dev:
            if vk_dev.get("deviceName"):
                return vk_dev["deviceName"]
            if vk_dev.get("name"):
                return vk_dev["name"]
        
        # Vendor fallback
        try:
            v_int = int(v_id, 16)
            if v_int == 0x10de:
                return f"NVIDIA GeForce (Device {d_id})"
            elif v_int == 0x1002:
                return f"AMD Radeon (Device {d_id})"
            elif v_int == 0x8086:
                return f"Intel Graphics (Device {d_id})"
        except Exception:
            pass
        return f"Graphics Card ({gpu.get('card_name', 'GPU')})"

    def _get_vendor_logo_path(self, vendor_id_str: str) -> str:
        """Return vendor logo image path."""
        try:
            v = int(vendor_id_str, 16)
            if v == 0x1002:
                return "../Images/AMD_logo.png"
            elif v == 0x10de:
                return "../Images/nvidia_logo.png"
            elif v == 0x8086:
                return "../Images/intel-logo.png"
        except Exception:
            pass
        return "../Images/about-us.png"

    # -----------------------------------------------------------------------
    # Tab 1: Graphics Card Specification Sheet
    # -----------------------------------------------------------------------

    def _build_graphics_card_tab(self) -> Gtk.Widget:
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)

        self.card_content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.card_content_box.set_margin_start(8)
        self.card_content_box.set_margin_end(8)
        self.card_content_box.set_margin_top(6)
        self.card_content_box.set_margin_bottom(8)

        self._refresh_graphics_card_content()
        scroll.set_child(self.card_content_box)
        return scroll

    def _refresh_graphics_card_content(self):
        """Regenerate the Graphics Card metrics sheet for the selected GPU.

        Shows live API version data and GPU hardware metrics instead of a
        static database lookup — covering Vulkan, OpenGL, EGL, OpenCL,
        Vulkan Video, VDPAU and GPU hardware stats.
        """
        # Clear previous children
        child = self.card_content_box.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self.card_content_box.remove(child)
            child = nxt

        # Reset live-update label registry for this GPU
        self._hw_live_labels = {}

        gpu = self._get_current_gpu()
        gpu_name = self._get_gpu_display_name(gpu)
        v_id = gpu.get("vendor_id", "")
        d_id = gpu.get("device_id", "")
        vk_dev = self._get_vulkan_device(v_id, d_id) or {}
        stats = gpu.get("stats", {}) or get_gpu_stats_for_index(gpu.get("card_index", 0)) or {}

        # Pull parsed summary blobs (populated by background worker)
        vk_data   = self.summary_data.get("vulkan",       {})
        gl_data   = self.summary_data.get("opengl",       {})
        cl_data   = self.summary_data.get("opencl",       {})
        vv_data   = self.summary_data.get("vulkan_video", {})
        vdpau_data = self.summary_data.get("vdpau",       {})

        # ── Header Box: Logo + Name ────────────────────────────────────
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_box.add_css_class("gpuz-card-frame")

        logo_path = self._get_vendor_logo_path(v_id)
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(logo_path, 42, 42, True)
            logo_img = Gtk.Picture.new_for_pixbuf(pixbuf)
            logo_img.set_size_request(42, 42)
            header_box.append(logo_img)
        except Exception:
            pass

        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        title_box.set_valign(Gtk.Align.CENTER)
        name_lbl = Gtk.Label(label=gpu_name)
        name_lbl.add_css_class("gpuz-header-title")
        name_lbl.set_halign(Gtk.Align.START)
        name_lbl.set_wrap(True)
        name_lbl.set_max_width_chars(32)
        title_box.append(name_lbl)

        sub_text = f"Card: {gpu.get('card_name', 'card0')} • PCI: {gpu.get('pci_address', '—')}"
        sub_lbl = Gtk.Label(label=sub_text)
        sub_lbl.add_css_class("dim-label")
        sub_lbl.set_halign(Gtk.Align.START)
        title_box.append(sub_lbl)

        header_box.append(title_box)
        self.card_content_box.append(header_box)

        # Helper: build a 2-column dual-field row inside a parent box
        def _add_dual_row(parent, l1, v1, l2, v2, live_key1=None, live_key2=None):
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            row_box.set_hexpand(True)
            row_box.set_homogeneous(True)
            row_box.append(self._make_field_cell(l1, v1, live_key=live_key1))
            if l2 or v2:
                row_box.append(self._make_field_cell(l2, v2, live_key=live_key2))
            else:
                spacer = Gtk.Box()
                spacer.set_hexpand(True)
                row_box.append(spacer)
            parent.append(row_box)

        # Helper: build a full-width single-field row
        def _add_single_row(parent, label, value, live_key=None):
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            row_box.set_hexpand(True)
            cell = self._make_field_cell(label, value, live_key=live_key)
            cell.set_hexpand(True)
            row_box.append(cell)
            parent.append(row_box)

        # Helper: section header label
        def _make_section(title) -> Gtk.Box:
            frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            frame.add_css_class("gpuz-card-frame")
            hdr = Gtk.Label(label=title)
            hdr.add_css_class("gpuz-field-label")
            hdr.set_halign(Gtk.Align.START)
            frame.append(hdr)
            sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            sep.set_margin_bottom(1)
            frame.append(sep)
            return frame

        # ── GPU Hardware Stats ─────────────────────────────────────────
        hw_frame = _make_section("GPU Hardware")

        dev_id_display = f"{v_id.upper()} / {d_id.upper()}" if v_id or d_id else "—"
        driver_val = gpu.get("driver") or vk_dev.get("driver_name") or "—"
        if vk_dev.get("driver_version"):
            driver_val += f"  {vk_dev['driver_version']}"
        bios_val = gpu.get("vbios") or "—"
        bus_interface = (
            f"{gpu.get('pcie_link_width', '')}  @  {gpu.get('pcie_link_speed', '—')}".strip(" @")
            if gpu.get("pcie_link_width") else "—"
        )

        vram_tot = stats.get("mem_total", 0)
        vram_size_display = f"{vram_tot} MB" if vram_tot > 0 else "—"
        vram_type = stats.get("vram_type") or gpu.get("vram_type") or "—"
        vram_used = stats.get("mem_used", 0)
        vram_used_display = f"{vram_used} MB" if vram_used > 0 else "—"

        core_clk = f"{stats.get('clock_current', 0)} MHz" if stats.get("clock_current", 0) > 0 else "—"
        boost_clk = f"{stats.get('clock_max', 0)} MHz" if stats.get("clock_max", 0) > 0 else "—"
        mem_clk = stats.get("vram_clock_max") or stats.get("vram_clock", 0)
        mem_clk_disp = f"{mem_clk} MHz" if mem_clk > 0 else "—"

        temp_val = stats.get("temp", 0)
        temp_disp = f"{temp_val} °C" if temp_val and temp_val > 0 else "—"
        power_val = stats.get("power_usage", -1)
        power_disp = f"{power_val} W" if power_val and power_val >= 0 else "—"
        usage_val = stats.get("usage", -1)
        usage_disp = f"{usage_val} %" if usage_val and usage_val >= 0 else "—"
        fan_val = stats.get("fan_speed", -1)
        fan_disp = f"{fan_val} %" if fan_val and fan_val >= 0 else "—"

        gtt_used = stats.get("gtt_used", 0)
        gtt_total = stats.get("gtt_total", 0)
        if gtt_total > 0:
            gtt_disp = f"{gtt_used} / {gtt_total} MB"
        elif gtt_used > 0:
            gtt_disp = f"{gtt_used} MB"
        else:
            gtt_disp = "—"

        _add_dual_row(hw_frame, "Device ID",    dev_id_display,   "Driver",      driver_val)
        _add_dual_row(hw_frame, "VBIOS",        bios_val,         "PCIe Link",   bus_interface)
        _add_dual_row(hw_frame, "VRAM Total",   vram_size_display,"VRAM Type",   vram_type)
        _add_dual_row(hw_frame, "VRAM Used",    vram_used_display,"GPU Usage",   usage_disp,
                      live_key1="hw_vram_used", live_key2="hw_usage")
        _add_dual_row(hw_frame, "GTT Memory",   gtt_disp,         "GPU Clock",   core_clk)
        _add_dual_row(hw_frame, "Boost Clock",  boost_clk,        "Memory Clock",mem_clk_disp)
        _add_dual_row(hw_frame, "Temperature",  temp_disp,        "Power Draw",  power_disp,
                      live_key1="hw_temp", live_key2="hw_power")
        _add_dual_row(hw_frame, "Fan Speed",    fan_disp,         "",            "",
                      live_key1="hw_fan")
        self.card_content_box.append(hw_frame)

        # ── Vulkan ────────────────────────────────────────────────────
        vk_frame = _make_section("Vulkan")
        vk_api = _clean_version(vk_dev.get("api_version") or vk_data.get("instance_version", "—"))
        vk_inst_ver = _clean_version(vk_data.get("instance_version", "—"))
        vk_drv_name = (vk_dev.get("driver_name") or "—").strip()
        vk_drv_ver  = _clean_version(vk_dev.get("driver_version", "—"))
        vk_drv_info = (vk_dev.get("driver_info") or "—").strip()
        vk_dev_type = _clean_device_type(vk_dev.get("device_type", "—"))
        vk_conform  = (vk_dev.get("conformance_version") or "—").strip()
        vk_vendor_id = (vk_dev.get("vendor_id") or "—").strip()
        vk_device_id = (vk_dev.get("device_id") or "—").strip()
        vk_ext_cnt  = str(vk_dev.get("extensions_count", 0)) if vk_dev.get("extensions_count") else "—"
        vk_fmt_cnt  = str(vk_dev.get("formats_count", 0)) if vk_dev.get("formats_count") else "—"
        vk_mem_types = str(vk_dev.get("memory_types_count", 0)) if vk_dev.get("memory_types_count") else "—"
        vk_mem_heaps = str(vk_dev.get("memory_heaps_count", 0)) if vk_dev.get("memory_heaps_count") else "—"
        vk_queue_fam = str(vk_dev.get("queue_count", 0)) if vk_dev.get("queue_count") else "—"
        vk_inst_ext_cnt = str(vk_data.get("instance_extensions_count", 0)) if vk_data.get("instance_extensions_count") else "—"
        vk_inst_layers_cnt = str(vk_data.get("instance_layers_count", 0)) if vk_data.get("instance_layers_count") else "—"
        vk_pipeline_uuid = (vk_dev.get("pipelineCacheUUID") or "—").strip()
        vk_uuid     = (vk_dev.get("device_uuid") or "—").strip()
        vk_drv_uuid = (vk_dev.get("driver_uuid") or "—").strip()

        # Ray tracing and Mesh shader support
        vk_exts = vk_dev.get("extensions", [])
        has_rt = vk_dev.get("has_ray_tracing")
        if has_rt is None:
            exts_lower = [e.lower() for e in vk_exts]
            has_rt = any("ray_tracing" in e or "ray_query" in e or "acceleration_structure" in e for e in exts_lower)
        has_mesh = vk_dev.get("has_mesh_shader")
        if has_mesh is None:
            exts_lower = [e.lower() for e in vk_exts]
            has_mesh = any("mesh_shader" in e for e in exts_lower)

        # Fallback to inspecting vulkaninfo output directly if extensions list wasn't populated
        if not vk_exts and not has_rt and not has_mesh and os.path.exists(Filenames.vulkaninfo_output_file):
            try:
                with open(Filenames.vulkaninfo_output_file, "r") as f:
                    v_content = f.read()
                blocks = re.split(r'\nGPU\d+:', "\n" + v_content)
                target_block = None
                dev_name = vk_dev.get("name") or vk_dev.get("deviceName", "")
                dev_id = vk_dev.get("device_id") or d_id
                for b in blocks[1:]:
                    if dev_name and dev_name in b:
                        target_block = b
                        break
                    if dev_id and dev_id in b:
                        target_block = b
                        break
                if not target_block and blocks[1:]:
                    target_block = blocks[1]
                if target_block:
                    has_rt = (
                        bool(re.search(r'\b(vk_khr_ray_tracing_pipeline|vk_khr_ray_query|vk_nv_ray_tracing|vk_khr_acceleration_structure)\b', target_block, re.I))
                        or bool(re.search(r'\b(raytracingpipeline|rayquery|accelerationstructure|raytracing|raytracingpositionfetch)\s*=\s*true\b', target_block, re.I))
                    )
                    has_mesh = (
                        bool(re.search(r'\b(vk_ext_mesh_shader|vk_nv_mesh_shader)\b', target_block, re.I))
                        or bool(re.search(r'\b(meshshader|taskshader)\s*=\s*true\b', target_block, re.I))
                    )
            except Exception:
                pass

        vk_rt_str = "Supported" if has_rt else "Not Available"
        vk_mesh_str = "Supported" if has_mesh else "Not Available"

        _add_dual_row(vk_frame, "API Version",        vk_api,             "Instance Ver.",   vk_inst_ver)
        _add_dual_row(vk_frame, "Driver Name",        vk_drv_name,        "Driver Ver.",     vk_drv_ver)
        if vk_drv_info and vk_drv_info not in ("—", "-"):
            _add_single_row(vk_frame, "Driver Info", vk_drv_info)
        _add_dual_row(vk_frame, "Device Type",        vk_dev_type,        "Conformance",     vk_conform)
        _add_dual_row(vk_frame, "Vendor ID",          vk_vendor_id,       "Device ID",       vk_device_id)
        _add_dual_row(vk_frame, "Device Extensions",  vk_ext_cnt,         "Device Formats",  vk_fmt_cnt)
        _add_dual_row(vk_frame, "Instance Ext.",      vk_inst_ext_cnt,    "Instance Layers", vk_inst_layers_cnt)
        _add_dual_row(vk_frame, "Memory Types",       vk_mem_types,       "Memory Heaps",    vk_mem_heaps)
        _add_dual_row(vk_frame, "Queue Families",     vk_queue_fam,       "",                "")
        _add_dual_row(vk_frame, "Ray Tracing",        vk_rt_str,          "Mesh Shaders",    vk_mesh_str)
        if vk_pipeline_uuid and vk_pipeline_uuid not in ("—", "-"):
            _add_single_row(vk_frame, "Pipeline Cache UUID", vk_pipeline_uuid)
        if vk_uuid and vk_uuid not in ("—", "-"):
            _add_single_row(vk_frame, "Device UUID", vk_uuid)
        if vk_drv_uuid and vk_drv_uuid not in ("—", "-"):
            _add_single_row(vk_frame, "Driver UUID", vk_drv_uuid)

        def _format_video_profile_counts(profile_names, profile_counts, mode):
            if not profile_names:
                return None
            parts = []
            for profile_name in profile_names:
                count = profile_counts.get(profile_name, 0)
                label = f"{profile_name} {mode}"
                if count > 0:
                    label = f"{label} - {count}"
                parts.append(label)
            return "; ".join(parts)

        if vk_dev.get("video_decode_profiles"):
            decode_text = _format_video_profile_counts(
                vk_dev["video_decode_profiles"],
                vk_dev.get("video_decode_profile_counts", {}),
                "Decode"
            )
            if decode_text:
                _add_single_row(vk_frame, "Video Decode Profiles", decode_text)

        if vk_dev.get("video_encode_profiles"):
            encode_text = _format_video_profile_counts(
                vk_dev["video_encode_profiles"],
                vk_dev.get("video_encode_profile_counts", {}),
                "Encode"
            )
            if encode_text:
                _add_single_row(vk_frame, "Video Encode Profiles", encode_text)

        self.card_content_box.append(vk_frame)

        # ── OpenGL & EGL ─────────────────────────────────────────────
        gl_frame = _make_section("OpenGL / EGL")
        gl_vendor   = gl_data.get("vendor", "—")
        gl_renderer = gl_data.get("renderer", "—")
        gl_version  = gl_data.get("version", "—")
        gl_glsl     = gl_data.get("shading_language_version", "—")
        gl_es_ver   = gl_data.get("es_version", "—")
        gl_glx_ver  = gl_data.get("glx_version", "—")
        egl_version = gl_data.get("egl_version", "—")
        gl_ext_cnt  = str(gl_data.get("extensions_count", 0)) if gl_data.get("extensions_count") else "—"
        egl_ext_cnt = str(gl_data.get("egl_count", 0)) if gl_data.get("egl_count") else "—"
        glx_ext_cnt = str(gl_data.get("glx_extension_count", 0)) if gl_data.get("glx_extension_count") else "—"
        glx_vis_cnt = str(gl_data.get("glx_visual_count", 0)) if gl_data.get("glx_visual_count") else "—"
        fbcfg_cnt   = str(gl_data.get("fbconfig_count", 0)) if gl_data.get("fbconfig_count") else "—"
        es_ext_cnt  = str(gl_data.get("es_extensions_count", 0)) if gl_data.get("es_extensions_count") else "—"

        _add_dual_row(gl_frame, "Vendor",         gl_vendor,    "Renderer",       gl_renderer)
        _add_dual_row(gl_frame, "OpenGL Version", gl_version,   "GLSL Version",   gl_glsl)
        _add_dual_row(gl_frame, "OpenGL ES",      gl_es_ver,    "GLX Version",    gl_glx_ver)
        _add_dual_row(gl_frame, "EGL Version",    egl_version,  "EGL Extensions", egl_ext_cnt)
        _add_dual_row(gl_frame, "GL Extensions",  gl_ext_cnt,   "GLX Extensions", glx_ext_cnt)
        _add_dual_row(gl_frame, "ES Extensions",  es_ext_cnt,   "GLX Visuals",    glx_vis_cnt)
        _add_dual_row(gl_frame, "FB Configs",     fbcfg_cnt,    "",               "")
        self.card_content_box.append(gl_frame)

        # ── OpenCL ────────────────────────────────────────────────────
        cl_frame = _make_section("OpenCL")
        cl_platforms = cl_data.get("platforms", [])
        if cl_platforms:
            plat0 = cl_platforms[0]
            cl_plat_name = plat0.get("name", "—")
            cl_plat_ver  = plat0.get("version", "—")
            cl_plat_ext  = str(plat0.get("extensions_count", 0)) if plat0.get("extensions_count") else "—"
            cl_plat_cnt  = str(len(cl_platforms))
            cl_devs = plat0.get("devices", [])
            if cl_devs:
                dev0 = cl_devs[0]
                cl_dev_name  = dev0.get("name", "—")
                cl_dev_type  = dev0.get("device_type", "—")
                cl_dev_ver   = dev0.get("version", "—")
                cl_opencl_c  = dev0.get("opencl_c_version", "—")
                cl_cus       = str(dev0.get("compute_units", "—"))
                cl_wgs       = str(dev0.get("workgroup_size", "—"))
                cl_gmem      = dev0.get("global_memory", "—")
                cl_lmem      = dev0.get("local_memory", "—")
                cl_clk       = str(dev0.get("max_clock", "—"))
                cl_drv_ver   = dev0.get("driver_version", "—")
                cl_dev_ext   = str(dev0.get("extensions_count", 0)) if dev0.get("extensions_count") else "—"
            else:
                cl_dev_name = cl_dev_type = cl_dev_ver = cl_opencl_c = "—"
                cl_cus = cl_wgs = cl_gmem = cl_lmem = cl_clk = cl_drv_ver = cl_dev_ext = "—"
        else:
            cl_plat_name = cl_plat_ver = cl_plat_ext = cl_plat_cnt = "—"
            cl_dev_name = cl_dev_type = cl_dev_ver = cl_opencl_c = "—"
            cl_cus = cl_wgs = cl_gmem = cl_lmem = cl_clk = cl_drv_ver = cl_dev_ext = "—"

        _add_dual_row(cl_frame, "Platform",       cl_plat_name, "Platforms",      cl_plat_cnt)
        _add_dual_row(cl_frame, "Platform Ver.",  cl_plat_ver,  "Plat. Ext.",     cl_plat_ext)
        _add_dual_row(cl_frame, "Device",         cl_dev_name,  "Device Type",    cl_dev_type)
        _add_dual_row(cl_frame, "Device Ver.",    cl_dev_ver,   "OpenCL C",       cl_opencl_c)
        _add_dual_row(cl_frame, "Compute Units",  cl_cus,       "Max Workgroup",  cl_wgs)
        _add_dual_row(cl_frame, "Global Mem.",    cl_gmem,      "Local Mem.",     cl_lmem)
        _add_dual_row(cl_frame, "Max Clock",      cl_clk,       "Dev. Extensions",cl_dev_ext)
        _add_dual_row(cl_frame, "Driver Ver.",    cl_drv_ver,   "",               "")
        self.card_content_box.append(cl_frame)

        # ── Vulkan Video ──────────────────────────────────────────────
        vv_frame = _make_section("Vulkan Video")
        vv_supported = "Yes" if vv_data.get("supported") else "No"
        vv_profiles  = vv_data.get("profiles", [])
        vv_codecs    = ", ".join(vv_profiles) if vv_profiles else "—"
        vv_count     = str(len(vv_profiles)) if vv_profiles else "0"
        # Decode / Encode split
        vv_decode = ", ".join(p for p in vv_profiles if "DECODE" in p.upper() or p.upper() in ("H264","H265","AV1","VP8","VP9","HEVC")) or "—"
        vv_encode = ", ".join(p for p in vv_profiles if "ENCODE" in p.upper()) or "—"
        _add_dual_row(vv_frame, "Supported",    vv_supported, "Codec Count",   vv_count)
        _add_single_row(vv_frame, "Codecs",     vv_codecs)
        self.card_content_box.append(vv_frame)

        # ── VDPAU ─────────────────────────────────────────────────────
        vdpau_frame = _make_section("VDPAU")
        vdpau_supported = "Yes" if vdpau_data.get("supported") else "No"
        vdpau_api  = vdpau_data.get("api_version", "—")
        vdpau_rend = vdpau_data.get("renderer", "—")
        _add_dual_row(vdpau_frame, "Supported",  vdpau_supported, "API Version", vdpau_api)
        _add_single_row(vdpau_frame, "Renderer", vdpau_rend)
        self.card_content_box.append(vdpau_frame)

        # ── API Support Badges ─────────────────────────────────────────
        tech_frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        tech_frame.add_css_class("gpuz-card-frame")

        tech_title = Gtk.Label(label="API Support")
        tech_title.add_css_class("gpuz-field-label")
        tech_title.set_halign(Gtk.Align.START)
        tech_frame.append(tech_title)

        tech_flow = Gtk.FlowBox()
        tech_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        tech_flow.set_max_children_per_line(4)
        tech_flow.set_min_children_per_line(2)
        tech_flow.set_row_spacing(6)
        tech_flow.set_column_spacing(6)
        tech_flow.set_homogeneous(True)

        # Determine live capabilities from parsed data
        has_vulkan       = bool(vk_dev) or vk_data.get("supported", False)
        has_opengl       = bool(gl_data.get("version"))
        has_egl          = bool(gl_data.get("egl_version")) or gl_data.get("egl_count", 0) > 0
        has_opencl       = bool(cl_platforms) or cl_data.get("supported", False)
        has_vulkan_video = vv_data.get("supported", False) or bool(vv_profiles)
        has_vdpau        = vdpau_data.get("supported", False)
        has_raytracing   = has_rt
        has_mesh_shaders = has_mesh

        techs = [
            ("Vulkan",        has_vulkan),
            ("OpenGL",        has_opengl),
            ("EGL",           has_egl),
            ("OpenCL",        has_opencl),
            ("Vulkan Video",  has_vulkan_video),
            ("VDPAU",         has_vdpau),
            ("Ray Tracing",   has_raytracing),
            ("Mesh Shaders",  has_mesh_shaders),
        ]

        for name, supported in techs:
            b = self._make_tech_badge(name, supported)
            tech_flow.append(b)

        tech_frame.append(tech_flow)
        self.card_content_box.append(tech_frame)

    def _make_field_cell(self, label: str, value: str, live_key: str = None) -> Gtk.Box:
        """Create a compact GPU-Z field with label and read-only value.

        Args:
            label:    Header label text.
            value:    Initial value text.
            live_key: If set, the value label is registered in
                      ``self._hw_live_labels[live_key]`` so that the sensor
                      polling loop can update it without rebuilding the whole tab.
        """
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box.add_css_class("gpuz-field-box")
        box.set_hexpand(True)
        box.set_valign(Gtk.Align.CENTER)

        lbl = Gtk.Label(label=label)
        lbl.add_css_class("gpuz-field-label")
        lbl.set_halign(Gtk.Align.START)
        lbl.set_valign(Gtk.Align.CENTER)
        lbl.set_xalign(0)
        box.append(lbl)

        clean_val = str(value).strip() if value is not None and str(value).strip() else "—"
        clean_val = re.sub(r'\s*\(\d+\)$', '', clean_val).strip()

        val = Gtk.Label(label=clean_val)
        val.add_css_class("gpuz-field-value")
        val.set_halign(Gtk.Align.END)
        val.set_valign(Gtk.Align.CENTER)
        val.set_hexpand(True)
        val.set_selectable(True)
        val.set_wrap(True)
        val.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        val.set_xalign(1)
        box.append(val)

        if live_key is not None:
            if not hasattr(self, "_hw_live_labels"):
                self._hw_live_labels = {}
            self._hw_live_labels[live_key] = val

        return box

    def _make_tech_badge(self, name: str, supported: bool) -> Gtk.Widget:
        """Create a GPU-Z style capability checkbox / badge."""
        badge = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        badge.add_css_class("gpuz-tech-badge")
        if supported:
            badge.add_css_class("gpuz-tech-supported")
            icon = Gtk.Image.new_from_icon_name("object-select-symbolic")
        else:
            badge.add_css_class("gpuz-tech-unsupported")
            icon = Gtk.Image.new_from_icon_name("window-close-symbolic")
        icon.set_pixel_size(12)
        badge.append(icon)

        lbl = Gtk.Label(label=name)
        lbl.set_halign(Gtk.Align.START)
        badge.append(lbl)
        return badge

    # -----------------------------------------------------------------------
    # Tab 2: Sensors Telemetry
    # -----------------------------------------------------------------------

    def _build_sensors_tab(self) -> Gtk.Widget:
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(8)
        box.set_margin_bottom(12)

        sensors_frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        sensors_frame.add_css_class("gpuz-card-frame")

        self.sensor_widgets = {}

        sensor_defs = [
            ("gpu_clock", "GPU Clock", "MHz", "clock", 0, 3000),
            ("mem_clock", "Memory Clock", "MHz", "vram_clock", 0, 3000),
            ("gpu_temp", "GPU Temperature", "°C", "temp", 0, 105),
            ("hotspot_temp", "GPU Hot Spot", "°C", "temp_hotspot", 0, 115),
            ("fan_pct", "Fan Speed (%)", "%", "fan", 0, 100),
            ("fan_rpm", "Fan Speed (RPM)", "RPM", "fan", 0, 4000),
            ("gpu_load", "GPU Load", "%", "usage", 0, 100),
            ("mem_busy", "Memory Controller Load", "%", "mem_busy", 0, 100),
            ("vram_used", "Memory Used (Dedicated)", "MB", "vram", 0, 16384),
            ("gtt_used", "Memory Used (Shared / GTT)", "MB", "gtt", 0, 16384),
            ("power", "Board Power Draw", "W", "power", 0, 450),
            ("voltage", "GPU Voltage (VDDC)", "V", "voltage", 0, 1.5),
            ("cpu_temp", "CPU Temperature", "°C", "cpu_temp", 0, 105),
            ("cpu_usage", "CPU Load", "", "cpu", 0, 100),
            ("ram_used", "System RAM Used", "", "ram", 0, 100),
        ]

        for key, title, unit, gauge_type, min_v, max_v in sensor_defs:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            row.add_css_class("gpuz-sensor-row")
            row.set_hexpand(True)

            t_lbl = Gtk.Label(label=title)
            t_lbl.add_css_class("gpuz-sensor-title")
            t_lbl.set_halign(Gtk.Align.START)
            t_lbl.set_hexpand(True)
            row.append(t_lbl)

            v_lbl = Gtk.Label(label="—")
            v_lbl.add_css_class("gpuz-sensor-val")
            v_lbl.set_halign(Gtk.Align.END)
            v_lbl.set_size_request(85, -1)
            row.append(v_lbl)

            sparkline = SparklineWidget(width=100, height=20, gauge_type=gauge_type)
            row.append(sparkline)

            sensors_frame.append(row)
            self.sensor_widgets[key] = {
                "label": v_lbl,
                "sparkline": sparkline,
                "unit": unit,
                "min": min_v,
                "max": max_v,
            }

        box.append(sensors_frame)
        scroll.set_child(box)
        return scroll

    def _update_sensors(self):
        """Poll telemetry and update values and sparklines."""
        gpu = self._get_current_gpu()
        idx = gpu.get("card_index", 0)
        stats = get_gpu_stats_for_index(idx) or {}

        # System telemetry
        cpu_usage_str = get_realtime_cpu_usage()
        cpu_temp_val = get_realtime_cpu_temp()
        ram_usage_str = get_realtime_ram_usage()

        def _set_val(key, val_num, display_text=None):
            w = self.sensor_widgets.get(key)
            if not w:
                return
            lbl = w["label"]
            spark = w["sparkline"]
            unit = w["unit"]

            if val_num is not None and val_num >= 0:
                text = display_text if display_text else f"{val_num} {unit}".strip()
                lbl.set_label(text)
                # Normalise to 0-100 range for sparkline
                max_v = w["max"] or 100
                norm_val = min(100.0, max(0.0, (float(val_num) / max_v) * 100.0))
                spark.push_value(norm_val)
            else:
                lbl.set_label("—")
                spark.push_value(0)

        # GPU stats mapping
        _set_val("gpu_clock", stats.get("clock_current", 0))
        _set_val("mem_clock", stats.get("vram_clock", 0))
        _set_val("gpu_temp", stats.get("temp", 0))
        _set_val("hotspot_temp", stats.get("temp_hotspot", 0))
        _set_val("fan_pct", stats.get("fan_speed", -1))
        _set_val("fan_rpm", stats.get("fan_rpm", -1))
        _set_val("gpu_load", stats.get("usage", -1))
        _set_val("mem_busy", stats.get("mem_busy", -1))
        _set_val("vram_used", stats.get("mem_used", 0))
        _set_val("gtt_used", stats.get("gtt_used", 0))
        _set_val("power", stats.get("power_usage", -1))
        
        volt = stats.get("voltage", 0.0)
        _set_val("voltage", volt, f"{volt:.3f} V" if volt > 0 else "—")

        # CPU & RAM
        if cpu_temp_val is not None:
            _set_val("cpu_temp", cpu_temp_val)
        try:
            m = re.search(r'(\d+)', cpu_usage_str)
            if m:
                _set_val("cpu_usage", int(m.group(1)), cpu_usage_str)
        except Exception:
            pass

        try:
            m = re.search(r'(\d+)%', ram_usage_str)
            pct = int(m.group(1)) if m else 0
            _set_val("ram_used", pct, ram_usage_str)
        except Exception:
            pass

        # ── Real-time updates for GPU Hardware tab labels ──────────────────
        # Update Temperature, Power Draw, Fan Speed, GPU Usage and VRAM Used
        # in-place without triggering a full tab rebuild (avoids flicker and
        # scroll resets).
        live = getattr(self, "_hw_live_labels", {})
        if live:
            temp_v = stats.get("temp", 0)
            if "hw_temp" in live:
                live["hw_temp"].set_label(
                    f"{temp_v} °C" if temp_v and temp_v > 0 else "—"
                )
            pwr_v = stats.get("power_usage", -1)
            if "hw_power" in live:
                live["hw_power"].set_label(
                    f"{pwr_v} W" if pwr_v is not None and pwr_v >= 0 else "—"
                )
            fan_v = stats.get("fan_speed", -1)
            if "hw_fan" in live:
                live["hw_fan"].set_label(
                    f"{fan_v} %" if fan_v is not None and fan_v >= 0 else "—"
                )
            usage_v = stats.get("usage", -1)
            if "hw_usage" in live:
                live["hw_usage"].set_label(
                    f"{usage_v} %" if usage_v is not None and usage_v >= 0 else "—"
                )
            vram_used_v = stats.get("mem_used", 0)
            if "hw_vram_used" in live:
                live["hw_vram_used"].set_label(
                    f"{vram_used_v} MB" if vram_used_v and vram_used_v > 0 else "—"
                )

    # -----------------------------------------------------------------------
    # Tab 3: Advanced API & Subsystem Inspector
    # -----------------------------------------------------------------------

    def _build_advanced_tab(self) -> Gtk.Widget:
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(8)
        box.set_margin_bottom(12)

        # Category Dropdown
        cat_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        cat_box.add_css_class("gpuz-card-frame")

        cat_lbl = Gtk.Label(label="Subsystem:")
        cat_lbl.add_css_class("gpuz-field-label")
        cat_box.append(cat_lbl)

        categories = [
            "Vulkan Limits & Properties",
            "OpenGL & GLX Capabilities",
            "OpenCL Platform & Devices",
            "Vulkan Video Codecs",
            "VDPAU Hardware Decoding",
            "System & OS Details",
        ]
        string_list = Gtk.StringList.new(categories)
        self.adv_dropdown = Gtk.DropDown.new(string_list, None)
        self.adv_dropdown.set_hexpand(True)
        cat_box.append(self.adv_dropdown)
        box.append(cat_box)

        # Content container
        self.adv_content_frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.adv_content_frame.add_css_class("gpuz-card-frame")
        box.append(self.adv_content_frame)

        self.adv_dropdown.connect("notify::selected", lambda *_: self._refresh_advanced_content())
        self._refresh_advanced_content()

        scroll.set_child(box)
        return scroll

    def _refresh_advanced_content(self):
        """Display property list for the selected category."""
        child = self.adv_content_frame.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self.adv_content_frame.remove(child)
            child = nxt

        idx = self.adv_dropdown.get_selected()
        gpu = self._get_current_gpu()
        v_id = gpu.get("vendor_id", "")
        d_id = gpu.get("device_id", "")
        vk_dev = self._get_vulkan_device(v_id, d_id) or {}

        rows = []
        if idx == 0:  # Vulkan
            vk_exts = vk_dev.get("extensions", [])
            has_rt = vk_dev.get("has_ray_tracing")
            if has_rt is None:
                exts_lower = [e.lower() for e in vk_exts]
                has_rt = any("ray_tracing" in e or "ray_query" in e or "acceleration_structure" in e for e in exts_lower)
            has_mesh = vk_dev.get("has_mesh_shader")
            if has_mesh is None:
                exts_lower = [e.lower() for e in vk_exts]
                has_mesh = any("mesh_shader" in e for e in exts_lower)

            if not vk_exts and not has_rt and not has_mesh and os.path.exists(Filenames.vulkaninfo_output_file):
                try:
                    with open(Filenames.vulkaninfo_output_file, "r") as f:
                        v_content = f.read()
                    blocks = re.split(r'\nGPU\d+:', "\n" + v_content)
                    target_block = None
                    dev_name = vk_dev.get("name") or vk_dev.get("deviceName", "")
                    dev_id = vk_dev.get("device_id") or d_id
                    for b in blocks[1:]:
                        if dev_name and dev_name in b:
                            target_block = b
                            break
                        if dev_id and dev_id in b:
                            target_block = b
                            break
                    if not target_block and blocks[1:]:
                        target_block = blocks[1]
                    if target_block:
                        has_rt = (
                            bool(re.search(r'\b(vk_khr_ray_tracing_pipeline|vk_khr_ray_query|vk_nv_ray_tracing|vk_khr_acceleration_structure)\b', target_block, re.I))
                            or bool(re.search(r'\b(raytracingpipeline|rayquery|accelerationstructure|raytracing|raytracingpositionfetch)\s*=\s*true\b', target_block, re.I))
                        )
                        has_mesh = (
                            bool(re.search(r'\b(vk_ext_mesh_shader|vk_nv_mesh_shader)\b', target_block, re.I))
                            or bool(re.search(r'\b(meshshader|taskshader)\s*=\s*true\b', target_block, re.I))
                        )
                except Exception:
                    pass

            rt_disp = "Supported" if has_rt else "Not Available"
            mesh_disp = "Supported" if has_mesh else "Not Available"

            rows = [
                ("Vulkan API Version", _clean_version(vk_dev.get("api_version") or self.summary_data.get("vulkan", {}).get("instance_version", "—"))),
                ("Instance Version", _clean_version(self.summary_data.get("vulkan", {}).get("instance_version", "—"))),
                ("Driver Name", (vk_dev.get("driver_name") or "—").strip()),
                ("Driver Version", _clean_version(vk_dev.get("driver_version", "—"))),
                ("Driver Info", (vk_dev.get("driver_info") or "—").strip()),
                ("Device Type", _clean_device_type(vk_dev.get("device_type", "—"))),
                ("Conformance Version", (vk_dev.get("conformance_version") or "—").strip()),
                ("Vendor ID", (vk_dev.get("vendor_id") or "—").strip()),
                ("Device ID", (vk_dev.get("device_id") or "—").strip()),
                ("Device Extensions Count", str(vk_dev.get("extensions_count", 0))),
                ("Supported Formats", str(vk_dev.get("formats_count", 0))),
                ("Memory Types", str(vk_dev.get("memory_types_count", 0))),
                ("Memory Heaps", str(vk_dev.get("memory_heaps_count", 0))),
                ("Queue Families", str(vk_dev.get("queue_count", 0))),
                ("Instance Extensions", str(self.summary_data.get("vulkan", {}).get("instance_extensions_count", 0))),
                ("Instance Layers", str(self.summary_data.get("vulkan", {}).get("instance_layers_count", 0))),
                ("Ray Tracing", rt_disp),
                ("Mesh Shaders", mesh_disp),
                ("Pipeline Cache UUID", (vk_dev.get("pipelineCacheUUID") or "—").strip()),
                ("Device UUID", (vk_dev.get("device_uuid") or "—").strip()),
                ("Driver UUID", (vk_dev.get("driver_uuid") or "—").strip()),
            ]
            if vk_dev.get("video_decode_profiles"):
                rows.append(("Video Decode Profiles", "; ".join(vk_dev["video_decode_profiles"])))
            if vk_dev.get("video_encode_profiles"):
                rows.append(("Video Encode Profiles", "; ".join(vk_dev["video_encode_profiles"])))
        elif idx == 1:  # OpenGL
            gl_data = self.summary_data.get("opengl", {})
            rows = [
                ("OpenGL Vendor", gl_data.get("vendor", "—")),
                ("Renderer", gl_data.get("renderer", "—")),
                ("OpenGL Version", gl_data.get("version", "—")),
                ("GLSL Version", gl_data.get("glsl_version", "—")),
                ("Core Profile", gl_data.get("profile", "—")),
                ("Direct Rendering", "Yes" if gl_data.get("direct_rendering") else "No"),
                ("Extensions Count", str(gl_data.get("extensions_count", 0))),
                ("Framebuffer Configs", str(gl_data.get("fbconfigs_count", 0))),
            ]
        elif idx == 2:  # OpenCL
            cl_data = self.summary_data.get("opencl", {})
            platforms = cl_data.get("platforms", [])
            p_name = platforms[0].get("name", "—") if platforms else "—"
            dev_name = platforms[0].get("devices", [{}])[0].get("name", "—") if platforms else "—"
            cus = platforms[0].get("devices", [{}])[0].get("compute_units", "—") if platforms else "—"
            rows = [
                ("OpenCL Platform", p_name),
                ("OpenCL Device", dev_name),
                ("Compute Units", str(cus)),
                ("Platform Count", str(len(platforms))),
            ]
        elif idx == 3:  # Vulkan Video
            vv_data = self.summary_data.get("vulkan_video", {})
            codecs = vv_data.get("codecs", [])
            rows = [
                ("Vulkan Video Supported", "Yes" if vv_data.get("supported") else "No"),
                ("Supported Codecs", ", ".join(codecs) if codecs else "None detected"),
            ]
        elif idx == 4:  # VDPAU
            vdpau_data = self.summary_data.get("vdpau", {})
            rows = [
                ("VDPAU Supported", "Yes" if vdpau_data.get("supported") else "No"),
                ("VDPAU API Version", vdpau_data.get("api_version", "—")),
                ("VDPAU Renderer", vdpau_data.get("renderer", "—")),
            ]
        else:  # System & OS
            sys_data = self.summary_data.get("system", {})
            rows = [
                ("Operating System", sys_data.get("os", "—")),
                ("Kernel Version", sys_data.get("kernel", "—")),
                ("Desktop / Session", sys_data.get("desktop", "—")),
                ("Processor", sys_data.get("processor", "—")),
                ("Architecture", sys_data.get("architecture", "—")),
            ]

        for label, val in rows:
            r = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            r.add_css_class("gpuz-sensor-row")
            r.set_hexpand(True)

            l_w = Gtk.Label(label=label)
            l_w.add_css_class("gpuz-field-label")
            l_w.set_halign(Gtk.Align.START)
            l_w.set_hexpand(True)
            r.append(l_w)

            v_w = Gtk.Label(label=str(val))
            v_w.add_css_class("gpuz-field-value")
            v_w.set_halign(Gtk.Align.END)
            v_w.set_selectable(True)
            r.append(v_w)

            self.adv_content_frame.append(r)

    # -----------------------------------------------------------------------
    # Bottom Bar: Multi-GPU Switcher
    # -----------------------------------------------------------------------

    def _build_bottom_bar(self) -> Gtk.Widget:
        bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        bar.add_css_class("gpuz-bottom-bar")

        lbl = Gtk.Label(label="Select GPU:")
        lbl.add_css_class("gpuz-field-label")
        lbl.set_valign(Gtk.Align.CENTER)
        bar.append(lbl)

        # GPU Dropdown labels
        gpu_labels = []
        for i, g in enumerate(self.gpus):
            name = self._get_gpu_display_name(g)
            gpu_labels.append(f"GPU {i}: {name}")

        if not gpu_labels:
            gpu_labels = ["GPU 0: Default Graphics"]

        str_list = Gtk.StringList.new(gpu_labels)
        self.gpu_dropdown = Gtk.DropDown.new(str_list, None)
        self.gpu_dropdown.set_selected(0)
        self.gpu_dropdown.set_hexpand(True)
        self.gpu_dropdown.connect("notify::selected", self._on_gpu_selected)
        bar.append(self.gpu_dropdown)

        return bar

    def update_summary_data(self, data: dict):
        """Update GPU list and refresh UI when fresh summary data arrives."""
        self.summary_data = data
        self.gpus = self._extract_gpu_list()

        gpu_labels = []
        for i, g in enumerate(self.gpus):
            name = self._get_gpu_display_name(g)
            gpu_labels.append(f"GPU {i}: {name}")

        if not gpu_labels:
            gpu_labels = ["GPU 0: Default Graphics"]

        if hasattr(self, "gpu_dropdown"):
            str_list = Gtk.StringList.new(gpu_labels)
            self.gpu_dropdown.set_model(str_list)
            if self.selected_gpu_idx >= len(self.gpus):
                self.selected_gpu_idx = 0
            self.gpu_dropdown.set_selected(self.selected_gpu_idx)

        self._refresh_graphics_card_content()
        self._refresh_advanced_content()
        self._update_sensors()

    def _on_gpu_selected(self, dropdown, _pspec):
        idx = dropdown.get_selected()
        if 0 <= idx < len(self.gpus):
            self.selected_gpu_idx = idx
            self._refresh_graphics_card_content()
            self._refresh_advanced_content()
            self._update_sensors()

    # -----------------------------------------------------------------------
    # Sensor Polling Loop
    # -----------------------------------------------------------------------

    def _start_sensor_polling(self):
        def _poll():
            if not self.get_mapped():
                return True
            self._update_sensors()
            return True

        interval = 1000
        if hasattr(self.app, "_current_refresh_interval_ms"):
            interval = self.app._current_refresh_interval_ms
        self.sensor_timer_id = GLib.timeout_add(interval, _poll)

    def _on_destroy(self, _widget):
        if self.sensor_timer_id:
            GLib.source_remove(self.sensor_timer_id)
            self.sensor_timer_id = 0
