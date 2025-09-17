Galaga3D — single-file 3D Galaga demo/library

Files
- `galaga3d.html` — Self-contained single-file library + demo. Drop it on a static host or open locally in a browser. Requires network access to load Three.js from unpkg.

Usage
- Open `galaga3d.html` in a browser.
- Controls: arrow keys to move, Space to shoot, Start/Pause/Reset buttons.

API
- window.Galaga3D(container, opts) — constructor. `container` can be a DOM element or selector.
  - instance.start() — start the game loop
  - instance.pause() — pause the game
  - instance.reset() — reset enemies and score
  - instance.onScore — callback(score)

License
- MIT
