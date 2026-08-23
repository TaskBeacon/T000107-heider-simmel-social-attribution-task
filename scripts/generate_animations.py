"""Generate original geometric-motion stimuli for T000107.

The trajectories below are newly authored for TaskBeacon. They encode only the
paradigm-level social/mechanical/random contrast and do not trace, sample, or
reconstruct frames from the 1944 Heider–Simmel film or later stimulus sets.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Callable

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw


WIDTH = 960
HEIGHT = 540
FPS = 24
DURATION_S = 15.0
FRAME_COUNT = int(FPS * DURATION_S)
BG = (250, 250, 248)
INK = (38, 45, 56)
BLUE = (43, 108, 176)
RED = (206, 64, 69)
GOLD = (232, 174, 45)


def _lerp(a: tuple[float, float], b: tuple[float, float], u: float) -> tuple[float, float]:
    eased = u * u * (3.0 - 2.0 * u)
    return (a[0] + (b[0] - a[0]) * eased, a[1] + (b[1] - a[1]) * eased)


def _keyframes(points: list[tuple[float, float]], t: float) -> tuple[float, float]:
    t = min(max(float(t), 0.0), 1.0)
    scaled = t * (len(points) - 1)
    index = min(int(scaled), len(points) - 2)
    return _lerp(points[index], points[index + 1], scaled - index)


def _triangle(center: tuple[float, float], radius: float, heading: float) -> list[tuple[float, float]]:
    return [
        (
            center[0] + radius * math.cos(heading + offset),
            center[1] + radius * math.sin(heading + offset),
        )
        for offset in (0.0, 2.45, -2.45)
    ]


def _heading(previous: tuple[float, float], current: tuple[float, float], fallback: float = 0.0) -> float:
    dx, dy = current[0] - previous[0], current[1] - previous[1]
    return math.atan2(dy, dx) if abs(dx) + abs(dy) > 0.05 else fallback


def _draw_enclosure(draw: ImageDraw.ImageDraw) -> None:
    left, top, right, bottom = 650, 145, 865, 390
    width = 7
    draw.line((left, top, right, top), fill=INK, width=width)
    draw.line((right, top, right, bottom), fill=INK, width=width)
    draw.line((right, bottom, left, bottom), fill=INK, width=width)
    draw.line((left, top, left, 245), fill=INK, width=width)
    draw.line((left, 315, left, bottom), fill=INK, width=width)
    draw.line((left, 245, left + 58, 280), fill=INK, width=6)


def _draw_agents(
    draw: ImageDraw.ImageDraw,
    positions: dict[str, tuple[float, float]],
    previous: dict[str, tuple[float, float]],
) -> None:
    big = positions["big"]
    small = positions["small"]
    circle = positions["circle"]
    big_heading = _heading(previous.get("big", big), big)
    small_heading = _heading(previous.get("small", small), small)
    draw.polygon(_triangle(big, 34, big_heading), fill=BLUE, outline=INK)
    draw.line(_triangle(big, 34, big_heading) + [_triangle(big, 34, big_heading)[0]], fill=INK, width=3)
    draw.polygon(_triangle(small, 25, small_heading), fill=RED, outline=INK)
    draw.line(_triangle(small, 25, small_heading) + [_triangle(small, 25, small_heading)[0]], fill=INK, width=3)
    r = 25
    draw.ellipse((circle[0] - r, circle[1] - r, circle[0] + r, circle[1] + r), fill=GOLD, outline=INK, width=3)


def _social_helping(t: float) -> dict[str, tuple[float, float]]:
    big = _keyframes([(150, 390), (240, 350), (310, 350), (420, 305), (545, 280), (620, 280), (735, 280), (790, 250)], t)
    circle = _keyframes([(560, 280), (620, 280), (610, 330), (600, 280), (615, 280), (670, 280), (750, 280), (805, 305)], t)
    small = _keyframes([(790, 330), (760, 330), (735, 330), (735, 320), (720, 340), (760, 350), (800, 340), (815, 330)], t)
    return {"big": big, "small": small, "circle": circle}


def _social_chasing(t: float) -> dict[str, tuple[float, float]]:
    big = _keyframes([(160, 380), (280, 365), (400, 285), (530, 205), (600, 300), (500, 395), (370, 350), (485, 285), (575, 280)], t)
    small = _keyframes([(285, 360), (400, 315), (525, 230), (610, 210), (545, 335), (420, 420), (300, 310), (435, 245), (610, 280)], t)
    circle = _keyframes([(760, 330), (750, 330), (725, 310), (680, 300), (640, 300), (610, 285), (585, 280), (600, 280), (595, 280)], t)
    return {"big": big, "small": small, "circle": circle}


def _tri_wave(value: float) -> float:
    wrapped = value % 2.0
    return wrapped if wrapped <= 1.0 else 2.0 - wrapped


def _mechanical_bounce(t: float) -> dict[str, tuple[float, float]]:
    time_s = t * DURATION_S
    big = (115 + 485 * _tri_wave(time_s * 0.19), 110 + 315 * _tri_wave(0.31 + time_s * 0.23))
    small = (135 + 455 * _tri_wave(0.62 + time_s * 0.23), 105 + 325 * _tri_wave(0.18 + time_s * 0.17))
    circle = (690 + 125 * _tri_wave(0.35 + time_s * 0.29), 185 + 165 * _tri_wave(0.80 + time_s * 0.21))
    return {"big": big, "small": small, "circle": circle}


CONVEYOR_PATH = [(120, 365), (350, 365), (565, 365), (565, 205), (400, 205), (230, 205), (120, 365)]


def _cyclic_path(progress: float) -> tuple[float, float]:
    return _keyframes(CONVEYOR_PATH, progress % 1.0)


def _mechanical_conveyor(t: float) -> dict[str, tuple[float, float]]:
    base = t * 1.35
    return {
        "big": _cyclic_path(base),
        "small": _cyclic_path(base + 0.33),
        "circle": _cyclic_path(base + 0.66),
    }


def _random_waypoints(seed: int) -> dict[str, list[tuple[float, float]]]:
    rng = np.random.default_rng(seed)
    output: dict[str, list[tuple[float, float]]] = {}
    for name, x_band in (("big", (90, 590)), ("small", (110, 610)), ("circle", (690, 830))):
        output[name] = [
            (float(rng.uniform(*x_band)), float(rng.uniform(100, 430)))
            for _ in range(13)
        ]
    return output


RANDOM_A = _random_waypoints(10701)
RANDOM_B = _random_waypoints(10702)


def _random_motion(points: dict[str, list[tuple[float, float]]], t: float) -> dict[str, tuple[float, float]]:
    return {name: _keyframes(path, t) for name, path in points.items()}


def _draw_mechanical_guides(draw: ImageDraw.ImageDraw, scenario: str) -> None:
    if scenario == "mechanical_bounce":
        draw.rectangle((80, 75, 620, 465), outline=(135, 142, 150), width=5)
        draw.line((350, 135, 350, 395), fill=(135, 142, 150), width=7)
    elif scenario == "mechanical_conveyor":
        draw.line(CONVEYOR_PATH, fill=(135, 142, 150), width=12, joint="curve")
        for x in range(145, 570, 48):
            draw.ellipse((x - 9, 382, x + 9, 400), fill=(180, 185, 191), outline=INK, width=2)


SCENARIOS: dict[str, Callable[[float], dict[str, tuple[float, float]]]] = {
    "social_helping": _social_helping,
    "social_chasing": _social_chasing,
    "mechanical_bounce": _mechanical_bounce,
    "mechanical_conveyor": _mechanical_conveyor,
    "random_drift_a": lambda t: _random_motion(RANDOM_A, t),
    "random_drift_b": lambda t: _random_motion(RANDOM_B, t),
}


def _render_scenario(name: str, resolver: Callable[[float], dict[str, tuple[float, float]]], output: Path) -> None:
    writer = imageio.get_writer(
        output,
        fps=FPS,
        codec="libx264",
        quality=8,
        macro_block_size=2,
        ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    )
    previous: dict[str, tuple[float, float]] = {}
    try:
        for frame_index in range(FRAME_COUNT):
            t = frame_index / max(FRAME_COUNT - 1, 1)
            image = Image.new("RGB", (WIDTH, HEIGHT), BG)
            draw = ImageDraw.Draw(image)
            _draw_enclosure(draw)
            _draw_mechanical_guides(draw, name)
            positions = resolver(t)
            _draw_agents(draw, positions, previous)
            previous = positions
            writer.append_data(np.asarray(image))
    finally:
        writer.close()


def main() -> None:
    task_root = Path(__file__).resolve().parents[1]
    output_dir = task_root / "assets" / "animations"
    output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for name, resolver in SCENARIOS.items():
        path = output_dir / f"{name}.mp4"
        print(f"[generate] {name} -> {path}")
        _render_scenario(name, resolver, path)
        records.append(
            {
                "condition": name,
                "filename": path.name,
                "duration_s": DURATION_S,
                "fps": FPS,
                "frame_size": [WIDTH, HEIGHT],
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    manifest = {
        "generator": "scripts/generate_animations.py",
        "generator_version": 1,
        "source_policy": "new deterministic trajectories; no copied film frames or paths",
        "animations": records,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
