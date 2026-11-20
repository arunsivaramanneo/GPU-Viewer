import re


_GPU_HEADER = re.compile(r"^\s*GPU\s*(\d+)\s*:")


def gpu_block_lines(content, gpu_index):
    """Return one GPU block without its heading."""
    lines = content.splitlines(keepends=True)
    start = None
    end = len(lines)
    for index, line in enumerate(lines):
        match = _GPU_HEADER.match(line)
        if not match:
            continue
        if start is None:
            if int(match.group(1)) == gpu_index:
                start = index + 1
        else:
            end = index
            break
    return lines[start:end] if start is not None else []


def section_lines(lines, start_marker, stop_markers=(), include_start=False):
    """Extract non-empty lines between marker strings."""
    result = []
    active = False
    for line in lines:
        if not active:
            if start_marker in line:
                active = True
                if include_start and line.strip():
                    result.append(line)
            continue
        if any(marker in line for marker in stop_markers):
            break
        if line.strip():
            result.append(line)
    return result


def parse_vulkan_summary_device(content, gpu_index):
    lines = gpu_block_lines(content, gpu_index)
    cleaned = []
    for line in lines:
        if not line.strip():
            continue
        newline = "\n" if line.endswith("\n") else ""
        cleaned.append(re.sub(r"\([0-9].*", "", line.rstrip("\n")) + newline)
    return sorted(cleaned)


def parse_pipeline_lines(content, gpu_index):
    lines = []
    for line in gpu_block_lines(content, gpu_index):
        if "VkPhysicalDeviceLimits:" in line:
            break
        if "pipeline" in line:
            lines.append(line)
    return lines


def parse_lscpu_device_info(content):
    lines = content.splitlines(keepends=True)
    cpu_info = sorted(
        (line for line in lines if "name" in line or line.startswith(("CPU", "L"))),
        reverse=True,
    )
    cpu_core_info = sorted(line for line in lines if " per " in line)
    return cpu_info, cpu_core_info


def parse_meminfo_lines(content):
    return [line for line in content.splitlines(keepends=True) if "Mem" in line]


def split_device_info_lines(lines):
    lhs = []
    rhs = []
    for line in lines:
        if line.strip():
            lhs.append(re.sub(r"[=,:].*", "", line))
        value = re.search(r"[=,:].*", line)
        if value:
            newline = "\n" if line.endswith("\n") else ""
            rhs.append(value.group(0) + newline)
    return lhs, rhs


def extract_format_feature_lines(lines, format_name, feature_group):
    format_name = format_name.strip()
    format_header = (
        format_name if format_name.startswith("FORMAT_") else f"FORMAT_{format_name}"
    )
    format_section = []
    active = False
    for line in lines:
        if not active:
            if line.strip() == format_header:
                active = True
                format_section.append(line)
            continue
        format_section.append(line)
        if "Common" in line:
            break

    start_marker, stop_marker = {
        "linear": ("linear", "optimal"),
        "optimal": ("optimal", "buffer"),
        "buffer": ("buffer", "Common"),
    }[feature_group]
    result = []
    active = False
    for line in format_section:
        if not active:
            if start_marker in line:
                active = True
            continue
        if stop_marker in line:
            break
        result.append(line)
    return result


def extract_device_properties(content, gpu_index):
    block = gpu_block_lines(content, gpu_index)
    return section_lines(
        block,
        "VkPhysicalDeviceSparseProperties:",
        ("Device Extensions",),
        include_start=True,
    )


def extract_device_extensions(content, gpu_index):
    block = gpu_block_lines(content, gpu_index)
    extensions = section_lines(
        block, "Device Extensions", ("VkQueueFamilyProperties",)
    )
    return sorted(line for line in extensions if "VK_" in line)


def extract_device_formats(content, gpu_index):
    device_formats = section_lines(
        gpu_block_lines(content, gpu_index),
        "Format Properties:",
        ("Unsupported Formats:", "Presentable Surfaces:"),
    )
    if device_formats:
        return device_formats
    return section_lines(
        content.splitlines(keepends=True),
        "Format Properties:",
        ("Unsupported Formats:", "Presentable Surfaces:"),
    )


def extract_memory_types(content, gpu_index):
    return section_lines(
        gpu_block_lines(content, gpu_index),
        "memoryTypes:",
        ("VkPhysicalDeviceFeatures:",),
    )


def extract_memory_heaps(content, gpu_index):
    return section_lines(
        gpu_block_lines(content, gpu_index),
        "memoryHeaps:",
        ("memoryTypes:", "VkPhysicalDeviceFeatures:"),
    )


def extract_queue_properties(content, gpu_index):
    block = gpu_block_lines(content, gpu_index)
    for index, line in enumerate(block):
        if "VkPhysicalDeviceMemoryProperties:" in line:
            block = block[:index]
            break
    return section_lines(
        block,
        "VkQueueFamilyProperties:",
    )


def extract_instance_extensions(content):
    return sorted(
        line for line in section_lines(content.splitlines(keepends=True),
                                       "Instance Extensions", ("Layers:",))
        if "VK_" in line
    )


def extract_instance_layers(content):
    return section_lines(
        content.splitlines(keepends=True),
        "Layers:",
        ("Presentable Surfaces:",),
    )


def extract_device_surface(content, gpu_index):
    surface_lines = section_lines(
        content.splitlines(keepends=True),
        "Presentable Surfaces:",
        ("Device Properties and Extensions",),
    )
    gpu_marker = re.compile(r"^\s*GPU\s+id\s*:\s*(\d+)\b")
    result = []
    active = False
    for line in surface_lines:
        match = gpu_marker.match(line)
        if match:
            if active:
                break
            active = int(match.group(1)) == gpu_index
            continue
        if not active:
            continue
        if "Groups:" in line:
            break
        if line.strip():
            result.append(line)
    return result


def extract_device_limits(content, gpu_index):
    block = gpu_block_lines(content, gpu_index)
    limits = section_lines(
        block,
        "VkPhysicalDeviceLimits:",
        ("VkPhysicalDeviceSparseProperties:",),
    )
    for index, line in enumerate(limits):
        if "--" in line:
            return [item for item in limits[index + 1:] if item.strip()]
    return []
