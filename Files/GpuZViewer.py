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
  - System Tab: Machine & OS system information inspector (CPU, RAM, OS, BIOS).
  - Bottom Bar: Multi-GPU switcher dropdown.
"""

import os
import re
import glob
import threading
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib, GdkPixbuf, Pango, Gdk, Gio

import const
import Filenames
from Common import get_gpu_stats_for_index
from SummaryViewer import (
    _make_gauge_dashboard,
    _update_gauge_dict,
    get_realtime_cpu_usage,
    get_realtime_cpu_temp,
    get_realtime_ram_usage,
    get_realtime_swap_usage,
    get_realtime_net_speed,
)



# ---------------------------------------------------------------------------
# GPU-Z CSS Styling
# ---------------------------------------------------------------------------

def get_gpuz_css(is_dark: bool = True) -> str:
    """Return GPU-Z CSS tailored to match the application dashboard theme."""
    if is_dark:
        return """
.gpuz-container {
    background-color: #222222;
    color: #ffffff;
    padding: 6px;
}

.gpuz-container > stack,
.gpuz-container scrolledwindow,
.gpuz-container viewport,
.gpuz-card-page,
.gpuz-system-page {
    background-color: #222222;
}

.gpuz-container headerbar {
    background-image: linear-gradient(
        to bottom,
        #181818,
        #111111
    );
    background-color: #181818;
    color: #ffffff;
}

.gpuz-header-frame {
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    background-image: linear-gradient(
        to bottom,
        #181818,
        #111111
    );
    background-color: #181818;
    padding: 6px 10px;
    margin-bottom: 4px;
}

.gpuz-header-title {
    font-size: 13pt;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.1px;
}

.gpuz-section-box {
    margin-top: 3px;
    margin-bottom: 3px;
    padding: 0 0 5px 0;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    background-color: #262626;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
}

.gpuz-section-header {
    background-image: linear-gradient(
        to bottom,
        #181818,
        #111111
    );
    background-color: #181818;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
    padding: 6px 10px;
    margin: 0;
}

.gpuz-section-header image {
    color: #ffffff;
}

.gpuz-section-title {
    font-size: 8.5pt;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}

.gpuz-section-sep {
    background-color: #333333;
    opacity: 0.6;
    margin: 0 0 3px 0;
    min-height: 1px;
}

.gpuz-section-header .gpuz-nav-btn {
    background-color: #1a1a1a;
    border: 1px solid #d43c50;
    color: #d43c50;
    border-radius: 6px;
    font-weight: 600;
    padding: 3px 10px;
}

.gpuz-section-header .gpuz-nav-btn:hover {
    background-color: #d43c50;
    color: #ffffff;
}

.gpuz-section-box > flowbox,
.gpuz-section-box > box:not(.gpuz-section-header) {
    margin-left: 6px;
    margin-right: 6px;
}

/* Classic GTK Frame for each field */
.gpuz-field-frame {
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 5px;
    background-color: #1a1a1a;
    margin: 1px 0;
    transition: 150ms ease-in-out;
}

.gpuz-field-frame:hover {
    border-color: rgba(255, 255, 255, 0.35);
    background-color: #222222;
}

.gpuz-frame-label {
    font-size: 7.5pt;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.70);
    padding: 0 3px;
    margin-left: 4px;
}

.gpuz-frame-content {
    padding: 1px 6px 3px 6px;
    min-height: 20px;
}

.gpuz-frame-value {
    font-size: 9pt;
    font-weight: 600;
    color: #ffffff;
}

.gpuz-field-box {
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 4px;
    padding: 2px 6px;
    min-height: 20px;
    background-color: #1a1a1a;
}

.gpuz-api-checkbox {
    border: 0;
    border-radius: 4px;
    padding: 2px 5px;
    font-size: 8.5pt;
    font-weight: 600;
    background-color: transparent;
    opacity: 1;
    min-height: 22px;
}

.gpuz-api-supported {
    color: #2ec27e;
}

.gpuz-api-supported check {
    color: white;
    background-color: #2ec27e;
    border-color: #25a969;
    -gtk-icon-size: 13px;
    min-width: 14px;
    min-height: 14px;
}

.gpuz-api-unsupported {
    color: #e01b24;
}

.gpuz-api-unsupported check {
    color: #e01b24;
    background-color: #281818;
    border-color: #e01b24;
    -gtk-icon-size: 13px;
    min-width: 14px;
    min-height: 14px;
}

.gpuz-bottom-bar {
    border-top: 1px solid rgba(255, 255, 255, 0.12);
    padding: 5px 10px;
    background-color: #181818;
    box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.3);
}

.gpuz-card-page .gpuz-header-title,
.gpuz-system-page .gpuz-header-title {
    font-size: 14pt;
}

.gpuz-card-page .gpuz-section-title,
.gpuz-system-page .gpuz-section-title {
    font-size: 9pt;
}

.gpuz-card-page .gpuz-frame-label,
.gpuz-system-page .gpuz-frame-label {
    font-size: 8.5pt;
}

.gpuz-card-page .gpuz-frame-value,
.gpuz-system-page .gpuz-frame-value {
    font-size: 10.5pt;
}

.gpuz-card-page .gpuz-frame-content,
.gpuz-system-page .gpuz-frame-content {
    min-height: 24px;
    padding: 3px 7px 4px;
}

.gpuz-card-page .gpuz-api-checkbox,
.gpuz-system-page .gpuz-api-checkbox {
    font-size: 9.5pt;
    min-height: 25px;
}
"""
    else:
        return """
.gpuz-container {
    background-color: #eaedf1;
    color: #0f172a;
    padding: 6px;
}

.gpuz-container headerbar {
    background-image: linear-gradient(
        to bottom,
        #1e2430,
        #161b24
    );
    background-color: #1e2430;
    color: #f8fafc;
}

.gpuz-header-frame {
    border: 1px solid rgba(15, 23, 42, 0.12);
    border-radius: 8px;
    background-image: linear-gradient(
        to bottom,
        #1e2430,
        #161b24
    );
    background-color: #1e2430;
    padding: 8px 12px;
    margin-bottom: 4px;
}

.gpuz-header-title {
    font-size: 13pt;
    font-weight: 700;
    color: #f8fafc;
    letter-spacing: 0.1px;
}

.gpuz-header-frame .dim-label {
    color: rgba(255, 255, 255, 0.75);
}

.gpuz-section-box {
    margin-top: 3px;
    margin-bottom: 3px;
    padding: 0 0 5px 0;
    border: 1px solid rgba(15, 23, 42, 0.12);
    border-radius: 8px;
    background-color: #f8fafc;
    box-shadow: 0 3px 10px rgba(15, 23, 42, 0.06);
}

.gpuz-section-header {
    background-image: linear-gradient(
        to bottom,
        #1e2430,
        #161b24
    );
    background-color: #1e2430;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
    padding: 6px 10px;
    margin: 0;
}

.gpuz-section-header image {
    color: #f8fafc;
}

.gpuz-section-title {
    font-size: 8.5pt;
    font-weight: 800;
    color: #f8fafc;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}

.gpuz-section-sep {
    background-color: rgba(0, 0, 0, 0.08);
    opacity: 0.5;
    margin: 0 0 3px 0;
    min-height: 1px;
}

.gpuz-section-header .gpuz-nav-btn {
    background-color: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.25);
    color: #ffffff;
    border-radius: 6px;
    font-weight: 600;
    padding: 3px 10px;
}

.gpuz-section-header .gpuz-nav-btn:hover {
    background-color: #d43c50;
    border-color: #d43c50;
    color: #ffffff;
}

.gpuz-section-box > flowbox,
.gpuz-section-box > box:not(.gpuz-section-header) {
    margin-left: 6px;
    margin-right: 6px;
}

/* Classic GTK Frame for each field */
.gpuz-field-frame {
    border: 1px solid rgba(15, 23, 42, 0.10);
    border-radius: 5px;
    background-color: #ffffff;
    margin: 1px 0;
    transition: 150ms ease-in-out;
}

.gpuz-field-frame:hover {
    border-color: rgba(15, 23, 42, 0.25);
    background-color: #f1f5f9;
}

.gpuz-frame-label {
    font-size: 7.5pt;
    font-weight: 700;
    color: #475569;
    padding: 0 3px;
    margin-left: 4px;
}

.gpuz-frame-content {
    padding: 1px 6px 3px 6px;
    min-height: 20px;
}

.gpuz-frame-value {
    font-size: 9pt;
    font-weight: 600;
    color: #0f172a;
}

.gpuz-field-box {
    border: 1px solid rgba(15, 23, 42, 0.10);
    border-radius: 4px;
    padding: 2px 6px;
    min-height: 20px;
    background-color: #ffffff;
}

.gpuz-api-checkbox {
    border: 0;
    border-radius: 4px;
    padding: 2px 5px;
    font-size: 8.5pt;
    font-weight: 600;
    background-color: transparent;
    opacity: 1;
    min-height: 22px;
}

.gpuz-api-supported {
    color: #16a34a;
}

.gpuz-api-supported check {
    color: white;
    background-color: #16a34a;
    border-color: #15803d;
    -gtk-icon-size: 13px;
    min-width: 14px;
    min-height: 14px;
}

.gpuz-api-unsupported {
    color: #dc2626;
}

.gpuz-api-unsupported check {
    color: #dc2626;
    background-color: #ffffff;
    border-color: #dc2626;
    -gtk-icon-size: 13px;
    min-width: 14px;
    min-height: 14px;
}

.gpuz-bottom-bar {
    border-top: 1px solid rgba(0, 0, 0, 0.10);
    padding: 5px 10px;
    background-color: #e2e8f0;
    box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.06);
}

.gpuz-card-page .gpuz-header-title,
.gpuz-system-page .gpuz-header-title {
    font-size: 14pt;
}

.gpuz-card-page .gpuz-section-title,
.gpuz-system-page .gpuz-section-title {
    font-size: 9pt;
}

.gpuz-card-page .gpuz-frame-label,
.gpuz-system-page .gpuz-frame-label {
    font-size: 8.5pt;
}

.gpuz-card-page .gpuz-frame-value,
.gpuz-system-page .gpuz-frame-value {
    font-size: 10.5pt;
}

.gpuz-card-page .gpuz-frame-content,
.gpuz-system-page .gpuz-frame-content {
    min-height: 24px;
    padding: 3px 7px 4px;
}

.gpuz-card-page .gpuz-api-checkbox,
.gpuz-system-page .gpuz-api-checkbox {
    font-size: 9.5pt;
    min-height: 25px;
}
"""


GPUZ_CSS = get_gpuz_css(True)


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
        self._css_provider = None
        self.theme_btn = None
        self.repository_btn = None
        self._refresh_interval_dropdown = None
        self._syncing_refresh_interval = False
        self.add_css_class("gpuz-container")

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

        # Theme and repository controls on the right
        self.repository_btn = Gtk.Button()
        self.repository_btn.add_css_class("flat")
        self.repository_btn.set_tooltip_text("Open GPU-Viewer GitHub repository")
        self.repository_btn.connect("clicked", self._open_repository)
        self.header_bar.pack_end(self.repository_btn)

        if hasattr(self.app, "_on_theme_button_clicked"):
            self.theme_btn = Gtk.Button()
            self.theme_btn.add_css_class("flat")
            self.theme_btn.connect("clicked", self._on_theme_btn_clicked)
            self.header_bar.pack_end(self.theme_btn)

        self.append(self.header_bar)

        # Apply initial theme matching dashboard
        self.apply_theme()

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

        # Build Tab 3: System Information (replaces legacy Advanced tab)
        self.system_page = self._build_system_tab()
        self.view_stack.add_titled_with_icon(
            self.system_page, "system", "System", "computer-symbolic"
        )

        self.append(self.view_stack)

        # Bottom Bar: Multi-GPU selector
        self.bottom_bar = self._build_bottom_bar()
        self.append(self.bottom_bar)
        self.view_stack.connect("notify::visible-child-name", self._on_view_changed)
        self._update_gpu_selector_visibility()

        # Connect cleanup on destroy
        self.connect("destroy", self._on_destroy)

        # Start sensor polling
        self._start_sensor_polling()

    def _on_theme_btn_clicked(self, button):
        if hasattr(self.app, "_on_theme_button_clicked"):
            self.app._on_theme_button_clicked(button)

    def apply_theme(self, is_dark: bool = None):
        """Synchronize GPU-Z styling and theme toggle with the application theme preference."""
        if is_dark is None:
            is_dark = self.app.config.get_theme_preference() if (self.app and hasattr(self.app, 'config')) else True
        self.is_dark = is_dark
        if hasattr(self, 'theme_btn') and self.theme_btn:
            self.theme_btn.set_icon_name("display-brightness-symbolic" if is_dark else "weather-clear-night-symbolic")
            self.theme_btn.set_tooltip_text("Switch to Light Theme" if is_dark else "Switch to Dark Theme")
            self.theme_btn.set_sensitive(True)
        if self.repository_btn is not None:
            logo_path = self._resolve_image_path("github.png")
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(logo_path, 16, 16, True)
            logo = Gtk.Picture.new_for_pixbuf(pixbuf)
            logo.set_size_request(16, 16)
            self.repository_btn.set_child(logo)

        css_data = get_gpuz_css(is_dark)
        display = Gdk.Display.get_default()
        if hasattr(self, '_css_provider') and self._css_provider and display:
            try:
                Gtk.StyleContext.remove_provider_for_display(display, self._css_provider)
            except Exception:
                pass
        self._css_provider = Gtk.CssProvider()
        self._css_provider.load_from_data(css_data.encode("utf-8"))
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display,
                self._css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_USER,
            )

    def _open_repository(self, _button):
        if not Gio.AppInfo.launch_default_for_uri(const.GITHUB_LINK, None):
            print(f"Could not open GPU-Viewer repository: {const.GITHUB_LINK}")

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

    def _get_all_opencl_devices_for_gpu(self, gpu: dict) -> list[tuple[dict, dict]]:
        """
        Find and return ALL matching (platform, device) tuples for the specified GPU dict.
        Matches based on PCIe topology, Vendor ID, Device ID, device name, and device type.
        Returns a list of (platform, device) tuples sorted by match score descending.
        """
        cl_data = self.summary_data.get("opencl", {})
        platforms = cl_data.get("platforms", [])
        if not platforms or not gpu:
            return []

        candidates = []
        for plat in platforms:
            for dev in plat.get("devices", []):
                candidates.append((plat, dev))

        if not candidates:
            return []

        v_id = gpu.get("vendor_id", "")
        d_id = gpu.get("device_id", "")

        def parse_hex_id(value):
            try:
                return int(value, 16) if value else None
            except ValueError:
                return None

        def normalize_pci_address(value):
            match = re.search(
                r'(?:(?P<domain>[0-9a-f]{4}):)?(?P<bus>[0-9a-f]{2}):'
                r'(?P<device>[0-9a-f]{2})\.(?P<function>[0-7])',
                str(value or ""),
                re.IGNORECASE,
            )
            if not match:
                return None
            return (
                match.group("domain").lower() if match.group("domain") else None,
                f'{match.group("bus").lower()}:{match.group("device").lower()}.{match.group("function")}',
            )

        def pci_addresses_match(first, second):
            return bool(
                first
                and second
                and first[1] == second[1]
                and (first[0] is None or second[0] is None or first[0] == second[0])
            )

        gpu_pci = normalize_pci_address(gpu.get("pci_address"))
        gpu_name = self._get_gpu_display_name(gpu).lower()

        gpu_v_int = parse_hex_id(v_id)
        gpu_d_int = parse_hex_id(d_id)

        # Filter candidates of the same vendor to rank relative index
        same_vendor_candidates_by_platform = {}
        for plat, dev in candidates:
            dev_v = dev.get("vendor_id", "")
            dev_v_int = parse_hex_id(dev_v)
            dev_d_int = parse_hex_id(dev.get("device_id", ""))
            dev_type = (dev.get("device_type") or "").upper()
            if not ("GPU" in dev_type or "ACCELERATOR" in dev_type):
                continue
            if gpu_v_int is not None and dev_v_int is not None and gpu_v_int != dev_v_int:
                continue
            if gpu_d_int is not None and dev_d_int is not None and gpu_d_int != dev_d_int:
                continue

            same_vendor = bool(gpu_v_int is not None and dev_v_int is not None and gpu_v_int == dev_v_int)
            if not same_vendor and gpu_v_int == 0x1002:
                d_vend = (dev.get("vendor") or "").lower()
                p_name = (plat.get("name") or "").lower()
                same_vendor = any(w in d_vend or w in p_name for w in ("amd", "advanced micro", "radeon", "rusticl"))
            elif not same_vendor and gpu_v_int == 0x10de:
                d_vend = (dev.get("vendor") or "").lower()
                p_name = (plat.get("name") or "").lower()
                same_vendor = any(w in d_vend or w in p_name for w in ("nvidia", "cuda"))
            elif not same_vendor and gpu_v_int == 0x8086:
                d_vend = (dev.get("vendor") or "").lower()
                p_name = (plat.get("name") or "").lower()
                same_vendor = "intel" in d_vend or "intel" in p_name

            if same_vendor:
                same_vendor_candidates_by_platform.setdefault(id(plat), []).append((plat, dev))

        # Use device ID too, so identical-model GPUs can be mapped independently.
        same_vendor_gpus = [gpu]
        if gpu_v_int is not None:
            same_vendor_gpus = []
            for g in self.gpus:
                peer_v_int = parse_hex_id(g.get("vendor_id", ""))
                peer_d_int = parse_hex_id(g.get("device_id", ""))
                if peer_v_int != gpu_v_int:
                    continue
                if gpu_d_int is not None and peer_d_int is not None and peer_d_int != gpu_d_int:
                    continue
                same_vendor_gpus.append(g)
        relative_gpu_idx = next(
            (i for i, peer in enumerate(same_vendor_gpus) if peer is gpu),
            0,
        )

        scored_candidates = []

        for plat, dev in candidates:
            dev_v_int = parse_hex_id(dev.get("vendor_id", ""))
            dev_d_int = parse_hex_id(dev.get("device_id", ""))
            if gpu_v_int is not None and dev_v_int is not None and gpu_v_int != dev_v_int:
                continue
            if gpu_d_int is not None and dev_d_int is not None and gpu_d_int != dev_d_int:
                continue

            dev_pci = normalize_pci_address(dev.get("pci_address"))
            pci_match = pci_addresses_match(gpu_pci, dev_pci)
            if gpu_pci and dev_pci and not pci_match:
                continue

            platform_candidates = same_vendor_candidates_by_platform.get(id(plat), [])
            candidate_index = next(
                (i for i, candidate in enumerate(platform_candidates) if candidate[1] is dev),
                None,
            )
            if len(same_vendor_gpus) > 1 and not pci_match:
                if len(platform_candidates) != len(same_vendor_gpus):
                    continue
                if candidate_index != relative_gpu_idx:
                    continue

            score = 0
            dev_type = (dev.get("device_type") or "").upper()
            is_gpu = "GPU" in dev_type or "ACCELERATOR" in dev_type
            if is_gpu:
                score += 50
            else:
                score -= 30

            # 1. PCIe topology / bus address
            if pci_match:
                score += 300

            # 2. Vendor ID / Name
            dev_v = dev.get("vendor_id", "")

            if gpu_v_int is not None and dev_v_int is not None:
                if gpu_v_int == dev_v_int:
                    score += 120
            else:
                d_vend = (dev.get("vendor") or "").lower()
                p_name = (plat.get("name") or "").lower()
                d_name = (dev.get("name") or "").lower()
                if gpu_v_int == 0x1002:
                    if any(w in d_vend or w in p_name or w in d_name for w in ["amd", "advanced micro", "radeon", "rusticl"]):
                        score += 60
                    elif any(w in d_vend or w in p_name for w in ["nvidia", "intel"]):
                        score -= 200
                elif gpu_v_int == 0x10de:
                    if any(w in d_vend or w in p_name or w in d_name for w in ["nvidia", "cuda", "geforce", "quadro"]):
                        score += 60
                    elif any(w in d_vend or w in p_name for w in ["amd", "intel"]):
                        score -= 200
                elif gpu_v_int == 0x8086:
                    if any(w in d_vend or w in p_name or w in d_name for w in ["intel", "arc", "iris", "xe"]):
                        score += 60
                    elif any(w in d_vend or w in p_name for w in ["amd", "nvidia"]):
                        score -= 200

            # 3. Device ID
            if gpu_d_int is not None and dev_d_int is not None:
                if gpu_d_int == dev_d_int:
                    score += 150

            # 4. Name substrings
            d_name = (dev.get("name") or "").lower()
            board = (dev.get("board_name") or "").lower()
            for token in re.findall(r'[A-Za-z0-9]+', gpu_name):
                if len(token) >= 3 and token not in ("gpu", "card", "graphics", "device"):
                    if token in d_name or token in board:
                        score += 25

            # 5. Relative index match among same vendor
            if candidate_index == relative_gpu_idx:
                score += 40

            if score > 0:
                scored_candidates.append((score, (plat, dev)))

        if scored_candidates:
            scored_candidates.sort(key=lambda x: x[0], reverse=True)
            return [cand for _, cand in scored_candidates]

        if len(self.gpus) == 1 and len(candidates) == 1:
            dev_type = (candidates[0][1].get("device_type") or "").upper()
            if "GPU" in dev_type or "ACCELERATOR" in dev_type:
                return [candidates[0]]

        return []

    def _get_opencl_device_for_gpu(self, gpu: dict) -> tuple[dict | None, dict | None]:
        """Find and return the best matching (platform, device) tuple for the GPU."""
        all_devs = self._get_all_opencl_devices_for_gpu(gpu)
        if all_devs:
            return all_devs[0]
        return None, None

        return None, None

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

    def _resolve_image_path(self, filename: str) -> str:
        """Resolve an image filename safely across development and installed environments."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidate = os.path.join(base_dir, "Images", filename)
        if os.path.exists(candidate):
            return candidate
        for prefix in ("../Images", "Images"):
            p = os.path.join(prefix, filename)
            if os.path.exists(p):
                return p
        return os.path.join(base_dir, "Images", filename)

    def _load_header_logo_pixbuf(self, path: str) -> GdkPixbuf.Pixbuf:
        return GdkPixbuf.Pixbuf.new_from_file_at_scale(path, 38, 38, True)

    def _get_vendor_logo_path(self, vendor_id_str: str) -> str:
        """Return the selected GPU vendor's logo image path."""
        try:
            vendor_id = int(vendor_id_str, 16)
        except (TypeError, ValueError):
            vendor_id = None

        if vendor_id == 0x1002:
            return self._resolve_image_path("AMD_D.png")
        if vendor_id == 0x10de:
            return self._resolve_image_path("nvidia_logo.png")
        if vendor_id == 0x8086:
            return self._resolve_image_path("intel-logo.png")
        return self._resolve_image_path("about-us.png")

    def _get_distro_logo_path(self, os_str: str) -> str:
        """Return the official Linux distribution logo image path based on OS name."""
        query = (os_str or "").lower()
        if not query or query == "—":
            if os.path.exists("/etc/os-release"):
                try:
                    with open("/etc/os-release", "r") as f:
                        query = f.read().lower()
                except Exception:
                    pass

        mapping = [
            ("cachy", "CachyOS_Logo.png"),
            ("nobara", "nobara.png"),
            ("endeavour", "endeavouros-icon.png"),
            ("reborn", "RebornOS_Icon.png"),
            ("rhino", "Rhino_Linux.png"),
            ("solus", "Solus.svg"),
            ("nixos", "NixOS.png"),
            ("steam", "Steam_icon_logo.png"),
            ("anduin", "anduinos_logo.svg"),
            ("kubuntu", "Kubuntu_logo.png"),
            ("lubuntu", "Lubuntu_logo.svg"),
            ("xubuntu", "xubuntu.png"),
            ("budgie", "Ubuntu_Budgie.png"),
            ("studio", "Ubuntu_Studio.png"),
            ("pop", "pop_os.png"),
            ("mint", "linux_mint.png"),
            ("manjaro", "Manjaro-log.png"),
            ("fedora", "Fedora_icon.png"),
            ("arch", "arch.png"),
            ("debian", "debian.png"),
            ("ubuntu", "Ubuntu.png"),
            ("suse", "open_suse.png"),
            ("opensuse", "open_suse.png"),
            ("elementary", "elementaryOS.png"),
            ("zorin", "Zorin_Logo.svg"),
            ("mx", "MX_Linux_logo.svg"),
            ("lite", "Linux-Lite-Logo.png"),
            ("mandriva", "Mandriva.png"),
        ]
        for key, img_name in mapping:
            if key in query:
                return self._resolve_image_path(img_name)

        return self._resolve_image_path("about-us.png")

    # -----------------------------------------------------------------------
    # Tab 1: Graphics Card Specification Sheet
    # -----------------------------------------------------------------------

    def _build_graphics_card_tab(self) -> Gtk.Widget:
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        self.card_scroll = scroll

        self.card_content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.card_content_box.add_css_class("gpuz-card-page")
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
        VDPAU and GPU hardware stats.
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
        vdpau_data = self.summary_data.get("vdpau",       {})

        # ── Pre-compute API Capabilities & Devices ──────────────────────
        # OpenCL matching
        matched_devices = self._get_all_opencl_devices_for_gpu(gpu)
        has_gpu_opencl = bool(matched_devices)

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
        has_vulkan_video = bool(
            vk_dev.get("video_decode_profiles") or vk_dev.get("video_encode_profiles")
        )

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

        has_vulkan       = bool(vk_dev) or vk_data.get("supported", False)
        has_opengl       = bool(gl_data.get("version"))
        has_egl          = bool(gl_data.get("egl_version")) or gl_data.get("egl_count", 0) > 0
        has_opencl       = has_gpu_opencl
        has_vdpau        = vdpau_data.get("supported", False)
        has_raytracing   = bool(has_rt)
        has_mesh_shaders = bool(has_mesh)

        # ── Header Box: Logo + Name ────────────────────────────────────
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.add_css_class("gpuz-header-frame")

        logo_path = self._get_vendor_logo_path(v_id)
        try:
            pixbuf = self._load_header_logo_pixbuf(logo_path)
            logo_img = Gtk.Picture.new_for_pixbuf(pixbuf)
            logo_img.set_size_request(38, 38)
            header_box.append(logo_img)
        except Exception:
            pass

        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        title_box.set_valign(Gtk.Align.CENTER)
        name_lbl = Gtk.Label(label=gpu_name)
        name_lbl.add_css_class("gpuz-header-title")
        name_lbl.set_halign(Gtk.Align.START)
        name_lbl.set_wrap(True)
        name_lbl.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        if hasattr(Gtk, "NaturalWrapMode") and hasattr(name_lbl, "set_natural_wrap_mode"):
            name_lbl.set_natural_wrap_mode(Gtk.NaturalWrapMode.NONE)
        title_box.append(name_lbl)

        sub_text = f"Card: {gpu.get('card_name', 'card0')} • PCI: {gpu.get('pci_address', '—')}"
        sub_lbl = Gtk.Label(label=sub_text)
        sub_lbl.add_css_class("dim-label")
        sub_lbl.set_halign(Gtk.Align.START)
        title_box.append(sub_lbl)

        header_box.append(title_box)
        self.card_content_box.append(header_box)

        # Helper: build a row of 1–5 fields.
        # Each item is (label, value) or (label, value, live_key).
        def _add_row(parent, *items):
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            row_box.set_hexpand(True)
            row_box.set_margin_start(6)
            row_box.set_margin_end(6)
            for item in items:
                lbl_text = item[0]
                val_text = item[1]
                lk = item[2] if len(item) > 2 else None
                row_box.append(self._make_field_frame(lbl_text, val_text, live_key=lk))
            parent.append(row_box)

        # Helper: section header with optional icon
        def _open_detail_page(page_name: str):
            app = self.app
            if hasattr(app, "set_view_mode"):
                app.set_view_mode("dashboard")
            if hasattr(app, "open_tab"):
                app.open_tab(page_name, gpu_index=gpu.get("card_index", 0))

        def _make_section(title, icon_name=None, fallback_icon_name=None,
                          nav_actions=()) -> Gtk.Box:
            sect_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            sect_box.add_css_class("gpuz-section-box")

            hdr_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            hdr_box.add_css_class("gpuz-section-header")

            if icon_name:
                if icon_name.endswith((".png", ".svg")):
                    try:
                        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_name, 18, 18, True)
                        icon = Gtk.Picture.new_for_pixbuf(pixbuf)
                        icon.set_size_request(18, 18)
                    except GLib.Error:
                        icon = Gtk.Image.new_from_icon_name(
                            fallback_icon_name or "application-x-executable-symbolic"
                        )
                        icon.set_pixel_size(18)
                else:
                    icon = Gtk.Image.new_from_icon_name(icon_name)
                    icon.set_pixel_size(14)
                hdr_box.append(icon)

            hdr = Gtk.Label(label=title)
            hdr.add_css_class("gpuz-section-title")
            hdr.set_halign(Gtk.Align.START)
            hdr.set_hexpand(True)
            hdr_box.append(hdr)
            for nav_label, page_name in nav_actions:
                nav_btn = Gtk.Button(label=nav_label)
                nav_btn.add_css_class("flat")
                nav_btn.add_css_class("gpuz-nav-btn")
                nav_btn.set_valign(Gtk.Align.CENTER)
                nav_btn.connect(
                    "clicked",
                    lambda _button, page=page_name: _open_detail_page(page),
                )
                hdr_box.append(nav_btn)
            sect_box.append(hdr_box)

            sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            sep.add_css_class("gpuz-section-sep")
            sect_box.append(sep)

            return sect_box

        def _apply_unsupported_state(section_box: Gtk.Box, supported: bool, label: str = "This feature") -> None:
            """When the feature is not detected, remove any field rows so only
            the header and a single not-detected line are shown, matching Summary viewer."""
            if supported:
                return
            # Remove any children except the header box and separator (first 2 children)
            child = section_box.get_first_child()
            if child:
                child = child.get_next_sibling()  # sep
            if child:
                child = child.get_next_sibling()  # first field row, if any
            while child:
                next_sib = child.get_next_sibling()
                section_box.remove(child)
                child = next_sib

            # Single notice line: header and a line feature was not detected
            notice_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            notice_box.set_margin_start(10)
            notice_box.set_margin_end(10)
            notice_box.set_margin_top(8)
            notice_box.set_margin_bottom(8)

            notice = Gtk.Label(label="This feature was not detected on your system.")
            notice.add_css_class("dim-label")
            notice.set_halign(Gtk.Align.START)
            notice_box.append(notice)
            section_box.append(notice_box)

            section_box.set_sensitive(False)
            section_box.set_opacity(0.55)

        # ── Graphics, Compute & Video Acceleration (below Header) ──────
        tech_frame = _make_section(
            "Graphics, Compute & Video Acceleration",
            const.ABOUT_US_PNG,
            fallback_icon_name="preferences-system-symbolic",
        )

        tech_flow = Gtk.FlowBox()
        tech_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        tech_flow.set_max_children_per_line(8)
        tech_flow.set_min_children_per_line(4)
        tech_flow.set_row_spacing(2)
        tech_flow.set_column_spacing(4)
        tech_flow.set_homogeneous(True)
        tech_flow.set_margin_start(6)
        tech_flow.set_margin_end(6)
        tech_flow.set_margin_top(2)
        tech_flow.set_margin_bottom(2)

        techs = [
            ("Vulkan",        has_vulkan),
            ("Vulkan Video",  has_vulkan_video),
            ("OpenGL",        has_opengl),
            ("EGL",           has_egl),
            ("OpenCL",        has_opencl),
            ("VDPAU",         has_vdpau),
            ("Ray Tracing",   has_raytracing),
            ("Mesh Shaders",  has_mesh_shaders),
        ]

        for name, supported in techs:
            b = self._make_tech_badge(name, supported)
            tech_flow.append(b)

        tech_frame.append(tech_flow)
        self.card_content_box.append(tech_frame)

        # ── GPU Hardware Stats ─────────────────────────────────────────
        hw_frame = _make_section(
            "GPU Hardware", const.APP_LOGO_PNG,
            fallback_icon_name="video-display-symbolic",
        )

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
        vram_used = stats.get("mem_used", 0)
        if vram_tot > 0:
            vram_disp = f"{vram_used} / {vram_tot} MB"
        elif vram_used is not None and vram_used >= 0:
            vram_disp = f"{vram_used} MB"
        else:
            vram_disp = "—"
        vram_type = stats.get("vram_type") or gpu.get("vram_type") or "—"

        core_clk = f"{stats.get('clock_current', 0)} MHz" if stats.get("clock_current", 0) > 0 else "—"
        boost_clk = f"{stats.get('clock_max', 0)} MHz" if stats.get("clock_max", 0) > 0 else "—"
        vram_clk_used = stats.get("vram_clock", 0)
        vram_clk_total = stats.get("vram_clock_max", 0)
        if vram_clk_used > 0 and vram_clk_total > 0:
            vram_clk_disp = f"{vram_clk_used} / {vram_clk_total} MHz"
        elif vram_clk_used > 0:
            vram_clk_disp = f"{vram_clk_used} MHz"
        elif vram_clk_total > 0:
            vram_clk_disp = f"{vram_clk_total} MHz"
        else:
            vram_clk_disp = "—"

        temp_val = stats.get("temp", 0)
        temp_disp = f"{temp_val} °C" if temp_val is not None and temp_val > 0 else "—"
        power_val = stats.get("power_usage", -1)
        power_disp = f"{power_val} W" if power_val is not None and power_val >= 0 else "—"
        usage_val = stats.get("usage", -1)
        usage_disp = f"{usage_val} %" if usage_val is not None and usage_val >= 0 else "—"
        
        fan_val = stats.get("fan_speed", -1)
        fan_rpm = stats.get("fan_rpm", -1)
        if fan_val is not None and fan_val >= 0 and fan_rpm is not None and fan_rpm > 0:
            fan_disp = f"{fan_val} % ({fan_rpm} RPM)"
        elif fan_val is not None and fan_val >= 0:
            fan_disp = f"{fan_val} %"
        elif fan_rpm is not None and fan_rpm >= 0:
            fan_disp = f"{fan_rpm} RPM"
        else:
            fan_disp = "—"

        gtt_used = stats.get("gtt_used", 0)
        gtt_total = stats.get("gtt_total", 0)
        if gtt_total > 0:
            gtt_disp = f"{gtt_used} / {gtt_total} MB"
        elif gtt_used is not None and gtt_used >= 0:
            gtt_disp = f"{gtt_used} MB"
        else:
            gtt_disp = "—"

        # GPU Hardware – packed into 3–4 fields per row
        _add_row(hw_frame, ("Device ID", dev_id_display),
                            ("Device Type", _clean_device_type(vk_dev.get("device_type", "—"))),
                            ("Driver", driver_val), ("VBIOS", bios_val))
        _add_row(hw_frame, ("PCIe Link", bus_interface),
                            ("VRAM", vram_disp, "hw_vram"), ("GTT Memory", gtt_disp, "hw_gtt"))
        _add_row(hw_frame, ("GPU Usage", usage_disp, "hw_usage"),
                            ("GPU Clock", core_clk, "hw_clock"), ("Boost Clock", boost_clk),
                            ("VRAM Clock", vram_clk_disp, "hw_vram_clock"))
        _add_row(hw_frame, ("Temperature", temp_disp, "hw_temp"),
                            ("Power Draw", power_disp, "hw_power"), ("Fan Speed", fan_disp, "hw_fan"))
        self.card_content_box.append(hw_frame)

        # ── Vulkan ────────────────────────────────────────────────────
        vk_frame = _make_section(
            "Vulkan", const.VULKAN_PNG, fallback_icon_name="image-x-generic-symbolic",
            nav_actions=[("Open Vulkan →", "page1")] if has_vulkan else [],
        )
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

        # Ray tracing and Mesh shader support (pre-computed)
        vk_rt_str = "Supported" if has_rt else "Not Available"
        vk_mesh_str = "Supported" if has_mesh else "Not Available"

        # Vulkan – 4 fields per row, long UUIDs on their own full-width row
        if has_vulkan:
            _add_row(vk_frame,
                     ("API Version", vk_api), ("Instance Ver.", vk_inst_ver),
                     ("Conformance", vk_conform), ("Device Type", vk_dev_type))
            _add_row(vk_frame,
                     ("Driver Name", vk_drv_name), ("Driver Info", vk_drv_info),
                     ("Driver Ver.", vk_drv_ver))
            _add_row(vk_frame, ("Vendor ID", vk_vendor_id), ("Device ID", vk_device_id))
            _add_row(vk_frame,
                     ("Device Ext.", vk_ext_cnt), ("Device Formats", vk_fmt_cnt),
                     ("Instance Ext.", vk_inst_ext_cnt), ("Instance Layers", vk_inst_layers_cnt))
            _add_row(vk_frame,
                     ("Memory Types", vk_mem_types), ("Memory Heaps", vk_mem_heaps),
                     ("Queue Families", vk_queue_fam),
                     ("Ray Tracing", vk_rt_str), ("Mesh Shaders", vk_mesh_str))
            if vk_pipeline_uuid and vk_pipeline_uuid not in ("—", "-"):
                _add_row(vk_frame, ("Pipeline Cache UUID", vk_pipeline_uuid))
            if vk_uuid and vk_uuid not in ("—", "-"):
                _add_row(vk_frame, ("Device UUID", vk_uuid))
            if vk_drv_uuid and vk_drv_uuid not in ("—", "-"):
                _add_row(vk_frame, ("Driver UUID", vk_drv_uuid))

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
                    _add_row(vk_frame, ("Video Decode Profiles", decode_text))

            if vk_dev.get("video_encode_profiles"):
                encode_text = _format_video_profile_counts(
                    vk_dev["video_encode_profiles"],
                    vk_dev.get("video_encode_profile_counts", {}),
                    "Encode"
                )
                if encode_text:
                    _add_row(vk_frame, ("Video Encode Profiles", encode_text))

        _apply_unsupported_state(vk_frame, has_vulkan, "Vulkan")
        self.card_content_box.append(vk_frame)

        # ── OpenGL & EGL ─────────────────────────────────────────────
        gl_frame = _make_section(
            "OpenGL / EGL", const.OPEN_GL_PNG,
            fallback_icon_name="applications-engineering-symbolic",
            nav_actions=[("Open EGL →", "page2")]
            if has_opengl or has_egl else [],
        )
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

        # OpenGL – related versions and extension counts share rows
        if has_opengl or has_egl:
            _add_row(gl_frame,
                     ("Vendor", gl_vendor), ("Renderer", gl_renderer),
                     ("OpenGL Version", gl_version), ("GLSL Version", gl_glsl),
                     ("GL Extensions", gl_ext_cnt))
            _add_row(gl_frame,
                     ("OpenGL ES", gl_es_ver), ("ES Extensions", es_ext_cnt),
                     ("EGL Version", egl_version), ("EGL Ext.", egl_ext_cnt))
            _add_row(gl_frame,
                     ("GLX Version", gl_glx_ver), ("GLX Extensions", glx_ext_cnt),
                     ("GLX Visuals", glx_vis_cnt), ("FB Configs", fbcfg_cnt))
        _apply_unsupported_state(gl_frame, has_opengl or has_egl, "OpenGL / EGL")
        self.card_content_box.append(gl_frame)

        # ── OpenCL ────────────────────────────────────────────────────
        cl_frame = _make_section(
            "OpenCL", "../Images/OpenCL.svg", fallback_icon_name="system-run-symbolic",
            nav_actions=[("Open OpenCL →", "opencl_page")]
            if has_opencl else [],
        )
        cl_platforms = cl_data.get("platforms", [])
        cl_plat_cnt = str(len(cl_platforms)) if cl_platforms else "0"

        def _populate_cl_device(cl_frame, matched_plat, matched_dev, cl_plat_cnt):
            cl_plat_name = matched_plat.get("name", "—")
            cl_plat_ver  = matched_plat.get("version", "—")
            cl_plat_ext  = str(matched_plat.get("extensions_count", 0)) if matched_plat.get("extensions_count") else "—"
            cl_dev_name  = matched_dev.get("name", "—")
            cl_dev_type  = matched_dev.get("device_type", "—")
            cl_dev_ver   = matched_dev.get("version", "—")
            cl_opencl_c  = matched_dev.get("opencl_c_version", "—")
            cl_cus       = str(matched_dev.get("compute_units", "—"))
            cl_wgs       = str(matched_dev.get("workgroup_size", "—"))
            cl_gmem      = matched_dev.get("global_memory", "—")
            cl_lmem      = matched_dev.get("local_memory", "—")
            cl_clk       = str(matched_dev.get("max_clock", "—"))
            cl_drv_ver   = matched_dev.get("driver_version", "—")
            cl_dev_ext   = str(matched_dev.get("extensions_count", 0)) if matched_dev.get("extensions_count") else "—"
            _add_row(cl_frame,
                     ("Platform", cl_plat_name), ("Platforms", cl_plat_cnt),
                     ("Platform Ver.", cl_plat_ver), ("Plat. Ext.", cl_plat_ext))
            _add_row(cl_frame,
                     ("Device", cl_dev_name), ("Device Type", cl_dev_type),
                     ("Device Ver.", cl_dev_ver), ("OpenCL C", cl_opencl_c))
            _add_row(cl_frame,
                     ("Compute Units", cl_cus), ("Max Workgroup", cl_wgs),
                     ("Global Mem.", cl_gmem), ("Local Mem.", cl_lmem), ("Max Clock", cl_clk))
            _add_row(cl_frame, ("Driver Ver.", cl_drv_ver), ("Dev. Extensions", cl_dev_ext))

        if has_opencl:
            if matched_devices:
                for idx, (matched_plat, matched_dev) in enumerate(matched_devices):
                    if idx > 0:
                        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                        sep.add_css_class("gpuz-section-sep")
                        cl_frame.append(sep)
                    if len(matched_devices) > 1:
                        inst_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                        inst_box.set_margin_top(2)
                        inst_box.set_margin_bottom(2)
                        inst_lbl = Gtk.Label(label=f"OpenCL Device #{idx + 1} — {matched_plat.get('name', 'Platform')}")
                        inst_lbl.add_css_class("gpuz-frame-label")
                        inst_lbl.set_halign(Gtk.Align.START)
                        inst_box.append(inst_lbl)
                        cl_frame.append(inst_box)
                    _populate_cl_device(cl_frame, matched_plat, matched_dev, cl_plat_cnt)
            else:
                empty_plat = {"name": "—", "version": "—", "extensions_count": 0}
                empty_dev  = {"name": "—", "device_type": "—", "version": "—",
                              "opencl_c_version": "—", "compute_units": "—", "workgroup_size": "—",
                              "global_memory": "—", "local_memory": "—", "max_clock": "—",
                              "driver_version": "—", "extensions_count": 0}
                _populate_cl_device(cl_frame, empty_plat, empty_dev, cl_plat_cnt)
        _apply_unsupported_state(cl_frame, has_opencl, "OpenCL")
        self.card_content_box.append(cl_frame)

        # ── VDPAU ─────────────────────────────────────────────────────
        vdpau_frame = _make_section(
            "VDPAU", const.VDPAU_CL_PNG,
            fallback_icon_name="media-playback-start-symbolic",
            nav_actions=[("Open VDPAU →", "vdpau_page")]
            if has_vdpau else [],
        )
        vdpau_supported = "Yes" if vdpau_data.get("supported") else "No"
        vdpau_api  = vdpau_data.get("api_version", "—")
        vdpau_rend = vdpau_data.get("renderer", "—")
        if has_vdpau:
            _add_row(vdpau_frame,
                     ("Supported", vdpau_supported), ("API Version", vdpau_api),
                     ("Renderer", vdpau_rend))
        _apply_unsupported_state(vdpau_frame, has_vdpau, "VDPAU")
        self.card_content_box.append(vdpau_frame)

    def _make_field_frame(self, label: str, value: str, live_key: str = None, registry: dict = None) -> Gtk.Frame:
        """Create a Classic GTK Frame with the field name embedded in the upper border
        and the content left-justified inside the frame.

        Args:
            label:    Header label text for the frame.
            value:    Initial value text.
            live_key: If set, the value label is registered in
                      ``registry[live_key]`` (defaults to ``self._hw_live_labels``)
                      so that the polling loop can update it in real time.
            registry: Optional target dictionary for live label registration.
        """
        frame = Gtk.Frame()
        frame.add_css_class("gpuz-field-frame")
        frame.set_hexpand(True)

        hdr_lbl = Gtk.Label(label=f" {label} ")
        hdr_lbl.add_css_class("gpuz-frame-label")
        hdr_lbl.set_halign(Gtk.Align.START)
        frame.set_label_widget(hdr_lbl)

        content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        content_box.add_css_class("gpuz-frame-content")

        clean_val = str(value).strip() if value is not None and str(value).strip() else "—"
        clean_val = re.sub(r'\s+', ' ', clean_val).strip()
        clean_val = re.sub(r'\s*\(\d+\)$', '', clean_val).strip()

        val = Gtk.Label(label=clean_val)
        val.add_css_class("gpuz-frame-value")
        val.set_halign(Gtk.Align.START)
        val.set_xalign(0.0)
        val.set_hexpand(True)
        val.set_selectable(True)
        # Wrap long values only when they exceed the available field frame width
        val.set_wrap(True)
        val.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        if hasattr(Gtk, "NaturalWrapMode") and hasattr(val, "set_natural_wrap_mode"):
            val.set_natural_wrap_mode(Gtk.NaturalWrapMode.NONE)
        val.set_ellipsize(Pango.EllipsizeMode.NONE)
        val.set_max_width_chars(-1)
        val.set_width_chars(-1)
        val.set_tooltip_text(clean_val)
        content_box.append(val)

        copy_btn = Gtk.Button()
        copy_btn.set_icon_name("edit-copy-symbolic")
        copy_btn.add_css_class("flat")
        copy_btn.set_valign(Gtk.Align.CENTER)
        copy_btn.set_tooltip_text("Copy to clipboard")
        copy_btn.set_opacity(0.0)

        def _copy_field_value(_button):
            display = Gdk.Display.get_default()
            if display is not None:
                display.get_clipboard().set(f"{label}: {val.get_label()}")

        copy_btn.connect("clicked", _copy_field_value)
        content_box.append(copy_btn)

        motion = Gtk.EventControllerMotion()
        motion.connect("enter", lambda *_args: copy_btn.set_opacity(0.6))
        motion.connect("leave", lambda *_args: copy_btn.set_opacity(0.0))
        frame.add_controller(motion)

        frame.set_child(content_box)

        if live_key is not None:
            target_reg = registry if registry is not None else getattr(self, "_hw_live_labels", None)
            if target_reg is not None:
                target_reg[live_key] = val
            elif registry is None:
                if not hasattr(self, "_hw_live_labels"):
                    self._hw_live_labels = {}
                self._hw_live_labels[live_key] = val

        return frame

    _make_field_cell = _make_field_frame

    def _make_tech_badge(self, name: str, supported: bool) -> Gtk.Widget:
        """Create a non-interactive API-support checkbox."""
        checkbox = Gtk.CheckButton(label=name)
        checkbox.set_active(supported)
        checkbox.set_hexpand(True)
        checkbox.add_css_class("gpuz-api-checkbox")
        if supported:
            checkbox.add_css_class("gpuz-api-supported")
        else:
            checkbox.add_css_class("gpuz-api-unsupported")

        checkbox.connect(
            "toggled",
            lambda button: button.set_active(supported)
            if button.get_active() != supported
            else None,
        )
        return checkbox

    # -----------------------------------------------------------------------
    # Tab 2: Sensors Telemetry
    # -----------------------------------------------------------------------

    def _build_sensors_tab(self) -> Gtk.Widget:
        sensor_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        sensor_page.add_css_class("gpuz-sensor-page")
        interval_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        interval_box.set_halign(Gtk.Align.END)
        interval_box.set_margin_top(6)
        interval_box.set_margin_end(12)
        interval_label = Gtk.Label(label="Stats refresh interval:")
        interval_label.add_css_class("gpuz-frame-label")
        interval_box.append(interval_label)
        refresh_interval_values = getattr(
            self.app, "_refresh_interval_values", [250, 500, 1000, 2000, 5000]
        )
        interval_options = ["250 ms", "500 ms", "1 s", "2 s", "5 s"]
        self._refresh_interval_dropdown = Gtk.DropDown.new(
            Gtk.StringList.new(interval_options), None
        )
        current_interval = getattr(self.app, "_current_refresh_interval_ms", 1000)
        try:
            selected_interval = refresh_interval_values.index(current_interval)
        except ValueError:
            selected_interval = 2
        self._refresh_interval_dropdown.set_selected(selected_interval)
        self._refresh_interval_dropdown.connect(
            "notify::selected", self._on_refresh_interval_selected
        )
        interval_box.append(self._refresh_interval_dropdown)
        sensor_page.append(interval_box)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        self.sensors_scroll = scroll

        self.sensor_widgets = {}
        gpu = self._get_current_gpu()
        gpu_stats = get_gpu_stats_for_index(gpu.get("card_index", 0)) or gpu.get("stats", {}) or {}
        net_down, net_up = get_realtime_net_speed()
        scroll.set_child(
            _make_gauge_dashboard(
                gpu_stats,
                self.sensor_widgets,
                cpu_usage=get_realtime_cpu_usage(),
                ram_usage=get_realtime_ram_usage(),
                cpu_temp=get_realtime_cpu_temp(),
                swap_usage=get_realtime_swap_usage(),
                net_down_mbps=net_down,
                net_up_mbps=net_up,
            )
        )
        sensor_page.append(scroll)
        return sensor_page

    def _on_refresh_interval_selected(self, dropdown, _pspec):
        if self._syncing_refresh_interval:
            return
        selected = dropdown.get_selected()
        values = getattr(
            self.app, "_refresh_interval_values", [250, 500, 1000, 2000, 5000]
        )
        if selected >= len(values):
            return

        interval_ms = values[selected]
        if hasattr(self.app, "config"):
            self.app.config.set_refresh_interval(interval_ms)
        self.app._current_refresh_interval_ms = interval_ms

        dashboard_dropdown = getattr(self.app, "_interval_dropdown", None)
        if dashboard_dropdown is not None and dashboard_dropdown.get_selected() != selected:
            dashboard_dropdown.set_selected(selected)
        else:
            self.set_refresh_interval(interval_ms)

    def _format_live_val(self, val_str: str) -> str:
        """Format live sensor / telemetry string: clean whitespace."""
        clean = re.sub(r'\s+', ' ', str(val_str).strip()) if val_str is not None and str(val_str).strip() else "—"
        clean = re.sub(r'\s*\(\d+\)$', '', clean).strip()
        return clean

    def _set_live_label(self, registry, key, val):
        """Avoid GTK relayout work when a live label has not changed."""
        label = registry.get(key)
        if label is None:
            return
        val = self._format_live_val(val)
        if label.get_label() != val:
            label.set_label(val)

    def _update_sensors(self, rebuild_dashboard=False):
        """Poll telemetry and update values and sparklines."""
        gpu = self._get_current_gpu()
        idx = gpu.get("card_index", 0)
        stats = get_gpu_stats_for_index(idx) or {}

        # System telemetry
        cpu_usage_str = get_realtime_cpu_usage()
        cpu_temp_val = get_realtime_cpu_temp()
        ram_usage_str = get_realtime_ram_usage()
        swap_usage = get_realtime_swap_usage()
        net_down_mbps, net_up_mbps = get_realtime_net_speed()
        if rebuild_dashboard and hasattr(self, "sensors_scroll"):
            self.sensor_widgets = {}
            dashboard = _make_gauge_dashboard(
                stats,
                self.sensor_widgets,
                cpu_usage=cpu_usage_str,
                ram_usage=ram_usage_str,
                cpu_temp=cpu_temp_val,
                swap_usage=swap_usage,
                net_down_mbps=net_down_mbps,
                net_up_mbps=net_up_mbps,
            )
            self.sensors_scroll.set_child(dashboard)
        else:
            _update_gauge_dict(
                getattr(self, "sensor_widgets", {}),
                stats,
                cpu_usage=cpu_usage_str,
                ram_usage=ram_usage_str,
                cpu_temp=cpu_temp_val,
                swap_usage=swap_usage,
                net_down_mbps=net_down_mbps,
                net_up_mbps=net_up_mbps,
            )

        # ── Real-time updates for GPU Hardware tab labels ──────────────────
        live = getattr(self, "_hw_live_labels", {})
        if live:
            temp_v = stats.get("temp", 0)
            if "hw_temp" in live:
                val = f"{temp_v} °C" if temp_v is not None and temp_v > 0 else "—"
                self._set_live_label(live, "hw_temp", val)
            pwr_v = stats.get("power_usage", -1)
            if "hw_power" in live:
                val = f"{pwr_v} W" if pwr_v is not None and pwr_v >= 0 else "—"
                self._set_live_label(live, "hw_power", val)
            fan_v = stats.get("fan_speed", -1)
            fan_rpm_v = stats.get("fan_rpm", -1)
            if "hw_fan" in live:
                if fan_v is not None and fan_v >= 0 and fan_rpm_v is not None and fan_rpm_v > 0:
                    val = f"{fan_v} % ({fan_rpm_v} RPM)"
                elif fan_v is not None and fan_v >= 0:
                    val = f"{fan_v} %"
                elif fan_rpm_v is not None and fan_rpm_v >= 0:
                    val = f"{fan_rpm_v} RPM"
                else:
                    val = "—"
                self._set_live_label(live, "hw_fan", val)
            usage_v = stats.get("usage", -1)
            if "hw_usage" in live:
                val = f"{usage_v} %" if usage_v is not None and usage_v >= 0 else "—"
                self._set_live_label(live, "hw_usage", val)
            vram_tot_v = stats.get("mem_total", 0)
            vram_used_v = stats.get("mem_used", 0)
            if "hw_vram" in live:
                if vram_tot_v > 0:
                    val = f"{vram_used_v} / {vram_tot_v} MB"
                elif vram_used_v is not None and vram_used_v >= 0:
                    val = f"{vram_used_v} MB"
                else:
                    val = "—"
                self._set_live_label(live, "hw_vram", val)
            gtt_u = stats.get("gtt_used", 0)
            gtt_t = stats.get("gtt_total", 0)
            if "hw_gtt" in live:
                if gtt_t > 0:
                    val = f"{gtt_u} / {gtt_t} MB"
                elif gtt_u is not None and gtt_u >= 0:
                    val = f"{gtt_u} MB"
                else:
                    val = "—"
                self._set_live_label(live, "hw_gtt", val)
            clk_v = stats.get("clock_current", 0)
            if "hw_clock" in live:
                val = f"{clk_v} MHz" if clk_v and clk_v > 0 else "—"
                self._set_live_label(live, "hw_clock", val)
            vram_clk_used_v = stats.get("vram_clock", 0)
            vram_clk_total_v = stats.get("vram_clock_max", 0)
            if vram_clk_used_v > 0 and vram_clk_total_v > 0:
                vram_clk_val = f"{vram_clk_used_v} / {vram_clk_total_v} MHz"
            elif vram_clk_used_v > 0:
                vram_clk_val = f"{vram_clk_used_v} MHz"
            elif vram_clk_total_v > 0:
                vram_clk_val = f"{vram_clk_total_v} MHz"
            else:
                vram_clk_val = "—"
            if "hw_vram_clock" in live:
                self._set_live_label(live, "hw_vram_clock", vram_clk_val)
            if "hw_mem_clock" in live:
                self._set_live_label(live, "hw_mem_clock", vram_clk_val)

        # ── Real-time updates for System tab labels ──────────────────────
        sys_live = getattr(self, "_sys_live_labels", {})
        if sys_live:
            if "sys_cpu_usage" in sys_live:
                val = cpu_usage_str if cpu_usage_str else "—"
                self._set_live_label(sys_live, "sys_cpu_usage", val)
            if "sys_cpu_temp" in sys_live:
                val = f"{cpu_temp_val} °C" if cpu_temp_val and cpu_temp_val > 0 else "—"
                self._set_live_label(sys_live, "sys_cpu_temp", val)
            if "sys_ram_usage" in sys_live:
                val = ram_usage_str if ram_usage_str else "—"
                self._set_live_label(sys_live, "sys_ram_usage", val)
            if "sys_uptime" in sys_live:
                try:
                    with open("/proc/uptime", "r") as f:
                        upt = float(f.readline().split()[0])
                        m, s = divmod(upt, 60)
                        h, m = divmod(m, 60)
                        d, h = divmod(h, 24)
                        parts = []
                        if d > 0: parts.append(f"{int(d)}d")
                        if h > 0: parts.append(f"{int(h)}h")
                        if m > 0: parts.append(f"{int(m)}m")
                        if not parts: parts.append(f"{int(s)}s")
                        self._set_live_label(sys_live, "sys_uptime", " ".join(parts))
                except Exception:
                    pass

    # -----------------------------------------------------------------------
    # Tab 3: System Information Inspector
    # -----------------------------------------------------------------------

    def _build_system_tab(self) -> Gtk.Widget:
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        self.system_scroll = scroll

        self.sys_content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.sys_content_box.add_css_class("gpuz-system-page")
        self.sys_content_box.set_margin_start(8)
        self.sys_content_box.set_margin_end(8)
        self.sys_content_box.set_margin_top(6)
        self.sys_content_box.set_margin_bottom(8)

        self._refresh_system_content()
        scroll.set_child(self.sys_content_box)
        return scroll

    def _refresh_system_content(self):
        """Build the System Information page with hardware, OS, and processor details."""
        child = self.sys_content_box.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self.sys_content_box.remove(child)
            child = nxt

        if not hasattr(self, "_sys_live_labels"):
            self._sys_live_labels = {}
        else:
            self._sys_live_labels.clear()

        sys_data = self.summary_data.get("system", {}) or {}

        # Helpers
        def _make_section(title, icon_name=None) -> Gtk.Box:
            sect_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            sect_box.add_css_class("gpuz-section-box")

            hdr_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            hdr_box.add_css_class("gpuz-section-header")

            if icon_name:
                icon = Gtk.Image.new_from_icon_name(icon_name)
                icon.set_pixel_size(14)
                hdr_box.append(icon)

            hdr = Gtk.Label(label=title)
            hdr.add_css_class("gpuz-section-title")
            hdr.set_halign(Gtk.Align.START)
            hdr_box.append(hdr)
            sect_box.append(hdr_box)

            sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            sep.add_css_class("gpuz-section-sep")
            sect_box.append(sep)

            return sect_box

        def _add_dual_row(parent, l1, v1, l2="", v2="", live_key1=None, live_key2=None):
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            row_box.set_hexpand(True)
            row_box.set_margin_start(6)
            row_box.set_margin_end(6)
            row_box.append(self._make_field_frame(l1, v1, live_key=live_key1, registry=self._sys_live_labels))
            if l2 or v2:
                row_box.append(self._make_field_frame(l2, v2, live_key=live_key2, registry=self._sys_live_labels))
            parent.append(row_box)

        def _add_single_row(parent, label, value, live_key=None):
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            row_box.set_hexpand(True)
            row_box.set_margin_start(6)
            row_box.set_margin_end(6)
            cell = self._make_field_frame(label, value, live_key=live_key, registry=self._sys_live_labels)
            cell.set_hexpand(True)
            row_box.append(cell)
            parent.append(row_box)

        # Flexible multi-column row helper (up to 5 cols).
        # Each item: (label, value) or (label, value, live_key).
        def _add_row(parent, *items):
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            row_box.set_hexpand(True)
            row_box.set_margin_start(6)
            row_box.set_margin_end(6)
            for item in items:
                lbl_text = item[0]
                val_text = item[1]
                lk = item[2] if len(item) > 2 else None
                row_box.append(self._make_field_frame(lbl_text, val_text, live_key=lk,
                                                      registry=self._sys_live_labels))
            parent.append(row_box)

        # ── Header: OS / System Summary Frame with Distro Logo ─────────
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.add_css_class("gpuz-header-frame")

        os_str = sys_data.get("os", "")
        distro_logo_path = self._get_distro_logo_path(os_str)
        logo_loaded = False
        if distro_logo_path and os.path.exists(distro_logo_path):
            try:
                pixbuf = self._load_header_logo_pixbuf(distro_logo_path)
                logo_img = Gtk.Picture.new_for_pixbuf(pixbuf)
                logo_img.set_size_request(38, 38)
                logo_img.set_valign(Gtk.Align.CENTER)
                header_box.append(logo_img)
                logo_loaded = True
            except Exception:
                pass

        if not logo_loaded:
            sys_icon = Gtk.Image.new_from_icon_name("computer-symbolic")
            sys_icon.set_pixel_size(44)
            sys_icon.set_valign(Gtk.Align.CENTER)
            header_box.append(sys_icon)

        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        title_box.set_valign(Gtk.Align.CENTER)
        sys_title = os_str if os_str else "Linux System"
        title_lbl = Gtk.Label(label=sys_title)
        title_lbl.add_css_class("gpuz-header-title")
        title_lbl.set_halign(Gtk.Align.START)
        title_lbl.set_wrap(True)
        title_lbl.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        if hasattr(Gtk, "NaturalWrapMode") and hasattr(title_lbl, "set_natural_wrap_mode"):
            title_lbl.set_natural_wrap_mode(Gtk.NaturalWrapMode.NONE)
        title_box.append(title_lbl)

        host_model = sys_data.get("hardware_model") or sys_data.get("hostname") or "System Information"
        kernel_ver = sys_data.get("kernel")
        sub_text = f"{host_model} • Linux {kernel_ver}" if kernel_ver else host_model
        host_lbl = Gtk.Label(label=sub_text)
        host_lbl.add_css_class("dim-label")
        host_lbl.set_halign(Gtk.Align.START)
        title_box.append(host_lbl)

        header_box.append(title_box)
        self.sys_content_box.append(header_box)

        # ── Section 1: Operating System & Session ───────────────────────
        os_frame = _make_section("Operating System", "computer-symbolic")
        _add_row(os_frame,
                 ("OS Name", sys_data.get("os", "—")), ("Kernel", sys_data.get("kernel", "—")),
                 ("Desktop", sys_data.get("desktop", "—")), ("Windowing", sys_data.get("windowing", "—")))
        _add_row(os_frame,
                 ("Hostname", sys_data.get("hostname", "—")),
                 ("Uptime", sys_data.get("uptime", "—"), "sys_uptime"))
        self.sys_content_box.append(os_frame)

        # ── Section 2: Motherboard & BIOS ──────────────────────────────
        hw_frame = _make_section("Motherboard & BIOS", "preferences-desktop-display-symbolic")
        hw_model = sys_data.get("hardware_model", "—")
        bios_ver = sys_data.get("bios_version", "—")
        bios_date = sys_data.get("bios_date", "—")
        if hw_model and hw_model != "—":
            _add_row(hw_frame, ("Hardware Model", hw_model), ("BIOS Version", bios_ver), ("BIOS Date", bios_date))
        else:
            _add_row(hw_frame, ("BIOS Version", bios_ver), ("BIOS Date", bios_date))
        self.sys_content_box.append(hw_frame)

        # ── Section 3: Processor (CPU) ──────────────────────────────────
        cpu_frame = _make_section("Processor (CPU)", "cpu-symbolic")
        cpu_name = sys_data.get("cpu", "—")
        _add_row(cpu_frame, ("Processor", cpu_name))
        cpu_u = get_realtime_cpu_usage()
        cpu_t = get_realtime_cpu_temp()
        cpu_t_disp = f"{cpu_t} °C" if cpu_t and cpu_t > 0 else "—"
        cpu_cache = sys_data.get("cpu_cache", "—")
        cpu_boost = sys_data.get("cpu_boost", "—")
        cpu_virt = sys_data.get("virtualization", "—")

        _add_row(
            cpu_frame,
            ("Architecture", sys_data.get("architecture", "—")),
            ("Cores / Threads", sys_data.get("cpu_cores_threads", "—")),
        )
        if (cpu_boost and cpu_boost != "—") or (cpu_virt and cpu_virt != "—"):
            _add_row(
                cpu_frame,
                ("Frequency Boost", cpu_boost),
                ("Virtualization", cpu_virt),
            )
        _add_row(
            cpu_frame,
            ("CPU Load", cpu_u, "sys_cpu_usage"),
            ("CPU Temperature", cpu_t_disp, "sys_cpu_temp"),
        )
        if cpu_cache and cpu_cache != "—":
            _add_row(cpu_frame, ("CPU Cache", cpu_cache))
        self.sys_content_box.append(cpu_frame)

        # ── Section 4: Memory & Storage ────────────────────────────────
        mem_frame = _make_section("Memory & Storage", "drive-harddisk-symbolic")
        ram_tot = sys_data.get("ram", "—")
        ram_u = get_realtime_ram_usage()
        disk_cap = sys_data.get("disk_capacity", "—")
        mem_items = [("Total RAM", ram_tot), ("RAM Usage", ram_u, "sys_ram_usage")]
        if disk_cap and disk_cap != "—":
            mem_items.append(("Storage", disk_cap))
        _add_row(mem_frame, *mem_items)
        self.sys_content_box.append(mem_frame)

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
        self._refresh_system_content()
        self._update_sensors(rebuild_dashboard=True)

    def _on_gpu_selected(self, dropdown, _pspec):
        idx = dropdown.get_selected()
        if 0 <= idx < len(self.gpus):
            self.selected_gpu_idx = idx
            self._refresh_graphics_card_content()
            self._update_sensors(rebuild_dashboard=True)
            self._scroll_gpu_pages_to_top()

    def _scroll_gpu_pages_to_top(self):
        """Reset GPU-Z page positions when switching GPUs."""
        for scroll_name in ("card_scroll", "sensors_scroll", "system_scroll"):
            scroll = getattr(self, scroll_name, None)
            if scroll is not None:
                scroll.get_vadjustment().set_value(0)

    def _on_view_changed(self, _stack, _pspec):
        self._update_gpu_selector_visibility()

    def _update_gpu_selector_visibility(self):
        visible_name = self.view_stack.get_visible_child_name()
        self.bottom_bar.set_visible(visible_name != "system")

    # -----------------------------------------------------------------------
    # Sensor Polling Loop
    # -----------------------------------------------------------------------

    def _start_sensor_polling(self):
        if self.sensor_timer_id:
            GLib.source_remove(self.sensor_timer_id)
            self.sensor_timer_id = 0

        def _poll():
            if not self.get_mapped():
                return True
            if getattr(self.app, "current_view_mode", "gpuz") != "gpuz":
                return True
            self._update_sensors()
            return True

        interval = getattr(self.app, "_current_refresh_interval_ms", 1000)
        self.sensor_timer_id = GLib.timeout_add(interval, _poll)

    def set_refresh_interval(self, interval_ms: int):
        self.app._current_refresh_interval_ms = interval_ms
        values = getattr(
            self.app, "_refresh_interval_values", [250, 500, 1000, 2000, 5000]
        )
        if self._refresh_interval_dropdown is not None and interval_ms in values:
            selected = values.index(interval_ms)
            if self._refresh_interval_dropdown.get_selected() != selected:
                self._syncing_refresh_interval = True
                try:
                    self._refresh_interval_dropdown.set_selected(selected)
                finally:
                    self._syncing_refresh_interval = False
        if self.sensor_timer_id:
            self._start_sensor_polling()

    def _on_destroy(self, _widget):
        if self.sensor_timer_id:
            GLib.source_remove(self.sensor_timer_id)
            self.sensor_timer_id = 0
        display = Gdk.Display.get_default()
        if hasattr(self, '_css_provider') and self._css_provider and display:
            try:
                Gtk.StyleContext.remove_provider_for_display(display, self._css_provider)
            except Exception:
                pass
            self._css_provider = None
