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
SummaryViewer.py
----------------
Builds the "Summary" overview tab — a GPU Caps Viewer-style single-window
snapshot of every detected GPU subsystem (Vulkan, OpenGL, OpenCL, VDPAU,
Vulkan Video) plus system information.

Data is read from files already written by the parallel probe stage in
gpu_viewer.py, so no extra subprocess calls are needed for most fields.
"""

import re
import os
import glob
import subprocess
import threading

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib, GdkPixbuf, Pango

import const
import Filenames
from Common import getLogo, getGpuImage, get_gpu_stats, fetchContentsFromCommand


# ---------------------------------------------------------------------------
# Data-gathering helpers (all run in a background thread)
# ---------------------------------------------------------------------------

def _parse_vulkan(results: dict) -> dict:
    """Return key Vulkan fields from the vulkaninfo output file."""
    data = {
        "supported": results.get("vulkan", False),
        "devices": [],
    }
    if not data["supported"]:
        return data

    try:
        with open(Filenames.vulkaninfo_output_file, "r") as f:
            content = f.read()
    except Exception:
        return data

    # Parse each GPU block: GPU0, GPU1 …
    gpu_blocks = re.split(r'\nGPU\d+:', "\n" + content)
    # gpu_blocks[0] is the preamble (instance version etc.)
    # gpu_blocks[1..] are per-device blocks

    instance_version = ""
    m = re.search(r'Instance Version\s*=\s*(\S+)', content)
    if m:
        instance_version = m.group(1)

    for block in gpu_blocks[1:]:
        device_name = ""
        api_version = ""
        driver_name = ""
        driver_version = ""
        device_type = ""
        formats_count = 0
        extensions_count = 0

        for line in block.splitlines():
            stripped = line.strip()
            if stripped.startswith("deviceName"):
                device_name = stripped.split("=", 1)[-1].strip()
            elif stripped.startswith("apiVersion"):
                raw = stripped.split("=", 1)[-1].strip()
                # Convert packed integer if it looks like one
                if re.match(r'^\d+$', raw):
                    try:
                        v = int(raw)
                        major = v >> 22
                        minor = (v >> 12) & 0x3FF
                        patch = v & 0xFFF
                        api_version = f"{major}.{minor}.{patch}"
                    except Exception:
                        api_version = raw
                else:
                    api_version = raw
            elif stripped.startswith("driverName"):
                driver_name = stripped.split("=", 1)[-1].strip()
            elif stripped.startswith("driverVersion"):
                raw = stripped.split("=", 1)[-1].strip()
                if re.match(r'^\d+$', raw):
                    try:
                        v = int(raw)
                        major = v >> 22
                        minor = (v >> 12) & 0x3FF
                        patch = v & 0xFFF
                        driver_version = f"{major}.{minor}.{patch}"
                    except Exception:
                        driver_version = raw
                else:
                    driver_version = raw
            elif stripped.startswith("deviceType"):
                device_type = stripped.split("=", 1)[-1].strip()
            elif "Formats:" in stripped and "count" in stripped:
                # Count formats in this GPU block
                m = re.search(r'count\s*=\s*(\d+)', stripped)
                if m:
                    formats_count += int(m.group(1))
            elif stripped.startswith("VK_") and "extension" in stripped.lower():
                # Count extensions in this GPU block
                extensions_count += 1

        if device_name:
            # Extract video profiles specifically from this GPU block
            video_profiles = set()
            matches = re.findall(r'VIDEO_CODEC_OPERATION_(\w+)_BIT_KHR', block)
            for match in matches:
                codec_name = match.replace("DECODE_", "").replace("ENCODE_", "")
                if codec_name:
                    video_profiles.add(codec_name)
            decode_matches = re.findall(r'VK_KHR_video_decode_(\w+)', block)
            for codec in decode_matches:
                if codec.lower() in ("av1", "h264", "h265", "vp8", "vp9"):
                    video_profiles.add(codec.upper())

            data["devices"].append({
                "name": device_name,
                "api_version": api_version,
                "driver_name": driver_name,
                "driver_version": driver_version,
                "device_type": device_type,
                "formats_count": formats_count,
                "extensions_count": extensions_count,
                "video_profiles": sorted(list(video_profiles)),
            })

    data["instance_version"] = instance_version
    return data


def _count_vulkan_formats(content: str) -> int:
    total = 0
    for match in re.findall(r'Formats:\s*count\s*=\s*(\d+)', content):
        total += int(match)
    return total


def _parse_opengl(results: dict) -> dict:
    """Return key OpenGL fields via glxinfo -B (re-using glxinfo.txt if possible)."""
    data = {
        "supported": results.get("opengl", False),
        "renderer": "",
        "vendor": "",
        "version": "",
        "shading_language_version": "",
        "es_version": "",
        "egl_version": "",
    }
    if not data["supported"]:
        return data

    try:
        # Try to use the already-written glxinfo file first
        lines = []
        if os.path.exists(Filenames.opengl_outpuf_file):
            with open(Filenames.opengl_outpuf_file, "r") as f:
                lines = f.readlines()
        # If the file is empty / too small, fall back to glxinfo -B
        if len(lines) < 5:
            lines = fetchContentsFromCommand("glxinfo -B 2>/dev/null")
    except Exception:
        return data

    extensions, fbconfig_count = _count_opengl_extensions_and_fbconfig(lines)
    data["extensions_count"] = len(extensions)
    data["fbconfig_count"] = fbconfig_count

    for line in lines:
        line = line.strip()
        if line.startswith("OpenGL renderer string:"):
            data["renderer"] = line.split(":", 1)[1].strip()
        elif line.startswith("OpenGL vendor string:"):
            data["vendor"] = line.split(":", 1)[1].strip()
        elif line.startswith("OpenGL version string:"):
            data["version"] = line.split(":", 1)[1].strip()
        elif line.startswith("OpenGL shading language version string:"):
            data["shading_language_version"] = line.split(":", 1)[1].strip()
        elif line.startswith("OpenGL ES profile version string:"):
            data["es_version"] = line.split(":", 1)[1].strip()
        elif "EGL" in line and "version" in line.lower():
            # Try to extract EGL version
            if "EGL version:" in line:
                data["egl_version"] = line.split(":", 1)[1].strip()

    return data


def _parse_opencl(results: dict) -> dict:
    """Return key OpenCL fields from the clinfo output file."""
    data = {
        "supported": results.get("opencl", False),
        "platforms": [],
    }
    if not data["supported"]:
        return data

    try:
        with open(Filenames.opencl_output_file, "r") as f:
            content = f.read()
    except Exception:
        return data

    # Quick pass: just grab Platform Name + first Device Name + Device Version + extensions
    current_platform = None
    current_device = None
    mode = "START"
    in_platform_extensions = False
    in_device_extensions = False

    for line in content.splitlines():
        if not line.strip():
            if in_platform_extensions or in_device_extensions:
                in_platform_extensions = False
                in_device_extensions = False
            continue
        indent = len(line) - len(line.lstrip())
        content_line = line.strip()

        if indent == 0:
            if "Number of platforms" in content_line:
                mode = "PLATFORM"
            elif "Number of devices" in content_line:
                mode = "DEVICE"
                current_device = None
            elif "ICD loader" in content_line or "NULL platform" in content_line:
                mode = "STOP"
            in_platform_extensions = False
            in_device_extensions = False
            continue

        if mode in ("STOP", "START"):
            continue

        if "  " in content_line:
            parts = re.split(r'\s{2,}', content_line, maxsplit=1)
            key = parts[0].strip()
            value = parts[1].strip() if len(parts) > 1 else ""
        else:
            key = content_line
            value = ""

        if indent == 2:
            if key == "Platform Name":
                current_platform = {"name": value, "devices": [], "extensions_count": 0}
                data["platforms"].append(current_platform)
                current_device = None
                in_platform_extensions = False
                in_device_extensions = False
            elif key == "Platform Extensions":
                in_platform_extensions = True
                in_device_extensions = False
                continue
            elif mode == "DEVICE" and current_platform:
                if key == "Device Name":
                    current_device = {
                        "name": value,
                        "version": "",
                        "opencl_c_version": "",
                        "driver_version": "",
                        "extensions_count": 0,
                    }
                    current_platform["devices"].append(current_device)
                    in_device_extensions = False
                elif key == "Device Extensions":
                    in_device_extensions = True
                    in_platform_extensions = False
                    continue
                elif current_device:
                    if key == "Device Version" or key == "Version":
                        current_device["version"] = value
                    elif "OpenCL C" in key and "Version" in key:
                        current_device["opencl_c_version"] = value
                    elif key == "Driver Version":
                        current_device["driver_version"] = value
            elif in_platform_extensions and current_platform:
                # Count platform extensions
                if re.match(r'^cl_\w+', key):
                    current_platform["extensions_count"] += 1
            elif in_device_extensions and current_device:
                # Count device extensions
                if re.match(r'^cl_\w+', key):
                    current_device["extensions_count"] += 1

    # Filter platforms to keep only those with devices
    data["platforms"] = [p for p in data["platforms"] if p.get("devices")]
    if not data["platforms"]:
        data["supported"] = False

    return data


def _count_opengl_extensions_and_fbconfig(lines: list) -> tuple[set, int]:
    extensions = set()
    fbconfig_count = 0
    in_extensions = False
    in_fbconfig = False
    fbconfig_started = False

    for line in lines:
        stripped = line.strip()
        if "OpenGL extensions:" in stripped:
            in_extensions = True
            continue

        if in_extensions and stripped == "":
            in_extensions = False

        if in_extensions:
            extensions.update(re.findall(r'\bGLX?_[A-Za-z0-9_]+\b', stripped))
            continue

        if "GLXFBConfigs" in stripped:
            in_fbconfig = True
            fbconfig_started = False
            continue

        if in_fbconfig:
            if re.match(r'^[-=]{2,}', stripped):
                fbconfig_started = True
                continue
            if not fbconfig_started:
                continue
            if stripped == "":
                break
            fbconfig_count += 1

    return extensions, fbconfig_count


def _parse_gpui_stats(results: dict) -> dict:
    data = {
        "supported": False,
        "mem_used": None,
        "mem_total": None,
        "usage": None,
        "temp": None,
        "clock_current": None,
        "clock_max": None,
        "fan_speed": None,
        "power_usage": None,
    }

    try:
        # Try multiple device path patterns
        card_paths = sorted(glob.glob("/sys/class/drm/card*/device"))
        if not card_paths:
            card_paths = sorted(glob.glob("/sys/class/drm/card*"))
        
        if card_paths:
            device_id = None
            # Try to read device ID from various possible paths
            for card_path in card_paths:
                device_file = f"{card_path}/device"
                if not os.path.exists(device_file):
                    device_file = f"{card_path}/../../device"
                if os.path.exists(device_file):
                    try:
                        with open(device_file, "r") as f:
                            device_id = int(f.read().strip(), 16)
                        break
                    except (ValueError, OSError):
                        continue
            
            if device_id is None:
                # Fallback: try reading from vendor/device files
                for card_path in card_paths:
                    vendor_file = f"{card_path}/vendor"
                    if os.path.exists(vendor_file):
                        try:
                            with open(vendor_file, "r") as f:
                                vendor = int(f.read().strip(), 16)
                            device_file = f"{card_path}/device"
                            with open(device_file, "r") as f:
                                dev_id = int(f.read().strip(), 16)
                            device_id = (vendor << 16) | dev_id
                            break
                        except (ValueError, OSError):
                            continue
            
            if device_id is not None:
                num_devices = len(card_paths)
                stats = get_gpu_stats(device_id, num_devices)
                if stats:
                    data.update(stats)
                    data["supported"] = True
    except Exception:
        pass

    return data


def _parse_vdpau(results: dict) -> dict:
    """Return key VDPAU fields from the vdpauinfo output file."""
    data = {
        "supported": results.get("vdpau", False),
        "api_version": "",
        "renderer": "",
    }
    if not data["supported"]:
        return data

    try:
        with open(Filenames.vdpauinfo_output_file, "r") as f:
            lines = f.readlines()
    except Exception:
        return data

    for line in lines:
        line_s = line.strip()
        if "API version:" in line_s:
            data["api_version"] = line_s.split(":", 1)[1].strip()
        elif "Information string:" in line_s:
            data["renderer"] = line_s.split(":", 1)[1].strip()

    return data


def _parse_vulkan_video(results: dict) -> dict:
    """Parse supported Vulkan video profiles from vulkaninfo output."""
    data = {
        "supported": results.get("vulkan_video", False),
        "profiles": [],
    }
    if not data["supported"]:
        return data
    
    try:
        with open(Filenames.vulkaninfo_output_file, "r") as f:
            content = f.read()
    except Exception:
        return data
    
    # Extract video codec operations
    profiles_set = set()
    
    # Pattern 1: VIDEO_CODEC_OPERATION_* identifiers (primary source)
    matches = re.findall(r'VIDEO_CODEC_OPERATION_(\w+)_BIT_KHR', content)
    for match in matches:
        # Extract codec name (e.g., "DECODE_AV1" -> "AV1")
        codec_name = match.replace("DECODE_", "").replace("ENCODE_", "")
        if codec_name and codec_name not in profiles_set:
            profiles_set.add(codec_name)
    
    # Pattern 2: VK_KHR_video_decode_* extensions (secondary source for completeness)
    decode_matches = re.findall(r'VK_KHR_video_decode_(\w+)', content)
    
    for codec in decode_matches:
        # Only add standard codec names, exclude 'queue'
        if codec.lower() in ("av1", "h264", "h265", "vp8", "vp9"):
            profiles_set.add(codec.upper())
    
    data["profiles"] = sorted(list(profiles_set))
    return data


def _parse_system() -> dict:
    """Return basic system info (OS, CPU, RAM, Kernel, Desktop)."""
    info = {
        "os": "",
        "cpu": "",
        "ram": "",
        "kernel": "",
        "desktop": "",
        "windowing": "",
    }
    try:
        result = subprocess.run(
            ["lsb_release", "-d", "-r", "-c"],
            capture_output=True, text=True, timeout=3
        )
        for line in result.stdout.splitlines():
            if line.startswith("Description:"):
                info["os"] = line.split(":", 1)[1].strip()
    except Exception:
        pass

    try:
        result = subprocess.run(
            "LC_ALL=C lscpu | grep -E 'Model name'",
            shell=True, capture_output=True, text=True, timeout=3
        )
        for line in result.stdout.splitlines():
            if "Model name" in line:
                info["cpu"] = line.split(":", 1)[1].strip()
                break
    except Exception:
        pass

    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    info["ram"] = f"{kb / (1024*1024):.1f} GB"
                    break
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["uname", "-r"], capture_output=True, text=True, timeout=2
        )
        info["kernel"] = result.stdout.strip()
    except Exception:
        pass

    info["desktop"] = os.environ.get("XDG_CURRENT_DESKTOP", "")
    info["windowing"] = os.environ.get("XDG_SESSION_TYPE", "")

    return info


def _gather_all(results: dict) -> dict:
    """Run all parsers (background thread safe)."""
    return {
        "vulkan": _parse_vulkan(results),
        "opengl": _parse_opengl(results),
        "opencl": _parse_opencl(results),
        "vdpau": _parse_vdpau(results),
        "vulkan_video": _parse_vulkan_video(results),
        "gpui_stats": _parse_gpui_stats(results),
        "system": _parse_system(),
    }


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------

def _make_action_row(title: str, subtitle: str) -> Adw.ActionRow:
    row = Adw.ActionRow()
    row.set_title(title)
    row.set_subtitle(subtitle if subtitle else "—")
    row.set_title_selectable(True)
    row.set_subtitle_selectable(True)
    
    # Add icon prefix
    icon_name = _get_icon_name(title)
    try:
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_pixel_size(16)
        row.add_prefix(icon)
    except Exception:
        pass
    
    return row


def _make_status_badge(text: str, good: bool) -> Gtk.Label:
    badge = Gtk.Label(label=text)
    badge.set_valign(Gtk.Align.CENTER)
    badge.add_css_class("pill" if good else "error")
    badge.add_css_class("caption")
    if good:
        badge.add_css_class("success")
    return badge


def _nav_button(label: str, page_name: str, app) -> Gtk.Button:
    btn = Gtk.Button(label=label)
    btn.add_css_class("flat")
    btn.add_css_class("suggested-action")
    btn.set_valign(Gtk.Align.CENTER)
    def on_clicked(_):
        if hasattr(app, "open_tab"):
            app.open_tab(page_name)
    btn.connect("clicked", on_clicked)
    return btn


def _section_title(text: str) -> Gtk.Label:
    lbl = Gtk.Label(label=text)
    lbl.add_css_class("title-4")
    lbl.set_halign(Gtk.Align.START)
    lbl.set_margin_top(16)
    lbl.set_margin_bottom(4)
    lbl.set_margin_start(4)
    return lbl


def _get_icon_name(field_name: str) -> str:
    """Return appropriate icon name for a field."""
    field_lower = field_name.lower()
    icon_map = {
        "operating system": "system-run-symbolic",
        "processor": "cpu-symbolic",
        "system ram": "memory-symbolic",
        "kernel": "system-symbolic",
        "desktop": "preferences-desktop-appearance-symbolic",
        "windowing system": "application-x-executable-symbolic",
        "device": "gpu-symbolic",
        "driver": "package-symbolic",
        "api version": "document-properties-symbolic",
        "driver version": "application-vnd.document-symbolic",
        "device type": "computer-symbolic",
        "instance version": "system-information-symbolic",
        "vulkan formats": "preferences-system-time-symbolic",
        "extensions": "plugin-symbolic",
        "video memory": "media-playback-start-symbolic",
        "gpu usage": "media-flash-symbolic",
        "temperature": "thermometer-symbolic",
        "gpu clock": "media-seek-forward-symbolic",
        "power": "battery-symbolic",
        "fan speed": "fan-symbolic",
        "renderer": "gpu-symbolic",
        "vendor": "organization-symbolic",
        "opengl version": "preferences-system-symbolic",
        "glsl version": "text-editor-symbolic",
        "egl version": "system-search-symbolic",
        "platform": "system-symbolic",
        "opencl version": "document-symbolic",
        "status": "emblem-ok-symbolic",
    }
    
    for key, icon in icon_map.items():
        if key in field_lower:
            return icon
    
    return "application-x-executable-symbolic"


# ---------------------------------------------------------------------------
# Card builders
# ---------------------------------------------------------------------------

def _make_card(title: str, icon_name: str, rows: list,
               nav_page: str | None, app,
               supported: bool = True,
               row_widgets_out: dict = None) -> Gtk.Box:
    """
    Create a styled card widget (an Adw.PreferencesGroup wrapped in a frame).
    `rows` is a list of (title, subtitle) tuples.
    """
    # Outer frame gives the card boundary
    frame = Gtk.Frame()
    frame.set_margin_start(0)
    frame.set_margin_end(0)
    frame.set_margin_top(0)
    frame.set_margin_bottom(0)

    card_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    frame.set_child(card_box)

    # ---------- Header bar ----------
    header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    header.set_margin_start(12)
    header.set_margin_end(12)
    header.set_margin_top(10)
    header.set_margin_bottom(10)

    # Try to load the subsystem logo icon
    try:
        icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            icon_name, 28, 28, True
        )
        icon_img = Gtk.Picture.new_for_pixbuf(icon_pixbuf)
        icon_img.set_size_request(28, 28)
        header.append(icon_img)
    except Exception:
        # Fallback: named icon
        icon_img = Gtk.Image.new_from_icon_name("application-x-executable-symbolic")
        icon_img.set_pixel_size(24)
        header.append(icon_img)

    title_lbl = Gtk.Label(label=title)
    title_lbl.add_css_class("title-3")
    title_lbl.set_halign(Gtk.Align.START)
    title_lbl.set_hexpand(True)
    header.append(title_lbl)

    # Status badge
    if supported:
        badge = _make_status_badge("Detected", True)
    else:
        badge = _make_status_badge("Not detected", False)
    header.append(badge)

    # Navigation button
    if nav_page and supported and app:
        btn = _nav_button("Open →", nav_page, app)
        header.append(btn)

    card_box.append(header)

    # Separator between header and rows
    sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    card_box.append(sep)

    # ---------- Property rows ----------
    if not supported:
        no_row = Adw.ActionRow()
        no_row.set_title("Status")
        no_row.set_subtitle("This subsystem was not detected on your system.")
        card_box.append(no_row)
    else:
        for row_title, row_subtitle in rows:
            row = _make_action_row(row_title, row_subtitle)
            card_box.append(row)
            if row_widgets_out is not None:
                row_widgets_out[row_title] = row

    # Dim the whole card if not supported
    if not supported:
        frame.set_sensitive(False)
        frame.set_opacity(0.55)

    return frame


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def create_summary_page(app, results: dict) -> Gtk.Widget:
    """
    Return a widget for the "Summary" tab.  Data gathering runs in a
    background thread; a spinner is shown until it completes.

    Parameters
    ----------
    app     : the GPUViewerApp instance (has .view_stack)
    results : the dict from _probe_and_build_tabs  {vulkan: bool, …}
    """
    outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    outer.set_vexpand(True)
    outer.set_hexpand(True)

    device_id_cache = [None]
    num_devices_cache = [0]
    
    # Pre-calculate device information once (fast, no processes spawned)
    try:
        card_paths = sorted(glob.glob("/sys/class/drm/card*/device"))
        if not card_paths:
            card_paths = sorted(glob.glob("/sys/class/drm/card*"))
        if card_paths:
            num_devices_cache[0] = len(card_paths)
            for card_path in card_paths:
                device_file = f"{card_path}/device"
                if not os.path.exists(device_file):
                    device_file = f"{card_path}/../../device"
                if os.path.exists(device_file):
                    try:
                        with open(device_file, "r") as f:
                            device_id_cache[0] = int(f.read().strip(), 16)
                        break
                    except (ValueError, OSError):
                        continue
    except Exception:
        pass

    # ---- Loading state ----
    loading_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    loading_box.set_valign(Gtk.Align.CENTER)
    loading_box.set_halign(Gtk.Align.CENTER)
    loading_box.set_vexpand(True)

    spinner = Gtk.Spinner()
    spinner.set_size_request(48, 48)
    spinner.start()
    loading_lbl = Gtk.Label(label="Gathering summary…")
    loading_lbl.add_css_class("dim-label")
    loading_box.append(spinner)
    loading_box.append(loading_lbl)
    outer.append(loading_box)

    def _bg_worker():
        data = _gather_all(results)
        GLib.idle_add(_build_ui, data)

    def _build_ui(data: dict):
        spinner.stop()
        outer.remove(loading_box)

        # Master scroll container
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        # Use a FlowBox for multi-column layout
        flow_box = Gtk.FlowBox()
        flow_box.set_homogeneous(False)
        flow_box.set_min_children_per_line(1)
        flow_box.set_max_children_per_line(3)  # 2-3 columns
        flow_box.set_selection_mode(Gtk.SelectionMode.NONE)
        flow_box.set_margin_top(12)
        flow_box.set_margin_bottom(24)
        flow_box.set_margin_start(12)
        flow_box.set_margin_end(12)
        flow_box.set_row_spacing(12)
        flow_box.set_column_spacing(12)
        
        scroll.set_child(flow_box)

        view_stack = getattr(app, "view_stack", None)

        # ── System Information ───────────────────────────────────────────
        sys_data = data["system"]
        sys_rows = []
        if sys_data.get("os"):
            sys_rows.append(("Operating System", sys_data["os"]))
        if sys_data.get("cpu"):
            sys_rows.append(("Processor", sys_data["cpu"]))
        if sys_data.get("ram"):
            sys_rows.append(("System RAM", sys_data["ram"]))
        if sys_data.get("kernel"):
            sys_rows.append(("Kernel", sys_data["kernel"]))
        if sys_data.get("desktop"):
            sys_rows.append(("Desktop", sys_data["desktop"]))
        if sys_data.get("windowing"):
            sys_rows.append(("Windowing System", sys_data["windowing"]))

        if sys_rows:
            sys_card = _make_card(
                "System",
                "../Images/about-us.png",
                sys_rows,
                nav_page=None,   # no detail tab for system info
                app=None,
                supported=True,
            )
            sys_card.set_size_request(300, -1)
            flow_box.append(sys_card)

        gpui_data = data["gpui_stats"]
        stats_widgets = {}
        if gpui_data["supported"]:
            stats_rows = []
            if gpui_data.get("mem_used") is not None and gpui_data.get("mem_total") is not None:
                stats_rows.append(("Video Memory", f"{gpui_data['mem_used']} MB / {gpui_data['mem_total']} MB"))
            if gpui_data.get("usage") is not None and gpui_data["usage"] >= 0:
                stats_rows.append(("GPU Usage", f"{gpui_data['usage']} %"))
            if gpui_data.get("temp") is not None:
                stats_rows.append(("Temperature", f"{gpui_data['temp']} °C"))
            if gpui_data.get("clock_current") is not None and gpui_data.get("clock_max") is not None:
                stats_rows.append(("GPU Clock", f"{gpui_data['clock_current']} / {gpui_data['clock_max']} MHz"))
            elif gpui_data.get("clock_current") is not None:
                stats_rows.append(("GPU Clock", f"{gpui_data['clock_current']} MHz"))
            if gpui_data.get("power_usage") is not None and gpui_data["power_usage"] > 0:
                stats_rows.append(("Power", f"{gpui_data['power_usage']} W"))
            if gpui_data.get("fan_speed") is not None and gpui_data["fan_speed"] >= 0:
                stats_rows.append(("Fan Speed", f"{gpui_data['fan_speed']} %"))
            if not stats_rows:
                stats_rows.append(("Status", "GPU stats are available, but no numeric values could be read."))
            stats_card = _make_card(
                "GPU Statistics",
                "../Images/about-us.png",
                stats_rows,
                nav_page=None,
                app=None,
                supported=True,
                row_widgets_out=stats_widgets
            )
            stats_card.set_size_request(300, -1)
            flow_box.append(stats_card)
        else:
            stats_card = _make_card(
                "GPU Statistics",
                "../Images/about-us.png",
                [],
                nav_page=None,
                app=None,
                supported=False,
            )
            stats_card.set_size_request(300, -1)
            flow_box.append(stats_card)

        # ── Vulkan ───────────────────────────────────────────────────────
        vk_data = data["vulkan"]
        if vk_data["supported"] and vk_data.get("devices"):
            for i, dev in enumerate(vk_data["devices"]):
                rows = []
                if dev.get("name"):
                    rows.append(("Device", dev["name"]))
                if dev.get("api_version"):
                    rows.append(("API Version", dev["api_version"]))
                if dev.get("driver_name"):
                    rows.append(("Driver", dev["driver_name"]))
                if dev.get("driver_version"):
                    rows.append(("Driver Version", dev["driver_version"]))
                if dev.get("device_type"):
                    rows.append(("Device Type", dev["device_type"]))
                if vk_data.get("instance_version"):
                    rows.append(("Instance Version", vk_data["instance_version"]))
                if dev.get("formats_count") is not None and dev.get("formats_count") > 0:
                    rows.append(("Vulkan Formats", str(dev["formats_count"])))
                if dev.get("extensions_count") is not None and dev.get("extensions_count") > 0:
                    rows.append(("Extensions", str(dev["extensions_count"])))
                if dev.get("video_profiles"):
                    rows.append(("Video Profiles", ", ".join(dev["video_profiles"])))

                label = f"Vulkan" if len(vk_data["devices"]) == 1 else f"Vulkan – GPU {i}"
                card = _make_card(
                    label,
                    "../Images/Vulkan.png",
                    rows,
                    nav_page="page1",
                    app=app,
                    supported=True,
                )
                card.set_size_request(300, -1)
                flow_box.append(card)
        else:
            card = _make_card(
                "Vulkan", "../Images/Vulkan.png",
                [], nav_page=None, app=None, supported=False,
            )
            card.set_size_request(300, -1)
            flow_box.append(card)

        # ── OpenGL ───────────────────────────────────────────────────────
        gl_data = data["opengl"]
        if gl_data["supported"] and gl_data.get("renderer"):
            rows = []
            if gl_data.get("renderer"):
                rows.append(("Renderer", gl_data["renderer"]))
            if gl_data.get("vendor"):
                rows.append(("Vendor", gl_data["vendor"]))
            if gl_data.get("version"):
                rows.append(("OpenGL Version", gl_data["version"]))
            if gl_data.get("shading_language_version"):
                rows.append(("GLSL Version", gl_data["shading_language_version"]))
            if gl_data.get("es_version"):
                rows.append(("OpenGL ES Version", gl_data["es_version"]))
            if gl_data.get("egl_version"):
                rows.append(("EGL Version", gl_data["egl_version"]))
            if gl_data.get("extensions_count") is not None:
                rows.append(("Extension Count", str(gl_data["extensions_count"])))
            if gl_data.get("fbconfig_count") is not None:
                rows.append(("GLX FBConfig Count", str(gl_data["fbconfig_count"])))
            card = _make_card(
                "OpenGL", "../Images/OpenGL.png",
                rows, nav_page="page2", app=app, supported=True,
            )
            card.set_size_request(300, -1)
            flow_box.append(card)
        else:
            card = _make_card(
                "OpenGL", "../Images/OpenGL.png",
                [], nav_page=None, app=None, supported=False,
            )
            card.set_size_request(300, -1)
            flow_box.append(card)

        # ── OpenCL ───────────────────────────────────────────────────────
        cl_data = data["opencl"]
        if cl_data["supported"] and cl_data.get("platforms"):
            for platform in cl_data["platforms"]:
                rows = [("Platform", platform["name"])]
                if platform.get("extensions_count", 0) > 0:
                    rows.append(("Platform Extensions", str(platform["extensions_count"])))
                for dev in platform.get("devices", [])[:3]:  # max 3 devices shown
                    if dev.get("name"):
                        rows.append(("Device", dev["name"]))
                    if dev.get("version"):
                        rows.append(("OpenCL Version", dev["version"]))
                    if dev.get("driver_version"):
                        rows.append(("Driver Version", dev["driver_version"]))
                    if dev.get("extensions_count", 0) > 0:
                        rows.append(("Device Extensions", str(dev["extensions_count"])))
                card = _make_card(
                    f"OpenCL – {platform['name']}",
                    "../Images/OpenCL.svg",
                    rows,
                    nav_page="opencl_page",
                    app=app,
                    supported=True,
                )
                card.set_size_request(300, -1)
                flow_box.append(card)
        else:
            card = _make_card(
                "OpenCL",
                "../Images/OpenCL.svg",
                [], nav_page=None, app=None, supported=False,
            )
            card.set_size_request(300, -1)
            flow_box.append(card)

        # ── VDPAU ────────────────────────────────────────────────────────
        vd_data = data["vdpau"]
        if vd_data["supported"]:
            rows = []
            if vd_data.get("api_version"):
                rows.append(("API Version", vd_data["api_version"]))
            if vd_data.get("renderer"):
                rows.append(("Renderer", vd_data["renderer"]))
            card = _make_card(
                "VDPAU",
                "../Images/vdpauinfo.png",
                rows,
                nav_page="vdpau_page",
                app=app,
                supported=True,
            )
        else:
            card = _make_card(
                "VDPAU", "../Images/vdpauinfo.png",
                [], nav_page=None, app=None, supported=False,
            )
        card.set_size_request(300, -1)
        flow_box.append(card)

        outer.append(scroll)

        # Periodic statistics update
        def update_stats_callback():
            if not outer.get_mapped():
                return True
                
            def fetch_stats():
                try:
                    dev_id = device_id_cache[0]
                    num_devs = num_devices_cache[0]
                    if dev_id is not None:
                        stats = get_gpu_stats(dev_id, num_devs)
                        
                        def apply_updates():
                            if stats:
                                if "Video Memory" in stats_widgets and stats.get("mem_used") is not None and stats.get("mem_total") is not None:
                                    stats_widgets["Video Memory"].set_subtitle(f"{stats['mem_used']} MB / {stats['mem_total']} MB")
                                if "GPU Usage" in stats_widgets and stats.get("usage") is not None:
                                    stats_widgets["GPU Usage"].set_subtitle(f"{stats['usage']} %")
                                if "Temperature" in stats_widgets and stats.get("temp") is not None:
                                    stats_widgets["Temperature"].set_subtitle(f"{stats['temp']} °C")
                                if "GPU Clock" in stats_widgets:
                                    if stats.get("clock_current") is not None and stats.get("clock_max") is not None:
                                        stats_widgets["GPU Clock"].set_subtitle(f"{stats['clock_current']} / {stats['clock_max']} MHz")
                                    elif stats.get("clock_current") is not None:
                                        stats_widgets["GPU Clock"].set_subtitle(f"{stats['clock_current']} MHz")
                                if "Power" in stats_widgets and stats.get("power_usage") is not None:
                                    stats_widgets["Power"].set_subtitle(f"{stats['power_usage']} W")
                                if "Fan Speed" in stats_widgets and stats.get("fan_speed") is not None:
                                    stats_widgets["Fan Speed"].set_subtitle(f"{stats['fan_speed']} %")
                            return False
                            
                        GLib.idle_add(apply_updates)
                except Exception as e:
                    print(f"Error updating real-time stats: {e}")
                    
            threading.Thread(target=fetch_stats, daemon=True).start()
            return True
            
        timeout_id = GLib.timeout_add(1000, update_stats_callback)
        
        def on_destroy(widget):
            GLib.source_remove(timeout_id)
        outer.connect("destroy", on_destroy)

        return False  # GLib.idle_add must return False to not repeat

    threading.Thread(target=_bg_worker, daemon=True).start()
    return outer
