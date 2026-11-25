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

import os
import re
import gi
import const
import Filenames
import subprocess
gi.require_version('Gtk','4.0')
gi.require_version(namespace='Adw', version='1')
import threading
from gi.repository import GLib



from gi.repository import Gtk,Gio,GObject,Adw,GdkPixbuf,Pango

Adw.init()

from Common import getScreenSize,createMainFile,create_scrollbar,setMargin,fetchContentsFromCommand,appendLimitsRHS,create_tab,getLogo,getGpuImage, create_sidebar_toggle

Title = [""]
Title2 = ["OpenGL Information ", " Details"]
LimitsTitle = ["OpenGL Hardware Limits", "Value"]


def parse_limit_lines(lines):
    """Split OpenGL limit lines into the same labels and values used by the UI."""
    labels = []
    values = []
    for line in lines:
        if not line.strip():
            continue
        labels.append(re.sub(r"[=,:].*", "", line))
        value_match = re.search(r".*[=,:]\s*", line)
        values.append(line[value_match.end():] if value_match else "")
    return labels, values


def select_limit_section(lines, title):
    """Return one named limits section, excluding its heading and next heading."""
    selected = []
    active = False
    for line in lines:
        if not active:
            if f"{title}:" in line:
                active = True
            continue
        if ":" in line:
            break
        if line.strip():
            selected.append(line)
    return selected


def parse_glx_limits(lines, profile):
    """Extract the requested core or compatibility limit block from glxinfo."""
    if profile == "core":
        start_marker = "OpenGL core profile limits:"
        stop_marker = "OpenGL version string"
    else:
        start_marker = "OpenGL limits:"
        stop_marker = "OpenGL ES profile"

    selected = []
    active = False
    for line in lines:
        if not active:
            if start_marker in line:
                active = True
            continue
        if stop_marker in line:
            break
        if line.strip():
            selected.append(line if line.endswith("\n") else f"{line}\n")
    return selected


def parse_framebuffer_sections(lines):
    """Extract GLX Visual and FBConfig rows after their separator lines."""
    sections = {"visuals": [], "fbconfigs": []}
    section = None
    past_separator = False
    for line in lines:
        if "GLX Visuals" in line:
            section = "visuals"
            past_separator = False
            continue
        if "GLXFBConfigs" in line:
            section = "fbconfigs"
            past_separator = False
            continue
        if section is None:
            continue
        if not past_separator:
            if "----" in line:
                past_separator = True
            continue
        if line.strip():
            sections[section].append(line)
    return sections["visuals"], sections["fbconfigs"]


def parse_extension_section(lines, start_marker, stop_marker, prefix):
    """Extract sorted extension rows from one section of a saved info file."""
    extensions = []
    active = False
    for line in lines:
        if not active:
            if start_marker in line:
                active = True
            continue
        if stop_marker in line:
            break
        if prefix in line:
            extensions.append(line.strip())
    return sorted(extensions)


def parse_extension_tokens(lines, start_marker, prefix):
    """Extract individual extension tokens from an indented tool output block."""
    extensions = []
    active = False
    for line in lines:
        stripped = line.strip()
        if not active:
            if stripped.startswith(start_marker):
                active = True
            continue
        if not stripped:
            continue
        if not line[0].isspace():
            break
        extensions.extend(
            re.findall(rf"\b{re.escape(prefix)}[A-Za-z0-9_]+\b", stripped)
        )
    return sorted(set(extensions))


def parse_egl_extensions(lines):
    """Extract EGL extensions from the es2_info extension block."""
    return parse_extension_tokens(lines, "EGL_EXTENSIONS", "EGL_")


def _resolve_image_path(filename):
    """Resolve an image filename across development and installed environments."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for candidate in (
        os.path.join(base_dir, "Images", filename),
        os.path.join("../Images", filename),
        os.path.join("Images", filename),
    ):
        if os.path.exists(candidate):
            return candidate
    return ""


def get_gpuz_vendor_logo_pixbuf(renderer):
    """Return a 38x38 vendor logo pixbuf matching GpuZViewer's header style."""
    text = (renderer or "").lower()
    if any(tok in text for tok in ("amd", "radeon", "ryzen", "ati")):
        filename = "AMD_D.png"
    elif any(tok in text for tok in ("nvidia", "geforce")):
        filename = "nvidia_logo.png"
    elif "intel" in text:
        filename = "intel-logo.png"
    else:
        filename = "about-us.png"

    path = _resolve_image_path(filename)
    if path:
        try:
            return GdkPixbuf.Pixbuf.new_from_file_at_scale(path, 38, 38, True)
        except Exception:
            pass
    return None


def detect_egl_platform(env=None):
    """Return ordered candidate eglinfo -p platforms based on the windowing session."""
    environ = env if env is not None else os.environ
    session = environ.get("XDG_SESSION_TYPE", "").strip().lower()
    candidates = []
    if session == "wayland" or environ.get("WAYLAND_DISPLAY"):
        candidates.append("wayland")
    if session == "x11" or environ.get("DISPLAY"):
        if "x11" not in candidates:
            candidates.append("x11")
    for fallback in ("gbm", "surfaceless"):
        if fallback not in candidates:
            candidates.append(fallback)
    return candidates


def parse_egl_limits(lines, profile):
    """Extract core, compatibility, or ES limits from eglinfo -l output."""
    if profile == "core":
        start_marker = "OpenGL core profile limits:"
    elif profile == "compat":
        start_marker = "OpenGL compatibility profile limits:"
    else:
        start_marker = "OpenGL ES profile limits:"

    selected = []
    active = False
    for line in lines:
        stripped = line.strip()
        if not active:
            if stripped.startswith(start_marker):
                active = True
            continue
        if (
            stripped.startswith("OpenGL core profile ")
            or stripped.startswith("OpenGL compatibility profile ")
            or stripped.startswith("OpenGL ES profile ")
            or stripped.startswith("Configurations:")
            or re.match(r"^\S.* platform:$", stripped)
        ):
            break
        if stripped:
            selected.append(line if line.endswith("\n") else f"{line}\n")
    return selected


EGL_CONFIG_COLUMNS = [
    "ID", "Buffer", "Level", "R", "G", "B", "A", "Depth", "Stencil",
    "Samples", "Buf", "Visual ID", "Caveat", "Bind", "GL", "ES", "ES2", "VG", "Surfaces",
]


def parse_egl_configurations(lines):
    """Parse the Configurations table from eglinfo output into 19-column rows."""
    rows = []
    in_section = False
    past_separator = False
    for raw_line in lines:
        line = raw_line.rstrip("\n")
        stripped = line.strip()
        if not in_section:
            if stripped.startswith("Configurations:"):
                in_section = True
            continue
        if not past_separator:
            if "----" in stripped:
                past_separator = True
            continue
        if not stripped:
            if rows:
                break
            continue
        if re.match(r"^\S.* platform:$", stripped):
            break
        if len(line) < 35:
            continue
        slices = (
            line[0:4], line[4:7], line[7:10], line[10:13], line[13:16],
            line[16:19], line[19:22], line[22:25], line[25:28], line[28:31],
            line[31:34], line[34:44], line[44:48], line[48:53], line[53:56],
            line[56:59], line[59:63], line[63:66], line[66:],
        )
        rows.append([part.strip() for part in slices])
    return rows


def extract_egl_brief_lines(lines):
    """Keep only summary lines from eglinfo -p <platform> -l for the Info tree."""
    brief = []
    skip_indented = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            skip_indented = False
            continue
        if (
            stripped.startswith("EGL client extensions string:")
            or stripped.startswith("EGL extensions string:")
            or stripped.startswith("OpenGL core profile extensions:")
            or stripped.startswith("OpenGL core profile limits:")
            or stripped.startswith("OpenGL compatibility profile extensions:")
            or stripped.startswith("OpenGL compatibility profile limits:")
            or stripped.startswith("OpenGL ES profile extensions:")
            or stripped.startswith("OpenGL ES profile limits:")
            or stripped.startswith("Configurations:")
        ):
            skip_indented = True
            continue
        if skip_indented:
            if line[0].isspace() or stripped.startswith("---") or re.match(r"^0x[0-9a-fA-F]+", stripped):
                continue
            skip_indented = False
        brief.append(line)
    return brief


class ExpandDataObject(GObject.GObject):
    def __init__(self, txt: str, txt2: str):
        super(ExpandDataObject, self).__init__()
        self.data = txt
        self.data2 = txt2
        self.children = []

class ExpandDataObject3(GObject.GObject):
    def __init__(self, txt: str, image: GdkPixbuf.Pixbuf, txt2: str):
        super(ExpandDataObject3, self).__init__()
        self.data = txt
        self.data2 = image
        self.data3 = txt2
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

def add_tree_node3(item):
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
        store = Gio.ListStore.new(ExpandDataObject3)
        for child in item.children:
            store.append(child)
        return store

def setup_image(widget, item):
    """Setup the widget to show in the Gtk.Listview"""
    image_render = Gtk.Picture()
    item.set_child(image_render)

def bind_image(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    row = item.get_item()
    obj = row.get_item()
    label.set_pixbuf(obj.data2)

def parse_glxinfo_brief(lines, dummy_transparent, getLogo):
    parsed_rows = []
    stack = []
    for raw_line in lines:
        line = raw_line.rstrip('\n')
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip('\t '))
        text = line.strip()
        if ":" in text:
            lhs, rhs = text.split(":", 1)
            lhs = lhs.strip()
            rhs = rhs.strip()
        else:
            lhs = text
            rhs = ""
        if lhs == "OpenGL renderer string":
            logo = getLogo(rhs)
        else:
            logo = dummy_transparent
        node = ExpandDataObject3(lhs, logo, rhs)
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if stack:
            stack[-1][1].children.append(node)
        else:
            parsed_rows.append(node)
        stack.append((indent, node))
    return parsed_rows


def parse_eglinfo_devices(lines):
    """Group eglinfo platform sections by their OpenGL renderer/device index."""
    sections = []
    current_section = None
    device_indices = []

    for line in lines:
        if re.match(r"^\S.* platform:$", line):
            if current_section is not None:
                sections.append(current_section)
            current_section = {"platform": line.strip()[:-1], "lines": []}
            continue

        if current_section is None:
            continue

        if current_section["platform"] == "Device platform":
            device_match = re.match(r"\s*Device #(\d+):", line)
            if device_match:
                device_indices.append(int(device_match.group(1)))
        current_section["lines"].append(line)

    if current_section is not None:
        sections.append(current_section)

    def renderer_for(section):
        for line in section["lines"]:
            match = re.match(
                r"\s*(?:OpenGL (?:core|compatibility|ES) profile renderer|GL_RENDERER):\s*(.*)",
                line,
            )
            if match:
                return match.group(1).strip()
        return ""

    devices = []
    device_sections = [
        section for section in sections
        if section["platform"] == "Platform Device platform"
    ]
    for position, section in enumerate(device_sections):
        renderer = renderer_for(section)
        if not renderer:
            continue
        device_index = (
            device_indices[position] if position < len(device_indices) else position
        )
        devices.append({
            "index": device_index,
            "renderer": renderer,
            "label": f"GPU {device_index}: {renderer}",
            "sections": [{
                "platform": f"Platform Device #{device_index}",
                "lines": section["lines"],
            }],
        })

    other_sections = [
        section for section in sections
        if section["platform"] not in ("Device platform", "Platform Device platform")
    ]
    if not devices:
        for section in other_sections:
            renderer = renderer_for(section)
            if not renderer:
                continue
            device = next(
                (item for item in devices if item["renderer"] == renderer), None
            )
            if device is None:
                device_index = len(devices)
                device = {
                    "index": device_index,
                    "renderer": renderer,
                    "label": f"GPU {device_index}: {renderer}",
                    "sections": [],
                }
                devices.append(device)
            device["sections"].append(section)
        return devices

    for section in other_sections:
        renderer = renderer_for(section)
        if not renderer:
            continue
        matching_devices = [
            item for item in devices if item["renderer"] == renderer
        ]
        if matching_devices:
            matching_devices[0]["sections"].append(section)

    return devices


def parse_device_extensions(device):
    """Return OpenGL, GLES, and EGL extension tokens for one EGL device."""
    sections = device.get("ext_sections") or device.get("sections", [])
    lines = [
        line
        for section in sections
        for line in section.get("lines", [])
    ]
    egl_extensions = parse_extension_tokens(
        lines, "EGL extensions string:", "EGL_"
    )
    if not egl_extensions:
        egl_extensions = parse_extension_tokens(lines, "EGL_EXTENSIONS:", "EGL_")

    return {
        "OpenGL core": parse_extension_tokens(
            lines, "OpenGL core profile extensions:", "GL_"
        ),
        "OpenGL compatibility": parse_extension_tokens(
            lines, "OpenGL compatibility profile extensions:", "GL_"
        ),
        "OpenGL ES": parse_extension_tokens(
            lines, "OpenGL ES profile extensions:", "GL_"
        ),
        "EGL": egl_extensions,
    }


def parse_glx_renderer(lines):
    """Return the renderer queried by glxinfo, if present."""
    for line in lines:
        if line.strip().startswith("OpenGL renderer string:"):
            return line.split(":", 1)[1].strip()
    return ""


def renderers_match(first, second):
    """Compare renderer names while allowing driver suffixes to differ."""
    first = " ".join(first.casefold().split())
    second = " ".join(second.casefold().split())
    return bool(first and second and (first == second or first in second or second in first))


class DataObject2(GObject.GObject):
    def __init__(self, column1: str):
        super(DataObject2, self).__init__()
        self.column1 = column1

class DataObject(GObject.GObject):
    def __init__(self, column1: str,column2: str):
        super(DataObject, self).__init__()
        self.column1 = column1
        self.column2 = column2

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

def bind_column1(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_text(obj.column1)
    label.add_css_class(css_class='parent')

def bind_column2(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    obj = item.get_item()
    label.set_label(obj.column2)

def bind1(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    row = item.get_item()
    obj = row.get_item()
    if "true" in obj.data2: 
        label.add_css_class(css_class='true')
    elif "false" in obj.data2:
        label.add_css_class(css_class='false')
    else:
        label.add_css_class(css_class='nothing')
    label.set_label(obj.data2)
    

def bind_column3(widget, item):
    """bind data from the store object to the widget"""
    label = item.get_child()
    row = item.get_item()
    obj = row.get_item()
    if "true" in obj.data3: 
        label.add_css_class(css_class='true')
    elif "false" in obj.data3:
        label.add_css_class(css_class='false')
    else:
        label.add_css_class(css_class='nothing')
    label.set_label(obj.data3)
    

def bind_expander(widget, item):
    """bind data from the store object to the widget"""
    expander = item.get_child()
    label = expander.get_child()
    row = item.get_item()
    expander.set_list_row(row)
    obj = row.get_item()
    label.set_label(obj.data)
    label.add_css_class(css_class='parent')

def OpenGL(self, tab):

    loaded_pages = set()
    page_spinners = {}
    page_content_containers = {}
    egl_state = {
        "devices": [],
        "pixbuf": None,
        "ready": False,
        "egl_lines": [],
        "egl_configs": [],
        "platform": "",
    }
    info_roots = {"egl": None}
    sidebar_rows = {}
    sidebar_headings = {}
    sidebar_group_rows = {}
    sidebar_listbox_map = {}
    refresh_extensions_callback = None
    refresh_framebuffer_callback = None

    def update_sidebar_support(device):
        device_extensions = parse_device_extensions(device) if device else {}
        has_limits = bool(
            parse_egl_limits(egl_state["egl_lines"], "core")
            or parse_egl_limits(egl_state["egl_lines"], "compat")
            or parse_egl_limits(egl_state["egl_lines"], "gles")
        )
        support = {
            "EGL Information": True,
            "OpenGL Limits": has_limits,
            "OpenGL": bool(
                device_extensions.get("OpenGL core")
                or device_extensions.get("OpenGL compatibility")
            ),
            "OpenGL ES": bool(device_extensions.get("OpenGL ES")),
            "EGL": bool(device_extensions.get("EGL")),
            "EGL Configurations": bool(egl_state["egl_configs"]),
        }

        for label, row in sidebar_rows.items():
            row.set_visible(support.get(label, True))

        # Hide section headings when all their rows are invisible
        for heading, rows in sidebar_group_rows.items():
            heading_visible = any(support.get(label, True) for label in rows)
            sidebar_headings[heading].set_visible(heading_visible)
            # Also hide the associated listbox stored alongside heading
            if heading in sidebar_listbox_map:
                sidebar_listbox_map[heading].set_visible(heading_visible)
        visible_page = content_stack.get_visible_child_name()
        if visible_page == "framebuffer-configuration" and not support["EGL Configurations"]:
            content_stack.set_visible_child_name("opengl-information")
            sidebar_listboxes[0].select_row(sidebar_listboxes[0].get_row_at_index(0))
        if visible_page == "extensions" and not any(
            support[name] for name in ("OpenGL", "OpenGL ES", "EGL")
        ):
            content_stack.set_visible_child_name("opengl-information")
            sidebar_listboxes[0].select_row(sidebar_listboxes[0].get_row_at_index(0))

        if refresh_extensions_callback is not None:
            refresh_extensions_callback(device_extensions, [])
        if refresh_framebuffer_callback is not None:
            refresh_framebuffer_callback(device)

    def refresh_egl_device(*_):
        if not egl_state["ready"]:
            return

        egl_root = info_roots["egl"]
        pixbuf = egl_state["pixbuf"]
        devices = egl_state["devices"]
        egl_root.children.clear()

        if devices:
            device = devices[0]
            renderer = device["renderer"]
            short_name = re.sub(r"\s*\([^)]*\)\s*$", "", renderer).strip() or renderer
            gpu_name_label.set_text(short_name)

            gl_version = ""
            egl_version = ""
            for line in egl_state["egl_lines"]:
                s = line.strip()
                if not gl_version and s.startswith("OpenGL core profile version:"):
                    gl_version = s.split(":", 1)[1].strip()
                elif not gl_version and s.startswith("OpenGL ES profile version:"):
                    gl_version = s.split(":", 1)[1].strip()
                elif not egl_version and s.startswith("EGL version string:"):
                    egl_version = f"EGL {s.split(':', 1)[1].strip()}"
            subtitle_parts = []
            if egl_state["platform"]:
                subtitle_parts.append(f"Platform: {egl_state['platform'].upper()}")
            if egl_version:
                subtitle_parts.append(egl_version)
            if gl_version:
                subtitle_parts.append(f"OpenGL {gl_version}")
            gpu_subtitle_label.set_text("  •  ".join(subtitle_parts))
            gpu_subtitle_label.set_visible(bool(subtitle_parts))

            gpu_logo.set_pixbuf(
                get_gpuz_vendor_logo_pixbuf(renderer) or getLogo(renderer)
            )
            device_root = ExpandDataObject3(device["label"], pixbuf, "")
            for section in device["sections"]:
                platform_root = ExpandDataObject3(section["platform"], pixbuf, "")
                platform_root.children.extend(section["rows"])
                device_root.children.append(platform_root)
            egl_root.children.append(device_root)
        else:
            gpu_name_label.set_text("No EGL GPUs detected")
            gpu_subtitle_label.set_text("")
            gpu_subtitle_label.set_visible(False)
            gpu_logo.set_pixbuf(pixbuf)
            egl_root.children.append(
                ExpandDataObject3("No EGL GPU details available", pixbuf, "")
            )

        opengl_info_list.remove_all()
        opengl_info_list.append(egl_root)
        update_sidebar_support(devices[0] if devices else None)

    def show_spinner(page_name):
        if page_name in page_spinners:
            page_spinners[page_name].set_visible(True)
            page_spinners[page_name].start()
            page_content_containers[page_name].set_visible(False)

    def hide_spinner(page_name):
        if page_name in page_spinners:
            page_spinners[page_name].set_visible(False)
            page_spinners[page_name].stop()
            page_content_containers[page_name].set_visible(True)

    def opengl_info():
        if "opengl-information" in loaded_pages:
            return
        
        show_spinner("opengl-information")
        
        def bg_worker():
            dummy_transparent = GdkPixbuf.Pixbuf.new_from_file_at_size(const.TRANSPARENT_PIXBUF, 24, 20)

            egl_lines = []
            used_platform = ""
            for platform in detect_egl_platform():
                try:
                    result = subprocess.run(
                        ["eglinfo", "-p", platform, "-l"],
                        capture_output=True,
                        text=True,
                        check=False,
                        timeout=15,
                    )
                    lines = result.stdout.splitlines()
                    if result.returncode == 0 and parse_eglinfo_devices(lines):
                        egl_lines = lines
                        used_platform = platform
                        break
                except (OSError, subprocess.TimeoutExpired) as error:
                    print(f"Failed to query eglinfo -p {platform} -l: {error}")

            egl_state["platform"] = used_platform
            egl_state["egl_lines"] = egl_lines
            egl_state["devices"] = parse_eglinfo_devices(egl_lines)
            for device in egl_state["devices"]:
                for section in device["sections"]:
                    brief_lines = extract_egl_brief_lines(section["lines"])
                    section["rows"] = parse_glxinfo_brief(
                        brief_lines, dummy_transparent, getLogo
                    )
            egl_state["egl_configs"] = parse_egl_configurations(egl_lines)

            def update_ui():
                opengl_info_list.remove_all()
                info_roots["egl"] = ExpandDataObject3(
                    "EGL Information", dummy_transparent, ""
                )
                egl_state["pixbuf"] = dummy_transparent
                egl_state["ready"] = True
                refresh_egl_device()

                loaded_pages.add("opengl-information")
                hide_spinner("opengl-information")
                return False

            GLib.idle_add(update_ui)

        threading.Thread(target=bg_worker, daemon=True).start()

    def create_loading_page(content_widget, page_name):
        wrapper = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        spinner = Gtk.Spinner()
        spinner.set_size_request(32, 32)
        spinner.set_halign(Gtk.Align.CENTER)
        spinner.set_valign(Gtk.Align.CENTER)
        spinner.set_vexpand(True)
        
        page_spinners[page_name] = spinner
        page_content_containers[page_name] = content_widget
        
        wrapper.append(spinner)
        wrapper.append(content_widget)
        content_widget.set_visible(False)
        return wrapper

    # Stubs to be filled later
    def load_limits_data():
        pass
    
    def load_framebuffer_data():
        pass
        
    def load_extensions_data():
        pass


    
    def clickme(button):

        button.set_sensitive(False)

        createMainFile(Filenames.opengl_core_limits_file,Filenames.fetch_opengl_core_limits_command)

        createMainFile(Filenames.opengl_core_limits_lhs_file,Filenames.fetch_opengl_core_limits_lhs_command)

        LimitsWin = Adw.Window()
        LimitsWin.set_title("OpenGL Hardware Limits")
        headerbar = Adw.HeaderBar.new()
        headerbar.add_css_class(css_class='compact')

        adw_toolbar_view = Adw.ToolbarView.new()
        LimitsWin.set_content(adw_toolbar_view)

        adw_toolbar_view.add_top_bar(headerbar)

        LimitsNotebook = Adw.ViewStack.new()
        limits_stack_switcher = Adw.ViewSwitcher.new()
        limits_stack_switcher.set_policy(1)
        limits_stack_switcher.set_stack(stack=LimitsNotebook)
        headerbar.set_title_widget(title_widget=limits_stack_switcher)
    #    LimitsNotebook.set_property('tab-pos',Gtk.PositionType.LEFT) 
        adw_toolbar_view.set_content(LimitsNotebook)
        LimitsCoreTab = create_tab(LimitsNotebook,"settings","Core",20,True)
    #    LimitsNotebook.append_page(LimitsCoreTab,Gtk.Label(label="\tCore\t"))
        LimitsCoreFrame = Gtk.Frame()
        limitsList = Gtk.StringList()
        limitsDropDown =Gtk.DropDown()
        limitsDropDown.set_model(limitsList)
        setMargin(limitsDropDown,2,2,2)

        # get Combo box value
        limitsList.append("Show All OpenGL Hardware Core Limits")
        with open(Filenames.opengl_core_limits_lhs_file,"r") as file1:
            for line in file1:
                if ":" in line:
                    text = line[:-2]
                    limitsList.append(text.strip(" "))

        LimitsCoreTab.append(LimitsCoreFrame)
        LimitsGrid = Gtk.Grid()
        LimitsGrid.set_row_spacing(5)
        LimitsCoreFrame.set_child(LimitsGrid)
        LimitsGrid.attach(limitsDropDown,0,0,1,1)

        limitsColumnView = Gtk.ColumnView()
        limitsColumnView.props.show_row_separators = True
        limitsColumnView.props.show_column_separators = False

        factory_limits = Gtk.SignalListItemFactory()
        factory_limits.connect("setup",setup_expander)
        factory_limits.connect("bind",bind_expander)

        factory_limits_value = Gtk.SignalListItemFactory()
        factory_limits_value.connect("setup",setup)
        factory_limits_value.connect("bind",bind1)

        limitSelection = Gtk.SingleSelection()
        LimitsCore_Store = Gio.ListStore.new(ExpandDataObject)

        limitModel = Gtk.TreeListModel.new(LimitsCore_Store,False,True,add_tree_node)
        limitSelection.set_model(limitModel)

        limitsColumnView.set_model(limitSelection)

        limitColumnLhs = Gtk.ColumnViewColumn.new("OpenGL Hardware Limits",factory_limits)
        limitColumnLhs.set_resizable(True)
        limitColumnRhs = Gtk.ColumnViewColumn.new("Value",factory_limits_value)
        limitColumnRhs.set_expand(True)

        limitsColumnView.append_column(limitColumnLhs)
        limitsColumnView.append_column(limitColumnRhs)


    #    LimitsCore_Store = Gtk.TreeStore(str, str, str)
    #    TreeCoreLimits = Gtk.TreeView.new_with_model(LimitsCore_Store)
    #    TreeCoreLimits.set_property("enable-grid-lines",1)


        showLimits(limitsDropDown,0, LimitsCore_Store, limitsColumnView,Filenames.opengl_core_limits_file)
        limitsDropDown.connect("notify::selected-item",showLimits, LimitsCore_Store, limitsColumnView,Filenames.opengl_core_limits_file)

    #    showLimits(LimitRHSValue, LimitsRHS, LimitsCore_Store, TreeCoreLimits,"/tmp/gpu-viewer/OpenGLCoreLimitsLHS.txt")

    #    setColumns(TreeCoreLimits, LimitsTitle, const.MWIDTH,0.0)
        LimitsCoreScrollbar = create_scrollbar(limitsColumnView)
        LimitsGrid.attach_next_to(LimitsCoreScrollbar,limitsDropDown,Gtk.PositionType.BOTTOM,1,1)

        createMainFile(Filenames.opengl_compat_limits_file,Filenames.fetch_opengl_compat_limits_command)

        createMainFile(Filenames.opengl_compat_limits_lhs_file,Filenames.fetch_opengl_compat_limits_lhs_command)

        LimitsCompatTab = create_tab(LimitsNotebook,"settings","Compat.",20,True)
    #    LimitsNotebook.append_page(LimitsCompatTab,Gtk.Label(label="    Compat.\t"))
        LimitsCompatFrame = Gtk.Frame()
        LimitsCompat_List = Gtk.StringList()
        limitsCompatDropDown = Gtk.DropDown()
        limitsCompatDropDown.set_model(LimitsCompat_List)
        LimitsCompat_List.append("Show All OpenGL Hardware Compatible Limits")
        with open(Filenames.opengl_compat_limits_lhs_file,"r") as file1:
            for line in file1:
                if ":" in line:
                    text = line[:-2]
                    LimitsCompat_List.append(text.strip(" "))


        LimitsCompatTab.append(LimitsCompatFrame)
        limitsCompatGrid = Gtk.Grid()
        limitsCompatGrid.set_row_spacing(5)
        LimitsCompatFrame.set_child(limitsCompatGrid)
        limitsCompatGrid.attach(limitsCompatDropDown,0,0,1,1)

    
        limitsCompatColumnView = Gtk.ColumnView()
        limitsCompatColumnView.props.show_row_separators = True
        limitsCompatColumnView.props.show_column_separators = False

        factory_compat_limits = Gtk.SignalListItemFactory()
        factory_compat_limits.connect("setup",setup_expander)
        factory_compat_limits.connect("bind",bind_expander)

        factory_compat_limits_value = Gtk.SignalListItemFactory()
        factory_compat_limits_value.connect("setup",setup)
        factory_compat_limits_value.connect("bind",bind1)

        limitCompatSelection = Gtk.SingleSelection()
        LimitsCompat_Store = Gio.ListStore.new(ExpandDataObject)

        limitCompatModel = Gtk.TreeListModel.new(LimitsCompat_Store,False,True,add_tree_node)
        limitCompatSelection.set_model(limitCompatModel)

        limitsCompatColumnView.set_model(limitCompatSelection)

        limitCompatColumnLhs = Gtk.ColumnViewColumn.new("OpenGL Hardware Limits",factory_compat_limits)
        limitCompatColumnLhs.set_resizable(True)
        limitCompatColumnRhs = Gtk.ColumnViewColumn.new("Value",factory_compat_limits_value)
        limitCompatColumnRhs.set_expand(True)

        limitsCompatColumnView.append_column(limitCompatColumnLhs)
        limitsCompatColumnView.append_column(limitCompatColumnRhs)

    #    LimitsCompat_Store = Gtk.TreeStore(str,str,str)
    #    TreeCompatLimits = Gtk.TreeView.new_with_model(LimitsCompat_Store)
    #    TreeCompatLimits.set_property("enable-grid-lines",1)

        showLimits(limitsCompatDropDown,0, LimitsCompat_Store, limitsCompatColumnView,Filenames.opengl_compat_limits_file)
        limitsCompatDropDown.connect("notify::selected-item",showLimits, LimitsCompat_Store, limitsCompatColumnView,Filenames.opengl_compat_limits_file)


     #   showLimits(LimitRHSValue2, LimitsRHS2, LimitsCompat_Store, TreeCompatLimits,"/tmp/gpu-viewer/OpenGLLimitsLHS.txt")

    #    setColumns(TreeCompatLimits, LimitsTitle, const.MWIDTH,0.0)
        LimitsCompatScrollbar = create_scrollbar(limitsCompatColumnView)
        limitsCompatGrid.attach_next_to(LimitsCompatScrollbar,limitsCompatDropDown,Gtk.PositionType.BOTTOM,1,1)

        def button_enable(win):
            button.set_sensitive(True)
        LimitsWin.connect("close-request",button_enable)
        screen_width,screen_height = getScreenSize()
        LimitsWin.set_default_size(960, 640)
        LimitsWin.set_size_request(650, 450)

        LimitsWin.present()

    def showLimits(dropdown,dummy,Limits_Store, TreeLimits,openGLLimits):
        selected =dropdown.props.selected_item
        limitValue = ""
        if selected is not None:
            limitValue = selected.props.string
        
        def bg_worker(limitValue):
            k = 0
            count = 0
            select_opengl_limits_file = Filenames.select_opengl_limits_file
            if "Show All OpenGL Hardware Core Limits" in limitValue or "Show All OpenGL Hardware Compatible Limits" in limitValue:
                select_opengl_limits_file = openGLLimits
                with open(select_opengl_limits_file, "r") as file:
                    limit_lines = file.readlines()
            else:
                with open(openGLLimits, "r") as file:
                    limit_lines = select_limit_section(file, limitValue)
                with open(select_opengl_limits_file, "w") as file:
                    file.writelines(limit_lines)

            opengl_limits_lhs, opengl_limits_rhs = parse_limit_lines(limit_lines)
            LimitsRHS,LimitRHSValue = appendLimitsRHS(select_opengl_limits_file,opengl_limits_rhs)

            def update_ui():
                Limits_Store.remove_all()
                toprow = None
                iter3 = None
                count = 0
                toprow_added = False
                with open(select_opengl_limits_file,"r") as file:
                    for i, line in enumerate(file):
            #         TreeLimits.expand_all()
                        text = opengl_limits_lhs[i].strip(' ')
                        if ("TEXTURE_FORMATS" in line or "SHADING_LANGUAGE" in line) and LimitRHSValue[i] == True:
                            try:
                            #    iter3 = Limits_Store.append(iter2, [text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                                iter3 = ExpandDataObject(text.strip('\n'), LimitsRHS[i].strip('\n'))
                                toprow.children.append(iter3)
                            except Exception:
                            #    iter3 = Limits_Store.append(None, [text.strip('\n'), LimitsRHS[i].strip('\n'), background_color])
                                toprow = ExpandDataObject(text.strip('\n'), LimitsRHS[i].strip('\n'))
                                toprow_added = False
                    #         toprow.children.append(iter3)
                            finally:
                                pass
                        elif "      " in line and LimitRHSValue[i] == False and ":" not in line:
                            iter4 = ExpandDataObject(text.strip('\n'), LimitsRHS[i].strip('\n'))
                            iter3.children.append(iter4)
                        else:
                            if ":" in line:
                                k = 0
                                text = opengl_limits_lhs[i]
                                count += 1
                                if toprow is not None and not toprow_added:
                                    Limits_Store.append(toprow)
                                toprow = ExpandDataObject(text.strip('\n'), LimitsRHS[i].strip('\n'))
                                toprow_added = False
                                continue
                            if count > 0 and "    " in line:
                                iter2_1 = ExpandDataObject(text.strip('\n'), LimitsRHS[i].strip('\n'))
                                toprow.children.append(iter2_1)
                            else:
                                toprow = ExpandDataObject(text.strip('\n'), LimitsRHS[i].strip('\n'))
                                Limits_Store.append(toprow)
                                toprow_added = True
                if toprow is not None and not toprow_added:
                    Limits_Store.append(toprow)
                return False

            GLib.idle_add(update_ui)

        threading.Thread(target=bg_worker, args=(limitValue,), daemon=True).start()


    def radcall2(dropdown,dummy,List,filename,Store,tree,filter,type_name="OpenGL"):
        selected = dropdown.props.selected_item
        value = 0
        if selected is not None:
            value = dropdown.props.selected

        GL_All = []

    #    List = copyContentsFromFile("/tmp/gpu-viewer/Vendor1.txt")
        List = [i.strip(' ') for i in List]
        List = [i.strip('\n ') for i in List]

        vendor_name = None
        if isinstance(value, int) and 0 <= value < len(List):
            vendor_name = List[value]
        elif selected is not None:
            vendor_name = selected.props.string if hasattr(selected, 'props') else str(selected)
        elif List:
            vendor_name = List[0]

        if vendor_name is None:
            return

        with open(filename, "r") as file1:
            for line in file1:
                if vendor_name == "Total":
                    GL_All.append(line)
                elif "_%s_" % vendor_name in line:
                    GL_All.append(line)

        Store.remove_all()
    #    tree.set_model(filter)

    #    for i in range(len(List)):
    #        if int(value) == i:
    #            frame4.set_label(List[i])

        for text in GL_All:
            Store.append(DataObject2(text.strip(' \n')))
        if not GL_All:
            Store.append(DataObject2(f"No {type_name} extensions available"))

    def getVendorList(filename):
        vendor_counts = {}
        total_count = 0
        
        if not os.path.exists(filename):
            return ["Total (0)"], ["Total"]

        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                total_count += 1
                
                parts = line.split('_')
                if len(parts) > 1:
                    vendor = parts[1]
                    vendor_counts[vendor] = vendor_counts.get(vendor, 0) + 1
        
        sorted_vendors = sorted(vendor_counts.keys())
        vendor_names = ["Total"] + sorted_vendors
        display_list = [f"Total ({total_count})"]
        for v in sorted_vendors:
            display_list.append(f"{v} ({vendor_counts[v]})")
            
        return display_list, vendor_names


#----------------------------------Filter -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    def _on_search_method_changed(search_entry,filterColumn):
        filterColumn.changed(Gtk.FilterChange.DIFFERENT)

# ------------------------------ Check es2_info Supported ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def es2_infoSupported():
        try:
            result = subprocess.run(
                ["es2_info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return result.returncode == 0
        except OSError:
            return False

    def create_sidebar_row(label_text, sensitive=True, css_class=None):
        row = Gtk.ListBoxRow()
        label = Gtk.Label.new(label_text)
        label.set_halign(Gtk.Align.FILL)
        label.set_hexpand(True)
        label.set_xalign(0.5)
        label.set_wrap(True)
        label.set_margin_start(12)
        label.set_margin_end(12)
        label.set_margin_top(6)
        label.set_margin_bottom(6)
        label.set_valign(Gtk.Align.CENTER)
        if css_class:
            label.add_css_class(css_class=css_class)
        row.set_child(label)
        row.set_sensitive(sensitive)
        return row

    def create_limits_page(core_file, core_lhs_file, compat_file, compat_lhs_file,
                              core_label, compat_label):

        limits_page = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        limits_page.add_css_class('toolbar')

        limitsList = Gtk.StringList()
        limitsDropDown = Gtk.DropDown()
        limitsDropDown.set_model(limitsList)

        profile_group = Adw.ToggleGroup.new()
        core_toggle = Adw.Toggle.new()
        core_toggle.set_name("core")
        profile_group.add(core_toggle)
        compat_toggle = Adw.Toggle.new()
        compat_toggle.set_name("compat")
        profile_group.add(compat_toggle)

        core_button = Gtk.ToggleButton.new_with_label("Core")
        compat_button = Gtk.ToggleButton.new_with_label("Compatibility")
        core_button.set_active(True)
        core_button.set_valign(Gtk.Align.CENTER)
        compat_button.set_valign(Gtk.Align.CENTER)

        toggle_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        toggle_box.set_valign(Gtk.Align.CENTER)
        toggle_box.append(core_button)
        toggle_box.append(compat_button)

        top_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)
        top_box.set_hexpand(True)
        top_box.append(limitsDropDown)
        top_box.append(toggle_box)
        limits_page.append(top_box)

        limitsColumnView = Gtk.ColumnView()
        limitsColumnView.props.show_row_separators = True
        limitsColumnView.props.show_column_separators = False

        factory_limits = Gtk.SignalListItemFactory()
        factory_limits.connect("setup", setup_expander)
        factory_limits.connect("bind", bind_expander)

        factory_limits_value = Gtk.SignalListItemFactory()
        factory_limits_value.connect("setup", setup)
        factory_limits_value.connect("bind", bind1)

        limitSelection = Gtk.SingleSelection()
        limits_store = Gio.ListStore.new(ExpandDataObject)
        search_entry = Gtk.SearchEntry()
        search_entry.set_property("placeholder-text", "Type here to filter Limits.....")
        search_entry.add_css_class(css_class='toolbar')

        def filter_func(item, filter_list_model):
            search_text_widget = search_entry.get_text()
            if not search_text_widget:
                return True
            return search_text_widget.upper() in item.data.upper() or search_text_widget.upper() in item.data2.upper()

        filterLimitsListStore = Gtk.FilterListModel(model=limits_store)
        filterLimits = Gtk.CustomFilter.new(filter_func, filterLimitsListStore)
        filterLimitsListStore.set_filter(filterLimits)

        limitModel = Gtk.TreeListModel.new(filterLimitsListStore, False, True, add_tree_node)
        limitSelection.set_model(limitModel)

        limitsColumnView.set_model(limitSelection)
        limitColumnLhs = Gtk.ColumnViewColumn.new("OpenGL Hardware Limits", factory_limits)
        limitColumnLhs.set_resizable(True)
        limitColumnRhs = Gtk.ColumnViewColumn.new("Value", factory_limits_value)
        limitColumnRhs.set_expand(True)
        limitsColumnView.append_column(limitColumnLhs)
        limitsColumnView.append_column(limitColumnRhs)

        current_mode = {"profile": "core", "file": core_file, "lhs": core_lhs_file, "label": core_label}
        limits_output = {"text": None}
        limits_output_lock = threading.Lock()

        def load_limits_profile(profile):
            def bg():
                if not egl_state["egl_lines"]:
                    with limits_output_lock:
                        if not egl_state["egl_lines"]:
                            for platform in detect_egl_platform():
                                try:
                                    result = subprocess.run(
                                        ["eglinfo", "-p", platform, "-l"],
                                        capture_output=True,
                                        text=True,
                                        check=False,
                                        timeout=15,
                                    )
                                    lines = result.stdout.splitlines()
                                    if result.returncode == 0 and lines:
                                        egl_state["egl_lines"] = lines
                                        egl_state["platform"] = platform
                                        break
                                except (OSError, subprocess.TimeoutExpired) as error:
                                    print(f"Failed to query OpenGL limits: {error}")

                if profile == "core":
                    profile_file = core_file
                    profile_lhs_file = core_lhs_file
                    profile_label = core_label
                else:
                    profile_file = compat_file
                    profile_lhs_file = compat_lhs_file
                    profile_label = compat_label

                limit_lines = parse_egl_limits(egl_state["egl_lines"], profile)
                if not limit_lines:
                    limit_lines = [
                        "OpenGL hardware limits unavailable.\n"
                    ]
                with open(profile_file, "w") as file:
                    file.writelines(limit_lines)
                with open(profile_lhs_file, "w") as file:
                    file.writelines(
                        re.sub(r"=.*", "", line) for line in limit_lines
                    )

                def ui():
                    current_mode["file"] = profile_file
                    current_mode["lhs"] = profile_lhs_file
                    current_mode["label"] = profile_label
                    if profile == "core":
                        limitColumnLhs.set_title("OpenGL Hardware Core Limits")
                    else:
                        limitColumnLhs.set_title("OpenGL Hardware Compatible Limits")

                    new_model = Gtk.StringList()
                    new_model.append(current_mode["label"])
                    with open(current_mode["lhs"], "r") as file1:
                        for line in file1:
                            if ":" in line:
                                text = line.split(":")[0]
                                new_model.append(text.strip(" "))
                    limitsDropDown.set_model(new_model)
                    limitsDropDown.set_selected(0)
                    showLimits(limitsDropDown, 0, limits_store, limitsColumnView, current_mode["file"])
                    return False
                GLib.idle_add(ui)
            threading.Thread(target=bg, daemon=True).start()

        def sync_toggle_buttons(profile):
            core_button.handler_block_by_func(on_core_toggled)
            compat_button.handler_block_by_func(on_compat_toggled)
            core_button.set_active(profile == "core")
            compat_button.set_active(profile == "compat")
            core_button.handler_unblock_by_func(on_core_toggled)
            compat_button.handler_unblock_by_func(on_compat_toggled)

        def on_profile_group_changed(group, pspec):
            profile = group.get_active_name()
            if not profile:
                return
            sync_toggle_buttons(profile)
            load_limits_profile(profile)

        def on_core_toggled(button):
            if button.get_active():
                profile_group.set_active_name("core")
            elif profile_group.get_active_name() == "core":
                button.handler_block_by_func(on_core_toggled)
                button.set_active(True)
                button.handler_unblock_by_func(on_core_toggled)

        def on_compat_toggled(button):
            if button.get_active():
                profile_group.set_active_name("compat")
            elif profile_group.get_active_name() == "compat":
                button.handler_block_by_func(on_compat_toggled)
                button.set_active(True)
                button.handler_unblock_by_func(on_compat_toggled)

        core_button.connect("toggled", on_core_toggled)
        compat_button.connect("toggled", on_compat_toggled)
        profile_group.connect("notify::active-name", on_profile_group_changed)

        search_entry.connect("search-changed", _on_search_method_changed, filterLimits)
        limitsDropDown.connect("notify::selected-item", lambda *args: showLimits(limitsDropDown, 0, limits_store, limitsColumnView, current_mode["file"]))
        limits_page.append(create_scrollbar(limitsColumnView))
        limits_page.append(search_entry)
        
        nonlocal load_limits_data
        def load_limits_data_impl():
            if "opengl-limits" in loaded_pages:
                return
            show_spinner("opengl-limits")
            def bg():
                def ui():
                    load_limits_profile("core")
                    loaded_pages.add("opengl-limits")
                    hide_spinner("opengl-limits")
                    return False
                GLib.idle_add(ui)
            threading.Thread(target=bg, daemon=True).start()
        load_limits_data = load_limits_data_impl

        return create_loading_page(limits_page, "opengl-limits")


    def create_framebuffer_page():
        page = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        page.add_css_class('toolbar')

        visuals_lines = []
        fbconfig_lines = []

        profile_group = Adw.ToggleGroup.new()
        visuals_toggle = Adw.Toggle.new()
        visuals_toggle.set_name("glx-visuals")
        profile_group.add(visuals_toggle)
        fbconfig_toggle = Adw.Toggle.new()
        fbconfig_toggle.set_name("glx-fbconfig")
        profile_group.add(fbconfig_toggle)

        frameBufferColumnView = Gtk.ColumnView()
        frameBufferColumnView.props.show_row_separators = True
        frameBufferColumnView.props.show_column_separators = True
        frameBufferColumnView.set_vexpand(True)
        frameBufferColumnView.set_hexpand(True)

        class FramebufferRow(GObject.GObject):
            def __init__(self, values):
                super(FramebufferRow, self).__init__()
                for index, value in enumerate(values, start=1):
                    if index <= 40:
                        setattr(self, f"data{index}", value)
                for index in range(len(values) + 1, 41):
                    setattr(self, f"data{index}", "")

        def make_bind(column_index):
            def bind(widget, item):
                label = item.get_child()
                obj = item.get_item()
                label.set_text(getattr(obj, f"data{column_index}", ""))
            return bind

        headings = const.FRAMEBUFFERLIST
        fb_selection = Gtk.SingleSelection()
        fb_store = Gio.ListStore.new(FramebufferRow)
        
        search_entry = Gtk.SearchEntry()
        search_entry.set_property("placeholder-text", "Type here to filter GLX FB Config.....")
        search_entry.add_css_class(css_class='toolbar')

        def filter_func(item, filter_list_model):
            search_text = search_entry.get_text().upper()
            if not search_text:
                return True
            
            for i in range(1, 41):
                attr = f"data{i}"
                if hasattr(item, attr):
                    val = getattr(item, attr)
                    if val and search_text in val.upper():
                        return True
            return False

        filterFbListStore = Gtk.FilterListModel(model=fb_store)
        filterFb = Gtk.CustomFilter.new(filter_func, filterFbListStore)
        filterFbListStore.set_filter(filterFb)
        fb_selection.set_model(filterFbListStore)
        frameBufferColumnView.set_model(fb_selection)

        def populate_lines(lines):
            fb_store.remove_all()
            for line in lines:
                tokens = line.strip().split()
                fb_store.append(FramebufferRow(tokens))

        def set_active_profile(profile):
            if profile == "glx-visuals":
                lines = visuals_lines
                message = "GLX visual data unavailable (requires GLX)."
            else:
                lines = fbconfig_lines
                message = "GLX framebuffer data unavailable (requires GLX)."
            populate_lines(lines or [message])

        def on_group_changed(group, pspec):
            profile = group.get_active_name()
            if not profile:
                return
            set_active_profile(profile)

        profile_group.connect("notify::active-name", on_group_changed)

        search_entry.connect("search-changed", _on_search_method_changed, filterFb)
        page.append(create_scrollbar(frameBufferColumnView))
        page.append(search_entry)
        
        nonlocal load_framebuffer_data
        framebuffer_loading = {"started": False}

        def setup_fb_cell(widget, item):
            label = Gtk.Label()
            label.props.xalign = 0.0
            label.set_margin_start(6)
            label.set_margin_end(6)
            item.set_child(label)

        def display_framebuffer_data():
            config_rows = egl_state["egl_configs"]
            while frameBufferColumnView.get_columns().get_n_items() > 0:
                frameBufferColumnView.remove_column(
                    frameBufferColumnView.get_columns().get_item(0)
                )

            if config_rows:
                for index, column_name in enumerate(EGL_CONFIG_COLUMNS, start=1):
                    factory = Gtk.SignalListItemFactory()
                    factory.connect("setup", setup_fb_cell)
                    factory.connect("bind", make_bind(index))
                    column = Gtk.ColumnViewColumn.new(column_name, factory)
                    column.set_resizable(True)
                    if index == len(EGL_CONFIG_COLUMNS):
                        column.set_expand(True)
                    frameBufferColumnView.append_column(column)
                fb_store.remove_all()
                for row in config_rows:
                    fb_store.append(FramebufferRow(row))
            else:
                factory_fb = Gtk.SignalListItemFactory()
                factory_fb.connect("setup", setup_fb_cell)
                factory_fb.connect("bind", bind_column1)
                fb_column = Gtk.ColumnViewColumn.new("EGL Configurations", factory_fb)
                fb_column.set_expand(True)
                frameBufferColumnView.append_column(fb_column)
                fb_store.remove_all()
                fb_store.append(FramebufferRow(["EGL configuration data unavailable."]))

        def refresh_framebuffer_data(device):
            config_rows = egl_state["egl_configs"] if device else []
            if "EGL Configurations" in framebuffer_sidebar_labels:
                framebuffer_sidebar_labels["EGL Configurations"].set_text(
                    f"EGL Configurations ({len(config_rows)})"
                )
            if "framebuffer-configuration" in loaded_pages:
                display_framebuffer_data()

        nonlocal refresh_framebuffer_callback
        refresh_framebuffer_callback = refresh_framebuffer_data

        def load_framebuffer_data_impl(profile="egl-configs"):
            if "framebuffer-configuration" in loaded_pages:
                return
            if framebuffer_loading["started"]:
                return
            framebuffer_loading["started"] = True
            show_spinner("framebuffer-configuration")
            refresh_framebuffer_data(
                egl_state["devices"][0] if egl_state["devices"] else None
            )
            display_framebuffer_data()
            loaded_pages.add("framebuffer-configuration")
            hide_spinner("framebuffer-configuration")
        load_framebuffer_data = load_framebuffer_data_impl

        return create_loading_page(page, "framebuffer-configuration")


    def create_extensions_page():
        page = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        page.add_css_class('toolbar')

        extensionColumnView = Gtk.ColumnView()
        extensionColumnView.props.show_row_separators = True
        extensionColumnView.props.single_click_activate = False
        extensionColumnView.props.show_column_separators = False

        factory_extension = Gtk.SignalListItemFactory()
        factory_extension.connect("setup", setup)
        factory_extension.connect("bind", bind_column1)

        extensionColumn = Gtk.ColumnViewColumn.new("Extensions", factory_extension)
        extensionColumn.set_expand(True)
        extensionColumnView.append_column(extensionColumn)

        extensionSelection = Gtk.SingleSelection()
        extension_list = Gio.ListStore.new(DataObject2)

        search_entry = Gtk.SearchEntry()
        search_entry.set_property("placeholder-text", "Type here to filter extensions.....")
        search_entry.add_css_class(css_class='toolbar')

        def filter_func(item, filter_list_model):
            search_text_widget = search_entry.get_text()
            return search_text_widget.upper() in item.column1.upper()

        filterExtensionListStore = Gtk.FilterListModel(model=extension_list)
        filterExtensions = Gtk.CustomFilter.new(filter_func, filterExtensionListStore)
        filterExtensionListStore.set_filter(filterExtensions)
        extensionSelection.set_model(filterExtensionListStore)
        extensionColumnView.set_model(extensionSelection)

        vendor_list = Gtk.StringList()
        vendor_dropdown = Gtk.DropDown()
        vendor_dropdown.set_model(vendor_list)
        setMargin(vendor_dropdown, 2, 1, 2)

        current_type = {"name": "OpenGL", "file": Filenames.opengl_vendor_gl_extension_file}
        opengl_profile = {"mode": "core"}
        tool_output_cache = {"eglinfo": None, "es2_info": None}
        tool_output_lock = threading.Lock()

        # Map type name -> Adw.Toggle widget for show/hide on GPU change
        type_toggle_widgets = {}

        def update_extension_header():
            if current_type["name"] == "OpenGL":
                if opengl_profile["mode"] == "core":
                    extensionColumn.set_title("OpenGL Core Extensions")
                else:
                    extensionColumn.set_title("OpenGL Compatible Extensions")
            elif current_type["name"] == "OpenGL ES":
                extensionColumn.set_title("OpenGL ES Extensions")
            elif current_type["name"] == "GLX":
                extensionColumn.set_title("GLX Extensions")
            elif current_type["name"] == "EGL":
                extensionColumn.set_title("EGL Extensions")
            else:
                extensionColumn.set_title("Extensions")

        type_group = Adw.ToggleGroup.new()
        for type_name in ("OpenGL", "OpenGL ES", "GLX", "EGL"):
            type_toggle = Adw.Toggle.new()
            type_toggle.set_name(type_name)
            type_group.add(type_toggle)
            type_toggle_widgets[type_name] = type_toggle

        profile_group = Adw.ToggleGroup.new()
        core_profile_toggle = Adw.Toggle.new()
        core_profile_toggle.set_name("core")
        profile_group.add(core_profile_toggle)
        compat_profile_toggle = Adw.Toggle.new()
        compat_profile_toggle.set_name("compat")
        profile_group.add(compat_profile_toggle)

        core_button = Gtk.ToggleButton.new_with_label("Core")
        compat_button = Gtk.ToggleButton.new_with_label("Compatibility")
        core_button.set_active(True)
        core_button.set_valign(Gtk.Align.CENTER)
        compat_button.set_valign(Gtk.Align.CENTER)

        profile_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 6)
        profile_box.set_valign(Gtk.Align.CENTER)
        profile_box.append(core_button)
        profile_box.append(compat_button)

        vendor_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)
        vendor_box.set_hexpand(True)
        vendor_box.set_halign(Gtk.Align.START)
        vendor_box.append(vendor_dropdown)
        vendor_box.append(profile_box)

        def get_tool_output(tool):
            with tool_output_lock:
                cached = tool_output_cache[tool]
                if cached is not None:
                    return cached
                environment = {**os.environ, "EGL_PLATFORM": "surfaceless"}
                try:
                    result = subprocess.run(
                        [tool],
                        capture_output=True,
                        text=True,
                        check=False,
                        timeout=15,
                        env=environment,
                    )
                    if result.returncode != 0:
                        print(f"{tool} failed: {result.stderr.strip()}")
                    output = result.stdout.splitlines()
                except (OSError, subprocess.TimeoutExpired) as error:
                    print(f"Failed to query {tool}: {error}")
                    output = []
                tool_output_cache[tool] = output
                return output

        def prepare_opengl_extension_file(profile, device_ext_lines=None):
            if profile == "core":
                start_marker = "OpenGL core profile extensions:"
            else:
                start_marker = "OpenGL compatibility profile extensions:"

            lines = []
            # First try to use per-device extension data from eglinfo
            if device_ext_lines is not None:
                lines = parse_extension_tokens(device_ext_lines, start_marker, "GL_")
            if not lines and os.path.exists(Filenames.opengl_outpuf_file):
                with open(Filenames.opengl_outpuf_file, "r") as src:
                    lines = parse_extension_tokens(src, start_marker, "GL_")
            if not lines:
                lines = parse_extension_tokens(
                    get_tool_output("eglinfo"), start_marker, "GL_"
                )

            with open(Filenames.opengl_vendor_gl_extension_file, "w") as file:
                file.write("\n".join(sorted(lines)))

        # Device-specific extension lines from the currently selected EGL device
        device_ext_lines_cache = {"lines": None}

        def prepare_type_file(type_name, callback=None):
            current_type["name"] = type_name
            dev_lines = device_ext_lines_cache["lines"] or egl_state["egl_lines"]
            def bg():
                if type_name == "OpenGL":
                    current_type["file"] = Filenames.opengl_vendor_gl_extension_file
                    prepare_opengl_extension_file(opengl_profile["mode"], dev_lines)
                elif type_name == "OpenGL ES":
                    current_type["file"] = Filenames.opengl_vendor_es_extension_file
                    extensions = parse_extension_tokens(
                        dev_lines, "OpenGL ES profile extensions:", "GL_"
                    )
                    if not extensions:
                        extensions = parse_extension_tokens(
                            get_tool_output("es2_info"), "GL_EXTENSIONS", "GL_"
                        )
                    with open(current_type["file"], "w") as file:
                        file.write("\n".join(extensions))
                else:
                    current_type["file"] = Filenames.egl_vendor_extension_file
                    extensions = parse_extension_tokens(
                        dev_lines, "EGL extensions string:", "EGL_"
                    )
                    if not extensions:
                        extensions = parse_extension_tokens(
                            dev_lines, "EGL_EXTENSIONS:", "EGL_"
                        )
                    with open(current_type["file"], "w") as file:
                        file.write("\n".join(extensions))

                def ui():
                    update_extension_header()
                    if callback: callback()
                    return False
                GLib.idle_add(ui)
            threading.Thread(target=bg, daemon=True).start()

        def refresh_vendors(callback=None):
            def bg():
                VendorList, vendor_names = getVendorList(current_type["file"])
                def ui():
                    new_vendor_model = Gtk.StringList()
                    for item in VendorList:
                        new_vendor_model.append(item)
                    vendor_dropdown.set_model(new_vendor_model)
                    vendor_dropdown.set_selected(0)
                    if callback: callback(VendorList, vendor_names)
                    return False
                GLib.idle_add(ui)
            threading.Thread(target=bg, daemon=True).start()

        current_vendors = {"names": []}

        def update_extension_list():
            def on_vendors_ready(VendorList, vendor_names):
                current_vendors["names"] = vendor_names
                radcall2(
                    vendor_dropdown, 0, vendor_names, current_type["file"],
                    extension_list, extensionColumnView, extension_list,
                    current_type["name"],
                )
            refresh_vendors(on_vendors_ready)

        def set_profile_visibility(type_name):
            profile_box.set_visible(type_name == "OpenGL")

        def on_type_group_changed(group, pspec):
            type_name = group.get_active_name()
            if not type_name:
                return
            set_profile_visibility(type_name)
            prepare_type_file(type_name, update_extension_list)

        def sync_profile_buttons(profile):
            core_button.handler_block_by_func(on_core_toggled)
            compat_button.handler_block_by_func(on_compat_toggled)
            core_button.set_active(profile == "core")
            compat_button.set_active(profile == "compat")
            core_button.handler_unblock_by_func(on_core_toggled)
            compat_button.handler_unblock_by_func(on_compat_toggled)

        def on_profile_group_changed(group, pspec):
            profile = group.get_active_name()
            if not profile:
                return
            sync_profile_buttons(profile)
            opengl_profile["mode"] = profile
            if current_type["name"] == "OpenGL":
                prepare_type_file("OpenGL", update_extension_list)
            update_extension_header()

        def on_core_toggled(button):
            if button.get_active():
                profile_group.set_active_name("core")
            elif profile_group.get_active_name() == "core":
                button.handler_block_by_func(on_core_toggled)
                button.set_active(True)
                button.handler_unblock_by_func(on_core_toggled)

        def on_compat_toggled(button):
            if button.get_active():
                profile_group.set_active_name("compat")
            elif profile_group.get_active_name() == "compat":
                button.handler_block_by_func(on_compat_toggled)
                button.set_active(True)
                button.handler_unblock_by_func(on_compat_toggled)

        def apply_device_extension_support(device_extensions, glx_extensions):
            """Called when device data loads — update toggle state and reload."""
            if egl_state["devices"]:
                dev = egl_state["devices"][0]
                ext_sections = dev.get("ext_sections") or dev.get("sections", [])
                device_ext_lines_cache["lines"] = [
                    line
                    for section in ext_sections
                    for line in section.get("lines", [])
                ]
            else:
                device_ext_lines_cache["lines"] = None

            type_support = {
                "OpenGL": bool(
                    device_extensions.get("OpenGL core")
                    or device_extensions.get("OpenGL compatibility")
                ),
                "OpenGL ES": bool(device_extensions.get("OpenGL ES")),
                "GLX": bool(glx_extensions),
                "EGL": bool(device_extensions.get("EGL")),
            }

            # Update type toggles without triggering the signal
            type_group.handler_block_by_func(on_type_group_changed)
            for tname, toggle in type_toggle_widgets.items():
                toggle.set_enabled(type_support.get(tname, False))
            type_group.handler_unblock_by_func(on_type_group_changed)

            # If the current type is now hidden, switch to first visible type
            current = current_type["name"]
            if not type_support.get(current, False):
                first_visible = next(
                    (t for t in ("OpenGL", "OpenGL ES", "GLX", "EGL") if type_support.get(t, False)),
                    None,
                )
                if first_visible:
                    type_group.handler_block_by_func(on_type_group_changed)
                    type_group.set_active_name(first_visible)
                    type_group.handler_unblock_by_func(on_type_group_changed)
                    set_profile_visibility(first_visible)
                    current_type["name"] = first_visible

            # Reload current extension content if the page is already loaded
            if "extensions" in loaded_pages:
                prepare_type_file(current_type["name"], update_extension_list)

        nonlocal refresh_extensions_callback
        refresh_extensions_callback = apply_device_extension_support

        type_group.connect("notify::active-name", on_type_group_changed)

        core_button.connect("toggled", on_core_toggled)
        compat_button.connect("toggled", on_compat_toggled)
        profile_group.connect("notify::active-name", on_profile_group_changed)

        vendor_dropdown.connect(
            'notify::selected-item',
            lambda dropdown, *_: radcall2(
                dropdown, 0, current_vendors["names"], current_type["file"],
                extension_list, extensionColumnView, extension_list,
                current_type["name"],
            ),
        )

        search_entry.connect("search-changed", _on_search_method_changed, filterExtensions)

        page.append(vendor_box)
        page.append(create_scrollbar(extensionColumnView))
        page.append(search_entry)

        nonlocal load_extensions_data
        def load_extensions_data_impl(type_name="OpenGL"):
            if "extensions" in loaded_pages:
                if type_group.get_active_name() != type_name:
                    type_group.set_active_name(type_name)
                return
            show_spinner("extensions")

            def on_ready():
                loaded_pages.add("extensions")
                hide_spinner("extensions")

            profile_group.handler_block_by_func(on_profile_group_changed)
            profile_group.set_active_name("core")
            profile_group.handler_unblock_by_func(on_profile_group_changed)
            sync_profile_buttons("core")
            opengl_profile["mode"] = "core"

            type_group.handler_block_by_func(on_type_group_changed)
            type_group.set_active_name(type_name)
            type_group.handler_unblock_by_func(on_type_group_changed)
            set_profile_visibility(type_name)
            prepare_type_file(type_name, lambda: (update_extension_list(), on_ready()))

        load_extensions_data = load_extensions_data_impl

        return create_loading_page(page, "extensions")


    sidebar_listboxes = []

    def on_row_activated(listbox, row):
        for other_listbox in sidebar_listboxes:
            if other_listbox is not listbox:
                other_listbox.unselect_all()
        tab_label = row.get_child()
        tab_name = tab_label.get_label()
        if not row.get_sensitive():
            return
        sidebar_target_names = {
            "EGL Information": "opengl-information",
            "OpenGL Limits": "opengl-limits",
            "OpenGL": "extensions",
            "OpenGL ES": "extensions",
            "EGL": "extensions",
        }
        framebuffer_profiles = {
            "EGL Configurations": "egl-configs",
        }
        framebuffer_profile = next(
            (profile for label, profile in framebuffer_profiles.items() if tab_name.startswith(label)),
            None,
        )
        child_name = sidebar_target_names.get(tab_name)
        if framebuffer_profile is not None:
            child_name = "framebuffer-configuration"
        if child_name is not None:
            content_stack.set_visible_child_name(child_name)
            if child_name == "opengl-information":
                opengl_info()
            elif child_name == "opengl-limits":
                load_limits_data()
            elif child_name == "framebuffer-configuration":
                load_framebuffer_data(framebuffer_profile or "egl-configs")
            elif child_name == "extensions":
                load_extensions_data(tab_name)


    opengl_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
    opengl_box.set_vexpand(True)
    opengl_box.set_hexpand(True)
    tab.append(opengl_box)

    split_view = Adw.NavigationSplitView.new()
    split_view.set_vexpand(True)
    split_view.set_hexpand(True)

    sidebar_vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
    sidebar_vbox.set_vexpand(True)

    framebuffer_sidebar_labels = {}
    sidebar_groups = [
        ("EGL", ["EGL Information", "OpenGL Limits"]),
        ("EGL FB Config", ["EGL Configurations"]),
        ("EXTENSIONS", ["OpenGL", "OpenGL ES", "EGL"]),
    ]
    for section_title, row_labels in sidebar_groups:
        heading = Gtk.Label.new(section_title)
        heading.add_css_class("heading")
        heading.set_halign(Gtk.Align.FILL)
        heading.set_hexpand(True)
        heading.set_xalign(0.5)
        heading.set_wrap(True)
        heading.set_margin_top(10)
        heading.set_margin_bottom(6)
        sidebar_vbox.append(heading)
        sidebar_headings[section_title] = heading
        sidebar_group_rows[section_title] = row_labels

        group_listbox = Gtk.ListBox.new()
        group_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        group_listbox.add_css_class("boxed-list")
        group_listbox.add_css_class("sidebar")
        group_listbox.set_show_separators(True)
        for row_label in row_labels:
            row = create_sidebar_row(row_label, True)
            if row_label not in ("EGL Information", "OpenGL Limits"):
                row.set_visible(False)
            sidebar_rows[row_label] = row
            group_listbox.append(row)
            if row_label == "EGL Configurations":
                framebuffer_sidebar_labels[row_label] = row.get_child()
        group_listbox.connect("row-activated", on_row_activated)
        sidebar_listboxes.append(group_listbox)
        sidebar_listbox_map[section_title] = group_listbox
        sidebar_vbox.append(group_listbox)

    content_stack = Gtk.Stack.new()
    content_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
    content_stack.set_vexpand(True)
    content_stack.set_hexpand(True)

    info_page = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
    info_page.set_vexpand(True)
    info_page.set_hexpand(True)
    info_page.set_halign(Gtk.Align.FILL)
    info_page.set_valign(Gtk.Align.FILL)

    openglColumnView = Gtk.ColumnView()
    openglColumnView.props.show_row_separators = True
    openglColumnView.props.single_click_activate = False
    openglColumnView.props.show_column_separators = False
    openglColumnView.set_vexpand(True)
    openglColumnView.set_hexpand(True)

    factoryOpenglLhs = Gtk.SignalListItemFactory()
    factoryOpenglLhs.connect("setup", setup_expander)
    factoryOpenglLhs.connect("bind", bind_expander)
    factory_image = Gtk.SignalListItemFactory()
    factory_image.connect("setup", setup_image)
    factory_image.connect("bind", bind_image)
    factoryOpenglRhs = Gtk.SignalListItemFactory()
    factoryOpenglRhs.connect("setup", setup)
    factoryOpenglRhs.connect("bind", bind_column3)

    openglColumn1 = Gtk.ColumnViewColumn.new("EGL Information")
    openglColumn1.set_factory(factoryOpenglLhs)
    openglColumn1.set_expand(False)
    openglColumn1.set_resizable(True)
    openglColumnView.append_column(openglColumn1)

    openglColumnLogo = Gtk.ColumnViewColumn.new("")
    openglColumnLogo.set_factory(factory_image)
    openglColumnView.append_column(openglColumnLogo)

    openglColumn2 = Gtk.ColumnViewColumn.new("Details")
    openglColumn2.set_factory(factoryOpenglRhs)
    openglColumn2.set_expand(True)
    openglColumnView.append_column(openglColumn2)

    openglSelection = Gtk.SingleSelection()
    opengl_info_list = Gio.ListStore.new(ExpandDataObject3)
    opengl_info_model = Gtk.TreeListModel.new(opengl_info_list, False, True, add_tree_node3)
    openglSelection.set_model(opengl_info_model)
    openglColumnView.set_model(openglSelection)

    opengl_info_scrollbar = create_scrollbar(openglColumnView)
    opengl_info_scrollbar.set_vexpand(True)
    opengl_info_scrollbar.set_hexpand(True)
    opengl_info_scrollbar.set_valign(Gtk.Align.FILL)
    opengl_info_scrollbar.set_min_content_height(440)

    # --- Compact Libadwaita Card Banner for Active EGL Device ---
    gpu_logo_pixbuf = (
        get_gpuz_vendor_logo_pixbuf("")
        or GdkPixbuf.Pixbuf.new_from_file_at_size(const.APP_LOGO_PNG, 38, 38)
    )
    gpu_logo = Gtk.Picture.new_for_pixbuf(gpu_logo_pixbuf)
    gpu_logo.set_content_fit(Gtk.ContentFit.CONTAIN)
    gpu_logo.set_size_request(38, 38)
    gpu_logo.set_valign(Gtk.Align.CENTER)

    gpu_name_label = Gtk.Label.new("Detecting EGL device...")
    gpu_name_label.add_css_class("title-4")
    gpu_name_label.set_xalign(0.0)
    gpu_name_label.set_ellipsize(Pango.EllipsizeMode.END)

    gpu_subtitle_label = Gtk.Label.new("")
    gpu_subtitle_label.add_css_class("dim-label")
    gpu_subtitle_label.add_css_class("caption")
    gpu_subtitle_label.set_xalign(0.0)
    gpu_subtitle_label.set_ellipsize(Pango.EllipsizeMode.END)
    gpu_subtitle_label.set_visible(False)

    banner_text_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 2)
    banner_text_box.set_valign(Gtk.Align.CENTER)
    banner_text_box.set_hexpand(True)
    banner_text_box.append(gpu_name_label)
    banner_text_box.append(gpu_subtitle_label)

    banner_row = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 14)
    banner_row.set_margin_top(10)
    banner_row.set_margin_bottom(10)
    banner_row.set_margin_start(14)
    banner_row.set_margin_end(14)
    banner_row.append(gpu_logo)
    banner_row.append(banner_text_box)

    banner_card = Adw.Bin.new()
    banner_card.add_css_class("card")
    banner_card.set_child(banner_row)

    banner_clamp = Adw.Clamp.new()
    banner_clamp.set_maximum_size(720)
    banner_clamp.set_margin_top(8)
    banner_clamp.set_margin_bottom(4)
    banner_clamp.set_margin_start(12)
    banner_clamp.set_margin_end(12)
    banner_clamp.set_child(banner_card)
    opengl_box.append(banner_clamp)

    info_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)
    info_box.set_hexpand(True)
    info_box.set_vexpand(True)
    info_box.append(opengl_info_scrollbar)
    info_page.append(info_box)

    info_page_wrapped = create_loading_page(info_page, "opengl-information")

    limits_page = create_limits_page(
        Filenames.opengl_core_limits_file,
        Filenames.opengl_core_limits_lhs_file,
        Filenames.opengl_compat_limits_file,
        Filenames.opengl_compat_limits_lhs_file,
        "Show All OpenGL Hardware Core Limits",
        "Show All OpenGL Hardware Compatible Limits",
    )

    framebuffer_page = create_framebuffer_page()

    extensions_page = create_extensions_page()

    content_stack.add_titled(info_page_wrapped, "opengl-information", "OpenGL Information")
    content_stack.add_titled(limits_page, "opengl-limits", "OpenGL Limits")
    content_stack.add_titled(framebuffer_page, "framebuffer-configuration", "GLX FB Config")
    content_stack.add_titled(extensions_page, "extensions", "Extensions")

    sidebar_scrolled_window = Gtk.ScrolledWindow.new()
    sidebar_scrolled_window.set_vexpand(True)
    sidebar_scrolled_window.set_hexpand(True)
    sidebar_scrolled_window.set_child(sidebar_vbox)

    sidebar_page = Adw.NavigationPage.new(sidebar_scrolled_window, "Sidebar")
    content_page = Adw.NavigationPage.new(content_stack, "Content")
    sidebar_page.set_vexpand(True)
    sidebar_page.set_hexpand(True)
    content_page.set_vexpand(True)
    content_page.set_hexpand(True)
    split_view.set_sidebar(sidebar_page)
    split_view.set_content(content_page)

    create_sidebar_toggle(opengl_box, split_view)
    opengl_box.append(split_view)

    sidebar_listboxes[0].select_row(sidebar_listboxes[0].get_row_at_index(0))
    content_stack.set_visible_child_name("opengl-information")
    opengl_info()

    return tab
