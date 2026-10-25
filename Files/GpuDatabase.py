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
GpuDatabase.py
--------------
Provides offline lookup of GPU physical attributes (GPU codename, process node,
die size, transistor count, release date, default ROPs/TMUs, shader count)
similar to TechPowerUp GPU-Z. Matches by PCI Vendor ID:Device ID, or by
model name heuristics.
"""

import re

# Format: (vendor_id_hex, device_id_hex): { ... specs ... }
# Vendor IDs: 0x10de (NVIDIA), 0x1002 (AMD), 0x8086 (Intel)
_PCI_GPU_DATABASE = {
    # ── NVIDIA Ada Lovelace (RTX 40-series) ───────────────────────────
    ("10de", "2684"): {
        "chip": "AD102", "node": "4N (5 nm)", "die_size": "608 mm²",
        "transistors": "76,300M", "release": "Oct 2022", "shaders": "16384 Unified",
        "rops_tmus": "176 / 512", "bus_width": "384 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("10de", "2704"): {
        "chip": "AD103", "node": "4N (5 nm)", "die_size": "379 mm²",
        "transistors": "45,900M", "release": "Nov 2022", "shaders": "9728 Unified",
        "rops_tmus": "112 / 304", "bus_width": "256 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("10de", "2782"): {
        "chip": "AD104", "node": "4N (5 nm)", "die_size": "295 mm²",
        "transistors": "35,800M", "release": "Jan 2023", "shaders": "7680 Unified",
        "rops_tmus": "80 / 240", "bus_width": "192 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("10de", "2786"): {
        "chip": "AD104", "node": "4N (5 nm)", "die_size": "295 mm²",
        "transistors": "35,800M", "release": "Apr 2023", "shaders": "5888 Unified",
        "rops_tmus": "64 / 184", "bus_width": "192 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("10de", "2803"): {
        "chip": "AD106", "node": "4N (5 nm)", "die_size": "188 mm²",
        "transistors": "22,900M", "release": "May 2023", "shaders": "4352 Unified",
        "rops_tmus": "48 / 136", "bus_width": "128 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("10de", "2882"): {
        "chip": "AD107", "node": "4N (5 nm)", "die_size": "159 mm²",
        "transistors": "18,900M", "release": "Jun 2023", "shaders": "3072 Unified",
        "rops_tmus": "32 / 96", "bus_width": "128 Bit", "directx": "12 Ultimate (12_2)",
    },

    # ── NVIDIA Ampere (RTX 30-series) ─────────────────────────────────
    ("10de", "2204"): {
        "chip": "GA102", "node": "8 nm", "die_size": "628 mm²",
        "transistors": "28,300M", "release": "Sep 2020", "shaders": "8704 Unified",
        "rops_tmus": "96 / 272", "bus_width": "320 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("10de", "2206"): {
        "chip": "GA102", "node": "8 nm", "die_size": "628 mm²",
        "transistors": "28,300M", "release": "Sep 2020", "shaders": "10496 Unified",
        "rops_tmus": "112 / 328", "bus_width": "384 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("10de", "2208"): {
        "chip": "GA102", "node": "8 nm", "die_size": "628 mm²",
        "transistors": "28,300M", "release": "Mar 2022", "shaders": "10752 Unified",
        "rops_tmus": "112 / 336", "bus_width": "384 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("10de", "2482"): {
        "chip": "GA104", "node": "8 nm", "die_size": "392 mm²",
        "transistors": "17,400M", "release": "Jun 2021", "shaders": "6144 Unified",
        "rops_tmus": "96 / 192", "bus_width": "256 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("10de", "2484"): {
        "chip": "GA104", "node": "8 nm", "die_size": "392 mm²",
        "transistors": "17,400M", "release": "Oct 2020", "shaders": "5888 Unified",
        "rops_tmus": "96 / 184", "bus_width": "256 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("10de", "2486"): {
        "chip": "GA104", "node": "8 nm", "die_size": "392 mm²",
        "transistors": "17,400M", "release": "Dec 2020", "shaders": "4864 Unified",
        "rops_tmus": "80 / 152", "bus_width": "256 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("10de", "2503"): {
        "chip": "GA106", "node": "8 nm", "die_size": "276 mm²",
        "transistors": "12,000M", "release": "Jan 2021", "shaders": "3584 Unified",
        "rops_tmus": "48 / 112", "bus_width": "192 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("10de", "2504"): {
        "chip": "GA106", "node": "8 nm", "die_size": "276 mm²",
        "transistors": "12,000M", "release": "May 2021", "shaders": "3584 Unified",
        "rops_tmus": "48 / 112", "bus_width": "192 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("10de", "2507"): {
        "chip": "GA106", "node": "8 nm", "die_size": "276 mm²",
        "transistors": "12,000M", "release": "Jan 2022", "shaders": "2560 Unified",
        "rops_tmus": "32 / 80", "bus_width": "128 Bit", "directx": "12 Ultimate (12_2)",
    },

    # ── NVIDIA Turing (RTX 20-series & GTX 16-series) ─────────────────
    ("10de", "1e04"): {
        "chip": "TU102", "node": "12 nm", "die_size": "754 mm²",
        "transistors": "18,600M", "release": "Sep 2018", "shaders": "4352 Unified",
        "rops_tmus": "88 / 272", "bus_width": "352 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("10de", "1e82"): {
        "chip": "TU104", "node": "12 nm", "die_size": "545 mm²",
        "transistors": "13,600M", "release": "Jul 2019", "shaders": "3072 Unified",
        "rops_tmus": "64 / 192", "bus_width": "256 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("10de", "1e84"): {
        "chip": "TU104", "node": "12 nm", "die_size": "545 mm²",
        "transistors": "13,600M", "release": "Sep 2018", "shaders": "2944 Unified",
        "rops_tmus": "64 / 184", "bus_width": "256 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("10de", "1f02"): {
        "chip": "TU106", "node": "12 nm", "die_size": "445 mm²",
        "transistors": "10,800M", "release": "Oct 2018", "shaders": "2304 Unified",
        "rops_tmus": "64 / 144", "bus_width": "256 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("10de", "1f06"): {
        "chip": "TU106", "node": "12 nm", "die_size": "445 mm²",
        "transistors": "10,800M", "release": "Jul 2019", "shaders": "2176 Unified",
        "rops_tmus": "64 / 136", "bus_width": "256 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("10de", "1f08"): {
        "chip": "TU106", "node": "12 nm", "die_size": "445 mm²",
        "transistors": "10,800M", "release": "Jan 2019", "shaders": "1920 Unified",
        "rops_tmus": "48 / 120", "bus_width": "192 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("10de", "2184"): {
        "chip": "TU116", "node": "12 nm", "die_size": "284 mm²",
        "transistors": "6,600M", "release": "Oct 2019", "shaders": "1536 Unified",
        "rops_tmus": "48 / 96", "bus_width": "192 Bit", "directx": "12 (12_1)",
    },

    # ── NVIDIA Pascal (GTX 10-series) ─────────────────────────────────
    ("10de", "1b06"): {
        "chip": "GP102", "node": "16 nm", "die_size": "471 mm²",
        "transistors": "12,000M", "release": "Mar 2017", "shaders": "3584 Unified",
        "rops_tmus": "88 / 224", "bus_width": "352 Bit", "directx": "12 (12_1)",
    },
    ("10de", "1b80"): {
        "chip": "GP104", "node": "16 nm", "die_size": "314 mm²",
        "transistors": "7,200M", "release": "May 2016", "shaders": "2560 Unified",
        "rops_tmus": "64 / 160", "bus_width": "256 Bit", "directx": "12 (12_1)",
    },
    ("10de", "1b81"): {
        "chip": "GP104", "node": "16 nm", "die_size": "314 mm²",
        "transistors": "7,200M", "release": "Jun 2016", "shaders": "1920 Unified",
        "rops_tmus": "64 / 120", "bus_width": "256 Bit", "directx": "12 (12_1)",
    },
    ("10de", "1c02"): {
        "chip": "GP106", "node": "16 nm", "die_size": "200 mm²",
        "transistors": "4,400M", "release": "Jul 2016", "shaders": "1280 Unified",
        "rops_tmus": "48 / 80", "bus_width": "192 Bit", "directx": "12 (12_1)",
    },
    ("10de", "1c03"): {
        "chip": "GP106", "node": "16 nm", "die_size": "200 mm²",
        "transistors": "4,400M", "release": "Jul 2016", "shaders": "1280 Unified",
        "rops_tmus": "48 / 80", "bus_width": "192 Bit", "directx": "12 (12_1)",
    },
    ("10de", "1c82"): {
        "chip": "GP107", "node": "14 nm", "die_size": "132 mm²",
        "transistors": "3,300M", "release": "Oct 2016", "shaders": "768 Unified",
        "rops_tmus": "32 / 48", "bus_width": "128 Bit", "directx": "12 (12_1)",
    },

    # ── AMD RDNA 3 (RX 7000-series) ───────────────────────────────────
    ("1002", "7448"): {
        "chip": "Navi 31", "node": "5 nm + 6 nm", "die_size": "529 mm²",
        "transistors": "57,700M", "release": "Dec 2022", "shaders": "6144 Unified",
        "rops_tmus": "192 / 384", "bus_width": "384 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("1002", "744c"): {
        "chip": "Navi 31", "node": "5 nm + 6 nm", "die_size": "529 mm²",
        "transistors": "57,700M", "release": "Dec 2022", "shaders": "5376 Unified",
        "rops_tmus": "192 / 336", "bus_width": "320 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("1002", "7460"): {
        "chip": "Navi 32", "node": "5 nm + 6 nm", "die_size": "346 mm²",
        "transistors": "28,100M", "release": "Sep 2023", "shaders": "3840 Unified",
        "rops_tmus": "96 / 240", "bus_width": "256 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("1002", "7461"): {
        "chip": "Navi 32", "node": "5 nm + 6 nm", "die_size": "346 mm²",
        "transistors": "28,100M", "release": "Sep 2023", "shaders": "3456 Unified",
        "rops_tmus": "96 / 216", "bus_width": "192 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("1002", "7480"): {
        "chip": "Navi 33", "node": "6 nm", "die_size": "204 mm²",
        "transistors": "13,300M", "release": "May 2023", "shaders": "2048 Unified",
        "rops_tmus": "64 / 128", "bus_width": "128 Bit", "directx": "12 Ultimate (12_2)",
    },

    # ── AMD RDNA 2 (RX 6000-series) ───────────────────────────────────
    ("1002", "73bf"): {
        "chip": "Navi 21", "node": "7 nm", "die_size": "520 mm²",
        "transistors": "26,800M", "release": "Nov 2020", "shaders": "5120 Unified",
        "rops_tmus": "128 / 320", "bus_width": "256 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("1002", "73df"): {
        "chip": "Navi 22", "node": "7 nm", "die_size": "335 mm²",
        "transistors": "17,200M", "release": "Mar 2021", "shaders": "2560 Unified",
        "rops_tmus": "64 / 160", "bus_width": "192 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("1002", "73ff"): {
        "chip": "Navi 23", "node": "7 nm", "die_size": "237 mm²",
        "transistors": "11,060M", "release": "Aug 2021", "shaders": "2048 Unified",
        "rops_tmus": "64 / 128", "bus_width": "128 Bit", "directx": "12 Ultimate (12_2)",
    },

    # ── AMD RDNA 1 (RX 5000-series) ───────────────────────────────────
    ("1002", "731f"): {
        "chip": "Navi 10", "node": "7 nm", "die_size": "251 mm²",
        "transistors": "10,300M", "release": "Jul 2019", "shaders": "2560 Unified",
        "rops_tmus": "64 / 160", "bus_width": "256 Bit", "directx": "12 (12_1)",
    },

    # ── AMD Polaris & Vega ────────────────────────────────────────────
    ("1002", "67df"): {
        "chip": "Polaris 20", "node": "14 nm", "die_size": "232 mm²",
        "transistors": "5,700M", "release": "Apr 2017", "shaders": "2304 Unified",
        "rops_tmus": "32 / 144", "bus_width": "256 Bit", "directx": "12 (12_0)",
    },
    ("1002", "15d8"): {
        "chip": "Raven Ridge / Vega 8", "node": "14 nm", "die_size": "210 mm²",
        "transistors": "4,940M", "release": "Feb 2018", "shaders": "512 Unified",
        "rops_tmus": "8 / 32", "bus_width": "128 Bit (System)", "directx": "12 (12_1)",
    },

    # ── Intel Arc Alchemist ───────────────────────────────────────────
    ("8086", "5690"): {
        "chip": "ACM-G10", "node": "TSMC N6 (6 nm)", "die_size": "406 mm²",
        "transistors": "21,700M", "release": "Oct 2022", "shaders": "4096 Unified",
        "rops_tmus": "128 / 256", "bus_width": "256 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("8086", "5691"): {
        "chip": "ACM-G10", "node": "TSMC N6 (6 nm)", "die_size": "406 mm²",
        "transistors": "21,700M", "release": "Oct 2022", "shaders": "3584 Unified",
        "rops_tmus": "128 / 224", "bus_width": "256 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("8086", "56a0"): {
        "chip": "ACM-G10", "node": "TSMC N6 (6 nm)", "die_size": "406 mm²",
        "transistors": "21,700M", "release": "Oct 2022", "shaders": "4096 Unified",
        "rops_tmus": "128 / 256", "bus_width": "256 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("8086", "56a1"): {
        "chip": "ACM-G10", "node": "TSMC N6 (6 nm)", "die_size": "406 mm²",
        "transistors": "21,700M", "release": "Oct 2022", "shaders": "3584 Unified",
        "rops_tmus": "128 / 224", "bus_width": "256 Bit", "directx": "12 Ultimate (12_2)",
    },
    ("8086", "56a5"): {
        "chip": "ACM-G11", "node": "TSMC N6 (6 nm)", "die_size": "157 mm²",
        "transistors": "7,200M", "release": "Jun 2022", "shaders": "1024 Unified",
        "rops_tmus": "32 / 64", "bus_width": "96 Bit", "directx": "12 Ultimate (12_2)",
    },

    # ── Intel Integrated Graphics (Gen 12 / Xe) ───────────────────────
    ("8086", "4680"): {
        "chip": "Alder Lake GT1 (UHD 770)", "node": "Intel 7 (10 nm)", "die_size": "209 mm²",
        "transistors": "—", "release": "Nov 2021", "shaders": "256 Unified",
        "rops_tmus": "16 / 32", "bus_width": "128 Bit (Shared)", "directx": "12 (12_1)",
    },
    ("8086", "4690"): {
        "chip": "Raptor Lake GT1 (UHD 770)", "node": "Intel 7 (10 nm)", "die_size": "257 mm²",
        "transistors": "—", "release": "Oct 2022", "shaders": "256 Unified",
        "rops_tmus": "16 / 32", "bus_width": "128 Bit (Shared)", "directx": "12 (12_1)",
    },
}

# Substring fallback for common names when PCI ID lookup misses
_NAME_HEURISTICS = [
    (r"rtx\s*4090", {"chip": "AD102", "node": "4N (5 nm)", "die_size": "608 mm²", "transistors": "76,300M", "release": "Oct 2022", "bus_width": "384 Bit"}),
    (r"rtx\s*4080", {"chip": "AD103", "node": "4N (5 nm)", "die_size": "379 mm²", "transistors": "45,900M", "release": "Nov 2022", "bus_width": "256 Bit"}),
    (r"rtx\s*4070\s*ti", {"chip": "AD104", "node": "4N (5 nm)", "die_size": "295 mm²", "transistors": "35,800M", "release": "Jan 2023", "bus_width": "192 Bit"}),
    (r"rtx\s*4070", {"chip": "AD104", "node": "4N (5 nm)", "die_size": "295 mm²", "transistors": "35,800M", "release": "Apr 2023", "bus_width": "192 Bit"}),
    (r"rtx\s*4060\s*ti", {"chip": "AD106", "node": "4N (5 nm)", "die_size": "188 mm²", "transistors": "22,900M", "release": "May 2023", "bus_width": "128 Bit"}),
    (r"rtx\s*4060", {"chip": "AD107", "node": "4N (5 nm)", "die_size": "159 mm²", "transistors": "18,900M", "release": "Jun 2023", "bus_width": "128 Bit"}),

    (r"rtx\s*3090", {"chip": "GA102", "node": "8 nm", "die_size": "628 mm²", "transistors": "28,300M", "release": "Sep 2020", "bus_width": "384 Bit"}),
    (r"rtx\s*3080", {"chip": "GA102", "node": "8 nm", "die_size": "628 mm²", "transistors": "28,300M", "release": "Sep 2020", "bus_width": "320 Bit"}),
    (r"rtx\s*3070", {"chip": "GA104", "node": "8 nm", "die_size": "392 mm²", "transistors": "17,400M", "release": "Oct 2020", "bus_width": "256 Bit"}),
    (r"rtx\s*3060\s*ti", {"chip": "GA104", "node": "8 nm", "die_size": "392 mm²", "transistors": "17,400M", "release": "Dec 2020", "bus_width": "256 Bit"}),
    (r"rtx\s*3060", {"chip": "GA106", "node": "8 nm", "die_size": "276 mm²", "transistors": "12,000M", "release": "Jan 2021", "bus_width": "192 Bit"}),
    (r"rtx\s*3050", {"chip": "GA106 / GA107", "node": "8 nm", "die_size": "200 mm²", "transistors": "12,000M", "release": "Jan 2022", "bus_width": "128 Bit"}),

    (r"rx\s*7900\s*xtx", {"chip": "Navi 31", "node": "5 nm + 6 nm", "die_size": "529 mm²", "transistors": "57,700M", "release": "Dec 2022", "bus_width": "384 Bit"}),
    (r"rx\s*7900\s*xt", {"chip": "Navi 31", "node": "5 nm + 6 nm", "die_size": "529 mm²", "transistors": "57,700M", "release": "Dec 2022", "bus_width": "320 Bit"}),
    (r"rx\s*7800\s*xt", {"chip": "Navi 32", "node": "5 nm + 6 nm", "die_size": "346 mm²", "transistors": "28,100M", "release": "Sep 2023", "bus_width": "256 Bit"}),
    (r"rx\s*7700\s*xt", {"chip": "Navi 32", "node": "5 nm + 6 nm", "die_size": "346 mm²", "transistors": "28,100M", "release": "Sep 2023", "bus_width": "192 Bit"}),
    (r"rx\s*7600", {"chip": "Navi 33", "node": "6 nm", "die_size": "204 mm²", "transistors": "13,300M", "release": "May 2023", "bus_width": "128 Bit"}),

    (r"rx\s*6800\s*xt", {"chip": "Navi 21", "node": "7 nm", "die_size": "520 mm²", "transistors": "26,800M", "release": "Nov 2020", "bus_width": "256 Bit"}),
    (r"rx\s*6700\s*xt", {"chip": "Navi 22", "node": "7 nm", "die_size": "335 mm²", "transistors": "17,200M", "release": "Mar 2021", "bus_width": "192 Bit"}),
    (r"rx\s*6600\s*xt", {"chip": "Navi 23", "node": "7 nm", "die_size": "237 mm²", "transistors": "11,060M", "release": "Aug 2021", "bus_width": "128 Bit"}),

    (r"arc\s*a770", {"chip": "ACM-G10", "node": "TSMC N6", "die_size": "406 mm²", "transistors": "21,700M", "release": "Oct 2022", "bus_width": "256 Bit"}),
    (r"arc\s*a750", {"chip": "ACM-G10", "node": "TSMC N6", "die_size": "406 mm²", "transistors": "21,700M", "release": "Oct 2022", "bus_width": "256 Bit"}),
    (r"arc\s*a580", {"chip": "ACM-G10", "node": "TSMC N6", "die_size": "406 mm²", "transistors": "21,700M", "release": "Oct 2023", "bus_width": "256 Bit"}),
    (r"arc\s*a380", {"chip": "ACM-G11", "node": "TSMC N6", "die_size": "157 mm²", "transistors": "7,200M", "release": "Jun 2022", "bus_width": "96 Bit"}),
]


def lookup_gpu_specs(vendor_id: str, device_id: str, name: str = "") -> dict:
    """
    Look up GPU physical specs given Vendor ID, Device ID, and/or device name.
    Normalises hex strings (strips 0x, lowercases).
    Returns a dict with guaranteed keys.
    """
    default_specs = {
        "chip": "—",
        "node": "—",
        "die_size": "—",
        "transistors": "—",
        "release": "—",
        "shaders": "—",
        "rops_tmus": "—",
        "bus_width": "—",
        "directx": "12.0",
    }

    v_clean = (vendor_id or "").strip().lower().replace("0x", "")
    d_clean = (device_id or "").strip().lower().replace("0x", "")

    # 1. Exact match on (vendor, device)
    if (v_clean, d_clean) in _PCI_GPU_DATABASE:
        res = dict(default_specs)
        res.update(_PCI_GPU_DATABASE[(v_clean, d_clean)])
        return res

    # 2. Heuristic match on device name
    n_clean = (name or "").strip().lower()
    if n_clean:
        for pattern, data in _NAME_HEURISTICS:
            if re.search(pattern, n_clean):
                res = dict(default_specs)
                res.update(data)
                return res

    return default_specs


def calculate_bandwidth(memory_clock_mhz: float, bus_width_bits: int, multiplier: float = 2.0) -> str:
    """
    Calculate theoretical memory bandwidth in GB/s:
    Bandwidth = (Effective Clock [MHz] * Bus Width [bits]) / (8 * 1000)
    For GDDR6/GDDR6X, multiplier reflects data transfers per clock cycle.
    """
    try:
        if memory_clock_mhz <= 0 or bus_width_bits <= 0:
            return "—"
        effective_freq_mhz = memory_clock_mhz * multiplier
        bandwidth_gbs = (effective_freq_mhz * bus_width_bits) / (8.0 * 1000.0)
        return f"{bandwidth_gbs:.1f} GB/s"
    except Exception:
        return "—"
