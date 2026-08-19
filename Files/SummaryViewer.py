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
import shutil

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib, GdkPixbuf, Pango, Gdk

import const
import Filenames
from Common import getLogo, getGpuImage, get_gpu_stats, get_gpu_stats_for_index, fetchContentsFromCommand
# Try to reuse the robust clinfo parser when available
try:
    from OpenCL import ClinfoParser
except Exception:
    ClinfoParser = None


# ---------------------------------------------------------------------------
# Data-gathering helpers (all run in a background thread)
# ---------------------------------------------------------------------------

def _normalise_video_codec_name(name: str) -> str:
    """Return a display-friendly codec name such as H.264 or H.265."""
    if not name:
        return ""
    key = name.strip().upper().replace("HEVC", "H265").replace("AVC", "H264")
    _MAP = {"H264": "H.264", "H265": "H.265", "AV1": "AV1", "VP8": "VP8", "VP9": "VP9"}
    return _MAP.get(key, key)


def _parse_vulkan(results: dict) -> dict:
    """Return key Vulkan fields from the vulkaninfo output file."""
    data = {
        "supported": results.get("vulkan", False),
        "devices": [],
        "instance_extensions_count": 0,
        "instance_layers_count": 0,
        "instance_version": "",
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

    for block in gpu_blocks[1:]:
        device_name = ""
        api_version = ""
        driver_name = ""
        driver_version = ""
        device_type = ""
        formats_count = 0
        extensions_count = 0
        memory_types_count = 0
        memory_heaps_count = 0
        queue_count = 0
        pipelineCacheUUID = ""
        vendor_id = ""
        device_id = ""
        driver_info = ""
        device_uuid = ""
        driver_uuid = ""
        conformance_version = ""
        
        in_conformance = False
        conf_major = None
        conf_minor = None
        conf_subminor = None
        conf_patch = None

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
            elif stripped.startswith("pipelineCacheUUID"):
                pipelineCacheUUID = stripped.split("=", 1)[-1].strip()
            elif stripped.startswith("vendorID"):
                vendor_id = stripped.split("=", 1)[-1].strip()
            elif stripped.startswith("deviceID"):
                device_id = stripped.split("=", 1)[-1].strip()
            elif stripped.startswith("driverInfo"):
                driver_info = stripped.split("=", 1)[-1].strip()
            elif stripped.startswith("deviceUUID"):
                device_uuid = stripped.split("=", 1)[-1].strip()
            elif stripped.startswith("driverUUID"):
                driver_uuid = stripped.split("=", 1)[-1].strip()
            elif stripped.startswith("conformanceVersion:"):
                in_conformance = True
                continue
            elif stripped.startswith("VK_") and "extension" in stripped.lower():
                # Count extensions in this GPU block
                extensions_count += 1

            if in_conformance:
                if "=" in stripped:
                    k, v = stripped.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    if k == "major":
                        conf_major = v
                    elif k == "minor":
                        conf_minor = v
                    elif k == "subminor":
                        conf_subminor = v
                    elif k == "patch":
                        conf_patch = v
                else:
                    if stripped and not stripped.startswith(("major", "minor", "subminor", "patch")):
                        in_conformance = False

        if conf_major is not None and conf_minor is not None:
            conformance_version = f"{conf_major}.{conf_minor}"
            if conf_subminor is not None:
                conformance_version += f".{conf_subminor}"
            if conf_patch is not None:
                conformance_version += f".{conf_patch}"

        if device_name:
            video_decode_profiles = {}
            video_encode_profiles = {}

            def _record_profile(op_type: str, codec_name: str, count: int = 1):
                if not codec_name:
                    return
                normalised = _normalise_video_codec_name(codec_name)
                if not normalised:
                    return
                counts = video_decode_profiles if op_type == "DECODE" else video_encode_profiles
                if count is None or count <= 0:
                    count = 1
                counts[normalised] = counts.get(normalised, 0) + count

            placeholder_seen = False
            placeholder_items = re.findall(r'placeholder\s*=\s*(.*)', block, re.I)
            for item in placeholder_items:
                item = item.strip()
                if not item:
                    continue
                placeholder_seen = True
                match = re.search(r'(?i)\b([A-Za-z0-9.]+)\s+(Decode|Encode)\b', item)
                if match:
                    codec, op_type = match.groups()
                    _record_profile(op_type.upper(), codec, 1)

            if not placeholder_seen:
                seen_flags = set()
                for op_type, codec in re.findall(r'VIDEO_CODEC_OPERATION_(DECODE|ENCODE)_(\w+)_BIT_KHR', block):
                    key = (op_type.upper(), codec.upper())
                    if key in seen_flags:
                        continue
                    seen_flags.add(key)
                    _record_profile(op_type.upper(), codec, 1)

                for codec in re.findall(r'VK_KHR_video_decode_(\w+)', block):
                    if codec.lower() in ("av1", "h264", "h265", "vp8", "vp9"):
                        _record_profile("DECODE", codec, 1)

                for codec in re.findall(r'VK_KHR_video_encode_(\w+)', block):
                    if codec.lower() in ("av1", "h264", "h265", "vp8", "vp9"):
                        _record_profile("ENCODE", codec, 1)

            memory_types_count = len(re.findall(r'memoryTypes\s*\[\s*\d+\s*\]', block, re.I))
            memory_heaps_count = len(re.findall(r'memoryHeaps\s*\[\s*\d+\s*\]', block, re.I))
            queue_count = len(re.findall(r'queueProperties\s*\[\s*\d+\s*\]', block, re.I))

            decode_names = sorted(video_decode_profiles)
            encode_names = sorted(video_encode_profiles)
            data["devices"].append({
                "name": device_name,
                "api_version": api_version,
                "driver_name": driver_name,
                "driver_version": driver_version,
                "device_type": device_type,
                "formats_count": formats_count,
                "extensions_count": extensions_count,
                "memory_types_count": memory_types_count,
                "memory_heaps_count": memory_heaps_count,
                "queue_count": queue_count,
                "pipelineCacheUUID": pipelineCacheUUID,
                "video_profiles": sorted(set(decode_names) | set(encode_names)),
                "video_decode_profiles": decode_names,
                "video_encode_profiles": encode_names,
                "video_decode_profile_counts": dict(sorted(video_decode_profiles.items())),
                "video_encode_profile_counts": dict(sorted(video_encode_profiles.items())),
                "vendor_id": vendor_id,
                "device_id": device_id,
                "driver_info": driver_info,
                "device_uuid": device_uuid,
                "driver_uuid": driver_uuid,
                "conformance_version": conformance_version,
            })

        # Post-process: count supported formats by scanning 'Format Properties' section
        try:
            # Sum numeric "Formats: count = <N>" values found in the
            # supported 'Format Properties' section (stop at 'Unsupported Formats').
            in_formats = False
            formats_total = 0
            for line in block.splitlines():
                s = line.strip()
                if 'Format Properties' in s:
                    in_formats = True
                    continue
                if in_formats:
                    if 'Unsupported Formats' in s:
                        break
                    m = re.search(r'Formats:\s*count\s*=\s*(\d+)', s)
                    if m:
                        try:
                            formats_total += int(m.group(1))
                        except Exception:
                            continue
            formats_count = formats_total
            if data['devices']:
                data['devices'][-1]['formats_count'] = formats_count
        except Exception:
            pass

    instance_ext_match = re.search(r'Instance Extensions\s*:\s*count\s*=\s*(\d+)', content, re.I)
    instance_version_match = re.search(r'Vulkan Instance Version\s*:\s*([^\n]+)', content, re.I)
    if instance_version_match:
        data["instance_version"] = instance_version_match.group(1).strip()
    else:
        version_match = re.search(r'VK_API_VERSION_\d+_\d+', content)
        data["instance_version"] = version_match.group(0) if version_match else ""
    if instance_ext_match:
        data["instance_extensions_count"] = int(instance_ext_match.group(1))
    else:
        ext_section = re.search(r'Instance Extensions\s*:\s*(.*?)\n\n', content, re.S | re.I)
        if ext_section:
            data["instance_extensions_count"] = len(re.findall(r'VK_[A-Za-z0-9_]+', ext_section.group(1)))
        else:
            data["instance_extensions_count"] = len(re.findall(r'VK_[A-Za-z0-9_]+', content))

    instance_layers_section = re.search(r'Instance Layers\s*:\s*(.*?)\n\n', content, re.S | re.I)
    if instance_layers_section:
        data["instance_layers_count"] = len(re.findall(r'VK_LAYER_[A-Za-z0-9_]+', instance_layers_section.group(1)))
    else:
        data["instance_layers_count"] = len(re.findall(r'VK_LAYER_[A-Za-z0-9_]+', content))

    return data


def _count_vulkan_formats(content: str) -> int:
    total = 0
    for match in re.findall(r'Formats:\s*count\s*=\s*(\d+)', content):
        total += int(match)
    return total


def _parse_opengl(results: dict) -> dict:
    """Return key OpenGL fields via glxinfo -B (re-using glxinfo.txt if possible)."""
    data = {
        "supported": results.get("opengl") or results.get("egl", False),
        "renderer": "",
        "vendor": "",
        "version": "",
        "shading_language_version": "",
        "es_version": "",
        "es_shading_language_version": "",
        "egl_version": "",
        "glx_version": "",
        "extensions_count": 0,
        "es_extensions_count": 0,
        "glx_extension_count": 0,
        "egl_count": 0,
        "glx_visual_count": 0,
        "fbconfig_count": 0,
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

    count_data = _parse_glx_es_egl_counts(lines)
    data.update(count_data)

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
        elif line.startswith("OpenGL ES profile shading language version string:"):
            data["es_shading_language_version"] = line.split(":", 1)[1].strip()
        elif line.startswith("GLX version:"):
            data["glx_version"] = line.split(":", 1)[1].strip()
        elif "EGL" in line and "version" in line.lower():
            # Try to extract EGL version
            if "EGL version:" in line:
                data["egl_version"] = line.split(":", 1)[1].strip()

    # Try to gather EGL extension count from es2_info when available.
    try:
        es2_lines = fetchContentsFromCommand("es2_info 2>/dev/null")
        egl_entries = []
        in_extensions_section = False
        for line in es2_lines:
            if line.startswith("EGL_VERSION") and not data["egl_version"]:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    data["egl_version"] = parts[1].strip()
                continue

            if line.startswith("EGL_EXTENSIONS"):
                in_extensions_section = True
                parts = line.split(":", 1)
                if len(parts) > 1:
                    egl_entries.append(parts[1])
                continue

            if in_extensions_section:
                if line.startswith("EGL_CLIENT"):
                    break
                egl_entries.append(line)

        extensions_text = ",".join(egl_entries)
        data["egl_count"] = len(re.findall(r'\bEGL_[A-Za-z0-9_]+\b', extensions_text))
    except Exception:
        pass

    return data


def _parse_opencl(results: dict) -> dict:
    """Return key OpenCL fields from the clinfo output file."""
    data = {
        "supported": results.get("opencl", False),
        "platforms": [],
    }
    # If the probe flag says OpenCL is unsupported, still attempt to parse
    # the clinfo output file if it exists and is non-empty — some systems
    # produce clinfo output even when the probe check failed.
    if not data["supported"]:
        try:
            if not os.path.exists(Filenames.opencl_output_file) or os.path.getsize(Filenames.opencl_output_file) < 10:
                return data
            # allow parsing to continue; `data["supported"]` will be updated
            # based on parsed platforms later
        except Exception:
            return data

    # Prefer the full parser from OpenCL.py if available — it's more robust.
    if ClinfoParser is not None:
        try:
            parser = ClinfoParser()
            platforms = []
            for p in parser.platforms:
                plat = {
                    "name": p.get("name", ""),
                    "version": "",
                    "profile": "",
                    "devices": [],
                    "extensions_count": 0
                }
                # Platform properties often contain 'Platform Extensions'
                for key, val, children in p.get("properties", []):
                    if key == "Platform Version" or key == "Version":
                        plat["version"] = val
                    elif key == "Platform Profile" or key == "Profile":
                        plat["profile"] = val
                    elif "Platform Extensions" == key:
                        # Count cl_* tokens in the value and any child entries
                        cnt = 0
                        if val:
                            cnt += len(re.findall(r'\bcl[A-Za-z0-9_]+\b', val))
                        for sub_k, sub_v in children:
                            cnt += len(re.findall(r'\bcl[A-Za-z0-9_]+\b', sub_k))
                            cnt += len(re.findall(r'\bcl[A-Za-z0-9_]+\b', sub_v))
                        plat["extensions_count"] = cnt
                for d in p.get("devices", []):
                    dev = {
                        "name": d.get("name", ""),
                        "version": "",
                        "opencl_c_version": "",
                        "device_profile": "",
                        "driver_version": "",
                        "extensions_count": 0,
                        "opencl_c_features_count": 0,
                        "device_type": "",
                        "compute_units": "",
                        "workgroup_size": "",
                        "global_memory": "",
                        "local_memory": "",
                        "vendor": "",
                        "vendor_id": "",
                        "max_clock": "",
                        "unified_memory": "",
                        "conformance_test": "",
                    }
                    for key, val, children in d.get("properties", []):
                        if key == "Device Version" or key == "Version":
                            dev["version"] = val
                        elif "Device OpenCL C Version" == key:
                            dev["opencl_c_version"] = val
                        elif "Device Profile" == key:
                            dev["device_profile"] = val
                        elif key == "Driver Version":
                            dev["driver_version"] = val
                        elif key == "Device Type":
                            dev["device_type"] = val
                        elif key == "Max compute units":
                            dev["compute_units"] = val
                        elif key == "Max work group size":
                            dev["workgroup_size"] = val
                        elif key == "Global memory size":
                            dev["global_memory"] = val
                        elif key == "Local memory size":
                            dev["local_memory"] = val
                        elif key == "Device Vendor":
                            dev["vendor"] = val
                        elif key == "Device Vendor ID":
                            dev["vendor_id"] = val
                        elif key == "Max clock frequency":
                            dev["max_clock"] = val
                        elif key == "Unified memory for Host and Device":
                            dev["unified_memory"] = val
                        elif key == "Latest conformance test passed":
                            dev["conformance_test"] = val
                        elif "Device Extensions" in key:
                            # Count cl_* tokens in value and children
                            cnt = 0
                            if val:
                                cnt += len(re.findall(r'\bcl[A-Za-z0-9_]+\b', val))
                            for sub_k, sub_v in children:
                                cnt += len(re.findall(r'\bcl[A-Za-z0-9_]+\b', sub_k))
                                cnt += len(re.findall(r'\bcl[A-Za-z0-9_]+\b', sub_v))
                            dev["extensions_count"] = cnt
                    # Count OpenCL C features (count _opencl_c in properties)
                    for key, val, children in d.get("properties", []):
                        if "OpenCL C" in key and "features" in key:
                            dev["opencl_c_features_count"] += len(re.findall(r'\b__opencl_c[A-Za-z0-9_]*\b', val or ""))
                            for sub_k, sub_v in children:
                                dev["opencl_c_features_count"] += len(re.findall(r'\b__opencl_c[A-Za-z0-9_]*\b', sub_k))
                                dev["opencl_c_features_count"] += len(re.findall(r'\b__opencl_c[A-Za-z0-9_]*\b', sub_v))
                    plat["devices"].append(dev)
                platforms.append(plat)

            data["platforms"] = [pp for pp in platforms if pp.get("devices")]
            if data["platforms"]:
                data["supported"] = True
            else:
                data["supported"] = False
            return data
        except Exception:
            # Fall through to the simple parser below
            pass

    # Fallback: quick parsing (best-effort)
    try:
        with open(Filenames.opencl_output_file, "r") as f:
            content = f.read()
    except Exception:
        return data

    # Quick pass: grab Platform Name, Version, Profile + Device info + extensions
    current_platform = None
    current_device = None
    mode = "START"
    in_platform_extensions = False
    in_device_extensions = False
    in_opencl_c_features = False

    for line in content.splitlines():
        if not line.strip():
            if in_platform_extensions or in_device_extensions or in_opencl_c_features:
                in_platform_extensions = False
                in_device_extensions = False
                in_opencl_c_features = False
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
            in_opencl_c_features = False
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
                current_platform = {
                    "name": value,
                    "version": "",
                    "profile": "",
                    "devices": [],
                    "extensions_count": 0
                }
                data["platforms"].append(current_platform)
                current_device = None
                in_platform_extensions = False
                in_device_extensions = False
                in_opencl_c_features = False
            elif key == "Platform Version" or key == "Version":
                if current_platform:
                    current_platform["version"] = value
            elif key == "Platform Profile" or key == "Profile":
                if current_platform:
                    current_platform["profile"] = value
            elif key == "Platform Extensions":
                in_platform_extensions = True
                in_device_extensions = False
                in_opencl_c_features = False
                continue
            elif mode == "DEVICE" and current_platform:
                if key == "Device Name":
                    current_device = {
                        "name": value,
                        "version": "",
                        "opencl_c_version": "",
                        "driver_version": "",
                        "extensions_count": 0,
                        "opencl_c_features_count": 0,
                        "device_type": "",
                        "compute_units": "",
                        "global_memory": "",
                        "local_memory": "",
                        "workgroup_size": "",
                        "vendor": "",
                        "vendor_id": "",
                        "max_clock": "",
                        "unified_memory": "",
                        "conformance_test": "",
                    }
                    current_platform["devices"].append(current_device)
                    in_device_extensions = False
                    in_opencl_c_features = False
                elif key == "Device Extensions":
                    in_device_extensions = True
                    in_platform_extensions = False
                    in_opencl_c_features = False
                    continue
                elif "OpenCL C" in key and "Features" in key:
                    in_opencl_c_features = True
                    in_device_extensions = False
                    in_platform_extensions = False
                    continue
                elif current_device:
                    if key == "Device Version" or key == "Version":
                        current_device["version"] = value
                    elif "OpenCL C" in key and "Version" in key:
                        current_device["opencl_c_version"] = value
                    elif key == "Driver Version":
                        current_device["driver_version"] = value
                    elif key == "Device Type":
                        current_device["device_type"] = value
                    elif key == "Device Vendor":
                        current_device["vendor"] = value
                    elif key == "Device Vendor ID":
                        current_device["vendor_id"] = value
                    elif key == "Max clock frequency":
                        current_device["max_clock"] = value
                    elif key == "Unified memory for Host and Device":
                        current_device["unified_memory"] = value
                    elif key == "Latest conformance test passed":
                        current_device["conformance_test"] = value
                    elif key == "Max compute units":
                        current_device["compute_units"] = value
                    elif key == "Global memory size":
                        current_device["global_memory"] = value
                    elif key == "Local memory size":
                        current_device["local_memory"] = value
                    elif key == "Max work group size":
                        current_device["workgroup_size"] = value
            elif in_platform_extensions and current_platform:
                # Extract cl_* tokens from the whole line
                matches = re.findall(r'\bcl_[A-Za-z0-9_]+\b', content_line)
                current_platform["extensions_count"] += len(matches)
            elif in_device_extensions and current_device:
                # Extract cl_* tokens from the whole line
                matches = re.findall(r'\bcl_[A-Za-z0-9_]+\b', content_line)
                current_device["extensions_count"] += len(matches)
            elif in_opencl_c_features and current_device:
                # Extract _opencl_c features from the whole line
                matches = re.findall(r'\b_opencl_c[A-Za-z0-9_]*\b', content_line)
                current_device["opencl_c_features_count"] += len(matches)

    # Filter platforms to keep only those with devices
    data["platforms"] = [p for p in data["platforms"] if p.get("devices")]
    if data["platforms"]:
        data["supported"] = True
    else:
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


def _parse_glx_es_egl_counts(lines: list) -> dict:
    es_extensions = set()
    glx_extensions = set()
    glx_visual_count = 0
    in_es_extensions = False
    in_glx_client_extensions = False
    in_glx_visuals = False
    glx_visuals_started = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("OpenGL ES profile extensions:"):
            in_es_extensions = True
            continue
        if in_es_extensions:
            if stripped == "":
                in_es_extensions = False
                continue
            es_extensions.update(re.findall(r'\bGL_[A-Za-z0-9_]+\b', stripped))
            continue

        if stripped.startswith("client glx extensions:"):
            in_glx_client_extensions = True
            continue
        if in_glx_client_extensions:
            if stripped == "":
                in_glx_client_extensions = False
                continue
            glx_extensions.update(re.findall(r'\bGLX_[A-Za-z0-9_]+\b', stripped))
            continue

        if "GLX Visuals" in stripped:
            in_glx_visuals = True
            glx_visuals_started = False
            continue
        if in_glx_visuals:
            if re.match(r'^[-=]{2,}', stripped):
                glx_visuals_started = True
                continue
            if not glx_visuals_started:
                continue
            if stripped == "":
                in_glx_visuals = False
                continue
            glx_visual_count += 1

    return {
        "es_extensions_count": len(es_extensions),
        "glx_extension_count": len(glx_extensions),
        "glx_visual_count": glx_visual_count,
    }


def _parse_gpui_stats(results: dict) -> list:
    gpus = []
    try:
        # Find all card directories under /sys/class/drm/
        # They are usually named card0, card1, card2 etc.
        card_dirs = sorted(glob.glob("/sys/class/drm/card[0-9]*"))
        for card_dir in card_dirs:
            # card_dir is /sys/class/drm/card1 etc.
            card_name = os.path.basename(card_dir) # e.g. "card1"
            # Get the card index from the name (digits only)
            m = re.search(r'\d+', card_name)
            if not m:
                continue
            card_index = int(m.group(0))
            
            # Read vendor, device, driver, vbios, pcie link speed/width, etc.
            device_path = f"{card_dir}/device"
            if not os.path.isdir(device_path):
                continue
            
            vendor_id = ""
            device_id = ""
            driver = ""
            vbios = ""
            pci_address = ""
            pcie_link_speed = ""
            pcie_link_width = ""
            
            # Vendor ID
            if os.path.exists(f"{device_path}/vendor"):
                try:
                    with open(f"{device_path}/vendor", "r") as f:
                        vendor_id = f.read().strip()
                except Exception:
                    pass
            
            # Device ID
            if os.path.exists(f"{device_path}/device"):
                try:
                    with open(f"{device_path}/device", "r") as f:
                        device_id = f.read().strip()
                except Exception:
                    pass
            
            # Driver
            driver_link = f"{device_path}/driver"
            if os.path.islink(driver_link):
                try:
                    driver = os.path.basename(os.readlink(driver_link))
                except Exception:
                    pass
            
            # VBIOS
            if os.path.exists(f"{device_path}/vbios_version"):
                try:
                    with open(f"{device_path}/vbios_version", "r") as f:
                        vbios = f.read().strip()
                except Exception:
                    pass
            
            # PCI Address (from the symlink target or subsystem slot)
            try:
                real_device_path = os.path.realpath(device_path)
                pci_address = os.path.basename(real_device_path) # e.g. 0000:03:00.0
            except Exception:
                pass
            
            # PCIe Link Speed
            curr_speed = ""
            max_speed = ""
            if os.path.exists(f"{device_path}/current_link_speed"):
                try:
                    with open(f"{device_path}/current_link_speed", "r") as f:
                        curr_speed = f.read().strip()
                except Exception:
                    pass
            if os.path.exists(f"{device_path}/max_link_speed"):
                try:
                    with open(f"{device_path}/max_link_speed", "r") as f:
                        max_speed = f.read().strip()
                except Exception:
                    pass
            if curr_speed or max_speed:
                pcie_link_speed = f"{curr_speed} / {max_speed}" if curr_speed and max_speed else (curr_speed or max_speed)
            
            # PCIe Link Width
            curr_width = ""
            max_width = ""
            if os.path.exists(f"{device_path}/current_link_width"):
                try:
                    with open(f"{device_path}/current_link_width", "r") as f:
                        curr_width = f.read().strip()
                except Exception:
                    pass
            if os.path.exists(f"{device_path}/max_link_width"):
                try:
                    with open(f"{device_path}/max_link_width", "r") as f:
                        max_width = f.read().strip()
                except Exception:
                    pass
            if curr_width or max_width:
                pcie_link_width = f"x{curr_width} / x{max_width}" if curr_width and max_width else (f"x{curr_width}" if curr_width else f"x{max_width}")

            # Now get real-time stats
            stats = get_gpu_stats_for_index(card_index)
            if not stats:
                stats = {
                    'mem_used': 0, 'mem_total': 0, 'temp': 0, 
                    'clock_current': 0, 'clock_max': 0, 'usage': -1, 
                    'fan_speed': -1, 'power_usage': -1
                }
            
            gpu_info = {
                "card_index": card_index,
                "card_name": card_name,
                "vendor_id": vendor_id,
                "device_id": device_id,
                "driver": driver,
                "vbios": vbios,
                "pci_address": pci_address,
                "pcie_link_speed": pcie_link_speed,
                "pcie_link_width": pcie_link_width,
                "stats": stats,
                "supported": True
            }
            gpus.append(gpu_info)
    except Exception as e:
        print(f"Error gathering GPU stats: {e}")
        pass
    return gpus


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


_cpu_last_stat = [0, 0]  # [idle, total]

def get_realtime_cpu_usage() -> str:
    global _cpu_last_stat
    try:
        with open("/proc/stat", "r") as f:
            line = f.readline()
        if line.startswith("cpu "):
            parts = [float(x) for x in line.split()[1:]]
            idle = parts[3] + parts[4]  # idle + iowait
            total = sum(parts)
            prev_idle, prev_total = _cpu_last_stat
            _cpu_last_stat = [idle, total]
            diff_total = total - prev_total
            diff_idle = idle - prev_idle
            if diff_total > 0:
                usage = (1.0 - diff_idle / diff_total) * 100.0
                usage = max(0.0, min(100.0, usage))

                total_cur_khz = 0.0
                total_max_khz = 0.0
                cpu_root = "/sys/devices/system/cpu"
                for cpu_dir in glob.glob(os.path.join(cpu_root, "cpu[0-9]*", "cpufreq")):
                    cur_path = os.path.join(cpu_dir, "scaling_cur_freq")
                    max_path = os.path.join(cpu_dir, "scaling_max_freq")
                    try:
                        if os.path.exists(cur_path):
                            total_cur_khz += float(open(cur_path, "r", encoding="utf-8").read().strip())
                        if os.path.exists(max_path):
                            total_max_khz += float(open(max_path, "r", encoding="utf-8").read().strip())
                    except Exception:
                        continue

                if total_max_khz > 0:
                    used_mhz = total_cur_khz / 1000.0
                    max_mhz = total_max_khz / 1000.0
                    freq_pct = max(0.0, min(100.0, (used_mhz / max_mhz) * 100.0)) if max_mhz > 0 else 0.0
                    return f"{used_mhz:.0f} MHz / {max_mhz:.0f} MHz ({freq_pct:.0f} %)"
                return f"{usage:.0f} %"
    except Exception:
        pass
    return "—"


def get_realtime_ram_usage() -> str:
    try:
        mem_total = 0
        mem_avail = 0
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    mem_total = int(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    mem_avail = int(line.split()[1])
        if mem_total > 0 and mem_avail > 0:
            mem_used = mem_total - mem_avail
            total_gb = mem_total / (1024 * 1024)
            used_gb = mem_used / (1024 * 1024)
            pct = (used_gb / total_gb) * 100.0
            return f"{used_gb:.1f} GB / {total_gb:.1f} GB ({pct:.0f} %)"
    except Exception:
        pass
    return "—"


def get_realtime_uptime() -> str:
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.readline().split()[0])
            mins, secs = divmod(uptime_seconds, 60)
            hours, mins = divmod(mins, 60)
            days, hours = divmod(hours, 24)
            parts = []
            if days > 0:
                parts.append(f"{int(days)}d")
            if hours > 0:
                parts.append(f"{int(hours)}h")
            if mins > 0 or days > 0 or hours > 0:
                parts.append(f"{int(mins)}m")
            parts.append(f"{int(secs)}s")
            return " ".join(parts)
    except Exception:
        pass
    return "—"


def _parse_system() -> dict:
    """Return basic system info (OS, CPU, RAM, Kernel, Desktop, plus detailed BIOS, Uptime, etc.)."""
    info = {
        "os": "",
        "cpu": "",
        "cpu_cores_threads": "—",
        "ram": "",
        "cpu_usage": "—",
        "ram_usage": "—",
        "kernel": "",
        "architecture": "",
        "hostname": "",
        "uptime": "",
        "bios_version": "",
        "bios_date": "",
        "desktop": "",
        "windowing": "",
        "hardware_model": "",
        "disk_capacity": "",
        "hard_drives": "",
        "display": "",
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

    # CPU Cores and Threads
    try:
        cores = 0
        threads = 0
        with open("/proc/cpuinfo", "r") as f:
            content = f.read()
            core_match = re.search(r'cpu cores\s*:\s*(\d+)', content)
            if core_match:
                cores = int(core_match.group(1))
            threads = len(re.findall(r'^processor\s*:', content, re.M))
        if cores > 0 and threads > 0:
            info["cpu_cores_threads"] = f"{cores} Cores / {threads} Threads"
        elif threads > 0:
            info["cpu_cores_threads"] = f"{threads} Threads"
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
        uname_res = os.uname()
        info["kernel"] = uname_res.release
        info["architecture"] = uname_res.machine
        info["hostname"] = uname_res.nodename
    except Exception:
        try:
            result = subprocess.run(
                ["uname", "-r"], capture_output=True, text=True, timeout=2
            )
            info["kernel"] = result.stdout.strip()
        except Exception:
            pass

    # System Uptime
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.readline().split()[0])
            mins, secs = divmod(uptime_seconds, 60)
            hours, mins = divmod(mins, 60)
            days, hours = divmod(hours, 24)
            parts = []
            if days > 0:
                parts.append(f"{int(days)}d")
            if hours > 0:
                parts.append(f"{int(hours)}h")
            if mins > 0:
                parts.append(f"{int(mins)}m")
            if not parts:
                parts.append(f"{int(secs)}s")
            info["uptime"] = " ".join(parts)
    except Exception:
        pass

    # BIOS Version & Date
    for path, key in [
        ("/sys/class/dmi/id/bios_version", "bios_version"),
        ("/sys/class/dmi/id/bios_date", "bios_date"),
    ]:
        try:
            if os.path.exists(path):
                with open(path, "r") as f:
                    info[key] = f.read().strip()
        except Exception:
            pass

    info["desktop"] = os.environ.get("XDG_CURRENT_DESKTOP", "")
    info["windowing"] = os.environ.get("XDG_SESSION_TYPE", "")

    try:
        product_name = ""
        sys_vendor = ""
        version = ""
        for path, key in [
            ("/sys/devices/virtual/dmi/id/product_name", "product_name"),
            ("/sys/devices/virtual/dmi/id/sys_vendor", "sys_vendor"),
            ("/sys/devices/virtual/dmi/id/product_version", "version"),
        ]:
            try:
                if os.path.exists(path):
                    with open(path, "r") as f:
                        value = f.read().strip()
                    if key == "product_name":
                        product_name = value
                    elif key == "sys_vendor":
                        sys_vendor = value
                    elif key == "version":
                        version = value
            except Exception:
                pass

        if product_name:
            model_parts = []
            if sys_vendor:
                model_parts.append(sys_vendor)
            model_parts.append(product_name)
            if version and version not in product_name:
                model_parts.append(version)
            info["hardware_model"] = " ".join(model_parts)
    except Exception:
        pass

    try:
        usage = shutil.disk_usage("/")
        total_gb = usage.total / (1024**3)
        used_gb = usage.used / (1024**3)
        free_gb = usage.free / (1024**3)
        info["disk_capacity"] = f"{used_gb:.1f} GB used / {total_gb:.1f} GB total ({free_gb:.1f} GB free)"
    except Exception:
        pass

    # Detect hard drives
    try:
        if shutil.which("lsblk"):
            result = subprocess.run(
                ["lsblk", "-ndbo", "NAME,SIZE,TYPE,SERIAL"],
                capture_output=True, text=True, timeout=3
            )
            drives = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[0]
                    size = parts[1]
                    drive_type = parts[2]
                    # Filter for actual drives (disk, nvme, etc.)
                    if drive_type in ['disk', 'nvme', 'mmc', 'loop']:
                        if len(parts) >= 4:
                            serial = parts[3]
                            drives.append(f"{name} ({size}) - {serial}")
                        else:
                            drives.append(f"{name} ({size})")
            if drives:
                info["hard_drives"] = ";".join(drives)
    except Exception:
        pass

    try:
        display_info = []
        if shutil.which("xrandr"):
            result = subprocess.run(
                ["xrandr", "--listmonitors"],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines()[1:]:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        display_info.append(f"{parts[1]} {parts[2]}")
                    elif len(parts) >= 2:
                        display_info.append(parts[1])
        if not display_info and shutil.which("xdpyinfo"):
            result = subprocess.run(
                ["xdpyinfo"], capture_output=True, text=True, timeout=3
            )
            for line in result.stdout.splitlines():
                if "dimensions:" in line:
                    display_info.append(line.strip().split("dimensions:", 1)[1].strip())
                    break
        if display_info:
            info["display"] = "; ".join(display_info)
    except Exception:
        pass

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

def _make_action_row(title: str, subtitle: str) -> Gtk.Widget:
    """Create a row widget with title and values connected like a tree structure.
    Multiple values can be separated by semicolons or newlines."""
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
    box.set_margin_start(8)
    box.set_margin_end(8)
    box.set_margin_top(6)
    box.set_margin_bottom(6)
    
    # Title label with wrapping enabled
    title_label = Gtk.Label(label=title)
    title_label.add_css_class("body")
    title_label.set_halign(Gtk.Align.START)
    title_label.set_wrap(True)
    title_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
    title_label.set_selectable(True)
    
    box.append(title_label)
    
    # Parse multiple values (split by semicolon or newline)
    if not subtitle or subtitle in ("—", "-", "N/A"):
        values = ["—"]
    else:
        # Split by semicolon first, then by newline, and clean up
        values = [v.strip() for v in subtitle.replace('\n', ';').split(';') if v.strip()]
        if not values:
            values = ["—"]
    
    # Store references to subtitle labels for updates
    box.subtitle_labels = []
    
    # Create a connector and label for each value
    for idx, value in enumerate(values):
        value_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        
        # Tree connector (└─ for items)
        connector_label = Gtk.Label(label="└─")
        connector_label.add_css_class("dim-label")
        connector_label.set_halign(Gtk.Align.START)
        
        # Value label with wrapping enabled
        value_label = Gtk.Label(label=value)
        value_label.add_css_class("caption")
        value_label.set_halign(Gtk.Align.START)
        value_label.set_wrap(True)
        value_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        value_label.set_selectable(True)
        
        value_container.append(connector_label)
        value_container.append(value_label)
        box.append(value_container)
        box.subtitle_labels.append(value_label)
    
    # Add a set_subtitle method for compatibility with update callbacks
    def set_subtitle(new_subtitle: str):
        # Update the first label (for single-value fields)
        if box.subtitle_labels:
            box.subtitle_labels[0].set_label(new_subtitle if new_subtitle else "—")
    box.set_subtitle = set_subtitle
    box.subtitle_label = box.subtitle_labels[0] if box.subtitle_labels else None
    
    return box


def _make_status_badge(text: str, good: bool) -> Gtk.Label:
    badge = Gtk.Label(label=text)
    badge.set_valign(Gtk.Align.CENTER)
    badge.add_css_class("pill" if good else "error")
    badge.add_css_class("caption")
    if good:
        badge.add_css_class("success")
    return badge


def _make_grid_card_content(columns: list[list[tuple[str, str]]], row_widgets_out: dict = None) -> Gtk.Widget:
    grid_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
    grid_box.set_hexpand(True)
    for column_rows in columns:
        col_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        col_box.set_hexpand(True)
        for title, subtitle in column_rows:
            # Skip rows that have no meaningful value
            if not subtitle or subtitle in ("—", "-", "N/A"):
                continue
            row = _make_action_row(title, subtitle)
            col_box.append(row)
            if row_widgets_out is not None:
                row_widgets_out[title] = row
        grid_box.append(col_box)
    return grid_box


def _move_card_in_registry(registry, card_id: str, target_index: int):
    if not registry:
        return registry
    current_order = [entry_card_id for entry_card_id, _ in registry]
    if card_id not in current_order:
        return registry
    source_index = current_order.index(card_id)
    new_index = max(0, min(len(current_order) - 1, target_index))
    if source_index == new_index:
        return registry
    new_order = current_order[:]
    moved = new_order.pop(source_index)
    new_order.insert(new_index, moved)
    widget_map = {entry_card_id: widget for entry_card_id, widget in registry}
    return [(entry_card_id, widget_map[entry_card_id]) for entry_card_id in new_order]


def _apply_registry_order(flow_box: Gtk.FlowBox | None, registry):
    if flow_box is None or not registry:
        return
    widget_map = {entry_card_id: widget for entry_card_id, widget in registry}
    ordered_widgets = [widget_map[entry_card_id] for entry_card_id, _ in registry]
    flow_box.remove_all()
    for widget in ordered_widgets:
        flow_box.append(widget)
    flow_box._summary_card_registry = list(registry)


def _nav_button(label: str, page_name: str, app, gpu_index=None) -> Gtk.Button:
    btn = Gtk.Button(label=label)
    btn.add_css_class("flat")
    btn.add_css_class("suggested-action")
    btn.set_valign(Gtk.Align.CENTER)
    def on_clicked(_):
        if hasattr(app, "open_tab"):
            app.open_tab(page_name, gpu_index=gpu_index)
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
        "ram usage": "memory-symbolic",
        "cpu usage": "cpu-symbolic",
        "uptime": "preferences-system-time-symbolic",
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
        "opengl es version": "text-editor-symbolic",
        "opengl es glsl version": "text-editor-symbolic",
        "opengl es extension count": "preferences-system-symbolic",
        "egl version": "system-search-symbolic",
        "egl extension count": "system-search-symbolic",
        "glx extension count": "view-grid-symbolic",
        "glx visual count": "view-preview-symbolic",
        "glx fbconfig count": "view-list-symbolic",
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
               row_widgets_out: dict = None,
               content_widget: Gtk.Widget | None = None,
               gpu_index: int | None = None,
               extra_nav_actions: list[tuple[str, str]] | None = None,
               card_id: str | None = None,
               allow_reorder: bool = False,
               flow_box: Gtk.FlowBox | None = None) -> Gtk.Box:
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
    # Add CSS class for styling
    frame.add_css_class("summary-card")

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
            icon_name, 20, 20, True
        )
        icon_img = Gtk.Picture.new_for_pixbuf(icon_pixbuf)
        icon_img.set_size_request(20, 20)
        header.append(icon_img)
    except Exception:
        # Fallback: named icon
        icon_img = Gtk.Image.new_from_icon_name("application-x-executable-symbolic")
        icon_img.set_pixel_size(20)
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

    # Navigation buttons
    if nav_page and supported and app:
        btn = _nav_button("Open →", nav_page, app, gpu_index=gpu_index)
        header.append(btn)

    if extra_nav_actions and supported and app:
        for label, page_name in extra_nav_actions:
            btn = _nav_button(label, page_name, app, gpu_index=gpu_index)
            header.append(btn)

    # Card-level reorder controls are intentionally removed here. The summary page
    # uses a single reorder button in the page header to manage the card order like
    # browser tabs. This keeps the GTK4 runtime compatibility safe and avoids the
    # unsupported data-access API.

    card_box.append(header)

    # Separator between header and rows
    sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    card_box.append(sep)

    # ---------- Property rows ----------
    if content_widget is not None and supported:
        card_box.append(content_widget)
    elif not supported:
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

    if card_id is not None:
        frame._summary_card_id = card_id
    frame._summary_card_title = title

    return frame


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def _match_vulkan_name(vendor_id_str, device_id_str, vk_devices):
    if not vendor_id_str or not device_id_str:
        return None
    try:
        v1 = int(vendor_id_str, 16)
        d1 = int(device_id_str, 16)
        for dev in vk_devices:
            vk_vendor = dev.get("vendor_id")
            vk_device = dev.get("device_id")
            if vk_vendor and vk_device:
                try:
                    v2 = int(vk_vendor, 16)
                    d2 = int(vk_device, 16)
                    if v1 == v2 and d1 == d2:
                        return dev.get("name")
                except ValueError:
                    pass
    except ValueError:
        pass
    return None


def _get_gpu_fallback_name(vendor_id_str, device_id_str):
    vendor_names = {
        0x1002: "AMD Radeon",
        0x10de: "NVIDIA GeForce",
        0x8086: "Intel Graphics",
    }
    try:
        v = int(vendor_id_str, 16)
        d = int(device_id_str, 16)
        vendor_name = vendor_names.get(v, "Generic")
        return f"{vendor_name} (Device {device_id_str})"
    except Exception:
        return "Unknown GPU"


def _get_gpu_logo(vendor_id_str: str) -> str:
    """Return the best logo image path for a GPU based on its vendor ID."""
    try:
        v = int(vendor_id_str, 16)
        if v == 0x1002:   # AMD
            return "../Images/AMD_logo.png"
        elif v == 0x10de: # NVIDIA
            return "../Images/nvidia_logo.png"
        elif v == 0x8086: # Intel
            return "../Images/intel-logo.png"
    except Exception:
        pass
    return "../Images/about-us.png"


def create_summary_page(app, results: dict) -> Gtk.Widget:
    """
    Return a widget for the "Summary" tab.  Data gathering runs in a
    background thread; a spinner is shown until it completes.

    Parameters
    ----------
    app     : the GPUViewerApp instance (has .view_stack)
    results : the dict from _probe_and_build_tabs  {vulkan: bool, …}
    """
    # Add CSS styling for cards based on active theme
    prefer_dark = app.config.get_theme_preference() if (app and hasattr(app, 'config')) else True
    css_provider = Gtk.CssProvider()
    if prefer_dark:
        card_css = """
        .summary-card {
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 12px;
            background-color: #242429;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }

        .summary-card:disabled {
            opacity: 0.55;
        }

        .summary-card .title-3 {
            font-weight: 700;
            color: #ffffff;
        }

        .summary-card row subtitle {
            color: rgba(255, 255, 255, 0.75);
        }

        .summary-card row title {
            color: #ffffff;
            font-weight: 500;
        }

        .summary-card button {
            background-color: #2e2e36;
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
        }

        .summary-card button:hover {
            background-color: #383842;
        }
        """
    else:
        card_css = """
        .summary-card {
            border: 1px solid rgba(0, 0, 0, 0.12);
            border-radius: 12px;
            background-color: #ffffff;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .summary-card:disabled {
            opacity: 0.55;
        }

        .summary-card .title-3 {
            font-weight: 700;
            color: #171717;
        }

        .summary-card row subtitle {
            color: rgba(0, 0, 0, 0.75);
        }

        .summary-card row title {
            color: #171717;
            font-weight: 500;
        }

        .summary-card button {
            background-color: #f4f4f5;
            color: #171717;
            border: 1px solid rgba(0, 0, 0, 0.1);
            border-radius: 6px;
        }

        .summary-card button:hover {
            background-color: #e4e4e7;
        }
        """
    css_provider.load_from_data(card_css.encode("utf-8"))
    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(),
        css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    
    outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    outer.set_vexpand(True)
    outer.set_hexpand(True)

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
        flow_box.set_max_children_per_line(2)  # up to 2 cards per row
        flow_box.set_selection_mode(Gtk.SelectionMode.NONE)
        flow_box.set_margin_top(12)
        flow_box.set_margin_bottom(24)
        flow_box.set_margin_start(12)
        flow_box.set_margin_end(12)
        flow_box.set_row_spacing(8)
        flow_box.set_column_spacing(8)
        flow_box._summary_card_registry = []
        flow_box._summary_card_titles = {}
        if app is not None:
            app.summary_flow_box = flow_box
            app.summary_card_titles = flow_box._summary_card_titles

        def _iter_flowbox_children(widget_container):
            child = widget_container.get_first_child()
            while child is not None:
                yield child
                child = child.get_next_sibling()

        def _apply_summary_card_order(order):
            if flow_box is None:
                return
            registry = list(getattr(flow_box, "_summary_card_registry", []))
            if not registry:
                return
            widget_by_id = {widget_id: widget for widget_id, widget in registry}
            ordered_widgets = [widget_by_id[widget_id] for widget_id in order if widget_id in widget_by_id]
            for widget_id in list(widget_by_id):
                if widget_id not in order:
                    ordered_widgets.append(widget_by_id[widget_id])
            flow_box.remove_all()
            for widget in ordered_widgets:
                flow_box.append(widget)
            flow_box._summary_card_registry = [(widget_id, widget_by_id[widget_id]) for widget_id in order if widget_id in widget_by_id]
            for widget_id in list(widget_by_id):
                if widget_id not in order:
                    flow_box._summary_card_registry.append((widget_id, widget_by_id[widget_id]))

        def _move_card_in_summary_order(card_id: str, direction: int):
            if flow_box is None:
                return
            registry = list(getattr(flow_box, "_summary_card_registry", []))
            if not registry:
                return
            current_order = [entry_card_id for entry_card_id, _ in registry]
            if card_id not in current_order:
                return
            index = current_order.index(card_id)
            new_index = index + direction
            if new_index < 0 or new_index >= len(current_order):
                return
            current_order[index], current_order[new_index] = current_order[new_index], current_order[index]
            _apply_summary_card_order(current_order)
            if hasattr(app, "config"):
                app.config.set_summary_card_order(current_order)

        def add_summary_card(card_id: str, widget: Gtk.Widget):
            registry = list(getattr(flow_box, "_summary_card_registry", []))
            if card_id and widget is not None and widget not in [existing_widget for _, existing_widget in registry]:
                registry.append((card_id, widget))
                flow_box._summary_card_registry = registry
                flow_box._summary_card_titles[card_id] = getattr(widget, "_summary_card_title", card_id)
            return widget

        def restore_summary_card_order():
            registry = list(getattr(flow_box, "_summary_card_registry", []))
            if not registry:
                return
            current_order = [widget_id for widget_id, _ in registry]
            saved_order = app.config.get_summary_card_order() if app is not None and hasattr(app, "config") else []
            if not saved_order:
                def default_card_priority(card_id):
                    if card_id.startswith("vulkan-"):
                        return 0
                    if card_id == "system":
                        return 1
                    if card_id.startswith("gpu-"):
                        return 2
                    if card_id.startswith("opengl"):
                        return 3
                    if card_id in ("egl", "glx"):
                        return 4
                    if card_id.startswith("opencl-"):
                        return 5
                    if card_id.startswith("vdpau"):
                        return 6
                    return 7

                default_order = sorted(
                    enumerate(current_order),
                    key=lambda item: (default_card_priority(item[1]), item[0]),
                )
                _apply_summary_card_order([card_id for _, card_id in default_order])
                return
            ordered = [card_id for card_id in saved_order if card_id in current_order]
            for card_id in current_order:
                if card_id not in ordered:
                    ordered.append(card_id)
            if ordered == current_order:
                return
            _apply_summary_card_order(ordered)

        scroll.set_child(flow_box)

        view_stack = getattr(app, "view_stack", None)

        # ── System Information ───────────────────────────────────────────
        sys_data = data["system"]
        cpu_usage_init = get_realtime_cpu_usage()
        ram_usage_init = get_realtime_ram_usage()
        uptime_init = get_realtime_uptime()

        sys_columns = [
            [
                ("Operating System", sys_data.get("os", "—")),
                ("Processor", sys_data.get("cpu", "—")),
                ("CPU Cores / Threads", sys_data.get("cpu_cores_threads", "—")),
                ("CPU Usage", cpu_usage_init),
                ("RAM Usage", ram_usage_init),
            ],
            [
                ("Kernel", sys_data.get("kernel", "—")),
                ("Architecture", sys_data.get("architecture", "—")),
                ("Hostname", sys_data.get("hostname", "—")),
                ("Uptime", uptime_init),
            ],
            [
                ("Hardware Model", sys_data.get("hardware_model", "—")),
                ("BIOS Info", f"{sys_data.get('bios_version', '—')} ({sys_data.get('bios_date', '—')})" if sys_data.get("bios_version") or sys_data.get("bios_date") else "—"),
                ("Desktop / Session", f"{sys_data.get('desktop', '—')} ({sys_data.get('windowing', '—')})" if sys_data.get("desktop") or sys_data.get("windowing") else "—"),
                ("Disk Capacity", sys_data.get("disk_capacity", "—")),
                ("Hard Drives", sys_data.get("hard_drives", "—")),
                ("Display", sys_data.get("display", "—")),
            ],
        ]
        sys_widgets = {}
        sys_card = _make_card(
            "System",
            "../Images/about-us.png",
            [],
            nav_page=None,   # no detail tab for system info
            app=app,
            supported=True,
            content_widget=_make_grid_card_content(sys_columns, row_widgets_out=sys_widgets),
            row_widgets_out=sys_widgets,
            card_id="system",
            allow_reorder=True,
            flow_box=flow_box,
        )
        sys_card.set_size_request(250, -1)
        flow_box.append(sys_card)
        add_summary_card("system", sys_card)

        # ── GPU Statistics & Details (Multi-GPU support) ─────────────────
        gpui_list = data["gpui_stats"] # This is a list of dicts
        stats_widgets_list = []
        vk_devices = data["vulkan"].get("devices", []) if data.get("vulkan") else []

        # Filter out GPU entries with no identifiable vendor/device ID
        known_gpus = [g for g in gpui_list if g.get("vendor_id") or g.get("device_id")]

        if known_gpus:
            for gpu_info in known_gpus:
                gpu_idx = gpu_info["card_index"]
                gpu_stats = gpu_info["stats"]
                
                # Match Vulkan name
                matched_name = _match_vulkan_name(gpu_info["vendor_id"], gpu_info["device_id"], vk_devices)
                if not matched_name:
                    matched_name = _get_gpu_fallback_name(gpu_info["vendor_id"], gpu_info["device_id"])
                
                card_title = f"{matched_name} ({gpu_info['card_name']})"
                
                opencl_hint = {}
                for platform in data.get("opencl", {}).get("platforms", []):
                    for device in platform.get("devices", []):
                        name = (device.get("name") or "").strip().lower()
                        if not name:
                            continue
                        if name in (matched_name.lower(), gpu_info.get("card_name", "").lower()):
                            opencl_hint = {
                                "compute_units": device.get("compute_units"),
                                "instruction_set": device.get("opencl_c_version") or device.get("version"),
                            }
                            break
                    if opencl_hint:
                        break
                if opencl_hint:
                    gpu_info.setdefault("compute_units", opencl_hint.get("compute_units"))
                    gpu_info.setdefault("instruction_set", opencl_hint.get("instruction_set"))
                    gpu_stats.setdefault("compute_units", opencl_hint.get("compute_units"))
                    gpu_stats.setdefault("instruction_set", opencl_hint.get("instruction_set"))
                
                gpu_widgets = {}

                def _gpu_val(v, suffix="", threshold=0, threshold_field=None):
                    """Return formatted string or None if value is unavailable."""
                    if v is None:
                        return None
                    if isinstance(v, (int, float)) and v < threshold:
                        return None
                    return f"{v}{suffix}"

                gpu_rows_col1 = []
                if gpu_info.get("pci_address"):
                    gpu_rows_col1.append(("PCI Address", gpu_info["pci_address"]))
                if gpu_info.get("driver"):
                    gpu_rows_col1.append(("Driver", gpu_info["driver"]))
                if gpu_info.get("vbios"):
                    gpu_rows_col1.append(("VBIOS Version", gpu_info["vbios"]))
                if gpu_info.get("pcie_link_speed"):
                    gpu_rows_col1.append(("PCIe Link Speed", gpu_info["pcie_link_speed"]))
                if gpu_info.get("pcie_link_width"):
                    gpu_rows_col1.append(("PCIe Link Width", gpu_info["pcie_link_width"]))

                gpu_rows_col2 = []
                mem_used = gpu_stats.get("mem_used")
                mem_total = gpu_stats.get("mem_total")
                if mem_used is not None and mem_total is not None and mem_total > 0:
                    pct = (mem_used / mem_total) * 100.0 if mem_total else 0.0
                    gpu_rows_col2.append(("VRAM", f"{mem_used} / {mem_total} MB ({pct:.0f} %)"))
                vram_clock = gpu_stats.get("vram_clock")
                vram_clock_max = gpu_stats.get("vram_clock_max")
                if vram_clock is not None and vram_clock > 0:
                    if vram_clock_max is not None and vram_clock_max > 0:
                        pct = (vram_clock / vram_clock_max) * 100.0 if vram_clock_max else 0.0
                        gpu_rows_col2.append(("VRAM Clock", f"{vram_clock} / {vram_clock_max} MHz ({pct:.0f} %)"))
                    else:
                        gpu_rows_col2.append(("VRAM Clock", f"{vram_clock} MHz"))
                vram_type = gpu_stats.get("vram_type") or gpu_info.get("vram_type")
                if vram_type:
                    gpu_rows_col2.append(("VRAM Type", str(vram_type)))
                if gpu_stats.get("usage") is not None and gpu_stats["usage"] >= 0:
                    gpu_rows_col2.append(("GPU Usage", f"{gpu_stats['usage']} %"))
                if gpu_stats.get("temp") is not None and gpu_stats["temp"] > 0:
                    gpu_rows_col2.append(("Temperature", f"{gpu_stats['temp']} °C"))

                gpu_rows_col3 = []
                clk_cur = gpu_stats.get("clock_current")
                clk_max = gpu_stats.get("clock_max")
                if clk_cur is not None and clk_cur > 0:
                    clk_str = f"{clk_cur} / {clk_max} MHz" if clk_max and clk_max > 0 else f"{clk_cur} MHz"
                    gpu_rows_col3.append(("GPU Clock", clk_str))
                if gpu_stats.get("power_usage") is not None and gpu_stats["power_usage"] > 0:
                    gpu_rows_col3.append(("Power", f"{gpu_stats['power_usage']} W"))
                if gpu_stats.get("fan_speed") is not None and gpu_stats["fan_speed"] >= 0:
                    gpu_rows_col3.append(("Fan Speed", f"{gpu_stats['fan_speed']} %"))

                compute_units = gpu_stats.get("compute_units") or gpu_info.get("compute_units")
                if compute_units:
                    gpu_rows_col3.append(("Compute Units", str(compute_units)))
                rop_count = gpu_stats.get("rop_count") or gpu_info.get("rop_count")
                if rop_count:
                    gpu_rows_col3.append(("ROPs", str(rop_count)))

                # Only include non-empty columns
                gpu_columns = [c for c in [gpu_rows_col1, gpu_rows_col2, gpu_rows_col3] if c]


                gpu_logo = _get_gpu_logo(gpu_info.get("vendor_id", ""))
                gpu_card = _make_card(
                    card_title,
                    gpu_logo,
                    [],
                    nav_page=None,
                    app=app,
                    supported=True,
                    content_widget=_make_grid_card_content(gpu_columns, row_widgets_out=gpu_widgets),
                    row_widgets_out=gpu_widgets,
                    card_id=f"gpu-{gpu_idx}",
                    allow_reorder=True,
                    flow_box=flow_box,
                )
                gpu_card.set_size_request(250, -1)
                flow_box.append(gpu_card)
                add_summary_card(f"gpu-{gpu_idx}", gpu_card)
                stats_widgets_list.append((gpu_idx, gpu_widgets))
        else:
            stats_card = _make_card(
                "GPU Statistics",
                "../Images/about-us.png",
                [],
                nav_page=None,
                app=app,
                supported=False,
                card_id="gpu-stats",
                allow_reorder=True,
                flow_box=flow_box,
            )
            stats_card.set_size_request(250, -1)
            flow_box.append(stats_card)
            add_summary_card("gpu-stats", stats_card)

        # ── Vulkan ───────────────────────────────────────────────────────
        vk_data = data["vulkan"]
        if vk_data["supported"] and vk_data.get("devices"):
            for i, dev in enumerate(vk_data["devices"]):
                def _vk_col(fields):
                    return [(k, v) for k, v in fields if v and v not in ("—", "-")]

                col1 = _vk_col([
                    ("API Version", dev.get("api_version", "")),
                    ("Driver", dev.get("driver_name", "")),
                    ("Driver Version", dev.get("driver_version", "")),
                    ("Driver Info", dev.get("driver_info", "")),
                    ("Device Type", dev.get("device_type", "")),
                    ("Pipeline Cache UUID", dev.get("pipelineCacheUUID", "")),
                ])
                col2 = _vk_col([
                    ("Vendor ID", dev.get("vendor_id", "")),
                    ("Device ID", dev.get("device_id", "")),
                    ("Device UUID", dev.get("device_uuid", "")),
                    ("Driver UUID", dev.get("driver_uuid", "")),
                    ("Conformance Version", dev.get("conformance_version", "")),
                ])
                col3 = _vk_col([
                    ("Device Formats", str(dev.get("formats_count", "")) if dev.get("formats_count") else ""),
                    ("Device Extensions", str(dev.get("extensions_count", "")) if dev.get("extensions_count") else ""),
                    ("Memory Types", str(dev.get("memory_types_count", "")) if dev.get("memory_types_count") else ""),
                    ("Memory Heaps", str(dev.get("memory_heaps_count", "")) if dev.get("memory_heaps_count") else ""),
                    ("Queue Families", str(dev.get("queue_count", "")) if dev.get("queue_count") else ""),
                ])
                col4 = _vk_col([
                    ("Instance Extensions", str(vk_data.get("instance_extensions_count", "")) if vk_data.get("instance_extensions_count") else ""),
                    ("Instance Layers", str(vk_data.get("instance_layers_count", "")) if vk_data.get("instance_layers_count") else ""),
                    ("Instance Version", str(vk_data.get("instance_version", ""))),
                ])
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

                if dev.get("video_decode_profiles"):
                    col4.append(("Video Decode Profiles", _format_video_profile_counts(dev["video_decode_profiles"], dev.get("video_decode_profile_counts", {}), "Decode")))
                if dev.get("video_encode_profiles"):
                    col4.append(("Video Encode Profiles", _format_video_profile_counts(dev["video_encode_profiles"], dev.get("video_encode_profile_counts", {}), "Encode")))

                columns = [c for c in [col1, col2, col3, col4] if c]
                extra_nav_actions = []
                if dev.get("video_decode_profiles") or dev.get("video_encode_profiles"):
                    extra_nav_actions.append(("Open Vulkan Video →", "vulkan_video_page"))

                content_widget = _make_grid_card_content(columns)
                label = f"Vulkan" if len(vk_data["devices"]) == 1 else f"Vulkan - {dev['name']}"
                card = _make_card(
                    label,
                    "../Images/Vulkan.png",
                    [],
                    nav_page="page1",
                    app=app,
                    supported=True,
                    content_widget=content_widget,
                    gpu_index=i,
                    extra_nav_actions=extra_nav_actions,
                    card_id=f"vulkan-{i}",
                    allow_reorder=True,
                    flow_box=flow_box,
                )
                card.set_size_request(250, -1)
                flow_box.append(card)
                add_summary_card(f"vulkan-{i}", card)
        else:
            card = _make_card(
                "Vulkan", "../Images/Vulkan.png",
                [], nav_page=None, app=app, supported=False,
                card_id="vulkan-missing",
                allow_reorder=True,
                flow_box=flow_box,
            )
            card.set_size_request(250, -1)
            flow_box.append(card)
            add_summary_card("vulkan-missing", card)

        # ── OpenGL ───────────────────────────────────────────────────────
        gl_data = data["opengl"]
        if gl_data["supported"] and gl_data.get("renderer"):
            renderer_label = gl_data["renderer"]

            # Card 1: Core OpenGL
            gl_columns = [
                [
                    ("Renderer", renderer_label),
                    ("Vendor", gl_data.get("vendor", "—")),
                ],
                [
                    ("OpenGL Version", gl_data.get("version", "—")),
                    ("GLSL Version", gl_data.get("shading_language_version", "—")),
                ],
                [
                    ("Extension Count", str(gl_data.get("extensions_count", "—"))),
                ],
            ]
            card = _make_card(
                f"OpenGL",
                "../Images/OpenGL.png",
                [],
                nav_page="page2",
                app=app,
                supported=True,
                content_widget=_make_grid_card_content(gl_columns),
                card_id="opengl",
                allow_reorder=True,
                flow_box=flow_box,
            )
            card.set_size_request(250, -1)
            flow_box.append(card)
            add_summary_card("opengl", card)

            # Card 2: OpenGL ES (only if data present)
            es_version = gl_data.get("es_version", "")
            if es_version:
                es_columns = [
                    [
                        ("OpenGL ES Version", es_version),
                        ("GLSL ES Version", gl_data.get("es_shading_language_version", "—")),
                    ],
                    [
                        ("Extension Count", str(gl_data.get("es_extensions_count", "—"))),
                    ],
                ]
                es_card = _make_card(
                    "OpenGL ES",
                    "../Images/OpenGL_ES.png",
                    [],
                    nav_page="page2",
                    app=app,
                    supported=True,
                    content_widget=_make_grid_card_content(es_columns),
                    card_id="opengl-es",
                    allow_reorder=True,
                    flow_box=flow_box,
                )
                es_card.set_size_request(250, -1)
                flow_box.append(es_card)
                add_summary_card("opengl-es", es_card)

            # Card 3: EGL (only if data present)
            egl_version = gl_data.get("egl_version", "")
            egl_count = gl_data.get("egl_count", 0)
            if egl_version or egl_count:
                egl_columns = [
                    [
                        ("EGL Version", egl_version or "—"),
                    ],
                    [
                        ("Extension Count", str(egl_count) if egl_count else "—"),
                    ],
                ]
                egl_card = _make_card(
                    "EGL",
                    "../Images/Egl_logo.png",
                    [],
                    nav_page="page2",
                    app=app,
                    supported=True,
                    content_widget=_make_grid_card_content(egl_columns),
                    card_id="egl",
                    allow_reorder=True,
                    flow_box=flow_box,
                )
                egl_card.set_size_request(250, -1)
                flow_box.append(egl_card)
                add_summary_card("egl", egl_card)

            # Card 4: GLX (only if data present)
            glx_version = gl_data.get("glx_version", "")
            glx_ext = gl_data.get("glx_extension_count", 0)
            glx_vis = gl_data.get("glx_visual_count", 0)
            glx_fb = gl_data.get("fbconfig_count", 0)
            if glx_version or glx_ext or glx_vis or glx_fb:
                glx_columns = [
                    [
                        ("GLX Version", glx_version or "—"),
                        ("Extension Count", str(glx_ext) if glx_ext else "—"),
                    ],
                    [
                        ("Visual Count", str(glx_vis) if glx_vis else "—"),
                        ("FBConfig Count", str(glx_fb) if glx_fb else "—"),
                    ],
                ]
                glx_card = _make_card(
                    "GLX",
                    "../Images/glx.png",
                    [],
                    nav_page="page2",
                    app=app,
                    supported=True,
                    content_widget=_make_grid_card_content(glx_columns),
                    card_id="glx",
                    allow_reorder=True,
                    flow_box=flow_box,
                )
                glx_card.set_size_request(250, -1)
                flow_box.append(glx_card)
                add_summary_card("glx", glx_card)
        else:
            card = _make_card(
                "OpenGL", "../Images/OpenGL.png",
                [], nav_page=None, app=app, supported=False,
                card_id="opengl-missing",
                allow_reorder=True,
                flow_box=flow_box,
            )
            card.set_size_request(250, -1)
            flow_box.append(card)
            add_summary_card("opengl-missing", card)

        # ── OpenCL ───────────────────────────────────────────────────────
        cl_data = data["opencl"]
        if cl_data["supported"] and cl_data.get("platforms"):
            for platform in cl_data["platforms"]:
                platform_name = platform.get("name", "Unknown Platform")
                devices = platform.get("devices", [])

                for dev_index, dev in enumerate(devices):
                    # Column 1: Platform details
                    platform_col = [
                        ("Platform", platform_name),
                        ("Version", platform.get("version", "—")),
                        ("Profile", platform.get("profile", "—")),
                        ("Extensions", str(platform.get("extensions_count", 0))),
                    ]

                    # Column 2: Device details (part 1: from Device to OpenCL C Version)
                    dev_col_1 = [
                        ("Device", dev.get("name", "—")),
                        ("Vendor", dev.get("vendor", "—")),
                        ("Vendor ID", dev.get("vendor_id", "—")),
                        ("Device Type", dev.get("device_type", "—")),
                        ("Device Profile", dev.get("device_profile", "—")),
                        ("Device Version", dev.get("version", "—")),
                        ("Driver Version", dev.get("driver_version", "—")),
                        ("OpenCL C Version", dev.get("opencl_c_version", "—")),
                    ]

                    # Column 3: The rest of the device details
                    dev_col_2 = [
                        ("Extensions", str(dev.get("extensions_count", 0))),
                        ("Compute Units", str(dev.get("compute_units", "—"))),
                        ("Max Clock Freq", dev.get("max_clock", "—")),
                        ("Max Workgroup Size", str(dev.get("workgroup_size", "—"))),
                        ("Global Memory", str(dev.get("global_memory", "—"))),
                        ("Local Memory", str(dev.get("local_memory", "—"))),
                        ("Unified Memory", dev.get("unified_memory", "—")),
                        ("OpenCL C Features", str(dev.get("opencl_c_features_count", "—"))),
                        ("Conformance Test", dev.get("conformance_test", "—")),
                    ]

                    card_title = f"OpenCL – {platform_name} ({dev.get('name', '—')})"
                    card = _make_card(
                        card_title,
                        "../Images/OpenCL.svg",
                        [],
                        nav_page="opencl_page",
                        app=app,
                        supported=True,
                        content_widget=_make_grid_card_content([platform_col, dev_col_1, dev_col_2]),
                        gpu_index=dev_index,
                        card_id=f"opencl-{platform_name}-{dev_index}",
                        allow_reorder=True,
                        flow_box=flow_box,
                    )
                    card.set_size_request(250, -1)
                    flow_box.append(card)
                    add_summary_card(f"opencl-{platform_name}-{dev_index}", card)
        else:
            card = _make_card(
                "OpenCL",
                "../Images/OpenCL.svg",
                [], nav_page=None, app=app, supported=False,
                card_id="opencl-missing",
                allow_reorder=True,
                flow_box=flow_box,
            )
            card.set_size_request(250, -1)
            flow_box.append(card)
            add_summary_card("opencl-missing", card)

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
                card_id="vdpau",
                allow_reorder=True,
                flow_box=flow_box,
            )
        else:
            card = _make_card(
                "VDPAU", "../Images/vdpauinfo.png",
                [], nav_page=None, app=app, supported=False,
                card_id="vdpau-missing",
                allow_reorder=True,
                flow_box=flow_box,
            )
        card.set_size_request(250, -1)
        flow_box.append(card)
        add_summary_card("vdpau" if vd_data["supported"] else "vdpau-missing", card)

        restore_summary_card_order()

        outer.append(scroll)

        # Periodic statistics update
        def update_stats_callback():
            if not outer.get_mapped():
                return True
                
            def fetch_stats():
                try:
                    # System real-time stats
                    cpu_u = get_realtime_cpu_usage()
                    ram_u = get_realtime_ram_usage()
                    upt_u = get_realtime_uptime()

                    def apply_sys_updates(c=cpu_u, r=ram_u, u=upt_u):
                        if "CPU Usage" in sys_widgets and c != "—":
                            sys_widgets["CPU Usage"].set_subtitle(c)
                        if "RAM Usage" in sys_widgets and r != "—":
                            sys_widgets["RAM Usage"].set_subtitle(r)
                        if "Uptime" in sys_widgets and u != "—":
                            sys_widgets["Uptime"].set_subtitle(u)
                        return False

                    GLib.idle_add(apply_sys_updates)

                    for gpu_index, widgets in stats_widgets_list:
                        stats = get_gpu_stats_for_index(gpu_index)
                        if stats:
                            def apply_updates(w=widgets, s=stats):
                                mem_used = s.get("mem_used")
                                mem_total = s.get("mem_total")
                                if "VRAM" in w:
                                    if mem_used is not None and mem_total is not None and mem_total > 0:
                                        pct = (mem_used / mem_total) * 100.0 if mem_total else 0.0
                                        w["VRAM"].set_subtitle(f"{mem_used} / {mem_total} MB ({pct:.0f} %)")
                                if "VRAM Clock" in w:
                                    vram_clock = s.get("vram_clock")
                                    vram_clock_max = s.get("vram_clock_max")
                                    if vram_clock is not None and vram_clock > 0:
                                        if vram_clock_max is not None and vram_clock_max > 0:
                                            pct = (vram_clock / vram_clock_max) * 100.0 if vram_clock_max else 0.0
                                            w["VRAM Clock"].set_subtitle(f"{vram_clock} / {vram_clock_max} MHz ({pct:.0f} %)")
                                        else:
                                            w["VRAM Clock"].set_subtitle(f"{vram_clock} MHz")
                                if "GPU Usage" in w and s.get("usage") is not None:
                                    w["GPU Usage"].set_subtitle(f"{s['usage']} %" if s["usage"] >= 0 else "—")
                                if "Temperature" in w and s.get("temp") is not None:
                                    w["Temperature"].set_subtitle(f"{s['temp']} °C" if s["temp"] > 0 else "—")
                                if "GPU Clock" in w:
                                    clk_cur = s.get("clock_current")
                                    clk_max = s.get("clock_max")
                                    if clk_cur is not None and clk_cur > 0:
                                        clk_str = f"{clk_cur} / {clk_max} MHz" if clk_max and clk_max > 0 else f"{clk_cur} MHz"
                                        w["GPU Clock"].set_subtitle(clk_str)
                                if "Power" in w and s.get("power_usage") is not None:
                                    w["Power"].set_subtitle(f"{s['power_usage']} W" if s["power_usage"] > 0 else "—")
                                if "Fan Speed" in w and s.get("fan_speed") is not None:
                                    w["Fan Speed"].set_subtitle(f"{s['fan_speed']} %" if s["fan_speed"] >= 0 else "—")
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
