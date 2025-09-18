#!/usr/bin/env python3
# astonishing.py
# Zero-dependency generative art & ASCII preview.
# Modes: flow-field particles (default), orbit-trap Mandelbrot.
# Author: You + M365 Copilot

from __future__ import annotations
import argparse
import math
import os
import random
import sys
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Callable, List, Tuple


# -----------------------------
# Utilities & image buffer (PPM)
# -----------------------------
@dataclass
class Image:
    w: int
    h: int
    # float buffer in linear [0, 1] for each channel
    r: List[float]
    g: List[float]
    b: List[float]

    @classmethod
    def new(cls, w: int, h: int, bg=(0.0, 0.0, 0.0)) -> "Image":
        n = w * h
        return cls(w, h, [bg[0]] * n, [bg[1]] * n, [bg[2]] * n)

    def idx(self, x: int, y: int) -> int:
        return y * self.w + x

    def add(self, x: int, y: int, color: Tuple[float, float, float], k: float = 1.0) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self.idx(x, y)
            self.r[i] = min(1.0, self.r[i] + color[0] * k)
            self.g[i] = min(1.0, self.g[i] + color[1] * k)
            self.b[i] = min(1.0, self.b[i] + color[2] * k)

    def tone_map(self, gamma: float = 1.8) -> Tuple[bytes, bytes, bytes]:
        # Soft roll-off for highlights + gamma to pop midtones
        def mapc(c: float) -> int:
            c = c / (1.0 + c)  # filmic-ish
            c = max(0.0, min(1.0, c)) ** (1.0 / gamma)
            return int(round(c * 255))
        R = bytes(map(mapc, self.r))
        G = bytes(map(mapc, self.g))
        B = bytes(map(mapc, self.b))
        return R, G, B

    def write_ppm(self, path: str) -> None:
        R, G, B = self.tone_map()
        header = f"P6 {self.w} {self.h} 255\n".encode("ascii")
        # interleave rgb quickly
        out = bytearray(self.w * self.h * 3)
        out[0::3] = R
        out[1::3] = G
        out[2::3] = B
        with open(path, "wb") as f:
            f.write(header)
            f.write(out)

    def write_png(self, path: str) -> None:
        """Write a PNG using Pillow if available. Falls back to an informative error if Pillow is not installed."""
        try:
            from PIL import Image as PILImage
        except Exception as e:
            raise RuntimeError("Pillow is required to write PNGs. Install it or use a virtualenv with Pillow available.") from e

        # Compose interleaved RGB bytes and create a PIL image
        R, G, B = self.tone_map()
        out = bytearray(self.w * self.h * 3)
        out[0::3] = R
        out[1::3] = G
        out[2::3] = B
        img = PILImage.frombytes('RGB', (self.w, self.h), bytes(out))
        img.save(path)


# -----------------------------
# Value noise (tileable option)
# -----------------------------
class ValueNoise2D:
    def __init__(self, seed: int, period: int = 256):
        random.seed(seed)
        self.period = period
        self.grid = [random.random() for _ in range(period * period)]

    def _g(self, ix: int, iy: int) -> float:
        ix %= self.period
        iy %= self.period
        return self.grid[iy * self.period + ix]

    @staticmethod
    def _smoothstep(t: float) -> float:
        return t * t * (3 - 2 * t)  # cubic smooth

    def sample(self, x: float, y: float, freq: float = 1.0) -> float:
        x *= freq
        y *= freq
        ix0 = math.floor(x)
        iy0 = math.floor(y)
        fx = x - ix0
        fy = y - iy0
        sx = self._smoothstep(fx)
        sy = self._smoothstep(fy)
        # Corners
        v00 = self._g(ix0,     iy0)
        v10 = self._g(ix0 + 1, iy0)
        v01 = self._g(ix0,     iy0 + 1)
        v11 = self._g(ix0 + 1, iy0 + 1)
        # Bilinear blend
        ix0 = v00 + sx * (v10 - v00)
        ix1 = v01 + sx * (v11 - v01)
        return ix0 + sy * (ix1 - ix0)


# -----------------------------
# Flow-field particle system
# -----------------------------
@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float

def flow_angle(noise: ValueNoise2D, x: float, y: float, scale: float, octaves=3) -> float:
    # Fractal value noise to angle in radians
    amp = 1.0
    val = 0.0
    norm = 0.0
    for i in range(octaves):
        f = (2 ** i) / scale
        v = noise.sample(x, y, f)
        val += amp * v
        norm += amp
        amp *= 0.5
    val /= max(1e-6, norm)
    return (val * 2.0 - 1.0) * math.pi  # [-pi, pi]

def render_flow_field(
    w: int, h: int, steps: int, n_particles: int, seed: int, strength: float = 0.75
) -> Image:
    rng = random.Random(seed)
    img = Image.new(w, h, bg=(0.0, 0.0, 0.0))
    noise = ValueNoise2D(seed=seed ^ 0xBEEF, period=1024)

    # Initialize particles in a loose ring to balance coverage
    particles: List[Particle] = []
    cx, cy = w * 0.5, h * 0.5
    rad = min(w, h) * 0.35
    for _ in range(n_particles):
        ang = rng.random() * 2 * math.pi
        r = rad * (0.65 + 0.35 * rng.random())
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang)
        particles.append(Particle(x, y, 0.0, 0.0))

    # Color palette: cool-to-warm blend along steps
    def palette(t: float) -> Tuple[float, float, float]:
        # t in [0,1]
        # midnight blue -> cyan -> warm amber
        c1 = (0.06, 0.10, 0.30)
        c2 = (0.00, 0.75, 0.75)
        c3 = (0.95, 0.70, 0.20)
        if t < 0.5:
            u = t * 2.0
            return (c1[0] + u * (c2[0] - c1[0]),
                    c1[1] + u * (c2[1] - c1[1]),
                    c1[2] + u * (c2[2] - c1[2]))
        else:
            u = (t - 0.5) * 2.0
            return (c2[0] + u * (c3[0] - c2[0]),
                    c2[1] + u * (c3[1] - c2[1]),
                    c2[2] + u * (c3[2] - c2[2]))

    # Integrate
    scale = 350.0
    for s in range(steps):
        t = s / max(1, steps - 1)
        col = palette(t)
        for p in particles:
            ang = flow_angle(noise, p.x, p.y, scale)
            ax = math.cos(ang) * strength
            ay = math.sin(ang) * strength
            p.vx = (p.vx + ax) * 0.98
            p.vy = (p.vy + ay) * 0.98
            p.x += p.vx
            p.y += p.vy
            # Fade at the edges; bounce softly
            if p.x < 1 or p.x >= w - 1:
                p.vx *= -0.6
            if p.y < 1 or p.y >= h - 1:
                p.vy *= -0.6
            # Deposit multi-sample to reduce aliasing
            ix = int(p.x); iy = int(p.y)
            img.add(ix, iy, col, k=0.015)
            img.add(ix + 1, iy, col, k=0.007)
            img.add(ix, iy + 1, col, k=0.007)
    return img


# -----------------------------
# Orbit-trap Mandelbrot render
# -----------------------------
def render_orbit_trap(w: int, h: int, iters: int, seed: int) -> Image:
    rng = random.Random(seed)
    img = Image.new(w, h, bg=(0.0, 0.0, 0.0))

    # Choose a trap (a circle near the origin) and a colormap
    trap_r = 0.15 + 0.10 * rng.random()
    trap_cx = 0.0 + (rng.random() - 0.5) * 0.1
    trap_cy = 0.0 + (rng.random() - 0.5) * 0.1

    # View window
    scale = 3.0
    cx, cy = -0.6, 0.0

    def colorize(d: float, n: int) -> Tuple[float, float, float]:
        # d: min distance to trap across the orbit; n: escape iteration
        # Rich, glossy feel
        u = math.exp(-4.0 * d)  # proximity boost
        v = n / iters
        r = 0.2 + 0.8 * u
        g = 0.2 + 0.8 * (1.0 - abs(0.5 - v) * 2.0)
        b = 0.25 + 0.75 * (1.0 - u) * (0.4 + 0.6 * v)
        return (r, g, b)

    for y in range(h):
        im = (y / h - 0.5) * scale + cy
        for x in range(w):
            re = (x / w - 0.5) * scale + cx
            zr = 0.0; zi = 0.0
            mind = 1e9
            n = 0
            for n in range(iters):
                # z = z^2 + c
                zr2 = zr * zr - zi * zi + re
                zi = 2.0 * zr * zi + im
                zr = zr2
                # trap distance
                dx = zr - trap_cx
                dy = zi - trap_cy
                d = abs(math.hypot(dx, dy) - trap_r)
                if d < mind:
                    mind = d
                if zr * zr + zi * zi > 4.0:
                    break
            img.add(x, y, colorize(mind, n), k=1.0)
    return img


# -----------------------------
# ASCII preview (terminal)
# -----------------------------
_ASCII = " .:-=+*#%@"

def ascii_preview(img: Image, width: int, height: int) -> None:
    # Downsample with average luminance
    sx = img.w / width
    sy = img.h / height
    for j in range(height):
        y0 = int(j * sy)
        y1 = min(img.h, int((j + 1) * sy))
        line = []
        for i in range(width):
            x0 = int(i * sx)
            x1 = min(img.w, int((i + 1) * sx))
            s = 0.0; c = 0
            for yy in range(y0, y1):
                for xx in range(x0, x1):
                    k = img.idx(xx, yy)
                    # relative luminance
                    lum = 0.2126 * img.r[k] + 0.7152 * img.g[k] + 0.0722 * img.b[k]
                    s += lum
                    c += 1
            avg = s / max(1, c)
            idx = min(len(_ASCII) - 1, int(avg / (avg + 1.0) * (len(_ASCII) - 1) * 1.2))
            line.append(_ASCII[idx])
        print("".join(line))


# -----------------------------
# CLI
# -----------------------------
def main():
    p = argparse.ArgumentParser(description="Astonishing, zero-dependency generative art")
    p.add_argument("--mode", choices=["flow", "orbit"], default="flow", help="engine to use")
    p.add_argument("--width", type=int, default=960)
    p.add_argument("--height", type=int, default=540)
    p.add_argument("--steps", type=int, default=1000, help="flow steps (flow mode)")
    p.add_argument("--particles", type=int, default=60000, help="number of particles (flow mode)")
    p.add_argument("--iters", type=int, default=300, help="max iterations (orbit mode)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=str, help="output PPM file path")
    p.add_argument("--png", type=str, help="output PNG file path (requires Pillow)")
    p.add_argument("--ensure-pillow", action="store_true", help="If Pillow missing, create venv and install it to produce PNG")
    p.add_argument("--ascii", action="store_true", help="print ASCII preview to terminal")
    args = p.parse_args()

    if args.mode == "flow":
        img = render_flow_field(
            w=args.width, h=args.height,
            steps=args.steps, n_particles=args.particles,
            seed=args.seed
        )
    else:
        img = render_orbit_trap(
            w=args.width, h=args.height,
            iters=args.iters, seed=args.seed
        )

    if args.ascii:
        # Render a quick preview without writing a file
        # Use downsample factor so terminals look good
        tw = min(args.width, 180)
        th = max(16, int(tw * args.height / max(1, args.width) * 0.35))
        ascii_preview(img, tw, th)

    if args.out:
        # Ensure parent dir exists
        d = os.path.dirname(args.out)
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
        img.write_ppm(args.out)
        print(f"Wrote {args.out}")

    if args.png:
        d = os.path.dirname(args.png)
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
        try:
            img.write_png(args.png)
            print(f"Wrote {args.png}")
        except RuntimeError as e:
            # If Pillow isn't available in this interpreter, optionally create a venv, install Pillow,
            # and perform conversion there. This keeps the running interpreter unchanged.
            if getattr(args, 'ensure_pillow', False):
                # write a temporary PPM and convert using the venv python
                tmp = tempfile.NamedTemporaryFile(suffix='.ppm', delete=False)
                tmp_path = tmp.name
                tmp.close()
                try:
                    img.write_ppm(tmp_path)
                    venv_dir = os.path.join(os.getcwd(), '.venv_astonish')
                    venv_python = os.path.join(venv_dir, 'bin', 'python')
                    # Create venv if missing
                    if not os.path.exists(venv_python):
                        print('Creating virtualenv for Pillow at', venv_dir)
                        subprocess.check_call([sys.executable, '-m', 'venv', venv_dir])
                    # Install pillow in the venv
                    print('Installing Pillow in the virtualenv...')
                    subprocess.check_call([venv_python, '-m', 'pip', 'install', '--upgrade', 'pip'])
                    subprocess.check_call([venv_python, '-m', 'pip', 'install', 'pillow'])
                    # Run a small conversion script with the venv python
                    cmd = [venv_python, '-c', (
                        "from PIL import Image; im=Image.open(\"%s\"); im.save(\"%s\")" % (tmp_path.replace('"','\"'), args.png.replace('"','\"'))
                    )]
                    subprocess.check_call(cmd)
                    print(f'Wrote {args.png}')
                finally:
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
            else:
                print(str(e), file=sys.stderr)

if __name__ == "__main__":
    main()
