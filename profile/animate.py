"""Encode the dashboard SVG animations as WebP frames for README image embeds."""

import argparse
import math
import re
from pathlib import Path
from xml.etree import ElementTree as ET

import gi
from PIL import Image

gi.require_version("Rsvg", "2.0")
from gi.repository import Rsvg

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)
WIDTH = 760
FRAME_MS = 125
DURATION = 8
SCANNER = "scan-beam"
MOTION_CLASSES = {
    SCANNER, "counter-roll", "graph-scan", "graph-reveal", "cell-beat",
    "orbit-signal", "signal-flow", "metric-fill", "gauge-fill", "counter-static",
}


def number(value):
    return f"{value:.3f}"


def fade(phase, fade_in, hold, fade_out):
    return max(0.0, min(1.0, phase / fade_in, (fade_out - phase) / (fade_out - hold)))


def ease_out(phase, end):
    return 1 - (1 - min(phase / end, 1)) ** 2


def animation_attributes(label, style, phase, node):
    if label == SCANNER:
        period = float(style["--period"].removesuffix("s"))
        delay = float(style["--phase"].removesuffix("s"))
        travel = float(style["--travel"].removesuffix("px"))
        stage = (phase - delay / period) % 1
        offset = -114 + (travel + 114) * min(stage / .75, 1)
        return {"transform": f"translate({number(offset)} 0)", "opacity": number(fade(stage, .09, .65, .75))}

    if label == "counter-roll":
        frames = int(re.fullmatch(r"steps\((\d+),end\)", style["animation-timing-function"])[1])
        end = float(style["--end"].removesuffix("px"))
        step = min(frames, int(frames * phase / .35))
        return {"transform": f"translate(0 {number(end * step / frames)})"}

    if label == "graph-scan":
        offset = -161 + 1063 * min(phase / .86, 1)
        return {"transform": f"translate({number(offset)} 0)", "opacity": number(fade(phase, .08, .72, .86))}

    if label == "cell-beat":
        delay = float(style.get("animation-delay", "0s").removesuffix("s"))
        stage = (phase - delay / 5.5) % 1
        return {"opacity": number(.58 + .42 * fade(stage, .20, .20, .46))}

    if label == "orbit-signal":
        return {"transform": f"rotate({number(phase * 360)})"}

    if label == "signal-flow":
        return {"stroke-dasharray": "8 11", "stroke-dashoffset": number(-38 * phase)}

    if label in {"metric-fill", "graph-reveal"}:
        end = .39 if label == "metric-fill" else .42
        return {"transform": f"scale({number(max(.001, ease_out(phase, end)))} 1)"}

    if label == "gauge-fill":
        circumference = math.tau * float(node.attrib["r"])
        remaining = float(style["--target"])
        offset = 100 - (100 - remaining) * ease_out(phase, .45)
        return {
            "pathLength": number(circumference),
            "stroke-dasharray": f"{number(circumference)} {number(circumference)}",
            "stroke-dashoffset": number(circumference * offset / 100),
        }

    return {"display": "none"}


def render_frame(source, width, height, phase):
    root = ET.fromstring(source)
    for sheet in root.findall(f"{{{SVG}}}style"):
        root.remove(sheet)
    for node in root.iter():
        label = node.get("class")
        if label in MOTION_CLASSES:
            style = dict(item.split(":", 1) for item in node.get("style", "").split(";") if ":" in item)
            node.attrib.update(animation_attributes(label, style, phase, node))
            node.attrib.pop("style", None)

    root.attrib.update(width=str(width), height=str(height))
    handle = Rsvg.Handle.new_from_data(ET.tostring(root, encoding="utf-8"))
    frame = handle.get_pixbuf()
    mode = "RGBA" if frame.get_has_alpha() else "RGB"
    return Image.frombytes(mode, (width, height), frame.get_pixels(), "raw", mode, frame.get_rowstride())


def encode(svg_path):
    source = svg_path.read_bytes()
    _, _, view_width, view_height = map(float, ET.fromstring(source).attrib["viewBox"].split())
    height = round(WIDTH * view_height / view_width)
    frames = [
        render_frame(source, WIDTH, height, (0.375 + frame_ms / (1000 * DURATION)) % 1)
        for frame_ms in range(0, DURATION * 1000, FRAME_MS)
    ]
    output = svg_path.with_suffix(".webp")
    frames[0].save(
        output, format="WEBP", save_all=True, append_images=frames[1:],
        duration=FRAME_MS, loop=0, quality=82, method=3, minimize_size=True,
    )
    with Image.open(output) as animation:
        if animation.n_frames < 2:
            raise ValueError(f"{output} is missing animation frames")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path, nargs="+")
    for path in parser.parse_args().svg:
        encode(path)
