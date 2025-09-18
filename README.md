# Astonish — zero-dependency generative art tool

This repository contains a small single-file renderer `astonish.py` that produces high-quality generative art as PPM/PNG outputs and a Docusaurus-based website in `website/` for documentation and a gallery.

## Quickstart

- ASCII preview in terminal:

```
python3 astonish.py --mode flow --width 160 --height 90 --steps 200 --particles 2000 --seed 42 --ascii
```

- Write a PPM file:

```
python3 astonish.py --mode flow --width 1920 --height 1080 --steps 1000 --particles 60000 --seed 42 --out outputs/astonish_1920x1080.ppm
```

- Write a PNG directly (requires Pillow). If Pillow is not installed, use `--ensure-pillow` to create a venv and install it:

```
python3 astonish.py --mode flow --width 1920 --height 1080 --steps 1000 --particles 60000 --seed 42 --png outputs/astonish_1920x1080.png --ensure-pillow
```

## License

MIT
