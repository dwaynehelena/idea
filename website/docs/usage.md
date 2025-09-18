# Usage

Basic CLI examples (run from the repository root):

Render an ASCII preview:

```
python3 astonish.py --mode flow --width 160 --height 90 --steps 200 --particles 2000 --seed 42 --ascii
```

Write a PPM image (full render):

```
python3 astonish.py --mode flow --width 1920 --height 1080 --steps 1000 --particles 60000 --seed 42 --out outputs/astonish_1920x1080.ppm
```

Convert to PNG using Pillow (optional):

```
python3 -m venv .venv_astonish
.venv_astonish/bin/python -m pip install pillow
.venv_astonish/bin/python - <<'PY'
from PIL import Image
im = Image.open('outputs/astonish_1920x1080.ppm')
im.save('outputs/astonish_1920x1080.png')
PY
```

Or write a PNG directly using the new `--png` flag (requires Pillow):

```
python3 astonish.py --mode flow --width 1920 --height 1080 --steps 1000 --particles 60000 --seed 42 --png outputs/astonish_1920x1080.png
```

Tip: full-resolution renders (4K) are CPU and memory intensive. Use smaller resolutions or fewer particles for quick iteration.
