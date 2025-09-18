# Astonish

Astonish is a zero-dependency generative art tool written in a single Python file, `astonish.py`. It supports two rendering engines:

- `flow` — a particle flow-field painter driven by fractal value noise.
- `orbit` — an orbit-trap Mandelbrot renderer.

This project provides:

- A small CLI (`astonish.py`) that can render ASCII previews, write PPM images, and (via Pillow) export PNGs.
- A compact image buffer and tone-mapping pipeline for PPM output.

See the Usage doc for how to render and the Gallery for sample outputs.
