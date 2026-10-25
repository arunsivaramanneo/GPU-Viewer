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
from Common import getLogo, getGpuImage, get_gpu_stats, get_gpu_stats_for_index, fetchContentsFromCommand, CircularGauge, SparklineWidget
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
            elif stripped.startswith("conformanceVersion =") or stripped.startswith("conformanceVersion="):
                conformance_version = stripped.split("=", 1)[-1].strip()
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
            # Post-process: count supported formats by scanning 'Format Properties' section
            try:
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
            except Exception:
                formats_count = 0

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
            
            new_dev = {
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
            }

            # Deduplicate / merge device entries for Flatpak or multi-section outputs
            existing_dev = None
            for d in data["devices"]:
                if (device_uuid and d.get("device_uuid") and device_uuid == d["device_uuid"] and
                    (not d.get("name") or not device_name or d["name"] == device_name)):
                    existing_dev = d
                    break
                if (device_name and d.get("name") == device_name and
                    ((vendor_id and d.get("vendor_id") == vendor_id and device_id and d.get("device_id") == device_id) or
                     (not vendor_id or not d.get("vendor_id")))):
                    existing_dev = d
                    break
                if (vendor_id and device_id and d.get("vendor_id") == vendor_id and d.get("device_id") == device_id and
                    (not d.get("name") or not device_name or d["name"] == device_name)):
                    existing_dev = d
                    break

            if existing_dev is not None:
                for k in ("name", "api_version", "driver_name", "driver_version", "device_type",
                          "pipelineCacheUUID", "vendor_id", "device_id", "driver_info",
                          "device_uuid", "driver_uuid", "conformance_version"):
                    if not existing_dev.get(k) and new_dev.get(k):
                        existing_dev[k] = new_dev[k]
                for k in ("formats_count", "extensions_count", "memory_types_count",
                          "memory_heaps_count", "queue_count"):
                    existing_dev[k] = max(existing_dev.get(k, 0), new_dev.get(k, 0))
                
                merged_decode = sorted(set(existing_dev.get("video_decode_profiles", [])) | set(new_dev.get("video_decode_profiles", [])))
                merged_encode = sorted(set(existing_dev.get("video_encode_profiles", [])) | set(new_dev.get("video_encode_profiles", [])))
                existing_dev["video_decode_profiles"] = merged_decode
                existing_dev["video_encode_profiles"] = merged_encode
                existing_dev["video_profiles"] = sorted(set(merged_decode) | set(merged_encode))
                
                for codec, cnt in new_dev.get("video_decode_profile_counts", {}).items():
                    existing_dev.setdefault("video_decode_profile_counts", {})[codec] = max(
                        existing_dev.get("video_decode_profile_counts", {}).get(codec, 0), cnt
                    )
                for codec, cnt in new_dev.get("video_encode_profile_counts", {}).items():
                    existing_dev.setdefault("video_encode_profile_counts", {})[codec] = max(
                        existing_dev.get("video_encode_profile_counts", {}).get(codec, 0), cnt
                    )
            else:
                data["devices"].append(new_dev)

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
            # Exclude connector symlinks like card1-DP-1 or card1-eDP-1
            if not re.fullmatch(r'card\d+', card_name):
                continue
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
            subsystem_vendor = ""
            subsystem_device = ""
            revision = ""
            vram_vendor = ""
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

            # Subsystem Vendor & Device ID
            if os.path.exists(f"{device_path}/subsystem_vendor"):
                try:
                    with open(f"{device_path}/subsystem_vendor", "r") as f:
                        subsystem_vendor = f.read().strip()
                except Exception:
                    pass
            if os.path.exists(f"{device_path}/subsystem_device"):
                try:
                    with open(f"{device_path}/subsystem_device", "r") as f:
                        subsystem_device = f.read().strip()
                except Exception:
                    pass

            # Revision
            if os.path.exists(f"{device_path}/revision"):
                try:
                    with open(f"{device_path}/revision", "r") as f:
                        revision = f.read().strip()
                except Exception:
                    pass

            # VRAM Vendor (AMD sysfs mem_info_vram_vendor)
            if os.path.exists(f"{device_path}/mem_info_vram_vendor"):
                try:
                    with open(f"{device_path}/mem_info_vram_vendor", "r") as f:
                        raw_v_vendor = f.read().strip()
                        if raw_v_vendor:
                            vram_vendor = raw_v_vendor.title()
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
            
            if not vendor_id and not device_id:
                continue

            gpu_info = {
                "card_index": card_index,
                "card_name": card_name,
                "vendor_id": vendor_id,
                "device_id": device_id,
                "subsystem_vendor": subsystem_vendor,
                "subsystem_device": subsystem_device,
                "revision": revision,
                "vram_vendor": vram_vendor,
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
_net_last_bytes = {}      # {iface: (rx_bytes, tx_bytes, timestamp)}


def get_realtime_net_speed() -> tuple[float, float]:
    """Return (download_Mbps, upload_Mbps) summed across all active non-loopback interfaces.

    Reads /proc/net/dev and computes byte-deltas since the last call.
    Returns (0.0, 0.0) when there is not yet enough history (first call) or on error.
    """
    global _net_last_bytes
    import time
    try:
        now = time.monotonic()
        rx_total = 0
        tx_total = 0
        with open("/proc/net/dev", "r") as f:
            lines = f.readlines()
        current = {}
        for line in lines[2:]:          # skip the two header lines
            parts = line.split(":")
            if len(parts) < 2:
                continue
            iface = parts[0].strip()
            if iface == "lo":           # skip loopback
                continue
            fields = parts[1].split()
            if len(fields) < 9:
                continue
            rx_bytes = int(fields[0])
            tx_bytes = int(fields[8])
            current[iface] = (rx_bytes, tx_bytes)

        down_mbps = 0.0
        up_mbps   = 0.0
        for iface, (rx, tx) in current.items():
            if iface in _net_last_bytes:
                prev_rx, prev_tx, prev_t = _net_last_bytes[iface]
                dt = now - prev_t
                if dt > 0:
                    down_mbps += max(0.0, (rx - prev_rx) / dt) / 1e6 * 8  # bytes/s → Mbit/s
                    up_mbps   += max(0.0, (tx - prev_tx) / dt) / 1e6 * 8
            _net_last_bytes[iface] = (rx, tx, now)

        # Prune disappeared interfaces
        for iface in list(_net_last_bytes.keys()):
            if iface not in current:
                del _net_last_bytes[iface]

        return (down_mbps, up_mbps)
    except Exception:
        return (0.0, 0.0)


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
                num_cpus = 0
                cpu_root = "/sys/devices/system/cpu"
                for cpu_dir in glob.glob(os.path.join(cpu_root, "cpu[0-9]*", "cpufreq")):
                    cur_path = os.path.join(cpu_dir, "scaling_cur_freq")
                    max_path = os.path.join(cpu_dir, "scaling_max_freq")
                    try:
                        if os.path.exists(cur_path):
                            total_cur_khz += float(open(cur_path, "r", encoding="utf-8").read().strip())
                            num_cpus += 1
                        if os.path.exists(max_path):
                            total_max_khz += float(open(max_path, "r", encoding="utf-8").read().strip())
                    except Exception:
                        continue

                if total_max_khz > 0 and num_cpus > 0:
                    avg_cur_khz = total_cur_khz / num_cpus
                    avg_max_khz = total_max_khz / num_cpus
                    cur_ghz = avg_cur_khz / 1000000.0
                    max_ghz = avg_max_khz / 1000000.0
                    return f"{cur_ghz:.2f} GHz / {max_ghz:.2f} GHz ({usage:.0f} %)"
                elif total_cur_khz > 0 and num_cpus > 0:
                    avg_cur_khz = total_cur_khz / num_cpus
                    cur_ghz = avg_cur_khz / 1000000.0
                    return f"{cur_ghz:.2f} GHz ({usage:.0f} %)"
                else:
                    try:
                        mhz_list = []
                        with open("/proc/cpuinfo", "r") as f:
                            for line in f:
                                if line.startswith("cpu MHz"):
                                    mhz_list.append(float(line.split(":")[1].strip()))
                        if mhz_list:
                            avg_mhz = sum(mhz_list) / len(mhz_list)
                            cur_ghz = avg_mhz / 1000.0
                            return f"{cur_ghz:.2f} GHz ({usage:.0f} %)"
                    except Exception:
                        pass
                return f"{usage:.0f} %"
    except Exception:
        pass
    return "—"


def _get_cpu_cache_info() -> str:
    """Return CPU cache details as a semicolon-separated string for tree row display.
    e.g. 'L1 Data Cache: 32 KiB; L1 Instruction Cache: 32 KiB; L2 Cache: 512 KiB; L3 Cache: 16 MiB'
    """
    caches = []
    try:
        index_dirs = sorted(glob.glob("/sys/devices/system/cpu/cpu0/cache/index*"))
        if index_dirs:
            for d in index_dirs:
                level_path = os.path.join(d, "level")
                type_path = os.path.join(d, "type")
                size_path = os.path.join(d, "size")
                if os.path.exists(level_path) and os.path.exists(size_path):
                    with open(level_path, "r", encoding="utf-8") as f:
                        level = f.read().strip()
                    with open(size_path, "r", encoding="utf-8") as f:
                        size = f.read().strip()
                    
                    ctype = ""
                    if os.path.exists(type_path):
                        with open(type_path, "r", encoding="utf-8") as f:
                            ctype = f.read().strip()
                    
                    if level == "1" and ctype.lower() == "data":
                        name = "L1 Data Cache"
                    elif level == "1" and ctype.lower() == "instruction":
                        name = "L1 Instruction Cache"
                    elif ctype and ctype.lower() != "unified":
                        name = f"L{level} {ctype.capitalize()} Cache"
                    else:
                        name = f"L{level} Cache"
                    
                    if size.endswith("K") or size.endswith("k"):
                        try:
                            k_val = int(size[:-1])
                            if k_val >= 1024 and k_val % 1024 == 0:
                                size_formatted = f"{k_val // 1024} MiB"
                            else:
                                size_formatted = f"{k_val} KiB"
                        except Exception:
                            size_formatted = f"{size[:-1]} KiB"
                    elif size.endswith("M") or size.endswith("m"):
                        size_formatted = f"{size[:-1]} MiB"
                    elif size.endswith("G") or size.endswith("g"):
                        size_formatted = f"{size[:-1]} GiB"
                    else:
                        size_formatted = size
                    
                    caches.append(f"{name}: {size_formatted}")
    except Exception:
        pass

    if caches:
        return " ; ".join(caches)

    try:
        res = subprocess.run(
            ["lscpu"], capture_output=True, text=True, timeout=3
        )
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                if "cache:" in line.lower():
                    parts = line.split(":", 1)
                    k_str = parts[0].strip()
                    v_str = parts[1].strip()
                    if k_str.lower().startswith("l1d"):
                        k_str = "L1 Data Cache"
                    elif k_str.lower().startswith("l1i"):
                        k_str = "L1 Instruction Cache"
                    elif k_str.lower().startswith("l2"):
                        k_str = "L2 Cache"
                    elif k_str.lower().startswith("l3"):
                        k_str = "L3 Cache"
                    caches.append(f"{k_str}: {v_str}")
    except Exception:
        pass

    if caches:
        return " ; ".join(caches)

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


def get_realtime_cpu_temp() -> int | None:
    """Return CPU temperature in °C from hwmon coretemp/k10temp/zenpower/acpitz."""
    try:
        for hw in glob.glob("/sys/class/hwmon/hwmon*"):
            name = ""
            name_file = os.path.join(hw, "name")
            if os.path.exists(name_file):
                try:
                    with open(name_file, "r") as fp:
                        name = fp.read().strip()
                except Exception:
                    pass
            if any(k in name.lower() for k in ["coretemp", "k10temp", "zenpower", "cpu_thermal", "acpitz", "tctl", "tdie"]):
                for tf in sorted(glob.glob(os.path.join(hw, "temp*_input"))):
                    try:
                        with open(tf, "r") as fp:
                            val = int(fp.read().strip()) // 1000
                        if 0 < val < 130:
                            return val
                    except Exception:
                        pass
    except Exception:
        pass
    return None


def get_realtime_swap_usage() -> str:
    """Return Swap usage formatted as 'X.X GB / Y.Y GB (Z %)'."""
    try:
        total = 0
        free = 0
        with open("/proc/meminfo", "r") as fp:
            for line in fp:
                if line.startswith("SwapTotal:"):
                    total = int(line.split()[1])
                elif line.startswith("SwapFree:"):
                    free = int(line.split()[1])
        if total > 0:
            used = total - free
            pct = (used / total) * 100.0
            used_gb = used / (1024 * 1024)
            total_gb = total / (1024 * 1024)
            return f"{used_gb:.1f} GB / {total_gb:.1f} GB ({pct:.0f} %)"
    except Exception:
        pass
    return "—"


def _parse_system() -> dict:
    """Return basic system info (OS, CPU, RAM, Kernel, Desktop, plus detailed BIOS, Uptime, etc.)."""
    info = {
        "os": "",
        "cpu": "",
        "cpu_cores_threads": "—",
        "cpu_cache": "—",
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

    info["cpu_cache"] = _get_cpu_cache_info()
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
# Metric descriptions / tooltips
# ---------------------------------------------------------------------------

METRIC_TOOLTIPS = {
    # Gauges & Real-Time Performance
    "VRAM": "Video RAM (Dedicated GPU Memory) — Percentage and amount of dedicated on-board graphics memory currently in use.",
    "VRAM Clock": "VRAM Memory Frequency — Operating clock speed of the dedicated video memory in MHz relative to its maximum frequency.",
    "Mem Bus": "Memory Controller Activity — Percentage of time the GPU memory interface and controller are actively transferring data.",
    "GTT Memory": "Graphics Translation Table / Shared Memory — System RAM allocated and used by the GPU as shared memory space.",
    "GPU Usage": "GPU Core Utilization — Percentage of graphics processing units and compute engines actively executing workloads.",
    "Temp": "GPU Core Temperature — Thermal reading of the graphics processor core sensor in Celsius (°C).",
    "Hotspot": "GPU Hotspot / Junction Temperature — Peak temperature measured among all localized sensors across the GPU die in Celsius (°C).",
    "GPU Clock": "GPU Core Frequency — Current operating frequency of the graphics core in MHz relative to maximum boost clock.",
    "Voltage": "GPU Core Voltage — Real-time electrical voltage supplied to the graphics processor in Volts (V).",
    "Power": "GPU Power Consumption — Real-time electrical power draw of the graphics card in Watts (W).",
    "Fan Speed": "Cooling Fan Speed — Current cooling fan speed as a percentage of maximum PWM duty cycle and revolutions per minute (RPM).",
    "CPU Usage": "Processor Utilization — Total central processor workload across all cores/threads and current operating frequency.",
    "CPU Temp": "Processor Temperature — Thermal package/core temperature of the central processor in Celsius (°C).",
    "RAM Usage": "System Memory — Amount and percentage of physical RAM currently allocated and in use.",
    "Swap": "Swap Space — Amount and percentage of virtual disk swap space utilized by the system.",
    "Net Down": "Network Download Speed — Real-time inbound data rate summed across all active network interfaces in Mbit/s.",
    "Net Up": "Network Upload Speed — Real-time outbound data rate summed across all active network interfaces in Mbit/s.",

    # System Information
    "Operating System": "Current Linux operating system distribution and version.",
    "Processor": "Central Processing Unit (CPU) model and architecture specifications.",
    "CPU Cores / Threads": "Number of physical CPU cores and logical hardware threads.",
    "CPU Cache": "Hardware cache hierarchy (L1 Data, L1 Instruction, L2, and L3 caches).",
    "Kernel": "Linux kernel version currently running.",
    "Architecture": "CPU instruction set architecture (e.g. x86_64, aarch64).",
    "Hostname": "System network hostname.",
    "Uptime": "Total elapsed time since the system was booted.",
    "CPU Temperature": "Thermal package/core temperature of the central processor in Celsius (°C).",
    "Swap Usage": "Amount and percentage of virtual disk swap memory currently utilized.",
    "Hardware Model": "Computer motherboard or chassis hardware model identifier.",
    "BIOS Info": "System BIOS / UEFI firmware version and release date.",
    "Desktop / Session": "Current desktop environment and windowing protocol (Wayland / X11).",
    "Disk Capacity": "Total available storage space across mounted storage partitions.",
    "Hard Drives": "Detected storage drives and solid-state disks.",
    "Display": "Connected monitor displays and output screen resolutions.",

    # GPU Card Details
    "Card": "Operating system DRM device node identifier (e.g. card0, card1).",
    "PCI Address": "PCI Express bus, device, and function address identifier of the graphics card.",
    "PCIe Link Speed": "Current negotiated PCIe link transfer speed (e.g. 8.0 GT/s PCIe Gen 3 / Gen 4).",
    "PCIe Link Width": "Current negotiated PCIe lane width (e.g. x16, x8, x4).",
    "Driver": "Active kernel and userspace graphics driver.",
    "VBIOS Version": "Video BIOS firmware version installed on the graphics card.",
    "Vendor / Device ID": "PCI Vendor ID and Device ID assigned by the hardware manufacturer.",
    "Subsystem ID": "PCI Subsystem Vendor and Subsystem Device ID identifying the specific board or OEM model.",
    "Revision": "Hardware silicon revision / stepping of the graphics processor die.",
    "VRAM Total": "Total physical dedicated video memory (VRAM) installed on the graphics card.",
    "VRAM Type": "Memory technology generation used for video RAM (e.g. GDDR6, GDDR5, HBM2, DDR4).",
    "VRAM Vendor": "Manufacturer of the onboard video memory chips (e.g. Samsung, Micron, SK Hynix).",
    "GTT / Shared Memory": "Total Graphics Translation Table (GTT) / system RAM shared with the GPU.",
    "Max Core Clock": "Maximum engine / boost operating frequency of the graphics core in MHz.",
    "Max Memory Clock": "Maximum operating frequency of the video memory (VRAM) in MHz.",
    "Compute Units": "Number of hardware compute units / streaming multiprocessors / execution units.",
    "ROPs": "Render Output Units (Raster Operations Pipelines) responsible for final pixel processing.",
    "Architecture": "GPU microarchitecture or instruction set family.",
    "Device UUID": "Universally Unique Identifier (UUID) of the physical graphics device.",

    # Subsystems
    "API Version": "Supported application programming interface version specification.",
    "Driver Version": "Graphics driver release build version.",
    "Instance Version": "Vulkan loader and instance runtime version.",
    "Extensions": "Number of supported driver and API extension modules.",
    "Vulkan Formats": "Number of supported image, texture, and buffer pixel formats.",
    "Device Type": "Classification of the graphics device (Discrete GPU, Integrated GPU, CPU, etc.).",
    "GLSL Version": "OpenGL Shading Language version supported by the driver.",
    "Renderer": "Active graphics rendering device name reported by the driver.",
    "Vendor": "Hardware manufacturer or graphics driver vendor.",
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

    tooltip = METRIC_TOOLTIPS.get(title)
    if tooltip:
        box.set_tooltip_text(tooltip)

    # Title label with wrapping enabled
    title_label = Gtk.Label(label=title)
    title_label.add_css_class("body")
    title_label.set_halign(Gtk.Align.START)
    title_label.set_wrap(True)
    title_label.set_wrap_mode(Pango.WrapMode.WORD)
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
        value_label.set_wrap_mode(Pango.WrapMode.WORD)
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

    # Copy button
    copy_btn = Gtk.Button()
    copy_btn.set_icon_name("edit-copy-symbolic")
    copy_btn.add_css_class("flat")
    copy_btn.set_valign(Gtk.Align.CENTER)
    copy_btn.set_tooltip_text("Copy to clipboard")
    copy_btn.set_opacity(0.6)

    def _on_copy_clicked(_btn, title=title, box_ref=box):
        values = [lbl.get_label() for lbl in box_ref.subtitle_labels
                  if hasattr(lbl, 'get_label') and lbl.get_label() not in ('—', '')]
        clip_text = f"{title}: {', '.join(values)}" if values else title
        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.set(clip_text)
    copy_btn.connect("clicked", _on_copy_clicked)

    # Outer horizontal wrapper
    outer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
    box.set_hexpand(True)
    outer_box.append(box)
    outer_box.append(copy_btn)
    # Copy attributes from inner box to outer box for compatibility
    outer_box.subtitle_labels = box.subtitle_labels
    outer_box.set_subtitle = box.set_subtitle
    outer_box.subtitle_label = box.subtitle_label
    return outer_box


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


def _move_card_in_registry(registry, card_id: str, target_index: int | str):
    if not registry:
        return registry
    current_order = [entry_card_id for entry_card_id, _ in registry]
    if card_id not in current_order:
        return registry
    source_index = current_order.index(card_id)
    if isinstance(target_index, str):
        if target_index in current_order:
            target_index = current_order.index(target_index)
        else:
            return registry
    new_index = max(0, min(len(current_order) - 1, target_index))
    if source_index == new_index:
        return registry
    new_order = current_order[:]
    moved = new_order.pop(source_index)
    new_order.insert(new_index, moved)
    widget_map = {entry_card_id: widget for entry_card_id, widget in registry}
    return [(entry_card_id, widget_map[entry_card_id]) for entry_card_id in new_order]


def _apply_registry_order(flow_box, registry):
    if flow_box is None or not registry:
        return
    if hasattr(flow_box, "apply_reorder"):
        flow_box.apply_reorder(registry)
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

_active_popout_windows = {}

def _make_section_header(title: str, icon_name: str, subtitle: str = "") -> Gtk.Box:
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    box.set_margin_top(16)
    box.set_margin_bottom(8)
    box.set_margin_start(4)
    box.set_margin_end(4)

    icon = Gtk.Image.new_from_icon_name(icon_name)
    icon.set_pixel_size(18)
    box.append(icon)

    lbl = Gtk.Label(label=title)
    lbl.add_css_class("title-4")
    lbl.add_css_class("summary-tier-header")
    lbl.set_halign(Gtk.Align.START)
    box.append(lbl)

    if subtitle:
        sub = Gtk.Label(label=subtitle)
        sub.add_css_class("dim-label")
        sub.add_css_class("caption")
        sub.set_halign(Gtk.Align.START)
        sub.set_margin_start(6)
        box.append(sub)

    return box


class SummaryDashboard(Gtk.Box):
    """
    Structured 3-Tier Executive Dashboard container for the Summary Tab.
    Tier 1: Executive Overview (System & GPU Hardware)
    Tier 2: Real-Time Telemetry & Performance
    Tier 3: Graphics & Compute Subsystems
    """
    def __init__(self, app=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.app = app
        self.set_margin_start(16)
        self.set_margin_end(16)
        self.set_margin_top(14)
        self.set_margin_bottom(24)
        self.set_vexpand(True)
        self.set_hexpand(True)

        self._summary_card_registry = []
        self._summary_card_titles = {}
        self._tier_cards = {1: [], 2: [], 3: []}

        # ── Tier 1: Executive Overview ──────────────────────────────────
        self.tier1_header = _make_section_header("System & Hardware Overview", "computer-symbolic")
        self.append(self.tier1_header)

        self.tier1_flow = Gtk.FlowBox()
        self.tier1_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.tier1_flow.set_max_children_per_line(2)
        self.tier1_flow.set_min_children_per_line(1)
        self.tier1_flow.set_row_spacing(12)
        self.tier1_flow.set_column_spacing(12)
        self.tier1_flow.set_homogeneous(True)
        self.tier1_flow.set_hexpand(True)
        self.append(self.tier1_flow)

        # ── Tier 2: Real-Time Telemetry ─────────────────────────────────
        self.tier2_header = _make_section_header("Real-Time Telemetry & Performance", "utilities-system-monitor-symbolic", "• Live monitoring")
        self.append(self.tier2_header)

        self.tier2_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.tier2_box.set_hexpand(True)
        self.append(self.tier2_box)

        # ── Tier 3: Graphics & Compute Subsystems ───────────────────────
        self.tier3_header = _make_section_header("Graphics & Compute APIs", "applications-graphics-symbolic", "• Subsystem capabilities & drivers")
        self.append(self.tier3_header)

        self.tier3_flow = Gtk.FlowBox()
        self.tier3_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.tier3_flow.set_max_children_per_line(2)
        self.tier3_flow.set_min_children_per_line(1)
        self.tier3_flow.set_row_spacing(12)
        self.tier3_flow.set_column_spacing(12)
        self.tier3_flow.set_homogeneous(False)
        self.tier3_flow.set_hexpand(True)
        self.append(self.tier3_flow)

        self._tier_containers = {
            1: self.tier1_flow,
            2: self.tier2_box,
            3: self.tier3_flow,
        }
        self._sections = [
            (self.tier1_header, self.tier1_flow, 1),
            (self.tier2_header, self.tier2_box, 2),
            (self.tier3_header, self.tier3_flow, 3),
        ]

    def add_card(self, tier: int, card_id: str, widget: Gtk.Widget):
        if not card_id or widget is None:
            return widget
        if widget not in [w for _, w in self._summary_card_registry]:
            self._summary_card_registry.append((card_id, widget))
            self._summary_card_titles[card_id] = getattr(widget, "_summary_card_title", card_id)
            self._tier_cards[tier].append((card_id, widget))
            container = self._tier_containers[tier]
            container.append(widget)
        return widget

    def refresh_display(self, app=None):
        saved_order = app.config.get_summary_card_order() if app is not None and hasattr(app, "config") else []

        for tier in (1, 2, 3):
            tier_entries = self._tier_cards[tier]
            if saved_order:
                def _sort_key(item):
                    c_id = item[0]
                    return saved_order.index(c_id) if c_id in saved_order else 999
                tier_entries.sort(key=_sort_key)

            visible_count = 0
            for card_id, widget in tier_entries:
                is_popped_out = card_id in _active_popout_windows
                parent = widget.get_parent()
                target_to_hide = parent if isinstance(parent, Gtk.FlowBoxChild) else widget
                if is_popped_out:
                    target_to_hide.set_visible(False)
                else:
                    target_to_hide.set_visible(True)
                    visible_count += 1

            header, container, _ = self._sections[tier - 1]
            header.set_visible(visible_count > 0)
            container.set_visible(visible_count > 0)

    def apply_reorder(self, reordered_registry):
        self._summary_card_registry = list(reordered_registry)
        ordered_ids = [c_id for c_id, _ in reordered_registry]
        widget_by_id = {c_id: w for c_id, w in reordered_registry}

        for tier in (1, 2, 3):
            tier_ids = [c_id for c_id, _ in self._tier_cards[tier] if c_id in widget_by_id]
            sorted_tier_ids = sorted(
                tier_ids,
                key=lambda c_id: ordered_ids.index(c_id) if c_id in ordered_ids else 999
            )
            self._tier_cards[tier] = [(c_id, widget_by_id[c_id]) for c_id in sorted_tier_ids]

            container = self._tier_containers[tier]
            for c_id in sorted_tier_ids:
                w = widget_by_id[c_id]
                parent = w.get_parent()
                if parent is not None:
                    if hasattr(parent, "set_child"):
                        parent.set_child(None)
                    else:
                        w.unparent()

            if hasattr(container, "remove_all"):
                container.remove_all()
            else:
                child = container.get_first_child()
                while child is not None:
                    next_c = child.get_next_sibling()
                    container.remove(child)
                    child = next_c

            for c_id in sorted_tier_ids:
                if c_id not in _active_popout_windows:
                    w = widget_by_id[c_id]
                    parent = w.get_parent()
                    if parent is not None:
                        if hasattr(parent, "set_child"):
                            parent.set_child(None)
                        else:
                            w.unparent()
                    container.append(w)

    def apply_search(self, query: str, app_instance=None):
        query_lower = query.strip().lower()
        for tier in (1, 2, 3):
            tier_entries = self._tier_cards[tier]
            visible_count = 0
            for card_id, widget in tier_entries:
                parent = widget.get_parent()
                target = parent if isinstance(parent, Gtk.FlowBoxChild) else widget
                if card_id in _active_popout_windows:
                    target.set_visible(False)
                    continue

                card_title = getattr(widget, "_summary_card_title", "").lower()
                if not query_lower:
                    self._set_widget_tree_visible(widget)
                    target.set_visible(True)
                    visible_count += 1
                elif query_lower in card_title:
                    self._set_widget_tree_visible(widget)
                    target.set_visible(True)
                    visible_count += 1
                else:
                    matched = self._search_card(widget, query_lower)
                    target.set_visible(matched)
                    if matched:
                        visible_count += 1

            header, container, _ = self._sections[tier - 1]
            header.set_visible(visible_count > 0)
            container.set_visible(visible_count > 0)

    def _search_card(self, card_widget, query_lower: str) -> bool:
        if not query_lower:
            self._set_widget_tree_visible(card_widget)
            return True
        card_box = card_widget.get_child() if hasattr(card_widget, "get_child") else None
        if card_box is None:
            return True
        any_match = False
        child = card_box.get_first_child()
        while child is not None:
            if self._search_widget(child, query_lower):
                any_match = True
            child = child.get_next_sibling()
        return any_match

    def _search_widget(self, widget, query_lower: str) -> bool:
        if isinstance(widget, Gtk.Box) and hasattr(widget, "subtitle_labels"):
            title_text = ""
            inner = widget.get_first_child()
            if inner is not None and isinstance(inner, Gtk.Box):
                t_lbl = inner.get_first_child()
                if t_lbl and hasattr(t_lbl, "get_label"):
                    title_text = t_lbl.get_label().lower()
            elif inner is not None and hasattr(inner, "get_label"):
                title_text = inner.get_label().lower()

            value_texts = " ".join(
                lbl.get_label().lower() for lbl in widget.subtitle_labels
                if hasattr(lbl, "get_label")
            )
            matched = query_lower in title_text or query_lower in value_texts
            widget.set_visible(matched)
            return matched

        any_match = False
        child = widget.get_first_child()
        while child is not None:
            if self._search_widget(child, query_lower):
                any_match = True
            child = child.get_next_sibling()
        return any_match

    def _set_widget_tree_visible(self, widget):
        if isinstance(widget, Gtk.Box) and hasattr(widget, "subtitle_labels"):
            widget.set_visible(True)
            return
        child = widget.get_first_child()
        while child is not None:
            self._set_widget_tree_visible(child)
            child = child.get_next_sibling()


def _refresh_flow_box_display(flow_box: Gtk.FlowBox | None, app=None):
    """Refresh flow_box / dashboard display to show all cards except those currently popped out."""
    if flow_box is None:
        return
    if hasattr(flow_box, "refresh_display"):
        flow_box.refresh_display(app)
        return
    registry = list(getattr(flow_box, "_summary_card_registry", []))
    if not registry:
        return
    widget_by_id = {widget_id: widget for widget_id, widget in registry}
    current_order = [widget_id for widget_id, _ in registry]
    saved_order = app.config.get_summary_card_order() if app is not None and hasattr(app, "config") else []
    order_to_use = saved_order if saved_order else current_order
    ordered_ids = [card_id for card_id in order_to_use if card_id in widget_by_id]
    for card_id in current_order:
        if card_id not in ordered_ids:
            ordered_ids.append(card_id)
    
    # Detach card widgets from existing parent FlowBoxChild containers to prevent GTK4 critical assertion errors
    for _, widget in registry:
        if widget is not None:
            parent = widget.get_parent()
            if parent is not None:
                if hasattr(parent, "set_child"):
                    parent.set_child(None)
                else:
                    widget.unparent()

    flow_box.remove_all()
    for card_id in ordered_ids:
        if card_id not in _active_popout_windows:
            widget = widget_by_id[card_id]
            parent = widget.get_parent()
            if parent is not None:
                if hasattr(parent, "set_child"):
                    parent.set_child(None)
                else:
                    widget.unparent()
            flow_box.append(widget)


def _open_card_in_separate_window(title: str, icon_name: str, rows: list = None,
                                   content_widget: Gtk.Widget | None = None,
                                   columns_data: list[list[tuple[str, str]]] | None = None,
                                   content_builder=None,
                                   supported: bool = True,
                                   app = None,
                                   parent_row_widgets: dict = None,
                                   card_id: str | None = None,
                                   card_widget: Gtk.Widget | None = None,
                                   flow_box = None,
                                   gpu_index: int | None = None):
    """Open a card in a separate standalone window."""
    if card_id and card_id in _active_popout_windows:
        _active_popout_windows[card_id]["window"].present()
        return

    win = Adw.Window()
    win.set_title(f"{title} - GPU-Viewer")
    
    headerbar = Adw.HeaderBar.new()
    headerbar.add_css_class(css_class='compact')
    
    # Dock to Main button in top bar
    dock_btn = Gtk.Button()
    dock_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    dock_img = Gtk.Image.new_from_icon_name("window-restore-symbolic")
    dock_label = Gtk.Label(label="Dock to Main")
    dock_box.append(dock_img)
    dock_box.append(dock_label)
    dock_btn.set_child(dock_box)
    dock_btn.add_css_class("flat")
    dock_btn.add_css_class("suggested-action")
    dock_btn.set_tooltip_text(f"Return {title} card to main window")
    headerbar.pack_start(dock_btn)

    title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    try:
        icon_pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_name, 18, 18, True)
        icon_img = Gtk.Picture.new_for_pixbuf(icon_pb)
        title_box.append(icon_img)
    except Exception:
        icon_img = Gtk.Image.new_from_icon_name("application-x-executable-symbolic")
        icon_img.set_pixel_size(18)
        title_box.append(icon_img)
    
    title_label = Gtk.Label(label=title)
    title_label.add_css_class("title-4")
    title_box.append(title_label)
    headerbar.set_title_widget(title_box)

    toolbar_view = Adw.ToolbarView.new()
    toolbar_view.add_top_bar(headerbar)
    win.set_content(toolbar_view)

    scroll = Gtk.ScrolledWindow()
    scroll.set_vexpand(True)
    scroll.set_hexpand(True)
    scroll.set_margin_start(16)
    scroll.set_margin_end(16)
    scroll.set_margin_top(16)
    scroll.set_margin_bottom(16)
    toolbar_view.set_content(scroll)

    card_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    scroll.set_child(card_container)

    popout_widgets = {}
    popout_gauges = {}

    if content_builder and supported:
        try:
            card_container.append(content_builder(popout_widgets, popout_gauges))
        except TypeError:
            card_container.append(content_builder(popout_widgets))
    elif columns_data and supported:
        content = _make_grid_card_content(columns_data, row_widgets_out=popout_widgets)
        card_container.append(content)
    elif rows and supported:
        for r_title, r_sub in rows:
            rw = _make_action_row(r_title, r_sub)
            card_container.append(rw)
            popout_widgets[r_title] = rw
    elif not supported:
        no_row = Adw.ActionRow()
        no_row.set_title("Status")
        no_row.set_subtitle("This subsystem was not detected on your system.")
        card_container.append(no_row)
    elif content_widget is not None:
        card_container.append(content_widget)

    key = card_id if card_id else f"popout-{id(win)}"
    popout_info = {
        "window": win,
        "card_widget": card_widget,
        "flow_box": flow_box,
        "widgets": popout_widgets,
        "gauges": popout_gauges,
        "gpu_index": gpu_index,
        "app": app,
        "docked": False,
    }
    _active_popout_windows[key] = popout_info

    def dock_back(focus_main=True):
        if not popout_info["docked"]:
            popout_info["docked"] = True
            _active_popout_windows.pop(key, None)
            if flow_box is not None:
                _refresh_flow_box_display(flow_box, app)
            if focus_main and app and hasattr(app, "window") and app.window:
                app.window.present()
            win.close()

    dock_btn.connect("clicked", lambda _: dock_back(focus_main=True))

    def on_popout_closed(window):
        if not popout_info["docked"]:
            dock_back(focus_main=True)
        return False

    win.connect("close-request", on_popout_closed)

    # Hide card from main window flow_box layout
    if flow_box is not None:
        _refresh_flow_box_display(flow_box, app)

    # Dynamic sizing based on number of columns to prevent awkward text wrapping
    num_cols = len(columns_data) if columns_data else (1 if rows else 2)
    if num_cols <= 1:
        default_w, default_h = 600, 480
    elif num_cols == 2:
        default_w, default_h = 820, 520
    elif num_cols == 3:
        default_w, default_h = 1040, 580
    else:
        default_w, default_h = 1240, 640

    win.set_default_size(default_w, default_h)
    win.set_size_request(550, 400)
    win.present()



def _usage_percent(value):
    if value is None:
        return 0.0
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*%", str(value))
    return float(match.group(1)) if match else 0.0


def _update_gauge_dict(gw: dict, s: dict = None, cpu_usage=None, ram_usage=None, cpu_temp=None, swap_usage=None,
                       net_down_mbps: float = None, net_up_mbps: float = None):
    """Update a dictionary of CircularGauge instances from stats, CPU usage, RAM usage, CPU temp, and Swap."""
    if not gw:
        return
    if s:
        mem_used = s.get("mem_used")
        mem_total = s.get("mem_total")
        gtt_used = s.get("gtt_used")
        gtt_total = s.get("gtt_total")
        vram_clock = s.get("vram_clock")
        vram_clock_max = s.get("vram_clock_max")
        clk_cur = s.get("clock_current")
        clk_max = s.get("clock_max")
        voltage = s.get("voltage")
        temp_hotspot = s.get("temp_hotspot")
        mem_busy = s.get("mem_busy")
        fan_rpm = s.get("fan_rpm")

        if mem_total and mem_total > 0 and "VRAM" in gw:
            vram_pct = (mem_used / mem_total * 100.0) if mem_used else 0
            gw["VRAM"].set_value(vram_pct, subtitle=f"{mem_used}/{mem_total}MB")
            if "VRAM__spark" in gw:
                gw["VRAM__spark"].push_value(vram_pct)

        if "VRAM Clock" in gw:
            if vram_clock and vram_clock > 0:
                vc_pct = (vram_clock / vram_clock_max * 100.0) if (vram_clock_max and vram_clock_max > 0) else 0
                vc_sub = f"{vram_clock}/{vram_clock_max}MHz" if (vram_clock_max and vram_clock_max > 0) else f"{vram_clock}MHz"
                gw["VRAM Clock"].set_value(vc_pct, subtitle=vc_sub, max_value=100.0)
            else:
                gw["VRAM Clock"].set_value(0, subtitle="N/A")
            if "VRAM Clock__spark" in gw:
                gw["VRAM Clock__spark"].push_value(vc_pct if (vram_clock and vram_clock > 0) else 0)

        if "Mem Bus" in gw and mem_busy is not None and mem_busy >= 0:
            gw["Mem Bus"].set_value(mem_busy)
            if "Mem Bus__spark" in gw:
                gw["Mem Bus__spark"].push_value(float(mem_busy))

        if gtt_total and gtt_total > 0 and "GTT Memory" in gw:
            gtt_pct = (gtt_used / gtt_total * 100.0) if gtt_used else 0
            gw["GTT Memory"].set_value(gtt_pct, subtitle=f"{gtt_used}/{gtt_total}MB")
            if "GTT Memory__spark" in gw:
                gw["GTT Memory__spark"].push_value(gtt_pct)

        if "GPU Usage" in gw and s.get("usage") is not None and s["usage"] >= 0:
            gw["GPU Usage"].set_value(s["usage"])
            if "GPU Usage__spark" in gw:
                gw["GPU Usage__spark"].push_value(float(s["usage"]))

        if "Temp" in gw and s.get("temp") is not None and s["temp"] > 0:
            gw["Temp"].set_value(s["temp"])
            if "Temp__spark" in gw:
                gw["Temp__spark"].push_value(s["temp"] / 110.0 * 100.0)

        if "Hotspot" in gw and temp_hotspot is not None and temp_hotspot > 0:
            gw["Hotspot"].set_value(temp_hotspot)
            if "Hotspot__spark" in gw:
                gw["Hotspot__spark"].push_value(temp_hotspot / 120.0 * 100.0)

        if "GPU Clock" in gw:
            if clk_cur and clk_cur > 0:
                clk_pct = (clk_cur / clk_max * 100.0) if (clk_max and clk_max > 0) else 0
                clk_sub = f"{clk_cur}/{clk_max}MHz" if (clk_max and clk_max > 0) else f"{clk_cur}MHz"
                gw["GPU Clock"].set_value(clk_pct, subtitle=clk_sub, max_value=100.0)
            else:
                gw["GPU Clock"].set_value(0, subtitle="N/A")
            if "GPU Clock__spark" in gw:
                gw["GPU Clock__spark"].push_value(clk_pct if (clk_cur and clk_cur > 0) else 0)

        if "Voltage" in gw and voltage is not None and voltage > 0:
            gw["Voltage"].set_value(voltage)
            if "Voltage__spark" in gw:
                gw["Voltage__spark"].push_value(voltage / 2.0 * 100.0)

        if "Power" in gw and s.get("power_usage") is not None and s["power_usage"] > 0:
            gw["Power"].set_value(s["power_usage"])
            if "Power__spark" in gw:
                gw["Power__spark"].push_value(s["power_usage"] / 300.0 * 100.0)

        if "Fan Speed" in gw and s.get("fan_speed") is not None and s["fan_speed"] >= 0:
            fan_sub = f"{fan_rpm} RPM" if (fan_rpm and fan_rpm > 0) else ""
            gw["Fan Speed"].set_value(s["fan_speed"], subtitle=fan_sub)
            if "Fan Speed__spark" in gw:
                gw["Fan Speed__spark"].push_value(float(s["fan_speed"]))

    if cpu_usage is not None and "CPU Usage" in gw:
        cpu_pct = _usage_percent(cpu_usage)
        freq_match = re.search(r"^([0-9\.\sGHz/]+)", str(cpu_usage))
        sub = freq_match.group(1).strip() if freq_match else ""
        gw["CPU Usage"].set_value(cpu_pct, subtitle=sub)
        if "CPU Usage__spark" in gw:
            gw["CPU Usage__spark"].push_value(cpu_pct)

    if cpu_temp is not None and "CPU Temp" in gw and cpu_temp > 0:
        gw["CPU Temp"].set_value(cpu_temp)
        if "CPU Temp__spark" in gw:
            gw["CPU Temp__spark"].push_value(cpu_temp / 110.0 * 100.0)

    if ram_usage is not None and "RAM Usage" in gw:
        ram_pct = _usage_percent(ram_usage)
        cap_match = re.search(r"([0-9\.]+\s*GB\s*/\s*[0-9\.]+\s*GB)", str(ram_usage))
        sub = cap_match.group(1).replace(" ", "") if cap_match else ""
        gw["RAM Usage"].set_value(ram_pct, subtitle=sub)
        if "RAM Usage__spark" in gw:
            gw["RAM Usage__spark"].push_value(ram_pct)

    if swap_usage is not None and "Swap" in gw:
        swap_pct = _usage_percent(swap_usage)
        cap_match = re.search(r"([0-9\.]+\s*GB\s*/\s*[0-9\.]+\s*GB)", str(swap_usage))
        sub = cap_match.group(1).replace(" ", "") if cap_match else ""
        gw["Swap"].set_value(swap_pct, subtitle=sub)
        if "Swap__spark" in gw:
            gw["Swap__spark"].push_value(swap_pct)

    NET_MAX = 1000.0
    if net_down_mbps is not None and "Net Down" in gw:
        down_pct = min(net_down_mbps / NET_MAX * 100.0, 100.0)
        down_sub = f"{net_down_mbps:.1f} Mb/s" if net_down_mbps >= 0.01 else "0 Mb/s"
        gw["Net Down"].set_value(down_pct, subtitle=down_sub)
        if "Net Down__spark" in gw:
            gw["Net Down__spark"].push_value(down_pct)

    if net_up_mbps is not None and "Net Up" in gw:
        up_pct = min(net_up_mbps / NET_MAX * 100.0, 100.0)
        up_sub = f"{net_up_mbps:.1f} Mb/s" if net_up_mbps >= 0.01 else "0 Mb/s"
        gw["Net Up"].set_value(up_pct, subtitle=up_sub)
        if "Net Up__spark" in gw:
            gw["Net Up__spark"].push_value(up_pct)



def _make_gauge_dashboard(gpu_stats: dict, gauges_out: dict,
                          cpu_usage=0.0, ram_usage=0.0,
                          cpu_temp=None, swap_usage=None,
                          net_down_mbps: float = 0.0,
                          net_up_mbps: float = 0.0) -> Gtk.Widget:
    """
    Build the speedometer / circular-gauge dashboard for a single GPU card.
    Only metrics with valid real-time data are rendered.
    """
    outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    outer.set_margin_start(8)
    outer.set_margin_end(8)
    outer.set_margin_top(4)
    outer.set_margin_bottom(8)

    # ---- Grid: up to 4 gauges per row ----
    grid = Gtk.Grid()
    grid.set_row_spacing(8)
    grid.set_column_spacing(8)
    grid.set_row_homogeneous(True)
    grid.set_column_homogeneous(True)

    GAUGE_SIZE = 138

    def _gauge_cell(title, unit, gauge_type, value, subtitle="", max_value=100.0):
        """Build a single gauge + sparkline cell with tooltip."""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox.set_halign(Gtk.Align.CENTER)
        vbox.set_valign(Gtk.Align.CENTER)

        tooltip = METRIC_TOOLTIPS.get(title)
        if tooltip:
            vbox.set_tooltip_text(tooltip)

        g = CircularGauge(size=GAUGE_SIZE, title=title, unit=unit,
                          min_value=0.0, max_value=max_value,
                          gauge_type=gauge_type)
        if tooltip:
            g.set_tooltip_text(tooltip)
        g.set_value(value, subtitle=subtitle)
        g.set_hexpand(True)
        g.set_vexpand(False)
        vbox.append(g)

        # Sparkline history chart below gauge
        spark = SparklineWidget(width=GAUGE_SIZE, height=24, gauge_type=gauge_type)
        normalized = (value / max_value * 100.0) if max_value > 0 else 0.0
        spark.push_value(normalized)
        spark.set_hexpand(True)
        spark.set_margin_top(1)
        if tooltip:
            spark.set_tooltip_text(tooltip)
        vbox.append(spark)

        return vbox, g, spark

    # ---- Derive initial values from gpu_stats ----
    mem_used  = gpu_stats.get("mem_used") or 0
    mem_total = gpu_stats.get("mem_total") or 0
    vram_pct  = (mem_used / mem_total * 100.0) if mem_total > 0 else 0
    vram_sub  = f"{mem_used}/{mem_total}MB" if mem_total > 0 else ""

    gtt_used  = gpu_stats.get("gtt_used") or 0
    gtt_total = gpu_stats.get("gtt_total") or 0
    gtt_pct   = (gtt_used / gtt_total * 100.0) if gtt_total > 0 else 0
    gtt_sub   = f"{gtt_used}/{gtt_total}MB" if gtt_total > 0 else ""

    vc_cur  = gpu_stats.get("vram_clock") or 0
    vc_max  = gpu_stats.get("vram_clock_max") or 0
    vc_pct  = (vc_cur / vc_max * 100.0) if vc_max > 0 else 0
    vc_sub  = f"{vc_cur}/{vc_max}MHz" if vc_max > 0 else (f"{vc_cur}MHz" if vc_cur > 0 else "")

    mem_busy = gpu_stats.get("mem_busy")

    usage = gpu_stats.get("usage")
    usage_val = usage if (usage is not None and usage >= 0) else 0

    temp = gpu_stats.get("temp") or 0
    temp_hotspot = gpu_stats.get("temp_hotspot") or 0

    clk_cur = gpu_stats.get("clock_current") or 0
    clk_max = gpu_stats.get("clock_max") or 0
    clk_pct = (clk_cur / clk_max * 100.0) if clk_max > 0 else 0
    clk_sub = f"{clk_cur}/{clk_max}MHz" if clk_max > 0 else (f"{clk_cur}MHz" if clk_cur > 0 else "")

    voltage = gpu_stats.get("voltage") or 0.0

    power = gpu_stats.get("power_usage") or 0
    fan   = gpu_stats.get("fan_speed")
    fan_rpm = gpu_stats.get("fan_rpm") or 0
    fan_val = fan if (fan is not None and fan >= 0) else 0
    fan_sub = f"{fan_rpm} RPM" if fan_rpm > 0 else ""

    # Filter out metrics that are unsupported or N/A
    valid_defs = []
    if mem_total > 0:
        valid_defs.append(("VRAM", "%", "vram", vram_pct, vram_sub, 100.0))
    if vc_cur > 0 or vc_max > 0:
        valid_defs.append(("VRAM Clock", "%", "vram_clock", vc_pct, vc_sub, 100.0))
    if mem_busy is not None and mem_busy >= 0:
        valid_defs.append(("Mem Bus", "%", "mem_busy", float(mem_busy), "", 100.0))
    if gtt_total > 0:
        valid_defs.append(("GTT Memory", "%", "gtt", gtt_pct, gtt_sub, 100.0))
    if usage is not None and usage >= 0:
        valid_defs.append(("GPU Usage", "%", "usage", usage_val, "", 100.0))
    if temp is not None and temp > 0:
        valid_defs.append(("Temp", "°C", "temp", float(temp), "", 110.0))
    if temp_hotspot is not None and temp_hotspot > 0:
        valid_defs.append(("Hotspot", "°C", "temp_hotspot", float(temp_hotspot), "", 120.0))
    if clk_cur > 0 or clk_max > 0:
        valid_defs.append(("GPU Clock", "%", "clock", clk_pct, clk_sub, 100.0))
    if voltage is not None and voltage > 0:
        valid_defs.append(("Voltage", "V", "voltage", float(voltage), "", 2.0))
    if power is not None and power > 0:
        valid_defs.append(("Power", "W", "power", float(power), "", 300.0))
    if fan is not None and fan >= 0:
        valid_defs.append(("Fan Speed", "%", "fan", float(fan_val), fan_sub, 100.0))
    # System CPU & RAM Gauges
    valid_defs.append(("CPU Usage", "%", "cpu", _usage_percent(cpu_usage), "", 100.0))
    if cpu_temp is not None and cpu_temp > 0:
        valid_defs.append(("CPU Temp", "°C", "cpu_temp", float(cpu_temp), "", 110.0))
    valid_defs.append(("RAM Usage", "%", "ram", _usage_percent(ram_usage), "", 100.0))
    if swap_usage is not None and swap_usage != "—":
        swap_pct = _usage_percent(swap_usage)
        swap_match = re.search(r"([0-9\.]+\s*GB\s*/\s*[0-9\.]+\s*GB)", str(swap_usage))
        swap_sub = swap_match.group(1).replace(" ", "") if swap_match else ""
        valid_defs.append(("Swap", "%", "swap", swap_pct, swap_sub, 100.0))

    # Network speed gauges — always shown, even at 0 Mbit/s, to give a live sparkline
    # Use a generous 1000 Mbit/s as max so the arc fills usefully at lower speeds.
    # The subtitle shows the raw Mbit/s value.
    NET_MAX = 1000.0
    net_down_sub = f"{net_down_mbps:.1f} Mb/s" if net_down_mbps >= 0.01 else "0 Mb/s"
    net_up_sub   = f"{net_up_mbps:.1f} Mb/s"   if net_up_mbps   >= 0.01 else "0 Mb/s"
    valid_defs.append(("Net Down", "%", "net_down",
                        min(net_down_mbps / NET_MAX * 100.0, 100.0), net_down_sub, 100.0))
    valid_defs.append(("Net Up", "%", "net_up",
                        min(net_up_mbps / NET_MAX * 100.0, 100.0), net_up_sub, 100.0))


    for idx, (key, unit, gtype, init_val, sub, max_v) in enumerate(valid_defs):
        col = idx % 4
        row = idx // 4
        cell, gauge, spark = _gauge_cell(key, unit, gtype, init_val, sub, max_v)
        grid.attach(cell, col, row, 1, 1)
        gauges_out[key] = gauge
        gauges_out[f"{key}__spark"] = spark


    outer.append(grid)
    return outer



def _make_card(title: str, icon_name: str, rows: list,
               nav_page: str | None, app,
               supported: bool = True,
               row_widgets_out: dict = None,
               content_widget: Gtk.Widget | None = None,
               content_builder=None,
               gpu_index: int | None = None,
               extra_nav_actions: list[tuple[str, str]] | None = None,
               card_id: str | None = None,
               allow_reorder: bool = False,
               flow_box = None,
               columns_data: list[list[tuple[str, str]]] | None = None) -> Gtk.Box:
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

    # Navigation buttons to jump to detail tabs
    if nav_page and supported and app:
        nav_btn = _nav_button("Open →", nav_page, app, gpu_index=gpu_index)
        nav_btn.set_tooltip_text(f"Open {title} tab")
        header.append(nav_btn)

    if extra_nav_actions and supported and app:
        for nav_lbl, nav_dest in extra_nav_actions:
            ext_btn = _nav_button(nav_lbl, nav_dest, app, gpu_index=gpu_index)
            header.append(ext_btn)

    # Pop-out button to open card in separate window
    popout_btn = Gtk.Button()
    popout_btn.set_icon_name("window-new-symbolic")
    popout_btn.add_css_class("flat")
    popout_btn.set_valign(Gtk.Align.CENTER)
    popout_btn.set_tooltip_text(f"Open {title} in separate window")

    def on_popout_clicked(_):
        _open_card_in_separate_window(
            title=title,
            icon_name=icon_name,
            rows=rows,
            content_widget=content_widget,
            columns_data=columns_data,
            content_builder=content_builder,
            supported=supported,
            app=app,
            parent_row_widgets=row_widgets_out,
            card_id=card_id,
            card_widget=frame,
            flow_box=flow_box,
            gpu_index=gpu_index,
        )

    popout_btn.connect("clicked", on_popout_clicked)
    header.append(popout_btn)

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

def _match_vulkan_device(vendor_id_str, device_id_str, vk_devices):
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
                        return dev
                except ValueError:
                    pass
    except ValueError:
        pass
    return None


def _match_vulkan_name(vendor_id_str, device_id_str, vk_devices):
    dev = _match_vulkan_device(vendor_id_str, device_id_str, vk_devices)
    return dev.get("name") if dev else None


def _format_device_type(raw_type: str) -> str:
    if not raw_type:
        return ""
    # Strip either prefix (most-specific first)
    t = raw_type
    for prefix in ("VK_PHYSICAL_DEVICE_TYPE_", "PHYSICAL_DEVICE_TYPE_"):
        if t.startswith(prefix):
            t = t[len(prefix):]
            break
    t = t.replace("_", " ").title()
    t = re.sub(r'\bGpu\b', 'GPU', t)
    t = re.sub(r'\bCpu\b', 'CPU', t)
    return t.strip()


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

        .summary-tier-header {
            font-weight: 700;
            color: #ffffff;
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

        .summary-tier-header {
            font-weight: 700;
            color: #171717;
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
        if app is not None:
            app.summary_data = data
            if hasattr(app, "_on_summary_data_ready"):
                GLib.idle_add(app._on_summary_data_ready, data)
        GLib.idle_add(_build_ui, data)

    def _build_ui(data: dict):
        spinner.stop()
        outer.remove(loading_box)

        # Master scroll container
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        # Dashboard: Option A Structured 3-Tier Executive Dashboard
        dashboard = SummaryDashboard(app=app)
        scroll.set_child(dashboard)

        if app is not None:
            app.summary_flow_box = dashboard
            app.summary_card_titles = dashboard._summary_card_titles

        def _apply_summary_card_order(order):
            if dashboard is None:
                return
            registry = list(getattr(dashboard, "_summary_card_registry", []))
            if not registry:
                return
            widget_by_id = {widget_id: widget for widget_id, widget in registry}
            ordered_ids = [card_id for card_id in order if card_id in widget_by_id]
            for card_id in list(widget_by_id):
                if card_id not in ordered_ids:
                    ordered_ids.append(card_id)
            reordered = [(card_id, widget_by_id[card_id]) for card_id in ordered_ids]
            dashboard.apply_reorder(reordered)
            dashboard.refresh_display(app)

        def restore_summary_card_order():
            registry = list(getattr(dashboard, "_summary_card_registry", []))
            if not registry:
                return
            current_order = [widget_id for widget_id, _ in registry]
            saved_order = app.config.get_summary_card_order() if app is not None and hasattr(app, "config") else []
            if not saved_order:
                def default_card_priority(card_id):
                    if card_id == "system":
                        return 0
                    if card_id.startswith("gpu-hw"):
                        return 1
                    if card_id.startswith("gpu-"):
                        return 2
                    if card_id.startswith("vulkan-"):
                        return 3
                    if card_id.startswith("opengl"):
                        return 4
                    if card_id in ("egl", "glx"):
                        return 5
                    if card_id.startswith("opencl-"):
                        return 6
                    if card_id.startswith("vdpau"):
                        return 7
                    return 8

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
                dashboard.refresh_display(app)
                return
            _apply_summary_card_order(ordered)

        view_stack = getattr(app, "view_stack", None)

        # ── Tier 1: Host System Information ──────────────────────────────
        sys_data = data["system"]
        cpu_usage_init = get_realtime_cpu_usage()
        ram_usage_init = get_realtime_ram_usage()
        uptime_init = get_realtime_uptime()
        cpu_temp_init = get_realtime_cpu_temp()
        swap_usage_init = get_realtime_swap_usage()

        sys_columns = [
            [
                ("Operating System", sys_data.get("os", "—")),
                ("Processor", sys_data.get("cpu", "—")),
                ("CPU Cores / Threads", sys_data.get("cpu_cores_threads", "—")),
                ("CPU Cache", sys_data.get("cpu_cache", "—")),
            ],
            [
                ("Kernel", sys_data.get("kernel", "—")),
                ("Architecture", sys_data.get("architecture", "—")),
                ("Hostname", sys_data.get("hostname", "—")),
                ("Uptime", uptime_init),
                ("Swap Usage", swap_usage_init),
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
            nav_page=None,
            app=app,
            supported=True,
            content_widget=_make_grid_card_content(sys_columns, row_widgets_out=sys_widgets),
            row_widgets_out=sys_widgets,
            card_id="system",
            allow_reorder=True,
            flow_box=dashboard,
            columns_data=sys_columns,
        )
        sys_card.set_size_request(280, -1)
        dashboard.add_card(1, "system", sys_card)

        # ── Multi-GPU Hardware Overview & Real-Time Performance ──────────
        gpui_list = data["gpui_stats"]
        stats_widgets_list = []
        vk_devices = data["vulkan"].get("devices", []) if data.get("vulkan") else []
        known_gpus = [g for g in gpui_list if g.get("vendor_id") or g.get("device_id")]

        # ── Tier 1: Primary GPU Hardware Overview Card(s) ────────────────
        if known_gpus:
            for gpu_info in known_gpus:
                gpu_idx = gpu_info["card_index"]
                gpu_stats = gpu_info["stats"]

                matched_name = _match_vulkan_name(gpu_info["vendor_id"], gpu_info["device_id"], vk_devices)
                if not matched_name:
                    matched_name = _get_gpu_fallback_name(gpu_info["vendor_id"], gpu_info["device_id"])

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

                compute_units = gpu_stats.get("compute_units") or gpu_info.get("compute_units") or opencl_hint.get("compute_units")
                rop_count = gpu_stats.get("rop_count") or gpu_info.get("rop_count")
                instruction_set = (
                    gpu_stats.get("instruction_set")
                    or gpu_info.get("instruction_set")
                    or opencl_hint.get("instruction_set")
                )

                vk_dev = _match_vulkan_device(gpu_info.get("vendor_id"), gpu_info.get("device_id"), vk_devices)
                if not vk_dev and vk_devices and gpu_idx < len(vk_devices):
                    vk_dev = vk_devices[gpu_idx]

                dev_type = ""
                if vk_dev and vk_dev.get("device_type"):
                    dev_type = _format_device_type(vk_dev["device_type"])

                col_hw_1 = [
                    ("Card", gpu_info.get("card_name", f"card{gpu_idx}")),
                ]
                if dev_type:
                    col_hw_1.append(("Device Type", dev_type))
                col_hw_1.append(("Driver", gpu_info.get("driver", "—")))
                if gpu_info.get("vbios"):
                    col_hw_1.append(("VBIOS Version", gpu_info["vbios"]))
                if compute_units:
                    col_hw_1.append(("Compute Units", str(compute_units)))
                if rop_count:
                    col_hw_1.append(("ROPs", str(rop_count)))
                if instruction_set:
                    col_hw_1.append(("Architecture", str(instruction_set)))

                col_hw_2 = []
                if gpu_info.get("vendor_id") or gpu_info.get("device_id"):
                    col_hw_2.append(("Vendor / Device ID", f"{gpu_info.get('vendor_id', '—')} : {gpu_info.get('device_id', '—')}"))
                if gpu_info.get("subsystem_vendor") and gpu_info.get("subsystem_device"):
                    col_hw_2.append(("Subsystem ID", f"{gpu_info['subsystem_vendor']} : {gpu_info['subsystem_device']}"))
                if gpu_info.get("revision"):
                    col_hw_2.append(("Revision", gpu_info["revision"]))
                if gpu_info.get("pci_address"):
                    col_hw_2.append(("PCI Address", gpu_info["pci_address"]))
                if gpu_info.get("pcie_link_speed"):
                    col_hw_2.append(("PCIe Link Speed", gpu_info["pcie_link_speed"]))
                if gpu_info.get("pcie_link_width"):
                    col_hw_2.append(("PCIe Link Width", gpu_info["pcie_link_width"]))

                col_hw_3 = []
                mem_tot = gpu_stats.get("mem_total") or 0
                if mem_tot > 0:
                    col_hw_3.append(("VRAM Total", f"{mem_tot} MB"))
                vram_type = gpu_stats.get("vram_type") or gpu_info.get("vram_type")
                if vram_type:
                    col_hw_3.append(("VRAM Type", str(vram_type)))
                vram_vendor = gpu_info.get("vram_vendor")
                if vram_vendor:
                    col_hw_3.append(("VRAM Vendor", str(vram_vendor)))
                gtt_tot = gpu_stats.get("gtt_total") or 0
                if gtt_tot > 0:
                    col_hw_3.append(("GTT / Shared Memory", f"{gtt_tot} MB"))
                clk_max = gpu_stats.get("clock_max") or 0
                if clk_max > 0:
                    col_hw_3.append(("Max Core Clock", f"{clk_max} MHz"))
                vclk_max = gpu_stats.get("vram_clock_max") or 0
                if vclk_max > 0:
                    col_hw_3.append(("Max Memory Clock", f"{vclk_max} MHz"))
                if vk_dev and vk_dev.get("device_uuid"):
                    uuid_str = vk_dev["device_uuid"].strip()
                    if uuid_str and set(uuid_str.replace("-", "")) != {"0"} and len(col_hw_3) < 4:
                        col_hw_3.append(("Device UUID", uuid_str))

                gpu_hw_columns = [c for c in [col_hw_1, col_hw_2, col_hw_3] if c]
                gpu_logo = _get_gpu_logo(gpu_info.get("vendor_id", ""))
                hw_card_title = f"{matched_name}" if len(known_gpus) == 1 else f"{matched_name} ({gpu_info['card_name']})"

                gpu_hw_card = _make_card(
                    hw_card_title,
                    gpu_logo,
                    [],
                    nav_page=None,
                    app=app,
                    supported=True,
                    content_widget=_make_grid_card_content(gpu_hw_columns),
                    card_id=f"gpu-hw-{gpu_idx}",
                    allow_reorder=True,
                    flow_box=dashboard,
                    columns_data=gpu_hw_columns,
                )
                gpu_hw_card.set_size_request(280, -1)
                dashboard.add_card(1, f"gpu-hw-{gpu_idx}", gpu_hw_card)

        # ── Tier 2: Real-Time Telemetry & Performance Dashboard ─────────
        if known_gpus:
            for gpu_info in known_gpus:
                gpu_idx = gpu_info["card_index"]
                gpu_stats = gpu_info["stats"]

                matched_name = _match_vulkan_name(gpu_info["vendor_id"], gpu_info["device_id"], vk_devices)
                if not matched_name:
                    matched_name = _get_gpu_fallback_name(gpu_info["vendor_id"], gpu_info["device_id"])

                perf_card_title = f"Real-Time Telemetry — {matched_name}" if len(known_gpus) == 1 else f"Real-Time Telemetry — {matched_name} ({gpu_info['card_name']})"

                def _make_gpu_card_builder(stats):
                    def _builder(out_widgets=None, out_gauges=None, **kwargs):
                        if out_gauges is None:
                            out_gauges = kwargs.get("g_out")
                        g_dict = {} if out_gauges is None else out_gauges
                        return _make_gauge_dashboard(stats, g_dict, cpu_usage=cpu_usage_init, ram_usage=ram_usage_init, cpu_temp=cpu_temp_init, swap_usage=swap_usage_init)
                    return _builder

                gpu_gauge_widgets = {}
                card_builder = _make_gpu_card_builder(gpu_stats)
                content_widget = card_builder(out_gauges=gpu_gauge_widgets)

                gpu_logo = _get_gpu_logo(gpu_info.get("vendor_id", ""))
                gpu_perf_card = _make_card(
                    perf_card_title,
                    gpu_logo,
                    [],
                    nav_page=None,
                    app=app,
                    supported=True,
                    content_widget=content_widget,
                    content_builder=card_builder,
                    card_id=f"gpu-{gpu_idx}",
                    allow_reorder=True,
                    flow_box=dashboard,
                    columns_data=None,
                )
                gpu_perf_card.set_hexpand(True)
                dashboard.add_card(2, f"gpu-{gpu_idx}", gpu_perf_card)
                stats_widgets_list.append((gpu_idx, {}, gpu_gauge_widgets))

        # ── Tier 3: Graphics & Compute Subsystems (APIs) ─────────────────
        # ── Vulkan
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
                    flow_box=dashboard,
                    columns_data=columns,
                )
                card.set_size_request(280, -1)
                dashboard.add_card(3, f"vulkan-{i}", card)
        else:
            card = _make_card(
                "Vulkan", "../Images/Vulkan.png",
                [], nav_page=None, app=app, supported=False,
                card_id="vulkan-missing",
                allow_reorder=True,
                flow_box=dashboard,
            )
            card.set_size_request(280, -1)
            dashboard.add_card(3, "vulkan-missing", card)

        # ── OpenGL (Unified Core, ES, EGL, GLX)
        gl_data = data["opengl"]
        if gl_data["supported"] and gl_data.get("renderer"):
            renderer_label = gl_data["renderer"]

            # Column 1: Core OpenGL
            col_core = [
                ("Renderer", renderer_label),
                ("Vendor", gl_data.get("vendor", "—")),
                ("OpenGL Version", gl_data.get("version", "—")),
                ("GLSL Version", gl_data.get("shading_language_version", "—")),
                ("Extension Count", str(gl_data.get("extensions_count", "—"))),
            ]

            # Column 2: OpenGL ES & EGL
            col_es_egl = []
            es_version = gl_data.get("es_version", "")
            if es_version:
                col_es_egl.append(("OpenGL ES Version", es_version))
                if gl_data.get("es_shading_language_version"):
                    col_es_egl.append(("GLSL ES Version", gl_data.get("es_shading_language_version")))
                if gl_data.get("es_extensions_count"):
                    col_es_egl.append(("ES Extension Count", str(gl_data.get("es_extensions_count"))))
            
            egl_version = gl_data.get("egl_version", "")
            egl_count = gl_data.get("egl_count", 0)
            if egl_version:
                col_es_egl.append(("EGL Version", egl_version))
            if egl_count:
                col_es_egl.append(("EGL Extension Count", str(egl_count)))

            # Column 3: GLX
            col_glx = []
            glx_version = gl_data.get("glx_version", "")
            glx_ext = gl_data.get("glx_extension_count", 0)
            glx_vis = gl_data.get("glx_visual_count", 0)
            glx_fb = gl_data.get("fbconfig_count", 0)
            if glx_version:
                col_glx.append(("GLX Version", glx_version))
            if glx_ext:
                col_glx.append(("GLX Extension Count", str(glx_ext)))
            if glx_vis:
                col_glx.append(("GLX Visual Count", str(glx_vis)))
            if glx_fb:
                col_glx.append(("GLX FBConfig Count", str(glx_fb)))

            gl_columns = [c for c in [col_core, col_es_egl, col_glx] if c]

            card = _make_card(
                "OpenGL",
                "../Images/OpenGL.png",
                [],
                nav_page="page2",
                app=app,
                supported=True,
                content_widget=_make_grid_card_content(gl_columns),
                card_id="opengl",
                allow_reorder=True,
                flow_box=dashboard,
                columns_data=gl_columns,
            )
            card.set_size_request(280, -1)
            dashboard.add_card(3, "opengl", card)
        else:
            card = _make_card(
                "OpenGL", "../Images/OpenGL.png",
                [], nav_page=None, app=app, supported=False,
                card_id="opengl-missing",
                allow_reorder=True,
                flow_box=dashboard,
            )
            card.set_size_request(280, -1)
            dashboard.add_card(3, "opengl-missing", card)

        # ── OpenCL
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
                        flow_box=dashboard,
                        columns_data=[platform_col, dev_col_1, dev_col_2],
                    )
                    card.set_size_request(280, -1)
                    dashboard.add_card(3, f"opencl-{platform_name}-{dev_index}", card)
        else:
            card = _make_card(
                "OpenCL",
                "../Images/OpenCL.svg",
                [], nav_page=None, app=app, supported=False,
                card_id="opencl-missing",
                allow_reorder=True,
                flow_box=dashboard,
            )
            card.set_size_request(280, -1)
            dashboard.add_card(3, "opencl-missing", card)

        # ── VDPAU
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
                flow_box=dashboard,
            )
        else:
            card = _make_card(
                "VDPAU", "../Images/vdpauinfo.png",
                [], nav_page=None, app=app, supported=False,
                card_id="vdpau-missing",
                allow_reorder=True,
                flow_box=dashboard,
            )
        card.set_size_request(280, -1)
        dashboard.add_card(3, "vdpau" if vd_data["supported"] else "vdpau-missing", card)

        restore_summary_card_order()

        outer.append(scroll)

        # Periodic statistics update
        def update_stats_callback():
            if not outer.get_mapped() and not _active_popout_windows:
                return True
                
            def fetch_stats():
                try:
                    # System real-time stats
                    cpu_u = get_realtime_cpu_usage()
                    ram_u = get_realtime_ram_usage()
                    upt_u = get_realtime_uptime()
                    cpu_t = get_realtime_cpu_temp()
                    swap_u = get_realtime_swap_usage()
                    net_down, net_up = get_realtime_net_speed()

                    def apply_sys_updates(c=cpu_u, r=ram_u, u=upt_u, su=swap_u):
                        if "CPU Usage" in sys_widgets and c != "—":
                            sys_widgets["CPU Usage"].set_subtitle(c)
                        if "RAM Usage" in sys_widgets and r != "—":
                            sys_widgets["RAM Usage"].set_subtitle(r)
                        if "Uptime" in sys_widgets and u != "—":
                            sys_widgets["Uptime"].set_subtitle(u)
                        if "Swap Usage" in sys_widgets and su != "—":
                            sys_widgets["Swap Usage"].set_subtitle(su)

                        if "system" in _active_popout_windows:
                            pw = _active_popout_windows["system"].get("widgets", {})
                            if "CPU Usage" in pw and c != "—":
                                pw["CPU Usage"].set_subtitle(c)
                            if "RAM Usage" in pw and r != "—":
                                pw["RAM Usage"].set_subtitle(r)
                            if "Uptime" in pw and u != "—":
                                pw["Uptime"].set_subtitle(u)
                            if "Swap Usage" in pw and su != "—":
                                pw["Swap Usage"].set_subtitle(su)
                        return False

                    GLib.idle_add(apply_sys_updates)

                    for item in stats_widgets_list:
                        gpu_index = item[0]
                        gauge_widgets = item[2] if len(item) == 3 else item[1]
                        stats = get_gpu_stats_for_index(gpu_index) if gpu_index is not None else {}
                        
                        def apply_updates(gw=gauge_widgets, s=stats, g_idx=gpu_index, c=cpu_u, r=ram_u, ct=cpu_t, su=swap_u,
                                          nd=net_down, nu=net_up):
                            # Update main card gauges
                            _update_gauge_dict(gw, s, cpu_usage=c, ram_usage=r, cpu_temp=ct, swap_usage=su,
                                               net_down_mbps=nd, net_up_mbps=nu)

                            # Update popped-out standalone window gauges
                            for p_key in ("gpu-stats", f"gpu-{g_idx}" if g_idx is not None else "gpu-0"):
                                if p_key in _active_popout_windows:
                                    popout_info = _active_popout_windows[p_key]
                                    pg_all = popout_info.get("gauges", {})
                                    if isinstance(pg_all, dict):
                                        pg = pg_all.get(g_idx, pg_all) if g_idx in pg_all else pg_all
                                        _update_gauge_dict(pg, s, cpu_usage=c, ram_usage=r, cpu_temp=ct, swap_usage=su,
                                                           net_down_mbps=nd, net_up_mbps=nu)

                            return False
                        GLib.idle_add(apply_updates)


                except Exception as e:

                    print(f"Error updating real-time stats: {e}")
                    
            threading.Thread(target=fetch_stats, daemon=True).start()
            return True
            
        initial_interval = app.config.get_refresh_interval() if (app and hasattr(app, 'config')) else 1000
        _timeout_id = [GLib.timeout_add(initial_interval, update_stats_callback)]
        _last_interval = [initial_interval]

        def _check_interval_change():
            if app and hasattr(app, '_current_refresh_interval_ms'):
                new_ms = app._current_refresh_interval_ms
                if new_ms != _last_interval[0] and _timeout_id[0]:
                    GLib.source_remove(_timeout_id[0])
                    _last_interval[0] = new_ms
                    _timeout_id[0] = GLib.timeout_add(new_ms, update_stats_callback)
            return True

        _watcher_id = [GLib.timeout_add(1000, _check_interval_change)]

        def on_destroy(widget):
            if not _active_popout_windows:
                if _timeout_id[0]:
                    GLib.source_remove(_timeout_id[0])
                    _timeout_id[0] = 0
                if _watcher_id[0]:
                    GLib.source_remove(_watcher_id[0])
                    _watcher_id[0] = 0
        outer.connect("destroy", on_destroy)

        return False  # GLib.idle_add must return False to not repeat

    threading.Thread(target=_bg_worker, daemon=True).start()
    return outer
