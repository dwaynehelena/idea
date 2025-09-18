Galaga3D — single-file 3D Galaga demo/library

Files
- `galaga3d.html` — Self-contained single-file library + demo. Drop it on a static host or open locally in a browser. Requires network access to load Three.js from unpkg.

Usage
- Open `galaga3d.html` in a browser.
- Controls: arrow keys to move, Space to shoot, Start/Pause/Reset buttons.

Command-line rendering (Astonish):

- ASCII preview:

```
python3 astonish.py --mode flow --width 160 --height 90 --steps 200 --particles 2000 --seed 42 --ascii
```

- Write a PPM file:

```
python3 astonish.py --mode flow --width 1920 --height 1080 --steps 1000 --particles 60000 --seed 42 --out outputs/astonish_1920x1080.ppm
```

- Write a PNG directly (requires Pillow):

```
python3 astonish.py --mode flow --width 1920 --height 1080 --steps 1000 --particles 60000 --seed 42 --png outputs/astonish_1920x1080.png
```

API
- window.Galaga3D(container, opts) — constructor. `container` can be a DOM element or selector.
  - instance.start() — start the game loop
  - instance.pause() — pause the game
  - instance.reset() — reset enemies and score
  - instance.onScore — callback(score)

License
- MIT
