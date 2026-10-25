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
from GpuDatabase import lookup_gpu_specs, calculate_bandwidth


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
    padding: 8px;
    margin-bottom: 8px;
}

.gpuz-header-title {
    font-size: 13pt;
    font-weight: 700;
}

.gpuz-field-label {
    font-size: 9pt;
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
    padding: 2px 6px;
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
        if not vendor_id and not device_id:
            return None
        vk_devices = self.summary_data.get("vulkan", {}).get("devices", [])
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

        self.card_content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.card_content_box.set_margin_start(10)
        self.card_content_box.set_margin_end(10)
        self.card_content_box.set_margin_top(8)
        self.card_content_box.set_margin_bottom(12)

        self._refresh_graphics_card_content()
        scroll.set_child(self.card_content_box)
        return scroll

    def _refresh_graphics_card_content(self):
        """Regenerate the Graphics Card spec sheet for the selected GPU."""
        # Clear previous children
        child = self.card_content_box.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self.card_content_box.remove(child)
            child = nxt

        gpu = self._get_current_gpu()
        gpu_name = self._get_gpu_display_name(gpu)
        v_id = gpu.get("vendor_id", "")
        d_id = gpu.get("device_id", "")
        vk_dev = self._get_vulkan_device(v_id, d_id) or {}
        stats = gpu.get("stats", {}) or get_gpu_stats_for_index(gpu.get("card_index", 0)) or {}

        # Look up physical specifications database
        specs = lookup_gpu_specs(v_id, d_id, gpu_name)

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

        # ── Specifications Grid ────────────────────────────────────────
        grid_frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        grid_frame.add_css_class("gpuz-card-frame")

        # Prepare field values
        chip_val = specs.get("chip", "—")
        rev_val = gpu.get("revision", "—")
        node_val = specs.get("node", "—")
        die_val = specs.get("die_size", "—")
        trans_val = specs.get("transistors", "—")
        rel_val = specs.get("release", "—")
        bios_val = gpu.get("vbios") or "—"
        
        dev_id_display = f"{v_id.upper()} {d_id.upper()}" if v_id or d_id else "—"
        sub_vendor_display = gpu.get("subsystem_vendor", "—")
        if gpu.get("subsystem_device"):
            sub_vendor_display += f" ({gpu['subsystem_device']})"
        
        rops_val = stats.get("rop_count") or specs.get("rops_tmus", "—")
        shaders_val = specs.get("shaders") or (f"{stats.get('compute_units')} CUs" if stats.get("compute_units") else "—")
        bus_interface = f"{gpu.get('pcie_link_width', 'PCIe')} @ {gpu.get('pcie_link_speed', '—')}"

        vram_tot = stats.get("mem_total", 0)
        vram_size_display = f"{vram_tot} MB" if vram_tot > 0 else "—"
        vram_type = stats.get("vram_type") or gpu.get("vram_type") or "GDDR"
        vram_vendor = gpu.get("vram_vendor", "—")
        bus_width = specs.get("bus_width", "—")
        
        mem_clk = stats.get("vram_clock_max") or stats.get("vram_clock", 0)
        bw_val = calculate_bandwidth(mem_clk, int(bus_width.split()[0])) if (bus_width and bus_width[0].isdigit()) else "—"

        driver_val = gpu.get("driver") or vk_dev.get("driver_name") or "—"
        if vk_dev.get("driver_version"):
            driver_val += f" {vk_dev['driver_version']}"
            
        core_clk = f"{stats.get('clock_current', 0)} MHz" if stats.get('clock_current', 0) > 0 else "—"
        boost_clk = f"{stats.get('clock_max', 0)} MHz" if stats.get('clock_max', 0) > 0 else "—"
        mem_clk_disp = f"{mem_clk} MHz" if mem_clk > 0 else "—"

        # Check Resizable BAR from heap properties or PCIe
        rebar_val = "Enabled" if any("DEVICE_LOCAL" in h and "HOST_VISIBLE" in h for h in vk_dev.get("heaps", [])) else "Supported"

        # Add 2-column key-value rows
        def _add_dual_row(l1, v1, l2, v2):
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            row_box.set_hexpand(True)

            # Left Cell
            c1 = self._make_field_cell(l1, v1)
            row_box.append(c1)

            # Right Cell
            c2 = self._make_field_cell(l2, v2)
            row_box.append(c2)

            grid_frame.append(row_box)

        _add_dual_row("GPU Code", chip_val, "Revision", rev_val)
        _add_dual_row("Technology", node_val, "Die Size", die_val)
        _add_dual_row("Transistors", trans_val, "Release Date", rel_val)
        _add_dual_row("BIOS Version", bios_val, "UEFI Support", "Supported")
        _add_dual_row("Device ID", dev_id_display, "Subvendor", sub_vendor_display)
        _add_dual_row("ROPs / TMUs", str(rops_val), "Shaders / CUs", str(shaders_val))
        _add_dual_row("DirectX API", specs.get("directx", "12.0"), "Bus Interface", bus_interface)
        _add_dual_row("Memory Type", vram_type, "Bus Width", str(bus_width))
        _add_dual_row("Memory Size", vram_size_display, "Bandwidth", bw_val)
        _add_dual_row("Memory Vendor", vram_vendor, "Driver Version", driver_val)
        _add_dual_row("GPU Clock", core_clk, "Boost Clock", boost_clk)
        _add_dual_row("Memory Clock", mem_clk_disp, "Resizable BAR", rebar_val)

        self.card_content_box.append(grid_frame)

        # ── Computing Capabilities Checkboxes ──────────────────────────
        tech_frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        tech_frame.add_css_class("gpuz-card-frame")

        tech_title = Gtk.Label(label="Computing Technologies")
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

        # Determine capabilities
        has_vulkan = self.results.get("vulkan", False)
        has_opengl = self.results.get("opengl", False)
        has_opencl = self.results.get("opencl", False)
        has_vulkan_video = self.results.get("vulkan_video", False)
        has_vdpau = self.results.get("vdpau", False)
        has_raytracing = any("ray_tracing" in ext.lower() or "ray_query" in ext.lower()
                             for ext in vk_dev.get("extensions", []))

        techs = [
            ("OpenCL", has_opencl),
            ("Vulkan", has_vulkan),
            ("OpenGL", has_opengl),
            ("Ray Tracing", has_raytracing),
            ("Vulkan Video", has_vulkan_video),
            ("VDPAU", has_vdpau),
            ("EGL", True),
            ("Direct Rendering", True),
        ]

        for name, supported in techs:
            b = self._make_tech_badge(name, supported)
            tech_flow.append(b)

        tech_frame.append(tech_flow)
        self.card_content_box.append(tech_frame)

    def _make_field_cell(self, label: str, value: str) -> Gtk.Box:
        """Create a compact GPU-Z field with label and read-only value."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        box.add_css_class("gpuz-field-box")
        box.set_hexpand(True)

        lbl = Gtk.Label(label=label)
        lbl.add_css_class("gpuz-field-label")
        lbl.set_halign(Gtk.Align.START)
        box.append(lbl)

        val = Gtk.Label(label=str(value))
        val.add_css_class("gpuz-field-value")
        val.set_halign(Gtk.Align.START)
        val.set_selectable(True)
        val.set_ellipsize(Pango.EllipsizeMode.END)
        box.append(val)
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
            rows = [
                ("Vulkan API Version", vk_dev.get("api_version") or self.summary_data.get("vulkan", {}).get("instance_version", "—")),
                ("Driver Version", vk_dev.get("driver_version", "—")),
                ("Conformance Version", vk_dev.get("conformance_version", "—")),
                ("Device Type", vk_dev.get("device_type", "—")),
                ("Extensions Count", str(vk_dev.get("extensions_count", 0))),
                ("Supported Formats", str(vk_dev.get("formats_count", 0))),
                ("Memory Types", str(vk_dev.get("memory_types_count", 0))),
                ("Memory Heaps", str(vk_dev.get("memory_heaps_count", 0))),
                ("Queue Families", str(vk_dev.get("queue_count", 0))),
                ("Device UUID", vk_dev.get("device_uuid", "—")),
            ]
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
