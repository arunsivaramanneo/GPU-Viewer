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
from gi.repository import Gtk, Adw, GLib, GdkPixbuf, Pango, Gdk

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

.gpuz-header-frame {
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    background-image: linear-gradient(
        90deg,
        rgba(36, 95, 218, 0.18),
        #242429
    );
    background-color: #242429;
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
    padding: 6px 8px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    background-color: #242429;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.gpuz-section-header {
    margin-top: 1px;
    margin-bottom: 1px;
    padding-left: 2px;
}

.gpuz-section-title {
    font-size: 8pt;
    font-weight: 800;
    color: #78aeed;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}

.gpuz-section-sep {
    background-color: rgba(255, 255, 255, 0.10);
    opacity: 0.35;
    margin-top: 1px;
    margin-bottom: 3px;
}

/* Classic GTK Frame for each field */
.gpuz-field-frame {
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 5px;
    background-color: #1a1a1e;
    margin: 1px 0;
    transition: 150ms ease-in-out;
}

.gpuz-field-frame:hover {
    border-color: rgba(120, 174, 237, 0.45);
    background-color: #222228;
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
    background-color: #1a1a1e;
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
    background-color: #1e1e22;
    box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.3);
}
"""
    else:
        return """
.gpuz-container {
    background-color: #dcdcdc;
    color: rgba(0, 0, 0, 0.87);
    padding: 6px;
}

.gpuz-header-frame {
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 8px;
    background-image: linear-gradient(
        90deg,
        rgba(36, 95, 218, 0.10),
        #ffffff
    );
    background-color: #ffffff;
    padding: 6px 10px;
    margin-bottom: 4px;
}

.gpuz-header-title {
    font-size: 13pt;
    font-weight: 700;
    color: rgba(0, 0, 0, 0.87);
    letter-spacing: 0.1px;
}

.gpuz-section-box {
    margin-top: 3px;
    margin-bottom: 3px;
    padding: 6px 8px;
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 8px;
    background-color: #ffffff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.gpuz-section-header {
    margin-top: 1px;
    margin-bottom: 1px;
    padding-left: 2px;
}

.gpuz-section-title {
    font-size: 8pt;
    font-weight: 800;
    color: #1c71d8;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}

.gpuz-section-sep {
    background-color: rgba(0, 0, 0, 0.10);
    opacity: 0.35;
    margin-top: 1px;
    margin-bottom: 3px;
}

/* Classic GTK Frame for each field */
.gpuz-field-frame {
    border: 1px solid rgba(0, 0, 0, 0.10);
    border-radius: 5px;
    background-color: #f6f6f8;
    margin: 1px 0;
    transition: 150ms ease-in-out;
}

.gpuz-field-frame:hover {
    border-color: rgba(28, 113, 216, 0.45);
    background-color: #eef4fc;
}

.gpuz-frame-label {
    font-size: 7.5pt;
    font-weight: 700;
    color: rgba(0, 0, 0, 0.65);
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
    color: rgba(0, 0, 0, 0.87);
}

.gpuz-field-box {
    border: 1px solid rgba(0, 0, 0, 0.10);
    border-radius: 4px;
    padding: 2px 6px;
    min-height: 20px;
    background-color: #f6f6f8;
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
    background-color: #ffffff;
    border-color: #e01b24;
    -gtk-icon-size: 13px;
    min-width: 14px;
    min-height: 14px;
}

.gpuz-bottom-bar {
    border-top: 1px solid rgba(0, 0, 0, 0.12);
    padding: 5px 10px;
    background-color: #ebebed;
    box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.06);
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

        # Theme toggle on top right
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

    def _get_vendor_logo_path(self, vendor_id_str: str) -> str:
        """Return the selected GPU vendor's logo image path."""
        try:
            vendor_id = int(vendor_id_str, 16)
        except (TypeError, ValueError):
            vendor_id = None

        if vendor_id == 0x1002:
            return self._resolve_image_path("AMD_logo.png")
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
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(logo_path, 38, 38, True)
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
        def _add_dual_row(parent, l1, v1, l2="", v2="", live_key1=None, live_key2=None):
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            row_box.set_hexpand(True)
            row_box.set_homogeneous(True)
            row_box.append(self._make_field_frame(l1, v1, live_key=live_key1))
            if l2 or v2:
                row_box.append(self._make_field_frame(l2, v2, live_key=live_key2))
            else:
                row_box.get_first_child().set_hexpand(True)
            parent.append(row_box)

        # Helper: build a full-width single-field row
        def _add_single_row(parent, label, value, live_key=None):
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            row_box.set_hexpand(True)
            cell = self._make_field_frame(label, value, live_key=live_key)
            cell.set_hexpand(True)
            row_box.append(cell)
            parent.append(row_box)

        # Helper: section header with optional icon
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

        # ── Graphics, Compute & Video Acceleration (below Header) ──────
        tech_frame = _make_section("Graphics, Compute & Video Acceleration", "preferences-system-symbolic")

        tech_flow = Gtk.FlowBox()
        tech_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        tech_flow.set_max_children_per_line(8)
        tech_flow.set_min_children_per_line(4)
        tech_flow.set_row_spacing(2)
        tech_flow.set_column_spacing(4)
        tech_flow.set_homogeneous(True)

        techs = [
            ("Vulkan",        has_vulkan),
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
        hw_frame = _make_section("GPU Hardware", "video-display-symbolic")

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
        mem_clk = stats.get("vram_clock_max") or stats.get("vram_clock", 0)
        mem_clk_disp = f"{mem_clk} MHz" if mem_clk > 0 else "—"

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

        _add_dual_row(hw_frame, "Device ID",    dev_id_display,   "Driver",      driver_val)
        _add_dual_row(hw_frame, "VBIOS",        bios_val,         "PCIe Link",   bus_interface)
        _add_dual_row(hw_frame, "VRAM",         vram_disp,        "VRAM Type",   vram_type,
                      live_key1="hw_vram")
        _add_dual_row(hw_frame, "GTT Memory",   gtt_disp,         "GPU Usage",   usage_disp,
                      live_key1="hw_gtt", live_key2="hw_usage")
        _add_dual_row(hw_frame, "GPU Clock",    core_clk,         "Boost Clock", boost_clk,
                      live_key1="hw_clock")
        _add_dual_row(hw_frame, "Memory Clock", mem_clk_disp,     "Temperature", temp_disp,
                      live_key1="hw_mem_clock", live_key2="hw_temp")
        _add_dual_row(hw_frame, "Power Draw",   power_disp,       "Fan Speed",   fan_disp,
                      live_key1="hw_power", live_key2="hw_fan")
        self.card_content_box.append(hw_frame)

        # ── Vulkan ────────────────────────────────────────────────────
        vk_frame = _make_section("Vulkan", "image-x-generic-symbolic")
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
        gl_frame = _make_section("OpenGL / EGL", "applications-engineering-symbolic")
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
        cl_frame = _make_section("OpenCL", "system-run-symbolic")
        cl_platforms = cl_data.get("platforms", [])
        cl_plat_cnt = str(len(cl_platforms)) if cl_platforms else "0"

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

                _add_dual_row(cl_frame, "Platform",       cl_plat_name, "Platforms",      cl_plat_cnt)
                _add_dual_row(cl_frame, "Platform Ver.",  cl_plat_ver,  "Plat. Ext.",     cl_plat_ext)
                _add_dual_row(cl_frame, "Device",         cl_dev_name,  "Device Type",    cl_dev_type)
                _add_dual_row(cl_frame, "Device Ver.",    cl_dev_ver,   "OpenCL C",       cl_opencl_c)
                _add_dual_row(cl_frame, "Compute Units",  cl_cus,       "Max Workgroup",  cl_wgs)
                _add_dual_row(cl_frame, "Global Mem.",    cl_gmem,      "Local Mem.",     cl_lmem)
                _add_dual_row(cl_frame, "Max Clock",      cl_clk,       "Dev. Extensions",cl_dev_ext)
                _add_dual_row(cl_frame, "Driver Ver.",    cl_drv_ver,   "",               "")
        else:
            cl_plat_name = cl_plat_ver = cl_plat_ext = "—"
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

        # ── VDPAU ─────────────────────────────────────────────────────
        vdpau_frame = _make_section("VDPAU", "media-playback-start-symbolic")
        vdpau_supported = "Yes" if vdpau_data.get("supported") else "No"
        vdpau_api  = vdpau_data.get("api_version", "—")
        vdpau_rend = vdpau_data.get("renderer", "—")
        _add_dual_row(vdpau_frame, "Supported",  vdpau_supported, "API Version", vdpau_api)
        _add_single_row(vdpau_frame, "Renderer", vdpau_rend)
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
        clean_val = re.sub(r'\s*\(\d+\)$', '', clean_val).strip()

        val = Gtk.Label(label=clean_val)
        val.add_css_class("gpuz-frame-value")
        val.set_halign(Gtk.Align.START)
        val.set_xalign(0.0)
        val.set_hexpand(True)
        val.set_selectable(True)
        val.set_wrap(True)
        val.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        content_box.append(val)

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
        swap_usage = get_realtime_swap_usage()
        net_down_mbps, net_up_mbps = get_realtime_net_speed()
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
                live["hw_temp"].set_label(
                    f"{temp_v} °C" if temp_v is not None and temp_v > 0 else "—"
                )
            pwr_v = stats.get("power_usage", -1)
            if "hw_power" in live:
                live["hw_power"].set_label(
                    f"{pwr_v} W" if pwr_v is not None and pwr_v >= 0 else "—"
                )
            fan_v = stats.get("fan_speed", -1)
            fan_rpm_v = stats.get("fan_rpm", -1)
            if "hw_fan" in live:
                if fan_v is not None and fan_v >= 0 and fan_rpm_v is not None and fan_rpm_v > 0:
                    live["hw_fan"].set_label(f"{fan_v} % ({fan_rpm_v} RPM)")
                elif fan_v is not None and fan_v >= 0:
                    live["hw_fan"].set_label(f"{fan_v} %")
                elif fan_rpm_v is not None and fan_rpm_v >= 0:
                    live["hw_fan"].set_label(f"{fan_rpm_v} RPM")
                else:
                    live["hw_fan"].set_label("—")
            usage_v = stats.get("usage", -1)
            if "hw_usage" in live:
                live["hw_usage"].set_label(
                    f"{usage_v} %" if usage_v is not None and usage_v >= 0 else "—"
                )
            vram_tot_v = stats.get("mem_total", 0)
            vram_used_v = stats.get("mem_used", 0)
            if "hw_vram" in live:
                if vram_tot_v > 0:
                    live["hw_vram"].set_label(f"{vram_used_v} / {vram_tot_v} MB")
                elif vram_used_v is not None and vram_used_v >= 0:
                    live["hw_vram"].set_label(f"{vram_used_v} MB")
                else:
                    live["hw_vram"].set_label("—")
            gtt_u = stats.get("gtt_used", 0)
            gtt_t = stats.get("gtt_total", 0)
            if "hw_gtt" in live:
                if gtt_t > 0:
                    live["hw_gtt"].set_label(f"{gtt_u} / {gtt_t} MB")
                elif gtt_u is not None and gtt_u >= 0:
                    live["hw_gtt"].set_label(f"{gtt_u} MB")
                else:
                    live["hw_gtt"].set_label("—")
            clk_v = stats.get("clock_current", 0)
            if "hw_clock" in live:
                live["hw_clock"].set_label(
                    f"{clk_v} MHz" if clk_v and clk_v > 0 else "—"
                )
            mclk_v = stats.get("vram_clock_max") or stats.get("vram_clock", 0)
            if "hw_mem_clock" in live:
                live["hw_mem_clock"].set_label(
                    f"{mclk_v} MHz" if mclk_v and mclk_v > 0 else "—"
                )

        # ── Real-time updates for System tab labels ──────────────────────
        sys_live = getattr(self, "_sys_live_labels", {})
        if sys_live:
            if "sys_cpu_usage" in sys_live:
                sys_live["sys_cpu_usage"].set_label(cpu_usage_str if cpu_usage_str else "—")
            if "sys_cpu_temp" in sys_live:
                sys_live["sys_cpu_temp"].set_label(
                    f"{cpu_temp_val} °C" if cpu_temp_val and cpu_temp_val > 0 else "—"
                )
            if "sys_ram_usage" in sys_live:
                sys_live["sys_ram_usage"].set_label(ram_usage_str if ram_usage_str else "—")
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
                        sys_live["sys_uptime"].set_label(" ".join(parts))
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
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            row_box.set_hexpand(True)
            row_box.set_homogeneous(True)
            row_box.append(self._make_field_frame(l1, v1, live_key=live_key1, registry=self._sys_live_labels))
            if l2 or v2:
                row_box.append(self._make_field_frame(l2, v2, live_key=live_key2, registry=self._sys_live_labels))
            else:
                row_box.get_first_child().set_hexpand(True)
            parent.append(row_box)

        def _add_single_row(parent, label, value, live_key=None):
            row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            row_box.set_hexpand(True)
            cell = self._make_field_frame(label, value, live_key=live_key, registry=self._sys_live_labels)
            cell.set_hexpand(True)
            row_box.append(cell)
            parent.append(row_box)

        # ── Header: OS / System Summary Frame with Distro Logo ─────────
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.add_css_class("gpuz-header-frame")

        os_str = sys_data.get("os", "")
        distro_logo_path = self._get_distro_logo_path(os_str)
        logo_loaded = False
        if distro_logo_path and os.path.exists(distro_logo_path):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(distro_logo_path, 38, 38, True)
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
        title_lbl.set_max_width_chars(32)
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
        _add_dual_row(os_frame, "OS Name", sys_data.get("os", "—"), "Kernel", sys_data.get("kernel", "—"))
        _add_dual_row(os_frame, "Desktop", sys_data.get("desktop", "—"), "Windowing", sys_data.get("windowing", "—"))
        _add_dual_row(os_frame, "Hostname", sys_data.get("hostname", "—"), "Uptime", sys_data.get("uptime", "—"),
                      live_key2="sys_uptime")
        self.sys_content_box.append(os_frame)

        # ── Section 2: Motherboard & BIOS ──────────────────────────────
        hw_frame = _make_section("Motherboard & BIOS", "preferences-desktop-display-symbolic")
        hw_model = sys_data.get("hardware_model", "—")
        if hw_model and hw_model != "—":
            _add_single_row(hw_frame, "Hardware Model", hw_model)
        _add_dual_row(hw_frame, "BIOS Version", sys_data.get("bios_version", "—"),
                      "BIOS Date", sys_data.get("bios_date", "—"))
        self.sys_content_box.append(hw_frame)

        # ── Section 3: Processor (CPU) ──────────────────────────────────
        cpu_frame = _make_section("Processor (CPU)", "cpu-symbolic")
        cpu_name = sys_data.get("cpu", "—")
        _add_single_row(cpu_frame, "Processor", cpu_name)
        _add_dual_row(cpu_frame, "Architecture", sys_data.get("architecture", "—"),
                      "Cores / Threads", sys_data.get("cpu_cores_threads", "—"))
        cpu_cache = sys_data.get("cpu_cache", "—")
        if cpu_cache and cpu_cache != "—":
            _add_single_row(cpu_frame, "CPU Cache", cpu_cache)

        cpu_u = get_realtime_cpu_usage()
        cpu_t = get_realtime_cpu_temp()
        cpu_t_disp = f"{cpu_t} °C" if cpu_t and cpu_t > 0 else "—"
        _add_dual_row(cpu_frame, "CPU Load", cpu_u, "CPU Temperature", cpu_t_disp,
                      live_key1="sys_cpu_usage", live_key2="sys_cpu_temp")
        self.sys_content_box.append(cpu_frame)

        # ── Section 4: Memory & Storage ────────────────────────────────
        mem_frame = _make_section("Memory & Storage", "drive-harddisk-symbolic")
        ram_tot = sys_data.get("ram", "—")
        ram_u = get_realtime_ram_usage()
        _add_dual_row(mem_frame, "Total RAM", ram_tot, "RAM Usage", ram_u,
                      live_key2="sys_ram_usage")
        disk_cap = sys_data.get("disk_capacity", "—")
        if disk_cap and disk_cap != "—":
            _add_single_row(mem_frame, "Storage", disk_cap)
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
        self._update_sensors()

    def _on_gpu_selected(self, dropdown, _pspec):
        idx = dropdown.get_selected()
        if 0 <= idx < len(self.gpus):
            self.selected_gpu_idx = idx
            self._refresh_graphics_card_content()
            self._update_sensors()
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
        display = Gdk.Display.get_default()
        if hasattr(self, '_css_provider') and self._css_provider and display:
            try:
                Gtk.StyleContext.remove_provider_for_display(display, self._css_provider)
            except Exception:
                pass
            self._css_provider = None
